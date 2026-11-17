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
import os
import re
import weakref
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
from typing import get_args
from urllib.parse import parse_qs, quote, unquote, urlparse, urlsplit

import httpx
from bs4 import BeautifulSoup

from app.models import Article, Site
from app.version import VERSION


_LANGUAGE_RE = re.compile(r"^[a-z0-9-]{2,12}$")
SITES: tuple[str, ...] = get_args(Site)
_HOST_RE = re.compile(rf"([a-z0-9-]{{2,12}})\.({'|'.join(SITES)})\.org")
WIKIPEDIA_PDF_PAPERS = {"A4": "a4", "Letter": "letter", "Legal": "legal"}
USER_AGENT = (
    f"Wikipedia2Book/{VERSION} (https://wikipedia2book.toolforge.org/; https://github.com/gmoulard/wikipedia2book) "
    f"httpx/{httpx.__version__}"
)
# NE PAS lever les limites ailleurs que sur Toolforge : seuls les outils Toolforge sont exemptés par la politique robots de Wikimédia ; Northflank y reste soumis.
ON_TOOLFORGE = os.environ.get("WIKIPEDIA2BOOK_PLATFORM") == "toolforge"
MEDIA_CONCURRENCY = 2
MEDIA_WINDOW_S = 10
MEDIA_WINDOW_BYTES = 25_000_000 // 8 * MEDIA_WINDOW_S
RETRY_STATUSES = {429, 503}
RETRY_DELAYS_S = (2, 4, 8, 16)
MAX_RETRY_WAIT_S = 20
FULL_TEXT_PAGES = {
    "version imprimable", "print version", "printable version", "druckversion", "versione stampabile",
    "versión para imprimir", "versión imprimible", "versão para impressão", "versão para imprimir", "afdrukbare versie",
    "yazdırılabilir sürüm", "印刷版", "印刷用", "打印版", "نسخه چاپی", "نسخة للطباعة", "نسخة قابلة للطباعة",
    "texte entier", "texte complet", "full text", "complete text", "volltext", "vollständiger text", "testo completo",
    "testo integrale", "texto completo", "texto integral", "volledige tekst", "tam metin", "全覽", "全文", "全本", "全文表示",
    "متن کامل", "النص الكامل",
}
SUBPAGE_BOOK_MIN = 2
SUBPAGE_BOOK_SITES = ("wikibooks", "wikisource")
RATE_LIMITED = "Wikipédia limite le nombre de requêtes en ce moment (HTTP {status}) : réessayez dans quelques minutes."


class MediaWikiError(Exception):
    pass


class MediaWikiPageNotFound(MediaWikiError):
    pass


@dataclass
class WikipediaBook:
    subtitle: str
    chapters: list[tuple[str, list[str]]]


def validate_language(language: str) -> str:
    normalized = language.lower()
    if not _LANGUAGE_RE.fullmatch(normalized):
        raise ValueError("Code de langue Wikipédia invalide.")
    return normalized


def site_host(language: str, site: str) -> str:
    if site not in SITES:
        raise ValueError(f"Site Wikimédia invalide : seuls {', '.join(SITES)} sont acceptés.")
    return f"{validate_language(language)}.{site}.org"


def article_url(language: str, title: str, site: str = "wikipedia") -> str:
    slug = quote(title.replace(" ", "_"), safe="()!$&'*,;=:@")
    return f"https://{site_host(language, site)}/wiki/{slug}"


def parse_article_url(url: str) -> tuple[str, str, str]:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    match = _HOST_RE.fullmatch(host)
    if parsed.scheme != "https" or not match or parsed.port is not None:
        raise ValueError(
            f"L’URL doit pointer vers une page HTTPS d’un projet Wikimédia <langue>.<projet>.org ({', '.join(SITES)})."
        )
    language = validate_language(match.group(1))
    site = match.group(2)
    if parsed.path.startswith("/wiki/"):
        title = unquote(parsed.path.removeprefix("/wiki/")).replace("_", " ")
    elif parsed.path == "/w/index.php":
        title = parse_qs(parsed.query).get("title", [""])[0].replace("_", " ")
    else:
        title = ""
    if not title or len(title) > 300:
        raise ValueError("L’URL ne contient pas de titre d’article valide.")
    return language, title, site


