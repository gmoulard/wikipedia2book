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
    wikibook = WikipediaBook(subtitle="", chapters=[])

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def get_page(self, title, language, site="wikipedia"):
        FakeClient.calls.append(("page", title, language, site))
        if FakeClient.fail:
            raise MediaWikiError("Impossible de joindre l’API Wikipédia.")
        return FakeClient.pages.get(title)

    async def get_book(self, title, language, limit=200):
        FakeClient.calls.append(("book", title, language))
        return WikipediaBook(subtitle="Sous-titre", chapters=[("", ["Chat"]), ("Partie", ["Chien"])])

    async def get_wikibook(self, title, language, limit=500):
        FakeClient.calls.append(("wikibook", title, language, "wikibooks"))
        return FakeClient.wikibook

    async def search(self, query, language, limit, site="wikipedia"):
        FakeClient.calls.append(("search", query, language, site))
        return [{"page_id": 1, "title": "Chat domestique", "snippet": "", "url": "https://fr.wikipedia.org/wiki/Chat_domestique"}]


class ResolveSourceTest(unittest.TestCase):
    def setUp(self):
        FakeClient.pages = {}
        FakeClient.calls = []
        FakeClient.fail = False
        FakeClient.wikibook = WikipediaBook(subtitle="", chapters=[])
        self.patch = patch.object(main, "MediaWikiClient", FakeClient)
        self.patch.start()
        self.client = TestClient(main.app)

    def tearDown(self):
        self.patch.stop()

    def resolve(self, text, language="fr", site="wikipedia"):
        return self.client.post("/api/sources/resolve", json={"input": text, "language": language, "site": site})

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
        self.assertIn(("search", "chats du monde", "fr", "wikipedia"), FakeClient.calls)

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

    def test_wikisource_text_url(self):
        FakeClient.pages = {"論語/學而第一": ("論語/學而第一", 0)}
        body = self.resolve("https://zh.wikisource.org/wiki/%E8%AB%96%E8%AA%9E/%E5%AD%B8%E8%80%8C%E7%AC%AC%E4%B8%80").json()
        self.assertEqual(body["kind"], "article")
        self.assertEqual(body["article"]["site"], "wikisource")
        self.assertEqual(body["article"]["language"], "zh")
        self.assertTrue(body["article"]["url"].startswith("https://zh.wikisource.org/wiki/"))
        self.assertIn(("page", "論語/學而第一", "zh", "wikisource"), FakeClient.calls)

    def test_wikisource_author_page_is_an_article(self):
        FakeClient.pages = {"Auteur:François Rabelais": ("Auteur:François Rabelais", 102)}
        body = self.resolve("https://fr.wikisource.org/wiki/Auteur:Fran%C3%A7ois_Rabelais").json()
        self.assertEqual(body["kind"], "article")
        self.assertEqual(body["article"]["title"], "Auteur:François Rabelais")
        self.assertEqual(body["article"]["site"], "wikisource")
        self.assertNotIn("book", [call[0] for call in FakeClient.calls])

    def test_spanish_wikisource_author_namespace_106_is_an_article(self):
        FakeClient.pages = {"Autor:Miguel de Cervantes": ("Autor:Miguel de Cervantes", 106)}
        self.assertEqual(self.resolve("https://es.wikisource.org/wiki/Autor:Miguel_de_Cervantes").json()["kind"], "article")

    def test_wikisource_talk_page_is_422(self):
        FakeClient.pages = {"Discussion Auteur:Victor Hugo": ("Discussion Auteur:Victor Hugo", 103)}
        self.assertEqual(self.resolve("https://fr.wikisource.org/wiki/Discussion_Auteur:Victor_Hugo").status_code, 422)

    def test_wikisource_non_content_namespace_is_422(self):
        FakeClient.pages = {"Aide:Accueil": ("Aide:Accueil", 12)}
        response = self.resolve("https://fr.wikisource.org/wiki/Aide:Accueil")
        self.assertEqual(response.status_code, 422)
        self.assertIn("pages de contenu", response.json()["detail"])
        self.assertNotIn("book", [call[0] for call in FakeClient.calls])

    def test_book_structure_refuses_wikisource(self):
        response = self.client.post("/api/books/structure", json={"url": "https://fr.wikisource.org/wiki/Livre:X"})
        self.assertEqual(response.status_code, 422)

    def test_other_wikimedia_projects_by_url(self):
        for site, url, title in (
            ("wikibooks", "https://fr.wikibooks.org/wiki/Programmation_Python", "Programmation Python"),
            ("wikivoyage", "https://fr.wikivoyage.org/wiki/Lyon", "Lyon"),
            ("wikiversity", "https://fr.wikiversity.org/wiki/Alg%C3%A8bre_lin%C3%A9aire", "Algèbre linéaire"),
            ("wikiquote", "https://fr.wikiquote.org/wiki/Victor_Hugo", "Victor Hugo"),
            ("wiktionary", "https://fr.wiktionary.org/wiki/chat", "chat"),
            ("wikinews", "https://en.wikinews.org/wiki/Main_Page", "Main Page"),
        ):
            with self.subTest(site=site):
                FakeClient.pages = {title: (title, 0)}
                body = self.resolve(url).json()
                self.assertEqual(body["kind"], "article")
                self.assertEqual(body["article"]["site"], site)
                self.assertTrue(body["article"]["url"].startswith(f"https://{url.split('/')[2]}/wiki/"))
                self.assertEqual(FakeClient.calls[-1][3], site)

    def test_title_on_another_project_searches_that_project(self):
        FakeClient.pages = {"Programmation Python": ("Programmation Python", 0)}
        body = self.resolve("Programmation Python", "fr", "wikibooks").json()
        self.assertEqual(body["article"]["site"], "wikibooks")
        self.assertEqual(body["article"]["url"], "https://fr.wikibooks.org/wiki/Programmation_Python")
        body = self.resolve("Pyhton", "fr", "wikibooks").json()
        self.assertEqual(body["kind"], "search")
        self.assertIn(("search", "Pyhton", "fr", "wikibooks"), FakeClient.calls)

    def test_other_project_namespace_is_422(self):
        FakeClient.pages = {"Wikilivres:Accueil": ("Wikilivres:Accueil", 4)}
        self.assertEqual(self.resolve("https://fr.wikibooks.org/wiki/Wikilivres:Accueil").status_code, 422)
        self.assertNotIn("book", [call[0] for call in FakeClient.calls])

    def test_unknown_site_is_422(self):
        self.assertEqual(self.resolve("Chat", "fr", "wikidata").status_code, 422)
        self.assertEqual(self.resolve("https://commons.wikimedia.org/wiki/Main_Page").status_code, 422)

    def test_add_article_by_title_on_another_project(self):
        response = self.client.post("/api/articles", json={"title": "Lyon", "language": "fr", "site": "wikivoyage"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["url"], "https://fr.wikivoyage.org/wiki/Lyon")
        self.assertEqual(response.json()["site"], "wikivoyage")

    def test_wikibooks_table_of_contents_offers_the_whole_book(self):
        FakeClient.pages = {"Programmation Python": ("Programmation Python", 0)}
        FakeClient.wikibook = WikipediaBook(subtitle="", chapters=[
            ("Bases", ["Programmation Python/Variables", "Programmation Python/Boucles"]),
            ("Modules", ["Programmation Python/Modules"]),
        ])
        body = self.resolve("https://fr.wikibooks.org/wiki/Programmation_Python").json()
        self.assertEqual(body["kind"], "wikibook")
        self.assertEqual((body["article"]["title"], body["article"]["site"]), ("Programmation Python", "wikibooks"))
        self.assertEqual(body["book_title"], "Programmation Python")
        articles = body["book"]["articles"]
        self.assertEqual([a["title"] for a in articles], ["Programmation Python/Variables", "Programmation Python/Boucles", "Programmation Python/Modules"])
        self.assertTrue(all(a["site"] == "wikibooks" and a["url"].startswith("https://fr.wikibooks.org/wiki/") for a in articles))
        self.assertEqual([c["title"] for c in body["book"]["chapters"]], ["Bases", "Modules"])
        self.assertEqual(body["book"]["chapters"][0]["article_keys"], ["wikibooks:fr:title:programmation python/variables", "wikibooks:fr:title:programmation python/boucles"])

    def test_wikibooks_page_without_subpages_is_an_article(self):
        FakeClient.pages = {"Programmation Python/Variables": ("Programmation Python/Variables", 0)}
        FakeClient.wikibook = WikipediaBook(subtitle="", chapters=[("", ["Programmation Python/Variables/Exemple"])])
        body = self.resolve("Programmation Python/Variables", site="wikibooks").json()
        self.assertEqual(body["kind"], "article")

    def test_other_projects_never_look_for_a_table_of_contents(self):
        FakeClient.pages = {"Lyon": ("Lyon", 0)}
        self.assertEqual(self.resolve("Lyon", site="wikivoyage").json()["kind"], "article")
        self.assertNotIn("wikibook", [call[0] for call in FakeClient.calls])

    def test_wikipedia_unreachable_is_502(self):
        FakeClient.fail = True
        self.assertEqual(self.resolve("Chat").status_code, 502)


async def _empty_book():
    return WikipediaBook(subtitle="", chapters=[])


if __name__ == "__main__":
    unittest.main()
