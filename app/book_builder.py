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
    "fr": {"introduction": "Introduction", "toc": "Table des matières", "chapter": "Chapitre", "conclusion": "Conclusion", "license": "Licence", "no_chapter": "Sans chapitre", "edition": "Édition du {date}", "sources": "Sources et auteurs", "history": "Historique et auteurs :", "license_name": "Creative Commons Attribution – Partage dans les mêmes conditions 4.0 International (CC BY-SA 4.0)", "license_url": "https://creativecommons.org/licenses/by-sa/4.0/deed.fr", "license_intro": "Les textes des articles Wikipédia reproduits dans ce livre sont publiés sous licence {license} :", "license_terms": "Vous êtes libre de partager et d'adapter ce contenu, y compris à des fins commerciales, à condition de créditer les auteurs, d'indiquer la licence et si des modifications ont été apportées, et de diffuser toute adaptation sous la même licence.", "license_media": "Les images et médias conservent leurs propres licences, indiquées dans chaque article.", "license_documents": "Les documents importés ({titles}) ne proviennent pas de Wikipédia et ne sont pas couverts par cette licence.", "license_unofficial": "Ce livre n'est pas une publication officielle de Wikipédia ni de la Wikimedia Foundation."},
    "en": {"introduction": "Introduction", "toc": "Table of contents", "chapter": "Chapter", "conclusion": "Conclusion", "license": "License", "no_chapter": "No chapter", "edition": "Edition of {date}", "sources": "Sources and authors", "history": "History and authors:", "license_name": "Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)", "license_url": "https://creativecommons.org/licenses/by-sa/4.0/deed.en", "license_intro": "The texts of the Wikipedia articles reproduced in this book are published under the {license} license:", "license_terms": "You are free to share and adapt this content, including for commercial purposes, provided that you credit the authors, indicate the license and whether changes were made, and distribute any adaptation under the same license.", "license_media": "Images and media keep their own licenses, indicated in each article.", "license_documents": "The imported documents ({titles}) do not come from Wikipedia and are not covered by this license.", "license_unofficial": "This book is not an official publication of Wikipedia or of the Wikimedia Foundation."},
    "es": {"introduction": "Introducción", "toc": "Índice", "chapter": "Capítulo", "conclusion": "Conclusión", "license": "Licencia", "no_chapter": "Sin capítulo", "edition": "Edición del {date}", "sources": "Fuentes y autores", "history": "Historial y autores:", "license_name": "Creative Commons Atribución-CompartirIgual 4.0 Internacional (CC BY-SA 4.0)", "license_url": "https://creativecommons.org/licenses/by-sa/4.0/deed.es", "license_intro": "Los textos de los artículos de Wikipedia reproducidos en este libro se publican bajo la licencia {license}:", "license_terms": "Usted es libre de compartir y adaptar este contenido, incluso con fines comerciales, siempre que dé crédito a los autores, indique la licencia y si se han realizado cambios, y distribuya cualquier adaptación bajo la misma licencia.", "license_media": "Las imágenes y los archivos multimedia conservan sus propias licencias, indicadas en cada artículo.", "license_documents": "Los documentos importados ({titles}) no proceden de Wikipedia y no están cubiertos por esta licencia.", "license_unofficial": "Este libro no es una publicación oficial de Wikipedia ni de la Fundación Wikimedia."},
    "pt": {"introduction": "Introdução", "toc": "Sumário", "chapter": "Capítulo", "conclusion": "Conclusão", "license": "Licença", "no_chapter": "Sem capítulo", "edition": "Edição de {date}", "sources": "Fontes e autores", "history": "Histórico e autores:", "license_name": "Creative Commons Atribuição-CompartilhaIgual 4.0 Internacional (CC BY-SA 4.0)", "license_url": "https://creativecommons.org/licenses/by-sa/4.0/deed.pt", "license_intro": "Os textos dos artigos da Wikipédia reproduzidos neste livro são publicados sob a licença {license}:", "license_terms": "Você é livre para compartilhar e adaptar este conteúdo, inclusive para fins comerciais, desde que dê crédito aos autores, indique a licença e se foram feitas alterações, e distribua qualquer adaptação sob a mesma licença.", "license_media": "As imagens e mídias mantêm suas próprias licenças, indicadas em cada artigo.", "license_documents": "Os documentos importados ({titles}) não provêm da Wikipédia e não estão cobertos por esta licença.", "license_unofficial": "Este livro não é uma publicação oficial da Wikipédia nem da Fundação Wikimedia."},
    "it": {"introduction": "Introduzione", "toc": "Indice", "chapter": "Capitolo", "conclusion": "Conclusione", "license": "Licenza", "no_chapter": "Senza capitolo", "edition": "Edizione del {date}", "sources": "Fonti e autori", "history": "Cronologia e autori:", "license_name": "Creative Commons Attribuzione - Condividi allo stesso modo 4.0 Internazionale (CC BY-SA 4.0)", "license_url": "https://creativecommons.org/licenses/by-sa/4.0/deed.it", "license_intro": "I testi delle voci di Wikipedia riprodotti in questo libro sono pubblicati con licenza {license}:", "license_terms": "Sei libero di condividere e modificare questo contenuto, anche a fini commerciali, a condizione di citare gli autori, indicare la licenza e se sono state apportate modifiche, e distribuire ogni adattamento con la stessa licenza.", "license_media": "Le immagini e i file multimediali mantengono le proprie licenze, indicate in ciascuna voce.", "license_documents": "I documenti importati ({titles}) non provengono da Wikipedia e non sono coperti da questa licenza.", "license_unofficial": "Questo libro non è una pubblicazione ufficiale di Wikipedia né della Wikimedia Foundation."},
    "de": {"introduction": "Einleitung", "toc": "Inhaltsverzeichnis", "chapter": "Kapitel", "conclusion": "Schlusswort", "license": "Lizenz", "no_chapter": "Ohne Kapitel", "edition": "Ausgabe vom {date}", "sources": "Quellen und Autoren", "history": "Versionsgeschichte und Autoren:", "license_name": "Creative Commons Namensnennung – Weitergabe unter gleichen Bedingungen 4.0 International (CC BY-SA 4.0)", "license_url": "https://creativecommons.org/licenses/by-sa/4.0/deed.de", "license_intro": "Die Texte der in diesem Buch wiedergegebenen Wikipedia-Artikel stehen unter der Lizenz {license}:", "license_terms": "Sie dürfen diese Inhalte teilen und bearbeiten, auch für kommerzielle Zwecke, sofern Sie die Autoren nennen, die Lizenz angeben, kenntlich machen, ob Änderungen vorgenommen wurden, und jede Bearbeitung unter derselben Lizenz weitergeben.", "license_media": "Bilder und Medien behalten ihre eigenen Lizenzen, die im jeweiligen Artikel angegeben sind.", "license_documents": "Die importierten Dokumente ({titles}) stammen nicht aus Wikipedia und fallen nicht unter diese Lizenz.", "license_unofficial": "Dieses Buch ist keine offizielle Veröffentlichung von Wikipedia oder der Wikimedia Foundation."},
    "nl": {"introduction": "Inleiding", "toc": "Inhoudsopgave", "chapter": "Hoofdstuk", "conclusion": "Conclusie", "license": "Licentie", "no_chapter": "Zonder hoofdstuk", "edition": "Editie van {date}", "sources": "Bronnen en auteurs", "history": "Geschiedenis en auteurs:", "license_name": "Creative Commons Naamsvermelding-GelijkDelen 4.0 Internationaal (CC BY-SA 4.0)", "license_url": "https://creativecommons.org/licenses/by-sa/4.0/deed.nl", "license_intro": "De teksten van de Wikipedia-artikelen in dit boek worden gepubliceerd onder de licentie {license}:", "license_terms": "U mag deze inhoud delen en bewerken, ook voor commerciële doeleinden, op voorwaarde dat u de auteurs vermeldt, de licentie aangeeft en vermeldt of er wijzigingen zijn aangebracht, en elke bewerking onder dezelfde licentie verspreidt.", "license_media": "Afbeeldingen en media behouden hun eigen licenties, vermeld in elk artikel.", "license_documents": "De geïmporteerde documenten ({titles}) zijn niet afkomstig van Wikipedia en vallen niet onder deze licentie.", "license_unofficial": "Dit boek is geen officiële publicatie van Wikipedia of van de Wikimedia Foundation."},
    "tr": {"introduction": "Giriş", "toc": "İçindekiler", "chapter": "Bölüm", "conclusion": "Sonuç", "license": "Lisans", "no_chapter": "Bölümsüz", "edition": "{date} baskısı", "sources": "Kaynaklar ve yazarlar", "history": "Geçmiş ve yazarlar:", "license_name": "Creative Commons Atıf-AynıLisanslaPaylaş 4.0 Uluslararası (CC BY-SA 4.0)", "license_url": "https://creativecommons.org/licenses/by-sa/4.0/deed.tr", "license_intro": "Bu kitapta yer alan Vikipedi maddelerinin metinleri {license} lisansı altında yayımlanmaktadır:", "license_terms": "Yazarlara atıfta bulunmanız, lisansı ve değişiklik yapılıp yapılmadığını belirtmeniz ve her türlü uyarlamayı aynı lisansla dağıtmanız koşuluyla, bu içeriği ticari amaçlar dahil olmak üzere paylaşmakta ve uyarlamakta özgürsünüz.", "license_media": "Görseller ve medya dosyaları, her maddede belirtilen kendi lisanslarını korur.", "license_documents": "İçe aktarılan belgeler ({titles}) Vikipedi'den gelmemektedir ve bu lisans kapsamında değildir.", "license_unofficial": "Bu kitap Vikipedi'nin veya Wikimedia Vakfı'nın resmî bir yayını değildir."},
    "zh": {"introduction": "引言", "toc": "目录", "chapter": "章", "conclusion": "结语", "license": "许可协议", "no_chapter": "未分章", "edition": "{date} 版", "sources": "来源与作者", "history": "历史与作者：", "license_name": "知识共享 署名-相同方式共享 4.0 国际 (CC BY-SA 4.0)", "license_url": "https://creativecommons.org/licenses/by-sa/4.0/deed.zh-hans", "license_intro": "本书收录的维基百科条目文本依据{license}许可协议发布：", "license_terms": "您可以自由地分享和改编本内容，包括用于商业目的，但须署名作者、注明许可协议并说明是否作了修改，且须以相同的许可协议发布任何改编作品。", "license_media": "图像和媒体文件保留各自的许可协议，详见各条目。", "license_documents": "导入的文档（{titles}）并非来自维基百科，不受本许可协议约束。", "license_unofficial": "本书并非维基百科或维基媒体基金会的官方出版物。"},
    "ja": {"introduction": "はじめに", "toc": "目次", "chapter": "章", "conclusion": "おわりに", "license": "ライセンス", "no_chapter": "章なし", "edition": "{date} 版", "sources": "出典と著者", "history": "履歴と著者：", "license_name": "クリエイティブ・コモンズ 表示 - 継承 4.0 国際 (CC BY-SA 4.0)", "license_url": "https://creativecommons.org/licenses/by-sa/4.0/deed.ja", "license_intro": "本書に収録されたウィキペディアの記事の本文は、{license} ライセンスの下で公開されています：", "license_terms": "著作者のクレジットを表示し、ライセンスを示し、変更の有無を明記し、改変したものを同じライセンスで頒布することを条件に、商用目的を含め、このコンテンツを自由に共有・改変できます。", "license_media": "画像やメディアには、各記事に記載されたそれぞれのライセンスが適用されます。", "license_documents": "インポートされた文書（{titles}）はウィキペディアに由来するものではなく、このライセンスの対象外です。", "license_unofficial": "本書はウィキペディアまたはウィキメディア財団の公式出版物ではありません。"},
    "ar": {"introduction": "مقدمة", "toc": "جدول المحتويات", "chapter": "الفصل", "conclusion": "خاتمة", "license": "الترخيص", "no_chapter": "بدون فصل", "edition": "طبعة {date}", "sources": "المصادر والمؤلفون", "history": "السجل والمؤلفون:", "license_name": "المشاع الإبداعي نسب المصنف - الترخيص بالمثل 4.0 دولي (CC BY-SA 4.0)", "license_url": "https://creativecommons.org/licenses/by-sa/4.0/deed.ar", "license_intro": "نصوص مقالات ويكيبيديا الواردة في هذا الكتاب منشورة بموجب ترخيص {license}:", "license_terms": "يحق لك مشاركة هذا المحتوى وتعديله، بما في ذلك للأغراض التجارية، بشرط نسبه إلى مؤلفيه، والإشارة إلى الترخيص وإلى ما إذا كانت قد أُجريت تعديلات، ونشر أي عمل معدَّل بموجب الترخيص نفسه.", "license_media": "تحتفظ الصور والوسائط بتراخيصها الخاصة المذكورة في كل مقالة.", "license_documents": "المستندات المستوردة ({titles}) ليست من ويكيبيديا ولا يشملها هذا الترخيص.", "license_unofficial": "هذا الكتاب ليس منشورًا رسميًا لويكيبيديا ولا لمؤسسة ويكيميديا."},
    "fa": {"introduction": "مقدمه", "toc": "فهرست مطالب", "chapter": "فصل", "conclusion": "نتیجه‌گیری", "license": "مجوز", "no_chapter": "بدون فصل", "edition": "ویرایش {date}", "sources": "منابع و نویسندگان", "history": "تاریخچه و نویسندگان:", "license_name": "کریتیو کامنز اختصاص - اشتراک‌گذاری همانند 4.0 بین‌المللی (CC BY-SA 4.0)", "license_url": "https://creativecommons.org/licenses/by-sa/4.0/deed.fa", "license_intro": "متن مقاله‌های ویکی‌پدیا که در این کتاب آمده است تحت مجوز {license} منتشر شده است:", "license_terms": "شما آزادید این محتوا را، حتی برای مقاصد تجاری، به اشتراک بگذارید و تغییر دهید، به شرط آنکه نام نویسندگان را ذکر کنید، مجوز را ذکر کنید و مشخص کنید که آیا تغییری داده شده است، و هر اثر اقتباسی را تحت همین مجوز منتشر کنید.", "license_media": "تصاویر و رسانه‌ها مجوزهای خاص خود را دارند که در هر مقاله ذکر شده است.", "license_documents": "اسناد واردشده ({titles}) از ویکی‌پدیا نیستند و تحت پوشش این مجوز قرار نمی‌گیرند.", "license_unofficial": "این کتاب یک انتشار رسمی ویکی‌پدیا یا بنیاد ویکی‌مدیا نیست."},
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


