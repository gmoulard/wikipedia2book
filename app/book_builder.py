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
import binascii
import io
import math
from datetime import date
from html import escape
from pathlib import Path
from typing import get_args
from urllib.parse import quote

from PIL import Image, ImageOps

from app.models import Article, BookImage, Project, Site, UploadedDocument

BookItem = Article | UploadedDocument

_PAGE_SIZES = {
    "A0": (841, 1189), "A1": (594, 841), "A2": (420, 594),
    "A3": (297, 420), "A4": (210, 297), "A5": (148, 210),
    "A6": (105, 148), "Letter": (216, 279), "Legal": (216, 356),
}

# NE PAS ajouter de langue ici sans l'ajouter à SUPPORTED_LANGUAGES dans i18n.js (et inversement) : test_i18n.PdfLabelsTest.
PDF_LABELS = {
    "fr": {"volume_title": "{title} — Tome {index}/{count}", "introduction": "Introduction", "toc": "Table des matières", "chapter": "Chapitre", "conclusion": "Conclusion", "license": "Licence", "no_chapter": "Sans chapitre", "edition": "Édition du {date}", "license_name": "Creative Commons Attribution – Partage dans les mêmes conditions 4.0 International (CC BY-SA 4.0)", "license_url": "https://creativecommons.org/licenses/by-sa/4.0/deed.fr", "license_intro": "Les textes provenant de {sites} reproduits dans ce livre sont publiés sous licence {license} :", "license_terms": "Vous êtes libre de partager et d'adapter ce contenu, y compris à des fins commerciales, à condition de créditer les auteurs, d'indiquer la licence et si des modifications ont été apportées, et de diffuser toute adaptation sous la même licence.", "license_authors": "Les auteurs de chaque article sont crédités par le lien vers sa source, placé à la fin de l'article : il mène à la version reproduite, dont l'historique liste tous les contributeurs.", "license_media": "Les images et médias conservent leurs propres licences, indiquées dans chaque article.", "license_documents": "Les documents importés ({titles}) ne proviennent pas des projets Wikimédia et ne sont pas couverts par cette licence.", "license_unofficial": "Ce livre n'est pas une publication officielle de {sites} ni de la Wikimedia Foundation.", "license_wikisource": "Les textes provenant de Wikisource sont pour la plupart dans le domaine public ; les autres (traductions, éditions récentes) sont publiés sous la licence indiquée sur leur page Wikisource, en général CC BY-SA 4.0.", "license_wikinews": "Les articles provenant de Wikinews sont publiés sous la licence Creative Commons Attribution (CC BY), dans la version indiquée sur leur page Wikinews.", "list_separator": ", ", "site_wikipedia": "Wikipédia", "site_wikisource": "Wikisource", "site_wikibooks": "Wikilivres", "site_wikivoyage": "Wikivoyage", "site_wikiversity": "Wikiversité", "site_wikiquote": "Wikiquote", "site_wiktionary": "Wiktionnaire", "site_wikinews": "Wikinews"},
    "en": {"volume_title": "{title} — Volume {index}/{count}", "introduction": "Introduction", "toc": "Table of contents", "chapter": "Chapter", "conclusion": "Conclusion", "license": "License", "no_chapter": "No chapter", "edition": "Edition of {date}", "license_name": "Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)", "license_url": "https://creativecommons.org/licenses/by-sa/4.0/deed.en", "license_intro": "The texts from {sites} reproduced in this book are published under the {license} license:", "license_terms": "You are free to share and adapt this content, including for commercial purposes, provided that you credit the authors, indicate the license and whether changes were made, and distribute any adaptation under the same license.", "license_authors": "The authors of each article are credited by the link to its source at the end of the article: it leads to the reproduced version, whose history lists all contributors.", "license_media": "Images and media keep their own licenses, indicated in each article.", "license_documents": "The imported documents ({titles}) do not come from Wikimedia projects and are not covered by this license.", "license_unofficial": "This book is not an official publication of {sites} or of the Wikimedia Foundation.", "license_wikisource": "Texts from Wikisource are mostly in the public domain; the others (translations, recent editions) are published under the license shown on their Wikisource page, usually CC BY-SA 4.0.", "license_wikinews": "Articles from Wikinews are published under the Creative Commons Attribution (CC BY) license, in the version shown on their Wikinews page.", "list_separator": ", ", "site_wikipedia": "Wikipedia", "site_wikisource": "Wikisource", "site_wikibooks": "Wikibooks", "site_wikivoyage": "Wikivoyage", "site_wikiversity": "Wikiversity", "site_wikiquote": "Wikiquote", "site_wiktionary": "Wiktionary", "site_wikinews": "Wikinews"},
    "es": {"volume_title": "{title} — Tomo {index}/{count}", "introduction": "Introducción", "toc": "Índice", "chapter": "Capítulo", "conclusion": "Conclusión", "license": "Licencia", "no_chapter": "Sin capítulo", "edition": "Edición del {date}", "license_name": "Creative Commons Atribución-CompartirIgual 4.0 Internacional (CC BY-SA 4.0)", "license_url": "https://creativecommons.org/licenses/by-sa/4.0/deed.es", "license_intro": "Los textos procedentes de {sites} reproducidos en este libro se publican bajo la licencia {license}:", "license_terms": "Usted es libre de compartir y adaptar este contenido, incluso con fines comerciales, siempre que dé crédito a los autores, indique la licencia y si se han realizado cambios, y distribuya cualquier adaptación bajo la misma licencia.", "license_authors": "Los autores de cada artículo se acreditan mediante el enlace a su fuente, situado al final del artículo: lleva a la versión reproducida, cuyo historial enumera a todos los colaboradores.", "license_media": "Las imágenes y los archivos multimedia conservan sus propias licencias, indicadas en cada artículo.", "license_documents": "Los documentos importados ({titles}) no proceden de los proyectos Wikimedia y no están cubiertos por esta licencia.", "license_unofficial": "Este libro no es una publicación oficial de {sites} ni de la Fundación Wikimedia.", "license_wikisource": "Los textos procedentes de Wikisource están en su mayoría en el dominio público; los demás (traducciones, ediciones recientes) se publican bajo la licencia indicada en su página de Wikisource, generalmente CC BY-SA 4.0.", "license_wikinews": "Los artículos procedentes de Wikinoticias se publican bajo la licencia Creative Commons Atribución (CC BY), en la versión indicada en su página de Wikinoticias.", "list_separator": ", ", "site_wikipedia": "Wikipedia", "site_wikisource": "Wikisource", "site_wikibooks": "Wikilibros", "site_wikivoyage": "Wikiviajes", "site_wikiversity": "Wikiversidad", "site_wikiquote": "Wikiquote", "site_wiktionary": "Wikcionario", "site_wikinews": "Wikinoticias"},
    "pt": {"volume_title": "{title} — Volume {index}/{count}", "introduction": "Introdução", "toc": "Sumário", "chapter": "Capítulo", "conclusion": "Conclusão", "license": "Licença", "no_chapter": "Sem capítulo", "edition": "Edição de {date}", "license_name": "Creative Commons Atribuição-CompartilhaIgual 4.0 Internacional (CC BY-SA 4.0)", "license_url": "https://creativecommons.org/licenses/by-sa/4.0/deed.pt", "license_intro": "Os textos provenientes de {sites} reproduzidos neste livro são publicados sob a licença {license}:", "license_terms": "Você é livre para compartilhar e adaptar este conteúdo, inclusive para fins comerciais, desde que dê crédito aos autores, indique a licença e se foram feitas alterações, e distribua qualquer adaptação sob a mesma licença.", "license_authors": "Os autores de cada artigo são creditados pelo link para a sua fonte, no final do artigo: ele leva à versão reproduzida, cujo histórico lista todos os colaboradores.", "license_media": "As imagens e mídias mantêm suas próprias licenças, indicadas em cada artigo.", "license_documents": "Os documentos importados ({titles}) não provêm dos projetos Wikimedia e não estão cobertos por esta licença.", "license_unofficial": "Este livro não é uma publicação oficial de {sites} nem da Fundação Wikimedia.", "license_wikisource": "Os textos provenientes do Wikisource estão, em sua maioria, em domínio público; os demais (traduções, edições recentes) são publicados sob a licença indicada em sua página do Wikisource, geralmente CC BY-SA 4.0.", "license_wikinews": "Os artigos provenientes do Wikinotícias são publicados sob a licença Creative Commons Atribuição (CC BY), na versão indicada em sua página do Wikinotícias.", "list_separator": ", ", "site_wikipedia": "Wikipédia", "site_wikisource": "Wikisource", "site_wikibooks": "Wikilivros", "site_wikivoyage": "Wikiviagem", "site_wikiversity": "Wikiversidade", "site_wikiquote": "Wikiquote", "site_wiktionary": "Wikcionário", "site_wikinews": "Wikinotícias"},
    "it": {"volume_title": "{title} — Volume {index}/{count}", "introduction": "Introduzione", "toc": "Indice", "chapter": "Capitolo", "conclusion": "Conclusione", "license": "Licenza", "no_chapter": "Senza capitolo", "edition": "Edizione del {date}", "license_name": "Creative Commons Attribuzione - Condividi allo stesso modo 4.0 Internazionale (CC BY-SA 4.0)", "license_url": "https://creativecommons.org/licenses/by-sa/4.0/deed.it", "license_intro": "I testi provenienti da {sites} riprodotti in questo libro sono pubblicati con licenza {license}:", "license_terms": "Sei libero di condividere e modificare questo contenuto, anche a fini commerciali, a condizione di citare gli autori, indicare la licenza e se sono state apportate modifiche, e distribuire ogni adattamento con la stessa licenza.", "license_authors": "Gli autori di ogni voce sono citati tramite il collegamento alla fonte, posto alla fine della voce: porta alla versione riprodotta, la cui cronologia elenca tutti i contributori.", "license_media": "Le immagini e i file multimediali mantengono le proprie licenze, indicate in ciascuna voce.", "license_documents": "I documenti importati ({titles}) non provengono dai progetti Wikimedia e non sono coperti da questa licenza.", "license_unofficial": "Questo libro non è una pubblicazione ufficiale di {sites} né della Wikimedia Foundation.", "license_wikisource": "I testi provenienti da Wikisource sono per lo più nel pubblico dominio; gli altri (traduzioni, edizioni recenti) sono pubblicati con la licenza indicata nella loro pagina di Wikisource, di solito CC BY-SA 4.0.", "license_wikinews": "Gli articoli provenienti da Wikinotizie sono pubblicati con licenza Creative Commons Attribuzione (CC BY), nella versione indicata nella loro pagina di Wikinotizie.", "list_separator": ", ", "site_wikipedia": "Wikipedia", "site_wikisource": "Wikisource", "site_wikibooks": "Wikibooks", "site_wikivoyage": "Wikivoyage", "site_wikiversity": "Wikiversità", "site_wikiquote": "Wikiquote", "site_wiktionary": "Wikizionario", "site_wikinews": "Wikinotizie"},
    "de": {"volume_title": "{title} – Band {index}/{count}", "introduction": "Einleitung", "toc": "Inhaltsverzeichnis", "chapter": "Kapitel", "conclusion": "Schlusswort", "license": "Lizenz", "no_chapter": "Ohne Kapitel", "edition": "Ausgabe vom {date}", "license_name": "Creative Commons Namensnennung – Weitergabe unter gleichen Bedingungen 4.0 International (CC BY-SA 4.0)", "license_url": "https://creativecommons.org/licenses/by-sa/4.0/deed.de", "license_intro": "Die in diesem Buch wiedergegebenen Texte aus {sites} stehen unter der Lizenz {license}:", "license_terms": "Sie dürfen diese Inhalte teilen und bearbeiten, auch für kommerzielle Zwecke, sofern Sie die Autoren nennen, die Lizenz angeben, kenntlich machen, ob Änderungen vorgenommen wurden, und jede Bearbeitung unter derselben Lizenz weitergeben.", "license_authors": "Die Autoren jedes Artikels werden durch den Link zur Quelle am Ende des Artikels genannt: Er führt zur wiedergegebenen Version, deren Versionsgeschichte alle Beitragenden aufführt.", "license_media": "Bilder und Medien behalten ihre eigenen Lizenzen, die im jeweiligen Artikel angegeben sind.", "license_documents": "Die importierten Dokumente ({titles}) stammen nicht aus Wikimedia-Projekten und fallen nicht unter diese Lizenz.", "license_unofficial": "Dieses Buch ist keine offizielle Veröffentlichung von {sites} oder der Wikimedia Foundation.", "license_wikisource": "Die Texte aus Wikisource sind größtenteils gemeinfrei; die übrigen (Übersetzungen, neuere Ausgaben) stehen unter der auf ihrer Wikisource-Seite angegebenen Lizenz, meist CC BY-SA 4.0.", "license_wikinews": "Die Artikel aus Wikinews stehen unter der Lizenz Creative Commons Namensnennung (CC BY) in der auf ihrer Wikinews-Seite angegebenen Version.", "list_separator": ", ", "site_wikipedia": "Wikipedia", "site_wikisource": "Wikisource", "site_wikibooks": "Wikibooks", "site_wikivoyage": "Wikivoyage", "site_wikiversity": "Wikiversity", "site_wikiquote": "Wikiquote", "site_wiktionary": "Wiktionary", "site_wikinews": "Wikinews"},
    "nl": {"volume_title": "{title} — Deel {index}/{count}", "introduction": "Inleiding", "toc": "Inhoudsopgave", "chapter": "Hoofdstuk", "conclusion": "Conclusie", "license": "Licentie", "no_chapter": "Zonder hoofdstuk", "edition": "Editie van {date}", "license_name": "Creative Commons Naamsvermelding-GelijkDelen 4.0 Internationaal (CC BY-SA 4.0)", "license_url": "https://creativecommons.org/licenses/by-sa/4.0/deed.nl", "license_intro": "De teksten uit {sites} in dit boek worden gepubliceerd onder de licentie {license}:", "license_terms": "U mag deze inhoud delen en bewerken, ook voor commerciële doeleinden, op voorwaarde dat u de auteurs vermeldt, de licentie aangeeft en vermeldt of er wijzigingen zijn aangebracht, en elke bewerking onder dezelfde licentie verspreidt.", "license_authors": "De auteurs van elk artikel worden vermeld via de link naar de bron aan het einde van het artikel: die leidt naar de overgenomen versie, waarvan de geschiedenis alle bijdragers vermeldt.", "license_media": "Afbeeldingen en media behouden hun eigen licenties, vermeld in elk artikel.", "license_documents": "De geïmporteerde documenten ({titles}) zijn niet afkomstig van Wikimedia-projecten en vallen niet onder deze licentie.", "license_unofficial": "Dit boek is geen officiële publicatie van {sites} of van de Wikimedia Foundation.", "license_wikisource": "Teksten van Wikisource zijn grotendeels in het publieke domein; de overige (vertalingen, recente edities) worden gepubliceerd onder de licentie die op hun Wikisource-pagina staat, meestal CC BY-SA 4.0.", "license_wikinews": "Artikelen van Wikinieuws worden gepubliceerd onder de licentie Creative Commons Naamsvermelding (CC BY), in de versie die op hun Wikinieuws-pagina staat.", "list_separator": ", ", "site_wikipedia": "Wikipedia", "site_wikisource": "Wikisource", "site_wikibooks": "Wikibooks", "site_wikivoyage": "Wikivoyage", "site_wikiversity": "Wikiversity", "site_wikiquote": "Wikiquote", "site_wiktionary": "WikiWoordenboek", "site_wikinews": "Wikinieuws"},
    "tr": {"volume_title": "{title} — Cilt {index}/{count}", "introduction": "Giriş", "toc": "İçindekiler", "chapter": "Bölüm", "conclusion": "Sonuç", "license": "Lisans", "no_chapter": "Bölümsüz", "edition": "{date} baskısı", "license_name": "Creative Commons Atıf-AynıLisanslaPaylaş 4.0 Uluslararası (CC BY-SA 4.0)", "license_url": "https://creativecommons.org/licenses/by-sa/4.0/deed.tr", "license_intro": "Bu kitapta yer alan {sites} metinleri {license} lisansı altında yayımlanmaktadır:", "license_terms": "Yazarlara atıfta bulunmanız, lisansı ve değişiklik yapılıp yapılmadığını belirtmeniz ve her türlü uyarlamayı aynı lisansla dağıtmanız koşuluyla, bu içeriği ticari amaçlar dahil olmak üzere paylaşmakta ve uyarlamakta özgürsünüz.", "license_authors": "Her maddenin yazarları, maddenin sonundaki kaynak bağlantısıyla belirtilir: bu bağlantı, geçmişi tüm katkıda bulunanları listeleyen çoğaltılmış sürüme götürür.", "license_media": "Görseller ve medya dosyaları, her maddede belirtilen kendi lisanslarını korur.", "license_documents": "İçe aktarılan belgeler ({titles}) Wikimedia projelerinden gelmemektedir ve bu lisans kapsamında değildir.", "license_unofficial": "Bu kitap, {sites} ya da Wikimedia Vakfı tarafından yayımlanmış resmî bir yayın değildir.", "license_wikisource": "Vikikaynak'tan alınan metinlerin çoğu kamu malıdır; diğerleri (çeviriler, yeni baskılar) Vikikaynak sayfalarında belirtilen lisansla, genellikle CC BY-SA 4.0 ile yayımlanır.", "license_wikinews": "Vikihaber'den alınan haberler, Vikihaber sayfalarında belirtilen sürümüyle Creative Commons Atıf (CC BY) lisansı altında yayımlanır.", "list_separator": ", ", "site_wikipedia": "Vikipedi", "site_wikisource": "Vikikaynak", "site_wikibooks": "Vikikitap", "site_wikivoyage": "Vikigezgin", "site_wikiversity": "Vikiversite", "site_wikiquote": "Vikisöz", "site_wiktionary": "Vikisözlük", "site_wikinews": "Vikihaber"},
    "zh": {"volume_title": "{title}（第 {index}/{count} 册）", "introduction": "引言", "toc": "目录", "chapter": "章", "conclusion": "结语", "license": "许可协议", "no_chapter": "未分章", "edition": "{date} 版", "license_name": "知识共享 署名-相同方式共享 4.0 国际 (CC BY-SA 4.0)", "license_url": "https://creativecommons.org/licenses/by-sa/4.0/deed.zh-hans", "license_intro": "本书收录的来自{sites}的文本依据{license}许可协议发布：", "license_terms": "您可以自由地分享和改编本内容，包括用于商业目的，但须署名作者、注明许可协议并说明是否作了修改，且须以相同的许可协议发布任何改编作品。", "license_authors": "每个条目的作者通过条目末尾的来源链接署名：该链接指向所复制的版本，其历史记录列出了所有贡献者。", "license_media": "图像和媒体文件保留各自的许可协议，详见各条目。", "license_documents": "导入的文档（{titles}）并非来自维基媒体项目，不受本许可协议约束。", "license_unofficial": "本书并非{sites}或维基媒体基金会的官方出版物。", "license_wikisource": "来自维基文库的文本大多属于公有领域；其余文本（译文、近期版本）依据其维基文库页面所注明的许可协议发布，通常为 CC BY-SA 4.0。", "license_wikinews": "来自维基新闻的文章依据知识共享 署名 (CC BY) 许可协议发布，版本以其维基新闻页面所注明的为准。", "list_separator": "、", "site_wikipedia": "维基百科", "site_wikisource": "维基文库", "site_wikibooks": "维基教科书", "site_wikivoyage": "维基导游", "site_wikiversity": "维基学院", "site_wikiquote": "维基语录", "site_wiktionary": "维基词典", "site_wikinews": "维基新闻"},
    "ja": {"volume_title": "{title}（第 {index} 巻／全 {count} 巻）", "introduction": "はじめに", "toc": "目次", "chapter": "章", "conclusion": "おわりに", "license": "ライセンス", "no_chapter": "章なし", "edition": "{date} 版", "license_name": "クリエイティブ・コモンズ 表示 - 継承 4.0 国際 (CC BY-SA 4.0)", "license_url": "https://creativecommons.org/licenses/by-sa/4.0/deed.ja", "license_intro": "本書に収録された{sites}の本文は、{license} ライセンスの下で公開されています：", "license_terms": "著作者のクレジットを表示し、ライセンスを示し、変更の有無を明記し、改変したものを同じライセンスで頒布することを条件に、商用目的を含め、このコンテンツを自由に共有・改変できます。", "license_authors": "各記事の著者は、記事の末尾にある出典へのリンクによって表示されます。このリンクは複製された版に通じ、その履歴にすべての投稿者が記載されています。", "license_media": "画像やメディアには、各記事に記載されたそれぞれのライセンスが適用されます。", "license_documents": "インポートされた文書（{titles}）はウィキメディアのプロジェクトに由来するものではなく、このライセンスの対象外です。", "license_unofficial": "本書は{sites}またはウィキメディア財団の公式出版物ではありません。", "license_wikisource": "ウィキソースに由来するテキストの多くはパブリックドメインです。その他（翻訳、最近の版）は、各ウィキソースのページに記載されたライセンス（通常は CC BY-SA 4.0）の下で公開されています。", "license_wikinews": "ウィキニュースに由来する記事は、各ウィキニュースのページに記載された版のクリエイティブ・コモンズ 表示 (CC BY) ライセンスの下で公開されています。", "list_separator": "、", "site_wikipedia": "ウィキペディア", "site_wikisource": "ウィキソース", "site_wikibooks": "ウィキブックス", "site_wikivoyage": "ウィキボヤージュ", "site_wikiversity": "ウィキバーシティ", "site_wikiquote": "ウィキクォート", "site_wiktionary": "ウィクショナリー", "site_wikinews": "ウィキニュース"},
    "ar": {"volume_title": "{title} — المجلد {index}/{count}", "introduction": "مقدمة", "toc": "جدول المحتويات", "chapter": "الفصل", "conclusion": "خاتمة", "license": "الترخيص", "no_chapter": "بدون فصل", "edition": "طبعة {date}", "license_name": "المشاع الإبداعي نسب المصنف - الترخيص بالمثل 4.0 دولي (CC BY-SA 4.0)", "license_url": "https://creativecommons.org/licenses/by-sa/4.0/deed.ar", "license_intro": "النصوص المأخوذة من {sites} والواردة في هذا الكتاب منشورة بموجب ترخيص {license}:", "license_terms": "يحق لك مشاركة هذا المحتوى وتعديله، بما في ذلك للأغراض التجارية، بشرط نسبه إلى مؤلفيه، والإشارة إلى الترخيص وإلى ما إذا كانت قد أُجريت تعديلات، ونشر أي عمل معدَّل بموجب الترخيص نفسه.", "license_authors": "يُنسب كل مقال إلى مؤلفيه عبر رابط المصدر الموجود في نهاية المقال: يقود إلى النسخة المنقولة، التي يسرد سجلها جميع المساهمين.", "license_media": "تحتفظ الصور والوسائط بتراخيصها الخاصة المذكورة في كل مقالة.", "license_documents": "المستندات المستوردة ({titles}) ليست من مشاريع ويكيميديا ولا يشملها هذا الترخيص.", "license_unofficial": "هذا الكتاب ليس منشورًا رسميًا لـ{sites} ولا لمؤسسة ويكيميديا.", "license_wikisource": "معظم النصوص المأخوذة من ويكي مصدر في الملك العام؛ أما الباقي (الترجمات والطبعات الحديثة) فمنشور بموجب الترخيص المذكور في صفحته على ويكي مصدر، وهو عادةً CC BY-SA 4.0.", "license_wikinews": "المقالات المأخوذة من ويكي الأخبار منشورة بموجب ترخيص المشاع الإبداعي نسب المصنف (CC BY)، بالإصدار المذكور في صفحتها على ويكي الأخبار.", "list_separator": "، ", "site_wikipedia": "ويكيبيديا", "site_wikisource": "ويكي مصدر", "site_wikibooks": "ويكي الكتب", "site_wikivoyage": "ويكي رحلات", "site_wikiversity": "ويكي الجامعة", "site_wikiquote": "ويكي الاقتباس", "site_wiktionary": "ويكاموس", "site_wikinews": "ويكي الأخبار"},
    "fa": {"volume_title": "{title} — جلد {index} از {count}", "introduction": "مقدمه", "toc": "فهرست مطالب", "chapter": "فصل", "conclusion": "نتیجه‌گیری", "license": "مجوز", "no_chapter": "بدون فصل", "edition": "ویرایش {date}", "license_name": "کریتیو کامنز اختصاص - اشتراک‌گذاری همانند 4.0 بین‌المللی (CC BY-SA 4.0)", "license_url": "https://creativecommons.org/licenses/by-sa/4.0/deed.fa", "license_intro": "متن‌های برگرفته از {sites} که در این کتاب آمده است تحت مجوز {license} منتشر شده است:", "license_terms": "شما آزادید این محتوا را، حتی برای مقاصد تجاری، به اشتراک بگذارید و تغییر دهید، به شرط آنکه نام نویسندگان را ذکر کنید، مجوز را ذکر کنید و مشخص کنید که آیا تغییری داده شده است، و هر اثر اقتباسی را تحت همین مجوز منتشر کنید.", "license_authors": "نویسندگان هر مقاله با پیوند منبع در پایان مقاله معرفی می‌شوند: این پیوند به نسخهٔ بازنشرشده می‌رود که تاریخچهٔ آن همهٔ مشارکت‌کنندگان را فهرست می‌کند.", "license_media": "تصاویر و رسانه‌ها مجوزهای خاص خود را دارند که در هر مقاله ذکر شده است.", "license_documents": "اسناد واردشده ({titles}) از پروژه‌های ویکی‌مدیا نیستند و تحت پوشش این مجوز قرار نمی‌گیرند.", "license_unofficial": "این کتاب یک انتشار رسمی {sites} یا بنیاد ویکی‌مدیا نیست.", "license_wikisource": "بیشتر متن‌های برگرفته از ویکی‌نبشته در مالکیت عمومی هستند؛ بقیه (ترجمه‌ها، ویرایش‌های جدید) تحت مجوزی که در صفحه ویکی‌نبشته آن‌ها ذکر شده است، معمولاً CC BY-SA 4.0، منتشر شده‌اند.", "license_wikinews": "مقاله‌های برگرفته از ویکی‌خبر تحت مجوز کریتیو کامنز اختصاص (CC BY)، با نسخه‌ای که در صفحه ویکی‌خبر آن‌ها ذکر شده است، منتشر شده‌اند.", "list_separator": "، ", "site_wikipedia": "ویکی‌پدیا", "site_wikisource": "ویکی‌نبشته", "site_wikibooks": "ویکی‌کتاب", "site_wikivoyage": "ویکی‌سفر", "site_wikiversity": "ویکی‌دانشگاه", "site_wikiquote": "ویکی‌گفتاورد", "site_wiktionary": "ویکی‌واژه", "site_wikinews": "ویکی‌خبر"},
}
RTL_LANGUAGES = {"ar", "fa"}


