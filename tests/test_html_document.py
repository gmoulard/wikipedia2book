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
from pydantic import ValidationError
from pypdf import PdfReader

import app.main as main
from app.html_document import html_for_print
from app.json_source import JsonSourceError
from app.models import UploadedDocument
from tests.test_pdf_stream import FakeClient, _make_pdf, _png, _parse_stream, _project

main.ISOLATE_ASSEMBLY = False

PAGE = b"""<!doctype html><html><head><title>Essai</title>
<link rel="stylesheet" href="/style.css"><link rel="icon" href="/favicon.ico">
<script>alert(1)</script></head>
<body onload="steal()"><h1 onclick="x()">Bonjour</h1>
<img src="images/photo.png" srcset="big.png 2x" alt="photo">
<img src="https://example.org/absente.png" alt="absente">
<img src="https://example.org/page.html" alt="pas une image">
<iframe src="https://example.org/cadre"></iframe><form action="/x"><input></form>
<p>Texte</p></body></html>"""
CSS = b"@import url(https://example.org/autre.css); body { color: #123; background: url(https://example.org/fond.png); }"


class HtmlForPrintTest(unittest.TestCase):
    def setUp(self):
        self.requested = []
        self.files = {
            "https://example.org/dossier/images/photo.png": (_png(), "image/png"),
            "https://example.org/style.css": (CSS, "text/css"),
            "https://example.org/page.html": (b"<html></html>", "text/html"),
        }

    async def download(self, url, max_bytes, label):
        self.requested.append(url)
        if url not in self.files:
            raise JsonSourceError(502, f"Introuvable : {url}")
        return self.files[url]

    def render(self):
        return asyncio.run(html_for_print(PAGE, "https://example.org/dossier/page.html", self.download, 210, 297))

    def test_scripts_frames_forms_and_handlers_are_removed(self):
        html = self.render()
        for forbidden in ("<script", "alert(1)", "<iframe", "<form", "onload", "onclick", "srcset", "favicon"):
            self.assertNotIn(forbidden, html)
        self.assertIn("Bonjour", html)
        self.assertIn("<p>Texte</p>", html)

    def test_images_and_styles_are_inlined_through_download(self):
        html = self.render()
        self.assertIn('src="data:image/png;base64,', html)
        self.assertEqual(html.count("<img"), 1)
        self.assertIn("color: #123", html)
        self.assertNotIn("fond.png", html)
        self.assertNotIn("@import", html)
        self.assertIn("@page { size: 210mm 297mm; margin: 15mm; }", html)
        self.assertNotIn("https://example.org/autre.css", self.requested)
        self.assertNotIn("https://example.org/fond.png", self.requested)

    def test_resources_are_bounded(self):
        with patch("app.html_document.MAX_IMAGES", 0), patch("app.html_document.MAX_STYLESHEETS", 0):
            html = self.render()
        self.assertNotIn("<img", html)
        self.assertEqual(self.requested, [])


class HtmlDocumentModelTest(unittest.TestCase):
    def test_a_web_page_is_given_by_its_address(self):
        UploadedDocument(title="Page", kind="html", url="https://example.org/page.html")
        with self.assertRaises(ValidationError):
            UploadedDocument(title="Page", kind="html", mime_type="text/html", data_base64="PGh0bWw+")


