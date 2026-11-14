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

import csv
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import toolviews_stats


def fake_fetcher(calls, hits):
    def fetch(url):
        calls.append(url)
        return {"results": {day: {"wikipedia2book": n} for day, n in hits.items()}}
    return fetch


def read(path):
    with path.open(encoding="utf-8") as handle:
        return [(r["date"], r["hits"]) for r in csv.DictReader(handle, delimiter=";")]


class ToolviewsStatsTest(unittest.TestCase):
    def test_fills_only_missing_days_and_skips_today(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stats.csv"
            path.write_text("date;hits\n2026-11-01;10\n", encoding="utf-8")
            calls = []
            added = toolviews_stats.update(path, date(2026, 11, 4), fake_fetcher(calls, {"2026-11-02": 20, "2026-11-03": 30}))
            self.assertEqual(added, ["2026-11-02", "2026-11-03"])
            self.assertEqual(len(calls), 1)
            self.assertTrue(calls[0].endswith("/tool/wikipedia2book/daily/2026-11-02/2026-11-03"))
            self.assertNotIn("/unique/", calls[0])
            self.assertEqual(read(path), [("2026-11-01", "10"), ("2026-11-02", "20"), ("2026-11-03", "30")])

    def test_days_without_visits_are_zero_until_last_published_day(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stats.csv"
            added = toolviews_stats.update(path, date(2026, 11, 5), fake_fetcher([], {"2026-11-03": 7}))
            self.assertEqual(added, ["2026-11-01", "2026-11-02", "2026-11-03"])
            self.assertEqual(read(path), [("2026-11-01", "0"), ("2026-11-02", "0"), ("2026-11-03", "7")])

    def test_nothing_written_when_api_has_no_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stats.csv"
            self.assertEqual(toolviews_stats.update(path, date(2026, 11, 3), fake_fetcher([], {})), [])
            self.assertFalse(path.exists())

    def test_no_call_when_up_to_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stats.csv"
            path.write_text("date;hits\n2026-11-01;1\n", encoding="utf-8")
            calls = []
            self.assertEqual(toolviews_stats.update(path, date(2026, 11, 2), fake_fetcher(calls, {})), [])
            self.assertEqual(calls, [])

    def test_comma_file_is_rewritten_with_semicolons(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stats.csv"
            path.write_text("date,hits\n2026-11-01,1\n", encoding="utf-8")
            self.assertEqual(toolviews_stats.update(path, date(2026, 11, 2), fake_fetcher([], {})), [])
            self.assertEqual(path.read_text(encoding="utf-8").splitlines(), ["date;hits", "2026-11-01;1"])

    def test_unique_visitors_column_is_dropped(self):
        for content in ("date;hits;unique_visitors\n2026-11-01;1;0\n", "date,hits,unique_visitors\n2026-11-01,1,0\n"):
            with self.subTest(content=content), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "stats.csv"
                path.write_text(content, encoding="utf-8")
                self.assertEqual(toolviews_stats.update(path, date(2026, 11, 2), fake_fetcher([], {})), [])
                self.assertEqual(path.read_text(encoding="utf-8").splitlines(), ["date;hits", "2026-11-01;1"])

    def test_unexpected_response_raises_and_writes_nothing(self):
        bad_responses = [
            {},
            {"results": []},
            {"results": {"2026-11-01": {"autre-outil": 3}}},
            {"results": {"2026-11-01": 3}},
            {"results": {"2026-11-01": {"wikipedia2book": "3"}}},
            {"results": {"hier": {"wikipedia2book": 3}}},
        ]
        for response in bad_responses:
            with self.subTest(response=response), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "stats.csv"
                with self.assertRaises(toolviews_stats.UnexpectedResponse):
                    toolviews_stats.update(path, date(2026, 11, 2), lambda url: response)
                self.assertFalse(path.exists())

    def test_empty_day_counts_as_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stats.csv"
            fetch = lambda url: {"results": {"2026-11-01": {}, "2026-11-02": {"wikipedia2book": 4}}}
            self.assertEqual(toolviews_stats.update(path, date(2026, 11, 3), fetch), ["2026-11-01", "2026-11-02"])
            self.assertEqual(read(path), [("2026-11-01", "0"), ("2026-11-02", "4")])


if __name__ == "__main__":
    unittest.main()
