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
import unittest
from email.utils import format_datetime
from datetime import datetime, timedelta, timezone

import httpx

import app.wikipedia_api as wikipedia_api
from app.wikipedia_api import MediaWikiClient, MediaWikiError

PDF = b"%PDF-1.4 fake"


class RateLimitTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.sleeps = []
        self.requests = []
        self.answers = []
        real_sleep = asyncio.sleep

        async def fake_sleep(delay, *args, **kwargs):
            self.sleeps.append(round(delay, 1))
            await real_sleep(0)

        self.original_sleep = wikipedia_api.asyncio.sleep
        wikipedia_api.asyncio.sleep = fake_sleep
        self.client = MediaWikiClient()
        await self.client.__aenter__()
        await self.client._client.aclose()
        self.client._client = httpx.AsyncClient(transport=httpx.MockTransport(self.handle))

    async def asyncTearDown(self):
        wikipedia_api.asyncio.sleep = self.original_sleep
        await self.client.__aexit__(None, None, None)

    def handle(self, request):
        self.requests.append(request.url.path)
        answer = self.answers.pop(0) if self.answers else (200, {}, PDF)
        status, headers, content = answer
        return httpx.Response(status, headers=headers, content=content)

    async def test_retries_after_429_with_backoff(self):
        self.answers = [(429, {}, b""), (429, {}, b"")]
        self.assertEqual(await self.client.get_article_pdf("Paris", "fr", "a4"), PDF)
        self.assertEqual(len(self.requests), 3)
        self.assertEqual(self.sleeps, [2.0, 4.0])

    async def test_retry_after_header_in_seconds_and_date_is_capped(self):
        later = format_datetime(datetime.now(timezone.utc) + timedelta(seconds=300), usegmt=True)
        self.answers = [(429, {"Retry-After": "7"}, b""), (503, {"Retry-After": later}, b"")]
        await self.client.get_article_pdf("Paris", "fr", "a4")
        self.assertEqual(self.sleeps, [7.0, float(wikipedia_api.MAX_RETRY_WAIT_S)])

    async def test_gives_up_with_explicit_message(self):
        self.answers = [(429, {}, b"")] * 5
        with self.assertRaises(MediaWikiError) as raised:
            await self.client.get_article_pdf("Paris", "fr", "a4")
        self.assertIn("HTTP 429", str(raised.exception))
        self.assertEqual(len(self.requests), 5)
        self.assertEqual(self.sleeps, [2.0, 4.0, 8.0, 16.0])

    async def test_other_errors_are_not_retried(self):
        self.answers = [(404, {}, b"")]
        with self.assertRaises(MediaWikiError):
            await self.client.get_article_pdf("Paris", "fr", "a4")
        self.assertEqual(len(self.requests), 1)
        self.assertEqual(self.sleeps, [])

    async def test_pause_is_shared_by_parallel_downloads(self):
        self.answers = [(429, {"Retry-After": "5"}, b"")]
        await asyncio.gather(*(self.client.get_article_pdf(title, "fr", "a4") for title in ("A", "B", "C")))
        self.assertEqual(len(self.requests), 4)
        self.client._resume_at = asyncio.get_running_loop().time() + 5
        await self.client.get_article_pdf("D", "fr", "a4")
        self.assertEqual(self.sleeps[-1], 5.0)

    async def test_api_calls_are_retried_too(self):
        self.answers = [(429, {}, b""), (200, {"Content-Type": "application/json"}, b'{"query": {"search": []}}')]
        self.assertEqual(await self.client.search("Paris"), [])
        self.assertEqual(self.requests, ["/w/api.php", "/w/api.php"])


if __name__ == "__main__":
    unittest.main()
