# مساعدة حقل «بناء الكتاب»: كل ما يقبله Wikipedia2Book

تسرد هذه الصفحة كل ما يقبله Wikipedia2Book، مع مثال لكل حالة يُجرَّب **في المتصفح** والحالة نفسها **عبر واجهة البرمجة (API)**. لها غرضان: عرض الإمكانات، وإجراء تحقق يدوي قبل نشر إصدار. وهي ترجمة [للصفحة المرجعية بالفرنسية](helpSearch.fr.md).

السلوك المرجعي موصوف في [المواصفات الوظيفية](FunctionalSpec.en.md) (القسم 3.1 للمصادر) و[المواصفات التقنية](TechnicalSpec.en.md) (القسم 13.3 لواجهة البرمجة).

## طريقة الاستخدام

- **المتصفح**: افتح https://wikipedia2book.toolforge.org/ ، والصق المثال في حقل خطوة «بناء الكتاب»، ثم انقر «إضافة». العنوان الذي يبدأ بـ `https://wikipedia2book.toolforge.org/?` يُفتح مباشرة.
- **واجهة البرمجة**: افتح العنوان في المتصفح (يُنزَّل ملف PDF) أو مرّره إلى `curl -OJ`. تُعطى استدعاءات `POST` في صورة أوامر `curl`.
- **الإصدار**: إصدار التطبيق الذي تعمل الحالة ابتداءً منه. الإصدار المنشور يظهر في https://wikipedia2book.toolforge.org/api/version .
- عمود «الإصدار» خاص بالمتصفح. في واجهة البرمجة، `GET /api/pdf/from-source` (الأقسام 1 إلى 4) والمعامل `?source=` للصفحة متاحان منذ 1.12.0 (في بيئة الإنتاج منذ مساء 16 نوفمبر 2026، قبل أن يحملا هذا الرقم): مع إصدار أقدم، أرسل الكتاب بصيغة JSON إلى `POST /api/pdf` (9.3) بعد التعرف على كل مُدخل عبر `POST /api/sources/resolve` (9.1).
- تم التحقق من الأمثلة في 17 نوفمبر 2026 باستخدام شيفرة التعرف على المصادر مقابل الويكيات الحقيقية؛ قد تتغير النتيجة إذا أُعيدت تسمية صفحة أو حُذفت منذ ذلك الحين.

اختصارات: **T** = https://wikipedia2book.toolforge.org . في عناوين واجهة البرمجة، `language` هي لغة العناوين المولّدة في ملف PDF (الغلاف، الفهرس، الترخيص)، و`wiki` لغة العناوين التي بلا بادئة.

## 1. صفحة واحدة

| الرقم | الحالة | المتصفح: ما يُدخَل | واجهة البرمجة | النتيجة المتوقعة | الإصدار |
|---|---|---|---|---|---|
| 1.1 | عنوان URL لمقالة في ويكيبيديا | `https://fr.wikipedia.org/wiki/Épaves_de_la_rade_de_Saint-Pierre` | `T/api/pdf/from-source?source=https://fr.wikipedia.org/wiki/%C3%89paves_de_la_rade_de_Saint-Pierre` | تُضاف المقالة؛ ويُقترح المقدمة والمؤلف مع أول مقالة | ≤ 1.9.7 |
| 1.2 | عنوان مطابق | `Montagne Pelée` (اللغة FR بجانب الحقل) | `T/api/pdf/from-source?source=Montagne%20Pel%C3%A9e&wiki=fr` | تُضاف مقالة «Montagne Pelée» | ≤ 1.9.7 |
| 1.3 | عنوان مُحوَّل | `Napoléon Bonaparte` | `T/api/pdf/from-source?source=Napol%C3%A9on%20Bonaparte&wiki=fr` | يُتبَع التحويل: تُضاف «Napoléon Ier» | ≤ 1.9.7 |
| 1.4 | عنوان بلا صفحة مطابقة | `volcan martinique` | `T/api/sources/resolve` بطريقة `POST` (انظر 9.1): `kind` = `search` | تظهر نتائج البحث تحت الحقل وتُضاف بنقرة؛ وتردّ واجهة التوليد بالرمز 404 مع النص المعني | ≤ 1.9.7 |
| 1.5 | البحث أثناء الكتابة | اكتب `Saint-Pie` دون تأكيد | `T/api/search?query=Saint-Pie&language=fr` | اقتراحات تحت الحقل | ≤ 1.9.7 |
| 1.6 | عنوان بلغة أخرى | `nl:Rotterdam` | `T/api/pdf/from-source?source=nl:Rotterdam` | تُضاف المقالة الهولندية موسومة بـ «NL» | 1.7.0 |
| 1.7 | كل اللغات | `Paris` مع اختيار «الكل» بجانب الحقل | `T/api/search?query=Paris&language=all&limit=3` | نتائج بكل لغة في القائمة، كل منها موسوم بلغته؛ وتحتفظ المقالة المختارة بلغتها | 1.12.4 |

