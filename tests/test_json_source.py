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
import json
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    import weasyprint  # noqa: F401
except Exception:
    fake = types.ModuleType("weasyprint")
    fake.HTML = lambda *a, **k: None
    sys.modules["weasyprint"] = fake

from fastapi import Response
from fastapi.testclient import TestClient

import app.main as main
from app import json_source
from app.json_source import JsonSourceError, fetch_project
from app.models import Project

BOOK = {"name": "Épaves", "book_title": "Épaves", "main_articles": [{"title": "Belem", "language": "fr", "url": "https://fr.wikipedia.org/wiki/Belem"}]}
WORKSPACE = {"format": "wikipedia2book-workspace", "version": 1, "projects": [BOOK]}
HOSTS = {"books.example.org": ["93.184.216.34"], "cdn.example.org": ["2606:2800:220:1::1"], "intranet.example.org": ["10.0.0.5"], "local.example.org": ["127.0.0.1"]}


def resolve(host):
    if host not in HOSTS:
        raise OSError("unknown host")
    return HOSTS[host]


def fetch(url, handler):
    return asyncio.run(fetch_project(url, transport=httpx.MockTransport(handler), resolve=resolve))


def serve(payload, status=200, headers=None):
    body = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
    return lambda request: httpx.Response(status, content=body, headers=headers or {})


class FetchProjectTest(unittest.TestCase):
    def test_workspace_list_and_bare_project_are_accepted(self):
        for payload in (WORKSPACE, [BOOK], BOOK):
            with self.subTest(payload=type(payload).__name__):
                project = fetch("https://books.example.org/livre.json", serve(payload))
                self.assertEqual(project.book_title, "Épaves")
                self.assertEqual(project.main_articles[0].title, "Belem")

    def test_only_https_and_public_hosts(self):
        for url in ("http://books.example.org/livre.json", "https://intranet.example.org/livre.json", "https://local.example.org/livre.json", "https://unknown.example.org/livre.json", "file:///etc/passwd"):
            with self.subTest(url=url), self.assertRaises(JsonSourceError) as caught:
                fetch(url, serve(WORKSPACE))
            self.assertEqual(caught.exception.status_code, 422)

    def test_redirects_are_followed_and_checked_again(self):
        def handler(request):
            if request.url.host == "books.example.org":
                return httpx.Response(302, headers={"location": "https://cdn.example.org/livre.json"})
            return httpx.Response(200, json=WORKSPACE)
        self.assertEqual(fetch("https://books.example.org/livre.json", handler).name, "Épaves")
        with self.assertRaises(JsonSourceError) as caught:
            fetch("https://books.example.org/livre.json", lambda request: httpx.Response(302, headers={"location": "https://intranet.example.org/x.json"}))
        self.assertEqual(caught.exception.status_code, 422)
        with self.assertRaises(JsonSourceError) as caught:
            fetch("https://books.example.org/a.json", lambda request: httpx.Response(302, headers={"location": "/b.json"}))
        self.assertEqual(caught.exception.status_code, 502)

    def test_errors_are_explicit(self):
        cases = [
            (serve(WORKSPACE, status=404), 502),
            (serve(b"not json"), 422),
            (serve({"format": "wikipedia2book-workspace", "version": 2, "projects": [BOOK]}), 422),
            (serve({"name": ""}), 422),
            (serve(WORKSPACE, headers={"content-length": str(json_source.MAX_JSON_BYTES + 1)}), 413),
        ]
        for handler, status in cases:
            with self.subTest(status=status), self.assertRaises(JsonSourceError) as caught:
                fetch("https://books.example.org/livre.json", handler)
            self.assertEqual(caught.exception.status_code, status)

    def test_body_larger_than_the_limit_is_refused(self):
        with patch.object(json_source, "MAX_JSON_BYTES", 100), self.assertRaises(JsonSourceError) as caught:
            fetch("https://books.example.org/livre.json", serve(WORKSPACE))
        self.assertEqual(caught.exception.status_code, 413)


class FromJsonEndpointTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(main.app)

    def test_generates_the_pdf_of_the_downloaded_book(self):
        project = Project.model_validate(BOOK)
        with patch.object(main, "fetch_project", AsyncMock(return_value=project)) as fetched, \
             patch.object(main, "_create_pdf_response", AsyncMock(return_value=Response(b"%PDF-1.7", media_type="application/pdf"))) as created:
            response = self.client.get("/api/pdf/from-json", params={"url": "https://books.example.org/livre.json", "language": "en"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"%PDF-1.7")
        fetched.assert_awaited_once_with("https://books.example.org/livre.json")
        created.assert_awaited_once_with(project, "en")

    def test_download_errors_keep_their_status(self):
        with patch.object(main, "fetch_project", AsyncMock(side_effect=JsonSourceError(422, "Hôte refusé."))):
            response = self.client.get("/api/pdf/from-json", params={"url": "https://intranet.example.org/x.json"})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["detail"], "Hôte refusé.")

    def test_url_is_required(self):
        self.assertEqual(self.client.get("/api/pdf/from-json").status_code, 422)


if __name__ == "__main__":
    unittest.main()