def pdf_label(language: str, key: str, **values: str) -> str:
    return PDF_LABELS[language][key].format(**values)


def _html_attrs(language: str) -> str:
    direction = "rtl" if language in RTL_LANGUAGES else "ltr"
    return f'lang="{language}" dir="{direction}"'



# NE PAS modifier sans aligner buildOrgSlots dans app.js (groupe sans chapitre en tête si unassigned_first).
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
        if unassigned and project.unassigned_first:
            groups.insert(0, ("", unassigned))
        elif unassigned:
            groups.append((pdf_label(language, "no_chapter"), unassigned))
    return groups


def book_slots(groups: list[tuple[str, list[BookItem]]]) -> list[tuple[str, int | BookItem]]:
    slots: list[tuple[str, int | BookItem]] = []
    for index, (chapter_title, items) in enumerate(groups):
        if chapter_title:
            slots.append(("chapter", index))
        slots.extend(("item", item) for item in items)
    return slots


# NE PAS modifier sans aligner tocSlotIndex dans app.js : la position de la TOC doit être la même à l'écran et dans le PDF.
def toc_slot_index(
    project: Project, groups: list[tuple[str, list[BookItem]]], slots: list[tuple[str, int | BookItem]]
) -> int | None:
    if not project.table_of_contents:
        return None
    # NE PAS donner de table des matières à un livre d'un seul article ou document : elle n'aurait qu'une ligne.
    if sum(kind == "item" for kind, _ in slots) <= 1:
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
    text_area = (outer, margin_top, page_width - inner, margin_top + (page_height - margin_top - margin_bottom) * 0.65)
    text_css = COVER_TEXT_CSS[cover_text_style(project.cover_image, page_width, page_height, text_area)] if project.cover_image else ""
    return f"""<!doctype html>
    <html {_html_attrs(language)}>
    <head>
    <meta charset="utf-8">
<title>{book_title}</title>
    <style>
@page {{ size: {page_width:g}mm {page_height:g}mm; margin: {margin_top:g}mm {outer:g}mm {margin_bottom:g}mm {inner:g}mm; }}
@page :left {{ margin-left: {inner:g}mm; margin-right: {outer:g}mm; }}
@page :right {{ margin-left: {outer:g}mm; margin-right: {inner:g}mm; }}
{_background_css(project.cover_image, ':first')}
    body {{ color: #202020; font: 10pt {SERIF_FONTS}; line-height: 1.5; }}
    h1, h2 {{ line-height: 1.2; }}
h1 {{ font-size: 26pt; }}
h2 {{ font-size: 18pt; }}
.cover {{ display: flex; min-height: 65vh; flex-direction: column; justify-content: center; page-break-after: always; }}
.cover h1 {{ max-width: 90%; margin-bottom: 8pt; }}
.subtitle {{ margin: 0; font-size: 15pt; }}
.author {{ margin-top: 32pt; color: #555; }}
.cover-note {{ margin-top: 20pt; color: #555; font-size: 9pt; }}
.opening {{ page-break-after: always; }}
{text_css}
    </style>
    </head>
    <body>
<header class="cover"><div class="cover-text"><h1>{book_title}</h1>{subtitle}{author}<p class="cover-note">{description}</p></div></header>
{introduction}
    </body>
    </html>"""