def retry_delay(response: httpx.Response, attempt: int) -> float:
    default = RETRY_DELAYS_S[attempt]
    header = response.headers.get("Retry-After", "").strip()
    if not header:
        return default
    try:
        delay = float(header)
    except ValueError:
        try:
            delay = (parsedate_to_datetime(header) - datetime.now(timezone.utc)).total_seconds()
        except (TypeError, ValueError):
            return default
    return min(max(delay, 1.0), MAX_RETRY_WAIT_S)


def _clock() -> float:
    return asyncio.get_running_loop().time()


class MediaLimiter:
    def __init__(self) -> None:
        self.slots = asyncio.Semaphore(MEDIA_CONCURRENCY)
        self.received: deque[tuple[float, int]] = deque()
        self.lock = asyncio.Lock()

    async def consume(self, size: int) -> None:
        async with self.lock:
            while True:
                now = _clock()
                while self.received and self.received[0][0] <= now - MEDIA_WINDOW_S:
                    self.received.popleft()
                if not self.received or sum(count for _, count in self.received) + size <= MEDIA_WINDOW_BYTES:
                    self.received.append((now, size))
                    return
                await asyncio.sleep(self.received[0][0] + MEDIA_WINDOW_S - now)


_media_limiters: "weakref.WeakKeyDictionary[asyncio.AbstractEventLoop, MediaLimiter]" = weakref.WeakKeyDictionary()


def media_limiter() -> MediaLimiter:
    loop = asyncio.get_running_loop()
    if loop not in _media_limiters:
        _media_limiters[loop] = MediaLimiter()
    return _media_limiters[loop]


