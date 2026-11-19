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

import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import toolforge_hourly
import toolviews_chart

POD = "wikipedia2book-7d9f-abcde"
FAKE_KUBECTL = """#!/bin/bash
if [ "$1" = get ]; then printf 'wikipedia2book-7d9f-abcde\\nother-job-xyz\\n'; exit 0; fi
cat <<'LOG'
2026-11-15T06:59:59.1Z INFO:     10.0.0.1:0 - "GET / HTTP/1.1" 200 OK
2026-11-15T07:01:00.1Z INFO:     10.0.0.1:0 - "GET /static/app.js HTTP/1.1" 200 OK
2026-11-15T07:02:00.1Z INFO:     10.0.0.2:0 - "POST /api/pdf/stream?language=fr HTTP/1.1" 200 OK
2026-11-15T07:03:00.1Z INFO:     Started server process [1]
2026-11-15T07:04:00.1Z {"generation": 1, "at_s": 0.1, "stage": "download", "process": "server", "rss": 1}
2026-11-15T07:05:00.1Z {"generation": 1, "status": "done", "duration_s": 12.5}
2026-11-15T07:06:00.1Z {"generation": 2, "status": "error", "duration_s": 3.0, "error": "x"}
2026-11-15T08:00:00.1Z {"generation": 3, "status": "done", "duration_s": 9.0}
2026-11-15T08:01:00.1Z INFO:     10.0.0.3:0 - "GET /?q={\"generation\": 4, \"status\": \"done\"} HTTP/1.1" 200 OK
LOG
"""


def capture(*lines, generations=()):
    return "\n".join(["bannière éventuelle", "BEGIN-HOURLY", *lines, "END-HOURLY", "BEGIN-GENERATIONS", *generations, "END-GENERATIONS", ""])


class ParseTest(unittest.TestCase):
    def test_parse_lines_between_markers(self):
        self.assertEqual(
            toolforge_hourly.parse(capture(f"{POD};2026-11-15T06;1", f"{POD};2026-11-15T07;2")),
            {("2026-11-15T06", POD): 1, ("2026-11-15T07", POD): 2},
        )

    def test_empty_capture_is_valid(self):
        self.assertEqual(toolforge_hourly.parse(capture()), {})

    def test_unexpected_input_raises(self):
        for text in (
            f"BEGIN-HOURLY\n{POD};2026-11-15T06;1\n",
            capture("10.0.0.1 - GET /"),
            capture(f"{POD};2026-11-15T25;1"),
            capture(f"autre-pod;2026-11-15T06;1"),
        ):
            with self.subTest(text=text), self.assertRaises(ValueError):
                toolforge_hourly.parse(text)


class MergeTest(unittest.TestCase):
    def test_same_pod_keeps_max_and_old_hours_are_dropped(self):
        rows = {("2026-11-01T00", POD): 9, ("2026-11-15T06", POD): 5, ("2026-11-15T06", "wikipedia2book-old"): 3}
        merged = toolforge_hourly.merge(rows, {("2026-11-15T06", POD): 4, ("2026-11-15T07", POD): 2}, datetime(2026, 11, 15, 8, tzinfo=timezone.utc))
        self.assertEqual(merged, {("2026-11-15T06", POD): 5, ("2026-11-15T06", "wikipedia2book-old"): 3, ("2026-11-15T07", POD): 2})

    def test_csv_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "hourly.csv"
            rows = {("2026-11-15T07", POD): 2, ("2026-11-15T06", POD): 1}
            toolforge_hourly.write_rows(path, rows)
            self.assertEqual(path.read_text(encoding="utf-8").splitlines()[0], "hour;pod;hits")
            self.assertEqual(toolforge_hourly.read_rows(path), rows)


@unittest.skipUnless(shutil.which("bash"), "bash introuvable (poste Windows sans Git Bash dans le PATH) ; le test tourne en intégration continue sous Linux")
class RemoteScriptTest(unittest.TestCase):
    def test_counts_requests_per_pod_and_hour(self):
        with tempfile.TemporaryDirectory() as tmp:
            kubectl = Path(tmp) / "kubectl"
            kubectl.write_text(FAKE_KUBECTL, encoding="utf-8")
            kubectl.chmod(kubectl.stat().st_mode | stat.S_IEXEC)
            env = {**os.environ, "PATH": f"{tmp}{os.pathsep}{os.environ['PATH']}"}
            result = subprocess.run(["bash", str(ROOT / "scripts" / "toolforge-hourly.sh")], capture_output=True, text=True, env=env, check=True)
            self.assertEqual(toolforge_hourly.parse(result.stdout), {("2026-11-15T06", POD): 1, ("2026-11-15T07", POD): 2})
            self.assertEqual(
                toolforge_hourly.parse_generations(result.stdout),
                {("2026-11-15T07", POD, "done"): 1, ("2026-11-15T07", POD, "error"): 1, ("2026-11-15T08", POD, "done"): 1},
            )


