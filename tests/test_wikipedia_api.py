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

import httpx
from unittest.mock import AsyncMock

from app.models import Article
from app.wikipedia_api import USER_AGENT, MediaWikiClient, MediaWikiPageNotFound, article_url, book_wikitext_title, parse_article_url, parse_book_wikitext, subpage_chapters


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


class BookWikitextTest(unittest.TestCase):
    WIKITEXT = "== Ports de ''Bretagne'' ==\n=== Guide des [[Port|ports]] ===\n:[[Brest]]\n;Finistère\n:[[Concarneau|Concarneau (port)]]\n:[[Catégorie:Port]]\n;Vide\n;[[Morbihan]]\n:[[Lorient#Port]]\n:[[Brest]]\n"

    def test_pasted_book_page_keeps_order_chapters_subtitle_and_title(self):
        book = parse_book_wikitext(self.WIKITEXT)
        self.assertEqual(book.subtitle, "Guide des ports")
        self.assertEqual(book.chapters, [("", ["Brest"]), ("Finistère", ["Concarneau"]), ("Morbihan", ["Lorient"])])
        self.assertEqual(book_wikitext_title(self.WIKITEXT), "Ports de Bretagne")

    def test_limit_and_missing_title(self):
        book = parse_book_wikitext("\n".join(f":[[Article {n}]]" for n in range(10)), limit=3)
        self.assertEqual(book.chapters, [("", ["Article 0", "Article 1", "Article 2"])])
        self.assertEqual(book_wikitext_title("=== Sous-titre ===\n:[[Brest]]"), "")


class GetArticlePdfTest(unittest.TestCase):
    def test_requests_the_given_paper_format(self):
        requests = []

        def handle(request):
            requests.append(request)
            return httpx.Response(200, content=b"%PDF-1.7 ...")

        async def run():
            async with MediaWikiClient() as client:
                await client._client.aclose()
                client._client = httpx.AsyncClient(transport=httpx.MockTransport(handle), headers={"User-Agent": USER_AGENT})
                return await client.get_article_pdf("Montagne Pelée", "fr", "letter")

        pdf = asyncio.run(run())
        self.assertTrue(pdf.startswith(b"%PDF-"))
        self.assertEqual(str(requests[0].url), "https://fr.wikipedia.org/api/rest_v1/page/pdf/Montagne_Pel%C3%A9e/letter")
        self.assertEqual(requests[0].headers["User-Agent"], USER_AGENT)

    def test_wikisource_pdf_comes_from_wikisource(self):
        requests = []

        def handle(request):
            requests.append(request)
            return httpx.Response(200, content=b"%PDF-1.7 ...")

        async def run():
            async with MediaWikiClient() as client:
                await client._client.aclose()
                client._client = httpx.AsyncClient(transport=httpx.MockTransport(handle))
                return await client.get_article_pdf("論語", "zh", "a4", "wikisource")

        asyncio.run(run())
        self.assertEqual(str(requests[0].url), "https://zh.wikisource.org/api/rest_v1/page/pdf/%E8%AB%96%E8%AA%9E/a4")

    def test_every_project_pdf_comes_from_its_own_site(self):
        for site in ("wikibooks", "wikivoyage", "wikiversity", "wikiquote", "wiktionary", "wikinews"):
            requests = []

            def handle(request):
                requests.append(request)
                return httpx.Response(200, content=b"%PDF-1.7 ...")

            async def run():
                async with MediaWikiClient() as client:
                    await client._client.aclose()
                    client._client = httpx.AsyncClient(transport=httpx.MockTransport(handle))
                    return await client.get_article_pdf("Programmation Python", "fr", "a4", site)

            with self.subTest(site=site):
                asyncio.run(run())
                self.assertEqual(str(requests[0].url), f"https://fr.{site}.org/api/rest_v1/page/pdf/Programmation_Python/a4")

    def test_rejects_an_unknown_site(self):
        client = MediaWikiClient()
        client._client = AsyncMock()
        with self.assertRaises(ValueError):
            asyncio.run(client.get_article_pdf("Chat", "fr", "a4", "wikidata"))
        client._client.get.assert_not_called()

    def test_rejects_an_unknown_paper_format(self):
        client = MediaWikiClient()
        client._client = AsyncMock()
        with self.assertRaises(ValueError):
            asyncio.run(client.get_article_pdf("Chat", "fr", "a5"))
        client._client.get.assert_not_called()