class MediaWikiClient:
    def __init__(self, timeout: float = 20.0) -> None:
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None
        self._resume_at = 0.0
        self.on_wait: Callable[[float], None] | None = None

    async def _media_get(self, url: str, **kwargs) -> httpx.Response:
        limiter = media_limiter()
        # NE PAS sortir ce bloc du sémaphore global ni lire le corps d'un coup : hors Toolforge, la politique robots de Wikimédia (REST API rules, 3 requêtes simultanées au plus) est respectée avec 2 téléchargements simultanés pour tout le serveur et 25 Mbit/s sur 10 s.
        async with limiter.slots:
            async with self._client.stream("GET", url, **kwargs) as response:
                chunks = []
                async for chunk in response.aiter_bytes():
                    await limiter.consume(len(chunk))
                    chunks.append(chunk)
        return httpx.Response(response.status_code, headers=response.headers, content=b"".join(chunks), request=response.request)

    async def _send(self, url: str, media: bool = False, **kwargs) -> httpx.Response:
        attempt = 0
        while True:
            pause = self._resume_at - _clock()
            if pause > 0:
                await asyncio.sleep(pause)
            response = await (self._media_get(url, **kwargs) if media and not ON_TOOLFORGE else self._client.get(url, **kwargs))
            if response.status_code not in RETRY_STATUSES:
                return response
            if attempt == len(RETRY_DELAYS_S):
                raise MediaWikiError(RATE_LIMITED.format(status=response.status_code))
            # NE PAS dormir seulement dans cette tâche : la pause est partagée par tout le client, sinon les téléchargements parallèles relancent aussitôt Wikimédia, qui les refuse encore.
            now = _clock()
            resume_at = max(self._resume_at, now + retry_delay(response, attempt))
            if resume_at > self._resume_at and self.on_wait is not None:
                self.on_wait(resume_at - now)
            self._resume_at = resume_at
            attempt += 1

    async def __aenter__(self) -> "MediaWikiClient":
        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            headers={"User-Agent": USER_AGENT},
        )
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _get(self, language: str, params: dict, site: str = "wikipedia") -> dict:
        host = site_host(language, site)
        if self._client is None:
            raise RuntimeError("MediaWikiClient doit être utilisé dans un bloc async with.")
        query = {"action": "query", "format": "json", "formatversion": 2, **params}
        try:
            response = await self._send(f"https://{host}/w/api.php", params=query)
            response.raise_for_status()
            result = response.json()
        except (httpx.HTTPError, ValueError) as error:
            raise MediaWikiError("Impossible de joindre l’API Wikipédia.") from error
        if "error" in result:
            raise MediaWikiError(result["error"].get("info", "Erreur de l’API Wikipédia."))
        return result

    async def search(self, query: str, language: str = "fr", limit: int = 10, site: str = "wikipedia") -> list[dict]:
        result = await self._get(
            language,
            {
                "list": "search",
                "srsearch": query,
                "srlimit": min(max(limit, 1), 20),
                "srnamespace": 0,
            },
            site,
        )
        items = result.get("query", {}).get("search", [])
        return [
            {
                "page_id": item["pageid"],
                "title": item["title"],
                "snippet": BeautifulSoup(item.get("snippet", ""), "html.parser").get_text(" ", strip=True),
                "url": article_url(language, item["title"], site),
            }
            for item in items
        ]

    async def get_page(self, title: str, language: str = "fr", site: str = "wikipedia") -> tuple[str, int] | None:
        result = await self._get(language, {"prop": "info", "titles": title, "redirects": 1}, site)
        pages = result.get("query", {}).get("pages", [])
        if not pages or pages[0].get("missing") or pages[0].get("invalid"):
            return None
        return pages[0]["title"], pages[0]["ns"]

    # NE PAS fusionner en un seul appel : MediaWiki ne renvoie pas extracts + première révision ensemble de façon exploitable.
    async def get_intro_and_creator(self, title: str, language: str = "fr", site: str = "wikipedia") -> tuple[str, str]:
        extract_result = await self._get(
            language, {"prop": "extracts", "exintro": 1, "explaintext": 1, "titles": title}, site
        )
        pages = extract_result.get("query", {}).get("pages", [])
        introduction = pages[0].get("extract", "") if pages and not pages[0].get("missing") else ""

        creator_result = await self._get(
            language, {"prop": "revisions", "rvlimit": 1, "rvdir": "newer", "rvprop": "user", "titles": title}, site
        )
        rev_pages = creator_result.get("query", {}).get("pages", [])
        revisions = rev_pages[0].get("revisions", []) if rev_pages else []
        creator = revisions[0].get("user", "") if revisions else ""

        return introduction, creator

    async def get_article_pdf(self, title: str, language: str, paper: str, site: str = "wikipedia") -> bytes:
        host = site_host(language, site)
        if paper not in WIKIPEDIA_PDF_PAPERS.values():
            raise ValueError("Format de PDF Wikipédia invalide.")
        if self._client is None:
            raise RuntimeError("MediaWikiClient doit être utilisé dans un bloc async with.")
        page_path = quote(title.replace(" ", "_"), safe="")
        url = f"https://{host}/api/rest_v1/page/pdf/{page_path}/{paper}"
        try:
            response = await self._send(url, media=True, timeout=120)
            response.raise_for_status()
        except httpx.HTTPError as error:
            raise MediaWikiError(f"Impossible de télécharger le PDF Wikipédia pour « {title} ».") from error
        if response.content[:5] != b"%PDF-":
            raise MediaWikiError(f"Wikipédia n’a pas renvoyé un PDF valide pour « {title} ».")
        return response.content

    async def get_links(self, title: str, language: str = "fr", site: str = "wikipedia") -> list[str]:
        result = await self._get(
            language,
            # NE PAS passer à prop=links : tri alphabétique, l'ordre d'apparition dans la page serait perdu.
            {"action": "parse", "page": title, "prop": "text", "redirects": 1, "disabletoc": 1},
            site,
        )
        parsed = result.get("parse", {})
        seen = {parsed.get("title", title).casefold()}
        links: list[str] = []
        for anchor in BeautifulSoup(parsed.get("text", ""), "html.parser").select('a[href^="/wiki/"]'):
            if "new" in (anchor.get("class") or []):
                continue
            link_title = unquote(anchor["href"][len("/wiki/"):].split("#", 1)[0]).replace("_", " ").strip()
            if not link_title or ":" in link_title or link_title.casefold() in seen:
                continue
            seen.add(link_title.casefold())
            links.append(link_title)
        return links

    async def get_subpage_book(self, title: str, language: str, site: str, limit: int = 500) -> WikipediaBook:
        # NE PAS passer à prop=links : tri alphabétique, l'ordre des chapitres du sommaire serait perdu.
        result = await self._get(language, {"action": "parse", "page": title, "prop": "text", "redirects": 1, "disabletoc": 1}, site)
        parsed = result.get("parse", {})
        chapters = subpage_chapters(parsed.get("text", ""), parsed.get("title", title), min(max(limit, 1), 500), skip_parents=site == "wikisource")
        return WikipediaBook(subtitle="", chapters=chapters)

    # NE PAS modifier sans aligner wikimediaFileUrl dans app.js : un PDF garde son original, une image sa vignette de 2 000 px.
    async def get_file_url(self, host: str, name: str) -> str:
        if self._client is None:
            raise RuntimeError("MediaWikiClient doit être utilisé dans un bloc async with.")
        query = {"action": "query", "format": "json", "formatversion": 2, "prop": "imageinfo", "iiprop": "url|mime", "iiurlwidth": 2000, "titles": f"File:{name}"}
        try:
            response = await self._send(f"https://{host}/w/api.php", params=query)
            response.raise_for_status()
            pages = response.json().get("query", {}).get("pages", [])
        except (httpx.HTTPError, ValueError) as error:
            raise MediaWikiError(f"Impossible de joindre l’API de {host}.") from error
        info = (pages[0].get("imageinfo") or [{}])[0] if pages else {}
        if not info.get("url"):
            raise MediaWikiPageNotFound(f"Le fichier « {name} » est introuvable sur {host}.")
        url = info["url"] if info.get("mime") == "application/pdf" else info.get("thumburl") or info["url"]
        parts = urlsplit(url)
        query = "&".join(pair for pair in parts.query.split("&") if pair and not pair.startswith("utm_"))
        return parts._replace(query=query).geturl()

    async def get_wikitext(self, title: str, language: str, site: str = "wikipedia") -> str | None:
        result = await self._get(
            validate_language(language),
            # NE PAS passer à prop=links ni parse&prop=links : tri alphabétique, l'ordre réel du livre serait perdu.
            {"prop": "revisions", "titles": title, "rvprop": "content", "rvslots": "main"},
            site,
        )
        pages = result.get("query", {}).get("pages", [])
        if not pages or pages[0].get("missing"):
            return None
        revisions = pages[0].get("revisions", [])
        return revisions[0].get("slots", {}).get("main", {}).get("content", "") if revisions else ""

    async def get_book(self, title: str, language: str = "fr", limit: int = 200) -> WikipediaBook:
        content = await self.get_wikitext(title, language)
        if content is None:
            raise MediaWikiPageNotFound(f"La page de livre Wikipédia « {title} » est introuvable.")
        return parse_book_wikitext(content, min(max(limit, 1), 500))


