from datetime import date
from html import escape

from app.article_parser import sanitize_html
from app.models import Article, Project


_PAGE_SIZES = {
    "A0": (841, 1189), "A1": (594, 841), "A2": (420, 594),
    "A3": (297, 420), "A4": (210, 297), "A5": (148, 210),
    "A6": (105, 148), "Letter": (216, 279), "Legal": (216, 356),
}


def ordered_article_groups(project: Project, articles: list[Article]) -> list[tuple[str, list[Article]]]:
    by_key = {article.key: article for article in articles}
    ordered = [by_key[key] for key in project.article_order if key in by_key]
    used_keys = {article.key for article in ordered}
    ordered.extend(article for article in articles if article.key not in used_keys)

    groups: list[tuple[str, list[Article]]] = []
    assigned: set[str] = set()
    for chapter in project.chapters:
        chapter_articles = [article for article in ordered if article.key in chapter.article_keys]
        assigned.update(article.key for article in chapter_articles)
        if chapter_articles:
            groups.append((chapter.title, chapter_articles))
    if not project.chapters:
        groups = [("", ordered)]
    else:
        unassigned = [article for article in ordered if article.key not in assigned]
        if unassigned:
            groups.append(("Sans chapitre", unassigned))
    return groups


def _page_layout(project: Project) -> tuple[float, float, float, float, float, float]:
    page_width, page_height = _PAGE_SIZES.get(
        project.page_format, (project.custom_width_mm, project.custom_height_mm)
    )
    if project.page_format == "custom":
        page_width, page_height = project.custom_width_mm, project.custom_height_mm
    if project.orientation == "landscape":
        page_width, page_height = page_height, page_width
    inner = project.margin_inside_mm + project.margin_binding_mm
    return page_width, page_height, project.margin_top_mm, project.margin_bottom_mm, inner, project.margin_outside_mm