class SearchTest(unittest.TestCase):
    def test_search_targets_the_project_site(self):
        client = MediaWikiClient()
        client._get = AsyncMock(return_value={"query": {"search": [{"pageid": 3, "title": "Lyon", "snippet": "<b>Lyon</b>"}]}})
        results = asyncio.run(client.search("Lyon", "fr", 5, "wikivoyage"))
        self.assertEqual(client._get.call_args.args[2], "wikivoyage")
        self.assertEqual(results, [{"page_id": 3, "title": "Lyon", "snippet": "Lyon", "url": "https://fr.wikivoyage.org/wiki/Lyon", "language": "fr"}])


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



def _toc(*parts):
    return "<div>" + "".join(parts) + "</div>"


def _sub(title, label="x", css=""):
    return f'<a{css} href="/wiki/{title.replace(" ", "_")}">{label}</a>'


class WikibookChaptersTest(unittest.TestCase):
    def test_subpages_in_page_order_without_print_version_red_links_or_others(self):
        html = _toc(
            '<h2>Sommaire<span class="mw-editsection">[modifier]</span></h2>',
            _sub("Python/Version imprimable"), _sub("Python/Introduction"), _sub("Python/Variables"),
            _sub("Autre livre/Page"), _sub("Python/Rouge", css=' class="new"'), _sub("Python/Introduction"),
            _sub("Python/Boucles#Exemple"), _sub("Python/Boucles/Exercices"), _sub("Fichier:Logo.png"),
        )
        self.assertEqual(subpage_chapters(html, "Python"), [("", ["Python/Introduction", "Python/Variables", "Python/Boucles", "Python/Boucles/Exercices"])])

    def test_sections_become_chapters_at_the_first_level_that_splits_the_book(self):
        html = _toc(
            "<h2>Contents</h2>", _sub("Py/Print version"),
            "<h3>Intro</h3>", _sub("Py/Overview"), _sub("Py/Setup"),
            "<h3>Basics</h3>", _sub("Py/Variables"),
            "<h4>Details</h4>", _sub("Py/Strings"),
            "<h2>See also</h2>", '<a href="/wiki/Python">Python</a>',
        )
        self.assertEqual(subpage_chapters(html, "Py"), [("Intro", ["Py/Overview", "Py/Setup"]), ("Basics", ["Py/Variables", "Py/Strings"])])

    def test_pages_before_the_first_section_stay_without_chapter(self):
        html = _toc(_sub("L/Préface"), '<div class="mw-heading"><h2>Partie 1</h2></div>', _sub("L/A"), "<h2>Partie 2</h2>", _sub("L/B"))
        self.assertEqual(subpage_chapters(html, "L"), [("", ["L/Préface"]), ("Partie 1", ["L/A"]), ("Partie 2", ["L/B"])])

    def test_page_without_subpage_and_limit(self):
        self.assertEqual(subpage_chapters(_toc(_sub("Autre")), "L"), [])
        html = _toc(*[_sub(f"L/P{index}") for index in range(10)])
        self.assertEqual(subpage_chapters(html, "L", limit=3), [("", ["L/P0", "L/P1", "L/P2"])])

    def test_get_subpage_book_parses_the_rendered_page_on_wikibooks(self):
        client = MediaWikiClient()
        client._get = AsyncMock(return_value={"parse": {"title": "Python", "text": _toc(_sub("Python/A"), _sub("Python/B"))}})
        book = asyncio.run(client.get_subpage_book("python", "fr", "wikibooks"))
        self.assertEqual(book.chapters, [("", ["Python/A", "Python/B"])])
        language, params, site = client._get.call_args.args
        self.assertEqual((language, params["action"], params["prop"], site), ("fr", "parse", "text", "wikibooks"))

    def test_full_text_pages_are_ignored_like_print_versions(self):
        html = _toc(_sub("論語/序說"), _sub("論語/學而第一"), _sub("論語/全覽"), _sub("Bovary/Texte entier"), _sub("論語/爲政第二"))
        self.assertEqual(subpage_chapters(html, "論語"), [("", ["論語/序說", "論語/學而第一", "論語/爲政第二"])])

    def test_wikisource_skips_intermediate_tables_of_contents(self):
        html = _toc(
            "<h2>Première partie</h2>", _sub("M/Tome 1"), _sub("M/Tome 1/Livre 1"), _sub("M/Tome 1/Livre 1/01"), _sub("M/Tome 1/Livre 1/02"),
            "<h2>Deuxième partie</h2>", _sub("M/Tome 2/Livre 1/01"), _sub("M/Préface seule"),
        )
        self.assertEqual(subpage_chapters(html, "M", skip_parents=True),
                         [("Première partie", ["M/Tome 1/Livre 1/01", "M/Tome 1/Livre 1/02"]), ("Deuxième partie", ["M/Tome 2/Livre 1/01", "M/Préface seule"])])
        kept = [page for _, pages in subpage_chapters(html, "M") for page in pages]
        self.assertIn("M/Tome 1/Livre 1", kept)

    def test_get_subpage_book_skips_parents_only_on_wikisource(self):
        html = _toc(_sub("L/A"), _sub("L/A/1"), _sub("L/B"))
        for site, expected in (("wikisource", ["L/A/1", "L/B"]), ("wikibooks", ["L/A", "L/A/1", "L/B"])):
            client = MediaWikiClient()
            client._get = AsyncMock(return_value={"parse": {"title": "L", "text": html}})
            book = asyncio.run(client.get_subpage_book("L", "fr", site))
            self.assertEqual([page for _, pages in book.chapters for page in pages], expected, site)
            self.assertEqual(client._get.call_args.args[2], site)


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


