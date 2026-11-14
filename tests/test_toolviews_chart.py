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

import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import toolviews_chart


def rows(pairs):
    return {day: {"date": day, "hits": str(hits), "unique_visitors": "0"} for day, hits in pairs}


class ToolviewsChartTest(unittest.TestCase):
    def test_daily_and_monthly_charts(self):
        page = toolviews_chart.build_page(rows([("2026-11-30", 5), ("2026-12-01", 7), ("2026-12-02", 1)]))
        charts = re.findall(r"```mermaid\n(.*?)```", page, re.S)
        self.assertEqual(len(charts), 2)
        self.assertIn('x-axis ["30/11", "01/12", "02/12"]', charts[0])
        self.assertIn("bar [5, 7, 1]", charts[0])
        self.assertIn("0 --> 7", charts[0])
        self.assertIn('x-axis ["2026-11", "2026-12"]', charts[1])
        self.assertIn("bar [5, 8]", charts[1])
        self.assertIn("**13**", page)

    def test_daily_chart_keeps_last_days_only(self):
        days = [(f"2026-{month:02d}-{day:02d}", 1) for month in (1, 2, 3, 4) for day in range(1, 29)]
        page = toolviews_chart.build_page(rows(days))
        daily = re.findall(r"```mermaid\n(.*?)```", page, re.S)[0]
        labels = re.search(r"x-axis \[(.*)\]", daily).group(1).split(", ")
        self.assertEqual(len(labels), toolviews_chart.DAILY_DAYS)
        self.assertEqual(labels[-1], '"28/04"')

    def test_all_zero_axis_is_valid(self):
        page = toolviews_chart.build_page(rows([("2026-11-01", 0)]))
        self.assertIn("0 --> 1", page)

    def test_empty_or_missing_csv_fails(self):
        with self.assertRaises(ValueError):
            toolviews_chart.build_page({})
        with tempfile.TemporaryDirectory() as tmp:
            sys.argv = ["toolviews_chart.py", str(Path(tmp) / "absent.csv"), str(Path(tmp) / "stats.md")]
            self.assertEqual(toolviews_chart.main(), 1)
            self.assertFalse((Path(tmp) / "stats.md").exists())


if __name__ == "__main__":
    unittest.main()
