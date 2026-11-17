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
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.resource_gate import ResourceGate, release_memory

MB = 1_000_000


class Memory:
    def __init__(self, used, limit=1000 * MB):
        self.used = used
        self.limit = limit

    def __call__(self):
        return self.used, self.limit


class ResourceGateTest(unittest.IsolatedAsyncioTestCase):
    async def test_a_stage_waits_while_used_plus_reserved_exceeds_the_margin(self):
        memory = Memory(500 * MB)
        gate = ResourceGate(memory, 0.95, poll_s=0.01)
        first = await gate.acquire(300 * MB)
        second = asyncio.ensure_future(gate.acquire(200 * MB))
        await asyncio.sleep(0.05)
        self.assertFalse(second.done())
        self.assertEqual(gate.state()["waiting_stages"], 1)
        first.release()
        reservation = await asyncio.wait_for(second, 1)
        self.assertEqual((gate.reserved, gate.active), (200 * MB, 1))
        reservation.release()
        self.assertEqual((gate.reserved, gate.active), (0, 0))

    async def test_a_lone_stage_always_starts(self):
        gate = ResourceGate(Memory(990 * MB), 0.95, poll_s=0.01)
        reservation = await asyncio.wait_for(gate.acquire(500 * MB), 1)
        self.assertEqual(reservation.waited_s >= 0, True)
        reservation.release()

    async def test_no_limit_or_zero_ratio_never_waits(self):
        for gate in (ResourceGate(Memory(990 * MB, None), 0.95, poll_s=0.01), ResourceGate(Memory(990 * MB), 0, poll_s=0.01)):
            first = await gate.acquire(500 * MB)
            await asyncio.wait_for(gate.acquire(500 * MB), 1)
            first.release()

    async def test_stages_start_in_arrival_order(self):
        memory = Memory(0)
        gate = ResourceGate(memory, 0.95, poll_s=0.01)
        holder = await gate.acquire(900 * MB)
        order = []

        async def stage(name, amount):
            reservation = await gate.acquire(amount)
            order.append(name)
            return reservation

        big = asyncio.ensure_future(stage("assemblage", 600 * MB))
        await asyncio.sleep(0.03)
        small = asyncio.ensure_future(stage("article", 10 * MB))
        await asyncio.sleep(0.05)
        self.assertEqual(order, [])
        holder.release()
        (await asyncio.wait_for(big, 1)).release()
        (await asyncio.wait_for(small, 1)).release()
        self.assertEqual(order, ["assemblage", "article"])

    async def test_waiting_is_announced_then_every_ten_seconds(self):
        now = [0.0]
        gate = ResourceGate(Memory(900 * MB), 0.95, poll_s=0.001, clock=lambda: now[0])
        holder = await gate.acquire(100 * MB)
        announced = []
        waiting = asyncio.ensure_future(gate.acquire(100 * MB, announced.append))
        for second in range(1, 26):
            await asyncio.sleep(0.005)
            now[0] = float(second)
        await asyncio.sleep(0.005)
        self.assertEqual(announced[0], 0.0)
        self.assertEqual(len(announced), 3)
        holder.release()
        (await asyncio.wait_for(waiting, 1)).release()

    async def test_cancelled_wait_leaves_the_queue(self):
        gate = ResourceGate(Memory(900 * MB), 0.95, poll_s=0.01)
        holder = await gate.acquire(100 * MB)
        waiting = asyncio.ensure_future(gate.acquire(100 * MB))
        await asyncio.sleep(0.03)
        waiting.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await waiting
        self.assertEqual(gate.state()["waiting_stages"], 0)
        holder.release()
        self.assertEqual(gate.state(), {"ratio": 0.95, "reserved_bytes": 0, "active_stages": 0, "waiting_stages": 0})

    async def test_reserve_releases_even_on_error(self):
        gate = ResourceGate(Memory(0), 0.95, poll_s=0.01)
        with self.assertRaises(RuntimeError):
            async with gate.reserve(50 * MB):
                self.assertEqual(gate.reserved, 50 * MB)
                raise RuntimeError("boom")
        self.assertEqual((gate.reserved, gate.active), (0, 0))


class ReleaseMemoryTest(unittest.TestCase):
    def test_release_memory_never_fails(self):
        self.assertIsNone(release_memory())
        self.assertIsNone(release_memory())


if __name__ == "__main__":
    unittest.main()
