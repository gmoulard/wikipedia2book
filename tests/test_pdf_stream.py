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
import base64
import contextlib
import io
import json
import sys
import types
import unittest
from io import BytesIO
from pathlib import Path
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

# NE PAS laisser l'assemblage dans un processus séparé ici : ces tests remplacent generate_pdf et fit_pdf_to_format dans main, ce que le processus enfant ne verrait pas (tests/test_isolation.py couvre le processus séparé).
main.ISOLATE_ASSEMBLY = False
from app.wikipedia_api import MediaWikiError, MediaWikiPageNotFound, WikipediaBook


def _parse_stream(content):
    events = []
    while content:
        line, _, content = content.partition(b"\n")
        if not line.strip():
            continue
        event = json.loads(line)
        if event["type"] == "done":
            event["pdf"] = content[:event["size"]]
            event["trailing"] = len(content) - event["size"]
            events.append(event)
            break
        events.append(event)
    return events


async def _book_events(project, language="fr"):
    events = []
    async for event in main.build_book_pdf(project, main._selected_items(project), language):
        if event["type"] == "done":
            event["pdf"] = event["path"].read_bytes()
        events.append(event)
    return events


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
    wait = None
    missing = ()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    papers = []

    async def get_article_pdf(self, title, language, paper, site="wikipedia"):
        FakeClient.papers.append(paper)
        if FakeClient.wait is not None and title == "Chat":
            self.on_wait(FakeClient.wait)
        if FakeClient.fail:
            raise MediaWikiError(f"PDF indisponible pour {title}")
        if title in FakeClient.missing:
            raise MediaWikiPageNotFound(f"La page « {title} » n'existe pas (ou plus) sur fr.wikipedia.org.")
        return _make_pdf(2)

    book = WikipediaBook(subtitle="", chapters=[("", ["Chien", "Chat"])])

    async def get_book(self, title, language, limit=200):
        return FakeClient.book

    async def get_intro_and_creator(self, title, language, site="wikipedia"):
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
        FakeClient.wait = None
        FakeClient.missing = ()
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
        return _parse_stream(response.content)

    def test_progress_steps_are_numbered_and_end_with_the_pdf(self):
        events = self._events(_project(conclusion="Fin"))
        progress = [e for e in events if e["type"] == "progress"]
        total = progress[0]["total"]
        self.assertEqual([e["step"] for e in progress], list(range(1, total)))
        self.assertTrue(all(e["total"] == total for e in progress))
        self.assertEqual(
            [e["code"] for e in progress],
            ["fetch_article", "fetch_article", "compute_page_numbers", "cover_and_toc",
             "assemble", "stamp_page_numbers", "finalize"],
        )
        self.assertEqual([e.get("title") for e in progress[:2]], ["Chat", "Chien"])
        self.assertEqual(events[-1]["type"], "done")
        pdf = PdfReader(BytesIO(events[-1]["pdf"]))
        self.assertEqual(len(pdf.pages), 1 + 1 + 2 + 2 + 1 + 1)
        self.assertIn("Licence", [item.title for item in pdf.outline[1]])

    def test_without_page_numbers_there_are_fewer_steps(self):
        events = self._events(_project(page_numbers=False))
        codes = [e["code"] for e in events if e["type"] == "progress"]
        self.assertEqual(codes, ["fetch_article", "fetch_article", "cover_and_toc", "assemble", "finalize"])
        self.assertEqual(events[0]["total"], 6)

    def test_wikipedia_pause_is_announced_without_counting_as_a_step(self):
        FakeClient.wait = 4.2
        events = self._events(_project(page_numbers=False))
        self.assertIn({"type": "wait", "seconds": 5}, events)
        progress = [e for e in events if e["type"] == "progress"]
        self.assertEqual([e["step"] for e in progress], [1, 2, 3, 4, 5])
        self.assertEqual(events[-1]["type"], "done")

    def test_wikipedia_failure_is_reported_as_an_error_event(self):
        FakeClient.fail = True
        events = self._events(_project())
        self.assertEqual(events[-1], {"type": "error", "detail": "PDF indisponible pour Chat"})
        self.assertFalse(any(e["type"] == "done" for e in events))

    def test_missing_wikipedia_page_is_skipped_and_reported(self):
        FakeClient.missing = ("Chat",)
        events = self._events(_project(page_numbers=False))
        self.assertIn({"type": "missing", "title": "Chat", "url": "https://fr.wikipedia.org/wiki/Chat"}, events)
        self.assertEqual(events[-1]["type"], "done")
        pdf = PdfReader(BytesIO(events[-1]["pdf"]))
        self.assertEqual(len(pdf.pages), 1 + 2 + 1)
        self.assertNotIn("Chat", [item.title for item in pdf.outline[1] if not isinstance(item, list)])

    def test_book_whose_pages_are_all_missing_is_an_error(self):
        FakeClient.missing = ("Chat", "Chien")
        events = self._events(_project())
        self.assertEqual(events[-1]["type"], "error")
        self.assertIn("Aucune page du livre", events[-1]["detail"])

    def test_empty_selection_is_refused_before_streaming(self):
        project = _project()
        for article in project["main_articles"]:
            article["selected"] = False
        response = self.client.post("/api/pdf/stream", json=project)
        self.assertEqual(response.status_code, 400)

    def test_two_titles_with_the_same_key_still_give_a_pdf(self):
        project = _project()
        project["main_articles"].append({"title": "chat", "language": "fr", "url": "https://fr.wikipedia.org/wiki/chat", "selected": True})
        response = self.client.post("/api/pdf", json=project)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertGreater(len(PdfReader(BytesIO(response.content)).pages), 1 + 1 + 2 + 2 + 1)

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
        pdf = PdfReader(BytesIO(response.content))
        self.assertEqual(len(pdf.pages), 1 + 2 + 1)
        self.assertNotIn("Table des matières", [item.title for item in pdf.outline[1] if not isinstance(item, list)])

    def test_single_article_book_has_no_table_of_contents_even_when_asked(self):
        project = _project(table_of_contents=True)
        project["main_articles"] = project["main_articles"][:1]
        pages = []
        with patch.object(main, "generate_pdf", lambda html: pages.append(html) or _make_pdf(1)):
            response = self.client.post("/api/pdf", json=project)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(any("<nav>" in html for html in pages))
        self.assertEqual([item.title for item in PdfReader(BytesIO(response.content)).outline[1] if not isinstance(item, list)], ["Chat", "Licence"])

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

    def test_wikipedia_book_generation_has_no_conclusion_by_default(self):
        pages = []
        with patch.object(main, "generate_pdf", lambda html: pages.append(html) or _make_pdf(1)):
            response = self.client.get(
                "/api/books/generate-from-wikipedia-book",
                params={"url": "https://fr.wikipedia.org/wiki/Livre:Animaux"},
            )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Generated by", "".join(pages))
        self.assertNotIn("Conclusion", PdfReader(BytesIO(response.content)).outline[1][-1].title)

    def test_logo_and_links_follow_the_license_after_the_conclusion(self):
        for conclusion in ("", "Fin du livre"):
            pages = []
            with patch.object(main, "generate_pdf", lambda html: pages.append(html) or _make_pdf(1)):
                response = self.client.post("/api/pdf", json=_project(conclusion=conclusion))
            self.assertEqual(response.status_code, 200)
            with_colophon = [index for index, html in enumerate(pages) if 'class="colophon"' in html]
            self.assertEqual(with_colophon, [len(pages) - 1], conclusion)
            last = pages[-1]
            self.assertIn('href="https://wikipedia2book.toolforge.org/"', last)
            self.assertIn('href="https://github.com/gmoulard/wikipedia2book"', last)
            self.assertIn('<a href="https://wikipedia2book.toolforge.org/"><img src="data:image/png;base64,', last)
            self.assertNotIn("Fin du livre", last)
            self.assertEqual("Fin du livre" in pages[-2], bool(conclusion))
            titles = [entry.title for entry in PdfReader(BytesIO(response.content)).outline[1] if not isinstance(entry, list)]
            if conclusion:
                self.assertLess(titles.index("Conclusion"), titles.index("Licence"))

    def test_back_image_is_a_page_after_the_license(self):
        project = _project(conclusion="Fin du livre")
        project["back_image"] = {"title": "dos.png", "mime_type": "image/png", "data_base64": base64.b64encode(b"fake-png").decode()}
        pages = []
        with patch.object(main, "generate_pdf", lambda html: pages.append(html) or _make_pdf(1)):
            response = self.client.post("/api/pdf", json=project)
        self.assertEqual(response.status_code, 200)
        self.assertIn('class="colophon"', pages[-2])
        self.assertIn("margin: 0;", pages[-1])
        self.assertNotIn("colophon", pages[-1])

    def test_back_color_or_logo_alone_adds_the_last_page(self):
        for fields in ({}, {"back_color": "#336699"}, {"back_logo": True}):
            pages = []
            with patch.object(main, "generate_pdf", lambda html: pages.append(html) or _make_pdf(1)):
                response = self.client.post("/api/pdf", json=_project(**fields))
            self.assertEqual(response.status_code, 200)
            with self.subTest(fields=fields):
                self.assertEqual("colophon" in pages[-1], not fields)

    def test_wikipedia_book_conclusion_can_be_replaced_or_removed(self):
        for payload, expected in (({"book_conclusion": "Fin du livre"}, "Fin du livre"), ({"book_conclusion": ""}, None)):
            pages = []
            with patch.object(main, "generate_pdf", lambda html: pages.append(html) or _make_pdf(1)):
                response = self.client.post(
                    "/api/books/generate-from-wikipedia-book",
                    json={"url": "https://fr.wikipedia.org/wiki/Livre:Animaux", **payload},
                )
            self.assertEqual(response.status_code, 200)
            conclusions = [html for html in pages if "Fin du livre" in html]
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
        for path in ("/", "/app", "/faq", "/static/app.js", "/static/i18n.js", "/static/styles.css", "/static/home.css", "/static/home.js"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers["cache-control"], "no-cache")
        self.assertNotIn("cache-control", self.client.get("/api/version").headers)

    def test_home_page_app_and_faq_are_separate_pages(self):
        pages = {path: self.client.get(path).text for path in ("/", "/app", "/faq")}
        self.assertIn('href="/app"', pages["/"])
        self.assertIn('href="/faq"', pages["/"])
        self.assertIn('id="articleQuery"', pages["/app"])
        self.assertNotIn('id="articleQuery"', pages["/"])
        self.assertIn('data-i18n="faq.q1"', pages["/faq"])

    def test_old_links_to_the_home_page_open_the_app(self):
        for query in ("json=https://example.org/livre.json", "source=Chat&source=Chien", "wiki=nl&source=Kat"):
            response = self.client.get(f"/?{query}", follow_redirects=False)
            self.assertEqual(response.status_code, 307)
            self.assertEqual(response.headers["location"], f"/app?{query}")
        self.assertEqual(self.client.get("/?utm_source=x", follow_redirects=False).status_code, 200)

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
        events = _parse_stream(response.content)
        pdf = PdfReader(BytesIO(events[-1]["pdf"]))
        titles = [item.title for item in pdf.outline[1] if not isinstance(item, list)]
        self.assertEqual(titles, ["Inhaltsverzeichnis", "Tiere", "Ohne Kapitel", "Schlusswort", "Lizenz"])

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
        self.assertIn('<span class="page-no">2</span><span class="toc-title">Chat</span>', toc_html)
        self.assertIn('<span class="page-no">5</span><span class="toc-title">Chien</span>', toc_html)

    def test_generation_does_not_block_the_server_and_renders_the_cover_once(self):
        import asyncio
        import time
        from app.models import Project

        rendered = []

        def slow_generate(html):
            time.sleep(0.2)
            rendered.append(html)
            return _make_pdf(1)

        async def scenario():
            ticks = 0
            done = False

            async def ticker():
                nonlocal ticks
                while not done:
                    ticks += 1
                    await asyncio.sleep(0.02)

            ticking = asyncio.create_task(ticker())
            project = Project(**_project(chapters=[{"id": "c1", "title": "Félins", "article_keys": ["fr:title:chat"]}]))
            events = await _book_events(project)
            done = True
            await ticking
            return ticks, events

        with patch.object(main, "generate_pdf", slow_generate):
            ticks, events = asyncio.run(scenario())
        self.assertEqual(events[-1]["type"], "done")
        self.assertGreater(ticks, len(rendered) * 5)
        self.assertEqual(sum('class="cover"' in html for html in rendered), 1)

    def test_articles_are_recomposed_while_the_next_ones_download(self):
        import asyncio
        import time
        from app.models import Project

        timeline = []

        class SlowClient(FakeClient):
            async def get_article_pdf(self, title, language, paper, site="wikipedia"):
                await asyncio.sleep(0.05 if title == "Chat" else 0.4)
                timeline.append(("downloaded", title, time.perf_counter()))
                return _make_pdf(2)

        real_fit = main.fit_pdf_to_format

        def recording_fit(data, width, height):
            timeline.append(("fit", None, time.perf_counter()))
            return real_fit(data, width, height)

        async def scenario():
            project = Project(**_project())
            return await _book_events(project)

        with patch.object(main, "MediaWikiClient", SlowClient), patch.object(main, "fit_pdf_to_format", recording_fit), patch.object(main, "generate_pdf", lambda html: _make_pdf(1)):
            events = asyncio.run(scenario())
        self.assertEqual(events[-1]["type"], "done")
        last_download = max(moment for kind, _, moment in timeline if kind == "downloaded")
        first_fit = min(moment for kind, _, moment in timeline if kind == "fit")
        self.assertLess(first_fit, last_download)

    def test_temporary_files_are_removed_after_success_error_and_abort(self):
        import asyncio
        from app.models import Project

        seen = []
        real_mkdtemp = main.tempfile.mkdtemp

        def recording_mkdtemp(*args, **kwargs):
            path = real_mkdtemp(*args, **kwargs)
            seen.append(Path(path))
            return path

        class FailingClient(FakeClient):
            async def get_article_pdf(self, title, language, paper, site="wikipedia"):
                if title == "Chien":
                    raise main.MediaWikiError("Wikipédia ne répond pas")
                return await super().get_article_pdf(title, language, paper)

        async def success():
            events = await _book_events(Project(**_project()))
            self.assertTrue(events[-1]["pdf"].startswith(b"%PDF-"))

        async def failure():
            with self.assertRaises(main.MediaWikiError):
                await _book_events(Project(**_project()))

        async def abort():
            book = main.build_book_pdf(Project(**_project()), main._selected_items(Project(**_project())), "fr")
            async for event in book:
                if event.get("code") == "assemble":
                    break
            self.assertTrue(any(seen[-1].iterdir()))
            await book.aclose()

        with patch.object(main.tempfile, "mkdtemp", recording_mkdtemp), patch.object(main, "generate_pdf", lambda html: _make_pdf(1)):
            with patch.object(main, "MediaWikiClient", FakeClient):
                asyncio.run(success())
                asyncio.run(abort())
            with patch.object(main, "MediaWikiClient", FailingClient):
                asyncio.run(failure())
        self.assertEqual(len(seen), 3)
        self.assertEqual([path.exists() for path in seen], [False, False, False])

    def test_article_limit_refuses_large_books_and_points_to_the_unlimited_server(self):
        with patch.object(main, "ARTICLE_LIMIT", 1), patch.object(main, "MediaWikiClient", FakeClient):
            for path in ("/api/pdf", "/api/pdf/stream"):
                response = self.client.post(path, json=_project())
                self.assertEqual(response.status_code, 413, path)
                detail = response.json()["detail"]
                self.assertEqual(detail["code"], "too_many_articles")
                self.assertEqual((detail["count"], detail["limit"]), (2, 1))
                self.assertIn("Wikimédia", detail["message"])
        with patch.object(main, "ARTICLE_LIMIT", 2), patch.object(main, "MediaWikiClient", FakeClient), patch.object(main, "generate_pdf", lambda html: _make_pdf(1)):
            self.assertEqual(self.client.post("/api/pdf", json=_project()).status_code, 200)

    def test_version_exposes_the_article_limit_for_volumes(self):
        with patch.object(main, "ARTICLE_LIMIT", 300):
            details = self.client.get("/api/version").json()
        self.assertEqual(details["article_limit"], 300)
        self.assertIn("version", details)
        with patch.object(main, "ARTICLE_LIMIT", None):
            self.assertIsNone(self.client.get("/api/version").json()["article_limit"])

    def test_article_limit_of_300_everywhere_by_default(self):
        self.assertEqual(main.DEFAULT_ARTICLE_LIMIT, 300)

    def test_deployment_settings_defaults_per_platform(self):
        self.assertEqual(main.deployment_settings({}, on_toolforge=True), (300, 4))
        self.assertEqual(main.deployment_settings({}, on_toolforge=False), (300, 2))

    def test_deployment_settings_from_the_environment(self):
        settings = main.deployment_settings
        self.assertEqual(settings({"WIKIPEDIA2BOOK_ARTICLE_LIMIT": "40", "WIKIPEDIA2BOOK_DOWNLOADS": "1"}, on_toolforge=False), (40, 1))
        self.assertEqual(settings({"WIKIPEDIA2BOOK_ARTICLE_LIMIT": "0"}, on_toolforge=True), (None, 4))
        self.assertEqual(settings({"WIKIPEDIA2BOOK_ARTICLE_LIMIT": " "}, on_toolforge=True), (300, 4))
        for environ, on_toolforge in (
            ({"WIKIPEDIA2BOOK_DOWNLOADS": "3"}, False),
            ({"WIKIPEDIA2BOOK_DOWNLOADS": "5"}, True),
            ({"WIKIPEDIA2BOOK_DOWNLOADS": "0"}, False),
            ({"WIKIPEDIA2BOOK_ARTICLE_LIMIT": "-1"}, False),
            ({"WIKIPEDIA2BOOK_ARTICLE_LIMIT": "beaucoup"}, False),
        ):
            with self.assertRaises(ValueError, msg=environ):
                settings(environ, on_toolforge)

    def test_downloaded_file_limits_default_to_100_and_15_megabytes(self):
        setting = main.megabytes_setting
        self.assertEqual(main.DOCUMENT_FILE_BYTES, setting({}, "WIKIPEDIA2BOOK_DOCUMENT_MB", 100))
        self.assertEqual(setting({}, "WIKIPEDIA2BOOK_DOCUMENT_MB", 100), 100_000_000)
        self.assertEqual(setting({}, "WIKIPEDIA2BOOK_HTML_PAGE_MB", 15), 15_000_000)
        self.assertEqual(setting({"WIKIPEDIA2BOOK_HTML_PAGE_MB": " 40 "}, "WIKIPEDIA2BOOK_HTML_PAGE_MB", 15), 40_000_000)
        for text in ("0", "-5", "1.5", "beaucoup"):
            with self.assertRaises(ValueError, msg=text):
                setting({"WIKIPEDIA2BOOK_DOCUMENT_MB": text}, "WIKIPEDIA2BOOK_DOCUMENT_MB", 100)

    def test_dockerfile_sets_both_settings_within_the_policy(self):
        dockerfile = (Path(main.__file__).resolve().parent.parent / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("WIKIPEDIA2BOOK_ARTICLE_LIMIT=300", dockerfile)
        self.assertIn("WIKIPEDIA2BOOK_DOWNLOADS=2", dockerfile)
        self.assertNotIn("WIKIPEDIA2BOOK_PLATFORM", dockerfile.split("# NE PAS")[0])

    def test_api_pdf_streams_the_file_with_its_length(self):
        with patch.object(main, "MediaWikiClient", FakeClient), patch.object(main, "generate_pdf", lambda html: _make_pdf(1)):
            response = TestClient(main.app).post("/api/pdf", json=_project())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(response.headers["content-length"]), len(response.content))
        self.assertTrue(response.content.startswith(b"%PDF-"))

    def test_pdf_follows_the_done_line_as_raw_bytes(self):
        events = self._events(_project())
        self.assertEqual(events[-1]["type"], "done")
        self.assertEqual(events[-1]["trailing"], 0)
        self.assertEqual(len(events[-1]["pdf"]), events[-1]["size"])
        self.assertTrue(events[-1]["pdf"].startswith(b"%PDF-"))

    def test_downloads_run_in_parallel_up_to_the_limit_and_keep_book_order(self):
        import asyncio
        from app.models import Project

        running = 0
        peak = 0

        class ParallelClient(FakeClient):
            async def get_article_pdf(self, title, language, paper, site="wikipedia"):
                nonlocal running, peak
                running += 1
                peak = max(peak, running)
                await asyncio.sleep(0.05)
                running -= 1
                return _make_pdf(2)

        articles = [
            {"title": f"Article {index}", "language": "fr", "url": f"https://fr.wikipedia.org/wiki/Article_{index}", "selected": True}
            for index in range(10)
        ]
        project = Project(name="Parallèle", main_articles=articles, page_numbers=False)

        async def scenario():
            return await _book_events(project)

        with patch.object(main, "MediaWikiClient", ParallelClient), patch.object(main, "generate_pdf", lambda html: _make_pdf(1)):
            events = asyncio.run(scenario())
        self.assertEqual(peak, main.DOWNLOAD_CONCURRENCY)
        fetches = [event for event in events if event.get("code") == "fetch_article"]
        self.assertEqual(len(fetches), 10)
        self.assertEqual([event["step"] for event in events if event["type"] == "progress"], list(range(1, len(events))))
        pdf = PdfReader(BytesIO(events[-1]["pdf"]))
        titles = [item.title for item in pdf.outline[1] if not isinstance(item, list)]
        self.assertEqual([title for title in titles if title.startswith("Article")], [f"Article {index}" for index in range(10)])

    def test_table_of_contents_entries_link_to_their_pages(self):
        import re
        from app.book_builder import TOC_LINK_PREFIX

        def fake_generate(html):
            if "<nav>" not in html:
                return _make_pdf(1)
            buffer = BytesIO()
            pdf_canvas = canvas.Canvas(buffer, pagesize=(400, 600))
            for index, href in enumerate(re.findall(r'href="([^"]+)"', html)):
                pdf_canvas.linkURL(href, (40, 500 - 30 * index, 360, 520 - 30 * index))
            pdf_canvas.drawString(50, 550, "toc")
            pdf_canvas.save()
            return buffer.getvalue()

        chapters = [{"id": "c1", "title": "Félins", "article_keys": ["fr:title:chat"]}]
        with patch.object(main, "generate_pdf", fake_generate):
            response = self.client.post("/api/pdf", json=_project(chapters=chapters, toc_position="start"))
        self.assertEqual(response.status_code, 200, response.text)
        pdf = PdfReader(BytesIO(response.content))
        pages_by_title = {}

        def walk(items):
            for item in items:
                if isinstance(item, list):
                    walk(item)
                else:
                    pages_by_title[item.title] = pdf.get_destination_page_number(item)

        walk(pdf.outline)
        toc_page = pdf.pages[pages_by_title["Table des matières"]]
        annotations = [reference.get_object() for reference in toc_page.get("/Annots", [])]
        self.assertFalse([a for a in annotations if str((a.get("/A") or {}).get("/URI", "")).startswith(TOC_LINK_PREFIX)])
        destinations = [a["/Dest"] if "/Dest" in a else a["/A"]["/D"] for a in annotations if "/Dest" in a or "/D" in (a.get("/A") or {})]
        targets = [pdf.get_page_number(destination[0].get_object()) for destination in destinations]
        self.assertEqual(targets, [pages_by_title["Félins"], pages_by_title["Chat"], pages_by_title["Sans chapitre"], pages_by_title["Chien"]])

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



