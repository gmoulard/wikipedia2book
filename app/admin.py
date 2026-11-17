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

import base64
import binascii
import hashlib
import hmac
import json
import secrets
import time
from collections.abc import Mapping
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException, Request

from app.wikipedia_api import USER_AGENT

OAUTH_BASE = "https://meta.wikimedia.org/w/rest.php/oauth2"
SESSION_COOKIE = "w2b_admin"
STATE_COOKIE = "w2b_oauth_state"
SESSION_S = 2 * 3600
ADMIN_PATH = "/admin"
MONITOR_TOKEN_MIN = 32
STATE_S = 600
OAUTH_TIMEOUT_S = 20.0
DEFAULT_ADMINS_HEX = ("474D6F756C617264", "436170697461696E6543616E65747465")
oauth_transport: httpx.AsyncBaseTransport | None = None
# NE PAS rendre cette clé fixe ni l'écrire sur disque : tirée au démarrage, elle invalide les sessions à chaque redémarrage, sans rien garder côté serveur (serveur sans état).
_SIGNING_KEY = secrets.token_bytes(32)


class AdminSettings:
    def __init__(self, admins: frozenset[str], client_id: str, client_secret: str, callback: str) -> None:
        self.admins = admins
        self.client_id = client_id
        self.client_secret = client_secret
        self.callback = callback

    @property
    def configured(self) -> bool:
        return bool(self.client_id and self.client_secret and self.callback)


def monitor_token_setting(environ: Mapping[str, str]) -> str:
    token = environ.get("WIKIPEDIA2BOOK_MONITOR_TOKEN", "").strip()
    if token and len(token) < MONITOR_TOKEN_MIN:
        raise ValueError(f"WIKIPEDIA2BOOK_MONITOR_TOKEN doit compter au moins {MONITOR_TOKEN_MIN} caractères (par exemple : python -c \"import secrets; print(secrets.token_urlsafe(32))\").")
    return token


def require_monitor(request: Request, token: str) -> None:
    scheme, _, given = request.headers.get("authorization", "").partition(" ")
    # NE PAS ouvrir ces endpoints sans jeton : ils donnent les limites, les alertes et le journal des générations, de quoi régler une attaque juste sous les seuils.
    if not token or scheme.lower() != "bearer" or not hmac.compare_digest(given.strip().encode(), token.encode()):
        raise HTTPException(status_code=401, detail={"code": "monitor_token_required", "message": "Jeton de supervision requis (en-tête Authorization: Bearer)."}, headers={"WWW-Authenticate": "Bearer"})


def normalize_username(name: str) -> str:
    name = " ".join(name.replace("_", " ").split())
    return name[:1].upper() + name[1:]


def decode_admins(text: str) -> frozenset[str]:
    names = set()
    for item in text.split(","):
        item = item.strip()
        if not item:
            continue
        try:
            name = bytes.fromhex(item).decode("utf-8")
        except (ValueError, UnicodeDecodeError) as error:
            raise ValueError(f"WIKIPEDIA2BOOK_ADMINS doit lister des noms d'utilisateur Wikimédia écrits en hexadécimal UTF-8, séparés par des virgules (reçu : {item!r}).") from error
        names.add(normalize_username(name))
    return frozenset(names)


def admin_settings(environ: Mapping[str, str]) -> AdminSettings:
    admins_text = environ.get("WIKIPEDIA2BOOK_ADMINS", "").strip() or ",".join(DEFAULT_ADMINS_HEX)
    return AdminSettings(
        decode_admins(admins_text),
        environ.get("WIKIPEDIA2BOOK_OAUTH_CLIENT_ID", "").strip(),
        environ.get("WIKIPEDIA2BOOK_OAUTH_CLIENT_SECRET", "").strip(),
        environ.get("WIKIPEDIA2BOOK_OAUTH_CALLBACK", "").strip(),
    )


def _sign(payload: dict) -> str:
    body = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode().rstrip("=")
    signature = hmac.new(_SIGNING_KEY, body.encode(), hashlib.sha256).hexdigest()
    return f"{body}.{signature}"


def _unsign(value: str | None) -> dict | None:
    if not value or "." not in value:
        return None
    body, signature = value.rsplit(".", 1)
    expected = hmac.new(_SIGNING_KEY, body.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        return None
    try:
        payload = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
    except (ValueError, binascii.Error):
        return None
    if not isinstance(payload, dict) or payload.get("exp", 0) < time.time():
        return None
    return payload


def session_cookie(username: str) -> str:
    return _sign({"user": username, "exp": int(time.time()) + SESSION_S})


def state_cookie(state: str) -> str:
    return _sign({"state": state, "exp": int(time.time()) + STATE_S})


def state_matches(cookie: str | None, state: str) -> bool:
    payload = _unsign(cookie)
    return bool(payload and state and hmac.compare_digest(str(payload.get("state", "")), state))


def session_user(request: Request, settings: AdminSettings) -> str | None:
    payload = _unsign(request.cookies.get(SESSION_COOKIE))
    if payload is None:
        return None
    user = payload.get("user")
    # NE PAS se fier à la seule session : un nom retiré de WIKIPEDIA2BOOK_ADMINS perd l'accès au redémarrage suivant, même avec un cookie encore valide.
    return user if isinstance(user, str) and user in settings.admins else None


def require_admin(request: Request, settings: AdminSettings) -> str:
    user = session_user(request, settings)
    if user is None:
        raise HTTPException(status_code=401, detail={"code": "admin_login_required", "message": "Connexion d'administrateur requise."})
    return user


def authorize_url(settings: AdminSettings, state: str) -> str:
    return f"{OAUTH_BASE}/authorize?" + urlencode({"response_type": "code", "client_id": settings.client_id, "redirect_uri": settings.callback, "state": state})


class OAuthError(Exception):
    pass


async def wikimedia_username(settings: AdminSettings, code: str) -> str:
    async with httpx.AsyncClient(transport=oauth_transport, timeout=OAUTH_TIMEOUT_S, headers={"User-Agent": USER_AGENT}) as client:
        try:
            token = await client.post(f"{OAUTH_BASE}/access_token", data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": settings.client_id,
                "client_secret": settings.client_secret,
                "redirect_uri": settings.callback,
            })
            if token.status_code != 200:
                raise OAuthError(f"Wikimédia a refusé le code de connexion (HTTP {token.status_code}).")
            access = token.json().get("access_token")
            if not access:
                raise OAuthError("Wikimédia n'a pas renvoyé de jeton d'accès.")
            profile = await client.get(f"{OAUTH_BASE}/resource/profile", headers={"Authorization": f"Bearer {access}"})
            if profile.status_code != 200:
                raise OAuthError(f"Wikimédia n'a pas renvoyé le profil (HTTP {profile.status_code}).")
            username = profile.json().get("username")
        except (httpx.HTTPError, ValueError) as error:
            raise OAuthError(f"Connexion à Wikimédia impossible ({type(error).__name__}).") from error
    if not isinstance(username, str) or not username:
        raise OAuthError("Le profil Wikimédia ne contient pas de nom d'utilisateur.")
    return normalize_username(username)