TOC_LINK_PREFIX = "https://wikipedia2book.invalid/toc/"
# NE PAS laisser la police générique seule : Pango parcourt alors toutes les polices installées (dont les polices CJK de Noto, très lourdes) pour choisir et compléter la police.
# NE PAS placer HanaMinA ni Noto CJK avant le générique : HanaMinB ne couvre que les extensions CJK B et suivantes (caractères rares, 僻字), les caractères chinois et japonais courants restent à Noto CJK, choisi selon la langue de la page.
SERIF_FONTS = '"DejaVu Serif", "HanaMinB", serif'
SANS_FONTS = '"DejaVu Sans", "HanaMinB", sans-serif'


GENERATED_BLOCK_ENTRIES = 100


def toc_link_key(key: str) -> str:
    return TOC_LINK_PREFIX + quote(key, safe="")


def _toc_entries(project: Project, items: list[BookItem], language: str) -> list[tuple[int, str, BookItem | None]]:
    entries: list[tuple[int, str, BookItem | None]] = []
    for index, (chapter_title, chapter_items) in enumerate(ordered_article_groups(project, items, language)):
        if chapter_title:
            entries.append((index, chapter_title, None))
        entries.extend((index, chapter_title, item) for item in chapter_items)
    return entries


def toc_block_count(project: Project, items: list[BookItem], language: str = "fr") -> int:
    return max(1, math.ceil(len(_toc_entries(project, items, language)) / GENERATED_BLOCK_ENTRIES))


