# راهنمای فیلد «ساختن کتاب»: هر آنچه Wikipedia2Book می‌پذیرد

این صفحه هر آنچه Wikipedia2Book می‌پذیرد را فهرست می‌کند و برای هر مورد یک نمونه برای آزمودن **در مرورگر** و همان مورد را **از راه API** می‌آورد. دو کاربرد دارد: نشان دادن امکانات و بررسی دستی پیش از انتشار یک نسخه. این صفحه ترجمهٔ [صفحهٔ مرجع فرانسوی](helpSearch.fr.md) است.

رفتار مرجع در [مشخصات کارکردی](FunctionalSpec.en.md) (بخش 3.1 برای منابع) و [مشخصات فنی](TechnicalSpec.en.md) (بخش 13.3 برای API) آمده است.

## روش استفاده

- **مرورگر**: https://wikipedia2book.toolforge.org/ را باز کنید، نمونه را در فیلد مرحلهٔ «ساختن کتاب» بچسبانید و روی «افزودن» کلیک کنید. نشانی‌ای که با `https://wikipedia2book.toolforge.org/?` آغاز شود مستقیم باز می‌شود.
- **API**: نشانی را در مرورگر باز کنید (PDF بارگیری می‌شود) یا آن را به `curl -OJ` بدهید. فراخوانی‌های `POST` به صورت فرمان `curl` آمده‌اند.
- **نسخه**: نسخه‌ای از برنامه که مورد از آن به بعد کار می‌کند. نسخهٔ در حال اجرا را https://wikipedia2book.toolforge.org/api/version نشان می‌دهد.
- ستون «نسخه» مربوط به مرورگر است. در API، `GET /api/pdf/from-source` (بخش‌های 1 تا 4) و پارامتر `?source=` صفحه از 1.12.0 وجود دارند (پیش از گرفتن این شماره، از شب 16 نوامبر 2026 در محیط عملیاتی): با نسخه‌ای قدیمی‌تر، پس از شناسایی هر ورودی با `POST /api/sources/resolve` (9.1)، کتاب را به صورت JSON به `POST /api/pdf` (9.3) بفرستید.
- نمونه‌ها در 17 نوامبر 2026 با کد شناسایی منابع در برابر ویکی‌های واقعی بررسی شده‌اند؛ صفحه‌ای که از آن پس تغییر نام داده یا حذف شده باشد می‌تواند نتیجه را تغییر دهد.

کوته‌نوشت‌ها: **T** = https://wikipedia2book.toolforge.org. در نشانی‌های API، `language` زبان عنوان‌های ساخته‌شده در PDF (جلد، فهرست مطالب، مجوز) و `wiki` زبان عنوان‌های بدون پیشوند است.

## 1. یک صفحه

| شماره | مورد | مرورگر: چه وارد کنید | API | نتیجهٔ مورد انتظار | نسخه |
|---|---|---|---|---|---|
| 1.1 | نشانی یک مقالهٔ ویکی‌پدیا | `https://fr.wikipedia.org/wiki/Épaves_de_la_rade_de_Saint-Pierre` | `T/api/pdf/from-source?source=https://fr.wikipedia.org/wiki/%C3%89paves_de_la_rade_de_Saint-Pierre` | مقاله افزوده می‌شود؛ با نخستین مقاله، مقدمه و نویسنده پیشنهاد می‌شوند | ≤ 1.9.7 |
| 1.2 | عنوان دقیق | `Montagne Pelée` (زبان FR کنار فیلد) | `T/api/pdf/from-source?source=Montagne%20Pel%C3%A9e&wiki=fr` | مقالهٔ «Montagne Pelée» افزوده می‌شود | ≤ 1.9.7 |
| 1.3 | عنوان تغییرمسیر داده‌شده | `Napoléon Bonaparte` | `T/api/pdf/from-source?source=Napol%C3%A9on%20Bonaparte&wiki=fr` | تغییرمسیر دنبال می‌شود: «Napoléon Ier» افزوده می‌شود | ≤ 1.9.7 |
| 1.4 | عنوان بدون صفحهٔ دقیق | `volcan martinique` | `T/api/sources/resolve` با `POST` (نگاه کنید به 9.1): `kind` = `search` | نتایج جست‌وجو زیر فیلد نمایش داده می‌شوند و با یک کلیک افزوده می‌شوند؛ API ساخت با متن مربوط پاسخ 404 می‌دهد | ≤ 1.9.7 |
| 1.5 | جست‌وجو هنگام تایپ | `Saint-Pie` را بدون تأیید تایپ کنید | `T/api/search?query=Saint-Pie&language=fr` | پیشنهادها زیر فیلد | ≤ 1.9.7 |
| 1.6 | عنوان به زبانی دیگر | `nl:Rotterdam` | `T/api/pdf/from-source?source=nl:Rotterdam` | مقالهٔ هلندی با نشان «NL» افزوده می‌شود | 1.7.0 |
| 1.7 | همهٔ زبان‌ها | `Paris`، با «همه» برگزیده در کنار فیلد | `T/api/search?query=Paris&language=all&limit=3` | نتایج به هر زبان فهرست، هر یک با نشان زبانش؛ مقالهٔ برگزیده زبان خود را نگه می‌دارد | 1.12.4 |

