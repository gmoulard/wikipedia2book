from html import escape

from app.article_parser import sanitize_html
from app.models import Article, Project


def build_book_html(project: Project, articles: list[Article]) -> str:
    sections: list[str] = []
    contents: list[str] = []
    for index, article in enumerate(articles, start=1):
        anchor = f"article-{index}"
        title = escape(article.title)
        contents.append(f'<li><a href="#{anchor}">{title}</a></li>')
        body = sanitize_html(article.content_html or f"<p>{escape(article.summary)}</p>", article.language)
        references = sanitize_html(article.references_html, article.language)
        reference_section = (
            f'<section class="references"><h3>Références</h3>{references}</section>'
            if references
            else ""
        )
        sections.append(
            f'<article id="{anchor}"><h2>{title}</h2>{body}{reference_section}'
            f'<p class="source">Source : <a href="{escape(article.url, quote=True)}">{escape(article.url)}</a></p></article>'
        )

    title = escape(project.name)
    description = escape(project.description)
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
@page {{ size: A5; margin: 18mm 16mm; }}
body {{ color: #202020; font: 10pt serif; line-height: 1.5; }}
h1, h2, h3 {{ line-height: 1.2; }}
h1 {{ font-size: 24pt; }}
h2 {{ font-size: 18pt; page-break-before: always; }}
h3 {{ font-size: 12pt; }}
a {{ color: #245c73; overflow-wrap: anywhere; }}
img {{ max-width: 100%; height: auto; }}
table {{ border-collapse: collapse; width: 100%; font-size: 8pt; }}
th, td {{ border: 0.5pt solid #888; padding: 3pt; }}
.references, .source {{ font-size: 8pt; }}
</style>
</head>
<body>
<header><h1>{title}</h1><p>{description}</p></header>
<nav><h2>Table des matières</h2><ol>{''.join(contents)}</ol></nav>
{''.join(sections)}
</body>
</html>"""