def book_slots(groups: list[tuple[str, list[BookItem]]]) -> list[tuple[str, int | BookItem]]:
    slots: list[tuple[str, int | BookItem]] = []
    for index, (chapter_title, items) in enumerate(groups):
        if chapter_title:
            slots.append(("chapter", index))
        slots.extend(("item", item) for item in items)
    return slots


def toc_slot_index(
    project: Project, groups: list[tuple[str, list[BookItem]]], slots: list[tuple[str, int | BookItem]]
) -> int | None:
    if not project.table_of_contents:
        return None
    if project.toc_position == "end":
        return len(slots)
    anchor = project.toc_position.removeprefix("before:")
    chapter_titles = {f"chapter:{chapter.id}": chapter.title for chapter in project.chapters}
    for index, (kind, value) in enumerate(slots):
        if kind == "item" and value.key == anchor:
            return index
        if kind == "chapter" and chapter_titles.get(anchor) == groups[value][0]:
            return index
        if kind == "chapter" and anchor == "chapter:" and value == len(groups) - 1 and groups[value][0] not in chapter_titles.values():
            return index
    return 0


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
[dir=rtl] nav ol {{ padding-left: 0; padding-right: 18pt; }}
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
        f'<li><strong>{escape(article.title)}</strong><br><span class="url">{escape(article.url)}</span><br>'
        f'{escape(pdf_label(language, "history"))} <span class="url">{escape(_history_url(article))}</span></li>'
        for article in articles
    )
    sources_section = f'<h2>{pdf_label(language, "sources")}</h2><ol>{sources}</ol>' if articles else ""
    documents_note = (
        f"<p>{escape(pdf_label(language, 'license_documents', titles=', '.join(document.title for document in documents)))}</p>"
        if documents else ""
    )
    license_name = f'<span class="license-name">{escape(pdf_label(language, "license_name"))}</span>'
    intro = license_name.join(escape(part) for part in PDF_LABELS[language]["license_intro"].split("{license}"))
    return f"""<!doctype html>
<html {_html_attrs(language)}><head><meta charset="utf-8"><style>
@page {{ size: {page_width:g}mm {page_height:g}mm; margin: {margin_top:g}mm {outer:g}mm {margin_bottom:g}mm {inner:g}mm; }}
@page :left {{ margin-left: {inner:g}mm; margin-right: {outer:g}mm; }}
@page :right {{ margin-left: {outer:g}mm; margin-right: {inner:g}mm; }}
body {{ color: #202020; font: 10pt serif; line-height: 1.5; }}
h1 {{ font-size: 22pt; }}
h2 {{ font-size: 14pt; margin-top: 18pt; }}
ol {{ padding-left: 18pt; font-size: 9pt; }}
[dir=rtl] ol {{ padding-left: 0; padding-right: 18pt; }}
li {{ margin-bottom: 6pt; overflow-wrap: anywhere; }}
.license-name {{ font-weight: bold; }}
.url {{ direction: ltr; unicode-bidi: embed; }}
</style></head><body>
<h1>{pdf_label(language, 'license')}</h1>
<p>{intro} <span class="url">{pdf_label(language, 'license_url')}</span></p>
<p>{escape(pdf_label(language, 'license_terms'))}</p>
<p>{escape(pdf_label(language, 'license_media'))}</p>
{documents_note}
<p>{escape(pdf_label(language, 'license_unofficial'))}</p>
{sources_section}
</body></html>"""
