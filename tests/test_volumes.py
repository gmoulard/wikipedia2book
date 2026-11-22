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
import types
import unittest
from unittest.mock import AsyncMock, patch

try:
    import weasyprint  # noqa: F401
except Exception:
    fake = types.ModuleType("weasyprint")
    fake.HTML = lambda *a, **k: None
    sys.modules["weasyprint"] = fake

from fastapi import Response
from fastapi.testclient import TestClient

import app.main as main
from app.models import Article, BookChapter, Project, UploadedDocument
from app.volumes import book_volumes, volume_project
from app.wikipedia_api import wikimedia_file_page


def article(n):
    return Article(title=f"Article {n}", language="fr", url=f"https://fr.wikipedia.org/wiki/Article_{n}", selected=True)


def book(count, chapters=(), **fields):
    articles = [article(n) for n in range(count)]
    built = [BookChapter(id=f"c{index}", title=f"Chapitre {index}", article_keys=[articles[n].key for n in members]) for index, members in enumerate(chapters)]
    return Project(name="Livre", book_title="Livre", main_articles=articles, chapters=built, introduction="Intro", conclusion="Fin", **fields)


def titles(volumes):
    return [[item.title for item in volume] for volume in volumes]


class BookVolumesTest(unittest.TestCase):
    def test_no_split_under_the_limit(self):
        self.assertEqual(len(book_volumes(book(5), 300)), 1)
        self.assertEqual(len(book_volumes(book(5), None)), 1)

    def test_split_between_chapters_when_a_chapter_fits(self):
        project = book(6, chapters=[(0, 1, 2), (3, 4, 5)])
        self.assertEqual(titles(book_volumes(project, 4)), [["Article 0", "Article 1", "Article 2"], ["Article 3", "Article 4", "Article 5"]])

    def test_chapter_larger_than_the_limit_is_cut_inside(self):
        self.assertEqual([len(volume) for volume in book_volumes(book(5, chapters=[(0, 1, 2, 3, 4)]), 2)], [2, 2, 1])

    def test_documents_do_not_count_toward_the_limit(self):
        project = book(2)
        project.uploaded_documents = [UploadedDocument(id=f"d{n}", title=f"Doc {n}", kind="image", mime_type="image/png", data_base64="aGVsbG8=") for n in range(3)]
        self.assertEqual(len(book_volumes(project, 2)), 1)

    def test_manual_breaks_come_first_and_are_ignored_on_first_item_or_empty_chapter(self):
        project = book(4, volume_breaks=["before:fr:title:article 2", "before:fr:title:article 0"])
        self.assertEqual(titles(book_volumes(project, 300)), [["Article 0", "Article 1"], ["Article 2", "Article 3"]])
        project = book(4, chapters=[(0, 1), ()], volume_breaks=["before:chapter:c1"])
        self.assertEqual(len(book_volumes(project, 300)), 1)
        project = book(4, chapters=[(0, 1), (2, 3)], volume_breaks=["before:chapter:c1"])
        self.assertEqual(titles(book_volumes(project, 300)), [["Article 0", "Article 1"], ["Article 2", "Article 3"]])

    def test_volume_project_keeps_only_its_items_and_numbers_the_title(self):
        project = book(4, volume_breaks=["before:fr:title:article 2"])
        volumes = book_volumes(project, 300)
        first, last = (volume_project(project, items, index, 2, "fr") for index, items in enumerate(volumes))
        self.assertEqual(first.book_title, "Livre — Tome 1/2")
        self.assertEqual(last.book_title, "Livre — Tome 2/2")
        self.assertEqual([a.title for a in first.main_articles if a.selected], ["Article 0", "Article 1"])
        self.assertEqual((first.introduction, first.conclusion, last.introduction, last.conclusion), ("Intro", "", "", "Fin"))
        self.assertTrue(all(a.selected for a in project.main_articles))


class VolumeEndpointsTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(main.app)
        self.limit = patch.object(main, "ARTICLE_LIMIT", 2)
        self.limit.start()

    def tearDown(self):
        self.limit.stop()

    def test_plan_lists_the_volumes(self):
        response = self.client.post("/api/books/volumes", params={"language": "en"}, json=book(5).model_dump(mode="json"))
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["limit"], 2)
        self.assertEqual([v["articles"] for v in body["volumes"]], [2, 2, 1])
        self.assertEqual(body["volumes"][2]["title"], "Livre — Volume 3/3")

    def test_too_many_articles_tells_how_many_volumes(self):
        response = self.client.post("/api/pdf", json=book(5).model_dump(mode="json"))
        self.assertEqual(response.status_code, 413)
        self.assertEqual(response.json()["detail"]["volumes"], 3)

    def test_volume_parameter_generates_that_volume(self):
        created = AsyncMock(return_value=Response(b"%PDF-1.7", media_type="application/pdf"))
        with patch.object(main, "_create_pdf_response", created):
            response = self.client.post("/api/pdf", params={"volume": 3}, json=book(5).model_dump(mode="json"))
        self.assertEqual(response.status_code, 200)
        project, language = created.await_args.args
        self.assertEqual([a.title for a in project.main_articles if a.selected], ["Article 4"])
        self.assertEqual(project.book_title, "Livre — Tome 3/3")
        self.assertEqual(self.client.post("/api/pdf", params={"volume": 4}, json=book(5).model_dump(mode="json")).status_code, 422)


class DirectGenerationTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(main.app)
        self.created = AsyncMock(return_value=Response(b"%PDF-1.7", media_type="application/pdf"))
        self.patch = patch.object(main, "_create_pdf_response", self.created)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()

    def test_json_body_in_every_accepted_shape(self):
        payload = book(2).model_dump(mode="json")
        for body in ({"format": "wikipedia2book-workspace", "version": 1, "projects": [payload]}, [payload], payload):
            with self.subTest(shape=type(body).__name__):
                self.assertEqual(self.client.post("/api/pdf/from-json", json=body).status_code, 200)
        self.assertEqual(self.client.post("/api/pdf/from-json", json={"format": "wikipedia2book-workspace", "version": 2, "projects": [payload]}).status_code, 422)

    def test_pasted_book_page_generates_a_pdf(self):
        response = self.client.post("/api/pdf/from-wikitext", params={"language": "en"}, json={"wikitext": "== Ports ==\n:[[Brest]]\n;Finistère\n:[[Concarneau]]"})
        self.assertEqual(response.status_code, 200)
        project, language = self.created.await_args.args
        self.assertEqual((project.book_title, language), ("Ports", "en"))
        self.assertEqual([a.title for a in project.main_articles], ["Brest", "Concarneau"])
        self.assertTrue(project.unassigned_first)
        self.assertEqual(self.client.post("/api/pdf/from-wikitext", json={"wikitext": "rien"}).status_code, 422)


class WikimediaFilePageTest(unittest.TestCase):
    def test_file_pages_are_recognised_on_wikimedia_hosts_only(self):
        self.assertEqual(wikimedia_file_page("https://commons.wikimedia.org/wiki/File:La_Pel%C3%A9e.jpg"), ("commons.wikimedia.org", "La Pelée.jpg"))
        self.assertEqual(wikimedia_file_page("https://fr.wikipedia.org/wiki/Fichier:Brest.jpg"), ("fr.wikipedia.org", "Brest.jpg"))
        for url in ("https://upload.wikimedia.org/wikipedia/commons/1/16/x.jpg", "https://example.org/wiki/File:x.jpg", "http://commons.wikimedia.org/wiki/File:x.jpg"):
            self.assertIsNone(wikimedia_file_page(url))

    def test_remote_file_resolves_the_file_page_first(self):
        class Client:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *exc):
                return False

            async def get_file_url(self, host, name):
                return "https://upload.wikimedia.org/wikipedia/commons/1/16/x.jpg"

        download = AsyncMock(return_value=(b"image", "image/jpeg"))
        with patch.object(main, "MediaWikiClient", Client), patch.object(main, "download", download):
            data = main.asyncio.run(main.fetch_remote_file("https://commons.wikimedia.org/wiki/File:x.jpg", {"image/jpeg"}, main.BACKGROUND_FILE_BYTES, "l’image"))
        self.assertEqual(data, (b"image", "image/jpeg"))
        self.assertEqual(download.await_args.args[0], "https://upload.wikimedia.org/wikipedia/commons/1/16/x.jpg")


if __name__ == "__main__":
    unittest.main()