class HtmlDocumentGenerationTest(unittest.TestCase):
    PAGE_URL = "https://example.org/dossier/page.html"

    def setUp(self):
        self.htmls = []

        async def fake_download(url, max_bytes, label):
            files = {self.PAGE_URL: (PAGE, "text/html"), "https://example.org/dossier/images/photo.png": (_png(), "image/png")}
            if url not in files:
                raise JsonSourceError(502, f"Introuvable : {url}")
            return files[url]

        def fake_generate(html):
            self.htmls.append(html)
            return _make_pdf(1)

        self.patches = [
            patch.object(main, "MediaWikiClient", FakeClient),
            patch.object(main, "generate_pdf", fake_generate),
            patch.object(main, "download", fake_download),
        ]
        for item in self.patches:
            item.start()
        FakeClient.fail = False
        FakeClient.wait = None
        self.client = TestClient(main.app)

    def tearDown(self):
        for item in self.patches:
            item.stop()

    def test_web_page_becomes_a_part_of_the_book(self):
        project = _project(page_numbers=False, uploaded_documents=[{"title": "Page web", "kind": "html", "url": self.PAGE_URL, "selected": True}])
        response = self.client.post("/api/pdf", json=project)
        self.assertEqual(response.status_code, 200)
        page = [html for html in self.htmls if "Bonjour" in html]
        self.assertEqual(len(page), 1)
        self.assertIn("data:image/png;base64,", page[0])
        self.assertNotIn("<script", page[0])

    def test_wikimedia_page_is_sent_to_the_sources_field(self):
        url = "https://fr.wikipedia.org/wiki/Paris"
        project = _project(uploaded_documents=[{"title": "Paris", "kind": "html", "url": url, "selected": True}])
        response = self.client.post("/api/pdf/stream", json=project)
        events = _parse_stream(response.content)
        self.assertEqual(events[-1]["type"], "error")
        self.assertIn("champ Sources", events[-1]["detail"])
        self.assertIn(url, events[-1]["detail"])

    def test_a_site_that_refuses_the_server_gets_an_explained_message(self):
        async def refusing_download(url, max_bytes, label):
            raise JsonSourceError(502, f"{label[0].upper()}{label[1:]} a été refusé par le site (HTTP 418), qui bloque sans doute les téléchargements faits depuis un serveur : {url}", refused=True)

        project = _project(uploaded_documents=[{"title": "Épaves", "kind": "html", "url": self.PAGE_URL, "selected": True}])
        with patch.object(main, "download", refusing_download):
            events = _parse_stream(self.client.post("/api/pdf/stream", json=project).content)
        detail = events[-1]["detail"]
        self.assertIn("HTTP 418", detail)
        self.assertIn("Enregistrer au format PDF", detail)
        self.assertIn(self.PAGE_URL, detail)

    def test_a_pdf_or_an_image_behind_a_web_page_address_is_kept_as_it_is(self):
        files = {"https://example.org/rapport.pdf/": (_make_pdf(3), "application/pdf"), "https://example.org/dossier/images/photo.png": (_png(), "image/png")}

        async def typed_download(url, max_bytes, label):
            self.assertEqual(max_bytes, max(main.DOCUMENT_FILE_BYTES, main.HTML_PAGE_BYTES))
            return files[url]

        documents = [{"title": title, "kind": "html", "url": url, "selected": True} for title, url in zip(("Rapport", "Image"), files)]
        with patch.object(main, "download", typed_download):
            response = self.client.post("/api/pdf", json=_project(page_numbers=False, table_of_contents=False, uploaded_documents=documents))
        self.assertEqual(response.status_code, 200)
        fetched = [(stage["pdf"], stage["html"]) for stage in main.generation_log[-1]["stages"] if stage["stage"] == "fetch_document"]
        self.assertEqual(sorted(fetched), [(False, False), (True, False)])
        self.assertGreaterEqual(len(PdfReader(io.BytesIO(response.content)).pages), 3 + 1)
        self.assertFalse(any("%PDF" in html for html in self.htmls))

    def test_a_file_that_is_neither_html_nor_a_document_is_refused(self):
        async def zip_download(url, max_bytes, label):
            return b"PK", "application/zip"

        project = _project(uploaded_documents=[{"title": "Archive", "kind": "html", "url": self.PAGE_URL, "selected": True}])
        with patch.object(main, "download", zip_download):
            events = _parse_stream(self.client.post("/api/pdf/stream", json=project).content)
        self.assertEqual(events[-1]["type"], "error")
        self.assertIn("n’est pas une page HTML (application/zip)", events[-1]["detail"])

    def test_a_web_page_over_the_page_limit_is_refused(self):
        async def big_download(url, max_bytes, label):
            return b"<html>" + b" " * main.HTML_PAGE_BYTES + b"</html>", "text/html"

        project = _project(uploaded_documents=[{"title": "Lourde", "kind": "html", "url": self.PAGE_URL, "selected": True}])
        with patch.object(main, "download", big_download):
            events = _parse_stream(self.client.post("/api/pdf/stream", json=project).content)
        self.assertEqual(events[-1]["type"], "error")
        self.assertIn("trop volumineuse", events[-1]["detail"])
        self.assertIn(self.PAGE_URL, events[-1]["detail"])

if __name__ == "__main__":
    unittest.main()