def build_toc_html(
    project: Project,
    items: list[BookItem],
    article_pages: dict[str, int] | None = None,
    chapter_pages: list[int | None] | None = None,
    language: str = "fr",
    block: int = 0,
) -> str:
    article_pages = article_pages or {}
    entries = _toc_entries(project, items, language)
    chapter_pages = chapter_pages or [None] * (max((index for index, _, _ in entries), default=-1) + 1)

    def line(label: str, page: int | None, key: str) -> str:
        page_span = f'<span class="page-no">{page}</span>' if page else ""
        return f'<a class="toc-line" href="{toc_link_key(key)}">{page_span}<span class="toc-title">{label}</span></a>'

    contents: list[str] = []
    open_chapter: int | None = None
    for index, chapter_title, item in entries[block * GENERATED_BLOCK_ENTRIES:(block + 1) * GENERATED_BLOCK_ENTRIES]:
        if open_chapter is not None and (item is None or index != open_chapter):
            contents.append("</ol></li>")
            open_chapter = None
        if item is None:
            chapter_page = chapter_pages[index] if index < len(chapter_pages) else None
            contents.append(f'<li class="toc-chapter">{line(escape(chapter_title), chapter_page, f"chapter:{index}")}<ol>')
            open_chapter = index
            continue
        if chapter_title and open_chapter is None:
            contents.append('<li class="toc-chapter"><ol>')
            open_chapter = index
        contents.append(f'<li class="toc-item">{line(escape(item.title), article_pages.get(item.key), item.key)}</li>')
    if open_chapter is not None:
        contents.append("</ol></li>")

    heading = f"<h2>{pdf_label(language, 'toc')}</h2>" if block == 0 else ""
    page_width, page_height, margin_top, margin_bottom, inner, outer = _page_layout(project)
    return f"""<!doctype html>
    <html {_html_attrs(language)}>
    <head>
    <meta charset="utf-8">
    <style>
@page {{ size: {page_width:g}mm {page_height:g}mm; margin: {margin_top:g}mm {outer:g}mm {margin_bottom:g}mm {inner:g}mm; }}
@page :left {{ margin-left: {inner:g}mm; margin-right: {outer:g}mm; }}
@page :right {{ margin-left: {outer:g}mm; margin-right: {inner:g}mm; }}
body {{ color: #202020; font: 10pt {SERIF_FONTS}; line-height: 1.4; }}
nav h2 {{ font-size: 18pt; line-height: 1.2; margin: 0 0 18pt; padding-bottom: 4pt; border-bottom: 0.75pt solid #202020; }}
nav ol {{ list-style: none; margin: 0; padding: 0; }}
nav li {{ display: block; }}
.toc-line {{ display: block; color: inherit; text-decoration: none; padding: 2.5pt 0; }}
.page-no {{ float: right; min-width: 2.5em; margin-left: 12pt; text-align: right; color: #444; }}
.toc-chapter {{ margin-top: 14pt; }}
.toc-chapter > .toc-line {{ font-size: 13pt; font-weight: bold; padding-bottom: 4pt; }}
.toc-chapter > ol {{ padding-left: 16pt; }}
[dir=rtl] .toc-chapter > ol {{ padding-left: 0; padding-right: 16pt; }}
[dir=rtl] .page-no {{ float: left; margin-left: 0; margin-right: 12pt; text-align: left; }}
    </style>
    </head>
    <body>
    <nav>{heading}<ol>{''.join(contents)}</ol></nav>
    </body>
    </html>"""


