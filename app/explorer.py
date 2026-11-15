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

from app.models import Article
from app.wikipedia_api import MediaWikiClient, article_url


async def discover_related_articles(
    client: MediaWikiClient,
    seeds: list[Article],
    max_depth: int = 1,
    max_articles: int = 30,
) -> list[Article]:
    if max_depth <= 0 or max_articles <= 0:
        return []

    seen = {(article.site, article.language, article.title.casefold()) for article in seeds}
    frontier = [(article.site, article.language, article.title, article.title) for article in seeds]
    discovered: list[Article] = []

    for depth in range(1, max_depth + 1):
        candidates: dict[tuple[str, str, str], tuple[str, str]] = {}
        next_frontier: list[tuple[str, str, str, str]] = []
        for site, language, source_title, origin_title in frontier:
            for title in await client.get_links(source_title, language, site):
                key = (site, language, title.casefold())
                if key in seen or key in candidates:
                    continue
                candidates[key] = (title, origin_title)
                if len(discovered) + len(candidates) >= max_articles:
                    break
            await asyncio.sleep(0.1)
            if len(discovered) + len(candidates) >= max_articles:
                break

        for (site, language, normalized_title), (title, origin_title) in candidates.items():
            seen.add((site, language, normalized_title))
            article = Article(
                title=title,
                language=language,
                site=site,
                url=article_url(language, title, site),
                origin_title=origin_title,
                depth=depth,
                selected=False,
            )
            discovered.append(article)
            next_frontier.append((site, language, article.title, origin_title))
            if len(discovered) >= max_articles:
                return discovered
        frontier = next_frontier
        if not frontier:
            break
    return discovered