def build_book_html(
    project: Project,
    articles: list[Article],
    *,
    include_articles: bool = True,
    include_conclusion: bool = True,
) -> str:
    groups = ordered_article_groups(project, articles)

    sections: list[str] = []
    contents: list[str] = []
    index = 0
    for chapter_title, chapter_articles in groups:
        links: list[str] = []
        if include_articles and chapter_title:
            sections.append(f'<section class="chapter"><h2>{escape(chapter_title)}</h2>')
        for article in chapter_articles:
            index += 1
            anchor = f"article-{index}"
            title = escape(article.title)
            link = f'<a href="#{anchor}">{title}</a>' if include_articles else title
            links.append(f"<li>{link}</li>")
            if not include_articles:
                continue
            body = sanitize_html(
                article.content_html or f"<p>{escape(article.summary)}</p>", article.language
            )
            references = sanitize_html(article.references_html, article.language)
            reference_section = (
                f'<section class="references"><h4>Références</h4>{references}</section>'
                if references else ""
            )
            heading = "h3" if chapter_title else "h2"
            sections.append(
                f'<article id="{anchor}" class="article"><{heading}>{title}</{heading}>{body}'
                f'{reference_section}<p class="source">Source : '
                f'<a href="{escape(article.url, quote=True)}">{escape(article.url)}</a></p></article>'
            )
        if chapter_title:
            contents.append(
                f'<li><span>{escape(chapter_title)}</span><ol>{"".join(links)}</ol></li>'
            )
            if include_articles:
                sections.append("</section>")
        else:
            contents.extend(links)

    page_width, page_height, margin_top, margin_bottom, inner, outer = _page_layout(project)
    book_title = escape(project.book_title or project.name)
    subtitle = f'<p class="subtitle">{escape(project.book_subtitle)}</p>' if project.book_subtitle else ""
    author = f'<p class="author">{escape(project.book_author)}</p>' if project.book_author else ""
    introduction_text = escape(project.introduction).replace("\n", "<br>")
    conclusion_text = escape(project.conclusion).replace("\n", "<br>")
    introduction = (
        f'<section class="opening"><h2>Introduction</h2><p>{introduction_text}</p></section>'
        if project.introduction else ""
    )
    conclusion = (
        f'<section class="closing"><h2>Conclusion</h2><p>{conclusion_text}</p></section>'
        if project.conclusion and include_conclusion else ""
    )
    description = escape(project.description)
    return f"""<!doctype html>
    <html lang="fr">
    <head>
    <meta charset="utf-8">
<title>{book_title}</title>
    <style>
@page {{ size: {page_width:g}mm {page_height:g}mm; margin: {margin_top:g}mm {outer:g}mm {margin_bottom:g}mm {inner:g}mm; }}
@page :left {{ margin-left: {inner:g}mm; margin-right: {outer:g}mm; }}
@page :right {{ margin-left: {outer:g}mm; margin-right: {inner:g}mm; }}
    body {{ color: #202020; font: 10pt serif; line-height: 1.5; }}
    h1, h2, h3 {{ line-height: 1.2; }}
h1 {{ font-size: 26pt; }}
h2 {{ font-size: 18pt; }}
h3 {{ font-size: 14pt; }}
h4 {{ font-size: 12pt; }}
    a {{ color: #245c73; overflow-wrap: anywhere; }}
    img {{ max-width: 100%; height: auto; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 8pt; }}
    th, td {{ border: 0.5pt solid #888; padding: 3pt; }}
.cover {{ display: flex; min-height: 65vh; flex-direction: column; justify-content: center; page-break-after: always; }}
.cover h1 {{ max-width: 90%; margin-bottom: 8pt; }}
.subtitle {{ margin: 0; font-size: 15pt; }}
.author {{ margin-top: 32pt; color: #555; }}
.cover-note {{ margin-top: 20pt; color: #555; font-size: 9pt; }}
.opening, nav {{ page-break-after: always; }}
nav h2 {{ page-break-before: auto; }}
nav ol {{ padding-left: 18pt; }}
nav ol ol {{ margin: 2pt 0 5pt; }}
.chapter {{ page-break-before: always; }}
.chapter > h2 {{ margin-bottom: 20pt; }}
.chapter .article h3 {{ page-break-before: auto; }}
.references, .source {{ font-size: 8pt; }}
.closing {{ page-break-before: always; }}
    </style>
    </head>
    <body>
<header class="cover"><h1>{book_title}</h1>{subtitle}{author}<p class="cover-note">{description}</p><p class="cover-note">Édition du {date.today().strftime('%d/%m/%Y')}</p></header>
{introduction}
    <nav><h2>Table des matières</h2><ol>{''.join(contents)}</ol></nav>
    {''.join(sections)}
{conclusion}
    </body>
    </html>"""


def build_chapter_page_html(project: Project, title: str) -> str:
    page_width, page_height, margin_top, margin_bottom, inner, outer = _page_layout(project)
    return f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><style>
@page {{ size: {page_width:g}mm {page_height:g}mm; margin: {margin_top:g}mm {outer:g}mm {margin_bottom:g}mm {inner:g}mm; }}
@page :left {{ margin-left: {inner:g}mm; margin-right: {outer:g}mm; }}
@page :right {{ margin-left: {outer:g}mm; margin-right: {inner:g}mm; }}
body {{ color: #202020; font: 11pt serif; }}
main {{ display: flex; min-height: 75vh; flex-direction: column; justify-content: center; }}
p {{ color: #167465; font: bold 9pt sans-serif; letter-spacing: 1pt; }}
h1 {{ font-size: 30pt; }}
</style></head><body><main><p>CHAPITRE</p><h1>{escape(title)}</h1></main></body></html>"""


def build_conclusion_page_html(project: Project) -> str:
    page_width, page_height, margin_top, margin_bottom, inner, outer = _page_layout(project)
    conclusion = escape(project.conclusion).replace("\n", "<br>")
    return f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><style>
@page {{ size: {page_width:g}mm {page_height:g}mm; margin: {margin_top:g}mm {outer:g}mm {margin_bottom:g}mm {inner:g}mm; }}
@page :left {{ margin-left: {inner:g}mm; margin-right: {outer:g}mm; }}
@page :right {{ margin-left: {outer:g}mm; margin-right: {inner:g}mm; }}
body {{ color: #202020; font: 11pt serif; line-height: 1.6; }}
h1 {{ font-size: 22pt; }}
</style></head><body><h1>Conclusion</h1><p>{conclusion}</p></body></html>"""