## 2. مشاريع ويكيميديا الأخرى

| الرقم | الحالة | المتصفح: ما يُدخَل | واجهة البرمجة | النتيجة المتوقعة | الإصدار |
|---|---|---|---|---|---|
| 2.1 | صفحة من ويكي رحلات | `https://fr.wikivoyage.org/wiki/Lyon` | `T/api/pdf/from-source?source=https://fr.wikivoyage.org/wiki/Lyon` | تُضاف الصفحة، والبطاقة موسومة بـ «ويكي رحلات» | 1.8.0 |
| 2.2 | بادئة المشروع واللغة | `[[voy:en:Lyon]]` | `T/api/pdf/from-source?source=voy:en:Lyon` | تُضاف صفحة ويكي رحلات الإنجليزية | 1.8.0 |
| 2.3 | ويكي الجامعة | `https://fr.wikiversity.org/wiki/Python` | `T/api/pdf/from-source?source=v:Python&wiki=fr` | تُضاف الصفحة موسومة بـ «ويكي الجامعة» | 1.8.0 |
| 2.4 | ويكي الاقتباس | `https://fr.wikiquote.org/wiki/Victor_Hugo` | `T/api/pdf/from-source?source=q:Victor%20Hugo&wiki=fr` | تُضاف الصفحة موسومة بـ «ويكي الاقتباس» | 1.8.0 |
| 2.5 | ويكاموس، البادئات بترتيب معكوس | `fr:wikt:chat` | `T/api/pdf/from-source?source=fr:wikt:chat` | تُضاف الصفحة موسومة بـ «ويكاموس» | 1.8.0 |
| 2.6 | ويكي الأخبار | `https://fr.wikinews.org/wiki/Accueil` | `T/api/pdf/from-source?source=https://fr.wikinews.org/wiki/Accueil` | تُضاف الصفحة موسومة بـ «ويكي الأخبار» | 1.8.0 |
| 2.7 | نص من ويكي مصدر (صفحة واحدة) | `https://zh.wikisource.org/wiki/論語/學而第一` | `T/api/pdf/from-source?source=https://zh.wikisource.org/wiki/%E8%AB%96%E8%AA%9E/%E5%AD%B8%E8%80%8C%E7%AC%AC%E4%B8%80` | تُضاف الصفحة؛ والعناوين الصينية مقروءة في ملف PDF | 1.7.8 |
| 2.8 | صفحة مؤلف في ويكي مصدر | `https://fr.wikisource.org/wiki/Auteur:François_Rabelais` | `T/api/pdf/from-source?source=https://fr.wikisource.org/wiki/Auteur:Fran%C3%A7ois_Rabelais` | تُضاف الصفحة كما هي (سيرة وقائمة أعمال) | 1.8.1 |

## 3. الكتب

