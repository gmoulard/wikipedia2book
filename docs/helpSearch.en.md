# Help for the "Build the book" field: everything Wikipedia2Book accepts

This page lists everything Wikipedia2Book accepts, with for each case an example to try **in the browser** and the same case **through the API**. It serves two purposes: showing what can be done, and running a manual check before going into production. It is a translation of the [French reference page](helpSearch.fr.md).

The reference behaviour is described in the [functional specification](FunctionalSpec.en.md) (section 3.1 for sources) and the [technical specification](TechnicalSpec.en.md) (section 13.3 for the API).

## How to use it

- **Browser**: open https://wikipedia2book.toolforge.org/, paste the example into the field of the "Build the book" step, then click "Add". An address starting with `https://wikipedia2book.toolforge.org/?` opens as it is.
- **API**: open the address in the browser (the PDF downloads) or pass it to `curl -OJ`. `POST` calls are given as `curl` commands.
- **Version**: version of the application from which the case works. Check the version in service with https://wikipedia2book.toolforge.org/api/version.
- The "Version" column applies to the browser. On the API side, `GET /api/pdf/from-source` (sections 1 to 4) and the page's `?source=` parameter exist since 1.12.0 (in production from the evening of 16 November 2026, before getting that number): with an older version, send the book as JSON to `POST /api/pdf` (9.3), after recognising each entry with `POST /api/sources/resolve` (9.1).
- The examples were checked on 17 November 2026 against the real wikis, by the source recognition code; a page renamed or deleted since may change the result.

Abbreviations: **T** = https://wikipedia2book.toolforge.org. In API addresses, `language` is the language of the titles generated in the PDF (cover, table of contents, license) and `wiki` the language of titles without a prefix.

## 1. A single page

| No. | Case | Browser: to enter | API | Expected result | Version |
|---|---|---|---|---|---|
| 1.1 | URL of a Wikipedia article | `https://fr.wikipedia.org/wiki/Épaves_de_la_rade_de_Saint-Pierre` | `T/api/pdf/from-source?source=https://fr.wikipedia.org/wiki/%C3%89paves_de_la_rade_de_Saint-Pierre` | The article is added; introduction and author suggested with the first article | ≤ 1.9.7 |
| 1.2 | Exact title | `Montagne Pelée` (language FR next to the field) | `T/api/pdf/from-source?source=Montagne%20Pel%C3%A9e&wiki=fr` | The article "Montagne Pelée" is added | ≤ 1.9.7 |
| 1.3 | Redirected title | `Napoléon Bonaparte` | `T/api/pdf/from-source?source=Napol%C3%A9on%20Bonaparte&wiki=fr` | The redirect is followed: "Napoléon Ier" is added | ≤ 1.9.7 |
| 1.4 | Title without an exact page | `volcan martinique` | `T/api/sources/resolve` as `POST` (see 9.1): `kind` = `search` | Search results appear below the field, to add with one click; the generation API answers 404 with the text concerned | ≤ 1.9.7 |
| 1.5 | Search as you type | Type `Saint-Pie` without confirming | `T/api/search?query=Saint-Pie&language=fr` | Suggestions below the field | ≤ 1.9.7 |
| 1.6 | Title in another language | `nl:Rotterdam` | `T/api/pdf/from-source?source=nl:Rotterdam` | The Dutch article is added, marked "NL" | 1.7.0 |
| 1.7 | All languages | `Paris`, with "All" chosen next to the field | `T/api/search?query=Paris&language=all&limit=3` | Results in every language of the list, each marked with its language; the chosen article keeps its own | 1.12.4 |

## 2. Other Wikimedia projects

