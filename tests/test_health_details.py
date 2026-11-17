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
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    import weasyprint  # noqa: F401
except Exception:
    fake = types.ModuleType("weasyprint")
    fake.HTML = lambda *a, **k: None
    sys.modules["weasyprint"] = fake

from fastapi.testclient import TestClient

import app.main as main

# NE PAS laisser l'assemblage dans un processus séparé ici : ces tests remplacent generate_pdf et fit_pdf_to_format dans main, ce que le processus enfant ne verrait pas (tests/test_isolation.py couvre le processus séparé).
main.ISOLATE_ASSEMBLY = False


MONITOR_TOKEN = "jeton-de-supervision-pour-les-tests-0123"


class HealthDetailsTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.root = Path(self.folder.name)
        (self.root / "status").write_text("Name:\tpython\nVmHWM:\t  2048 kB\nVmRSS:\t  1024 kB\n")
        self.patches = [
            patch.object(main, "CGROUP_DIRECTORY", self.root / "cgroup"),
            patch.object(main, "PROCESS_STATUS", self.root / "status"),
        ]
        for item in self.patches:
            item.start()
        (self.root / "cgroup").mkdir()

    def tearDown(self):
        for item in self.patches:
            item.stop()
        self.folder.cleanup()

    def details(self):
        with patch.object(main, "MONITOR_TOKEN", MONITOR_TOKEN):
            response = TestClient(main.app).get("/api/health/details", headers={"Authorization": f"Bearer {MONITOR_TOKEN}"})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("access-control-allow-origin", response.headers)
        self.assertEqual(response.headers["x-frame-options"], "DENY")
        self.assertEqual(response.headers["cache-control"], "no-store")
        return response.json()

    def test_cgroup_v2_memory_and_process(self):
        (self.root / "cgroup" / "memory.current").write_text("536870912\n")
        (self.root / "cgroup" / "memory.max").write_text("2147483648\n")
        (self.root / "cgroup" / "memory.peak").write_text("1073741824\n")
        memory = self.details()["memory"]
        self.assertEqual(memory["used_bytes"], 536870912)
        self.assertEqual(memory["limit_bytes"], 2147483648)
        self.assertEqual(memory["peak_bytes"], 1073741824)
        self.assertEqual(memory["used_percent"], 25.0)
        self.assertEqual(memory["process_rss_bytes"], 1024 * 1024)
        self.assertEqual(memory["process_peak_rss_bytes"], 2048 * 1024)

    def test_cgroup_v2_without_limit(self):
        (self.root / "cgroup" / "memory.current").write_text("1000\n")
        (self.root / "cgroup" / "memory.max").write_text("max\n")
        memory = self.details()["memory"]
        self.assertEqual(memory["used_bytes"], 1000)
        self.assertIsNone(memory["limit_bytes"])
        self.assertIsNone(memory["used_percent"])

    def test_cgroup_v1_and_unlimited_value(self):
        legacy = self.root / "cgroup" / "memory"
        legacy.mkdir()
        (legacy / "memory.usage_in_bytes").write_text("300\n")
        (legacy / "memory.limit_in_bytes").write_text("9223372036854771712\n")
        (legacy / "memory.max_usage_in_bytes").write_text("400\n")
        memory = self.details()["memory"]
        self.assertEqual((memory["used_bytes"], memory["limit_bytes"], memory["peak_bytes"]), (300, None, 400))

    def test_no_cgroup_gives_nulls(self):
        memory = self.details()["memory"]
        self.assertIsNone(memory["used_bytes"])
        self.assertIsNone(memory["limit_bytes"])

    def test_temporary_space_counts_only_generation_folders(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory) / (main.TEMPORARY_PREFIX + "abc")
            work.mkdir()
            (work / "part-0.pdf").write_bytes(b"x" * 1500)
            (Path(directory) / "other.bin").write_bytes(b"y" * 9000)
            with patch.object(main.tempfile, "gettempdir", lambda: directory):
                temporary = self.details()["temporary"]
        self.assertEqual(temporary["generation_files_bytes"], 1500)
        self.assertGreater(temporary["total_bytes"], 0)
        self.assertGreaterEqual(temporary["free_bytes"], 0)

    def test_not_counted_in_hourly_hits(self):
        main.hourly_hits.clear()
        self.details()
        self.assertEqual(main.hourly_hits, {})

    def test_generations_in_progress_counts_running_books(self):
        from tests.test_pdf_stream import FakeClient, _make_pdf, _project
        from app.models import Project

        seen = []

        async def scenario():
            book = main.build_book_pdf(Project(**_project()), main._selected_items(Project(**_project())), "fr")
            async for event in book:
                seen.append(main.generations_in_progress)
            seen.append(main.generations_in_progress)

        with patch.object(main, "MediaWikiClient", FakeClient), patch.object(main, "generate_pdf", lambda html: _make_pdf(1)):
            asyncio.run(scenario())
        self.assertEqual(set(seen[:-1]), {1})
        self.assertEqual(seen[-1], 0)


if __name__ == "__main__":
    unittest.main()
