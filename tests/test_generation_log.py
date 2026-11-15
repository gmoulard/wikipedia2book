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
import contextlib
import io
import json
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
from app.models import Project
from tests.test_pdf_stream import FakeClient, _make_pdf, _project

# NE PAS laisser l'assemblage dans un processus séparé ici : ces tests remplacent generate_pdf dans main, ce que le processus enfant ne verrait pas.
main.ISOLATE_ASSEMBLY = False


class FailingClient(FakeClient):
    async def get_article_pdf(self, title, language, paper="a4", site="wikipedia"):
        raise main.MediaWikiError(f"PDF indisponible pour {title}")


async def run_book(stop_at=None):
    project = Project(**_project())
    book = main.build_book_pdf(project, main._selected_items(project), "fr")
    async with contextlib.aclosing(book):
        async for event in book:
            if event.get("code") == stop_at:
                return


class GenerationLogTest(unittest.TestCase):
    def setUp(self):
        main.generation_log.clear()
        self.client = TestClient(main.app)
        self.output = io.StringIO()
        self.patches = [
            patch.object(main, "generate_pdf", lambda html: _make_pdf(1)),
            contextlib.redirect_stdout(self.output),
        ]
        for item in self.patches:
            item.__enter__()

    def tearDown(self):
        for item in reversed(self.patches):
            item.__exit__(None, None, None)

    def journal(self):
        response = self.client.get(main.GENERATION_LOG_PATH)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["access-control-allow-origin"], "*")
        self.assertEqual(response.headers["cache-control"], "no-store")
        return response.json()

    def test_successful_generation_lists_every_stage_with_memory(self):
        with patch.object(main, "MediaWikiClient", FakeClient):
            asyncio.run(run_book())
        entry = self.journal()["generations"][0]
        self.assertEqual(entry["status"], "done")
        self.assertEqual(entry["articles"], 2)
        self.assertGreater(entry["size_bytes"], 0)
        stages = [stage["stage"] for stage in entry["stages"]]
        for name in ("start", "downloads_done", "assembly_start", "render_cover", "render_toc", "render_license", "merge", "outline_and_links", "save"):
            self.assertIn(name, stages)
        self.assertLess(stages.index("render_license"), stages.index("merge"))
        assembly = [stage for stage in entry["stages"] if stage["process"] == "assembly"]
        self.assertTrue(assembly)
        for stage in entry["stages"]:
            self.assertIn("container_bytes", stage)
            self.assertIn("rss_bytes", stage)
            self.assertIsInstance(stage["at_s"], float)

    def test_journal_holds_no_article_title_even_on_error(self):
        with patch.object(main, "MediaWikiClient", FailingClient):
            with self.assertRaises(main.MediaWikiError):
                asyncio.run(run_book())
        body = json.dumps(self.journal())
        entry = self.journal()["generations"][0]
        self.assertEqual(entry["status"], "error")
        self.assertEqual(entry["error"], "MediaWikiError")
        for title in ("Chat", "Chien"):
            self.assertNotIn(title, body)
            self.assertNotIn(title, self.output.getvalue())

    def test_abandoned_generation_is_marked_aborted(self):
        with patch.object(main, "MediaWikiClient", FakeClient):
            asyncio.run(run_book(stop_at="assemble"))
        self.assertEqual(self.journal()["generations"][0]["status"], "aborted")

    def test_each_stage_is_also_written_to_standard_output(self):
        with patch.object(main, "MediaWikiClient", FakeClient):
            asyncio.run(run_book())
        lines = [json.loads(line) for line in self.output.getvalue().splitlines() if line.startswith("{")]
        self.assertIn("downloads_done", [line.get("stage") for line in lines])
        self.assertEqual(lines[-1]["status"], "done")

    def test_newest_first_and_bounded(self):
        with patch.object(main, "MediaWikiClient", FakeClient):
            for _ in range(3):
                asyncio.run(run_book())
        ids = [entry["id"] for entry in self.journal()["generations"]]
        self.assertEqual(ids, sorted(ids, reverse=True))
        self.assertEqual(main.generation_log.maxlen, main.GENERATION_LOG_KEEP)

    def test_not_counted_in_hourly_hits(self):
        main.hourly_hits.clear()
        self.journal()
        self.assertEqual(main.hourly_hits, {})


if __name__ == "__main__":
    unittest.main()
