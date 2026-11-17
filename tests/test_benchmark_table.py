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
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import benchmark_table as bt

CSV = """date,version,target,level,scenario,pages,wikipedia_s,application_s,transfer_s,total_s,app_per_page_delta_pct,verdict
2026-11-15,1.8.2,Toolforge,max,50-pages,51,6.88,0.4,1.96,9.24,-47,ok
2026-11-15,1.8.2,Toolforge,max,1-article,5,0.37,0.22,0.31,0.9,+57,watch
2026-11-16,1.9.5,workflow,max,1-article,4,0.19,0.27,0,0.46,+141,regression
2026-11-16,1.9.7+,Toolforge,trial,livre-exemple-images,107,3.83,3.17,3.47,10.47,,new
2026-11-17,1.12.0,workflow,max,livre-reference-images,,,,,,,failure
2026-11-17,1.12.0+,workflow,min,50-pages,50,0.61,0.56,0.01,1.16,-38,ok
2026-11-17,1.12.0+,workflow,min,50-pages,50,0.6,0.5,0.01,1.1,-40,ok
"""


class BenchmarkTableTest(unittest.TestCase):
    def setUp(self):
        self.rows = bt.read_rows(CSV)

    def test_one_row_per_run_and_one_column_per_scenario(self):
        lines = bt.table(self.rows, "fr").split("\n")
        self.assertEqual(lines[0], "| Version | Date | Cible | Niveau | 50 p. | 1 art. | Livre exemple | Livre de référence |")
        self.assertEqual(lines[2], "| 1.8.2 | 2026-11-15 | Toolforge | max | ✅ | ⚠️ (+57 %) |  |  |")
        self.assertEqual(lines[3], "| 1.9.5 | 2026-11-16 | workflow | max |  | ❌ (+141 %) |  |  |")
        self.assertIn('essai (1 génération) |  |  | <span class="bench-new">nouveau</span> |', lines[4])
        self.assertTrue(lines[5].endswith("| ❌ échec |"))
        self.assertEqual(len(lines), 8)

    def test_english_labels(self):
        text = bt.table(self.rows, "en")
        self.assertIn("| Version | Date | Target | Level |", text)
        self.assertIn("⚠️ (+57%)", text)
        self.assertIn("trial (1 generation)", text)
        self.assertIn("❌ failed", text)

    def test_block_is_replaced_between_markers_only(self):
        text = f"avant\n  {bt.START}\n  ancien\n  {bt.END}\naprès\n"
        updated = bt.update_spec(text, "fr", self.rows)
        self.assertTrue(updated.startswith("avant\n  " + bt.START))
        self.assertTrue(updated.endswith(bt.END + "\naprès\n"))
        self.assertNotIn("ancien", updated)
        self.assertEqual(bt.update_spec(updated, "fr", self.rows), updated)
        self.assertIn("\r\n", bt.update_spec(text.replace("\n", "\r\n"), "fr", self.rows))

    def test_unknown_values_are_refused(self):
        with self.assertRaises(ValueError):
            bt.read_rows(CSV.replace(",watch", ",maybe"))
        with self.assertRaises(ValueError):
            bt.read_rows(CSV.replace("1-article", "2-articles"))

    def test_repository_csv_matches_both_specifications(self):
        rows = bt.read_rows(bt.CSV_PATH.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(rows), 80)
        for lang, path in bt.SPECS.items():
            text = path.read_bytes().decode("utf-8")
            self.assertEqual(bt.update_spec(text, lang, rows), text, lang)


if __name__ == "__main__":
    unittest.main()
