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
from app.wikipedia_api import MediaWikiError, WikipediaBook


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

    papers = []

    async def get_article_pdf(self, title, language, paper):
        FakeClient.papers.append(paper)
        if FakeClient.fail:
            raise MediaWikiError(f"PDF indisponible pour {title}")
        return _make_pdf(2)

    book = WikipediaBook(subtitle="", chapters=[("", ["Chien", "Chat"])])

    async def get_book(self, title, language, limit=200):
        return FakeClient.book

    async def get_intro_and_creator(self, title, language):
        return ("Introduction de test", "Auteur du livre")


def _project(**extra):
    articles = [
        {"title": title, "language": "fr", "url": f"https://fr.wikipedia.org/wiki/{title}", "selected": True}
        for title in ("Chat", "Chien")
    ]
    return {"name": "Test", "book_title": "Animaux", "main_articles": articles, **extra}


class PdfStreamTest(unittest.TestCase):
    def setUp(self):
        FakeClient.fail = False
        FakeClient.papers = []
        FakeClient.book =WikipediaBook(subtitle="", chapters=[("", ["Chien", "Chat"])])
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

    def test_non_latin_book_title_gives_a_valid_download_name(self):
        response = self.client.post("/api/pdf", json=_project(book_title='東京 "タワー"'))
        self.assertEqual(response.status_code, 200)
        disposition = response.headers["content-disposition"]
        self.assertIn('filename="__ _____.pdf"', disposition)
        self.assertIn("filename*=UTF-8''%E6%9D%B1%E4%BA%AC%20%22%E3%82%BF%E3%83%AF%E3%83%BC%22.pdf", disposition)

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
        self.assertIn("Animaux.pdf", response.headers["content-disposition"])
        pdf = PdfReader(BytesIO(response.content))
        child_titles = [item.title for item in pdf.outline[1] if not isinstance(item, list)]
        self.assertLess(child_titles.index("Chien"), child_titles.index("Chat"))

    def test_wikipedia_book_generation_ends_with_the_default_conclusion(self):
        pages = []
        with patch.object(main, "generate_pdf", lambda html: pages.append(html) or _make_pdf(1)):
            response = self.client.get(
                "/api/books/generate-from-wikipedia-book",
                params={"url": "https://fr.wikipedia.org/wiki/Livre:Animaux"},
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Generated by https://wikipedia2book.toolforge.org/", pages[-1])

    def test_wikipedia_book_conclusion_can_be_replaced_or_removed(self):
        for payload, expected in (({"book_conclusion": "Fin du livre"}, "Fin du livre"), ({"book_conclusion": ""}, None)):
            pages = []
            with patch.object(main, "generate_pdf", lambda html: pages.append(html) or _make_pdf(1)):
                response = self.client.post(
                    "/api/books/generate-from-wikipedia-book",
                    json={"url": "https://fr.wikipedia.org/wiki/Livre:Animaux", **payload},
                )
            self.assertEqual(response.status_code, 200)
            conclusions = [html for html in pages if "Generated by" in html or "Fin du livre" in html]
            self.assertEqual(len(conclusions), 0 if expected is None else 1)

    def test_default_title_keeps_only_the_last_part_of_the_book_page_name(self):
        response = self.client.get(
            "/api/books/generate-from-wikipedia-book",
            params={"url": "https://fr.wikipedia.org/wiki/Utilisateur:Exemple/Livres/Les_épaves_de_Saint-Pierre"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("filename*=UTF-8''Les%20%C3%A9paves%20de%20Saint-Pierre.pdf", response.headers["content-disposition"])
        self.assertEqual(PdfReader(BytesIO(response.content)).outline[0].title, "Les épaves de Saint-Pierre")

    def test_book_structure_returns_subtitle_and_chapters(self):
        FakeClient.book = WikipediaBook(
            subtitle="Petit guide", chapters=[("", ["Loup"]), ("Canidés", ["Chien"]), ("Félidés", ["Chat", "Lion"])]
        )
        response = self.client.post("/api/books/structure", json={"url": "https://fr.wikipedia.org/wiki/Livre:Animaux"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual([a["title"] for a in data["articles"]], ["Loup", "Chien", "Chat", "Lion"])
        self.assertEqual(data["subtitle"], "Petit guide")
        self.assertEqual(
            [(c["title"], c["article_keys"]) for c in data["chapters"]],
            [("Canidés", ["fr:title:chien"]), ("Félidés", ["fr:title:chat", "fr:title:lion"])],
        )
        self.assertTrue(data["unassigned_first"])
        legacy = self.client.post("/api/books/import", json={"url": "https://fr.wikipedia.org/wiki/Livre:Animaux"})
        self.assertEqual([a["title"] for a in legacy.json()], ["Loup", "Chien", "Chat", "Lion"])

    def test_wikipedia_book_generation_uses_its_subtitle_and_chapters(self):
        FakeClient.book = WikipediaBook(subtitle="Petit guide", chapters=[("Canidés", ["Chien"]), ("Félidés", ["Chat"])])
        pages = []
        with patch.object(main, "generate_pdf", lambda html: pages.append(html) or _make_pdf(1)):
            response = self.client.get(
                "/api/books/generate-from-wikipedia-book",
                params={"url": "https://fr.wikipedia.org/wiki/Livre:Animaux"},
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Petit guide", pages[0])
        self.assertTrue(any("Canidés" in html and "Chien" not in html for html in pages))
        self.assertTrue(any("Félidés" in html and "Chat" not in html for html in pages))

    def test_articles_before_the_first_chapter_stay_at_the_start_without_chapter_page(self):
        FakeClient.book = WikipediaBook(subtitle="", chapters=[("", ["Loup"]), ("Félidés", ["Chat"])])
        pages = []
        with patch.object(main, "generate_pdf", lambda html: pages.append(html) or _make_pdf(1)):
            response = self.client.get(
                "/api/books/generate-from-wikipedia-book",
                params={"url": "https://fr.wikipedia.org/wiki/Livre:Animaux", "table_of_contents": "false"},
            )
        self.assertEqual(response.status_code, 200)
        root = PdfReader(BytesIO(response.content)).outline[1]
        titles = [item.title for item in root if not isinstance(item, list)]
        self.assertEqual(titles[:2], ["Loup", "Félidés"])
        self.assertFalse(any("Sans chapitre" in html for html in pages))

    def test_structure_without_leading_articles_keeps_unassigned_last(self):
        FakeClient.book = WikipediaBook(subtitle="", chapters=[("Félidés", ["Chat"])])
        response = self.client.post("/api/books/structure", json={"url": "https://fr.wikipedia.org/wiki/Livre:Animaux"})
        self.assertFalse(response.json()["unassigned_first"])

    def test_wikipedia_pdf_paper_follows_the_book_format(self):
        for page_format, paper in (("A4", "a4"), ("Letter", "letter"), ("Legal", "legal"), ("A5", "a4"), ("custom", "a4")):
            FakeClient.papers = []
            response = self.client.post("/api/pdf", json=_project(page_format=page_format, page_numbers=False))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(FakeClient.papers, [paper, paper])

    def test_web_app_files_are_revalidated_by_the_browser(self):
        for path in ("/", "/static/app.js", "/static/i18n.js", "/static/styles.css"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers["cache-control"], "no-cache")
        self.assertNotIn("cache-control", self.client.get("/api/version").headers)

    def test_explicit_subtitle_replaces_the_book_subtitle(self):
        FakeClient.book = WikipediaBook(subtitle="Petit guide", chapters=[("", ["Chien"])])
        pages = []
        with patch.object(main, "generate_pdf", lambda html: pages.append(html) or _make_pdf(1)):
            self.client.post(
                "/api/books/generate-from-wikipedia-book",
                json={"url": "https://fr.wikipedia.org/wiki/Livre:Animaux", "book_subtitle": "Autre"},
            )
        self.assertIn("Autre", pages[0])
        self.assertNotIn("Petit guide", pages[0])

    def test_get_generation_can_disable_the_table_of_contents(self):
        response = self.client.get(
            "/api/books/generate-from-wikipedia-book",
            params={"url": "https://fr.wikipedia.org/wiki/Livre:Animaux", "table_of_contents": "false"},
        )
        self.assertEqual(response.status_code, 200)
        pdf = PdfReader(BytesIO(response.content))
        outline_titles = [item.title for item in pdf.outline[1] if not isinstance(item, list)]
        self.assertNotIn("Table des matières", outline_titles)

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

    def _outline(self, project):
        response = self.client.post("/api/pdf", json=project)
        self.assertEqual(response.status_code, 200, response.text)
        pdf = PdfReader(BytesIO(response.content))

        def flatten(items):
            return [flatten(item) if isinstance(item, list) else item.title for item in items]

        return flatten(pdf.outline[1]), len(pdf.pages)

    def test_table_of_contents_can_be_placed_before_any_article(self):
        outline, pages = self._outline(_project(page_numbers=False, toc_position="before:fr:title:chien"))
        self.assertEqual(outline, ["Chat", "Table des matières", "Chien", "Licence"])
        self.assertEqual(pages, 1 + 2 + 1 + 2 + 1)

    def test_table_of_contents_can_be_placed_before_a_chapter(self):
        chapters = [
            {"id": "c1", "title": "Félins", "article_keys": ["fr:title:chat"]},
            {"id": "c2", "title": "Canidés", "article_keys": ["fr:title:chien"]},
        ]
        outline, _ = self._outline(_project(page_numbers=False, chapters=chapters, toc_position="before:chapter:c2"))
        self.assertEqual(outline, ["Félins", ["Chat"], "Table des matières", "Canidés", ["Chien"], "Licence"])

    def test_table_of_contents_can_be_removed(self):
        outline, pages = self._outline(_project(page_numbers=False, table_of_contents=False))
        self.assertEqual(outline, ["Chat", "Chien", "Licence"])
        self.assertEqual(pages, 1 + 2 + 2 + 1)

    def test_unknown_anchor_falls_back_to_the_start(self):
        outline, _ = self._outline(_project(page_numbers=False, toc_position="before:fr:title:absent"))
        self.assertEqual(outline, ["Table des matières", "Chat", "Chien", "Licence"])

    def test_invalid_toc_position_is_refused(self):
        response = self.client.post("/api/pdf", json=_project(toc_position="milieu"))
        self.assertEqual(response.status_code, 422)

    def test_page_numbers_account_for_a_table_of_contents_in_the_middle(self):
        rendered = []

        def fake_generate(html):
            rendered.append(html)
            return _make_pdf(1)

        with patch.object(main, "generate_pdf", fake_generate):
            self.client.post("/api/pdf", json=_project(toc_position="before:fr:title:chien"))
        toc_html = [html for html in rendered if "<nav>" in html][-1]
        self.assertIn('<span>Chat</span><span class="page-no">2</span>', toc_html)
        self.assertIn('<span>Chien</span><span class="page-no">5</span>', toc_html)

    def test_table_of_contents_can_be_placed_before_the_articles_without_chapter(self):
        chapters = [{"id": "c1", "title": "Félins", "article_keys": ["fr:title:chat"]}]
        outline, _ = self._outline(_project(page_numbers=False, chapters=chapters, toc_position="before:chapter:"))
        self.assertEqual(outline, ["Félins", ["Chat"], "Table des matières", "Sans chapitre", ["Chien"], "Licence"])

    def test_empty_book_title_defaults_to_the_first_article_in_book_order(self):
        chapters = [{"id": "c1", "title": "Canidés", "article_keys": ["fr:title:chien"]}]
        response = self.client.post("/api/pdf", json=_project(book_title="", page_numbers=False, chapters=chapters))
        self.assertEqual(response.status_code, 200)
        self.assertIn('filename="Chien.pdf"', response.headers["content-disposition"])
        self.assertEqual(PdfReader(BytesIO(response.content)).outline[0].title, "Chien")

    def test_explicit_book_title_is_kept(self):
        response = self.client.post("/api/pdf", json=_project(page_numbers=False))
        self.assertIn('filename="Animaux.pdf"', response.headers["content-disposition"])


if __name__ == "__main__":
    unittest.main()