class ResourceGateGenerationTest(unittest.TestCase):
    def setUp(self):
        self.patches = [
            patch.object(main, "MediaWikiClient", FakeClient),
            patch.object(main, "generate_pdf", lambda html: _make_pdf(1)),
        ]
        for p in self.patches:
            p.start()
        FakeClient.fail = False
        FakeClient.wait = None
        FakeClient.missing = ()

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def test_a_generation_waits_for_memory_then_resumes(self):
        from app.resource_gate import ResourceGate
        from app.models import Project
        ticks = iter(range(10_000))
        gate = ResourceGate(lambda: (1_990_000_000, 2_000_000_000), 0.95, poll_s=0.01, clock=lambda: next(ticks) * 0.5)

        async def scenario():
            holder = await gate.acquire(1)
            book = asyncio.ensure_future(_book_events(Project(**_project(page_numbers=False))))
            await asyncio.sleep(0.2)
            self.assertFalse(book.done())
            holder.release()
            return await asyncio.wait_for(book, 10)

        with patch.object(main, "MEMORY_GATE", gate):
            events = asyncio.run(scenario())
        self.assertIn("busy", [event["type"] for event in events])
        self.assertTrue(all(event["seconds"] >= 0 for event in events if event["type"] == "busy"))
        progress = [event for event in events if event["type"] == "progress"]
        self.assertEqual([event["step"] for event in progress], list(range(1, len(progress) + 1)))
        self.assertEqual(events[-1]["type"], "done")
        self.assertEqual(gate.state()["reserved_bytes"], 0)
        waits = [stage for stage in main.generation_log[-1]["stages"] if stage["stage"] == "memory_wait"]
        self.assertTrue(waits)
        self.assertTrue(all(stage["reason"] in {"download", "fit", "assembly", "fetch_image"} for stage in waits))

    def test_ratio_settings(self):
        for name in ("WIKIPEDIA2BOOK_MEMORY_RATIO", "WIKIPEDIA2BOOK_DISK_RATIO"):
            self.assertEqual(main.ratio_setting({}, name), 0.95)
            self.assertEqual(main.ratio_setting({name: "0.8"}, name), 0.8)
            self.assertEqual(main.ratio_setting({name: "0"}, name), 0)
            for wrong in ("1.5", "-0.1", "beaucoup"):
                with self.subTest(name=name, wrong=wrong), self.assertRaises(ValueError) as caught:
                    main.ratio_setting({name: wrong}, name)
                self.assertIn(name, str(caught.exception))

    def test_downloads_wait_for_disk_space(self):
        from app.models import Project
        from app.resource_gate import ResourceGate
        ticks = iter(range(10_000))
        disk = ResourceGate(lambda: (99_000_000_000, 100_000_000_000), 0.95, poll_s=0.01, clock=lambda: next(ticks) * 0.5)
        roomy = ResourceGate(lambda: (0, 2_000_000_000), 0.95, poll_s=0.01)

        async def scenario():
            holder = await disk.acquire(1)
            book = asyncio.ensure_future(_book_events(Project(**_project(page_numbers=False))))
            await asyncio.sleep(0.2)
            self.assertFalse(book.done())
            self.assertEqual(FakeClient.papers, [])
            holder.release()
            return await asyncio.wait_for(book, 10)

        FakeClient.papers = []
        with patch.object(main, "DISK_GATE", disk), patch.object(main, "MEMORY_GATE", roomy):
            events = asyncio.run(scenario())
        self.assertIn("busy", [event["type"] for event in events])
        self.assertEqual(events[-1]["type"], "done")
        self.assertEqual(disk.state()["reserved_bytes"], 0)
        reasons = {stage.get("reason") for stage in main.generation_log[-1]["stages"] if stage["stage"] == "memory_wait"}
        self.assertIn("disk", reasons)

    def test_assembly_waits_for_disk_space_too(self):
        from app.models import Project
        from app.resource_gate import ResourceGate
        disk = ResourceGate(lambda: (0, 100_000_000_000), 0.95, poll_s=0.01)
        amounts = []
        original = disk.acquire

        async def recording(amount, on_wait=None):
            amounts.append(amount)
            return await original(amount, on_wait)

        disk.acquire = recording
        with patch.object(main, "DISK_GATE", disk):
            events = asyncio.run(_book_events(Project(**_project(page_numbers=False))))
        self.assertEqual(events[-1]["type"], "done")
        self.assertEqual(amounts[:2], [main.DOWNLOAD_DISK_BYTES, main.DOWNLOAD_DISK_BYTES])
        self.assertEqual(len(amounts), 3)
        self.assertGreater(amounts[2], main.ASSEMBLY_DISK_BASE_BYTES)
        self.assertEqual(disk.state()["reserved_bytes"], 0)

    def test_disk_estimate_for_the_assembly(self):
        self.assertEqual(main.assembly_disk_reserve(10_000_000), 50_000_000 + 20_000_000)

    def test_a_generation_waits_at_the_entry_before_downloading(self):
        from app.models import Project
        from app.resource_gate import ResourceGate
        ticks = iter(range(10_000))
        entry = ResourceGate(lambda: (0, 1_000_000_000), 0.5, poll_s=0.01, clock=lambda: next(ticks) * 0.5)

        async def scenario():
            holder = await entry.acquire(490_000_000)
            book = asyncio.ensure_future(_book_events(Project(**_project(page_numbers=False))))
            await asyncio.sleep(0.2)
            self.assertFalse(book.done())
            self.assertEqual(FakeClient.papers, [])
            holder.release()
            return await asyncio.wait_for(book, 10)

        FakeClient.papers = []
        with patch.object(main, "GENERATION_GATE", entry):
            events = asyncio.run(scenario())
        self.assertEqual(events[0]["type"], "busy")
        self.assertEqual(events[-1]["type"], "done")
        self.assertEqual(entry.state()["reserved_bytes"], 0)
        waits = [stage for stage in main.generation_log[-1]["stages"] if stage["stage"] == "memory_wait"]
        self.assertEqual(waits[0]["reason"], "generation")

    def test_generation_reserve_counts_the_data_kept_by_the_book(self):
        from app.models import BookImage, Project, UploadedDocument
        document = UploadedDocument(title="Plan", kind="image", mime_type="image/png", data_base64="A" * 1000)
        project = Project(name="Livre", cover_image=BookImage(title="Couverture", url="https://example.org/c.jpg"), back_image=BookImage(mime_type="image/png", data_base64="QUFB" * 250))
        self.assertEqual(main.generation_reserve(project, [document]), main.GENERATION_BASE_BYTES + main.INLINE_FACTOR * (1000 + 1000) + main.BACKGROUND_FILE_BYTES)
        self.assertEqual(main.ratio_setting({}, "WIKIPEDIA2BOOK_GENERATIONS_RATIO", 0.5), 0.5)

    def test_estimates_follow_the_file_sizes(self):
        self.assertEqual(main.fit_reserve(2_000_000), 5_000_000 + 25 * 2_000_000)
        self.assertEqual(main.assembly_reserve(10_000_000, 1_000_000), 100_000_000 + 25_000_000 + 35_000_000)