def build_chapter_page_html(project: Project, title: str, language: str = "fr") -> str:
    page_width, page_height, margin_top, margin_bottom, inner, outer = _page_layout(project)
    return f"""<!doctype html>
<html {_html_attrs(language)}><head><meta charset="utf-8"><style>
@page {{ size: {page_width:g}mm {page_height:g}mm; margin: {margin_top:g}mm {outer:g}mm {margin_bottom:g}mm {inner:g}mm; }}
@page :left {{ margin-left: {inner:g}mm; margin-right: {outer:g}mm; }}
@page :right {{ margin-left: {outer:g}mm; margin-right: {inner:g}mm; }}
body {{ color: #202020; font: 11pt {SERIF_FONTS}; }}
main {{ display: flex; min-height: 75vh; flex-direction: column; justify-content: center; }}
p {{ color: #167465; font: bold 9pt {SANS_FONTS}; letter-spacing: 1pt; text-transform: uppercase; }}
p:lang(ar), p:lang(fa) {{ letter-spacing: 0; }}
h1 {{ font-size: 30pt; }}
</style></head><body><main><p>{pdf_label(language, 'chapter')}</p><h1>{escape(title)}</h1></main></body></html>"""


APP_URL = "https://wikipedia2book.toolforge.org/"
SOURCE_URL = "https://github.com/gmoulard/wikipedia2book"
COLOPHON_LOGO = Path(__file__).parent / "static" / "Wikipedia2bookLogoPrint.png"
COLOPHON_CSS = (
    ".colophon {{ margin-top: 28pt; text-align: center; break-inside: avoid; font: 9pt {fonts}; line-height: 1.6; }}"
    ".colophon img {{ width: 100mm; max-width: 100%; }}"
    ".colophon a {{ color: #36c; text-decoration: none; }}"
)


