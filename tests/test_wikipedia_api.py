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
import unittest
from unittest.mock import AsyncMock, Mock

from app.wikipedia_api import MediaWikiClient, MediaWikiPageNotFound


def _book_client(wikitext):
    client = MediaWikiClient()
    client._get = AsyncMock(
        return_value={"query": {"pages": [{"revisions": [{"slots": {"main": {"content": wikitext}}}]}]}}
    )
    return client


class GetBookTest(unittest.TestCase):
    def test_preserves_wikitext_order_and_skips_namespaced_links(self):
        wikitext = (
            "== Titre du livre ==\n"
            ":[[Second article]]\n"
            ":[[Premier article|texte affiché]]\n"
            ":[[Catégorie:Ignoré]]\n"
            ":[[Utilisateur:Auteur]]\n"
        )
        book = asyncio.run(_book_client(wikitext).get_book("Titre", "fr"))
        self.assertEqual(book.subtitle, "")
        self.assertEqual(book.chapters, [("", ["Second article", "Premier article"])])

    def test_reads_subtitle_and_chapters(self):
        wikitext = (
            "{{livre sauvegardé}}\n"
            "== Volcans ==\n"
            "=== Un tour du monde des '''éruptions''' ===\n"
            "==== Pas un sous-titre ====\n"
            ":[[Volcan]]\n"
            ";Europe\n"
            ":[[Etna]]\n"
            ":[[Vésuve]]\n"
            "; [[Amérique|Les Amériques]] \n"
            ":[[Montagne Pelée]]\n"
            ":[[Etna]]\n"
            ";Chapitre vide\n"
        )
        book = asyncio.run(_book_client(wikitext).get_book("Titre", "fr"))
        self.assertEqual(book.subtitle, "Un tour du monde des éruptions")
        self.assertEqual(
            book.chapters,
            [("", ["Volcan"]), ("Europe", ["Etna", "Vésuve"]), ("Les Amériques", ["Montagne Pelée"])],
        )

    def test_missing_page_raises(self):
        client = MediaWikiClient()
        client._get = AsyncMock(return_value={"query": {"pages": [{"missing": True}]}})
        with self.assertRaises(MediaWikiPageNotFound):
            asyncio.run(client.get_book("Titre", "fr"))


class GetArticlePdfTest(unittest.TestCase):
    def test_requests_the_given_paper_format(self):
        client = MediaWikiClient()
        client._client = AsyncMock()
        client._client.get.return_value = Mock(content=b"%PDF-1.7 ...", raise_for_status=Mock())
        pdf = asyncio.run(client.get_article_pdf("Montagne Pelée", "fr", "letter"))
        self.assertTrue(pdf.startswith(b"%PDF-"))
        self.assertEqual(
            client._client.get.call_args.args[0],
            "https://fr.wikipedia.org/api/rest_v1/page/pdf/Montagne_Pel%C3%A9e/letter",
        )

    def test_rejects_an_unknown_paper_format(self):
        client = MediaWikiClient()
        client._client = AsyncMock()
        with self.assertRaises(ValueError):
            asyncio.run(client.get_article_pdf("Chat", "fr", "a5"))
        client._client.get.assert_not_called()


class GetIntroAndCreatorTest(unittest.TestCase):
    def test_returns_extract_and_first_revision_author(self):
        client = MediaWikiClient()
        client._get = AsyncMock(side_effect=[
            {"query": {"pages": [{"extract": "Une introduction."}]}},
            {"query": {"pages": [{"revisions": [{"user": "Hashar"}]}]}},
        ])
        introduction, creator = asyncio.run(client.get_intro_and_creator("Chat", "fr"))
        self.assertEqual(introduction, "Une introduction.")
        self.assertEqual(creator, "Hashar")

    def test_missing_page_returns_empty_strings(self):
        client = MediaWikiClient()
        client._get = AsyncMock(side_effect=[
            {"query": {"pages": [{"missing": True}]}},
            {"query": {"pages": [{"revisions": []}]}},
        ])
        introduction, creator = asyncio.run(client.get_intro_and_creator("Inconnu", "fr"))
        self.assertEqual(introduction, "")
        self.assertEqual(creator, "")


class GetLinksPageOrderTest(unittest.TestCase):
    def test_returns_article_links_in_page_order(self):
        html = (
            '<div><table class="infobox"><a href="/wiki/Magma">magma</a></table>'
            '<p><a href="/wiki/Volcan">self</a> <a href="/wiki/%C3%89ruption_volcanique#Types">éruption</a>'
            ' <a href="/wiki/Fichier:Etna.jpg">image</a> <a class="new" href="/w/index.php?title=Inexistant&amp;redlink=1">rouge</a>'
            ' <a class="new" href="/wiki/Rouge">rouge</a> <a href="#cite_note-1">[1]</a>'
            ' <a href="/wiki/Magma">encore</a> <a href="/wiki/Lave">lave</a></p></div>'
        )
        client = MediaWikiClient()
        client._get = AsyncMock(return_value={"parse": {"title": "Volcan", "text": html}})

        links = asyncio.run(client.get_links("Volcan", "fr"))
        self.assertEqual(links, ["Magma", "Éruption volcanique", "Lave"])
        params = client._get.call_args.args[1]
        self.assertEqual((params["action"], params["page"], params["prop"]), ("parse", "Volcan", "text"))


if __name__ == "__main__":
    unittest.main()


class GetPageTest(unittest.TestCase):
    def test_returns_normalized_title_and_namespace(self):
        client = MediaWikiClient()
        client._get = AsyncMock(return_value={"query": {"pages": [{"title": "Chat", "ns": 0}]}})
        self.assertEqual(asyncio.run(client.get_page("chat", "fr")), ("Chat", 0))
        self.assertEqual(client._get.call_args.args[1]["redirects"], 1)

    def test_missing_or_invalid_page_returns_none(self):
        for page in ({"title": "Xyz", "missing": True}, {"title": "[[", "invalid": True}):
            client = MediaWikiClient()
            client._get = AsyncMock(return_value={"query": {"pages": [page]}})
            self.assertIsNone(asyncio.run(client.get_page("Xyz", "fr")))
