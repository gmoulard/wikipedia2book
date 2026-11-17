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
import sys
import tempfile
import types
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    import weasyprint  # noqa: F401
except Exception:
    fake = types.ModuleType("weasyprint")
    fake.HTML = lambda *a, **k: None
    sys.modules["weasyprint"] = fake

from fastapi import FastAPI
from fastapi.testclient import TestClient

import app.main as main

TOOLFORGE_DATE = "Tue, 01 Jan 1980 00:00:01 GMT"
TOOLFORGE_MTIME = 315532801


class StaticCacheTest(unittest.TestCase):
    def test_served_files_have_a_content_etag_and_no_date(self):
        client = TestClient(main.app)
        response = client.get("/static/i18n.js")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("last-modified", response.headers)
        self.assertEqual(response.headers["cache-control"], "no-cache")
        self.assertEqual(client.get("/static/i18n.js", headers={"If-Modified-Since": TOOLFORGE_DATE}).status_code, 200)
        self.assertEqual(client.get("/static/i18n.js", headers={"If-None-Match": response.headers["etag"]}).status_code, 304)

    def test_same_date_and_size_but_new_content_is_sent_again(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "i18n.js"
            app = FastAPI()
            app.mount("/static", main.ContentStaticFiles(directory=folder), name="static")
            client = TestClient(app)

            path.write_text("const A = 1;", encoding="utf-8")
            os.utime(path, (TOOLFORGE_MTIME, TOOLFORGE_MTIME))
            first = client.get("/static/i18n.js")
            path.write_text("const B = 2;", encoding="utf-8")
            os.utime(path, (TOOLFORGE_MTIME, TOOLFORGE_MTIME))
            second = client.get("/static/i18n.js", headers={"If-None-Match": first.headers["etag"], "If-Modified-Since": TOOLFORGE_DATE})

        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.text, "const B = 2;")
        self.assertNotEqual(first.headers["etag"], second.headers["etag"])


if __name__ == "__main__":
    unittest.main()