## 2. دیگر پروژه‌های ویکی‌مدیا

| شماره | مورد | مرورگر: چه وارد کنید | API | نتیجهٔ مورد انتظار | نسخه |
|---|---|---|---|---|---|
| 2.1 | صفحهٔ ویکی‌سفر | `https://fr.wikivoyage.org/wiki/Lyon` | `T/api/pdf/from-source?source=https://fr.wikivoyage.org/wiki/Lyon` | صفحه افزوده می‌شود، کارت با نشان «ویکی‌سفر» | 1.8.0 |
| 2.2 | پیشوند پروژه و زبان | `[[voy:en:Lyon]]` | `T/api/pdf/from-source?source=voy:en:Lyon` | صفحهٔ انگلیسی ویکی‌سفر افزوده می‌شود | 1.8.0 |
| 2.3 | ویکی‌دانشگاه | `https://fr.wikiversity.org/wiki/Python` | `T/api/pdf/from-source?source=v:Python&wiki=fr` | صفحه افزوده می‌شود، با نشان «ویکی‌دانشگاه» | 1.8.0 |
| 2.4 | ویکی‌گفتاورد | `https://fr.wikiquote.org/wiki/Victor_Hugo` | `T/api/pdf/from-source?source=q:Victor%20Hugo&wiki=fr` | صفحه افزوده می‌شود، با نشان «ویکی‌گفتاورد» | 1.8.0 |
| 2.5 | ویکی‌واژه، پیشوندها به ترتیب وارونه | `fr:wikt:chat` | `T/api/pdf/from-source?source=fr:wikt:chat` | صفحه افزوده می‌شود، با نشان «ویکی‌واژه» | 1.8.0 |
| 2.6 | ویکی‌خبر | `https://fr.wikinews.org/wiki/Accueil` | `T/api/pdf/from-source?source=https://fr.wikinews.org/wiki/Accueil` | صفحه افزوده می‌شود، با نشان «ویکی‌خبر» | 1.8.0 |
| 2.7 | متن ویکی‌نبشته (یک صفحه) | `https://zh.wikisource.org/wiki/論語/學而第一` | `T/api/pdf/from-source?source=https://zh.wikisource.org/wiki/%E8%AB%96%E8%AA%9E/%E5%AD%B8%E8%80%8C%E7%AC%AC%E4%B8%80` | صفحه افزوده می‌شود؛ عنوان‌های چینی در PDF خوانا هستند | 1.7.8 |
| 2.8 | صفحهٔ نویسنده در ویکی‌نبشته | `https://fr.wikisource.org/wiki/Auteur:François_Rabelais` | `T/api/pdf/from-source?source=https://fr.wikisource.org/wiki/Auteur:Fran%C3%A7ois_Rabelais` | صفحه همان‌گونه که هست افزوده می‌شود (زندگی‌نامه و فهرست آثار) | 1.8.1 |

## 3. کتاب‌ها

