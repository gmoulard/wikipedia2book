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
import contextlib
import io
import json
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

import httpx

import app.issue_report as issue_report
import app.main as main
from tests.test_generation_log import FailingClient, run_book
from tests.test_pdf_stream import FakeClient, _make_pdf

# NE PAS laisser l'assemblage dans un processus séparé ici : ces tests remplacent generate_pdf dans main, ce que le processus enfant ne verrait pas.
main.ISOLATE_ASSEMBLY = False

TOKEN = "github-token-for-tests"


def failure(request=b'{"format": "wikipedia2book-workspace"}', stages=1):
    generation = {"id": 7, "started": "2026-11-21T10:00:00+00:00", "version": "9.9.9", "language": "fr", "articles": 2, "documents": 0, "chapters": 0, "page_format": "A4", "orientation": "portrait", "status": "error", "duration_s": 1.5, "request_bytes": 40, "stages": [{"stage": "start", "at_s": 0.0}] * stages}
    return issue_report.GenerationFailure(generation, "MediaWikiError : PDF indisponible", "Traceback ...", request, {"version": {"commit": "abc"}})


class FakeGitHub:
    def __init__(self, status=201):
        self.status = status
        self.requests = []

    def handler(self, request):
        self.requests.append(request)
        if request.url.path.endswith("/comments"):
            return httpx.Response(201, json={"id": len(self.requests)})
        return httpx.Response(self.status, json={"number": 42, "html_url": "https://github.com/o/r/issues/42"})


class IssueReportTest(unittest.TestCase):
    def setUp(self):
        self.github = FakeGitHub()
        self.output = io.StringIO()
        self.patches = [patch.object(issue_report, "issue_transport", httpx.MockTransport(self.github.handler)), contextlib.redirect_stdout(self.output)]
        for item in self.patches:
            item.__enter__()

    def tearDown(self):
        for item in reversed(self.patches):
            item.__exit__(None, None, None)

    def reporter(self, per_day=20):
        return issue_report.IssueReporter(issue_report.IssueSettings(TOKEN, "o/r", per_day))

    def test_settings(self):
        settings = issue_report.issue_settings({})
        self.assertEqual((settings.token, settings.repository, settings.per_day), ("", "gmoulard/wikipedia2book", 20))
        settings = issue_report.issue_settings({"WIKIPEDIA2BOOK_GITHUB_TOKEN": " t ", "WIKIPEDIA2BOOK_ISSUE_REPOSITORY": "a/b", "WIKIPEDIA2BOOK_ISSUES_PER_DAY": "0"})
        self.assertEqual((settings.token, settings.repository, settings.per_day), ("t", "a/b", 0))
        for value in ("a", "a/b/c", "https://github.com/a/b"):
            with self.assertRaises(ValueError):
                issue_report.issue_settings({"WIKIPEDIA2BOOK_ISSUE_REPOSITORY": value})

    def test_issue_holds_request_journal_and_debug_with_label(self):
        item = failure()
        self.assertEqual(self.reporter().send(item), "https://github.com/o/r/issues/42")
        request = self.github.requests[0]
        self.assertEqual(request.url, "https://api.github.com/repos/o/r/issues")
        self.assertEqual(request.headers["authorization"], f"Bearer {TOKEN}")
        self.assertTrue(request.headers["user-agent"].startswith("Wikipedia2Book/"))
        payload = json.loads(request.content)
        self.assertEqual(payload["labels"], ["generationProbleme"])
        self.assertTrue(payload["title"].startswith("generationProbleme : génération 7"))
        for text in ("wikipedia2book-workspace", "Journal de la génération", '"stage": "start"', "Traceback ...", '"commit": "abc"', "PDF indisponible"):
            self.assertIn(text, payload["body"])
        self.assertNotIn(TOKEN, payload["body"])
        self.assertEqual(item.generation["issue"], "https://github.com/o/r/issues/42")
        self.assertEqual(len(self.github.requests), 1)

    def test_large_sections_go_to_comments_under_github_limits(self):
        big = json.dumps({"introduction": "x" * 200_000}).encode()
        body, comments = issue_report.issue_texts(failure(request=big))
        self.assertLess(len(body), 65_536)
        self.assertIn("commentaires", body)
        self.assertGreaterEqual(len(comments), 4)
        self.assertTrue(all(len(comment) < 65_536 for comment in comments))
        self.assertEqual("".join(c.split("\n", 3)[3].rsplit("\n", 1)[0] for c in comments if c.startswith("## Demande")), big.decode())
        self.reporter().send(failure(request=big))
        self.assertEqual([r.url.path for r in self.github.requests[1:]], ["/repos/o/r/issues/42/comments"] * len(comments))

    def test_comments_are_bounded(self):
        _, comments = issue_report.issue_texts(failure(request=b"y" * 5_000_000))
        self.assertEqual(len(comments), issue_report.MAX_COMMENTS)
        self.assertIn("pas été envoyés", comments[-1])

    def test_backticks_in_request_do_not_close_the_block(self):
        body, _ = issue_report.issue_texts(failure(request=b'{"introduction": "````"}'))
        self.assertIn("`````json", body)

    def test_missing_request_is_said(self):
        body, _ = issue_report.issue_texts(failure(request=None))
        self.assertIn("demande absente", body)

    def test_github_error_is_logged_without_token(self):
        self.github.status = 403
        item = failure()
        self.assertIsNone(self.reporter().send(item))
        self.assertEqual(item.generation["issue"], "failed")
        line = json.loads(self.output.getvalue().splitlines()[-1])
        self.assertEqual(line["status"], 403)
        self.assertNotIn(TOKEN, self.output.getvalue())

    def test_per_day_quota_and_disabled_without_token(self):
        reporter = self.reporter(per_day=1)
        with patch.object(reporter, "failures") as queued, patch.object(issue_report.threading, "Thread"):
            reporter.report(failure())
            second = failure()
            reporter.report(second)
        self.assertEqual(queued.put.call_count, 1)
        self.assertEqual(second.generation["issue"], "quota")
        disabled = issue_report.IssueReporter(issue_report.IssueSettings("", "o/r", 0))
        disabled.report(failure())
        self.assertIsNone(disabled.sender)