| الرقم | الحالة | المتصفح: ما يُدخَل | واجهة البرمجة | النتيجة المتوقعة | الإصدار |
|---|---|---|---|---|---|
| 3.1 | صفحة كتاب في ويكيبيديا عبر URL | `https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique` | `T/api/books/generate-from-wikipedia-book?url=https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique` | 113 مقالة بترتيب الصفحة، فصول `;`، عنوان فرعي `===`؛ العنوان «Martinique» | 1.3.0 |
| 3.2 | صفحة كتاب باسمها | `Utilisateur:Alexbzh972/Livres/Martinique` | `T/api/pdf/from-source?source=Utilisateur:Alexbzh972/Livres/Martinique` | النتيجة نفسها في 3.1 | 1.3.0 |
| 3.3 | فهرس كتاب في ويكي الكتب | `https://fr.wikibooks.org/wiki/Cosmologie` | `T/api/pdf/from-source?source=b:Cosmologie&wiki=fr` | نافذة «الكتاب كاملًا / الكتاب كاملًا مع فهرسه / هذه الصفحة فقط / إلغاء»؛ «الكتاب كاملًا» يعطي 27 صفحة في فصول | 1.10.0 |
| 3.4 | الكتاب كاملًا مع فهرسه | كما في 3.3، اختر «الكتاب كاملًا مع فهرسه» | `T/api/pdf/from-source?source=b:Cosmologie&wiki=fr&summary=1` | صفحة الفهرس أولًا، قبل الفصل الأول | 1.10.0 |
| 3.5 | صفحة الفهرس وحدها | كما في 3.3، اختر «هذه الصفحة فقط» | `POST /api/pdf` بصفحة الفهرس وحدها (انظر 9.3) | صفحة الفهرس وحدها | 1.10.0 |
| 3.6 | عمل في ويكي مصدر | `s:Les Misérables` (اللغة FR) | `T/api/pdf/from-source?source=s:Les%20Mis%C3%A9rables&wiki=fr` | نافذة الاختيار؛ «الكتاب كاملًا» يعطي 365 فصلًا في 5 أجزاء، دون «Texte entier» | 1.11.0 |
| 3.7 | نسخة للطباعة مكتوبة يدويًا (عنوان) | `https://fr.wikibooks.org/wiki/Hélices_de_navires_à_déplacement/Version_imprimable` | `T/api/pdf/from-source?source=https://fr.wikibooks.org/wiki/H%C3%A9lices_de_navires_%C3%A0_d%C3%A9placement/Version_imprimable` | 13 صفحة، فصل لكل عنوان `= … =`، دون غلاف، العنوان «Hélices de navires à déplacement» | 1.12.0 |
| 3.8 | نسخة للطباعة عبر `{{imprimable}}` (عنوان) | `https://fr.wikibooks.org/wiki/Programmation_C/Version_imprimable` | `T/api/pdf/from-source?source=https://fr.wikibooks.org/wiki/Programmation_C/Version_imprimable` | نافذة الاختيار لفهرس «Programmation C» (21 صفحة) | 1.12.0 |

## 4. قوائم الصفحات (عدة أسطر)

الصق كل الأسطر دفعة واحدة في الحقل (أو افصل بينها بـ Shift+Enter). في واجهة البرمجة، كرّر `source=` (50 على الأكثر).

| الرقم | الحالة | السطر المُدخل | النتيجة المتوقعة | الإصدار |
|---|---|---|---|---|
| 4.1 | رابط ويكي | `[[Brest]]` | تُضاف «Brest» | 1.7.0 |
| 4.2 | رابط ويكي مع لغة | `[[nl:Amsterdam]]` | تُضاف المقالة الهولندية | 1.7.0 |
| 4.3 | رابط ويكي مع نص | `[[Frégate (bateau)\|Frégate]]` | تُضاف «Frégate (bateau)» | 1.7.0 |
| 4.4 | رابط Markdown، أقواس في العنوان | `[Suchet](https://fr.wikipedia.org/wiki/Suchet_(navire))` | تُضاف «Suchet (navire)» | 1.7.0 |
| 4.5 | رقم في بداية السطر | `1. Lorient` | تُضاف «Lorient» | 1.7.0 |
| 4.6 | تعداد نقطي في بداية السطر | `* Concarneau` (وأيضًا `-` و`•` و`#`) | تُضاف «Concarneau» | 1.7.0 |
| 4.7 | سطر غير موجود | `Xyzzy inexistant` | يبقى السطر في الحقل، وتعدّه الرسالة الختامية «غير موجود» | 1.7.0 |
| 4.8 | فهرس داخل قائمة | `b:Programmation Python` | تُفتح نافذة الاختيار لذلك الفهرس؛ ولا تُؤخذ فصوله | 1.10.0 |

