import asyncio

from app.models import Article
from app.wikipedia_api import MediaWikiClient


async def discover_related_articles(
    client: MediaWikiClient,
    seeds: list[Article],
    max_depth: int = 1,
    max_articles: int = 30,
) -> list[Article]:
    if max_depth <= 0 or max_articles <= 0:
        return []

    seen = {(article.language, article.title.casefold()) for article in seeds}
    frontier = [(article.language, article.title, article.title, 0) for article in seeds]
    discovered: list[Article] = []

    for depth in range(1, max_depth + 1):
        candidates: dict[tuple[str, str], tuple[str, str]] = {}
        next_frontier: list[tuple[str, str, str, int]] = []
        for language, source_title, origin_title, _ in frontier:
            for title in await client.get_links(source_title, language):
                key = (language, title.casefold())
                if key in seen or key in candidates:
                    continue
                candidates[key] = (title, origin_title)
                if len(discovered) + len(candidates) >= max_articles:
                    break
            await asyncio.sleep(0.1)
            if len(discovered) + len(candidates) >= max_articles:
                break

        by_language: dict[str, list[tuple[str, str]]] = {}
        for (language, _), candidate in candidates.items():
            by_language.setdefault(language, []).append(candidate)

        for language, language_candidates in by_language.items():
            fetched = await client.get_articles_by_titles(
                [title for title, _ in language_candidates], language
            )
            by_title = {article.title.casefold(): article for article in fetched}
            for requested_title, origin_title in language_candidates:
                key = (language, requested_title.casefold())
                seen.add(key)
                article = by_title.get(requested_title.casefold())
                if article is None:
                    continue
                article.origin_title = origin_title
                article.depth = depth
                article.selected = False
                discovered.append(article)
                next_frontier.append((language, article.title, origin_title, depth))
                if len(discovered) >= max_articles:
                    return discovered
        frontier = next_frontier
        if not frontier:
            break
    return discovered