| No. | Case | Browser: to enter | API | Expected result | Version |
|---|---|---|---|---|---|
| 2.1 | Wikivoyage page | `https://fr.wikivoyage.org/wiki/Lyon` | `T/api/pdf/from-source?source=https://fr.wikivoyage.org/wiki/Lyon` | Page added, card marked "Wikivoyage" | 1.8.0 |
| 2.2 | Project and language prefix | `[[voy:en:Lyon]]` | `T/api/pdf/from-source?source=voy:en:Lyon` | English Wikivoyage page added | 1.8.0 |
| 2.3 | Wikiversity | `https://fr.wikiversity.org/wiki/Python` | `T/api/pdf/from-source?source=v:Python&wiki=fr` | Page added, marked "Wikiversity" | 1.8.0 |
| 2.4 | Wikiquote | `https://fr.wikiquote.org/wiki/Victor_Hugo` | `T/api/pdf/from-source?source=q:Victor%20Hugo&wiki=fr` | Page added, marked "Wikiquote" | 1.8.0 |
| 2.5 | Wiktionary, prefixes in the other order | `fr:wikt:chat` | `T/api/pdf/from-source?source=fr:wikt:chat` | Page added, marked "Wiktionary" | 1.8.0 |
| 2.6 | Wikinews | `https://fr.wikinews.org/wiki/Accueil` | `T/api/pdf/from-source?source=https://fr.wikinews.org/wiki/Accueil` | Page added, marked "Wikinews" | 1.8.0 |
| 2.7 | Wikisource text (one page) | `https://zh.wikisource.org/wiki/論語/學而第一` | `T/api/pdf/from-source?source=https://zh.wikisource.org/wiki/%E8%AB%96%E8%AA%9E/%E5%AD%B8%E8%80%8C%E7%AC%AC%E4%B8%80` | Page added; Chinese titles readable in the PDF | 1.7.8 |
| 2.8 | Wikisource author page | `https://fr.wikisource.org/wiki/Auteur:François_Rabelais` | `T/api/pdf/from-source?source=https://fr.wikisource.org/wiki/Auteur:Fran%C3%A7ois_Rabelais` | Page added as it is (biography and list of works) | 1.8.1 |

## 3. Books

| No. | Case | Browser: to enter | API | Expected result | Version |
|---|---|---|---|---|---|
| 3.1 | Wikipedia book page by URL | `https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique` | `T/api/books/generate-from-wikipedia-book?url=https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique` | 113 articles in the order of the page, `;` chapters, `===` subtitle; title "Martinique" | 1.3.0 |
| 3.2 | Book page by its name | `Utilisateur:Alexbzh972/Livres/Martinique` | `T/api/pdf/from-source?source=Utilisateur:Alexbzh972/Livres/Martinique` | Same result as 3.1 | 1.3.0 |
| 3.3 | Table of contents of a Wikibooks book | `https://fr.wikibooks.org/wiki/Cosmologie` | `T/api/pdf/from-source?source=b:Cosmologie&wiki=fr` | Window "The whole book / The whole book and its table of contents / Only this page / Cancel"; "The whole book" gives 27 pages in chapters | 1.10.0 |
| 3.4 | Whole book and its table of contents | As 3.3, choose "The whole book and its table of contents" | `T/api/pdf/from-source?source=b:Cosmologie&wiki=fr&summary=1` | The table of contents first, before the first chapter | 1.10.0 |
| 3.5 | Only the table of contents page | As 3.3, choose "Only this page" | `POST /api/pdf` with only the table of contents page (see 9.3) | The table of contents page alone | 1.10.0 |
| 3.6 | Wikisource work | `s:Les Misérables` (language FR) | `T/api/pdf/from-source?source=s:Les%20Mis%C3%A9rables&wiki=fr` | Choice window; "The whole book" gives 365 chapters in 5 parts, without "Texte entier" | 1.11.0 |
| 3.7 | Hand-written printable version (address) | `https://fr.wikibooks.org/wiki/Hélices_de_navires_à_déplacement/Version_imprimable` | `T/api/pdf/from-source?source=https://fr.wikibooks.org/wiki/H%C3%A9lices_de_navires_%C3%A0_d%C3%A9placement/Version_imprimable` | 13 pages, one chapter per `= … =` heading, cover left out, title "Hélices de navires à déplacement" | 1.12.0 |
| 3.8 | Printable version through `{{imprimable}}` (address) | `https://fr.wikibooks.org/wiki/Programmation_C/Version_imprimable` | `T/api/pdf/from-source?source=https://fr.wikibooks.org/wiki/Programmation_C/Version_imprimable` | The choice window for the "Programmation C" table of contents (21 pages) | 1.12.0 |

## 4. Lists of pages (several lines)

Paste all the lines at once into the field (or separate them with Shift+Enter). On the API side, repeat `source=` (50 at most).

| No. | Case | Line to enter | Expected result | Version |
|---|---|---|---|---|
| 4.1 | Wiki link | `[[Brest]]` | "Brest" added | 1.7.0 |
| 4.2 | Wiki link with language | `[[nl:Amsterdam]]` | Dutch article added | 1.7.0 |
| 4.3 | Wiki link with label | `[[Frégate (bateau)\|Frégate]]` | "Frégate (bateau)" added | 1.7.0 |
| 4.4 | Markdown link, brackets in the URL | `[Suchet](https://fr.wikipedia.org/wiki/Suchet_(navire))` | "Suchet (navire)" added | 1.7.0 |
| 4.5 | Number at the start of the line | `1. Lorient` | "Lorient" added | 1.7.0 |
| 4.6 | Bullet at the start of the line | `* Concarneau` (also `-`, `•`, `#`) | "Concarneau" added | 1.7.0 |
| 4.7 | Line not found | `Xyzzy inexistant` | The line stays in the field, the final message counts it as "not found" | 1.7.0 |
| 4.8 | Table of contents in a list | `b:Programmation Python` | The choice window opens for this table of contents; its chapters are not kept | 1.10.0 |

