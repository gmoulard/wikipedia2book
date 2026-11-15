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
import os
import tempfile
import time
import unittest
from pathlib import Path

from app.isolation import IsolatedProcessDied, run_in_thread, run_isolated


def reports_then_returns(value, report):
    report("first")
    report("second")
    return value * 2, os.getpid()


def raises_value_error(report):
    report("started")
    raise ValueError("titre introuvable")


def dies(report):
    report("started")
    os._exit(137)


def writes_pid_then_waits(path, report):
    Path(path).write_text(str(os.getpid()))
    report("waiting")
    time.sleep(60)


async def collect(runner, function, *args):
    return [message async for message in runner(function, *args)]


def alive(pid: int) -> bool:
    if os.name == "nt":
        import ctypes

        handle = ctypes.windll.kernel32.OpenProcess(0x1000 | 0x100000, False, pid)
        if not handle:
            return False
        try:
            return ctypes.windll.kernel32.WaitForSingleObject(handle, 0) != 0
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


class RunIsolatedTest(unittest.TestCase):
    def test_reports_then_result_from_another_process(self):
        messages = asyncio.run(collect(run_isolated, reports_then_returns, 21))
        self.assertEqual(messages[:2], [("report", "first"), ("report", "second")])
        kind, (value, pid) = messages[2]
        self.assertEqual((kind, value), ("result", 42))
        self.assertNotEqual(pid, os.getpid())
        self.assertEqual(len(messages), 3)

    def test_child_exception_is_raised_in_parent(self):
        with self.assertRaisesRegex(ValueError, "titre introuvable"):
            asyncio.run(collect(run_isolated, raises_value_error))

    def test_killed_child_raises_explicit_error(self):
        with self.assertRaisesRegex(IsolatedProcessDied, "code 137"):
            asyncio.run(collect(run_isolated, dies))

    def test_abandoned_generation_kills_child(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "pid"

            async def abandon():
                messages = run_isolated(writes_pid_then_waits, str(path))
                self.assertEqual(await anext(messages), ("report", "waiting"))
                await messages.aclose()

            asyncio.run(abandon())
            self.assertFalse(alive(int(path.read_text())))


class RunInThreadTest(unittest.TestCase):
    def test_same_protocol_as_isolated(self):
        messages = asyncio.run(collect(run_in_thread, reports_then_returns, 21))
        self.assertEqual(messages, [("report", "first"), ("report", "second"), ("result", (42, os.getpid()))])

    def test_exception_is_raised(self):
        with self.assertRaisesRegex(ValueError, "titre introuvable"):
            asyncio.run(collect(run_in_thread, raises_value_error))


if __name__ == "__main__":
    unittest.main()
