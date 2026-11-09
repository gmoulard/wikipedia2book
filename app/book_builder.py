from datetime import date
from html import escape

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
    article_pages: dict[str, int] | None = None,
    chapter_pages: list[int | None] | None = None,
) -> str:
    groups = ordered_article_groups(project, articles)
    article_pages = article_pages or {}
    chapter_pages = chapter_pages or [None] * len(groups)

    def entry(label: str, page: int | None) -> str:
        page_span = f'<span class="page-no">{page}</span>' if page else ""
        return f"<li><span>{label}</span>{page_span}</li>"

    contents: list[str] = []
    for index, (chapter_title, chapter_articles) in enumerate(groups):
        titles = [entry(escape(article.title), article_pages.get(article.key)) for article in chapter_articles]
        if chapter_title:
            chapter_page = chapter_pages[index] if index < len(chapter_pages) else None
            page_span = f'<span class="page-no">{chapter_page}</span>' if chapter_page else ""
            contents.append(
                f'<li><span>{escape(chapter_title)}</span>{page_span}<ol>{"".join(titles)}</ol></li>'
            )
        else:
            contents.extend(titles)

    page_width, page_height, margin_top, margin_bottom, inner, outer = _page_layout(project)
    book_title = escape(project.book_title or project.name)
    subtitle = f'<p class="subtitle">{escape(project.book_subtitle)}</p>' if project.book_subtitle else ""
    author = f'<p class="author">{escape(project.book_author)}</p>' if project.book_author else ""
    introduction_text = escape(project.introduction).replace("\n", "<br>")
    introduction = (
        f'<section class="opening"><h2>Introduction</h2><p>{introduction_text}</p></section>'
        if project.introduction else ""
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
    h1, h2 {{ line-height: 1.2; }}
h1 {{ font-size: 26pt; }}
h2 {{ font-size: 18pt; }}
.cover {{ display: flex; min-height: 65vh; flex-direction: column; justify-content: center; page-break-after: always; }}
.cover h1 {{ max-width: 90%; margin-bottom: 8pt; }}
.subtitle {{ margin: 0; font-size: 15pt; }}
.author {{ margin-top: 32pt; color: #555; }}
.cover-note {{ margin-top: 20pt; color: #555; font-size: 9pt; }}
.opening, nav {{ page-break-after: always; }}
nav ol {{ padding-left: 18pt; list-style: none; }}
nav ol ol {{ margin: 2pt 0 5pt; }}
nav li {{ display: flex; justify-content: space-between; gap: 8pt; }}
.page-no {{ flex: 0 0 auto; color: #555; }}
    </style>
    </head>
    <body>
<header class="cover"><h1>{book_title}</h1>{subtitle}{author}<p class="cover-note">{description}</p><p class="cover-note">Édition du {date.today().strftime('%d/%m/%Y')}</p></header>
{introduction}
    <nav><h2>Table des matières</h2><ol>{''.join(contents)}</ol></nav>
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
