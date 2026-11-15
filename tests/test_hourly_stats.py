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

import sys
import types
import unittest
from unittest.mock import patch

try:
    import weasyprint  # noqa: F401
except Exception:
    fake = types.ModuleType("weasyprint")
    fake.HTML = lambda *a, **k: None
    sys.modules["weasyprint"] = fake

from fastapi.testclient import TestClient

import app.main as main


class HourlyStatsTest(unittest.TestCase):
    def setUp(self):
        main.hourly_hits.clear()
        self.client = TestClient(main.app)

    def test_counts_every_request_but_the_stats_endpoint(self):
        with patch.object(main, "_current_hour", return_value="2026-11-15T09"):
            self.client.get("/health")
            self.client.get("/api/version")
            self.client.get("/static/does-not-exist.js")
            response = self.client.get("/api/stats/hourly")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["hours"], {"2026-11-15T09": 3})
        self.assertEqual(response.json()["now"], "2026-11-15T09")
        self.assertIn("started", response.json())

    def test_open_cors_and_no_cache(self):
        response = self.client.get("/api/stats/hourly")
        self.assertEqual(response.headers["access-control-allow-origin"], "*")
        self.assertEqual(response.headers["cache-control"], "no-store")

    def test_keeps_only_recent_hours(self):
        hours = [f"2026-11-{day:02d}T{hour:02d}" for day in (13, 14, 15) for hour in range(24)]
        for hour in hours:
            with patch.object(main, "_current_hour", return_value=hour):
                self.client.get("/health")
        kept = self.client.get("/api/stats/hourly").json()["hours"]
        self.assertEqual(len(kept), main.HOURLY_KEEP)
        self.assertEqual(min(kept), hours[-main.HOURLY_KEEP])


if __name__ == "__main__":
    unittest.main()