class GenerationsTest(unittest.TestCase):
    def test_parse_merge_and_round_trip(self):
        text = capture(generations=(f"{POD};2026-11-15T07;done;3", f"{POD};2026-11-15T07;aborted;1"))
        captured = toolforge_hourly.parse_generations(text)
        self.assertEqual(captured, {("2026-11-15T07", POD, "done"): 3, ("2026-11-15T07", POD, "aborted"): 1})
        merged = toolforge_hourly.merge_generations({("2026-11-15T07", POD, "done"): 5, ("2026-11-01T00", POD, "error"): 2}, captured)
        self.assertEqual(merged, {("2026-11-15T07", POD, "done"): 5, ("2026-11-15T07", POD, "aborted"): 1, ("2026-11-01T00", POD, "error"): 2})
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "generations.csv"
            toolforge_hourly.write_generations(path, merged)
            self.assertEqual(path.read_text(encoding="utf-8").splitlines()[0], "hour;pod;status;generations")
            self.assertEqual(toolforge_hourly.read_generations(path), merged)

    def test_unexpected_generation_lines_raise(self):
        for text in (
            "\n".join(["BEGIN-HOURLY", "END-HOURLY", ""]),
            capture(generations=(f"{POD};2026-11-15T07;running;1",)),
            capture(generations=(f"{POD};2026-11-15T07;done",)),
        ):
            with self.subTest(text=text), self.assertRaises(ValueError):
                toolforge_hourly.parse_generations(text)

    def test_daily_chart_sums_pods_and_statuses_and_fills_gaps(self):
        generations = {
            ("2026-11-15T07", POD, "done"): 3, ("2026-11-15T09", "wikipedia2book-old", "error"): 1,
            ("2026-11-17T00", POD, "aborted"): 2,
        }
        page = toolviews_chart.build_page({"2026-11-01": {"date": "2026-11-01", "hits": "1"}}, {}, generations)
        self.assertIn("**6** generations, 3 finished, 1 with an error, 2 abandoned", page)
        self.assertIn("Depuis le 15/11/2026 : **6** générations", page)
        chart = re.search(r"```mermaid\n([^`]*Daily generations[^`]*)```", page).group(1)
        self.assertIn('x-axis ["15", "16", "17"]', chart)
        self.assertIn('y-axis "Generations"', chart)
        self.assertIn("bar [4, 0, 2]", chart)

    def test_no_generations_section_without_data(self):
        self.assertNotIn("generations", toolviews_chart.build_page({"2026-11-01": {"date": "2026-11-01", "hits": "1"}}, {}, {}))


class HourlyChartTest(unittest.TestCase):
    def test_hourly_chart_sums_pods_fills_gaps_and_keeps_36_hours(self):
        hourly = {("2026-11-13T00", POD): 7, ("2026-11-14T10", POD): 1, ("2026-11-14T10", "wikipedia2book-old"): 2, ("2026-11-14T12", POD): 4}
        page = toolviews_chart.build_page({"2026-11-01": {"date": "2026-11-01", "hits": "1"}}, hourly)
        chart = re.findall(r"```mermaid\n(.*?)```", page, re.S)[0]
        self.assertIn("Hourly hits (UTC) 13/11 01h - 14/11 12h", chart)
        labels = re.search(r"x-axis \[(.*)\]", chart).group(1).split(", ")
        self.assertEqual(len(labels), 36)
        self.assertTrue(re.search(r"bar \[[0, ]*3, 0, 4\]", chart))

    def test_no_hourly_section_without_data(self):
        page = toolviews_chart.build_page({"2026-11-01": {"date": "2026-11-01", "hits": "1"}}, {})
        self.assertNotIn("Hourly", page)
        self.assertEqual(len(re.findall(r"```mermaid", page)), 2)

    def test_short_history_starts_at_oldest_hour(self):
        page = toolviews_chart.build_page({"2026-11-01": {"date": "2026-11-01", "hits": "1"}}, {("2026-11-15T06", POD): 1, ("2026-11-15T07", POD): 2})
        self.assertIn('x-axis ["06", "07"]', page)


if __name__ == "__main__":
    unittest.main()