class AnonymizedIssueTest(unittest.TestCase):
    def request(self):
        project = {
            "name": "Livre de Jeanne", "book_title": "Mon livre", "book_subtitle": "", "book_author": "Jeanne Dupont 1975",
            "introduction": "Écrit par Jeanne pour Paul.", "conclusion": "Fin.", "description": "Notes",
            "chapters": [{"id": "c1", "title": "Souvenirs de Jeanne", "article_keys": ["fr:1"]}],
            "main_articles": [{"title": "Chat", "language": "fr", "url": "https://fr.wikipedia.org/wiki/Chat", "summary": "Le chat"}],
            "uploaded_documents": [{"id": "d", "title": "photo-jeanne.png", "kind": "image", "url": "https://perso.example.org/jeanne/photo-jeanne.png?cle=42"}],
            "cover_image": {"title": "Jeanne", "data_base64": None, "removed_base64_chars": 10},
        }
        return json.dumps({"format": "wikipedia2book-workspace", "version": 1, "projects": [project]}, ensure_ascii=False).encode()

    def test_user_texts_and_private_paths_are_masked_with_lengths_kept(self):
        item = failure(request=self.request())
        item.generation["stages"] = [{"stage": "download", "url": "https://perso.example.org/jeanne/photo-jeanne.png?cle=42"}, {"stage": "download", "url": "https://fr.wikipedia.org/api/rest_v1/page/pdf/Chat/a4"}]
        item.error = "RemoteFileError : Le document « photo-jeanne.png » n’a pas pu être intégré"
        item.traceback = "Traceback\nRemoteFileError: Le document « photo-jeanne.png »"
        public = issue_report.anonymized(item)
        body, comments = issue_report.issue_texts(public)
        text = body + "".join(comments) + issue_report.issue_title(public)
        for secret in ("Jeanne", "jeanne", "Paul", "Dupont", "1975", "Notes", "Souvenirs", "cle=42"):
            self.assertNotIn(secret, text)
        project = json.loads(public.request)["projects"][0]
        self.assertEqual(project["book_author"], "Xxxxxx Xxxxxx 0000")
        self.assertEqual(len(project["introduction"]), len("Écrit par Jeanne pour Paul."))
        self.assertEqual(project["main_articles"][0]["title"], "Chat")
        self.assertEqual(project["main_articles"][0]["url"], "https://fr.wikipedia.org/wiki/Chat")
        self.assertEqual(project["uploaded_documents"][0]["url"], "https://perso.example.org/xxxxxx/xxxxx-xxxxxx.png?xxx=00")
        self.assertEqual(public.generation["stages"][1]["url"], "https://fr.wikipedia.org/api/rest_v1/page/pdf/Chat/a4")
        self.assertIn("xxxxx-xxxxxx.png", public.error)
        self.assertIn("jeanne", item.generation["stages"][0]["url"])

    def test_sent_issue_is_anonymized(self):
        github = FakeGitHub()
        with patch.object(issue_report, "issue_transport", httpx.MockTransport(github.handler)), contextlib.redirect_stdout(io.StringIO()):
            item = failure(request=self.request())
            item.error = "Erreur sur photo-jeanne.png"
            issue_report.IssueReporter(issue_report.IssueSettings(TOKEN, "o/r", 0)).send(item)
        payload = github.requests[0].content.decode()
        self.assertNotIn("jeanne", payload.lower())
        self.assertIn("anonymis", json.loads(payload)["body"])
        self.assertEqual(item.generation["issue"], "https://github.com/o/r/issues/42")

    def test_unreadable_request_is_not_sent(self):
        public = issue_report.anonymized(failure(request=b"pas du json Jeanne"))
        self.assertNotIn(b"Jeanne", public.request)


