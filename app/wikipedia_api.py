import re
from urllib.parse import parse_qs, unquote, urlparse

import httpx
from bs4 import BeautifulSoup

from app.models import Article


_LANGUAGE_RE = re.compile(r"^[a-z0-9-]{2,12}$")
_USER_AGENT = "Wikipedia2Book/0.1 (https://github.com/gmoulard/wikipedia2book; MediaWiki API client)"


class MediaWikiError(Exception):
    pass


def validate_language(language: str) -> str:
    normalized = language.lower()
    if not _LANGUAGE_RE.fullmatch(normalized):
        raise ValueError("Code de langue Wikipédia invalide.")
    return normalized


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

    async def get_article(self, title: str, language: str = "fr") -> Article:
        articles = await self.get_articles_by_titles([title], language)
        if not articles:
            raise MediaWikiError("Article Wikipédia introuvable.")
        return articles[0]

    async def get_articles_by_titles(self, titles: list[str], language: str = "fr") -> list[Article]:
        language = validate_language(language)
        articles: list[Article] = []
        for start in range(0, len(titles), 50):
            batch = titles[start : start + 50]
            result = await self._get(
                language,
                {
                    "prop": "extracts|info|revisions",
                    "inprop": "url",
                    "exchars": 30000,
                    "explaintext": 0,
                    "rvprop": "timestamp",
                    "rvlimit": 1,
                    "redirects": 1,
                    "titles": "|".join(batch),
                },
            )
            for page in result.get("query", {}).get("pages", []):
                if page.get("missing") or "pageid" not in page:
                    continue
                revisions = page.get("revisions", [])
                articles.append(
                    Article(
                        page_id=page["pageid"],
                        title=page["title"],
                        language=language,
                        url=page.get("fullurl")
                        or f"https://{language}.wikipedia.org/wiki/{page['title'].replace(' ', '_')}",
                        summary=BeautifulSoup(page.get("extract", ""), "html.parser").get_text(" ", strip=True)[:1000],
                        last_modified=revisions[0].get("timestamp") if revisions else None,
                        content_html=page.get("extract", ""),
                    )
                )
        return articles

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