def parse_book_wikitext(content: str, limit: int = 200) -> WikipediaBook:
    subtitle = ""
    chapters: list[tuple[str, list[str]]] = [("", [])]
    seen: set[str] = set()
    count = 0
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("="):
            heading = re.fullmatch(r"===(?!=)(.*?)(?<!=)===", stripped)
            if heading and not subtitle:
                subtitle = _plain_wikitext(heading.group(1))
            continue
        if stripped.startswith(";"):
            chapter_title = _plain_wikitext(stripped[1:])
            if chapter_title:
                chapters.append((chapter_title, []))
            continue
        for match in re.finditer(r"\[\[([^\[\]|#]+)", line):
            link_title = match.group(1).strip().replace("_", " ")
            if not link_title or ":" in link_title or link_title.casefold() in seen:
                continue
            seen.add(link_title.casefold())
            chapters[-1][1].append(link_title)
            count += 1
            if count >= limit:
                break
        if count >= limit:
            break
    return WikipediaBook(subtitle=subtitle, chapters=[chapter for chapter in chapters if chapter[1]])


WIKIMEDIA_HOST = re.compile(r"^(?:[a-z0-9-]+\.)*(?:wikimedia|wikipedia|wikisource|wikibooks|wikivoyage|wikiversity|wikiquote|wiktionary|wikinews)\.org$")


def wikimedia_file_page(url: str) -> tuple[str, str] | None:
    parts = urlsplit(url)
    page = re.fullmatch(r"/wiki/[^:/]+:(.+)", unquote(parts.path))
    if parts.scheme != "https" or not page or not WIKIMEDIA_HOST.match(parts.hostname or ""):
        return None
    return parts.hostname, page.group(1).replace("_", " ")


