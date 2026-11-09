import asyncio
import unittest
from unittest.mock import AsyncMock

from app.wikipedia_api import MediaWikiClient, MediaWikiPageNotFound


class GetBookLinksOrderTest(unittest.TestCase):
    def test_preserves_wikitext_order_and_skips_namespaced_links(self):
        wikitext = (
            "== Chapitre ==\n"
            ":[[Second article]]\n"
            ":[[Premier article|texte affiché]]\n"
            ":[[Catégorie:Ignoré]]\n"
            ":[[Utilisateur:Auteur]]\n"
        )
        payload = {
            "query": {
                "pages": [{"revisions": [{"slots": {"main": {"content": wikitext}}}]}]
            }
        }
        client = MediaWikiClient()
        client._get = AsyncMock(return_value=payload)

        links = asyncio.run(client.get_book_links("Titre", "fr"))
        self.assertEqual(links, ["Second article", "Premier article"])

    def test_missing_page_raises(self):
        client = MediaWikiClient()
        client._get = AsyncMock(return_value={"query": {"pages": [{"missing": True}]}})
        with self.assertRaises(MediaWikiPageNotFound):
            asyncio.run(client.get_book_links("Titre", "fr"))


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


if __name__ == "__main__":
    unittest.main()