| شماره | مورد | مرورگر: چه وارد کنید | API | نتیجهٔ مورد انتظار | نسخه |
|---|---|---|---|---|---|
| 3.1 | صفحهٔ کتاب ویکی‌پدیا با نشانی | `https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique` | `T/api/books/generate-from-wikipedia-book?url=https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique` | 113 مقاله به ترتیب صفحه، فصل‌های `;`، زیرعنوان `===`؛ عنوان «Martinique» | 1.3.0 |
| 3.2 | صفحهٔ کتاب با نامش | `Utilisateur:Alexbzh972/Livres/Martinique` | `T/api/pdf/from-source?source=Utilisateur:Alexbzh972/Livres/Martinique` | همان نتیجهٔ 3.1 | 1.3.0 |
| 3.3 | فهرست یک کتاب ویکی‌کتاب | `https://fr.wikibooks.org/wiki/Cosmologie` | `T/api/pdf/from-source?source=b:Cosmologie&wiki=fr` | پنجرهٔ «کل کتاب / کل کتاب و فهرست آن / فقط همین صفحه / لغو»؛ «کل کتاب» 27 صفحه در فصل‌ها می‌دهد | 1.10.0 |
| 3.4 | کل کتاب با فهرستش | مانند 3.3، «کل کتاب و فهرست آن» را برگزینید | `T/api/pdf/from-source?source=b:Cosmologie&wiki=fr&summary=1` | صفحهٔ فهرست نخست، پیش از فصل اول | 1.10.0 |
| 3.5 | فقط صفحهٔ فهرست | مانند 3.3، «فقط همین صفحه» را برگزینید | `POST /api/pdf` فقط با صفحهٔ فهرست (نگاه کنید به 9.3) | صفحهٔ فهرست به تنهایی | 1.10.0 |
| 3.6 | اثری در ویکی‌نبشته | `s:Les Misérables` (زبان FR) | `T/api/pdf/from-source?source=s:Les%20Mis%C3%A9rables&wiki=fr` | پنجرهٔ انتخاب؛ «کل کتاب» 365 فصل در 5 بخش می‌دهد، بدون «Texte entier» | 1.11.0 |
| 3.7 | نسخهٔ چاپی دست‌نوشته (نشانی) | `https://fr.wikibooks.org/wiki/Hélices_de_navires_à_déplacement/Version_imprimable` | `T/api/pdf/from-source?source=https://fr.wikibooks.org/wiki/H%C3%A9lices_de_navires_%C3%A0_d%C3%A9placement/Version_imprimable` | 13 صفحه، یک فصل برای هر عنوان `= … =`، بدون جلد، عنوان «Hélices de navires à déplacement» | 1.12.0 |
| 3.8 | نسخهٔ چاپی با `{{imprimable}}` (نشانی) | `https://fr.wikibooks.org/wiki/Programmation_C/Version_imprimable` | `T/api/pdf/from-source?source=https://fr.wikibooks.org/wiki/Programmation_C/Version_imprimable` | پنجرهٔ انتخاب برای فهرست «Programmation C» (21 صفحه) | 1.12.0 |

## 4. فهرست صفحه‌ها (چند خط)

همهٔ خط‌ها را یک‌جا در فیلد بچسبانید (یا با Shift+Enter جدا کنید). در API، `source=` را تکرار کنید (حداکثر 50).

| شماره | مورد | خطی که وارد می‌شود | نتیجهٔ مورد انتظار | نسخه |
|---|---|---|---|---|
| 4.1 | پیوند ویکی | `[[Brest]]` | «Brest» افزوده می‌شود | 1.7.0 |
| 4.2 | پیوند ویکی با زبان | `[[nl:Amsterdam]]` | مقالهٔ هلندی افزوده می‌شود | 1.7.0 |
| 4.3 | پیوند ویکی با متن | `[[Frégate (bateau)\|Frégate]]` | «Frégate (bateau)» افزوده می‌شود | 1.7.0 |
| 4.4 | پیوند مارک‌داون، پرانتز در نشانی | `[Suchet](https://fr.wikipedia.org/wiki/Suchet_(navire))` | «Suchet (navire)» افزوده می‌شود | 1.7.0 |
| 4.5 | شماره در آغاز خط | `1. Lorient` | «Lorient» افزوده می‌شود | 1.7.0 |
| 4.6 | گلوله در آغاز خط | `* Concarneau` (همچنین `-`، `•`، `#`) | «Concarneau» افزوده می‌شود | 1.7.0 |
| 4.7 | خط یافت‌نشده | `Xyzzy inexistant` | خط در فیلد می‌ماند و پیام پایانی آن را «یافت نشد» می‌شمارد | 1.7.0 |
| 4.8 | فهرست کتاب درون یک فهرست | `b:Programmation Python` | پنجرهٔ انتخاب برای آن فهرست باز می‌شود؛ فصل‌هایش نگه داشته نمی‌شوند | 1.10.0 |

فهرست کامل برای چسباندن در مرورگر:

```
[[Brest]]
[[nl:Amsterdam]]
[Suchet](https://fr.wikipedia.org/wiki/Suchet_(navire))
1. Lorient
* Concarneau
[[voy:en:Lyon]]
fr:wikt:chat
```

نتیجهٔ مورد انتظار: «7 صفحه افزوده شد، 0 صفحه از قبل در کتاب بود، 0 صفحه یافت نشد.»

