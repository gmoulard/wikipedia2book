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

import json
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
from pathlib import Path

from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import perf_check


def fake_pdf(pages):
    buffer = BytesIO()
    document = canvas.Canvas(buffer)
    for _ in range(pages):
        document.showPage()
    document.save()
    return buffer.getvalue()


class FakeApp(BaseHTTPRequestHandler):
    fail = None
    received = []

    def log_message(self, *args):
        pass

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        FakeApp.received.append((self.path, body))
        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson")
        self.end_headers()
        titles = [article["title"] for article in body["main_articles"]]
        for step, title in enumerate(titles, 1):
            self.wfile.write((json.dumps({"type": "progress", "step": step, "code": "fetch_article", "title": title}) + "\n").encode())
        if FakeApp.fail:
            self.wfile.write((json.dumps({"type": "error", "detail": FakeApp.fail}) + "\n").encode())
            return
        self.wfile.write((json.dumps({"type": "progress", "step": len(titles) + 1, "code": "cover_and_toc"}) + "\n").encode())
        pdf = fake_pdf(len(titles) + 2)
        self.wfile.write((json.dumps({"type": "done", "size": len(pdf)}) + "\n").encode())
        self.wfile.write(pdf)


class PerfCheckTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), FakeApp)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def setUp(self):
        FakeApp.fail = None
        FakeApp.received.clear()

    def test_scenarios_file_matches_levels(self):
        config = json.loads(perf_check.SCENARIOS.read_text(encoding="utf-8"))
        self.assertEqual(config["levels"]["min"]["scenarios"], ["50-pages", "200-pages"])
        for level in config["levels"].values():
            for name in level["scenarios"]:
                self.assertIn(name, config["scenarios"])
        for name, count in (("50-pages", 10), ("200-pages", 10), ("20-articles", 20)):
            self.assertEqual(len(set(config["scenarios"][name]["articles"])), count)
        self.assertTrue(set(config["levels"]["min"]["scenarios"]) <= set(config["levels"]["max"]["scenarios"]))

    def test_project_builds_chapters_and_options(self):
        body = perf_check.project("x", {"articles": ["A", "B", "C", "D", "E"], "chapters": 2, "options": {"page_numbers": False}}, "fr")
        self.assertEqual([article["title"] for article in body["main_articles"]], ["A", "B", "C", "D", "E"])
        self.assertTrue(all(article["selected"] for article in body["main_articles"]))
        self.assertEqual([chapter["article_keys"] for chapter in body["chapters"]], [["fr:title:a", "fr:title:b", "fr:title:c"], ["fr:title:d", "fr:title:e"]])
        self.assertFalse(body["page_numbers"])

    def test_generate_measures_phases_and_counts_pages(self):
        body = perf_check.project("x", {"articles": ["A", "B", "C"]}, "fr")
        run = perf_check.generate(self.url, body, "fr")
        self.assertEqual(run["pages"], 5)
        self.assertAlmostEqual(run["total_s"], run["wikipedia_s"] + run["app_s"] + run["transfer_s"], places=6)
        self.assertEqual(FakeApp.received[0][0], "/api/pdf/stream?language=fr")

    def test_generate_raises_on_error_event(self):
        FakeApp.fail = "Impossible de télécharger le PDF Wikipédia pour « A »."
        with self.assertRaises(perf_check.GenerationError):
            perf_check.generate(self.url, perf_check.project("x", {"articles": ["A"]}, "fr"), "fr")

    def test_verdict_thresholds_on_application_time_per_page(self):
        reference = {"pages": 100, "app_s": 10.0, "total_s": 40.0}
        def measure(app_s, pages=100):
            return {"pages": pages, "app_s": app_s, "total_s": 99.0}
        self.assertEqual(perf_check.verdict(measure(12.0), reference)[0], "ok")
        self.assertEqual(perf_check.verdict(measure(14.0), reference)[0], "à surveiller")
        self.assertEqual(perf_check.verdict(measure(16.0), reference)[0], "régression")
        self.assertEqual(perf_check.verdict(measure(16.0, pages=200), reference)[0], "ok")
        self.assertTrue(perf_check.verdict(measure(10.0, pages=120), reference)[1])
        self.assertEqual(perf_check.verdict(measure(10.0), None)[0], "nouveau")

    def test_report_marks_failures_and_divergence(self):
        reference = {"created": "2026-11-15", "environment": {"label": "ci"}, "scenarios": {"50-pages": {"pages": 50, "app_s": 5.0, "total_s": 20.0}}}
        measures = {"50-pages": {"pages": 50, "total_s": 30.0, "wikipedia_s": 22.0, "app_s": 8.0, "transfer_s": 0.0}}
        text, verdicts = perf_check.report("min", self.url, measures, reference, {"200-pages": "boom"})
        self.assertEqual(verdicts, {"50-pages": "régression", "200-pages": "échec"})
        self.assertIn("+60%", text)
        self.assertIn("+50%", text)
        self.assertIn("200-pages : boom", text)

    def test_median_run(self):
        runs = [{"total_s": t, "wikipedia_s": t, "app_s": t, "transfer_s": 0.0, "pages": 50, "size_bytes": 1} for t in (3.0, 1.0, 2.0)]
        self.assertEqual(perf_check.median_run(runs)["app_s"], 2.0)
        self.assertEqual(perf_check.median_run(runs)["runs"], 3)


if __name__ == "__main__":
    unittest.main()
