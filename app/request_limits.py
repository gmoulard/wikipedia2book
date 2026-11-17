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
import hashlib
import ipaddress
import json
import math
import re
import secrets
import time
from collections import deque
from collections.abc import Callable, Mapping
from datetime import datetime, timezone

from fastapi import HTTPException
from fastapi.responses import StreamingResponse

MEGABYTE = 1_000_000
MAX_BODY_BYTES = 60 * MEGABYTE
SEND_TIMEOUT_S = 20
WINDOW_S = 60
CONCURRENT_RETRY_S = 10
QUEUE_RETRY_S = 30
CLIENT_HEADER = "x-wikipedia2book-client"
CLIENT_TOKEN = re.compile(r"^[A-Za-z0-9-]{8,64}$")
GENERATION_PATHS = {
    ("POST", "/api/pdf"),
    ("POST", "/api/pdf/stream"),
    ("GET", "/api/pdf/from-source"),
    ("GET", "/api/pdf/from-json"),
    ("POST", "/api/pdf/from-json"),
    ("POST", "/api/pdf/from-wikitext"),
    ("POST", "/api/books/generate"),
    ("GET", "/api/books/generate-from-wikipedia-book"),
    ("POST", "/api/books/generate-from-wikipedia-book"),
}
REFUSALS = {
    "client_concurrent": "Trop de générations en cours pour ce client ({limit} au plus) : réessayez dans {retry} s.",
    "client_per_minute": "Trop de générations demandées par ce client ({limit} par minute au plus) : réessayez dans {retry} s.",
    "total_concurrent": "Trop de générations en cours sur le serveur ({limit} au plus) : réessayez dans {retry} s.",
    "total_per_minute": "Trop de générations demandées au serveur ({limit} par minute au plus) : réessayez dans {retry} s.",
    "queue_full": "Trop de générations en attente sur le serveur ({limit} au plus) : réessayez dans {retry} s.",
}


def count_setting(environ: Mapping[str, str], name: str, default: int) -> int:
    text = environ.get(name, "").strip()
    if not text:
        return default
    if not text.isdigit():
        raise ValueError(f"{name} doit être un entier positif, ou 0 pour ne pas limiter (reçu : {text!r}).")
    return int(text)


class LimitRefused(Exception):
    def __init__(self, reason: str, limit: int, retry_after: int) -> None:
        super().__init__(REFUSALS[reason].format(limit=limit, retry=retry_after))
        self.reason = reason
        self.limit = limit
        self.retry_after = retry_after


class RequestTooLarge(HTTPException):
    def __init__(self, limit: int) -> None:
        super().__init__(status_code=413, detail=request_too_large_detail(limit))


class SendStalled(Exception):
    pass


class ClosingStreamingResponse(StreamingResponse):
    # NE PAS revenir à StreamingResponse : après un envoi coupé, son générateur reste suspendu jusqu'au ramasse-miettes, avec le dossier temporaire et les réserves de mémoire de la génération.
    async def stream_response(self, send) -> None:
        async with contextlib.aclosing(self.body_iterator):
            await super().stream_response(send)


def request_too_large_detail(limit: int) -> dict:
    return {
        "code": "request_too_large",
        "limit": limit,
        "message": f"La requête dépasse {limit // MEGABYTE} Mo : retirez des documents importés ou découpez le livre en volumes.",
    }


class Admission:
    def __init__(self, limits: "GenerationLimits", keys: list[str]) -> None:
        self.limits = limits
        self.keys = keys
        self.released = False

    def release(self) -> None:
        if self.released:
            return
        self.released = True
        for key in self.keys:
            self.limits.active[key] -= 1
            if not self.limits.active[key]:
                del self.limits.active[key]


class GenerationLimits:
    def __init__(self, client_concurrent: int, client_per_minute: int, total_concurrent: int, total_per_minute: int, clock: Callable[[], float] = time.monotonic) -> None:
        self.rules = {"client": (client_concurrent, client_per_minute), "total": (total_concurrent, total_per_minute)}
        self.clock = clock
        self.active: dict[str, int] = {}
        self.starts: dict[str, deque[float]] = {}

    def _refusal(self, key: str, now: float) -> LimitRefused | None:
        prefix = "total" if key == "total" else "client"
        concurrent, per_minute = self.rules[prefix]
        if concurrent and self.active.get(key, 0) >= concurrent:
            return LimitRefused(f"{prefix}_concurrent", concurrent, CONCURRENT_RETRY_S)
        starts = self.starts.get(key)
        if per_minute and starts and len(starts) >= per_minute:
            return LimitRefused(f"{prefix}_per_minute", per_minute, max(1, math.ceil(starts[0] + WINDOW_S - now)))
        return None

    def admit(self, client_keys: list[str]) -> Admission:
        now = self.clock()
        for starts in self.starts.values():
            while starts and starts[0] <= now - WINDOW_S:
                starts.popleft()
        for key in [key for key, starts in self.starts.items() if not starts]:
            del self.starts[key]
        keys = [*client_keys, "total"]
        for key in keys:
            refusal = self._refusal(key, now)
            if refusal is not None:
                raise refusal
        for key in keys:
            self.active[key] = self.active.get(key, 0) + 1
            self.starts.setdefault(key, deque()).append(now)
        return Admission(self, keys)

    def state(self) -> dict:
        client_concurrent, client_per_minute = self.rules["client"]
        total_concurrent, total_per_minute = self.rules["total"]
        return {
            "client_concurrent": client_concurrent,
            "client_per_minute": client_per_minute,
            "total_concurrent": total_concurrent,
            "total_per_minute": total_per_minute,
            "clients": sum(key != "total" for key in self.active),
            "generations": self.active.get("total", 0),
        }