Full list to paste in the browser:

```
[[Brest]]
[[nl:Amsterdam]]
[Suchet](https://fr.wikipedia.org/wiki/Suchet_(navire))
1. Lorient
* Concarneau
[[voy:en:Lyon]]
fr:wikt:chat
```

Expected result: "7 page(s) added, 0 already in the book, 0 not found."

API, same list: `T/api/pdf/from-source?source=[[Brest]]&source=[[nl:Amsterdam]]&source=1.%20Lorient&source=*%20Concarneau&source=[[voy:en:Lyon]]&source=fr:wikt:chat&wiki=fr`

## 5. Pasted book text

| No. | Case | Text to paste | API | Expected result | Version |
|---|---|---|---|---|---|
| 5.1 | Wikipedia "Book:" syntax | Block 5.1 below | `curl` 5.1 below | Title "Ports bretons", subtitle "Guide des ports", chapters "Finistère" and "Morbihan", "Brest" first without a chapter | 1.12.0 |
| 5.2 | Wikibooks printable version | Block 5.2 below | `curl` 5.2 below | 3 Wikibooks pages in 3 chapters, license left out | 1.12.0 |

Block 5.1:

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

Block 5.2:

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

To read only the structure, without a PDF: same body on `POST /api/books/from-wikitext`.

## 6. Opening a saved book (JSON)

| No. | Case | Browser | API | Expected result | Version |
|---|---|---|---|---|---|
| 6.1 | JSON book by address | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Wrecks-of-Saint-Pierre-harbor.json` | `T/api/pdf/from-json?url=https://gmoulard.github.io/wikipedia2book/static/Wrecks-of-Saint-Pierre-harbor.json&language=en` | The book opens ("Book imported.") with its background images and its document | 1.9.6 |
| 6.2 | Wikibooks book as JSON | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json` | `T/api/pdf/from-json?url=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json` | 27 pages in 8 chapters | 1.9.6 |
| 6.3 | Local JSON file | "Open" button, choose a file exported with "Save" | `curl -OJ -X POST 'T/api/pdf/from-json' -H 'Content-Type: application/json' --data @book.json` | The book opens / the PDF is produced | ≤ 1.9.7 (browser), 1.12.0 (API) |
| 6.4 | JSON then extra sources | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json&source=b:Programmation%20Python` | — | The JSON book opens, then the choice window for the added table of contents | 1.12.0 |
| 6.5 | Sources in the page address | `T/?source=https://fr.wikibooks.org/wiki/Cosmologie&source=Montagne%20Pel%C3%A9e&wiki=fr` | See 3.3 and 1.2 | Each source is added as if it had been typed, question included | 1.12.0 |
| 6.6 | Refused address | `T/?json=http://example.com/livre.json` | `T/api/pdf/from-json?url=http://example.com/livre.json` | Error message, nothing is imported; the API answers 422 "doit commencer par https://" | 1.9.6 |

## 7. Documents and background images

| No. | Case | Browser | API (field of the JSON book) | Expected result | Version |
|---|---|---|---|---|---|
| 7.1 | Image or PDF from the computer | Organization step, "Choose a file +" | `uploaded_documents[]` with `data_base64` | Document placed in the book like an article, 15 MB at most | ≤ 1.9.7 |
| 7.2 | Document by address | Organization step, address field: `https://upload.wikimedia.org/wikipedia/commons/1/16/La_Pel%C3%A9e_vue_du_Carbet.jpg` | `uploaded_documents[]` with `"url": "https://upload.wikimedia.org/…"` | Only the address is saved; the server downloads the image at each generation | 1.10.0 |
| 7.3 | Document by Commons file page | `https://commons.wikimedia.org/wiki/File:La_Pelée_vue_du_Carbet.jpg` | `"url": "https://commons.wikimedia.org/wiki/File:La_Pel%C3%A9e_vue_du_Carbet.jpg"` | The image (2,000 px thumbnail) is used; for a PDF, the original | 1.10.0 (browser), 1.12.0 (API) |
| 7.4 | PDF by file page | `https://commons.wikimedia.org/wiki/File:Interpersonal_communication_and_coordination_in_Wikipedia_Working_Paper_30_June_2020.pdf` | Same address in `uploaded_documents[].url` | The original PDF is included, pages refitted to the book format | 1.10.0 (browser), 1.12.0 (API) |
| 7.5 | Cover background image | Editing step, "Cover background image", file or address (7.2 or 7.3) | `cover_image`: `{"title": "…", "url": "…"}` or `data_base64` | Cover background, without distortion | 1.9.6 |
| 7.6 | Last page image | Editing step, "Last page background image" | `back_image` | Separate page after the license | 1.9.6 |
| 7.7 | Unreachable address | Document `https://example.org/inexistant.png` | Same address | Generation stopped, the address concerned is named; 502 through the API | 1.10.0 |

