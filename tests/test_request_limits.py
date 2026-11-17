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
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    import weasyprint  # noqa: F401
except Exception:
    fake = types.ModuleType("weasyprint")
    fake.HTML = lambda *a, **k: None
    sys.modules["weasyprint"] = fake

from fastapi.testclient import TestClient

import app.main as main
from app import request_limits, wikipedia_api
from app.request_limits import Alerts, GenerationLimits, LimitRefused, RequestGuard, client_keys, count_setting

TOKEN = "0123456789abcdef"


class Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


class GenerationLimitsTest(unittest.TestCase):
    def test_client_concurrent_limit_and_release(self):
        limits = GenerationLimits(2, 0, 0, 0, clock=Clock())
        first, second = limits.admit(["token:a"]), limits.admit(["token:a"])
        with self.assertRaises(LimitRefused) as caught:
            limits.admit(["token:a"])
        self.assertEqual((caught.exception.reason, caught.exception.limit), ("client_concurrent", 2))
        limits.admit(["token:b"]).release()
        first.release()
        first.release()
        limits.admit(["token:a"])
        second.release()
        self.assertEqual(limits.state()["generations"], 1)

    def test_client_per_minute_limit_gives_the_wait(self):
        clock = Clock()
        limits = GenerationLimits(0, 3, 0, 0, clock=clock)
        for _ in range(3):
            limits.admit(["ip:a"]).release()
            clock.now += 10
        with self.assertRaises(LimitRefused) as caught:
            limits.admit(["ip:a"])
        self.assertEqual((caught.exception.reason, caught.exception.retry_after), ("client_per_minute", 30))
        clock.now += 30
        limits.admit(["ip:a"]).release()
        self.assertEqual(sorted(limits.starts), ["ip:a", "total"])

    def test_total_limits_apply_to_every_request(self):
        clock = Clock()
        limits = GenerationLimits(0, 0, 2, 3, clock=clock)
        held = [limits.admit([]), limits.admit(["token:x"])]
        with self.assertRaises(LimitRefused) as caught:
            limits.admit(["token:y"])
        self.assertEqual(caught.exception.reason, "total_concurrent")
        held.pop().release()
        limits.admit([]).release()
        with self.assertRaises(LimitRefused) as caught:
            limits.admit([])
        self.assertEqual(caught.exception.reason, "total_per_minute")
        self.assertIn("3 par minute", str(caught.exception))

    def test_a_refused_request_reserves_nothing(self):
        limits = GenerationLimits(1, 0, 0, 0, clock=Clock())
        limits.admit(["ip:a"])
        with self.assertRaises(LimitRefused):
            limits.admit(["token:b", "ip:a"])
        self.assertNotIn("token:b", limits.active)
        self.assertEqual(limits.active["total"], 1)

    def test_count_setting(self):
        self.assertEqual(count_setting({}, "X", 5), 5)
        self.assertEqual(count_setting({"X": "0"}, "X", 5), 0)
        with self.assertRaises(ValueError):
            count_setting({"X": "-1"}, "X", 5)


class ClientKeysTest(unittest.TestCase):
    def test_public_address_and_token_are_hashed(self):
        keys = client_keys("93.184.216.34", {"x-wikipedia2book-client": TOKEN}, "")
        self.assertEqual([key.split(":")[0] for key in keys], ["ip", "token"])
        self.assertFalse(any("93.184" in key or TOKEN in key for key in keys))
        self.assertEqual(keys, client_keys("93.184.216.34", {"x-wikipedia2book-client": TOKEN}, ""))

    def test_private_or_missing_address_and_bad_token_are_ignored(self):
        for peer in ("172.16.3.4", "10.0.0.1", "127.0.0.1", "testclient", None):
            with self.subTest(peer=peer):
                self.assertEqual(client_keys(peer, {"x-wikipedia2book-client": "court"}, ""), [])

    def test_forwarded_header_uses_the_address_added_by_the_proxy(self):
        headers = {"x-forwarded-for": "1.2.3.4, 93.184.216.34"}
        self.assertEqual(client_keys("10.0.0.1", headers, "x-forwarded-for"), client_keys("93.184.216.34", {}, ""))
        self.assertEqual(client_keys("93.184.216.34", {}, "x-forwarded-for"), [])


