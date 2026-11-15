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
import re
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx

import app.wikipedia_api as wikipedia_api
from app.version import VERSION
from app.wikipedia_api import MediaWikiClient


class FakeClock:
    def __init__(self):
        self.now = 0.0
        self.sleeps = []

    def time(self):
        return self.now

    async def sleep(self, delay, *args, **kwargs):
        self.sleeps.append(delay)
        self.now += delay


class MediaPolicyTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.clock = FakeClock()
        self.saved = (wikipedia_api._clock, wikipedia_api.asyncio.sleep)
        wikipedia_api._clock = self.clock.time
        wikipedia_api.asyncio.sleep = self.clock.sleep
        self.active = 0
        self.peak = 0
        self.body = b"%PDF-" + b"x" * 1000

    async def asyncTearDown(self):
        wikipedia_api._clock, wikipedia_api.asyncio.sleep = self.saved

    async def client(self, handler):
        client = MediaWikiClient()
        await client.__aenter__()
        await client._client.aclose()
        client._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        return client

    async def held_pdf(self, request):
        self.active += 1
        self.peak = max(self.peak, self.active)
        await self.release.wait()
        self.active -= 1
        return httpx.Response(200, content=self.body)

    async def test_total_concurrency_is_two_across_clients(self):
        self.release = asyncio.Event()
        first, second = await self.client(self.held_pdf), await self.client(self.held_pdf)
        titles = [f"Article {index}" for index in range(6)]
        downloads = asyncio.ensure_future(asyncio.gather(*(client.get_article_pdf(title, "fr", "a4") for client in (first, second) for title in titles)))
        real_sleep = self.saved[1]
        for _ in range(50):
            await real_sleep(0)
        self.assertEqual(self.active, wikipedia_api.MEDIA_CONCURRENCY)
        self.release.set()
        self.assertEqual(len(await downloads), 12)
        self.assertEqual(self.peak, wikipedia_api.MEDIA_CONCURRENCY)
        self.assertEqual(wikipedia_api.MEDIA_CONCURRENCY, 2)
        await first.__aexit__(None, None, None)
        await second.__aexit__(None, None, None)

    async def test_bandwidth_window_throttles_reading(self):
        limiter = wikipedia_api.MediaLimiter()
        half = wikipedia_api.MEDIA_WINDOW_BYTES // 2
        await limiter.consume(half)
        await limiter.consume(half)
        self.assertEqual(self.clock.sleeps, [])
        self.clock.now = 3.0
        await limiter.consume(1)
        self.assertEqual(self.clock.sleeps, [wikipedia_api.MEDIA_WINDOW_S - 3.0])
        self.assertGreaterEqual(self.clock.now, wikipedia_api.MEDIA_WINDOW_S)

    def test_window_matches_25_mbps_over_10_seconds(self):
        self.assertEqual(wikipedia_api.MEDIA_WINDOW_S, 10)
        self.assertEqual(wikipedia_api.MEDIA_WINDOW_BYTES * 8 / wikipedia_api.MEDIA_WINDOW_S, 25_000_000)

    async def test_api_calls_do_not_use_media_slots(self):
        limiter = wikipedia_api.media_limiter()
        for _ in range(wikipedia_api.MEDIA_CONCURRENCY):
            await limiter.slots.acquire()
        client = await self.client(lambda request: httpx.Response(200, json={"query": {"search": []}}))
        self.assertEqual(await asyncio.wait_for(client.search("Paris"), 1), [])
        for _ in range(wikipedia_api.MEDIA_CONCURRENCY):
            limiter.slots.release()
        await client.__aexit__(None, None, None)

    async def test_toolforge_downloads_skip_the_media_limits(self):
        limiter = wikipedia_api.media_limiter()
        for _ in range(wikipedia_api.MEDIA_CONCURRENCY):
            await limiter.slots.acquire()
        client = await self.client(lambda request: httpx.Response(200, content=self.body))
        with patch.object(wikipedia_api, "ON_TOOLFORGE", True):
            self.assertEqual(await asyncio.wait_for(client.get_article_pdf("Chat", "fr", "a4"), 1), self.body)
        self.assertEqual(list(limiter.received), [])
        for _ in range(wikipedia_api.MEDIA_CONCURRENCY):
            limiter.slots.release()
        await client.__aexit__(None, None, None)

    def test_only_the_toolforge_procfile_lifts_the_limits(self):
        root = Path(__file__).resolve().parent.parent
        self.assertIn("WIKIPEDIA2BOOK_PLATFORM=toolforge", (root / "Procfile").read_text(encoding="utf-8"))
        self.assertNotIn("WIKIPEDIA2BOOK_PLATFORM", (root / "Dockerfile").read_text(encoding="utf-8"))

    def test_user_agent_follows_wikimedia_policy(self):
        self.assertRegex(wikipedia_api.USER_AGENT, r"^Wikipedia2Book/" + re.escape(VERSION) + r" \(https://[^)]+\) httpx/[0-9.]+$")


if __name__ == "__main__":
    unittest.main()