class ParseArticleUrlTest(unittest.TestCase):
    def test_accepts_wikipedia_and_wikisource(self):
        self.assertEqual(parse_article_url("https://fr.wikipedia.org/wiki/Chat"), ("fr", "Chat", "wikipedia"))
        self.assertEqual(
            parse_article_url("https://fr.wikisource.org/wiki/Les_Fleurs_du_mal"), ("fr", "Les Fleurs du mal", "wikisource")
        )

    def test_accepts_the_other_language_projects(self):
        for site in ("wikibooks", "wikivoyage", "wikiversity", "wikiquote", "wiktionary", "wikinews"):
            with self.subTest(site=site):
                self.assertEqual(parse_article_url(f"https://de.{site}.org/wiki/Haus_und_Hof"), ("de", "Haus und Hof", site))
                self.assertEqual(article_url("de", "Haus und Hof", site), f"https://de.{site}.org/wiki/Haus_und_Hof")
                self.assertEqual(
                    Article(title="Haus", language="de", site=site, url=article_url("de", "Haus", site)).key,
                    f"{site}:de:title:haus",
                )

    def test_rejects_other_sites(self):
        for url in (
            "https://wikisource.org/wiki/Main_Page",
            "http://fr.wikisource.org/wiki/X",
            "https://commons.wikimedia.org/wiki/Main_Page",
            "https://www.wikidata.org/wiki/Q42",
            "https://species.wikimedia.org/wiki/Felis",
            "https://fr.wikibooks.org.example.com/wiki/X",
        ):
            with self.assertRaises(ValueError):
                parse_article_url(url)

    def test_wikisource_key_does_not_collide_with_wikipedia(self):
        wikipedia = Article(title="Chat", language="fr", url="https://fr.wikipedia.org/wiki/Chat")
        wikisource = Article(title="Chat", language="fr", site="wikisource", url="https://fr.wikisource.org/wiki/Chat")
        self.assertEqual(wikipedia.key, "fr:title:chat")
        self.assertEqual(wikisource.key, "wikisource:fr:title:chat")
        self.assertEqual(article_url("fr", "Les Fleurs du mal", "wikisource"), "https://fr.wikisource.org/wiki/Les_Fleurs_du_mal")


if __name__ == "__main__":
    unittest.main()