class AlertsTest(unittest.TestCase):
    def test_counts_log_line_and_one_email_per_hour(self):
        clock = Clock()
        sent = []
        alerts = Alerts("outil.maintainers@toolforge.org", "smtp.example.org", "outil.alerts@toolforge.org", clock=clock, mailer=lambda message, host: sent.append((message, host)))
        output = io.StringIO()
        with contextlib.redirect_stdout(output), patch.object(request_limits.threading, "Thread", lambda target, args, daemon: types.SimpleNamespace(start=lambda: target(*args))):
            alerts.raise_alert("queue_full", path="/api/pdf/stream", limit=100)
            clock.now += 60
            alerts.raise_alert("queue_full", path="/api/pdf/stream", limit=100)
            clock.now += request_limits.ALERT_EMAIL_EVERY_S
            alerts.raise_alert("queue_full", path="/api/pdf/stream", limit=100)
        self.assertEqual(alerts.state()["queue_full"]["count"], 3)
        self.assertEqual(output.getvalue().count('"alert": "queue_full"'), 3)
        self.assertEqual(len(sent), 2)
        message, host = sent[0]
        self.assertEqual((message["To"], message["From"], host), ("outil.maintainers@toolforge.org", "outil.alerts@toolforge.org", "smtp.example.org"))
        self.assertIn("queue_full", message["Subject"])

    def test_failed_email_is_logged_not_raised(self):
        def broken(message, host):
            raise OSError("relais injoignable")

        alerts = Alerts("a@example.org", "smtp.example.org", mailer=broken)
        output = io.StringIO()
        with contextlib.redirect_stdout(output), patch.object(request_limits.threading, "Thread", lambda target, args, daemon: types.SimpleNamespace(start=lambda: target(*args))):
            alerts.raise_alert("send_timeout")
        self.assertIn("alert_email_failed", output.getvalue())

    def test_no_email_without_settings(self):
        sent = []
        with contextlib.redirect_stdout(io.StringIO()):
            Alerts(mailer=lambda message, host: sent.append(message)).raise_alert("request_too_large")
        self.assertEqual(sent, [])


class EndpointLimitsTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(main.app)
        self.alerts = Alerts()
        self.saved = (main.GENERATION_LIMITS, main.ALERTS, main.WAITING_GENERATIONS)
        main.ALERTS = self.alerts
        self.output = contextlib.redirect_stdout(io.StringIO())
        self.output.__enter__()

    def tearDown(self):
        self.output.__exit__(None, None, None)
        main.GENERATION_LIMITS, main.ALERTS, main.WAITING_GENERATIONS = self.saved

    def test_body_larger_than_the_limit_is_refused_before_reading(self):
        with patch.object(request_limits, "MAX_BODY_BYTES", 100):
            response = self.client.post("/api/pdf/stream", content=b"x" * 101, headers={"content-type": "application/json"})
            small = self.client.post("/api/sources/resolve", json={"text": ""})
        self.assertEqual(response.status_code, 413)
        self.assertEqual(response.json()["detail"]["code"], "request_too_large")
        self.assertNotEqual(small.status_code, 413)
        self.assertEqual(self.alerts.state()["request_too_large"]["count"], 1)

    def test_client_over_its_limit_gets_429_with_retry_after(self):
        main.GENERATION_LIMITS = GenerationLimits(1, 0, 0, 0)
        held = main.GENERATION_LIMITS.admit(client_keys(None, {"x-wikipedia2book-client": TOKEN}, ""))
        response = self.client.post("/api/pdf/stream", json={"name": "Livre"}, headers={"X-Wikipedia2Book-Client": TOKEN})
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.headers["retry-after"], str(request_limits.CONCURRENT_RETRY_S))
        detail = response.json()["detail"]
        self.assertEqual((detail["code"], detail["reason"], detail["limit"]), ("too_many_requests", "client_concurrent", 1))
        other = self.client.post("/api/pdf/stream", json={"name": "Livre"}, headers={"X-Wikipedia2Book-Client": "fedcba9876543210"})
        self.assertNotEqual(other.status_code, 429)
        held.release()
        self.assertEqual(main.GENERATION_LIMITS.state()["generations"], 0)
        self.assertEqual(self.alerts.state()["client_concurrent"]["count"], 1)

    def test_full_queue_gets_429(self):
        main.WAITING_GENERATIONS = 1
        main.GENERATION_GATE.queue.append(object())
        try:
            response = self.client.get("/api/pdf/from-json", params={"url": "https://example.org/livre.json"})
        finally:
            main.GENERATION_GATE.queue.pop()
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.json()["detail"]["reason"], "queue_full")

    def test_other_endpoints_are_not_limited(self):
        main.GENERATION_LIMITS = GenerationLimits(0, 0, 1, 0)
        main.GENERATION_LIMITS.admit([])
        self.assertEqual(self.client.get("/api/version").status_code, 200)

    def test_health_details_exposes_limits_and_alerts(self):
        self.alerts.raise_alert("queue_full")
        details = self.client.get("/api/health/details").json()
        self.assertEqual(details["request_limits"]["waiting_limit"], main.WAITING_GENERATIONS)
        self.assertEqual(details["alerts"]["queue_full"]["count"], 1)


