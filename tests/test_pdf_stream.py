import base64
import json
import sys
import types
import unittest
from io import BytesIO
from unittest.mock import patch

try:
    import weasyprint  # noqa: F401
except Exception:
    fake = types.ModuleType("weasyprint")
    fake.HTML = lambda *a, **k: None
    sys.modules["weasyprint"] = fake

from fastapi.testclient import TestClient
from pypdf import PdfReader
from reportlab.pdfgen import canvas

import app.main as main
from app.wikipedia_api import MediaWikiError


def _make_pdf(num_pages=1):
    buffer = BytesIO()
    pdf_canvas = canvas.Canvas(buffer, pagesize=(400, 600))
    for _ in range(num_pages):
        pdf_canvas.drawString(50, 500, "page body")
        pdf_canvas.showPage()
    pdf_canvas.save()
    return buffer.getvalue()


class FakeClient:
    fail = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def get_article_pdf(self, title, language):
        if FakeClient.fail:
            raise MediaWikiError(f"PDF indisponible pour {title}")
        return _make_pdf(2)

    async def get_book_links(self, title, language, limit=200):
        return ["Chien", "Chat"]


def _project(**extra):
    articles = [
        {"title": title, "language": "fr", "url": f"https://fr.wikipedia.org/wiki/{title}", "selected": True}
        for title in ("Chat", "Chien")
    ]
    return {"name": "Test", "book_title": "Animaux", "main_articles": articles, **extra}


class PdfStreamTest(unittest.TestCase):
    def setUp(self):
        FakeClient.fail = False
        self.patches = [
            patch.object(main, "MediaWikiClient", FakeClient),
            patch.object(main, "generate_pdf", lambda html: _make_pdf(1)),
        ]
        for p in self.patches:
            p.start()
        self.client = TestClient(main.app)

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def _events(self, project):
        response = self.client.post("/api/pdf/stream", json=project)
        self.assertEqual(response.status_code, 200)
        return [json.loads(line) for line in response.text.splitlines() if line.strip()]

    def test_progress_steps_are_numbered_and_end_with_the_pdf(self):
        events = self._events(_project(conclusion="Fin"))
        progress = [e for e in events if e["type"] == "progress"]
        total = progress[0]["total"]
        self.assertEqual([e["step"] for e in progress], list(range(1, total + 1)))
        self.assertTrue(all(e["total"] == total for e in progress))
        self.assertEqual(
            [e["code"] for e in progress],
            ["fetch_article", "fetch_article", "compute_page_numbers", "cover_and_toc",
             "assemble", "stamp_page_numbers", "finalize"],
        )
        self.assertEqual([e.get("title") for e in progress[:2]], ["Chat", "Chien"])
        self.assertEqual(events[-1]["type"], "done")
        pdf = PdfReader(BytesIO(base64.b64decode(events[-1]["pdf_base64"])))
        self.assertEqual(len(pdf.pages), 1 + 1 + 2 + 2 + 1 + 1)
        self.assertIn("Licence", [item.title for item in pdf.outline[1]])

    def test_without_page_numbers_there_are_fewer_steps(self):
        events = self._events(_project(page_numbers=False))
        codes = [e["code"] for e in events if e["type"] == "progress"]
        self.assertEqual(codes, ["fetch_article", "fetch_article", "cover_and_toc", "assemble", "finalize"])
        self.assertEqual(events[0]["total"], 5)

    def test_wikipedia_failure_is_reported_as_an_error_event(self):
        FakeClient.fail = True
        events = self._events(_project())
        self.assertEqual(events[-1], {"type": "error", "detail": "PDF indisponible pour Chat"})
        self.assertFalse(any(e["type"] == "done" for e in events))

    def test_empty_selection_is_refused_before_streaming(self):
        project = _project()
        for article in project["main_articles"]:
            article["selected"] = False
        response = self.client.post("/api/pdf/stream", json=project)
        self.assertEqual(response.status_code, 400)

    def test_plain_pdf_endpoint_still_returns_the_pdf(self):
        response = self.client.post("/api/pdf", json=_project())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/pdf")
        self.assertEqual(len(PdfReader(BytesIO(response.content)).pages), 1 + 1 + 2 + 2 + 1)

    def test_high_level_generation_accepts_article_references(self):
        response = self.client.post(
            "/api/books/generate",
            json={"book_title": "Animaux", "articles": [{"title": "Chat", "language": "fr"}]},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/pdf")
        self.assertEqual(len(PdfReader(BytesIO(response.content)).pages), 1 + 1 + 2 + 1)

    def test_high_level_generation_from_wikipedia_book_keeps_article_order(self):
        response = self.client.post(
            "/api/books/generate-from-wikipedia-book",
            json={"url": "https://fr.wikipedia.org/wiki/Livre:Animaux", "book_title": "Animaux"},
        )
        self.assertEqual(response.status_code, 200)
        pdf = PdfReader(BytesIO(response.content))
        child_titles = [item.title for item in pdf.outline[1] if not isinstance(item, list)]
        self.assertLess(child_titles.index("Chien"), child_titles.index("Chat"))

    def test_get_generation_from_wikipedia_book_needs_only_the_url(self):
        response = self.client.get(
            "/api/books/generate-from-wikipedia-book",
            params={"url": "https://fr.wikipedia.org/wiki/Livre:Animaux"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/pdf")
        self.assertEqual(response.headers["cache-control"], "no-store")
        pdf = PdfReader(BytesIO(response.content))
        child_titles = [item.title for item in pdf.outline[1] if not isinstance(item, list)]
        self.assertLess(child_titles.index("Chien"), child_titles.index("Chat"))

    def test_high_level_generation_rejects_empty_article_list(self):
        response = self.client.post("/api/books/generate", json={"articles": []})
        self.assertEqual(response.status_code, 422)

    def test_generated_titles_follow_the_requested_language(self):
        project = _project(conclusion="Ende", chapters=[{"title": "Tiere", "article_keys": ["fr:title:chat"]}])
        response = self.client.post("/api/pdf/stream?language=de", json=project)
        events = [json.loads(line) for line in response.text.splitlines() if line.strip()]
        pdf = PdfReader(BytesIO(base64.b64decode(events[-1]["pdf_base64"])))
        titles = [item.title for item in pdf.outline[1] if not isinstance(item, list)]
        self.assertEqual(titles, ["Inhaltsverzeichnis", "Tiere", "Ohne Kapitel", "Lizenz", "Schlusswort"])

    def test_unknown_language_is_refused(self):
        response = self.client.post("/api/pdf/stream?language=xx", json=_project())
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
