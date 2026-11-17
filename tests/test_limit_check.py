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
import threading
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import limit_check
from benchmark import GenerationError


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

    def test_search_doubles_then_halves_the_interval(self):
        waited = []
        titles = [f"Article {index}" for index in range(2000)]
        results, passed, failed = limit_check.search("http://x", titles, "fr", 100, 50, 2000, generator=self.fake(730), wait=waited.append)
        self.assertEqual(self.calls, [100, 200, 400, 800, 600, 700, 750])
        self.assertEqual((passed, failed), (700, 750))
        self.assertEqual(waited, ["http://x", "http://x"])
        self.assertEqual(len(results), len(self.calls))

    def test_search_stops_at_the_maximum_when_nothing_fails(self):
        results, passed, failed = limit_check.search("http://x", ["A"] * 300, "fr", 100, 50, 300, generator=self.fake(1000), wait=lambda url: None)
        self.assertEqual(self.calls, [100, 200, 300])
        self.assertEqual((passed, failed), (300, None))
        self.assertIn("non atteinte", limit_check.summary(passed, failed, 300))

    def test_search_goes_below_the_start_when_it_fails(self):
        results, passed, failed = limit_check.search("http://x", ["A"] * 300, "fr", 100, 10, 300, generator=self.fake(30), wait=lambda url: None)
        self.assertEqual(self.calls, [100, 50, 20, 40, 30])
        self.assertEqual((passed, failed), (30, 40))
        self.assertEqual(limit_check.summary(passed, failed, 300), "Limite entre 30 articles (réussi) et 40 articles (échec).")

    def test_wait_for_server_retries_until_the_server_answers(self):
        attempts = []
        slept = []

        class Answer:
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

        def opener(request, timeout):
            attempts.append(request.full_url)
            if len(attempts) < 3:
                raise OSError("connexion refusée")
            return Answer()

        limit_check.wait_for_server("http://x", opener=opener, sleep=slept.append)
        self.assertEqual(attempts, ["http://x/api/version"] * 3)
        self.assertEqual(slept, [10, 10])

    def test_save_dir_names_each_pdf_after_its_step(self):
        targets = []

        def generator(base_url, body, language, timeout, save_to=None):
            targets.append(save_to)
            return {"total_s": 1.0, "wikipedia_s": 0.5, "app_s": 0.3, "transfer_s": 0.2, "pages": 1, "size_bytes": 1}

        limit_check.run("http://x", [2, 3], ["A", "B", "C"], "fr", generator=generator, save_dir=Path("tmp"))
        self.assertEqual(targets, [Path("tmp") / "limite-2-articles.pdf", Path("tmp") / "limite-3-articles.pdf"])
        limit_check.run("http://x", [2], ["A", "B"], "fr", generator=self.fake(10))
        self.assertEqual(self.calls, [2])

    def test_report_shows_successes_and_the_failure(self):
        table = limit_check.report([
            {"articles": 25, "pages": 250, "size_bytes": 2_500_000, "wikipedia_s": 0.5, "app_s": 0.3, "transfer_s": 0.2, "total_s": 1.0},
            {"articles": 50, "error": "GenerationError: flux interrompu", "after_s": 12.0},
        ])
        self.assertIn("| 25 | 250 | 2.5 Mo |", table)
        self.assertIn("échec : GenerationError: flux interrompu", table)


class ParallelTest(unittest.TestCase):
    def setUp(self):
        self.lock = threading.Lock()
        self.running = 0
        self.peak = 0
        self.waited = []

    def fake(self, limit):

        def generator(base_url, body, language, timeout):
            with self.lock:
                self.running += 1
                self.peak = max(self.peak, self.running)
                position = self.running
            time.sleep(0.05)
            with self.lock:
                self.running -= 1
            if position > limit:
                raise GenerationError("flux interrompu avant la fin de la génération")
            return {"total_s": 2.0 + position / 10}
        return generator

    def test_generations_of_a_step_run_at_the_same_time_until_a_step_fails(self):
        body = {"name": "Épaves", "main_articles": []}
        results = limit_check.run_parallel("http://x", [3, 6, 12], body, "fr", generator=self.fake(8), wait=self.waited.append)
        self.assertEqual([r["books"] for r in results], [3, 6, 12])
        self.assertEqual([(r["passed"], r["failed"]) for r in results[:2]], [(3, 0), (6, 0)])
        self.assertEqual(results[2]["failed"], 4)
        self.assertEqual(self.peak, 12)
        self.assertEqual(self.waited, ["http://x"])
        self.assertIn("GenerationError: flux interrompu avant la fin de la génération", results[2]["errors"])

    def test_parallel_report(self):
        table = limit_check.parallel_report([
            {"books": 10, "passed": 10, "failed": 0, "wall_s": 30.0, "median_s": 25.0, "slowest_s": 29.0, "errors": []},
            {"books": 50, "passed": 0, "failed": 50, "wall_s": 90.0, "median_s": None, "slowest_s": None, "errors": ["OSError: boom"]},
        ])
        self.assertIn("| 10 | 10 | 0 | 30.0 s | 25.0 s | 29.0 s | — |", table)
        self.assertIn("| 50 | 0 | 50 | 90.0 s | — | — | OSError: boom |", table)

    def test_reference_book_is_the_frozen_sample(self):
        book = limit_check.book_from_json(limit_check.REFERENCE_BOOK)
        self.assertEqual(len(book["main_articles"]), 10)


if __name__ == "__main__":
    unittest.main()
