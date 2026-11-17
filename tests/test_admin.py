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

import contextlib
import io
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    import weasyprint  # noqa: F401
except Exception:
    fake = types.ModuleType("weasyprint")
    fake.HTML = lambda *a, **k: None
    sys.modules["weasyprint"] = fake

from fastapi.testclient import TestClient

import app.main as main
from app import admin
from app.admin import AdminSettings, admin_settings, decode_admins, monitor_token_setting, normalize_username
from app.request_limits import GenerationLimits

CALLBACK = "http://testserver/admin/callback"


def wikimedia(username, token_status=200):
    calls = []

    def handler(request):
        calls.append(request)
        if request.url.path.endswith("/access_token"):
            return httpx.Response(token_status, json={"access_token": "jeton"})
        return httpx.Response(200, json={"username": username, "sub": 1})

    return httpx.MockTransport(handler), calls


class AdminSettingsTest(unittest.TestCase):
    def test_default_admins_are_written_in_hexadecimal(self):
        self.assertEqual(admin_settings({}).admins, frozenset({"GMoulard", "CapitaineCanette"}))
        self.assertNotIn("GMoulard", Path(admin.__file__).read_text(encoding="utf-8"))

    def test_admins_variable_replaces_the_default(self):
        settings = admin_settings({"WIKIPEDIA2BOOK_ADMINS": "4578656d706c65,  ", "WIKIPEDIA2BOOK_OAUTH_CLIENT_ID": "id"})
        self.assertEqual(settings.admins, frozenset({"Exemple"}))
        self.assertFalse(settings.configured)

    def test_invalid_hexadecimal_prevents_startup(self):
        with self.assertRaises(ValueError):
            decode_admins("GMoulard")

    def test_usernames_are_normalized_like_mediawiki(self):
        self.assertEqual(normalize_username("capitaine_Canette "), "Capitaine Canette")


class SignedCookieTest(unittest.TestCase):
    def test_session_is_signed_and_expires(self):
        cookie = admin.session_cookie("GMoulard")
        self.assertEqual(admin._unsign(cookie)["user"], "GMoulard")
        body, signature = cookie.rsplit(".", 1)
        self.assertIsNone(admin._unsign(body + "." + "0" * len(signature)))
        with patch.object(admin.time, "time", return_value=admin.time.time() + admin.SESSION_S + 1):
            self.assertIsNone(admin._unsign(cookie))

    def test_state_must_match(self):
        cookie = admin.state_cookie("abc")
        self.assertTrue(admin.state_matches(cookie, "abc"))
        self.assertFalse(admin.state_matches(cookie, "abd"))
        self.assertFalse(admin.state_matches(None, "abc"))


