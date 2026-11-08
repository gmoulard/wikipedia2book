import re
from urllib.parse import parse_qs, quote, unquote, urlparse

import httpx
from bs4 import BeautifulSoup

from app.models import Article


_LANGUAGE_RE = re.compile(r"^[a-z0-9-]{2,12}$")
_USER_AGENT = "Wikipedia2Book/0.1 (https://github.com/gmoulard/wikipedia2book; MediaWiki API client)"


class MediaWikiError(Exception):
    pass


class MediaWikiPageNotFound(MediaWikiError):
    pass


def validate_language(language: str) -> str:
    normalized = language.lower()
    if not _LANGUAGE_RE.fullmatch(normalized):
        raise ValueError("Code de langue Wikipédia invalide.")
    return normalized


def article_url(language: str, title: str) -> str:
    language = validate_language(language)
    slug = quote(title.replace(" ", "_"), safe="()!$&'*,;=:@")
    return f"https://{language}.wikipedia.org/wiki/{slug}"


def parse_article_url(url: str) -> tuple[str, str]:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    match = re.fullmatch(r"([a-z0-9-]{2,12})\.wikipedia\.org", host)
    if parsed.scheme != "https" or not match or parsed.port is not None:
        raise ValueError("L’URL doit pointer vers un article HTTPS de wikipedia.org.")
    language = validate_language(match.group(1))
    if parsed.path.startswith("/wiki/"):
        title = unquote(parsed.path.removeprefix("/wiki/")).replace("_", " ")
    elif parsed.path == "/w/index.php":
        title = parse_qs(parsed.query).get("title", [""])[0].replace("_", " ")
    else:
        title = ""
    if not title or len(title) > 300:
        raise ValueError("L’URL ne contient pas de titre d’article valide.")
    return language, title


class MediaWikiClient:
    def __init__(self, timeout: float = 20.0) -> None:
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "MediaWikiClient":
        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            headers={"User-Agent": _USER_AGENT},
        )
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _get(self, language: str, params: dict) -> dict:
        language = validate_language(language)
        if self._client is None:
            raise RuntimeError("MediaWikiClient doit être utilisé dans un bloc async with.")
        query = {"action": "query", "format": "json", "formatversion": 2, **params}
        try:
            response = await self._client.get(
                f"https://{language}.wikipedia.org/w/api.php", params=query
            )
            response.raise_for_status()
            result = response.json()
        except (httpx.HTTPError, ValueError) as error:
            raise MediaWikiError("Impossible de joindre l’API Wikipédia.") from error
        if "error" in result:
            raise MediaWikiError(result["error"].get("info", "Erreur de l’API Wikipédia."))
        return result

    async def search(self, query: str, language: str = "fr", limit: int = 10) -> list[dict]:
        result = await self._get(
            language,
            {
                "list": "search",
                "srsearch": query,
                "srlimit": min(max(limit, 1), 20),
                "srnamespace": 0,
            },
        )
        items = result.get("query", {}).get("search", [])
        return [
            {
                "page_id": item["pageid"],
                "title": item["title"],
                "snippet": BeautifulSoup(item.get("snippet", ""), "html.parser").get_text(" ", strip=True),
                "url": f"https://{validate_language(language)}.wikipedia.org/wiki/{item['title'].replace(' ', '_')}",
            }
            for item in items
        ]

    async def get_article_pdf(self, title: str, language: str = "fr") -> bytes:
        language = validate_language(language)
        if self._client is None:
            raise RuntimeError("MediaWikiClient doit être utilisé dans un bloc async with.")
        page_path = quote(title.replace(" ", "_"), safe="")
        url = f"https://{language}.wikipedia.org/api/rest_v1/page/pdf/{page_path}"
        try:
            response = await self._client.get(url, timeout=120)
            response.raise_for_status()
        except httpx.HTTPError as error:
            raise MediaWikiError(f"Impossible de télécharger le PDF Wikipédia pour « {title} ».") from error
        if response.content[:5] != b"%PDF-":
            raise MediaWikiError(f"Wikipédia n’a pas renvoyé un PDF valide pour « {title} ».")
        return response.content

    async def get_links(self, title: str, language: str = "fr", limit: int = 100) -> list[str]:
        result = await self._get(
            language,
            {
                "prop": "links",
                "titles": title,
                "plnamespace": 0,
                "pllimit": min(max(limit, 1), 500),
            },
        )
        pages = result.get("query", {}).get("pages", [])
        return [link["title"] for page in pages for link in page.get("links", [])]

    async def get_book_links(
        self, title: str, language: str = "fr", limit: int = 200
    ) -> list[str]:
        language = validate_language(language)
        remaining = min(max(limit, 1), 500)
        params = {
            "prop": "info|links",
            "titles": title,
            "inprop": "url",
            "plnamespace": 0,
            "pllimit": min(remaining, 500),
        }
        links: list[str] = []
        seen: set[str] = set()
        first_page = True

        while remaining:
            result = await self._get(language, params)
            pages = result.get("query", {}).get("pages", [])
            if first_page and (not pages or pages[0].get("missing")):
                raise MediaWikiPageNotFound(
                    f"La page de livre Wikipédia « {title} » est introuvable."
                )
            first_page = False
            for page in pages:
                for link in page.get("links", []):
                    link_title = link.get("title", "")
                    normalized = link_title.casefold()
                    if link_title and normalized not in seen:
                        links.append(link_title)
                        seen.add(normalized)
                        remaining -= 1
                        if remaining == 0:
                            break
                if remaining == 0:
                    break
            continuation = result.get("continue")
            if not continuation or remaining == 0:
                break
            params.update(continuation)
            params["pllimit"] = min(remaining, 500)
        return links