API، همان فهرست: `T/api/pdf/from-source?source=[[Brest]]&source=[[nl:Amsterdam]]&source=1.%20Lorient&source=*%20Concarneau&source=[[voy:en:Lyon]]&source=fr:wikt:chat&wiki=fr`

## 5. متن کتاب چسبانده‌شده

| شماره | مورد | متنی که چسبانده می‌شود | API | نتیجهٔ مورد انتظار | نسخه |
|---|---|---|---|---|---|
| 5.1 | نحو «کتاب:» ویکی‌پدیا | بلوک 5.1 در پایین | `curl` 5.1 در پایین | عنوان «Ports bretons»، زیرعنوان «Guide des ports»، فصل‌های «Finistère» و «Morbihan»، «Brest» در آغاز بدون فصل | 1.12.0 |
| 5.2 | نسخهٔ چاپی ویکی‌کتاب | بلوک 5.2 در پایین | `curl` 5.2 در پایین | 3 صفحهٔ ویکی‌کتاب در 3 فصل، بدون مجوز | 1.12.0 |

بلوک 5.1:

```
== Ports bretons ==
=== Guide des ports ===
:[[Brest]]
;Finistère
:[[Concarneau]]
:[[Douarnenez]]
;Morbihan
:[[Lorient]]
```

```bash
curl -OJ -X POST 'https://wikipedia2book.toolforge.org/api/pdf/from-wikitext?language=fr' \
	-H 'Content-Type: application/json' \
	--data '{"wikitext":"== Ports bretons ==\n=== Guide des ports ===\n:[[Brest]]\n;Finistère\n:[[Concarneau]]\n:[[Douarnenez]]\n;Morbihan\n:[[Lorient]]","language":"fr"}'
```

بلوک 5.2:

```
= Le paradoxe d'Olbers =
{{:Cosmologie/Le paradoxe d'Olbers}}
= L'expansion de l'univers =
{{:Cosmologie/L'expansion de l'univers}}
= Le facteur de Hubble =
{{:Cosmologie/Le facteur de Hubble}}
{{:Licence de documentation libre GNU}}
```

```bash
curl -OJ -X POST 'https://wikipedia2book.toolforge.org/api/pdf/from-wikitext?language=fr' \
	-H 'Content-Type: application/json' \
	--data "{\"wikitext\":\"= Le paradoxe d'Olbers =\n{{:Cosmologie/Le paradoxe d'Olbers}}\n= L'expansion de l'univers =\n{{:Cosmologie/L'expansion de l'univers}}\n= Le facteur de Hubble =\n{{:Cosmologie/Le facteur de Hubble}}\n{{:Licence de documentation libre GNU}}\",\"language\":\"fr\"}"
```

برای خواندن ساختار به تنهایی، بدون PDF: همان محتوا را به `POST /api/books/from-wikitext` بفرستید.

## 6. باز کردن کتاب ذخیره‌شده (JSON)

| شماره | مورد | مرورگر | API | نتیجهٔ مورد انتظار | نسخه |
|---|---|---|---|---|---|
| 6.1 | کتاب JSON با نشانی | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Wrecks-of-Saint-Pierre-harbor.json` | `T/api/pdf/from-json?url=https://gmoulard.github.io/wikipedia2book/static/Wrecks-of-Saint-Pierre-harbor.json&language=en` | کتاب با تصویرهای پس‌زمینه و سندش باز می‌شود («کتاب وارد شد.») | 1.9.6 |
| 6.2 | کتاب ویکی‌کتاب به صورت JSON | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json` | `T/api/pdf/from-json?url=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json` | 27 صفحه در 8 فصل | 1.9.6 |
| 6.3 | پروندهٔ JSON محلی | دکمهٔ «باز کردن»، پرونده‌ای را که با «ذخیره» برون‌برد شده برگزینید | `curl -OJ -X POST 'T/api/pdf/from-json' -H 'Content-Type: application/json' --data @book.json` | کتاب باز می‌شود / PDF ساخته می‌شود | ≤ 1.9.7 (مرورگر)، 1.12.0 (API) |
| 6.4 | JSON و سپس منابع دیگر | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json&source=b:Programmation%20Python` | — | کتاب JSON باز می‌شود، سپس پنجرهٔ انتخاب برای فهرست افزوده‌شده | 1.12.0 |
| 6.5 | منابع در نشانی صفحه | `T/?source=https://fr.wikibooks.org/wiki/Cosmologie&source=Montagne%20Pel%C3%A9e&wiki=fr` | نگاه کنید به 3.3 و 1.2 | هر منبع گویی تایپ شده افزوده می‌شود، همراه با پرسش | 1.12.0 |
| 6.6 | نشانی ردشده | `T/?json=http://example.com/livre.json` | `T/api/pdf/from-json?url=http://example.com/livre.json` | پیام خطا، چیزی وارد نمی‌شود؛ API پاسخ 422 «doit commencer par https://» می‌دهد | 1.9.6 |