class AdminEndpointsTest(unittest.TestCase):
    def setUp(self):
        self.saved = main.ADMIN
        main.ADMIN = AdminSettings(frozenset({"GMoulard"}), "client", "secret", CALLBACK)
        self.client = TestClient(main.app, follow_redirects=False)
        self.output = contextlib.redirect_stdout(io.StringIO())
        self.output.__enter__()

    def tearDown(self):
        self.output.__exit__(None, None, None)
        main.ADMIN = self.saved
        admin.oauth_transport = None
        main.ADMIN_LOGIN_LIMITS = GenerationLimits(0, 10, 0, 30)

    def login(self, username):
        response = self.client.get("/admin/login")
        state = parse_qs(urlsplit(response.headers["location"]).query)["state"][0]
        admin.oauth_transport, calls = wikimedia(username)
        return self.client.get("/admin/callback", params={"code": "c0de", "state": state}), calls

    def test_page_and_session_without_login(self):
        self.assertIn("adminBoard", self.client.get("/admin").text)
        self.assertEqual(self.client.get("/admin/api/session").json(), {"configured": True, "user": None})
        response = self.client.get("/admin/api/summary")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"]["code"], "admin_login_required")

    def test_login_redirects_to_wikimedia_with_a_state(self):
        response = self.client.get("/admin/login")
        self.assertEqual(response.status_code, 302)
        target = urlsplit(response.headers["location"])
        self.assertEqual((target.netloc, target.path), ("meta.wikimedia.org", "/w/rest.php/oauth2/authorize"))
        query = parse_qs(target.query)
        self.assertEqual((query["client_id"], query["redirect_uri"], query["response_type"]), (["client"], [CALLBACK], ["code"]))
        self.assertIn(admin.STATE_COOKIE, response.headers["set-cookie"])

    def test_admin_login_opens_the_summary(self):
        response, calls = self.login("GMoulard")
        self.assertEqual((response.status_code, response.headers["location"]), (302, "/admin"))
        self.assertEqual(calls[0].url.path, "/w/rest.php/oauth2/access_token")
        self.assertIn(b"client_secret=secret", calls[0].content)
        self.assertEqual(calls[1].headers["authorization"], "Bearer jeton")
        self.assertEqual(self.client.get("/admin/api/session").json()["user"], "GMoulard")
        summary = self.client.get("/admin/api/summary")
        self.assertEqual(summary.status_code, 200)
        self.assertEqual(summary.headers["cache-control"], "no-store")
        self.assertEqual(set(summary.json()), {"user", "version", "server", "system", "settings", "usage", "performance", "recent", "refused_urls"})
        self.client.get("/admin/logout")
        self.assertIsNone(self.client.get("/admin/api/session").json()["user"])

    def test_other_accounts_are_refused(self):
        response, _ = self.login("Quelqu'un")
        self.assertEqual(response.headers["location"], "/admin?error=forbidden")
        self.assertNotIn(admin.SESSION_COOKIE, response.headers.get("set-cookie", ""))
        self.assertEqual(self.client.get("/admin/api/summary").status_code, 401)

    def test_admin_removed_from_the_list_loses_access(self):
        self.login("GMoulard")
        main.ADMIN = AdminSettings(frozenset({"CapitaineCanette"}), "client", "secret", CALLBACK)
        self.assertEqual(self.client.get("/admin/api/summary").status_code, 401)

    def test_wrong_state_and_refused_code(self):
        self.client.get("/admin/login")
        self.assertEqual(self.client.get("/admin/callback", params={"code": "c", "state": "autre"}).headers["location"], "/admin?error=state")
        self.assertEqual(self.client.get("/admin/callback", params={"error": "access_denied"}).headers["location"], "/admin?error=denied")
        response = self.client.get("/admin/login")
        state = parse_qs(urlsplit(response.headers["location"]).query)["state"][0]
        admin.oauth_transport, _ = wikimedia("GMoulard", token_status=400)
        self.assertEqual(self.client.get("/admin/callback", params={"code": "c", "state": state}).headers["location"], "/admin?error=oauth")

    def test_session_cookie_is_limited_to_admin_paths(self):
        response, _ = self.login("GMoulard")
        cookie = [value for name, value in response.headers.multi_items() if name == "set-cookie" and value.startswith(admin.SESSION_COOKIE)][0]
        self.assertIn("Path=/admin", cookie)
        self.assertIn("HttpOnly", cookie)
        self.assertIn(f"Max-Age={2 * 3600}", cookie)

    def test_admin_generation_journal_and_security_headers(self):
        self.login("GMoulard")
        with patch.object(main, "generation_log", [{"id": 9, "status": "done", "stages": []}]):
            found = self.client.get("/admin/api/generations/9")
            missing = self.client.get("/admin/api/generations/8")
        self.assertEqual(found.json()["generation"]["id"], 9)
        self.assertEqual(missing.status_code, 404)
        page = self.client.get("/admin")
        self.assertIn("frame-ancestors 'none'", page.headers["content-security-policy"])
        self.assertEqual((page.headers["x-frame-options"], page.headers["x-content-type-options"], page.headers["referrer-policy"]), ("DENY", "nosniff", "no-referrer"))
        self.assertNotIn("content-security-policy", self.client.get("/api/version").headers)

    def test_generation_page_and_system_information(self):
        page = self.client.get("/admin/generation", params={"id": 3})
        self.assertIn('data-admin-page="generation"', page.text)
        self.assertIn("frame-ancestors 'none'", page.headers["content-security-policy"])
        self.login("GMoulard")
        system = self.client.get("/admin/api/summary").json()["system"]
        for key in ("host", "python", "cpu_count", "uptime_s", "threads", "oom_kills", "libraries"):
            self.assertIn(key, system)
        self.assertIn("weasyprint", system["libraries"])

    def test_admin_generation_journal_needs_the_session(self):
        self.assertEqual(self.client.get("/admin/api/generations/1").status_code, 401)

    def test_sign_in_attempts_are_limited(self):
        main.ADMIN_LOGIN_LIMITS = GenerationLimits(0, 0, 0, 2)
        statuses = [self.client.get("/admin/login").headers["location"].startswith("https://meta.wikimedia.org") for _ in range(2)]
        self.assertEqual(statuses, [True, True])
        self.assertEqual(self.client.get("/admin/login").headers["location"], "/admin?error=too_many")
        self.assertEqual(self.client.get("/admin/callback", params={"code": "c", "state": "s"}).headers["location"], "/admin?error=too_many")

    def test_not_configured(self):
        main.ADMIN = AdminSettings(frozenset({"GMoulard"}), "", "", "")
        self.assertEqual(self.client.get("/admin/login").headers["location"], "/admin?error=not_configured")
        self.assertFalse(self.client.get("/admin/api/session").json()["configured"])


