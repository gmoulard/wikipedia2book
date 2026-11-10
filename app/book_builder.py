from datetime import date
from html import escape

from app.models import Article, Project, UploadedDocument

BookItem = Article | UploadedDocument

_PAGE_SIZES = {
    "A0": (841, 1189), "A1": (594, 841), "A2": (420, 594),
    "A3": (297, 420), "A4": (210, 297), "A5": (148, 210),
    "A6": (105, 148), "Letter": (216, 279), "Legal": (216, 356),
}

PDF_LABELS = {
    "fr": {"introduction": "Introduction", "toc": "Table des matières", "chapter": "Chapitre", "conclusion": "Conclusion", "license": "Licence", "no_chapter": "Sans chapitre", "edition": "Édition du {date}", "sources": "Sources et auteurs", "history": "Historique et auteurs :"},
    "en": {"introduction": "Introduction", "toc": "Table of contents", "chapter": "Chapter", "conclusion": "Conclusion", "license": "License", "no_chapter": "No chapter", "edition": "Edition of {date}", "sources": "Sources and authors", "history": "History and authors:"},
    "es": {"introduction": "Introducción", "toc": "Índice", "chapter": "Capítulo", "conclusion": "Conclusión", "license": "Licencia", "no_chapter": "Sin capítulo", "edition": "Edición del {date}", "sources": "Fuentes y autores", "history": "Historial y autores:"},
    "pt": {"introduction": "Introdução", "toc": "Sumário", "chapter": "Capítulo", "conclusion": "Conclusão", "license": "Licença", "no_chapter": "Sem capítulo", "edition": "Edição de {date}", "sources": "Fontes e autores", "history": "Histórico e autores:"},
    "it": {"introduction": "Introduzione", "toc": "Indice", "chapter": "Capitolo", "conclusion": "Conclusione", "license": "Licenza", "no_chapter": "Senza capitolo", "edition": "Edizione del {date}", "sources": "Fonti e autori", "history": "Cronologia e autori:"},
    "de": {"introduction": "Einleitung", "toc": "Inhaltsverzeichnis", "chapter": "Kapitel", "conclusion": "Schlusswort", "license": "Lizenz", "no_chapter": "Ohne Kapitel", "edition": "Ausgabe vom {date}", "sources": "Quellen und Autoren", "history": "Versionsgeschichte und Autoren:"},
    "nl": {"introduction": "Inleiding", "toc": "Inhoudsopgave", "chapter": "Hoofdstuk", "conclusion": "Conclusie", "license": "Licentie", "no_chapter": "Zonder hoofdstuk", "edition": "Editie van {date}", "sources": "Bronnen en auteurs", "history": "Geschiedenis en auteurs:"},
    "tr": {"introduction": "Giriş", "toc": "İçindekiler", "chapter": "Bölüm", "conclusion": "Sonuç", "license": "Lisans", "no_chapter": "Bölümsüz", "edition": "{date} baskısı", "sources": "Kaynaklar ve yazarlar", "history": "Geçmiş ve yazarlar:"},
    "zh": {"introduction": "引言", "toc": "目录", "chapter": "章", "conclusion": "结语", "license": "许可协议", "no_chapter": "未分章", "edition": "{date} 版", "sources": "来源与作者", "history": "历史与作者："},
    "ja": {"introduction": "はじめに", "toc": "目次", "chapter": "章", "conclusion": "おわりに", "license": "ライセンス", "no_chapter": "章なし", "edition": "{date} 版", "sources": "出典と著者", "history": "履歴と著者："},
    "ar": {"introduction": "مقدمة", "toc": "جدول المحتويات", "chapter": "الفصل", "conclusion": "خاتمة", "license": "الترخيص", "no_chapter": "بدون فصل", "edition": "طبعة {date}", "sources": "المصادر والمؤلفون", "history": "السجل والمؤلفون:"},
    "fa": {"introduction": "مقدمه", "toc": "فهرست مطالب", "chapter": "فصل", "conclusion": "نتیجه‌گیری", "license": "مجوز", "no_chapter": "بدون فصل", "edition": "ویرایش {date}", "sources": "منابع و نویسندگان", "history": "تاریخچه و نویسندگان:"},
}
RTL_LANGUAGES = {"ar", "fa"}


def pdf_label(language: str, key: str, **values: str) -> str:
    return PDF_LABELS[language][key].format(**values)


def _html_attrs(language: str) -> str:
    direction = "rtl" if language in RTL_LANGUAGES else "ltr"
    return f'lang="{language}" dir="{direction}"'



