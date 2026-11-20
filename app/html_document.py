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
import re
from typing import Awaitable, Callable
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from app.json_source import JsonSourceError

HTML_TYPES = {"text/html", "application/xhtml+xml"}
HTML_PAGE_BYTES = 5 * 1024 * 1024
RESOURCE_BYTES = 5 * 1024 * 1024
RESOURCES_TOTAL_BYTES = 20 * 1024 * 1024
MAX_IMAGES = 40
MAX_STYLESHEETS = 10
IMAGE_TYPES = {"image/png", "image/jpeg", "image/gif", "image/webp", "image/svg+xml"}
REMOVED_TAGS = "script, iframe, object, embed, frame, frameset, video, audio, form, noscript, base, meta[http-equiv], template"
CSS_URL = re.compile(r"url\([^)]*\)", re.IGNORECASE)
CSS_IMPORT = re.compile(r"@import[^;]*;?", re.IGNORECASE)

Download = Callable[[str, int, str], Awaitable[tuple[bytes, str]]]


# NE PAS laisser WeasyPrint aller chercher lui-même les images ou les styles de la page : son rendu reste limité aux adresses data: (pdf_generator.RENDER_PROTOCOLS) ; chaque ressource passe par download, qui refuse les adresses internes et limite la taille.
async def html_for_print(page: bytes, url: str, download: Download, width_mm: float, height_mm: float) -> str:
    soup = BeautifulSoup(page, "html.parser")
    for tag in soup.select(REMOVED_TAGS):
        tag.decompose()
    budget = RESOURCES_TOTAL_BYTES
    styles: list[str] = []
    for link in soup.select('link[rel~="stylesheet"][href]')[:MAX_STYLESHEETS]:
        data = await _resource(download, urljoin(url, link["href"]), {"text/css"}, budget)
        if data is not None:
            budget -= len(data)
            styles.append(CSS_IMPORT.sub("", CSS_URL.sub("none", data.decode("utf-8", "replace"))))
    for link in soup.select("link"):
        link.decompose()
    for index, image in enumerate(soup.select("img")):
        source = (image.get("src") or "").strip()
        if source.startswith("data:"):
            continue
        data = await _resource(download, urljoin(url, source), IMAGE_TYPES, budget, with_type=True) if source and index < MAX_IMAGES else None
        if data is None:
            image.decompose()
            continue
        content, content_type = data
        budget -= len(content)
        image["src"] = f"data:{content_type};base64,{base64.b64encode(content).decode('ascii')}"
    for tag in soup.find_all(True):
        for attribute in [name for name in tag.attrs if name.lower().startswith("on") or name.lower() in ("srcset", "sizes")]:
            del tag[attribute]
    if soup.head is None:
        head = soup.new_tag("head")
        (soup.html or soup).insert(0, head)
    page_style = soup.new_tag("style")
    page_style.string = "\n".join(styles)
    soup.head.append(page_style)
    _add_print_style(soup, width_mm, height_mm)
    return str(soup)


# NE PAS abandonner la page web quand WeasyPrint échoue avec ses feuilles de style (issue #4, page d'un dépôt GitHub) : elle est rendue une seconde fois sans elles, le texte et les images comptent plus que la mise en forme.
def without_styles(html: str, width_mm: float, height_mm: float) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.select("style"):
        tag.decompose()
    for tag in soup.find_all(style=True):
        del tag["style"]
    if soup.head is None:
        head = soup.new_tag("head")
        (soup.html or soup).insert(0, head)
    _add_print_style(soup, width_mm, height_mm)
    return str(soup)


def _add_print_style(soup: BeautifulSoup, width_mm: float, height_mm: float) -> None:
    style = soup.new_tag("style")
    style.string = f"@page {{ size: {width_mm:g}mm {height_mm:g}mm; margin: 15mm; }}\nimg, svg, table {{ max-width: 100%; }}\nimg {{ height: auto; }}"
    soup.head.append(style)


async def _resource(download: Download, address: str, accepted: set[str], budget: int, with_type: bool = False):
    if budget <= 0:
        return None
    try:
        data, content_type = await download(address, min(RESOURCE_BYTES, budget), "une ressource de la page")
    except JsonSourceError:
        return None
    if content_type not in accepted:
        return None
    return (data, content_type) if with_type else data