القائمة الكاملة للصقها في المتصفح:

```
[[Brest]]
[[nl:Amsterdam]]
[Suchet](https://fr.wikipedia.org/wiki/Suchet_(navire))
1. Lorient
* Concarneau
[[voy:en:Lyon]]
fr:wikt:chat
```

النتيجة المتوقعة: «أُضيفت 7 صفحة، و0 موجودة مسبقًا في الكتاب، و0 غير موجودة.»

واجهة البرمجة، القائمة نفسها: `T/api/pdf/from-source?source=[[Brest]]&source=[[nl:Amsterdam]]&source=1.%20Lorient&source=*%20Concarneau&source=[[voy:en:Lyon]]&source=fr:wikt:chat&wiki=fr`

## 5. نص كتاب ملصوق

| الرقم | الحالة | النص الملصوق | واجهة البرمجة | النتيجة المتوقعة | الإصدار |
|---|---|---|---|---|---|
| 5.1 | صيغة «كتاب:» في ويكيبيديا | الكتلة 5.1 أدناه | أمر `curl` 5.1 أدناه | العنوان «Ports bretons»، العنوان الفرعي «Guide des ports»، الفصلان «Finistère» و«Morbihan»، و«Brest» في البداية بلا فصل | 1.12.0 |
| 5.2 | نسخة للطباعة من ويكي الكتب | الكتلة 5.2 أدناه | أمر `curl` 5.2 أدناه | 3 صفحات من ويكي الكتب في 3 فصول، دون الترخيص | 1.12.0 |

الكتلة 5.1:

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

الكتلة 5.2:

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

لقراءة البنية وحدها دون PDF: أرسل المحتوى نفسه إلى `POST /api/books/from-wikitext`.

## 6. فتح كتاب محفوظ (JSON)

| الرقم | الحالة | المتصفح | واجهة البرمجة | النتيجة المتوقعة | الإصدار |
|---|---|---|---|---|---|
| 6.1 | كتاب JSON عبر عنوان | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Wrecks-of-Saint-Pierre-harbor.json` | `T/api/pdf/from-json?url=https://gmoulard.github.io/wikipedia2book/static/Wrecks-of-Saint-Pierre-harbor.json&language=en` | يُفتح الكتاب («استُورد الكتاب.») مع صور الخلفية والمستند | 1.9.6 |
| 6.2 | كتاب من ويكي الكتب بصيغة JSON | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json` | `T/api/pdf/from-json?url=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json` | 27 صفحة في 8 فصول | 1.9.6 |
| 6.3 | ملف JSON محلي | زر «فتح»، ثم اختر ملفًا صُدِّر عبر «حفظ» | `curl -OJ -X POST 'T/api/pdf/from-json' -H 'Content-Type: application/json' --data @book.json` | يُفتح الكتاب / يُولَّد ملف PDF | ≤ 1.9.7 (المتصفح)، 1.12.0 (واجهة البرمجة) |
| 6.4 | JSON ثم مصادر أخرى | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json&source=b:Programmation%20Python` | — | يُفتح كتاب JSON، ثم نافذة الاختيار للفهرس المضاف | 1.12.0 |
| 6.5 | مصادر في عنوان الصفحة | `T/?source=https://fr.wikibooks.org/wiki/Cosmologie&source=Montagne%20Pel%C3%A9e&wiki=fr` | انظر 3.3 و1.2 | يُضاف كل مصدر كأنه كُتب، بما في ذلك السؤال | 1.12.0 |
| 6.6 | عنوان مرفوض | `T/?json=http://example.com/livre.json` | `T/api/pdf/from-json?url=http://example.com/livre.json` | رسالة خطأ، ولا يُستورد شيء؛ وتردّ واجهة البرمجة بالرمز 422 «doit commencer par https://» | 1.9.6 |