def _png():
    from PIL import Image
    buffer = BytesIO()
    Image.new("RGB", (40, 60), "white").save(buffer, "PNG")
    return buffer.getvalue()


class RemoteFilesTest(unittest.TestCase):
    COVER = "https://upload.wikimedia.org/couverture.png"
    BACK = "https://example.org/dos.png"
    PHOTO = "https://example.org/photo.png"
    LEAFLET = "https://example.org/notice.pdf"

    def setUp(self):
        self.files = {
            self.COVER: (_png(), "image/png"),
            self.BACK: (_png(), "image/png"),
            self.PHOTO: (_png(), "image/png"),
            self.LEAFLET: (_make_pdf(3), "application/pdf"),
        }
        self.requested = []
        self.htmls = []

        async def fake_download(url, max_bytes, label):
            self.requested.append(url)
            if url not in self.files:
                raise main.JsonSourceError(502, f"Introuvable : {url}")
            return self.files[url]

        def fake_generate(html):
            self.htmls.append(html)
            return _make_pdf(1)

        self.patches = [
            patch.object(main, "MediaWikiClient", FakeClient),
            patch.object(main, "generate_pdf", fake_generate),
            patch.object(main, "download", fake_download),
        ]
        for p in self.patches:
            p.start()
        FakeClient.fail = False
        FakeClient.wait = None
        FakeClient.missing = ()
        self.client = TestClient(main.app)

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def _project(self, **extra):
        documents = [
            {"title": "Photo", "kind": "image", "url": self.PHOTO, "selected": True},
            {"title": "Notice", "kind": "image", "url": self.LEAFLET, "selected": True},
        ]
        return _project(
            page_numbers=False,
            cover_image={"title": "Couverture", "url": self.COVER},
            back_image={"title": "Dos", "url": self.BACK},
            uploaded_documents=documents,
            **extra,
        )

    def test_images_and_documents_are_downloaded_at_each_generation(self):
        for _ in range(2):
            response = self.client.post("/api/pdf/stream", json=self._project())
            events = _parse_stream(response.content)
            codes = [e["code"] for e in events if e["type"] == "progress"]
            self.assertEqual(codes[:2], ["fetch_image", "fetch_image"])
            self.assertEqual(codes.count("prepare_document"), 2)
            self.assertEqual(events[-1]["type"], "done")
            pdf = PdfReader(BytesIO(events[-1]["pdf"]))
            self.assertEqual(len(pdf.pages), 1 + 1 + 2 + 2 + 1 + 3 + 1 + 1)
        self.assertEqual(sorted(self.requested), sorted([self.COVER, self.BACK, self.PHOTO, self.LEAFLET] * 2))
        cover = base64.b64encode(_png()).decode("ascii")
        self.assertTrue(any(f"data:image/png;base64,{cover}" in html for html in self.htmls))
        self.assertFalse(any("https://upload.wikimedia.org" in html for html in self.htmls))

    def test_image_processing_is_timed_in_the_generation_journal(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            events = _parse_stream(self.client.post("/api/pdf/stream", json=self._project()).content)
        self.assertEqual(events[-1]["type"], "done")
        stages = main.generation_log[-1]["stages"]
        images = [stage for stage in stages if stage["stage"] == "fetch_image"]
        self.assertEqual([stage["image"] for stage in images], ["cover_image", "back_image"])
        documents = [stage for stage in stages if stage["stage"] == "fetch_document"]
        self.assertEqual(sorted(stage["pdf"] for stage in documents), [False, True])
        fit = [stage for stage in stages if stage["stage"] == "fit_backgrounds"]
        self.assertEqual(len(fit), 1)
        self.assertGreater(fit[0]["bytes_before"], 0)
        cover = [stage for stage in stages if stage["stage"] == "cover_html"]
        self.assertEqual(len(cover), 1)
        self.assertTrue(cover[0]["background"])
        for stage in images + documents + cover:
            self.assertGreaterEqual(stage["duration_s"], 0)
        for stage in images + documents:
            self.assertGreater(stage["size_bytes"], 0)
        journal = json.dumps(main.generation_log[-1])
        for text in ("Couverture", "Notice", "Photo"):
            self.assertNotIn(text, journal)
        self.assertEqual([stage["url"] for stage in images], ["https://upload.wikimedia.org/couverture.png", "https://example.org/dos.png"])
        downloads = [stage for stage in stages if stage["stage"] == "download"]
        self.assertEqual(sorted(stage["kind"] for stage in downloads), ["article", "article", "document", "document"])
        self.assertIn("https://fr.wikipedia.org/api/rest_v1/page/pdf/Chat/a4", [stage["url"] for stage in downloads])
        for stage in downloads:
            self.assertGreaterEqual(stage["download_s"], 0)
            self.assertGreaterEqual(stage["fit_s"], 0)
            self.assertGreater(stage["pages"], 0)
        for text in ("example.org", "wikimedia", "rest_v1", '"url"'):
            self.assertNotIn(text, output.getvalue())

    def test_background_images_go_to_disk_not_to_the_assembly_project(self):
        seen = {}
        original = main._finish_book

        def spy(project, selected, language, workdir, fitted, background_files, report):
            seen["project"] = project
            seen["files"] = {field: (path.name, mime, title, path.read_bytes()) for field, (path, mime, title) in background_files.items()}
            return original(project, selected, language, workdir, fitted, background_files, report)

        with patch.object(main, "_finish_book", spy):
            events = _parse_stream(self.client.post("/api/pdf/stream", json=self._project()).content)
        self.assertEqual(events[-1]["type"], "done")
        self.assertIsNone(seen["project"].cover_image)
        self.assertIsNone(seen["project"].back_image)
        self.assertEqual(sorted(seen["files"]), ["back_image", "cover_image"])
        self.assertEqual(seen["files"]["cover_image"][:3], ("cover_image.image", "image/png", "Couverture"))
        self.assertEqual(seen["files"]["cover_image"][3], _png())

    def test_unreachable_image_stops_the_generation_with_its_address(self):
        del self.files[self.BACK]
        events = _parse_stream(self.client.post("/api/pdf/stream", json=self._project()).content)
        self.assertEqual(events[-1]["type"], "error")
        self.assertIn(self.BACK, events[-1]["detail"])
        self.assertFalse(any(e["type"] == "done" for e in events))

    def test_unexpected_file_type_is_refused(self):
        self.files[self.COVER] = (b"<html></html>", "text/html")
        events = _parse_stream(self.client.post("/api/pdf/stream", json=self._project()).content)
        self.assertEqual(events[-1]["type"], "error")
        self.assertIn("text/html", events[-1]["detail"])

    def test_unreachable_document_gives_a_502_on_api_pdf(self):
        del self.files[self.PHOTO]
        response = self.client.post("/api/pdf", json=self._project())
        self.assertEqual(response.status_code, 502)
        self.assertIn(self.PHOTO, response.json()["detail"])



class WebPageRenderingTest(unittest.TestCase):
    PAGE = "https://github.com/gmoulard/wikipedia2book"
    STYLE = "https://github.githubassets.com/assets/github.css"

    def setUp(self):
        self.files = {
            self.PAGE: (f'<html><head><link rel="stylesheet" href="{self.STYLE}"><style>.inline {{ color: red }}</style></head><body><p style="color: blue">README Wikipedia2Book</p></body></html>'.encode(), "text/html"),
            self.STYLE: (b".markdown-body { color: var(--fgColor-default); }", "text/css"),
        }
        self.rendered = []
        self.fail_with_styles = True
        self.fail_without_styles = False

        async def fake_download(url, max_bytes, label):
            if url not in self.files:
                raise main.JsonSourceError(502, f"Introuvable : {url}")
            return self.files[url]

        def fake_generate(html):
            self.rendered.append(html)
            if "README" in html:
                styled = "markdown-body" in html or ".inline" in html or 'style="' in html
                if (styled and self.fail_with_styles) or (not styled and self.fail_without_styles):
                    raise KeyError("--fgColor-default")
            return _make_pdf(1)

        self.patches = [
            patch.object(main, "MediaWikiClient", FakeClient),
            patch.object(main, "generate_pdf", fake_generate),
            patch.object(main, "download", fake_download),
        ]
        for p in self.patches:
            p.start()
        FakeClient.fail = False
        FakeClient.wait = None
        FakeClient.missing = ()
        self.client = TestClient(main.app)

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def _project(self):
        documents = [
            {"title": "wikipedia2book", "kind": "html", "url": self.PAGE, "selected": True},
            {"title": "Alos", "kind": "pdf", "mime_type": "application/pdf", "data_base64": base64.b64encode(_make_pdf(3)).decode("ascii"), "selected": True},
        ]
        return {"name": "Mon livre", "main_articles": [], "uploaded_documents": documents}

    def test_page_that_weasyprint_cannot_render_with_its_styles_is_rendered_without_them(self):
        events = _parse_stream(self.client.post("/api/pdf/stream", json=self._project()).content)
        self.assertEqual(events[-1]["type"], "done")
        pages = [html for html in self.rendered if "README" in html]
        self.assertEqual(len(pages), 2)
        self.assertNotIn("markdown-body", pages[1])
        self.assertNotIn(".inline", pages[1])
        self.assertNotIn('style="color: blue"', pages[1])
        self.assertIn("@page { size: 210mm 297mm; margin: 15mm; }", pages[1])
        stages = [stage for stage in main.generation_log[-1]["stages"] if stage["stage"] == "html_without_styles"]
        self.assertEqual([(stage["url"], stage["error"]) for stage in stages], [(self.PAGE, "KeyError")])
        pdf = PdfReader(BytesIO(events[-1]["pdf"]))
        self.assertEqual(len(pdf.pages), 1 + 1 + 1 + 3 + 1)

    def test_page_that_cannot_be_rendered_at_all_is_named_in_the_error(self):
        self.fail_without_styles = True
        events = _parse_stream(self.client.post("/api/pdf/stream", json=self._project()).content)
        self.assertEqual(events[-1]["type"], "error")
        detail = events[-1]["detail"]
        self.assertIn("« wikipedia2book »", detail)
        self.assertIn(self.PAGE, detail)
        self.assertIn("KeyError", detail)
        self.assertNotIn("La génération du PDF a échoué", detail)
        response = self.client.post("/api/pdf", json=self._project())
        self.assertEqual(response.status_code, 502)
        self.assertIn("« wikipedia2book »", response.json()["detail"])

    def test_damaged_imported_pdf_is_named_in_the_error(self):
        project = self._project()
        project["uploaded_documents"][1]["data_base64"] = base64.b64encode(b"%PDF-1.7 pas un vrai PDF").decode("ascii")
        self.fail_with_styles = False
        events = _parse_stream(self.client.post("/api/pdf/stream", json=project).content)
        self.assertEqual(events[-1]["type"], "error")
        self.assertIn("Le document « Alos » n’a pas pu être intégré au livre", events[-1]["detail"])

    def test_unexpected_server_error_is_not_the_same_sentence_twice(self):
        self.assertEqual(main._pdf_error_detail(KeyError("x")), "erreur inattendue du serveur (KeyError).")

if __name__ == "__main__":
    unittest.main()