class SendTimeoutTest(unittest.TestCase):
    def test_stalled_client_is_cut_and_its_slot_released(self):
        limits = GenerationLimits(0, 0, 0, 0)
        alerts = Alerts()

        async def app(scope, receive, send):
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b"x", "more_body": True})

        async def stalled_send(message):
            if message["type"] == "http.response.body":
                await asyncio.Event().wait()

        async def receive():
            return {"type": "http.request", "body": b"", "more_body": False}

        guard = RequestGuard(app, lambda: limits, lambda: 0, lambda: 0, lambda: alerts, lambda: "", send_timeout=lambda: 0.05)
        scope = {"type": "http", "method": "POST", "path": "/api/pdf/stream", "headers": [], "client": ("93.184.216.34", 1)}
        with contextlib.redirect_stdout(io.StringIO()):
            asyncio.run(asyncio.wait_for(guard(scope, receive, stalled_send), 5))
        self.assertEqual(alerts.state()["send_timeout"]["count"], 1)
        self.assertEqual(limits.state()["generations"], 0)

    def test_stalled_stream_generator_is_closed_at_once(self):
        closed = []

        async def chunks():
            try:
                while True:
                    yield b"x"
            finally:
                closed.append(True)

        async def stalled_send(message):
            if message["type"] == "http.response.body":
                await asyncio.Event().wait()

        async def receive():
            await asyncio.Event().wait()

        response = request_limits.ClosingStreamingResponse(chunks())
        guard = RequestGuard(response, lambda: GenerationLimits(0, 0, 0, 0), lambda: 0, lambda: 0, lambda: Alerts(), lambda: "", send_timeout=lambda: 0.05)
        scope = {"type": "http", "method": "POST", "path": "/api/pdf/stream", "headers": [], "client": None, "asgi": {"spec_version": "2.4"}}
        with contextlib.redirect_stdout(io.StringIO()):
            asyncio.run(asyncio.wait_for(guard(scope, receive, stalled_send), 5))
        self.assertEqual(closed, [True])

    def test_chunked_body_over_the_limit_is_refused(self):
        alerts = Alerts()
        statuses = []

        async def app(scope, receive, send):
            await receive()
            await receive()

        chunks = iter([{"type": "http.request", "body": b"x" * 60, "more_body": True}, {"type": "http.request", "body": b"x" * 60, "more_body": False}])

        async def receive():
            return next(chunks)

        async def send(message):
            statuses.append(message)

        guard = RequestGuard(app, lambda: GenerationLimits(0, 0, 0, 0), lambda: 0, lambda: 0, lambda: alerts, lambda: "", max_body=lambda: 100)
        scope = {"type": "http", "method": "POST", "path": "/api/sources/resolve", "headers": [], "client": None}
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(request_limits.RequestTooLarge):
            asyncio.run(guard(scope, receive, send))
        self.assertEqual(alerts.state()["request_too_large"]["count"], 1)


class ApiLimiterTest(unittest.IsolatedAsyncioTestCase):
    async def test_requests_are_spaced_and_long_waits_alerted(self):
        now = [0.0]
        sleeps, alerts = [], []

        async def fake_sleep(delay, *args, **kwargs):
            sleeps.append(round(delay, 2))

        limiter = wikipedia_api.ApiLimiter()
        with patch.object(wikipedia_api, "_clock", lambda: now[0]), patch.object(wikipedia_api.asyncio, "sleep", fake_sleep), patch.object(wikipedia_api, "on_api_throttle", alerts.append):
            for _ in range(3):
                await limiter.wait()
            self.assertEqual(sleeps, [0.1, 0.2])
            limiter.next_at = now[0] + wikipedia_api.API_ALERT_WAIT_S + 1
            await limiter.wait()
        self.assertEqual(alerts, [wikipedia_api.API_ALERT_WAIT_S + 1])


if __name__ == "__main__":
    unittest.main()
