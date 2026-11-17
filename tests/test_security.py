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
import ipaddress
import re
import sys
import time
import types
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    import weasyprint  # noqa: F401
    REAL_WEASYPRINT = hasattr(weasyprint, "URLFetcher")
except Exception:
    REAL_WEASYPRINT = False
    fake = types.ModuleType("weasyprint")
    fake.HTML = lambda *a, **k: None
    sys.modules["weasyprint"] = fake

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx
from fastapi.testclient import TestClient
from pydantic import ValidationError

import app.main as main
from app import pdf_generator
from app.book_builder import (
    build_chapter_page_html,
    build_conclusion_page_html,
    build_cover_html,
    build_license_page_html,
    build_toc_html,
)
from app.json_source import JsonSourceError, download
from app.models import Article, BookChapter, BookImage, Project, UploadedDocument
from app.wikipedia_api import (
    book_wikitext_title,
    is_printable_wikitext,
    parse_book_wikitext,
    parse_printable_wikitext,
    printable_wikitext_title,
)

PUBLIC = "93.184.216.34"
HOSTS = {"public.example.org": [PUBLIC]}
INTERNAL_ADDRESSES = [
    "127.0.0.1", "127.1.2.3", "10.0.0.5", "172.16.0.1", "192.168.1.1", "169.254.169.254", "100.64.0.1",
    "0.0.0.0", "255.255.255.255", "224.0.0.1", "::1", "::", "fc00::1", "fe80::1%eth0", "::ffff:127.0.0.1",
    "::ffff:10.0.0.5", "::ffff:169.254.169.254", "64:ff9b::7f00:1", "64:ff9b::a9fe:a9fe", "2002:7f00:1::1",
    "2002:a00:5::1", "2001:db8::1", "ff02::1", "ff0e::1",
]
PAYLOAD = '<img src="file:///etc/passwd"></style><link rel="stylesheet" href="http://169.254.169.254/"><script>x</script>'
PNG = base64.b64encode(b"\x89PNG\r\n\x1a\n" + b"\x00" * 16).decode()


def resolve(host):
    try:
        ipaddress.ip_address(host.split("%")[0])
        return [host]
    except ValueError:
        if host not in HOSTS:
            raise OSError("unknown host")
        return HOSTS[host]


def run_download(url, handler=None, resolver=resolve):
    calls = []

    def recording(request):
        calls.append(request)
        return handler(request) if handler else httpx.Response(200, content=b"{}")

    try:
        return asyncio.run(download(url, 1_000_000, "le fichier JSON", httpx.MockTransport(recording), resolver)), calls
    except JsonSourceError as error:
        return error, calls