def _background_css(image: BookImage | None, page: str) -> str:
    if image is None:
        return ""
    # NE PAS retirer « fixed » : sans lui, WeasyPrint dimensionne le fond d'une page sur la zone intérieure aux marges, l'image ne couvre plus toute la feuille.
    return f'@page {page} {{ background: url("data:{image.mime_type};base64,{image.data_base64}") center / cover no-repeat fixed; }}'



BACKGROUND_DPI = 300
BACKGROUND_JPEG_QUALITY = 90
_ROTATED_ORIENTATIONS = {5, 6, 7, 8}


# NE PAS laisser WeasyPrint rendre l'image d'origine : une photo de 5 616 × 3 744 px y prenait 2,0 s sur Toolforge pour une page A4 qui n'en affiche que 2 480 × 3 508, 0,7 s une fois réduite.
def fit_background(image: BookImage, width_mm: float, height_mm: float) -> BookImage:
    if image.data_base64 is None or image.mime_type == "image/svg+xml":
        return image
    target = (round(width_mm / 25.4 * BACKGROUND_DPI), round(height_mm / 25.4 * BACKGROUND_DPI))
    try:
        picture = Image.open(io.BytesIO(base64.b64decode(image.data_base64)))
        width, height = picture.size
        rotated = picture.getexif().get(0x0112) in _ROTATED_ORIENTATIONS
        if rotated:
            width, height = height, width
        scale = max(target[0] / width, target[1] / height)
        if scale > 1 or (width, height) == target:
            return image
        needed = (math.ceil(width * scale), math.ceil(height * scale))
        picture.draft("RGB", (needed[1], needed[0]) if rotated else needed)
        picture = ImageOps.exif_transpose(picture)
        scale = max(target[0] / picture.width, target[1] / picture.height)
        visible = (target[0] / scale, target[1] / scale)
        box = ((picture.width - visible[0]) / 2, (picture.height - visible[1]) / 2, (picture.width + visible[0]) / 2, (picture.height + visible[1]) / 2)
        # NE PAS redimensionner toute l'image avant de la recadrer : resize(box=…) ne traite que la partie visible, 70 Mo de mémoire de moins pour une photo de 5 616 × 3 744 px.
        picture = picture.resize(target, Image.LANCZOS, box=box)
        transparent = picture.mode in ("RGBA", "LA") or (picture.mode == "P" and "transparency" in picture.info)
        buffer = io.BytesIO()
        if transparent:
            picture.convert("RGBA").save(buffer, "PNG", optimize=True)
            mime_type = "image/png"
        else:
            picture.convert("RGB").save(buffer, "JPEG", quality=BACKGROUND_JPEG_QUALITY, optimize=True)
            mime_type = "image/jpeg"
    except (OSError, ValueError, binascii.Error, Image.DecompressionBombError):
        return image
    return BookImage(title=image.title, mime_type=mime_type, data_base64=base64.b64encode(buffer.getvalue()).decode("ascii"))


