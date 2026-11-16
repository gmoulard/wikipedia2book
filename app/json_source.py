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
import ipaddress
import json
import socket
from urllib.parse import urljoin, urlsplit

import httpx
from pydantic import ValidationError

from app.models import Project
from app.wikipedia_api import USER_AGENT

MAX_JSON_BYTES = 60_000_000
MAX_REDIRECTS = 3
TIMEOUT_S = 30.0


class JsonSourceError(Exception):
    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code


def _resolve(host: str) -> list[str]:
    return [info[4][0] for info in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)]


# NE PAS télécharger une adresse qui mène au réseau interne (127.0.0.1, 10.x, métadonnées du cloud…) : le serveur deviendrait un relais vers ses voisins ; chaque redirection est revérifiée.
async def _check_url(url: str, resolve) -> None:
    parts = urlsplit(url)
    if parts.scheme != "https" or not parts.hostname:
        raise JsonSourceError(422, "L’URL du fichier JSON doit commencer par https://.")
    try:
        addresses = await asyncio.to_thread(resolve, parts.hostname)
    except OSError as error:
        raise JsonSourceError(422, f"Hôte introuvable : {parts.hostname}.") from error
    if not addresses or any(not ipaddress.ip_address(address.split("%")[0]).is_global for address in addresses):
        raise JsonSourceError(422, f"Hôte refusé : {parts.hostname} n’est pas une adresse publique.")


def _project_from_payload(payload) -> Project:
    if isinstance(payload, dict) and payload.get("format") == "wikipedia2book-workspace":
        if payload.get("version") != 1 or not isinstance(payload.get("projects"), list) or not payload["projects"]:
            raise JsonSourceError(422, "Version ou structure du fichier JSON non prise en charge.")
        payload = payload["projects"][0]
    elif isinstance(payload, list):
        if not payload:
            raise JsonSourceError(422, "Le fichier JSON ne contient aucun livre.")
        payload = payload[0]
    try:
        return Project.model_validate(payload)
    except ValidationError as error:
        raise JsonSourceError(422, f"Livre invalide dans le fichier JSON : {error.errors()[0]['msg']}.") from error


async def fetch_project(url: str, transport: httpx.AsyncBaseTransport | None = None, resolve=_resolve) -> Project:
    async with httpx.AsyncClient(transport=transport, timeout=TIMEOUT_S, follow_redirects=False, headers={"User-Agent": USER_AGENT}) as client:
        for _ in range(MAX_REDIRECTS + 1):
            await _check_url(url, resolve)
            try:
                async with client.stream("GET", url) as response:
                    if response.is_redirect:
                        url = urljoin(url, response.headers.get("location", ""))
                        continue
                    if response.status_code != 200:
                        raise JsonSourceError(502, f"Le fichier JSON n’a pas pu être téléchargé (HTTP {response.status_code}).")
                    if int(response.headers.get("content-length") or 0) > MAX_JSON_BYTES:
                        raise JsonSourceError(413, f"Fichier JSON trop volumineux ({MAX_JSON_BYTES // 1_000_000} Mo au plus).")
                    body = bytearray()
                    async for chunk in response.aiter_bytes():
                        body.extend(chunk)
                        if len(body) > MAX_JSON_BYTES:
                            raise JsonSourceError(413, f"Fichier JSON trop volumineux ({MAX_JSON_BYTES // 1_000_000} Mo au plus).")
            except httpx.HTTPError as error:
                raise JsonSourceError(502, f"Le fichier JSON n’a pas pu être téléchargé ({type(error).__name__}).") from error
            try:
                payload = json.loads(bytes(body))
            except (ValueError, UnicodeDecodeError) as error:
                raise JsonSourceError(422, "Le fichier téléchargé n’est pas un JSON valide.") from error
            return _project_from_payload(payload)
    raise JsonSourceError(502, "Trop de redirections pour télécharger le fichier JSON.")