class RemoteDownloadTest(unittest.TestCase):
    def test_only_https_is_accepted(self):
        for url in ("http://public.example.org/livre.json", "ftp://public.example.org/livre.json", "file:///etc/passwd",
                    "gopher://public.example.org/", "data:application/json,{}", "https:///livre.json", "//public.example.org/x"):
            with self.subTest(url=url):
                result, calls = run_download(url)
                self.assertIsInstance(result, JsonSourceError)
                self.assertEqual(result.status_code, 422)
                self.assertEqual(calls, [])

    def test_internal_addresses_are_refused(self):
        for address in INTERNAL_ADDRESSES:
            with self.subTest(address=address):
                result, calls = run_download("https://evil.example.org/livre.json", resolver=lambda host, a=address: [a])
                self.assertIsInstance(result, JsonSourceError)
                self.assertEqual(result.status_code, 422)
                self.assertEqual(calls, [])

    def test_ip_literals_and_disguised_hosts_are_refused(self):
        for url in ("https://127.0.0.1/x.json", "https://[::1]/x.json", "https://[::ffff:127.0.0.1]/x.json",
                    "https://public.example.org@127.0.0.1/x.json", "https://169.254.169.254/latest/meta-data/"):
            with self.subTest(url=url):
                result, calls = run_download(url)
                self.assertIsInstance(result, JsonSourceError)
                self.assertEqual(calls, [])

    def test_host_with_one_internal_address_among_public_ones_is_refused(self):
        result, calls = run_download("https://mixed.example.org/x.json", resolver=lambda host: [PUBLIC, "10.0.0.5"])
        self.assertIsInstance(result, JsonSourceError)
        self.assertEqual(calls, [])

    def test_decimal_and_octal_hosts_resolving_inside_are_refused(self):
        for host in ("2130706433", "0x7f000001", "017700000001"):
            with self.subTest(host=host):
                result, calls = run_download(f"https://{host}/x.json", resolver=lambda name: ["127.0.0.1"])
                self.assertIsInstance(result, JsonSourceError)
                self.assertEqual(calls, [])

    def test_redirects_are_checked_again(self):
        for location in ("http://public.example.org/x.json", "https://127.0.0.1/x.json", "https://[::1]/x.json", "file:///etc/passwd"):
            with self.subTest(location=location):
                result, calls = run_download("https://public.example.org/x.json", lambda request, l=location: httpx.Response(302, headers={"location": l}))
                self.assertIsInstance(result, JsonSourceError)
                self.assertEqual(len(calls), 1)

    def test_endless_redirects_stop(self):
        result, calls = run_download("https://public.example.org/x.json", lambda request: httpx.Response(302, headers={"location": "/again"}))
        self.assertIsInstance(result, JsonSourceError)
        self.assertEqual(result.status_code, 502)
        self.assertLessEqual(len(calls), 4)

    def test_connection_goes_to_the_checked_address(self):
        answers = iter([[PUBLIC], ["127.0.0.1"]])
        result, calls = run_download("https://public.example.org/x.json", resolver=lambda host: next(answers))
        self.assertEqual(result[0], b"{}")
        self.assertEqual(calls[0].url.host, PUBLIC)
        self.assertEqual(calls[0].headers["host"], "public.example.org")

    def test_size_limit_without_content_length(self):
        async def chunks():
            yield b"x" * 600_000
            yield b"x" * 600_000

        def stream(request):
            return httpx.Response(200, content=chunks())

        result, _ = run_download("https://public.example.org/x.json", stream)
        self.assertIsInstance(result, JsonSourceError)
        self.assertEqual(result.status_code, 413)


def hostile_book():
    titled = Article(title='A"><img src=x onerror=alert(1)>', language="fr", url="https://fr.wikipedia.org/wiki/A", selected=True)
    plain = Article(title=PAYLOAD, language="fr", page_id=7, url="https://fr.wikipedia.org/wiki/B", selected=True)
    document = UploadedDocument(title=PAYLOAD, kind="image", mime_type="image/png", data_base64=PNG)
    return Project(
        name="Livre", book_title=PAYLOAD, book_subtitle=PAYLOAD, book_author=PAYLOAD, description=PAYLOAD,
        introduction=PAYLOAD, conclusion=PAYLOAD, main_articles=[titled, plain], uploaded_documents=[document],
        chapters=[BookChapter(id="c", title=PAYLOAD[:120], article_keys=[titled.key, plain.key])],
    )


class GeneratedHtmlTest(unittest.TestCase):
    def documents(self):
        project = hostile_book()
        items = project.main_articles + project.uploaded_documents
        return {
            "cover": build_cover_html(project),
            "toc": build_toc_html(project, items),
            "chapter": build_chapter_page_html(project, PAYLOAD),
            "conclusion": build_conclusion_page_html(project),
            "license": build_license_page_html(project, items),
        }

    def test_book_text_never_becomes_markup(self):
        for name, html in self.documents().items():
            with self.subTest(document=name):
                self.assertNotIn("<img src=\"file", html)
                self.assertNotIn("<img src=x", html)
                self.assertNotIn("<script", html)
                self.assertNotIn("169.254.169.254/\">", html)
                self.assertEqual(html.count("</style>"), 1)
                self.assertNotIn("<link", html)

    def test_only_expected_urls_are_referenced(self):
        for name, html in self.documents().items():
            with self.subTest(document=name):
                for url in re.findall(r'(?:src|href)="([^"]*)"', html):
                    self.assertTrue(url.startswith(("data:", "https://wikipedia2book.", "https://github.com/gmoulard/")), url)

    def test_toc_links_keep_the_key_inside_the_attribute(self):
        html = self.documents()["toc"]
        hrefs = re.findall(r'href="([^"]*)"', html)
        self.assertTrue(hrefs)
        for href in hrefs:
            self.assertRegex(href, r"^https://wikipedia2book\.invalid/toc/[A-Za-z0-9%._~-]+$")