class GenerationIssueTest(unittest.TestCase):
    def setUp(self):
        main.generation_log.clear()
        self.reported = []
        self.patches = [
            patch.object(main, "generate_pdf", lambda html: _make_pdf(1)),
            patch.object(main, "ISSUES", types.SimpleNamespace(enabled=True, report=self.reported.append)),
            contextlib.redirect_stdout(io.StringIO()),
        ]
        for item in self.patches:
            item.__enter__()

    def tearDown(self):
        for item in reversed(self.patches):
            item.__exit__(None, None, None)

    def test_failed_generation_reports_request_journal_and_debug(self):
        with patch.object(main, "MediaWikiClient", FailingClient):
            with self.assertRaises(main.MediaWikiError):
                asyncio.run(run_book())
        self.assertEqual(len(self.reported), 1)
        item = self.reported[0]
        self.assertEqual(item.generation["status"], "error")
        self.assertIn("PDF indisponible", item.error)
        self.assertIn("MediaWikiError", item.traceback)
        workspace = json.loads(item.request)
        self.assertEqual([a["title"] for a in workspace["projects"][0]["main_articles"]], ["Chat", "Chien"])
        for key in ("version", "system", "memory", "memory_gate", "settings"):
            self.assertIn(key, item.debug)

    def test_successful_or_abandoned_generation_reports_nothing(self):
        with patch.object(main, "MediaWikiClient", FakeClient):
            asyncio.run(run_book())
            asyncio.run(run_book(stop_at="assemble"))
        self.assertEqual(self.reported, [])

    def test_disabled_reporter_is_not_called(self):
        with patch.object(main, "ISSUES", types.SimpleNamespace(enabled=False, report=self.reported.append)), patch.object(main, "MediaWikiClient", FailingClient):
            with self.assertRaises(main.MediaWikiError):
                asyncio.run(run_book())
        self.assertEqual(self.reported, [])


if __name__ == "__main__":
    unittest.main()
