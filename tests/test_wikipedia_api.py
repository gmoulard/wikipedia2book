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


if __name__ == "__main__":
    unittest.main()