## 7. سندها و تصویرهای پس‌زمینه

| شماره | مورد | مرورگر | API (فیلد کتاب JSON) | نتیجهٔ مورد انتظار | نسخه |
|---|---|---|---|---|---|
| 7.1 | تصویر یا PDF از رایانه | مرحلهٔ سازماندهی، «انتخاب فایل +» | `uploaded_documents[]` با `data_base64` | سند مانند یک مقاله در کتاب جای می‌گیرد، حداکثر 15 مگابایت | ≤ 1.9.7 |
| 7.2 | سند با نشانی | مرحلهٔ سازماندهی، فیلد نشانی: `https://upload.wikimedia.org/wikipedia/commons/1/16/La_Pel%C3%A9e_vue_du_Carbet.jpg` | `uploaded_documents[]` با `"url": "https://upload.wikimedia.org/…"` | فقط نشانی نگه داشته می‌شود؛ کارساز تصویر را در هر ساخت بارگیری می‌کند | 1.10.0 |
| 7.3 | سند با صفحهٔ پروندهٔ ویکی‌انبار | `https://commons.wikimedia.org/wiki/File:La_Pelée_vue_du_Carbet.jpg` | `"url": "https://commons.wikimedia.org/wiki/File:La_Pel%C3%A9e_vue_du_Carbet.jpg"` | تصویر (پیش‌نمایش 2 000 پیکسلی) به کار می‌رود؛ برای PDF، پروندهٔ اصلی | 1.10.0 (مرورگر)، 1.12.0 (API) |
| 7.4 | PDF با صفحهٔ پرونده | `https://commons.wikimedia.org/wiki/File:Interpersonal_communication_and_coordination_in_Wikipedia_Working_Paper_30_June_2020.pdf` | همان نشانی در `uploaded_documents[].url` | PDF اصلی درج می‌شود، صفحه‌ها با قطع کتاب هماهنگ می‌شوند | 1.10.0 (مرورگر)، 1.12.0 (API) |
| 7.5 | تصویر پس‌زمینهٔ جلد | مرحلهٔ ویرایش، «تصویر پس‌زمینهٔ جلد»، پرونده یا نشانی (7.2 یا 7.3) | `cover_image`: `{"title": "…", "url": "…"}` یا `data_base64` | پس‌زمینهٔ جلد، بدون کج‌شدگی | 1.9.6 |
| 7.6 | تصویر صفحهٔ آخر | مرحلهٔ ویرایش، «تصویر پس‌زمینهٔ صفحهٔ آخر» | `back_image` | صفحه‌ای جداگانه پس از مجوز | 1.9.6 |
| 7.7 | نشانی دسترس‌ناپذیر | سند `https://example.org/inexistant.png` | همان نشانی | ساخت متوقف می‌شود و نشانی مربوط ذکر می‌شود؛ 502 از راه API | 1.10.0 |

## 8. سازماندهی و صفحه‌آرایی

