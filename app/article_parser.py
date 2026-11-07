from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup


_ALLOWED_TAGS = {
    "a", "blockquote", "br", "caption", "dd", "div", "dl", "dt", "em", "figcaption",
    "figure", "h1", "h2", "h3", "h4", "h5", "h6", "hr", "i", "img", "li", "ol",
    "p", "small", "span", "strong", "sub", "sup", "table", "tbody", "td", "th", "thead",
    "tr", "u", "ul",
}
_REMOVED_SELECTORS = (
    ".mw-editsection", ".navbox", ".metadata", ".catlinks", ".printfooter", ".noprint",
    ".mw-jump-link", ".mw-empty-elt",
)


def sanitize_html(fragment: str, language: str = "fr") -> str:
    soup = BeautifulSoup(fragment or "", "html.parser")
    for node in soup.select("script, style, iframe, object, embed, form, input, button, svg, math"):
        node.decompose()
    for node in soup.select(", ".join(_REMOVED_SELECTORS)):
        node.decompose()

    base_url = f"https://{language}.wikipedia.org/"
    for tag in list(soup.find_all(True)):
        if tag.name not in _ALLOWED_TAGS:
            tag.unwrap()
            continue
        original_href = tag.get("href")
        original_src = tag.get("src")
        attributes = {key: value for key, value in tag.attrs.items() if key in {"href", "src", "alt", "title", "colspan", "rowspan"}}
        tag.attrs = attributes
        if original_href is not None and tag.name == "a":
            href = urljoin(base_url, str(original_href))
            scheme = urlparse(href).scheme
            if scheme in {"http", "https", "mailto"}:
                tag["href"] = href
        if original_src is not None and tag.name == "img":
            src = urljoin(base_url, str(original_src))
            parsed_src = urlparse(src)
            if parsed_src.scheme == "https" and (parsed_src.hostname == "upload.wikimedia.org" or (parsed_src.hostname or "").endswith(".wikimedia.org")):
                tag["src"] = src
            else:
                tag.decompose()
    return "".join(str(child) for child in soup.contents)


def extract_article_content(html: str, language: str = "fr") -> tuple[str, str]:
    soup = BeautifulSoup(html or "", "html.parser")
    for node in soup.select(", ".join(_REMOVED_SELECTORS)):
        node.decompose()
    reference_nodes = soup.select("ol.references, div.reflist")
    references_html = "".join(str(node) for node in reference_nodes)
    for node in reference_nodes:
        node.decompose()
    content_html = "".join(str(child) for child in soup.contents)
    return sanitize_html(content_html, language), sanitize_html(references_html, language)
