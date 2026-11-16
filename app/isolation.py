# This file is part of Wikipedia2Book
# <https://github.com/gmoulard/wikipedia2book>.
# Copyright (c) 2026 Guillaume Moulard.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import asyncio
import contextlib
import multiprocessing
from collections.abc import AsyncIterator, Callable, Iterable
from typing import Any

# NE PAS passer à « fork » : le serveur a des fils d'exécution (asyncio.to_thread) qui peuvent tenir un verrou de WeasyPrint, Pango ou MuPDF au moment du fork, et le processus enfant resterait bloqué. Le forkserver démarre ses enfants depuis un processus sans fil d'exécution.
CONTEXT = multiprocessing.get_context(
    "forkserver" if "forkserver" in multiprocessing.get_all_start_methods() else "spawn"
)


class IsolatedProcessDied(RuntimeError):
    pass


def preload(modules: Iterable[str]) -> None:
    if CONTEXT.get_start_method() == "forkserver":
        CONTEXT.set_forkserver_preload(list(modules))


def _child(connection, function: Callable, args: tuple) -> None:
    try:
        result = function(*args, lambda message: connection.send(("report", message)))
        connection.send(("result", result))
    except BaseException as error:
        try:
            connection.send(("error", error))
        except Exception:
            connection.send(("error", RuntimeError(f"{type(error).__name__}: {error}")))
    finally:
        connection.close()


async def run_isolated(function: Callable, *args: Any) -> AsyncIterator[tuple[str, Any]]:
    receiver, sender = CONTEXT.Pipe(duplex=False)
    process = CONTEXT.Process(target=_child, args=(sender, function, args), daemon=True)
    try:
        await asyncio.to_thread(process.start)
        sender.close()
        while True:
            try:
                kind, value = await asyncio.to_thread(receiver.recv)
            except EOFError:
                await asyncio.to_thread(process.join)
                raise IsolatedProcessDied(
                    f"L'assemblage du livre s'est arrêté (code {process.exitcode}), probablement faute de mémoire : "
                    "essayez avec moins d'articles."
                ) from None
            if kind == "error":
                raise value
            yield kind, value
            if kind == "result":
                return
    finally:
        # NE PAS laisser vivre le processus enfant : un client qui abandonne la génération doit libérer tout de suite sa mémoire et son processeur.
        if process.pid is not None and process.is_alive():
            process.kill()
        if process.pid is not None:
            await asyncio.to_thread(process.join)
        sender.close()
        receiver.close()


async def run_in_thread(function: Callable, *args: Any) -> AsyncIterator[tuple[str, Any]]:
    loop = asyncio.get_running_loop()
    messages: asyncio.Queue[tuple[str, Any]] = asyncio.Queue()

    def report(message: Any) -> None:
        loop.call_soon_threadsafe(messages.put_nowait, ("report", message))

    task = asyncio.ensure_future(asyncio.to_thread(function, *args, report))
    try:
        while True:
            getter = asyncio.ensure_future(messages.get())
            await asyncio.wait({task, getter}, return_when=asyncio.FIRST_COMPLETED)
            if getter.done():
                yield getter.result()
                continue
            getter.cancel()
            while not messages.empty():
                yield messages.get_nowait()
            yield "result", task.result()
            return
    finally:
        # NE PAS rendre la main avant la fin du fil d'exécution : il écrit encore dans le dossier temporaire que l'appelant supprime juste après.
        with contextlib.suppress(BaseException):
            await task
