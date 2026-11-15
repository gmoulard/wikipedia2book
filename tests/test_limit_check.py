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

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import limit_check
from perf_check import GenerationError


class LimitCheckTest(unittest.TestCase):
    def setUp(self):
        self.calls = []

    def fake(self, limit):
        def generator(base_url, body, language, timeout):
            count = len(body["main_articles"])
            self.calls.append(count)
            if count > limit:
                raise GenerationError("flux interrompu avant la fin de la génération")
            return {"total_s": 1.0, "wikipedia_s": 0.5, "app_s": 0.3, "transfer_s": 0.2, "pages": count * 10, "size_bytes": count * 100_000}
        return generator

    def test_steps_grow_until_the_first_failure(self):
        titles = [f"Article {index}" for index in range(800)]
        results = limit_check.run("http://x", [25, 50, 100, 200], titles, "fr", generator=self.fake(60))
        self.assertEqual(self.calls, [25, 50, 100])
        self.assertEqual([result.get("pages") for result in results[:2]], [250, 500])
        self.assertIn("GenerationError", results[2]["error"])

    def test_each_step_uses_the_first_titles_of_the_list(self):
        seen = []

        def generator(base_url, body, language, timeout):
            seen.append([article["title"] for article in body["main_articles"]])
            return {"total_s": 1.0, "wikipedia_s": 0.5, "app_s": 0.3, "transfer_s": 0.2, "pages": 1, "size_bytes": 1}

        limit_check.run("http://x", [2, 3], ["A", "B", "C", "D"], "fr", generator=generator)
        self.assertEqual(seen, [["A", "B"], ["A", "B", "C"]])

    def test_report_shows_successes_and_the_failure(self):
        table = limit_check.report([
            {"articles": 25, "pages": 250, "size_bytes": 2_500_000, "wikipedia_s": 0.5, "app_s": 0.3, "transfer_s": 0.2, "total_s": 1.0},
            {"articles": 50, "error": "GenerationError: flux interrompu", "after_s": 12.0},
        ])
        self.assertIn("| 25 | 250 | 2.5 Mo |", table)
        self.assertIn("échec : GenerationError: flux interrompu", table)


if __name__ == "__main__":
    unittest.main()