def ordered_article_groups(
    project: Project, items: list[BookItem], language: str = "fr"
) -> list[tuple[str, list[BookItem]]]:
    by_key = {item.key: item for item in items}
    ordered = [by_key[key] for key in project.article_order if key in by_key]
    used_keys = {item.key for item in ordered}
    ordered.extend(item for item in items if item.key not in used_keys)

    groups: list[tuple[str, list[BookItem]]] = []
    assigned: set[str] = set()
    for chapter in project.chapters:
        chapter_items = [item for item in ordered if item.key in chapter.article_keys]
        assigned.update(item.key for item in chapter_items)
        if chapter_items:
            groups.append((chapter.title, chapter_items))
    if not project.chapters:
        groups = [("", ordered)]
    else:
        unassigned = [item for item in ordered if item.key not in assigned]
        if unassigned:
            groups.append((pdf_label(language, "no_chapter"), unassigned))
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


def page_size_mm(project: Project) -> tuple[float, float]:
    width, height, *_ = _page_layout(project)
    return width, height


def build_cover_html(project: Project, language: str = "fr") -> str:
    page_width, page_height, margin_top, margin_bottom, inner, outer = _page_layout(project)
    book_title = escape(project.book_title or project.name)
    subtitle = f'<p class="subtitle">{escape(project.book_subtitle)}</p>' if project.book_subtitle else ""
    author = f'<p class="author">{escape(project.book_author)}</p>' if project.book_author else ""
    introduction_text = escape(project.introduction).replace("\n", "<br>")
    introduction = (
        f'<section class="opening"><h2>{pdf_label(language, "introduction")}</h2><p>{introduction_text}</p></section>'
        if project.introduction else ""
    )
    description = escape(project.description)
    return f"""<!doctype html>
    <html {_html_attrs(language)}>
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
.opening {{ page-break-after: always; }}
    </style>
    </head>
    <body>
<header class="cover"><h1>{book_title}</h1>{subtitle}{author}<p class="cover-note">{description}</p><p class="cover-note">{escape(pdf_label(language, 'edition', date=date.today().strftime('%d/%m/%Y')))}</p></header>
{introduction}
    </body>
    </html>"""


def build_toc_html(
    project: Project,
    items: list[BookItem],
    article_pages: dict[str, int] | None = None,
    chapter_pages: list[int | None] | None = None,
    language: str = "fr",
) -> str:
    groups = ordered_article_groups(project, items, language)
    article_pages = article_pages or {}
    chapter_pages = chapter_pages or [None] * len(groups)

    def entry(label: str, page: int | None) -> str:
        page_span = f'<span class="page-no">{page}</span>' if page else ""
        return f"<li><span>{label}</span>{page_span}</li>"

    contents: list[str] = []
    for index, (chapter_title, chapter_items) in enumerate(groups):
        titles = [entry(escape(item.title), article_pages.get(item.key)) for item in chapter_items]
        if chapter_title:
            chapter_page = chapter_pages[index] if index < len(chapter_pages) else None
            page_span = f'<span class="page-no">{chapter_page}</span>' if chapter_page else ""
            contents.append(
                f'<li><span>{escape(chapter_title)}</span>{page_span}<ol>{"".join(titles)}</ol></li>'
            )
        else:
            contents.extend(titles)

    page_width, page_height, margin_top, margin_bottom, inner, outer = _page_layout(project)
    return f"""<!doctype html>
    <html {_html_attrs(language)}>
    <head>
    <meta charset="utf-8">
    <style>
@page {{ size: {page_width:g}mm {page_height:g}mm; margin: {margin_top:g}mm {outer:g}mm {margin_bottom:g}mm {inner:g}mm; }}
@page :left {{ margin-left: {inner:g}mm; margin-right: {outer:g}mm; }}
@page :right {{ margin-left: {outer:g}mm; margin-right: {inner:g}mm; }}
    body {{ color: #202020; font: 10pt serif; line-height: 1.5; }}
    h2 {{ font-size: 18pt; line-height: 1.2; }}
nav ol {{ padding-left: 18pt; list-style: none; }}
nav ol ol {{ margin: 2pt 0 5pt; }}
nav li {{ display: flex; justify-content: space-between; gap: 8pt; }}
.page-no {{ flex: 0 0 auto; color: #555; }}
    </style>
    </head>
    <body>
    <nav><h2>{pdf_label(language, 'toc')}</h2><ol>{''.join(contents)}</ol></nav>
    </body>
    </html>"""