class BackgroundImageTest(unittest.TestCase):
    def test_mime_type_cannot_escape_the_css(self):
        for mime_type in ('image/png") } @import url(file:///etc/passwd', "image/png;x", "text/css", "image/svg+xml\n", "IMAGE/PNG"):
            with self.subTest(mime_type=mime_type), self.assertRaises(ValidationError):
                BookImage(mime_type=mime_type, data_base64=PNG)

    def test_content_must_be_base64(self):
        for data in ('AAAA") } body { background: url(file:///etc/passwd', "AA AA", "<svg/>"):
            with self.subTest(data=data), self.assertRaises(ValidationError):
                BookImage(mime_type="image/png", data_base64=data)

    def test_remote_address_must_be_https_without_spaces(self):
        for url in ("http://example.org/a.png", "file:///etc/passwd", "https://example.org/a b.png", "javascript:alert(1)"):
            with self.subTest(url=url), self.assertRaises(ValidationError):
                BookImage(url=url)
            with self.subTest(document=url), self.assertRaises(ValidationError):
                UploadedDocument(title="Doc", kind="image", url=url)


class RenderFetcherTest(unittest.TestCase):
    def test_rendering_only_allows_data_uris(self):
        recorded = {}

        class Recorder:
            def __init__(self, string, url_fetcher=None):
                recorded["fetcher"] = url_fetcher

            def write_pdf(self):
                return b"%PDF"

        fake_module = types.SimpleNamespace(URLFetcher=lambda **options: ("fetcher", options))
        with patch.object(pdf_generator, "HTML", Recorder), patch.object(pdf_generator, "weasyprint", fake_module):
            self.assertEqual(pdf_generator.generate_pdf("<p>x</p>"), b"%PDF")
        self.assertEqual(recorded["fetcher"], ("fetcher", {"allowed_protocols": frozenset({"data"})}))

    @unittest.skipUnless(REAL_WEASYPRINT, "WeasyPrint indisponible (bibliothèques GTK absentes)")
    def test_real_fetcher_refuses_files_and_network(self):
        fetcher = weasyprint.URLFetcher(allowed_protocols=pdf_generator.RENDER_PROTOCOLS)
        for url in ("file:///etc/passwd", "http://169.254.169.254/latest/meta-data/", "https://example.org/a.png", "ftp://example.org/a"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                fetcher.fetch(url)
        self.assertEqual(fetcher.fetch("data:text/plain;base64,SGk=").read(), b"Hi")


EPS = b"%!PS-Adobe-3.0 EPSF-3.0\n%%BoundingBox: 0 0 100 100\n0 0 100 100 rectfill showpage\n%%EOF\n"


def png_bytes():
    from io import BytesIO

    from PIL import Image

    buffer = BytesIO()
    Image.new("RGB", (40, 60), "white").save(buffer, "PNG")
    return buffer.getvalue()


class ImageFormatTest(unittest.TestCase):
    def setUp(self):
        import PIL.EpsImagePlugin

        self.ghostscript_calls = []
        patcher = patch.object(PIL.EpsImagePlugin, "Ghostscript", lambda *a, **k: self.ghostscript_calls.append(a) or (_ for _ in ()).throw(OSError("ghostscript")))
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_uploaded_eps_is_never_handed_to_ghostscript(self):
        from PIL import UnidentifiedImageError

        with self.assertRaises(UnidentifiedImageError):
            pdf_generator.image_to_pdf(EPS, 210, 297)
        self.assertEqual(self.ghostscript_calls, [])
        self.assertTrue(pdf_generator.image_to_pdf(png_bytes(), 210, 297).startswith(b"%PDF"))

    def test_background_disguised_as_png_is_never_handed_to_ghostscript(self):
        from app.book_builder import cover_text_style, fit_background

        image = BookImage(mime_type="image/png", data_base64=base64.b64encode(EPS).decode())
        self.assertIs(fit_background(image, 10, 10), image)
        self.assertEqual(cover_text_style(image, 210, 297, (0, 0, 210, 200)), "band")
        self.assertEqual(self.ghostscript_calls, [])

    def test_weasyprint_has_the_image_and_fetcher_fixes(self):
        requirements = (Path(__file__).resolve().parent.parent / "requirements.txt").read_text(encoding="utf-8")
        version = re.search(r"^weasyprint==(\d+)\.", requirements, re.MULTILINE)
        self.assertGreaterEqual(int(version.group(1)), 70)


SLOW_S = 2.0
HOSTILE_WIKITEXTS = {
    "transclusion sans fin": "{{:a" + " " * 199_990,
    "transclusions ouvertes": "{{:" * 66_000,
    "barres": "{{:a|" + "|" * 199_990,
    "titres": "=" * 199_999 + "a",
    "titre et espaces": "= a" + " " * 199_990 + "x",
    "liens ouverts": ":[[" * 66_000,
    "chapitres": ";" + " " * 199_990 + "x",
    "paramètres": "|titre=" * 28_000,
    "accolades": "{{" * 100_000,
}


class HostileWikitextTest(unittest.TestCase):
    def test_parsers_stay_linear(self):
        parsers = (parse_printable_wikitext, parse_book_wikitext, is_printable_wikitext, book_wikitext_title, printable_wikitext_title)
        for name, text in HOSTILE_WIKITEXTS.items():
            for parser in parsers:
                with self.subTest(text=name, parser=parser.__name__):
                    start = time.perf_counter()
                    parser(text)
                    self.assertLess(time.perf_counter() - start, SLOW_S)

    def test_endpoint_answers_quickly(self):
        client = TestClient(main.app)
        start = time.perf_counter()
        response = client.post("/api/books/from-wikitext", json={"wikitext": HOSTILE_WIKITEXTS["transclusion sans fin"], "language": "fr"})
        self.assertLess(time.perf_counter() - start, SLOW_S)
        self.assertEqual(response.status_code, 422)

    def test_too_long_wikitext_is_refused(self):
        response = TestClient(main.app).post("/api/books/from-wikitext", json={"wikitext": "a" * 200_001, "language": "fr"})
        self.assertEqual(response.status_code, 422)


class ApiInputTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(main.app)
        self.book = {"name": "Livre", "main_articles": [{"title": "A", "language": "fr", "url": "https://fr.wikipedia.org/wiki/A", "selected": True}]}

    def test_language_cannot_reach_the_html_attributes(self):
        for language in ('fr" onload="x', "fr><script>", "../etc", "FR", "f"):
            with self.subTest(language=language):
                response = self.client.post("/api/books/volumes", params={"language": language}, json=self.book)
                self.assertEqual(response.status_code, 422)

    def test_toc_position_is_constrained(self):
        with self.assertRaises(ValidationError):
            Project(name="Livre", toc_position="middle")

    def test_error_responses_do_not_echo_markup_as_html(self):
        response = self.client.post("/api/books/volumes", params={"language": "<script>"}, json=self.book)
        self.assertEqual(response.headers["content-type"].split(";")[0], "application/json")


class FrontendLinksTest(unittest.TestCase):
    SOURCE = (Path(__file__).resolve().parent.parent / "app" / "static" / "app.js").read_text(encoding="utf-8")

    def test_data_urls_go_through_safe_url(self):
        for match in re.finditer(r'href="\$\{escapeHtml\(([^)]*)\)', self.SOURCE):
            with self.subTest(expression=match.group(1)):
                self.assertTrue(match.group(1).startswith(("safeUrl(", "openHref")), match.group(1))
        self.assertIn("const openHref = isDoc ? '#' : safeUrl(a.url);", self.SOURCE)
        self.assertIn("window.open(safeUrl(doc.url)", self.SOURCE)

    def test_safe_url_only_keeps_https(self):
        body = re.search(r"function safeUrl\(value\) \{\n\s*return (.*);\n\}", self.SOURCE.replace("\r\n", "\n")).group(1)
        self.assertEqual(body, "/^https:\\/\\//i.test(String(value || '')) ? String(value) : '#'")


if __name__ == "__main__":
    unittest.main()
