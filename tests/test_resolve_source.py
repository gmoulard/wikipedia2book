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

import app.main as main
from app.wikipedia_api import MediaWikiError, WikipediaBook


class FakeClient:
    pages = {}
    calls = []
    fail = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def get_page(self, title, language):
        FakeClient.calls.append(("page", title, language))
        if FakeClient.fail:
            raise MediaWikiError("Impossible de joindre l’API Wikipédia.")
        return FakeClient.pages.get(title)

    async def get_book(self, title, language, limit=200):
        FakeClient.calls.append(("book", title, language))
        return WikipediaBook(subtitle="Sous-titre", chapters=[("", ["Chat"]), ("Partie", ["Chien"])])

    async def search(self, query, language, limit):
        FakeClient.calls.append(("search", query, language))
        return [{"page_id": 1, "title": "Chat domestique", "snippet": "", "url": "https://fr.wikipedia.org/wiki/Chat_domestique"}]


class ResolveSourceTest(unittest.TestCase):
    def setUp(self):
        FakeClient.pages = {}
        FakeClient.calls = []
        FakeClient.fail = False
        self.patch = patch.object(main, "MediaWikiClient", FakeClient)
        self.patch.start()
        self.client = TestClient(main.app)

    def tearDown(self):
        self.patch.stop()

    def resolve(self, text, language="fr"):
        return self.client.post("/api/sources/resolve", json={"input": text, "language": language})

    def test_article_url(self):
        FakeClient.pages = {"Épaves de la rade": ("Épaves de la rade", 0)}
        response = self.resolve("https://fr.wikipedia.org/wiki/%C3%89paves_de_la_rade")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["kind"], "article")
        self.assertEqual(body["article"]["title"], "Épaves de la rade")
        self.assertEqual(body["article"]["language"], "fr")

    def test_book_url_uses_url_language(self):
        title = "Utilisateur:X/Livres/Mon livre"
        FakeClient.pages = {title: (title, 2)}
        body = self.resolve("https://en.wikipedia.org/wiki/Utilisateur:X/Livres/Mon_livre", "fr").json()
        self.assertEqual(body["kind"], "book")
        self.assertEqual(body["book_title"], "Mon livre")
        self.assertEqual([a["title"] for a in body["book"]["articles"]], ["Chat", "Chien"])
        self.assertEqual(body["book"]["subtitle"], "Sous-titre")
        self.assertTrue(body["book"]["unassigned_first"])
        self.assertIn(("book", title, "en"), FakeClient.calls)

    def test_title_text_follows_redirect_to_article(self):
        FakeClient.pages = {"chat": ("Chat", 0)}
        body = self.resolve("  chat  ", "de").json()
        self.assertEqual(body["kind"], "article")
        self.assertEqual(body["article"]["title"], "Chat")
        self.assertEqual(body["article"]["url"], "https://de.wikipedia.org/wiki/Chat")

    def test_book_page_title_text(self):
        title = "Livre:Animaux"
        FakeClient.pages = {title: (title, 108)}
        body = self.resolve(title).json()
        self.assertEqual(body["kind"], "book")
        self.assertEqual(body["book_title"], "Animaux")

    def test_unknown_text_falls_back_to_search(self):
        body = self.resolve("chats du monde").json()
        self.assertEqual(body["kind"], "search")
        self.assertEqual(body["results"][0]["title"], "Chat domestique")
        self.assertIn(("search", "chats du monde", "fr"), FakeClient.calls)

    def test_unknown_url_is_404(self):
        self.assertEqual(self.resolve("https://fr.wikipedia.org/wiki/Inexistant").status_code, 404)

    def test_book_without_articles_is_422(self):
        FakeClient.pages = {"Livre:Vide": ("Livre:Vide", 108)}
        with patch.object(FakeClient, "get_book", lambda self, *a, **k: _empty_book()):
            self.assertEqual(self.resolve("Livre:Vide").status_code, 422)

    def test_invalid_inputs(self):
        self.assertEqual(self.resolve("https://example.com/wiki/Chat").status_code, 422)
        self.assertEqual(self.resolve("   ").status_code, 422)
        self.assertEqual(self.client.post("/api/sources/resolve", json={"input": ""}).status_code, 422)
        self.assertEqual(self.resolve("Chat", "FR!").status_code, 422)

    def test_wikipedia_unreachable_is_502(self):
        FakeClient.fail = True
        self.assertEqual(self.resolve("Chat").status_code, 502)


async def _empty_book():
    return WikipediaBook(subtitle="", chapters=[])


if __name__ == "__main__":
    unittest.main()
