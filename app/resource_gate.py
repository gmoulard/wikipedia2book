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
import ctypes
import ctypes.util
import time
from collections import deque
from collections.abc import Callable

ANNOUNCE_EVERY_S = 10


def _malloc_trim():
    try:
        return ctypes.CDLL(ctypes.util.find_library("c") or "libc.so.6").malloc_trim
    except (OSError, AttributeError, TypeError):
        return None


_MALLOC_TRIM = _malloc_trim()


# NE PAS retirer cet appel après les grosses étapes : sans lui, la glibc garde la mémoire libérée par Python, le conteneur reste plein (2 Go relevés sur Toolforge à 50 générations simultanées) et le contrôle de la mémoire ne laisse plus passer qu'une étape à la fois.
def release_memory() -> None:
    if _MALLOC_TRIM is not None:
        _MALLOC_TRIM(0)


class Reservation:
    def __init__(self, gate: "ResourceGate", amount: int, waited_s: float) -> None:
        self.gate = gate
        self.amount = amount
        self.waited_s = waited_s
        self.released = False

    def release(self) -> None:
        if not self.released:
            self.released = True
            self.gate.reserved -= self.amount
            self.gate.active -= 1


class ResourceGate:
    def __init__(self, read_usage: Callable[[], tuple[int | None, int | None]], ratio: float, poll_s: float = 1.0, clock: Callable[[], float] = time.monotonic) -> None:
        self.read_usage = read_usage
        self.ratio = ratio
        self.poll_s = poll_s
        self.clock = clock
        self.reserved = 0
        self.active = 0
        self.queue: deque[object] = deque()

    def fits(self, amount: int) -> bool:
        # NE PAS faire attendre une étape quand aucune autre n'a de réserve : elle attendrait sans fin une ressource (mémoire, disque) que personne ne libère, et un livre trop gros pour la marge ne se ferait jamais.
        if self.active == 0 or not self.ratio:
            return True
        used, limit = self.read_usage()
        if used is None or not limit:
            return True
        return used + self.reserved + amount <= self.ratio * limit

    async def acquire(self, amount: int, on_wait: Callable[[float], None] | None = None) -> Reservation:
        ticket = object()
        self.queue.append(ticket)
        started = self.clock()
        announced: float | None = None
        try:
            # NE PAS laisser passer une étape avant celles qui attendent déjà : une grosse étape (assemblage) serait doublée sans fin par les petites (articles).
            while not (self.queue[0] is ticket and self.fits(amount)):
                waited = self.clock() - started
                if on_wait is not None and (announced is None or waited - announced >= ANNOUNCE_EVERY_S):
                    announced = waited
                    on_wait(waited)
                await asyncio.sleep(self.poll_s)
        finally:
            self.queue.remove(ticket)
        self.reserved += amount
        self.active += 1
        return Reservation(self, amount, self.clock() - started)

    @contextlib.asynccontextmanager
    async def reserve(self, amount: int, on_wait: Callable[[float], None] | None = None):
        reservation = await self.acquire(amount, on_wait)
        try:
            yield reservation
        finally:
            reservation.release()

    def state(self) -> dict[str, float | int]:
        return {"ratio": self.ratio, "reserved_bytes": self.reserved, "active_stages": self.active, "waiting_stages": len(self.queue)}
