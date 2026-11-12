import asyncio
import unittest
from unittest.mock import AsyncMock

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
