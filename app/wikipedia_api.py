import re
from dataclasses import dataclass
from urllib.parse import parse_qs, quote, unquote, urlparse

import httpx
from bs4 import BeautifulSoup

from app.models import Article


_LANGUAGE_RE = re.compile(r"^[a-z0-9-]{2,12}$")
WIKIPEDIA_PDF_PAPERS = {"A4": "a4", "Letter": "letter", "Legal": "legal"}
_USER_AGENT ="Wikipedia2Book/0.1 (https://github.com/gmoulard/wikipedia2book; MediaWiki API client)"


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

    async def get_page(self, title: str, language: str = "fr") -> tuple[str, int] | None:
        result = await self._get(language, {"prop": "info", "titles": title, "redirects": 1})
        pages = result.get("query", {}).get("pages", [])
        if not pages or pages[0].get("missing") or pages[0].get("invalid"):
            return None
        return pages[0]["title"], pages[0]["ns"]

    async def get_intro_and_creator(self, title: str, language: str = "fr") -> tuple[str, str]:
        extract_result = await self._get(
            language, {"prop": "extracts", "exintro": 1, "explaintext": 1, "titles": title}
        )
        pages = extract_result.get("query", {}).get("pages", [])
        introduction = pages[0].get("extract", "") if pages and not pages[0].get("missing") else ""

        creator_result = await self._get(
            language, {"prop": "revisions", "rvlimit": 1, "rvdir": "newer", "rvprop": "user", "titles": title}
        )
        rev_pages = creator_result.get("query", {}).get("pages", [])
        revisions = rev_pages[0].get("revisions", []) if rev_pages else []
        creator = revisions[0].get("user", "") if revisions else ""

        return introduction, creator

    async def get_article_pdf(self, title: str, language: str, paper: str) -> bytes:
        language = validate_language(language)
        if paper not in WIKIPEDIA_PDF_PAPERS.values():
            raise ValueError("Format de PDF Wikipédia invalide.")
        if self._client is None:
            raise RuntimeError("MediaWikiClient doit être utilisé dans un bloc async with.")
        page_path = quote(title.replace(" ", "_"), safe="")
        url = f"https://{language}.wikipedia.org/api/rest_v1/page/pdf/{page_path}/{paper}"
        try:
            response = await self._client.get(url, timeout=120)
            response.raise_for_status()
        except httpx.HTTPError as error:
            raise MediaWikiError(f"Impossible de télécharger le PDF Wikipédia pour « {title} ».") from error
        if response.content[:5] != b"%PDF-":
            raise MediaWikiError(f"Wikipédia n’a pas renvoyé un PDF valide pour « {title} ».")
        return response.content

    async def get_links(self, title: str, language: str = "fr") -> list[str]:
        result = await self._get(
            language,
            {"action": "parse", "page": title, "prop": "text", "redirects": 1, "disabletoc": 1},
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

    async def get_book(self, title: str, language: str = "fr", limit: int = 200) -> WikipediaBook:
        language = validate_language(language)
        limit = min(max(limit, 1), 500)
        result = await self._get(
            language,
            {"prop": "revisions", "titles": title, "rvprop": "content", "rvslots": "main"},
        )
        pages = result.get("query", {}).get("pages", [])
        if not pages or pages[0].get("missing"):
            raise MediaWikiPageNotFound(f"La page de livre Wikipédia « {title} » est introuvable.")
        revisions = pages[0].get("revisions", [])
        content = revisions[0].get("slots", {}).get("main", {}).get("content", "") if revisions else ""

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


def _plain_wikitext(text: str) -> str:
    text = re.sub(r"\[\[(?:[^\[\]|]*\|)?([^\[\]]*)\]\]", r"\1", text)
    return re.sub(r"'{2,}", "", text).strip()