def build_chapter_page_html(project: Project, title: str, language: str = "fr") -> str:
    page_width, page_height, margin_top, margin_bottom, inner, outer = _page_layout(project)
    return f"""<!doctype html>
<html {_html_attrs(language)}><head><meta charset="utf-8"><style>
@page {{ size: {page_width:g}mm {page_height:g}mm; margin: {margin_top:g}mm {outer:g}mm {margin_bottom:g}mm {inner:g}mm; }}
@page :left {{ margin-left: {inner:g}mm; margin-right: {outer:g}mm; }}
@page :right {{ margin-left: {outer:g}mm; margin-right: {inner:g}mm; }}
body {{ color: #202020; font: 11pt serif; }}
main {{ display: flex; min-height: 75vh; flex-direction: column; justify-content: center; }}
p {{ color: #167465; font: bold 9pt sans-serif; letter-spacing: 1pt; text-transform: uppercase; }}
p:lang(ar), p:lang(fa) {{ letter-spacing: 0; }}
h1 {{ font-size: 30pt; }}
</style></head><body><main><p>{pdf_label(language, 'chapter')}</p><h1>{escape(title)}</h1></main></body></html>"""


def build_conclusion_page_html(project: Project, language: str = "fr") -> str:
    page_width, page_height, margin_top, margin_bottom, inner, outer = _page_layout(project)
    conclusion = escape(project.conclusion).replace("\n", "<br>")
    return f"""<!doctype html>
<html {_html_attrs(language)}><head><meta charset="utf-8"><style>
@page {{ size: {page_width:g}mm {page_height:g}mm; margin: {margin_top:g}mm {outer:g}mm {margin_bottom:g}mm {inner:g}mm; }}
@page :left {{ margin-left: {inner:g}mm; margin-right: {outer:g}mm; }}
@page :right {{ margin-left: {outer:g}mm; margin-right: {inner:g}mm; }}
body {{ color: #202020; font: 11pt serif; line-height: 1.6; }}
h1 {{ font-size: 22pt; }}
</style></head><body><h1>{pdf_label(language, 'conclusion')}</h1><p>{conclusion}</p></body></html>"""


def _history_url(article: Article) -> str:
    return article.url.replace("/wiki/", "/w/index.php?title=", 1) + "&action=history"


def build_license_page_html(project: Project, items: list[BookItem], language: str = "fr") -> str:
    page_width, page_height, margin_top, margin_bottom, inner, outer = _page_layout(project)
    groups = ordered_article_groups(project, items, language)
    ordered = list({item.key: item for _, group in groups for item in group}.values())
    articles = [item for item in ordered if isinstance(item, Article)]
    documents = [item for item in ordered if isinstance(item, UploadedDocument)]
    sources = "".join(
        f'<li><strong>{escape(article.title)}</strong><br>{escape(article.url)}<br>'
        f'{escape(pdf_label(language, "history"))} {escape(_history_url(article))}</li>'
        for article in articles
    )
    sources_section = (
        f'<h2 {_html_attrs(language)}>{pdf_label(language, "sources")}</h2><ol>{sources}</ol>' if articles else ""
    )
    documents_note = (
        "<p>Les documents importés ("
        + ", ".join(escape(document.title) for document in documents)
        + ") ne proviennent pas de Wikipédia et ne sont pas couverts par cette licence.</p>"
        if documents else ""
    )
    return f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><style>
@page {{ size: {page_width:g}mm {page_height:g}mm; margin: {margin_top:g}mm {outer:g}mm {margin_bottom:g}mm {inner:g}mm; }}
@page :left {{ margin-left: {inner:g}mm; margin-right: {outer:g}mm; }}
@page :right {{ margin-left: {outer:g}mm; margin-right: {inner:g}mm; }}
body {{ color: #202020; font: 10pt serif; line-height: 1.5; }}
h1 {{ font-size: 22pt; }}
h2 {{ font-size: 14pt; margin-top: 18pt; }}
ol {{ padding-left: 18pt; font-size: 9pt; }}
li {{ margin-bottom: 6pt; overflow-wrap: anywhere; }}
.license-name {{ font-weight: bold; }}
</style></head><body>
<h1 {_html_attrs(language)}>{pdf_label(language, 'license')}</h1>
<p>Les textes des articles Wikipédia reproduits dans ce livre sont publiés sous licence
<span class="license-name">Creative Commons Attribution – Partage dans les mêmes conditions 4.0 International (CC BY-SA 4.0)</span> :
https://creativecommons.org/licenses/by-sa/4.0/deed.fr</p>
<p>Vous êtes libre de partager et d'adapter ce contenu, y compris à des fins commerciales, à condition de créditer
les auteurs, d'indiquer la licence et si des modifications ont été apportées, et de diffuser toute adaptation
sous la même licence.</p>
<p>Les images et médias conservent leurs propres licences, indiquées dans chaque article.</p>
{documents_note}
<p>Ce livre n'est pas une publication officielle de Wikipédia ni de la Wikimedia Foundation.</p>
{sources_section}
</body></html>"""