## 7. المستندات وصور الخلفية

| الرقم | الحالة | المتصفح | واجهة البرمجة (حقل في كتاب JSON) | النتيجة المتوقعة | الإصدار |
|---|---|---|---|---|---|
| 7.1 | صورة أو PDF من الحاسوب | خطوة التنظيم، «اختيار ملف +» | `uploaded_documents[]` مع `data_base64` | يوضع المستند في الكتاب كمقالة، 15 ميغابايت على الأكثر | ≤ 1.9.7 |
| 7.2 | مستند عبر عنوان | خطوة التنظيم، حقل العنوان: `https://upload.wikimedia.org/wikipedia/commons/1/16/La_Pel%C3%A9e_vue_du_Carbet.jpg` | `uploaded_documents[]` مع `"url": "https://upload.wikimedia.org/…"` | يُحفظ العنوان وحده؛ ويُنزّل الخادم الصورة عند كل توليد | 1.10.0 |
| 7.3 | مستند عبر صفحة ملف في ويكيميديا كومنز | `https://commons.wikimedia.org/wiki/File:La_Pelée_vue_du_Carbet.jpg` | `"url": "https://commons.wikimedia.org/wiki/File:La_Pel%C3%A9e_vue_du_Carbet.jpg"` | تُستخدم الصورة (معاينة بعرض 2 000 بكسل)؛ وللملف PDF يُستخدم الأصل | 1.10.0 (المتصفح)، 1.12.0 (واجهة البرمجة) |
| 7.4 | PDF عبر صفحة ملف | `https://commons.wikimedia.org/wiki/File:Interpersonal_communication_and_coordination_in_Wikipedia_Working_Paper_30_June_2020.pdf` | العنوان نفسه في `uploaded_documents[].url` | يُدرج ملف PDF الأصلي، وتُعدَّل صفحاته على قياس الكتاب | 1.10.0 (المتصفح)، 1.12.0 (واجهة البرمجة) |
| 7.5 | صورة خلفية الغلاف | خطوة التحرير، «صورة خلفية الغلاف»، ملف أو عنوان (7.2 أو 7.3) | `cover_image`: `{"title": "…", "url": "…"}` أو `data_base64` | خلفية الغلاف، دون تشويه | 1.9.6 |
| 7.6 | صورة الصفحة الأخيرة | خطوة التحرير، «صورة خلفية الصفحة الأخيرة» | `back_image` | صفحة مستقلة بعد الترخيص | 1.9.6 |
| 7.7 | عنوان يتعذر الوصول إليه | المستند `https://example.org/inexistant.png` | العنوان نفسه | يتوقف التوليد مع ذكر العنوان المعني؛ والرمز 502 عبر واجهة البرمجة | 1.10.0 |

## 8. التنظيم والتنسيق

| الرقم | الحالة | المتصفح | واجهة البرمجة (كتاب JSON إلى `POST /api/pdf`) | النتيجة المتوقعة | الإصدار |
|---|---|---|---|---|---|
| 8.1 | مقالات مرتبطة | زر «مقالات مرتبطة» في مقالة | `POST /api/explore` | تُقترح روابط المقالة بترتيب الصفحة | ≤ 1.9.7 |
| 8.2 | الفصول والترتيب | خطوة التنظيم، «إنشاء فصل»، السحب والإفلات | `chapters` و`article_order` و`unassigned_first` | يتبع ملف PDF الترتيب المعروض | ≤ 1.9.7 |
| 8.3 | الفهرس | خطوة التحرير: بلا، في البداية، في النهاية | `table_of_contents` و`toc_position` (`start` و`end` و`before:<مفتاح>`) | الفهرس في مكانه، وروابطه قابلة للنقر | 1.9.6 |
| 8.4 | القياس والاتجاه والهوامش | خطوة التحرير | `page_format` و`orientation` و`margin_*_mm` و`custom_width_mm` | كل الصفحات بالقياس المختار | ≤ 1.9.7 |
| 8.5 | أرقام الصفحات | «ترقيم الصفحات» | `page_numbers` | أرقام أسفل الصفحة، ما عدا الغلاف | ≤ 1.9.7 |
| 8.6 | لغة عناوين PDF | منتقي اللغة في الأعلى | المعامل `language` (12 لغة) | الغلاف والفهرس والترخيص باللغة المختارة | ≤ 1.9.7 |
| 8.7 | تقسيم يدوي إلى مجلدات | خطوة التنظيم، «مجلد جديد» | `volume_breaks`: `["before:<مفتاح>"]`، ثم `?volume=N` | ملف PDF لكل مجلد، ويبدأ الترقيم من 1 من جديد | 1.9.2 (المتصفح)، 1.12.0 (واجهة البرمجة) |
| 8.8 | أكثر من 300 مقالة | الكتاب 3.1 + صفحات أخرى حتى تجاوز 300 | `POST /api/books/volumes` للخطة، ثم `POST /api/pdf?volume=1` و`?volume=2`… | تقسيم تلقائي بين الفصول، «المجلد 1/2»…؛ ودون `volume` رفض 413 مع عدد المجلدات | 1.9.0 (المتصفح)، 1.12.0 (واجهة البرمجة) |