BLACK_TEXT_MIN_LUMINANCE = 0.175
WHITE_TEXT_MAX_LUMINANCE = 0.183
READABLE_SHARE = 0.95
_LINEAR = [((v / 255) / 12.92) if v <= 10 else (((v / 255) + 0.055) / 1.055) ** 2.4 for v in range(256)]


def _cover_luminances(image: BookImage, width: float, height: float, area: tuple[float, float, float, float]) -> list[float]:
    picture = Image.open(io.BytesIO(base64.b64decode(image.data_base64)))
    picture.draft("RGB", (512, 512))
    picture = ImageOps.exif_transpose(picture).convert("RGBA")
    flat = Image.new("RGBA", picture.size, "white")
    flat.alpha_composite(picture)
    scale = max(width / flat.width, height / flat.height)
    left, top, right, bottom = area
    box = tuple(round(v) for v in (
        flat.width / 2 + (left - width / 2) / scale, flat.height / 2 + (top - height / 2) / scale,
        flat.width / 2 + (right - width / 2) / scale, flat.height / 2 + (bottom - height / 2) / scale,
    ))
    region = flat.crop(box).convert("RGB")
    region.thumbnail((96, 96))
    return [0.2126 * _LINEAR[r] + 0.7152 * _LINEAR[g] + 0.0722 * _LINEAR[b] for r, g, b in region.getdata()]


