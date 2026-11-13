import csv
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import toolviews_stats


def fake_fetcher(calls, hits, unique):
    def fetch(url):
        calls.append(url)
        source = unique if "/unique/" in url else hits
        return {"results": {day: {"wikipedia2book": n} for day, n in source.items()}}
    return fetch


class ToolviewsStatsTest(unittest.TestCase):
    def test_fills_only_missing_days_and_skips_today(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stats.csv"
            path.write_text("date;hits;unique_visitors\n2026-11-01;10;3\n", encoding="utf-8")
            calls = []
            fetch = fake_fetcher(calls, {"2026-11-02": 20, "2026-11-03": 30}, {"2026-11-02": 5})
            added = toolviews_stats.update(path, date(2026, 11, 4), fetch)
            self.assertEqual(added, ["2026-11-02", "2026-11-03"])
            self.assertTrue(all(url.endswith("/2026-11-02/2026-11-03") for url in calls))
            with path.open(encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle, delimiter=";"))
            self.assertEqual(
                [(r["date"], r["hits"], r["unique_visitors"]) for r in rows],
                [("2026-11-01", "10", "3"), ("2026-11-02", "20", "5"), ("2026-11-03", "30", "0")],
            )

    def test_days_without_visits_are_zero_until_last_published_day(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stats.csv"
            added = toolviews_stats.update(path, date(2026, 11, 5), fake_fetcher([], {"2026-11-03": 7}, {}))
            self.assertEqual(added, ["2026-11-01", "2026-11-02", "2026-11-03"])
            with path.open(encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle, delimiter=";"))
            self.assertEqual(
                [(r["date"], r["hits"], r["unique_visitors"]) for r in rows],
                [("2026-11-01", "0", "0"), ("2026-11-02", "0", "0"), ("2026-11-03", "7", "0")],
            )

    def test_nothing_written_when_api_has_no_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stats.csv"
            self.assertEqual(toolviews_stats.update(path, date(2026, 11, 3), fake_fetcher([], {}, {})), [])
            self.assertFalse(path.exists())

    def test_no_call_when_up_to_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stats.csv"
            path.write_text("date;hits;unique_visitors\n2026-11-01;1;1\n", encoding="utf-8")
            calls = []
            self.assertEqual(toolviews_stats.update(path, date(2026, 11, 2), fake_fetcher(calls, {}, {})), [])
            self.assertEqual(calls, [])

    def test_comma_file_is_rewritten_with_semicolons(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stats.csv"
            path.write_text("date,hits,unique_visitors\n2026-11-01,1,1\n", encoding="utf-8")
            self.assertEqual(toolviews_stats.update(path, date(2026, 11, 2), fake_fetcher([], {}, {})), [])
            self.assertEqual(path.read_text(encoding="utf-8").splitlines(), ["date;hits;unique_visitors", "2026-11-01;1;1"])


if __name__ == "__main__":
    unittest.main()