| شماره | مورد | مرورگر | API (کتاب JSON به `POST /api/pdf`) | نتیجهٔ مورد انتظار | نسخه |
|---|---|---|---|---|---|
| 8.1 | مقاله‌های مرتبط | دکمهٔ «مقاله‌های مرتبط» یک مقاله | `POST /api/explore` | پیوندهای مقاله به ترتیب صفحه پیشنهاد می‌شوند | ≤ 1.9.7 |
| 8.2 | فصل‌ها و ترتیب | مرحلهٔ سازماندهی، «ساخت فصل»، کشیدن و رها کردن | `chapters`، `article_order`، `unassigned_first` | PDF از ترتیب نمایش‌داده‌شده پیروی می‌کند | ≤ 1.9.7 |
| 8.3 | فهرست مطالب | مرحلهٔ ویرایش: هیچ، آغاز، پایان | `table_of_contents`، `toc_position` (`start`، `end`، `before:<کلید>`) | فهرست در جای درست، پیوندهای کلیک‌پذیر | 1.9.6 |
| 8.4 | قطع، جهت، حاشیه‌ها | مرحلهٔ ویرایش | `page_format`، `orientation`، `margin_*_mm`، `custom_width_mm` | همهٔ صفحه‌ها در قطع برگزیده | ≤ 1.9.7 |
| 8.5 | شمارهٔ صفحه | «شماره‌گذاری صفحه‌ها» | `page_numbers` | شماره در پایین صفحه، به جز جلد | ≤ 1.9.7 |
| 8.6 | زبان عنوان‌های PDF | انتخاب زبان در بالا | پارامتر `language` (12 زبان) | جلد، فهرست، مجوز به زبان برگزیده | ≤ 1.9.7 |
| 8.7 | جداسازی دستی جلدها | مرحلهٔ سازماندهی، «جلد جدید» | `volume_breaks`: `["before:<کلید>"]`، سپس `?volume=N` | یک PDF برای هر جلد، شماره‌گذاری از 1 از نو | 1.9.2 (مرورگر)، 1.12.0 (API) |
| 8.8 | بیش از 300 مقاله | کتاب 3.1 + صفحه‌های دیگر تا بیش از 300 | `POST /api/books/volumes` برای طرح، سپس `POST /api/pdf?volume=1`، `?volume=2`… | جداسازی خودکار میان فصل‌ها، «جلد 1 از 2»…؛ بدون `volume`، رد 413 همراه با شمار جلدها | 1.9.0 (مرورگر)، 1.12.0 (API) |

## 9. فراخوانی‌های API بدون PDF

| شماره | مورد | فراخوانی | نتیجهٔ مورد انتظار |
|---|---|---|---|
| 9.1 | شناسایی یک ورودی | `curl -X POST 'T/api/sources/resolve' -H 'Content-Type: application/json' --data '{"input":"volcan martinique","language":"fr"}'` | `kind`: `article`، `book`، `subpages` یا `search` |
| 9.2 | ساختار صفحهٔ کتاب | `curl -X POST 'T/api/books/structure' -H 'Content-Type: application/json' --data '{"url":"https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique"}'` | مقاله‌ها، زیرعنوان، فصل‌ها |
| 9.3 | PDF کتابی که با JSON توصیف شده | `curl -OJ -X POST 'T/api/pdf?language=fr' -H 'Content-Type: application/json' --data '{"name":"Test","main_articles":[{"title":"Cosmologie","language":"fr","site":"wikibooks","url":"https://fr.wikibooks.org/wiki/Cosmologie","selected":true}]}'` | PDF تنها یک صفحهٔ فهرست |
| 9.4 | دنبال کردن ساخت | همان محتوا به `POST /api/pdf/stream` | خط‌های NDJSON `progress`، `wait`، سپس `done` و PDF |
| 9.5 | مقدمه و نویسندهٔ پیشنهادی | `T/api/articles/intro?title=Montagne%20Pel%C3%A9e&language=fr` | نخستین بند و سازندهٔ صفحه |
| 9.6 | نسخهٔ در حال اجرا | `T/api/version` | نسخه، کامیت، سقف مقاله‌ها |

## 10. ورودی‌های ردشده

پیام‌های خطا از کارساز می‌آیند و به هر زبانی که رابط باشد، فرانسوی می‌مانند.

| شماره | ورودی | نتیجهٔ مورد انتظار |
|---|---|---|
| 10.1 | `https://example.com/wiki/Chat` | «L'URL doit pointer vers une page HTTPS d'un projet Wikimédia…»؛ 422 |
| 10.2 | `https://fr.wikibooks.org/wiki/Wikilivres:Le_Bistro` | «Seules les pages de contenu de fr.wikibooks.org…»؛ 422 |
| 10.3 | `https://commons.wikimedia.org/wiki/File:La_Pelée_vue_du_Carbet.jpg` در فیلد منابع | به عنوان منبع رد می‌شود (ویکی‌انبار نشانی `<زبان>.<پروژه>.org` ندارد)؛ به عنوان سند یا تصویر پس‌زمینه پذیرفته می‌شود (7.3) |
| 10.4 | `https://fr.wikipedia.org/wiki/Page_qui_n_existe_pas` | «La page … est introuvable»؛ 404 |
| 10.5 | فیلد خالی | «Saisissez …»؛ 422 |
| 10.6 | کتابی بی هیچ مقالهٔ برگزیده، سپس «ساخت PDF» | پیام «پیش از ساخت PDF دست‌کم یک مقاله را برگزینید.»؛ 400 |