## 9. استدعاءات واجهة البرمجة دون PDF

| الرقم | الحالة | الاستدعاء | النتيجة المتوقعة |
|---|---|---|---|
| 9.1 | التعرف على مُدخل | `curl -X POST 'T/api/sources/resolve' -H 'Content-Type: application/json' --data '{"input":"volcan martinique","language":"fr"}'` | `kind`: `article` أو `book` أو `subpages` أو `search` |
| 9.2 | بنية صفحة كتاب | `curl -X POST 'T/api/books/structure' -H 'Content-Type: application/json' --data '{"url":"https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique"}'` | المقالات والعنوان الفرعي والفصول |
| 9.3 | PDF لكتاب موصوف بصيغة JSON | `curl -OJ -X POST 'T/api/pdf?language=fr' -H 'Content-Type: application/json' --data '{"name":"Test","main_articles":[{"title":"Cosmologie","language":"fr","site":"wikibooks","url":"https://fr.wikibooks.org/wiki/Cosmologie","selected":true}]}'` | ملف PDF لصفحة فهرس واحدة |
| 9.4 | متابعة التوليد | المحتوى نفسه إلى `POST /api/pdf/stream` | أسطر NDJSON `progress` و`wait`، ثم `done` وملف PDF |
| 9.5 | المقدمة والمؤلف المقترحان | `T/api/articles/intro?title=Montagne%20Pel%C3%A9e&language=fr` | الفقرة الأولى ومنشئ الصفحة |
| 9.6 | الإصدار المنشور | `T/api/version` | الإصدار، الإيداع، حد المقالات |

## 10. المدخلات المرفوضة

تأتي رسائل الخطأ من الخادم وتبقى بالفرنسية، أيًّا كانت لغة الواجهة.

| الرقم | المُدخل | النتيجة المتوقعة |
|---|---|---|
| 10.1 | `https://example.com/wiki/Chat` | «L'URL doit pointer vers une page HTTPS d'un projet Wikimédia…»؛ 422 |
| 10.2 | `https://fr.wikibooks.org/wiki/Wikilivres:Le_Bistro` | «Seules les pages de contenu de fr.wikibooks.org…»؛ 422 |
| 10.3 | `https://commons.wikimedia.org/wiki/File:La_Pelée_vue_du_Carbet.jpg` في حقل المصادر | يُرفض كمصدر (لا عنوان `<لغة>.<مشروع>.org` لكومنز)؛ ويُقبل كمستند أو صورة خلفية (7.3) |
| 10.4 | `https://fr.wikipedia.org/wiki/Page_qui_n_existe_pas` | «La page … est introuvable»؛ 404 |
| 10.5 | حقل فارغ | «Saisissez …»؛ 422 |
| 10.6 | كتاب بلا أي مقالة مختارة، ثم «إنشاء PDF» | رسالة «حدّد مقالة واحدة على الأقل قبل إنشاء ملف PDF.»؛ 400 |