_SALT = secrets.token_bytes(16)


def _hashed(kind: str, value: str) -> str:
    # NE PAS garder ni journaliser l'adresse IP ou le jeton en clair : seule une empreinte salée, propre à ce processus, sert de clé, et disparaît une minute après la dernière génération du client.
    return f"{kind}:{hashlib.sha256(_SALT + value.encode()).hexdigest()[:16]}"


def client_keys(peer: str | None, headers: Mapping[str, str], ip_header: str) -> list[str]:
    keys = []
    address = peer
    if ip_header:
        forwarded = headers.get(ip_header, "")
        address = forwarded.split(",")[-1].strip() if forwarded else None
    try:
        ip = ipaddress.ip_address((address or "").split("%")[0])
    except ValueError:
        ip = None
    # NE PAS limiter par une adresse privée : derrière un proxy qui masque les visiteurs (Toolforge), tous arriveraient avec la même adresse et seraient bloqués ensemble.
    if ip is not None and ip.is_global:
        keys.append(_hashed("ip", ip.compressed))
    token = headers.get(CLIENT_HEADER, "")
    if CLIENT_TOKEN.match(token):
        keys.append(_hashed("token", token))
    return keys


class Alerts:
    def __init__(self) -> None:
        self.counts: dict[str, dict] = {}

    def raise_alert(self, kind: str, **details) -> None:
        # NE PAS y mettre d'adresse IP, de jeton ni de titre : les alertes sont publiques (GET /api/health/details) et recopiées dans les journaux de la plateforme.
        at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        entry = self.counts.setdefault(kind, {"count": 0, "last": None})
        entry["count"] += 1
        entry["last"] = at
        print(json.dumps({"alert": kind, "at": at, "count": entry["count"], **details}, ensure_ascii=False), flush=True)

    def state(self) -> dict:
        return {name: dict(entry) for name, entry in sorted(self.counts.items())}


def _contains(error: BaseException, kind: type) -> bool:
    if isinstance(error, kind):
        return True
    return isinstance(error, BaseExceptionGroup) and any(_contains(inner, kind) for inner in error.exceptions)


async def _send_json(send, status: int, payload: dict, headers: list[tuple[bytes, bytes]] = ()) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode()
    await send({
        "type": "http.response.start",
        "status": status,
        "headers": [(b"content-type", b"application/json"), (b"content-length", str(len(body)).encode()), *headers],
    })
    await send({"type": "http.response.body", "body": body})


class RequestGuard:
    def __init__(self, app, limits: Callable[[], GenerationLimits], waiting: Callable[[], int], max_waiting: Callable[[], int], alerts: Callable[[], Alerts], ip_header: Callable[[], str], max_body: Callable[[], int] = lambda: MAX_BODY_BYTES, send_timeout: Callable[[], float] = lambda: SEND_TIMEOUT_S) -> None:
        self.app = app
        self.limits = limits
        self.waiting = waiting
        self.max_waiting = max_waiting
        self.alerts = alerts
        self.ip_header = ip_header
        self.max_body = max_body
        self.send_timeout = send_timeout

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        headers = {name.decode("latin-1").lower(): value.decode("latin-1") for name, value in scope.get("headers", [])}
        limit = self.max_body()
        length = headers.get("content-length", "")
        if limit and length.isdigit() and int(length) > limit:
            self.alerts().raise_alert("request_too_large", path=scope["path"], size_bytes=int(length), limit_bytes=limit)
            await _send_json(send, 413, {"detail": request_too_large_detail(limit)})
            return
        if limit:
            receive = self._bounded(receive, limit, scope["path"])
        if (scope["method"], scope["path"]) not in GENERATION_PATHS:
            await self.app(scope, receive, send)
            return
        try:
            maximum = self.max_waiting()
            if maximum and self.waiting() >= maximum:
                raise LimitRefused("queue_full", maximum, QUEUE_RETRY_S)
            peer = (scope.get("client") or (None,))[0]
            admission = self.limits().admit(client_keys(peer, headers, self.ip_header()))
        except LimitRefused as refusal:
            self.alerts().raise_alert(refusal.reason, path=scope["path"], limit=refusal.limit)
            await _send_json(
                send,
                429,
                {"detail": {"code": "too_many_requests", "reason": refusal.reason, "limit": refusal.limit, "retry_after": refusal.retry_after, "message": str(refusal)}},
                [(b"retry-after", str(refusal.retry_after).encode())],
            )
            return
        try:
            await self.app(scope, receive, self._timed(send))
        except BaseException as error:
            if not _contains(error, SendStalled):
                raise
            self.alerts().raise_alert("send_timeout", path=scope["path"], timeout_s=self.send_timeout())
        finally:
            admission.release()

    def _bounded(self, receive, limit: int, path: str):
        received = 0

        async def bounded():
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > limit:
                    self.alerts().raise_alert("request_too_large", path=path, size_bytes=received, limit_bytes=limit)
                    raise RequestTooLarge(limit)
            return message

        return bounded

    def _timed(self, send):
        async def timed(message):
            if message["type"] != "http.response.body":
                await send(message)
                return
            # NE PAS attendre sans fin un client qui ne lit plus le PDF : il garderait sa connexion, son créneau et le dossier temporaire de la génération.
            try:
                await asyncio.wait_for(send(message), self.send_timeout())
            except TimeoutError as error:
                raise SendStalled() from error

        return timed