def cover_text_style(image: BookImage, width: float, height: float, area: tuple[float, float, float, float]) -> str:
    try:
        luminances = sorted(_cover_luminances(image, width, height, area))
    except (OSError, ValueError, binascii.Error, Image.DecompressionBombError):
        return "band"
    if not luminances:
        return "band"
    margin = int(len(luminances) * (1 - READABLE_SHARE))
    if luminances[margin] >= BLACK_TEXT_MIN_LUMINANCE:
        return "dark"
    if luminances[len(luminances) - 1 - margin] <= WHITE_TEXT_MAX_LUMINANCE:
        return "light"
    return "band"


COVER_TEXT_CSS = {
    "dark": "",
    "light": ".cover, .cover .author, .cover .cover-note { color: #fff; }",
    "band": ".cover-text { padding: 14pt 18pt; background: rgba(255, 255, 255, 0.85); }",
}


def _colophon_html(language: str) -> str:
    logo = base64.b64encode(COLOPHON_LOGO.read_bytes()).decode("ascii")
    edition = escape(pdf_label(language, "edition", date=date.today().strftime("%d/%m/%Y")))
    return (
        f'<footer class="colophon"><a href="{APP_URL}"><img src="data:image/png;base64,{logo}" alt="Wikipedia2Book"></a>'
        f'<p class="edition">{edition}</p>'
        f'<p><a href="{APP_URL}">{APP_URL}</a><br><a href="{SOURCE_URL}">{SOURCE_URL}</a></p></footer>'
    )


def build_back_cover_html(project: Project) -> str:
    page_width, page_height, *_ = _page_layout(project)
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
@page {{ size: {page_width:g}mm {page_height:g}mm; margin: 0; }}
{_background_css(project.back_image, "")}
</style></head><body><div></div></body></html>"""


def build_conclusion_page_html(project: Project, language: str = "fr") -> str:
    page_width, page_height, margin_top, margin_bottom, inner, outer = _page_layout(project)
    conclusion = escape(project.conclusion).replace("\n", "<br>")
    return f"""<!doctype html>
<html {_html_attrs(language)}><head><meta charset="utf-8"><style>
@page {{ size: {page_width:g}mm {page_height:g}mm; margin: {margin_top:g}mm {outer:g}mm {margin_bottom:g}mm {inner:g}mm; }}
@page :left {{ margin-left: {inner:g}mm; margin-right: {outer:g}mm; }}
@page :right {{ margin-left: {outer:g}mm; margin-right: {inner:g}mm; }}
body {{ color: #202020; font: 11pt {SERIF_FONTS}; line-height: 1.6; }}
h1 {{ font-size: 22pt; }}
</style></head><body><h1>{pdf_label(language, 'conclusion')}</h1><p>{conclusion}</p></body></html>"""


def _site_names(language: str, sites: list[str]) -> str:
    return pdf_label(language, "list_separator").join(pdf_label(language, f"site_{site}") for site in sites)


def _license_articles(project: Project, items: list[BookItem], language: str) -> tuple[list[Article], list[UploadedDocument]]:
    groups = ordered_article_groups(project, items, language)
    ordered = list({item.key: item for _, group in groups for item in group}.values())
    return (
        [item for item in ordered if isinstance(item, Article)],
        [item for item in ordered if isinstance(item, UploadedDocument)],
    )


# NE PAS remettre la liste des articles avec leurs adresses (« Sources et auteurs ») : chaque PDF d'article se termine déjà par le lien vers la version reproduite, qui crédite ses auteurs, et cette liste pesait plusieurs pages et autant de rendus WeasyPrint sur un gros livre.
def build_license_page_html(project: Project, items: list[BookItem], language: str = "fr") -> str:
    page_width, page_height, margin_top, margin_bottom, inner, outer = _page_layout(project)
    articles, documents = _license_articles(project, items, language)
    present = [site for site in get_args(Site) if any(article.site == site for article in articles)] or ["wikipedia"]
    share_alike = [site for site in present if site not in ("wikisource", "wikinews")]
    notes = "".join(f"<p>{escape(pdf_label(language, f'license_{site}'))}</p>" for site in ("wikisource", "wikinews") if site in present)
    documents_note = (
        f"<p>{escape(pdf_label(language, 'license_documents', titles=', '.join(document.title for document in documents)))}</p>"
        if documents else ""
    )
    license_name = f'<span class="license-name">{escape(pdf_label(language, "license_name"))}</span>'
    intro_template = PDF_LABELS[language]["license_intro"].replace("{sites}", _site_names(language, share_alike))
    intro = license_name.join(escape(part) for part in intro_template.split("{license}"))
    share_alike_license = (
        f"<p>{intro} <span class='url'>{pdf_label(language, 'license_url')}</span></p>"
        f"<p>{escape(pdf_label(language, 'license_terms'))}</p>"
        if share_alike else ""
    )
    header = (
        f"<h1>{pdf_label(language, 'license')}</h1>\n{share_alike_license}\n{notes}\n"
        f"<p>{escape(pdf_label(language, 'license_authors'))}</p>\n"
        f"<p>{escape(pdf_label(language, 'license_media'))}</p>\n{documents_note}\n"
        f"<p>{escape(pdf_label(language, 'license_unofficial', sites=_site_names(language, present)))}</p>"
    )
    return f"""<!doctype html>
<html {_html_attrs(language)}><head><meta charset="utf-8"><style>
@page {{ size: {page_width:g}mm {page_height:g}mm; margin: {margin_top:g}mm {outer:g}mm {margin_bottom:g}mm {inner:g}mm; }}
@page :left {{ margin-left: {inner:g}mm; margin-right: {outer:g}mm; }}
@page :right {{ margin-left: {outer:g}mm; margin-right: {inner:g}mm; }}
body {{ color: #202020; font: 10pt {SERIF_FONTS}; line-height: 1.5; }}
h1 {{ font-size: 22pt; }}
.license-name {{ font-weight: bold; }}
.url {{ direction: ltr; unicode-bidi: embed; }}
{COLOPHON_CSS.format(fonts=SANS_FONTS)}
</style></head><body>
{header}
{_colophon_html(language)}
</body></html>"""