PRINTABLE_SKIPPED_PAGES = {"couverture", "cover", "licence de documentation libre gnu", "gnu free documentation license", "licence", "license"}
TRANSCLUSION = re.compile(r"\{\{\s*:\s*([^{}|]+?)\s*(?:\|[^{}]*)?\}\}")


def is_printable_wikitext(content: str) -> bool:
    return bool(TRANSCLUSION.search(content))


def parse_printable_wikitext(content: str, limit: int = 500) -> WikipediaBook:
    chapters: list[tuple[str, list[str]]] = [("", [])]
    seen: set[str] = set()
    count = 0
    for line in content.splitlines():
        heading = re.fullmatch(r"=(?!=)(.*?)(?<!=)=", line.strip())
        if heading:
            chapter_title = _plain_wikitext(re.sub(r"<[^>]*>", "", heading.group(1)))
            if chapter_title:
                chapters.append((chapter_title, []))
        for match in TRANSCLUSION.finditer(line):
            page_title = match.group(1).strip().replace("_", " ")
            if not page_title or ":" in page_title or page_title.casefold() in seen:
                continue
            if page_title.rsplit("/", 1)[-1].casefold() in PRINTABLE_SKIPPED_PAGES:
                continue
            seen.add(page_title.casefold())
            chapters[-1][1].append(page_title)
            count += 1
            if count >= limit:
                return WikipediaBook(subtitle="", chapters=[chapter for chapter in chapters if chapter[1]])
    return WikipediaBook(subtitle="", chapters=[chapter for chapter in chapters if chapter[1]])


def printable_wikitext_title(content: str) -> str:
    named = re.search(r"\|\s*(?:titre|title)\s*=\s*([^|{}\n]+)", content)
    return _plain_wikitext(named.group(1)) if named else ""


def book_wikitext_title(content: str) -> str:
    for line in content.splitlines():
        heading = re.fullmatch(r"==(?!=)(.*?)(?<!=)==", line.strip())
        if heading:
            return _plain_wikitext(heading.group(1))
    return ""


def subpage_chapters(html: str, title: str, limit: int = 500, skip_parents: bool = False) -> list[tuple[str, list[str]]]:
    soup = BeautifulSoup(html, "html.parser")
    for edit_link in soup.select(".mw-editsection"):
        edit_link.decompose()
    prefix = title + "/"
    seen: set[str] = set()
    sequence: list[tuple[int, str]] = []
    for element in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "a"]):
        if element.name != "a":
            sequence.append((int(element.name[1]), element.get_text(" ", strip=True)))
            continue
        href = element.get("href", "")
        if not href.startswith("/wiki/") or "new" in (element.get("class") or []):
            continue
        link_title = unquote(href[len("/wiki/"):].split("#", 1)[0]).replace("_", " ").strip()
        # NE PAS garder la version imprimable ni le texte entier : ils contiennent tout le livre, qui serait en double dans le PDF.
        if not link_title.startswith(prefix) or link_title in seen or link_title.rsplit("/", 1)[-1].casefold() in FULL_TEXT_PAGES:
            continue
        seen.add(link_title)
        sequence.append((0, link_title))
        if len(seen) >= limit:
            break
    if skip_parents:
        # NE PAS appliquer à Wikilivres : un chapitre y a souvent son propre texte en plus de ses sous-pages ; sur Wikisource, une page qui a des sous-pages dans le livre n'est qu'un sommaire intermédiaire.
        pages = {text for heading_level, text in sequence if heading_level == 0}
        sequence = [(heading_level, text) for heading_level, text in sequence
                    if heading_level != 0 or not any(page.startswith(text + "/") for page in pages)]
    for level in (2, 3, 4):
        chapters: list[tuple[str, list[str]]] = [("", [])]
        for heading_level, text in sequence:
            if heading_level == 0:
                chapters[-1][1].append(text)
            elif heading_level <= level:
                chapters.append((text, []))
        chapters = [chapter for chapter in chapters if chapter[1]]
        if sum(1 for name, _ in chapters if name) >= 2:
            return chapters
    pages = [text for heading_level, text in sequence if heading_level == 0]
    return [("", pages)] if pages else []


def _plain_wikitext(text: str) -> str:
    text = re.sub(r"\[\[(?:[^\[\]|]*\|)?([^\[\]]*)\]\]", r"\1", text)
    return re.sub(r"'{2,}", "", text).strip()
