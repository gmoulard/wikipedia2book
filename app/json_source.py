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
from urllib.parse import urljoin, urlsplit, urlunsplit

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


NAT64_PREFIX = ipaddress.ip_network("64:ff9b::/96")


# NE PAS se fier au seul is_global : une adresse IPv6 peut transporter une IPv4 interne (::ffff:…, NAT64 64:ff9b::…, 6to4, Teredo) et une adresse multicast passe pour publique.
def is_public_address(address: str) -> bool:
    ip = ipaddress.ip_address(address.split("%")[0])
    if ip.is_multicast or not ip.is_global:
        return False
    if ip.version == 6:
        embedded = [ip.ipv4_mapped, ip.sixtofour, *(ip.teredo or ())]
        if ip in NAT64_PREFIX:
            embedded.append(ipaddress.IPv4Address(int(ip) & 0xFFFFFFFF))
        return all(is_public_address(str(inner)) for inner in embedded if inner is not None)
    return True


def _resolve(host: str) -> list[str]:
    return [info[4][0] for info in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)]


# NE PAS télécharger une adresse qui mène au réseau interne (127.0.0.1, 10.x, métadonnées du cloud…) : le serveur deviendrait un relais vers ses voisins ; chaque redirection est revérifiée.
async def _check_url(url: str, resolve, label: str) -> str:
    parts = urlsplit(url)
    if parts.scheme != "https" or not parts.hostname:
        raise JsonSourceError(422, f"L’adresse {label} doit commencer par https:// : {url}")
    try:
        addresses = await asyncio.to_thread(resolve, parts.hostname)
    except OSError as error:
        raise JsonSourceError(422, f"Hôte introuvable pour {label} : {parts.hostname}.") from error
    if not addresses or not all(is_public_address(address) for address in addresses):
        raise JsonSourceError(422, f"Hôte refusé pour {label} : {parts.hostname} n’est pas une adresse publique.")
    return addresses[0].split("%")[0]


# NE PAS laisser httpx résoudre le nom une seconde fois : un nom qui change d'adresse entre la vérification et la connexion (DNS rebinding) mènerait au réseau interne ; la connexion se fait à l'adresse vérifiée, le nom ne sert qu'à l'en-tête Host et au certificat (SNI).
def _pinned(url: str, address: str) -> tuple[str, dict, dict]:
    parts = urlsplit(url)
    port = f":{parts.port}" if parts.port else ""
    host = f"[{address}]" if ":" in address else address
    target = urlunsplit(parts._replace(netloc=host + port))
    return target, {"Host": parts.hostname + port}, {"sni_hostname": parts.hostname}


async def download(
    url: str, max_bytes: int, label: str, transport: httpx.AsyncBaseTransport | None = None, resolve=_resolve
) -> tuple[bytes, str]:
    too_large = f"{label[0].upper()}{label[1:]} est trop volumineux ({max_bytes // 1_000_000} Mo au plus) : {url}"
    async with httpx.AsyncClient(transport=transport, timeout=TIMEOUT_S, follow_redirects=False, headers={"User-Agent": USER_AGENT}) as client:
        for _ in range(MAX_REDIRECTS + 1):
            target, headers, extensions = _pinned(url, await _check_url(url, resolve, label))
            try:
                async with client.stream("GET", target, headers=headers, extensions=extensions) as response:
                    if response.is_redirect:
                        url = urljoin(url, response.headers.get("location", ""))
                        continue
                    if response.status_code != 200:
                        raise JsonSourceError(502, f"{label[0].upper()}{label[1:]} n’a pas pu être téléchargé (HTTP {response.status_code}) : {url}")
                    if int(response.headers.get("content-length") or 0) > max_bytes:
                        raise JsonSourceError(413, too_large)
                    body = bytearray()
                    async for chunk in response.aiter_bytes():
                        body.extend(chunk)
                        if len(body) > max_bytes:
                            raise JsonSourceError(413, too_large)
                    content_type = response.headers.get("content-type", "").split(";")[0].strip().lower()
            except httpx.HTTPError as error:
                raise JsonSourceError(502, f"{label[0].upper()}{label[1:]} n’a pas pu être téléchargé ({type(error).__name__}) : {url}") from error
            return bytes(body), content_type
    raise JsonSourceError(502, f"Trop de redirections pour télécharger {label} : {url}")


def project_from_payload(payload) -> Project:
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
    body, _ = await download(url, MAX_JSON_BYTES, "le fichier JSON", transport, resolve)
    try:
        payload = json.loads(body)
    except (ValueError, UnicodeDecodeError) as error:
        raise JsonSourceError(422, "Le fichier téléchargé n’est pas un JSON valide.") from error
    return project_from_payload(payload)