class GenerationJournalEntryTest(unittest.TestCase):
    def test_one_generation_with_the_monitor_token(self):
        client = TestClient(main.app)
        journal = [{"id": 41, "status": "done", "stages": []}, {"id": 42, "status": "error", "stages": [{"stage": "start"}]}]
        hits_before = sum(main.hourly_hits.values())
        headers = {"Authorization": "Bearer " + "j" * 32}
        with patch.object(main, "generation_log", journal), patch.object(main, "MONITOR_TOKEN", "j" * 32):
            found = client.get("/api/health/generations/42", headers=headers)
            missing = client.get("/api/health/generations/7", headers=headers)
        self.assertEqual(found.json()["generation"], journal[1])
        self.assertEqual(missing.status_code, 404)
        self.assertEqual(sum(main.hourly_hits.values()), hits_before)


class MonitorTokenTest(unittest.TestCase):
    def test_health_endpoints_need_the_token(self):
        client = TestClient(main.app)
        for path in ("/api/health/details", "/api/health/generations", "/api/health/generations/1"):
            with self.subTest(path=path):
                with patch.object(main, "MONITOR_TOKEN", ""):
                    self.assertEqual(client.get(path, headers={"Authorization": "Bearer "}).status_code, 401)
                with patch.object(main, "MONITOR_TOKEN", "k" * 32):
                    refused = client.get(path)
                    wrong = client.get(path, headers={"Authorization": "Bearer " + "x" * 32})
                    basic = client.get(path, headers={"Authorization": "Basic " + "k" * 32})
                self.assertEqual((refused.status_code, wrong.status_code, basic.status_code), (401, 401, 401))
                self.assertEqual(refused.headers["www-authenticate"], "Bearer")
                self.assertEqual(refused.json()["detail"]["code"], "monitor_token_required")

    def test_short_token_prevents_startup(self):
        self.assertEqual(monitor_token_setting({}), "")
        with self.assertRaises(ValueError):
            monitor_token_setting({"WIKIPEDIA2BOOK_MONITOR_TOKEN": "court"})

    def test_admin_and_health_are_hidden_from_the_api_description(self):
        paths = TestClient(main.app).get("/openapi.json").json()["paths"]
        self.assertFalse([path for path in paths if path.startswith(("/admin", "/api/health"))])
        self.assertIn("/api/pdf/stream", paths)


class SummaryPayloadTest(unittest.TestCase):
    def test_statistics_of_the_generation_journal(self):
        def generation(number, status, duration, articles, size, peak, waited=0):
            stages = [{"stage": "start", "peak_rss_bytes": peak}]
            if waited:
                stages.append({"stage": "memory_wait", "waited_s": waited, "peak_rss_bytes": None})
            return {"id": number, "started": "2026-11-17T08:00:00+00:00", "version": "1.12.0", "status": status, "duration_s": duration, "articles": articles, "documents": 0, "page_format": "A4", "size_bytes": size, "stages": stages}

        journal = [generation(1, "done", 10.0, 10, 1000, 300), generation(2, "done", 30.0, 10, 3000, 500, waited=4.0), generation(3, "error", 5.0, 2, None, 100)]
        with patch.object(main, "generation_log", journal), patch.object(main, "hourly_hits", {"2000-01-01T00": 7}):
            data = main.admin_summary_payload("GMoulard")
        perf = data["performance"]
        self.assertEqual((perf["generations"], perf["median_s"], perf["max_s"], perf["median_s_per_article"]), (2, 10.0, 30.0, 1.0))
        self.assertEqual((perf["median_size_bytes"], perf["max_peak_rss_bytes"], perf["waited_s"]), (1000, 500, 4.0))
        self.assertEqual(data["usage"]["generations"], {"done": 2, "error": 1})
        self.assertEqual((data["usage"]["hits_24h"], data["usage"]["hits_48h"]), (0, 7))
        self.assertEqual([row["id"] for row in data["recent"]], [3, 2, 1])


if __name__ == "__main__":
    unittest.main()