## 8. Organization and layout

| No. | Case | Browser | API (JSON book sent to `POST /api/pdf`) | Expected result | Version |
|---|---|---|---|---|---|
| 8.1 | Related articles | "Related articles" button of an article | `POST /api/explore` | Links of the article suggested, in the order of the page | ≤ 1.9.7 |
| 8.2 | Chapters and order | Organization step, "Create a chapter", drag and drop | `chapters`, `article_order`, `unassigned_first` | The PDF follows the displayed order | ≤ 1.9.7 |
| 8.3 | Table of contents | Editing step: none, start, end | `table_of_contents`, `toc_position` (`start`, `end`, `before:<key>`) | Table placed in the right place, clickable links | 1.9.6 |
| 8.4 | Format, orientation, margins | Editing step | `page_format`, `orientation`, `margin_*_mm`, `custom_width_mm` | Every page in the chosen format | ≤ 1.9.7 |
| 8.5 | Page numbers | "Number the pages" | `page_numbers` | Numbers at the bottom of the page, except the cover | ≤ 1.9.7 |
| 8.6 | Language of the PDF titles | Language selector at the top | `language` parameter (12 languages) | Cover, table, license in the chosen language | ≤ 1.9.7 |
| 8.7 | Manual volume break | Organization step, "New volume" | `volume_breaks`: `["before:<key>"]`, then `?volume=N` | One PDF per volume, numbering starting again at 1 | 1.9.2 (browser), 1.12.0 (API) |
| 8.8 | More than 300 articles | Book 3.1 + other pages up to more than 300 | `POST /api/books/volumes` for the plan, then `POST /api/pdf?volume=1`, `?volume=2`… | Automatic split between chapters, "Volume 1/2"…; without `volume`, refusal 413 with the number of volumes | 1.9.0 (browser), 1.12.0 (API) |

## 9. API calls without a PDF

| No. | Case | Call | Expected result |
|---|---|---|---|
| 9.1 | Recognise an entry | `curl -X POST 'T/api/sources/resolve' -H 'Content-Type: application/json' --data '{"input":"volcan martinique","language":"fr"}'` | `kind`: `article`, `book`, `subpages` or `search` |
| 9.2 | Structure of a book page | `curl -X POST 'T/api/books/structure' -H 'Content-Type: application/json' --data '{"url":"https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique"}'` | Articles, subtitle, chapters |
| 9.3 | PDF of a book described as JSON | `curl -OJ -X POST 'T/api/pdf?language=fr' -H 'Content-Type: application/json' --data '{"name":"Test","main_articles":[{"title":"Cosmologie","language":"fr","site":"wikibooks","url":"https://fr.wikibooks.org/wiki/Cosmologie","selected":true}]}'` | PDF of a single table of contents page |
| 9.4 | Follow the generation | Same body on `POST /api/pdf/stream` | NDJSON lines `progress`, `wait`, then `done` and the PDF |
| 9.5 | Suggested introduction and author | `T/api/articles/intro?title=Montagne%20Pel%C3%A9e&language=fr` | First paragraph and creator of the page |
| 9.6 | Version in service | `T/api/version` | Version, commit, article limit |

## 10. Refused entries

Error messages come from the server and stay in French, whatever the interface language.

| No. | Entry | Expected result |
|---|---|---|
| 10.1 | `https://example.com/wiki/Chat` | "L'URL doit pointer vers une page HTTPS d'un projet Wikimédia…"; 422 |
| 10.2 | `https://fr.wikibooks.org/wiki/Wikilivres:Le_Bistro` | "Seules les pages de contenu de fr.wikibooks.org…"; 422 |
| 10.3 | `https://commons.wikimedia.org/wiki/File:La_Pelée_vue_du_Carbet.jpg` in the Sources field | Refused as a source (Commons has no `<language>.<project>.org` address); accepted as a document or background image (7.3) |
| 10.4 | `https://fr.wikipedia.org/wiki/Page_qui_n_existe_pas` | "La page … est introuvable"; 404 |
| 10.5 | Empty field | "Saisissez …"; 422 |
| 10.6 | Book without any selected article, then "Generate PDF" | Message "Select at least one article before generating the PDF."; 400 |
