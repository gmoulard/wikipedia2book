# Wikipedia2Book — Functional specification

<!-- {% raw %} -->

<table border="0" ><tr><td>
<img src="https://gmoulard.github.io/wikipedia2book/static/Wikipedia2bookLogo.png" alt="Wikipedia2Book logo" width="100"  >
</td><td markdown="1">
This is the English translation of [FunctionalSpec.fr.md](https://gmoulard.github.io/wikipedia2book/FunctionalSpec.fr.html). The French document is the reference: if the two ever differ, the French version prevails. Interface labels are quoted as they appear in the English interface. The documentation has three parts: functional specification ([FunctionalSpec.en.md](https://gmoulard.github.io/wikipedia2book/FunctionalSpec.en.html)), technical specification ([TechnicalSpec.en.md](https://gmoulard.github.io/wikipedia2book/TechnicalSpec.en.html)) and version history, in French only ([CHANGELOG.fr.md](https://gmoulard.github.io/wikipedia2book/CHANGELOG.fr.html)); the technical specification is numbered from 1; a reference to another document names it ("section 1.3 of the technical specification", "section 3.1 of the functional specification").
</td></tr></table>

---

## Table of contents

- [1. Overview of Wikipedia2Book](#1-overview-of-wikipedia2book)
	- [1.1 Purpose](#11-purpose)
	- [1.2 Core principles](#12-core-principles)
- [2. The in-memory book and how it is saved](#2-the-in-memory-book-and-how-it-is-saved)
- [3. Adding articles](#3-adding-articles)
	- [3.1 Ways to add articles](#31-ways-to-add-articles)
	- [3.2 Information kept for each article](#32-information-kept-for-each-article)
	- [3.3 Automatically suggested introduction and author](#33-automatically-suggested-introduction-and-author)
- [4. Exploring related articles](#4-exploring-related-articles)
	- [4.1 Principle](#41-principle)
	- [4.2 Exploration depth](#42-exploration-depth)
	- [4.3 Exploration results](#43-exploration-results)
	- [4.4 Starting an exploration](#44-starting-an-exploration)
- [5. Selecting articles](#5-selecting-articles)
- [6. Organizing the book](#6-organizing-the-book)
	- [6.1 Imported documents (images and PDFs)](#61-imported-documents-images-and-pdfs)
- [7. Retrieving Wikipedia content](#7-retrieving-wikipedia-content)
- [8. References, images and licenses](#8-references-images-and-licenses)
- [9. Book format settings](#9-book-format-settings)
	- [9.1 Standard formats](#91-standard-formats)
	- [9.2 Custom format](#92-custom-format)
	- [9.3 Orientation](#93-orientation)
	- [9.4 Margins](#94-margins)
- [10. Book layout](#10-book-layout)
	- [10.1 Format and orientation, applied to every page](#101-format-and-orientation-applied-to-every-page)
	- [10.2 Page numbering](#102-page-numbering)
- [11. PDF generation](#11-pdf-generation)
	- [11.1 Process](#111-process)
	- [11.2 Result](#112-result)
	- [11.3 Error handling](#113-error-handling)
- [12. User interface](#12-user-interface)
	- [12.1 Interface languages](#121-interface-languages)
	- [12.2 Administration page](#122-administration-page)
- [15. Compliance with Wikipedia licenses](#15-compliance-with-wikipedia-licenses)
- [16. Acceptance criteria](#16-acceptance-criteria)
- [18. Status and future developments](#18-status-and-future-developments)

## 1\. Overview of Wikipedia2Book

### 1.1 Purpose

Wikipedia2Book is software for creating a printable PDF book directly from Wikipedia articles. The user starts building the book right away.

As soon as the application opens, an empty book is ready to use. The user adds one or more main articles, explores the articles linked from them, chooses exactly which content to include, organizes the articles into chapters and generates a structured PDF document.

The software runs on every platform thanks to a Python architecture containerized with Docker.

### 1.2 Core principles

* The software is not limited to one topic or category of articles.

* Several main articles can be added to the same book.

* Exploration of Wikipedia links starts from an article chosen by the user (depth and maximum number of articles can be set through the API).

* No discovered article is ever added to the book automatically.

* The user keeps full control over which articles are selected.

* The book format is configurable (dimensions, orientation, margins).

* The resulting PDF is suitable for printing.

## 2\. The in-memory book and how it is saved

The software handles a single book at a time, built entirely in the browser's memory.

* When the application opens, an empty book is created automatically; the user can give it a name and a description.

* All changes (articles, selection, organization, layout) are kept in the browser's memory during the session, and sent to the API only for the operations that need it (search, exploration, PDF generation).

* The user can explicitly download the state of the book as a JSON file, named after the book title (or, when no title is set, after the title of the book's first article).

* The user can import a previously downloaded JSON file to resume a book; the import replaces the current book.

* A book can also be opened from the address of a JSON file published online, by passing it in the page address: `https://wikipedia2book.toolforge.org/?json=<file-url>` (example: [https://wikipedia2book.toolforge.org/?json=https://gmoulard.github.io/wikipedia2book/static/Wrecks-of-Saint-Pierre-harbor.json](https://wikipedia2book.toolforge.org/?json=https://gmoulard.github.io/wikipedia2book/static/Wrecks-of-Saint-Pierre-harbor.json), which opens the sample book *Wrecks of Saint-Pierre harbor*). The browser reads the file (`fetchWorkspaceText` in `app.js`), like an import: the site hosting it must allow it (CORS), as GitHub Pages and raw.githubusercontent.com do; otherwise, or if the file is not a valid book, an "Import JSON impossible: …" message is shown and the page stays on an empty book. The server never sees this address.

* A book can also be built from the page address, with one or more `source=` parameters (in order, each read as a line of the field: URL, title, `b:Title`, `fr:Title`, book page), and `wiki=<language>` for the language of titles without a prefix (by default the one chosen next to the field): for example `https://wikipedia2book.toolforge.org/?source=https://fr.wikibooks.org/wiki/Cosmologie`. Each source is added as if it had been typed in "Build the book" (`addSourcesFromAddress` in `app.js`), including the question for a Wikibooks or Wikisource contents page and the search when no exact page matches; with `json=` as well, the JSON book is opened first, then the sources are added to it.

* The server never persists any book or file on its disk: persistence is entirely up to the user, by downloading and later manually importing the JSON file. Only temporary files exist for the duration of a PDF generation (section 11.1), deleted as soon as it ends, fails or is abandoned.

The book contains in particular:

* The main articles.

* The discovered articles.

* The selection of articles.

* The structure of the book (order, chapters, presence and position of the table of contents).

* The layout settings.

* The cover information (title, subtitle, author, introduction, conclusion).

The full data model and the format of the JSON file are described in section 1.9 of the technical specification.

## 3\. Adding articles

### 3.1 Ways to add articles

A single input field, in the Sources step, is used for every way of adding content: the user does not say what kind of thing they are typing, the software recognizes it by querying Wikipedia (`POST /api/sources/resolve`, which receives `input`, `language` and `site`):

* a `https://<language>.wikipedia.org/wiki/…` URL is read with the language of the URL; so is a URL of another Wikimedia project of the form `https://<language>.<project>.org/wiki/…`, on that project (see below); otherwise, the text is taken as a page title, in the Wikipedia language chosen next to the field. This selector offers FR, EN, DE, ES, IT, PT and NL; when the application opens, it is set to the browser language (main part of the code, for example `pt` for `pt-BR`, `no` for `nb`), added to the list if missing (for example JA). If the browser language is missing or not a valid code, EN is selected. This choice is saved neither in the book nor in the browser;

* the page is looked up on Wikipedia, following redirects: a page in the main namespace (an article) is added as an article; a page in another namespace (`User:…/Books/…`, `Book:…`, etc.) is imported as a book page;

* if no page has exactly that title, the Wikipedia search results are offered below the field, to be added with one click; a URL pointing to a page that does not exist is reported as not found.

* **All languages**: the "All" choice, at the end of the language selector, searches a title in every language of the selector (FR, EN, DE, ES, IT, PT, NL and the browser language when it is added) at the same time; results are offered below the field, grouped by language (at most three per language while typing, five on adding), each with its language, and the article added with one click keeps its own. With "All", a title is never added directly: one must pick among the results; a URL or a language prefix (`nl:Title`) still take precedence, and pasted book page content is read in the interface language if it is in the selector, otherwise in English. A language that does not answer does not stop the others.

* **Help**: below the field, the "See the help: everything you can enter, with examples" link opens, in a new tab, the help page of the documentation site in the interface language ([French](helpSearch.fr.md), [English](helpSearch.en.md) and the ten other languages), which gives an example of every possible entry; server error messages are quoted there in French.

* **Other Wikimedia projects**: a page in the main namespace, or in a project-specific namespace, of Wikisource (`wikisource`), Wikibooks (`wikibooks`), Wikivoyage (`wikivoyage`), Wikiversity (`wikiversity`), Wikiquote (`wikiquote`), Wiktionary (`wiktionary`) or Wikinews (`wikinews`) is added as an article, with the official PDF of the project (same service as Wikipedia, section 1.2 of the technical specification), for example `https://zh.wikisource.org/wiki/論語/學而第一`, `https://fr.wikibooks.org/wiki/Programmation_Python` or `https://fr.wikivoyage.org/wiki/Lyon`. It is given by its URL or by a title preceded by a project interwiki prefix (see the list below): the page is then looked up on that project and, if there is no exact page, that project's search results are offered. Book pages (`Book:`) remain specific to Wikipedia; on Wikibooks, a book is recognized by its contents page: a main namespace page that contains at least 2 links to its own subpages (`Book/Chapter`, red links excluded) is offered as a book (`kind` = `subpages`, `MediaWikiClient.get_subpage_book`, which reads the HTML rendered by `action=parse` to keep the order of the contents page, 500 subpages at most). A window then asks "“Programmation Python” is the table of contents of a Wikibooks book (56 pages). What do you want to add?": "The whole book" (the subpages in the order of the contents page, the book title taken from it), "The whole book and its table of contents" (the contents page first, before the first chapter), "Only this page" (as before) or "Cancel" (nothing is added, as with Escape). The sections of the contents page become book chapters at the first heading level that gives at least two of them containing subpages (for example the `h3` "Intro", "Basics"… under a single `h2` "Contents" in *Python Programming*); subpages placed before the first section stay without chapter, and a contents page with a single section gives a book without chapters. "Print version" subpages (Version imprimable, Print version, Druckversion, Versione stampabile, Versión para imprimir, Versão para impressão, Afdrukbare versie…, `FULL_TEXT_PAGES`), which contain the whole book, are ignored; the other side pages (guest book…) are removed with "×". The same goes on Wikisource for a work split into subpages (`Work/Chapter`, for example 史記: 130 scrolls in 5 chapters 本紀, 表, 書, 世家, 列傳; Les Misérables: 365 chapters in 5 parts): pages containing the whole work ("Texte entier", "全覽", "全文"…, same `FULL_TEXT_PAGES` list) are ignored, and a page whose subpages are already in the book is only an intermediate contents page (for example "Les Misérables/Tome 1/Livre 1"): it is left out on Wikisource, kept on Wikibooks, where a chapter often has its own text besides its subpages. In a list of several pages, the same question is asked for each contents page, and chapters are not kept, as for a Wikipedia book page. Project-specific namespaces are those MediaWiki numbers from 100 upwards, excluding talk pages (odd numbers): for example the author page `https://fr.wikisource.org/wiki/Auteur:François_Rabelais` (namespace 102 in French, 106 in Spanish), `Page:…` and `Index:…` on Wikisource, or `Appendix:…` on Wiktionary; it is added as it is, with its official PDF (for an author page: biography and list of works, without the works themselves). A page in a standard namespace (`Wikibooks:…`, `Help:…`, `Category:…`, etc.) or a talk page is rejected, unless it is a book listing: a Wikibooks compilation (`https://fr.wikibooks.org/wiki/Wikilivres:Compilations/Programmation_C`) or any page made of `: [[…]]` lines with no other text (at least 2, and 80% of the lines that contain a link, `wikipedia_api.is_book_listing`) is read like a Wikipedia book page: pages in order, `;` chapters, book title taken from the page name ("Programmation C"), pages taken from the same project and language. A discussion that mentions pages is still rejected, with the message "Seules les pages de contenu de fr.wikibooks.org (textes, pages d'auteur…) et les compilations ou pages de livre sont acceptées." Each page is added as is: for a work or a book split into subpages (Wikisource, Wikibooks), the main page often contains only the table of contents, and each subpage must be added (the list of their URLs can be pasted, one per line). The article card shows the name of the project, in the interface language (for example "Wikibooks"), next to the language. Projects without a `<language>.<project>.org` address (Commons, Meta-Wiki, MediaWiki.org, Wikispecies, Wikidata) are not accepted as articles; a Commons file given by its address becomes an imported document (section 6.1).

The field also accepts a **list of pages, one per line** (pasted, or typed with Shift+Enter; Enter alone starts the addition). Each line is recognized and then looked up on Wikipedia one after the other, with a message "Adding the list: n / total — title":

* bullets and numbers at the start of a line (`1.`, `2)`, `#`, `*`, `-`, `•`) are ignored, as are empty lines;
* wiki link `[[Title]]`, `[[:fr:Title]]` or `[[nl:Title|text]]`: the title, in the language given by the prefix if any;
* Markdown link `[text](https://…)`: the URL, parentheses included (`…/Suchet%20(navire)`);
* language prefix `nl:Title` (2 or 3 lowercase letters, optionally followed by a variant, for example `zh-yue`): the page with that title on that Wikipedia, which allows multilingual lists;
* project interwiki prefix, alone or combined with a language prefix in any order: `w:` Wikipedia, `s:` Wikisource, `b:` Wikibooks, `voy:` Wikivoyage, `v:` Wikiversity, `q:` Wikiquote, `wikt:` Wiktionary, `n:` Wikinews (for example `b:Programmation Python`, `[[voy:en:Lyon]]`, `fr:wikt:chat`): the page with that title on that project, in the language of the prefix or, failing that, the one chosen next to the field;
* URL of Wikipedia or of another accepted project: read with its language; plain title: on Wikipedia, in the language chosen next to the field.

Each page found is added as an article (or, for a book page, all its articles); a page already in the book is skipped. Lines without an exact page, or in error, stay in the field to be corrected and are listed below it. A final message gives the number of pages added, already present and not found. Search-as-you-type is turned off as soon as the field contains several lines.

Below the field, a short permanent label recalls the essentials ("Enter a title, the address of a Wikimedia page, or several pages, one per line.") and points, through a bold link, to the help page that details everything the field accepts, with examples. Status messages (article added, pages imported, no exact page) are shown on a separate line underneath, without replacing that label. While typing text that is not a URL, search results are suggested as you type, on the project and in the language of the prefixes if any (`b:fr:Program…` searches the French Wikibooks). The previous endpoints (`POST /api/articles`, `POST /api/books/structure`, `GET /api/search`) remain available. The content of a "Book:" page can also be pasted there (see below); the help page gives an example.

The user can therefore add articles to the book in any of the following ways:

* URL of a Wikipedia article.

* Article title typed directly.

* Search in Wikipedia: results are suggested as you type, to be added with one click.

* URL of a Wikipedia "book" page listing articles: every article it references is imported and pre-selected, **in the order in which they appear on the book page** (not in alphabetical order — the MediaWiki API sorts links, so the software reads the page's wikitext to recover the real order). Only their title and URL are loaded at this stage; their full PDF is downloaded only at generation time. The structure of the book page is also kept: the first line of the form `=== … ===` becomes the book subtitle (only if the "Subtitle" field of the Editing step is empty), and each line starting with `;` opens a chapter that receives the articles listed below it, up to the next chapter (Organization step, section 6). The book keeps the exact order of the page: the articles placed before the first `;` stay without a chapter but **at the start of the book**, before the first chapter and without a chapter page or a "No chapter" heading (book setting `unassigned_first`, saved in the JSON file); this applies only if the book had no chapter yet before the import, otherwise those articles join the other articles without a chapter, at the end. Links and `''`/`'''` formatting in those lines are reduced to their text; a chapter without articles is ignored, and `== … ==` lines (title recorded by the book creator) are not used. The confirmation message links to the Wikipedia help page about books (`https://fr.wikipedia.org/wiki/Aide:Livres`).
  Syntax of a book page, as described in the Wikipedia help ([Aide:Livres/Aide avancée](https://fr.wikipedia.org/wiki/Aide:Livres/Aide_avanc%C3%A9e)), and how the software handles it (`wikipedia_api.get_book`):
  * Title — `== Title ==`: ignored; the book title is entered in the Editing step.
  * Subtitle — `=== Subtitle ===`: the first line of this form becomes the book subtitle (see above).
  * Chapter — `;Chapter name`: opens a chapter.
  * Article — `:[[Article]]`: the article is added to the current chapter. In practice, every `[[…]]` link on a line that is neither a heading nor a chapter is taken, even without a leading `:`; an anchor (`#section`) is removed; links whose title contains `:` (other namespaces, interlanguage links, files) and duplicates are ignored; at most 200 articles are read.
  * Renamed article — `:[[Frégate (bateau)|Frégate]]`: the target article (`Frégate (bateau)`) is added; the label after `|` is ignored, and the book shows the article title.
  * Specific revision — `:[{{fullurl:Article name|oldid=revision number}} Article title]`: not supported. It is not a `[[…]]` link, so the article is not imported; an article's PDF is always that of its current revision.

* Content of a book page pasted as is into the field, over several lines: as soon as a line starts with `;` or `:[[`, or is a `== … ==` or `=== … ===` heading, the whole text is sent in one block to `POST /api/books/from-wikitext` (`{"wikitext": "…", "language": "fr"}`, 200,000 characters at most) instead of being read line by line. It is read by the same function as the wikitext of a book page (`wikipedia_api.parse_book_wikitext`, same rules, 200 articles at most): order, `;` chapters, `===` subtitle, and the title as well: the first `== … ==` line becomes the book title (`book_wikitext_title`). The articles are taken from Wikipedia, in the language chosen next to the field, without checking that they exist (as for a book page, a missing article only fails at generation). A text without any `[[…]]` link to an article is refused (HTTP 422). This makes it possible to put together a book in the "Book:" format without saving it on Wikipedia.

* `https://` address of an image, a PDF or a web page from another site, or of a Wikimedia Commons file: added as an imported document (section 6.1), marked "Internet URL" under its name in the "Your articles" list.

* Hand-written Wikibooks printable version (syntax described by [Wikilivres/Créer la version imprimable d'un livre](https://fr.wikibooks.org/wiki/Wikilivres/Cr%C3%A9er_la_version_imprimable_d%27un_livre)), pasted as is or given by its address: as soon as the text contains a `{{:Page}}` transclusion, it is read as a printable version (`wikipedia_api.parse_printable_wikitext`, same endpoint `POST /api/books/from-wikitext`, 500 pages at most). Each `{{:Book/Chapter}}` transclusion becomes a **Wikibooks** page, in the language chosen next to the field, in the order of the text; each level-1 heading `= … =` opens a chapter (tags such as `<center>` and formatting removed); the other templates (`{{Notice de version imprimable}}`, `{{Nouvelle page imprimée}}`, `{{#ifeq:…}}`…), duplicates, transclusions from another namespace and the cover and licence pages (`…/Couverture`, `Licence de documentation libre GNU`…, `PRINTABLE_SKIPPED_PAGES`), which the application produces itself, are ignored; the `titre=` (or `title=`) parameter of the first template that has one (`{{Couverture de version imprimable|titre=…}}`, `{{Page de titre|titre=…}}`) becomes the book title (`printable_wikitext_title`). The address of a Wikibooks "…/Version imprimable" page (names in `FULL_TEXT_PAGES`) is no longer added as a single page: the server reads its wikitext (`MediaWikiClient.get_wikitext`); if it contains transclusions, the book is taken from it in the same way (title from `titre=`, otherwise from the table of contents); otherwise (printable version made by the `{{imprimable}}` module, which reads the table of contents), the parent table of contents is offered, with the "The whole book" / "The whole book and its table of contents" / "Only this page" window described above.

Example of an article URL:

`https://fr.wikipedia.org/wiki/Épaves_de_la_rade_de_Saint-Pierre`

### 3.2 Information kept for each article

For each article, the software keeps:

* The title.

* The Wikipedia URL.

* The language.

* The summary, when it comes from a search (articles added by URL, by title or imported from a book page have no pre-filled summary).

* The Wikipedia page identifier, when known (search results).

The user can delete a main article without affecting the others.

### 3.3 Automatically suggested introduction and author

When the very first main article of the book is added (including the first article of an imported book page, section 3.1), the software automatically suggests, in the Editing step (section 12):

* The introduction of the book, from that article's introductory summary on Wikipedia.

* The author of the book, from the username (or the IP address, for an anonymous contribution) that created the page on Wikipedia.

This suggestion never replaces a field already filled in by the user, and remains fully editable. It is triggered only once, for the first article only — adding more articles afterwards does not trigger it again.

## 4\. Exploring related articles

### 4.1 Principle

The software explores the internal links of the main articles in order to suggest complementary articles, relying on the official MediaWiki API (`action=parse&prop=text`): links are read from the rendered HTML of the article, hence **in their order of appearance in the page** (banners, infobox and captions included), and not in alphabetical order as `prop=links` would return them. Ignored: links to pages that do not exist (red links), links outside the main namespace (`File:`, `Category:`, `Help:`, etc.), internal anchors, the page's link to itself and duplicates.

### 4.2 Exploration depth

The depth can be set between 0 and 3 on the API side (`/api/explore`); the interface always uses depth 1 (section 4.4):

| Depth | Behavior                                          |
| ----- | ------------------------------------------------- |
| 0     | No complementary article                          |
| 1     | Articles directly linked from the main articles   |
| 2     | Articles linked from depth-1 articles             |
| 3     | Articles linked from depth-2 articles             |

The maximum depth is capped at 3 levels to avoid excessive exploration.

### 4.3 Exploration results

For each discovered article, the software shows:

* Its title.

* Its URL.

* An "Add to book" button and a "×" button to dismiss it (section 5).

Above the list, a line recalls which article the suggestions come from ("Links from "…", in page order."). Duplicates are removed automatically (case-insensitive comparison of language and title), and articles already in "Your articles" are not suggested again.

### 4.4 Starting an exploration

* By default, the "Suggestions" section is empty and contains no button: a message invites the user to click "Related articles" on one of their articles.

* The "Related articles" button, present on every card in "Your articles", fills the list with the articles cited by that article, in page order (depth 1, up to 200 links). The button of the article whose links are shown is highlighted.

* Clicking "Related articles" on another article **clears the list** and fills it with the links of that new article: the list always shows the links of a single article at a time.

* No setting is required. The API, for its part, still accepts a depth from 0 to 3 and a maximum from 1 to 200.

* At the end, a message gives the number of suggestions found, then the page scrolls to the list; if the article cites no new article, a message says so.

## 5\. Selecting articles

This feature is essential.

No discovered article may be added to the book automatically.

The software presents the list of discovered articles ("Suggestions") and lets the user choose exactly which ones to keep.

Available features:

* "Add to book" on a suggestion: it leaves the suggestion list and joins "Your articles", checked, with a mention of the article it came from; a message confirms the addition. It then becomes a main article like any other: it can be unchecked, removed, or used as the starting point of a new exploration.

* "×" on a suggestion: it is removed from the list.

* "Add all": adds every visible suggestion (respecting the title filter). This button, the filter and the sort choice only appear when the list contains suggestions.

* Search by title among the suggestions.

* Sorting the suggestions, on the same line as the filter (which shrinks to make room for them, including on smartphones), with two buttons: "Page order" (order of appearance of the links in the article, the initial choice each time the application opens) or "A → Z" (alphabetical order according to the interface language, ignoring case and accents: "Éruption" is filed under E). Sorting combines with the filter; the sentence naming the source article states which order is shown. This choice is not saved in the book's JSON file.

* In "Your articles", a checkbox for each article indicates whether it is included in the book.

The selection is kept with the rest of the book, in memory and in the JSON export. Suggestions, however, are not saved in the JSON export (`discovered_articles` is always empty there since 1.9.6): they come back by running "Related articles" again. When an older JSON file is opened, the discovered articles that were checked in it are moved to "Your articles", the others stay in the suggestions.

## 6\. Organizing the book

The user organizes the selected articles before generating the PDF.

Features:

* Reorder articles by drag and drop.

* Create chapters and give them a title. The first chapter created goes after the articles already there, which stay at the top of the book without a heading (`unassigned_first`), without "No chapter" appearing; articles are then dragged into it.

* Move an article from one chapter to another, or out of any chapter, by drag and drop: membership of a chapter comes from the article's place under the chapter row (there is no chapter selection menu). An article dropped on a chapter row goes to the top of that chapter; dropped on "No chapter", it leaves every chapter; dropped on another article, it takes its place (`applyOrgSequence` in `app.js`, which updates `chapters`, `article_order` and `unassigned_first`).

* Move a chapter by drag and drop, by grabbing any part of its row outside its title (the title field is no wider than the title, since Chrome does not start a drag from an input field). The list reads as a sequence: only the chapter row moves, and each article belongs to the chapter placed above it; the articles placed before the first chapter are at the top of the book, without a heading (`unassigned_first`). When the book has a "No chapter" group at the end of the list, a chapter cannot go below that row.

* Each article or imported document row fits on one line (title, then origin in smaller type) and has a "×" button that removes it from the book (a removed article also disappears from "Your articles", an imported document is deleted) and a "↗" button that opens the article on Wikipedia or the imported document in a new tab. Chapters, the table of contents and volume breaks have the same "×".

* The table of contents is not in the Organization list: it is chosen in the Editing step, next to "Number the pages", among three choices — "None" (`table_of_contents` false), "At the start", right after the cover (`toc_position` `start`), or "At the end", after the last article, before the license and the conclusion (`toc_position` `end`). The server still accepts `before:<key>` (article/document key, `chapter:<id>`, or `chapter:` for the "No chapter" group) for a direct API call; a JSON file that places the table of contents in the middle of the book puts it back at the start when opened.


* A book of a single article or document has no table of contents, whatever the choice in the Editing step: the PDF has none (`book_builder.toc_slot_index`). It comes back as soon as the book has two elements; a volume of a single article has none either.

* When the book has chapters, the articles that belong to no chapter are shown at the end of the list, under the "No chapter" heading, as in the PDF. Exception: when the first chapter was created after them, when they were dragged before the first chapter, or for a book imported from a Wikipedia book page in which articles precede the first chapter (section 3.1), those articles are shown and placed in the PDF at the start, before the first chapter, without a heading or chapter page.

* Split the book into several volumes at will, even under the server limit: the "New volume +" button in the toolbar adds a break in the middle of the last volume; the "Start of a volume" line is moved by drag and drop like the table of contents, and removed with its "×" (the volume then joins the previous one). Each break is stored relative to the element that follows it (`volume_breaks`, a list of `before:<key>`, same keys as `toc_position`, kept in the JSON export and ignored by the server); a break whose element disappears, that would target the first element of the book or a chapter without articles is ignored. Each volume is generated as a separate PDF (section 11.1).

* Add a general introduction and a conclusion.

* Choose in the Editing step a background image for the cover and another one for the last page, each imported from a file or from its address (section 11.1).

* Turn page numbering on or off (on by default).

An article can be moved freely within the structure of the book.

### 6.1 Imported documents (images and PDFs)

From the Sources step, the user can also import their own files (image or PDF) by clicking "Add" with nothing typed in the field (the file picker opens, several files at once; there is no longer a "Choose a file +" button in the Organization step), or give them by their address, typed in that same field (section 3.1), to include them in the book as if they were articles. Each document appears in the "Your articles" list of the Sources step, with "Internet URL" (address), "Imported PDF document" or "Imported image" (file) under its name, and "×" to remove it:

* Accepted formats: images (`image/*`) and PDF (`application/pdf`); 15 MB maximum per file imported from the computer, 100 MB for a file given by its address (`WIKIPEDIA2BOOK_DOCUMENT_MB`, section 1.4 of the technical specification).

* By address: an `https://` address typed in the Sources field, alone or in a list, that is not a page of a `<language>.<project>.org` project (another site, another wiki such as Miraheze, a Wikimedia Commons file, `upload.wikimedia.org`), or that is a file page of a Wikimedia project (namespace 6, for example `Fichier:…` on fr.wikipedia.org), becomes an imported document (`sourceDocument` in `app.js`), without going through `/api/sources/resolve`. It also appears in the "Your articles" list of the Sources step, marked "Internet URL" under its name, with "×" to remove it; an address already there is not added twice ("This article is already in the book."). A Wikimedia file page goes through the `imageinfo` API, as for background images (section 11.1): a PDF gives the address of the original file, an image its 2,000 px thumbnail; for any other address, the document is a PDF if the address ends with `.pdf`, otherwise an image, which the browser tries to display before accepting it ("Document not reachable at this address (…)." on failure). Only the address is kept in the book and in the JSON export (`url`, without `data_base64`): the server downloads the document at each generation, during the "Preparing the imported document" step, with the same checks as background images (PNG, JPEG, GIF, WebP or PDF according to the `Content-Type` header, which also decides whether it is a PDF), and the generation stops with the address at fault if it is unreachable. "↗" then opens the address itself.

* An imported document appears in the list of items to organize just like an article: it can be reordered and moved into a chapter by drag and drop, counts in a volume, is removed with "×" and opened with "↗" (through a `blob:` address, since Chrome refuses to open a `data:` address in a new tab), and its starting page appears in the table of contents if page numbering is on.

* An imported image is included as a full page, centered and scaled to the book format; an imported PDF is included as is, page by page.

* The document is removed from the book with its "×" button, independently of the other documents and articles; there is no separate list of imported documents nor any box to exclude them without deleting them. A document deselected in a JSON file older than 1.9.6 comes back into the book when the file is opened.

* **Document title**: each imported document has, in the list of the Organization step, a title field ("Document title in the book", 300 characters at most, an empty title is not saved). This title replaces the file name everywhere in the PDF: table of contents, bookmarks, license page. When a file is imported, the suggested title is the file name without its extension ("IMG_1234" for "IMG_1234.jpg").

* **Web page**: the `https://` address of any web page is also accepted: an address that ends neither in `.pdf` (or `.pdf/`) nor in an image extension and that the browser cannot display as an image becomes a `kind` = `html` document (label "Web page converted to PDF"), given by its address only. A page of a Wikimedia project that is neither a content page of a `<language>.<project>.org` project nor a file (for example a Meta-Wiki page or a Commons category) does not become a document: it is sent to `/api/sources/resolve`, which refuses it; the server also refuses to download a Wikimedia web page. At each generation, the server downloads the page (15 MB at most, `WIKIPEDIA2BOOK_HTML_PAGE_MB`, `text/html` or `application/xhtml+xml` type, same checks as the other addresses: HTTPS, public addresses, redirections checked again). The type guessed by the browser from the address is not trusted: if the site actually sends a PDF or a PNG, JPEG, GIF or WebP image (`Content-Type` header of the response, 100 MB at most, like the other documents given by their address), the file is kept as it is as an imported document, without conversion. For a real page, the server removes scripts, frames, forms, objects, videos and `on…` attributes (`app/html_document.py`), downloads its style sheets itself (10 at most, `@import` and `url(…)` removed) and its images (40 at most, PNG, JPEG, GIF, WebP or SVG, 5 MB each and 20 MB in all for all resources), with the same checks, and embeds them as `data:`; a refused or unreachable resource is simply left out. The page is then rendered to PDF by WeasyPrint in the book format (15 mm margins), still limited to `data:` addresses, in a worker process, then refitted like the other documents. If this rendering fails (for example with the style sheets of a GitHub repository page, issue #4), the page is rendered a second time without any style (style sheets, `<style>` tags and `style` attributes removed): the text and images remain. An unreachable page or one that is neither HTML, nor a PDF, nor an image stops the generation with a message giving the address; so does a page that cannot be rendered even without style, with its title, its address, the error type and the advice to save it as PDF from the browser and then add it with "Add", the Sources field empty. Likewise, an imported document that the server cannot include (damaged PDF…) stops the generation with its title ("Le document « … » n’a pas pu être intégré au livre (…)"), and an unexpected server error is shown as "PDF generation failed: erreur inattendue du serveur (error type)." instead of repeating "PDF generation failed" twice.

* The file content is kept base64-encoded in the book state and in the JSON export, so that the PDF can be regenerated or the book resumed without importing the file again.

## 7\. Retrieving Wikipedia content

Adding and exploring do not download the full content of pages. When the PDF is generated, each selected article is retrieved through the official Wikimedia PDF endpoint (`/api/rest_v1/page/pdf/{title}/{format}`), equivalent to Wikipedia's "Download as PDF" feature. Wikipedia only lays out its PDFs in three formats (`a4`, `letter`, `legal`, always portrait): the software requests `letter` for a Letter book, `legal` for a Legal book, and `a4` for every other format (A0 to A6, custom). For Letter and Legal, the article pages are therefore laid out by Wikipedia directly in the right format, with no white margins caused by a change of proportions.

The content of each article (text, structure, images, references) is never rebuilt: it is exactly that of the official Wikipedia PDF. Only its physical layout changes: each page is recomposed (scaled and centered, without distortion) onto the format and orientation chosen for the book — see section 10.1.

## 8\. References, images and licenses

The software does not rebuild article content: each selected article is included as the official PDF generated by Wikipedia. As a result:

* References and citations stay exactly those of the Wikipedia PDF, with their original formatting.

* Images and their captions are those embedded by Wikipedia in its PDF export, with their original layout.

* Credits and licenses for texts and images are those printed by Wikipedia in its own PDF; the software does not extract them or rewrite them separately.

* When Wikimedia temporarily refuses a request because it receives too many (HTTP 429) or is overloaded (HTTP 503), the software waits and retries, up to 4 times: the delay given by Wikimedia (`Retry-After` header, capped at 20 s), or otherwise 2, 4, 8 then 16 s. The wait is shared by all the ongoing downloads of the same book (they resume together instead of each hitting Wikimedia again) and does not block the server, which keeps answering other requests. During PDF generation, each new pause is shown in the status window, under the current step's label, as a countdown ("Wikipedia is limiting requests right now: retrying in 5 s…") that disappears when the pause ends; the step and the progress bar do not move. This applies to every request to Wikipedia (PDF and MediaWiki API).
* An article whose page has been renamed (the title in the book has become a redirect) is generated with the page Wikipedia redirects to, without error.
* If the page of a selected article does not exist or no longer exists on Wikipedia (the PDF service answers HTTP 404, for example for a deleted page), the article is removed from the book, which is generated without it (not in the table of contents, the bookmarks or the license page); the browser announces it at the end, without blocking anything, with the message "PDF ready, without {count} page(s) that no longer exist on Wikipedia: {titles}." (key `export.readyWithoutMissing`, shown for 15 s). If no page of the book exists, generation fails ("Aucune page du livre n’existe sur Wikipédia : le PDF ne peut pas être généré.").
* If Wikipedia cannot produce a PDF for a selected article for another reason (service unavailable, invalid response, or still refused after these 4 retries, with the message "Wikipédia limite le nombre de requêtes en ce moment…"), the generation of the whole book fails and an explicit error message is shown; no partial book is produced.

* The only exception to the integrity of the official PDF: when page numbering is on (section 10), a page number is overlaid at the bottom of every page, including article pages — without touching the content, credits or license notices printed by Wikipedia.

## 9\. Book format settings

The document format is fully configurable.

### 9.1 Standard formats

Available formats:

| Format | Dimensions    |
| ------ | ------------- |
| A0     | 841 × 1189 mm |
| A1     | 594 × 841 mm  |
| A2     | 420 × 594 mm  |
| A3     | 297 × 420 mm  |
| A4     | 210 × 297 mm  |
| A5     | 148 × 210 mm  |
| A6     | 105 × 148 mm  |
| Letter | 216 × 279 mm  |
| Legal  | 216 × 356 mm  |

A4 is offered by default, without being imposed.

### 9.2 Custom format

The user can enter:

* The width in millimeters.

* The height in millimeters.

### 9.3 Orientation

Two orientations are available:

* Portrait.

* Landscape.

### 9.4 Margins

The user first chooses a predefined set of margins:

| Preset       | Top | Bottom | Inside | Outside | Binding |
| ------------ | --- | ------ | ------ | ------- | ------- |
| Standard     | 18  | 18     | 18     | 16      | 0       |
| Narrow       | 10  | 10     | 12     | 10      | 0       |
| Wide         | 25  | 25     | 25     | 22      | 0       |
| For binding  | 18  | 18     | 20     | 16      | 10      |

Values in millimeters; "Standard" matches the default values. Choosing "Custom", or expanding "Fine-tune margins (mm)", gives access to each margin individually. The preset shown is derived from the book's values: as soon as a margin no longer matches any preset, "Custom" is shown. Presets are not saved as such in the book or in the JSON export, only the five values are.

The margins that can be set individually are:

* The top margin.

* The bottom margin.

* The inside margin.

* The outside margin.

* The binding margin, added to the inside margin.

## 10\. Book layout

The PDF is structured like a real book.

Items generated by the application:

* Cover (book title, subtitle, author, note; the edition date is at the end of the book, under the logo).

* Introduction, if one was entered.

* Table of contents, grouped by chapter: under an underlined heading, each chapter is a bold line (title on the left, page number aligned on the right), followed by the indented list of its articles and documents, with their page numbers aligned in the same column. Each line, page number included, is a clickable internal link to the first page of the chapter or article.

* Chapter title pages, for each chapter containing articles.

The table of contents may be absent if the user removed it (section 6).

* Conclusion, if one was entered.

* License page (section 15), always present, after the conclusion (or after the last article, and after the table of contents if it is at the end of the book), ending with the Wikipedia2Book logo, the edition date and links.

* Last page background image, alone on a page, if one was chosen.

The content of articles and imported documents is not laid out by the application: these are the pages of their original PDF (official Wikipedia PDF, or imported document). Their physical format, however, is always harmonized with the rest of the book — see section 10.1.

The cover and the table of contents are two separate sections in the final PDF: the position chosen for the table of contents in the Editing step (section 6) is the one actually used at generation — the cover always stays the first page, and the table of contents is inserted exactly where chosen: right after the cover, before a chapter (before its title page), before an article, or after the last article (before the license and the conclusion).

Navigation in the final PDF relies on bookmarks (cover, table of contents, one entry per chapter and per article, license, conclusion) and on the links of the table of contents. These links are produced as follows: WeasyPrint generates each line as a link to a placeholder address (`https://wikipedia2book.invalid/toc/<key>`, an article or document key, or `chapter:<n>`); after assembly, these links are read back (`pdf_generator.internal_links`), removed, then replaced by internal links to the item's actual page in the book (`BookAssembly.link_toc`), even when page numbering is turned off.

### 10.1 Format and orientation, applied to every page

Every page of the final PDF follows the format and orientation chosen for the book (section 9), without exception:

* The pages generated by the application (cover, introduction, table of contents, chapter pages, license, conclusion) are produced natively in that format.

* Each article page (official Wikipedia PDF) and each page of an imported document is recomposed onto a page of that same format: its content is scaled and centered, keeping its original proportions (no distortion). If the proportions of the source page differ from those of the book, white margins appear on the sides or at the top/bottom rather than distorting the content. A page that already has the book format to within 1 point (0.35 mm), without rotation, is not recomposed: its size is only set exactly to the book format, without rewriting its content. This is the case for Wikipedia PDFs in A4, Letter and Legal books, which are requested directly in that format (section 7): their assembly is then about seven times faster.

* The content itself (text, images, references) is never modified or rebuilt — only its scale and position on the page change.

### 10.2 Page numbering

The "Number the pages" option (section 6) is on by default and can be turned off.

When it is on:

* Every page of the book shows a number at the bottom, continuously — including article pages and imported documents, except the cover and the background last page (image, color or logo).

* The table of contents shows, for each chapter and each article, the number of the page where it starts.

* To compute these numbers before assembling the book, the software generates the cover (which does not depend on the numbers and is used as is in the book, without being generated a second time) and a first version of the table of contents unless it is placed at the end, in order to measure their page count (the numbers of the items placed after the table of contents take it into account); it then regenerates the table of contents with the correct numbers. In rare cases (very dense book), adding the numbers to the table of contents may shift this pagination slightly by one page.

No preview feature is currently offered.

## 11\. PDF generation

### 11.1 Process

The "Generate PDF" button is always visible and active, whichever tab is shown; if no article or document is selected, a message says so when the button is clicked, rather than disabling the button.

Once the PDF is started, the software:

* Checks that at least one article or document is selected; otherwise, generation is refused.

* Downloads the official PDF of each selected article; decodes each selected imported document (section 6.1), converting an image into a PDF page if needed.

* If page numbering is on, computes in advance the starting page of each chapter and each article (section 10.2).

* Generates the cover (with the introduction, if any) and the table of contents (with page numbers if enabled) as two separate sections; the cover receives the root bookmark carrying the book title.

* Inserts the table of contents at the chosen position (section 6), or omits it if it was removed.

* For each chapter (or for all the articles if there is no chapter): generates a chapter title page with its own bookmark, then adds the official PDF of each article of the chapter, with one bookmark per article.

* Recomposes each added page (cover, table of contents, chapters, articles, imported documents) onto the format and orientation chosen for the book (section 10.1), before assembling it into the final document. Each article's or document's PDF is recomposed in the background as soon as it is downloaded or prepared, while the next one downloads, so that its pages are usually ready by the time of assembly.

* Adds a license page with a "License" bookmark (section 15), after the conclusion, or after the last chapter/article and the table of contents placed at the end of the book when there is no conclusion.

* Ends the license page, right after its text, with the Wikipedia2Book logo (`app/static/Wikipedia2bookLogoPrint.png`, embedded in the PDF, at most 100 mm wide, itself clickable to https://wikipedia2book.toolforge.org/), the edition date ("Edition of DD/MM/YYYY", no longer on the cover) and two clickable links, https://wikipedia2book.toolforge.org/ and https://github.com/gmoulard/wikipedia2book; a book in volumes has them at the end of each volume.

* **Background images** (Editing step, fields "Cover background image" and "Last page background image"): each image is imported from a file (PNG, JPEG, GIF, WebP or SVG, 15 MB at most) or from its address; the address of a Wikimedia file page (`https://commons.wikimedia.org/wiki/File:…`, or a file page on a `<language>.<project>.org` project) goes through that wiki's `imageinfo` API, called by the browser (`origin=*`) to get a 2,000 px wide thumbnail on `upload.wikimedia.org`; `utm_*` tracking parameters removed; any other address must start with `https://` (otherwise "The address must start with https://.") and is only accepted if the browser manages to display the image, without needing a CORS permission (otherwise a message suggests downloading the image and importing the file). An image imported from a file is kept in the book in base64; an image given by its address only keeps the address, in the book as in the JSON export, and the server downloads it at each generation (progress step `fetch_image`, "Downloading the image “…”", before the articles): `main.fetch_remote_file`, then `json_source.download`, with the checks of `GET /api/pdf/from-json` (HTTPS, public addresses only, checked again at each redirect, 3 at most, 30 s at most) and 15 MB at most, PNG, JPEG, GIF, WebP or SVG type according to the `Content-Type` header. The downloaded image is only kept in memory during the generation; if it is unreachable or of another type, the generation stops with a message giving the address (`error` event, HTTP 502 on `/api/pdf`). `BookImage` model (`cover_image`, `back_image`): `title`, then either `url`, or `mime_type` and `data_base64` (base64 checked by the server), never both. The preview is shown from the address or the content, with a "Remove" button. Each image fills its whole page, margins included, without distortion: anything beyond the page width or height is cropped from the center (`background-size: cover`; `background-attachment: fixed`, without which WeasyPrint sizes the background to the area inside the margins). Under each field, when the image is not suitable, the interface shows the recommended size in pixels, computed at 300 dpi from the book format and orientation (2,480 × 3,508 px for A4 portrait, `recommendedBackgroundSize` in `app.js`) and updated when they change, with the warning that explains it: image too small (under 150 dpi once the page is filled: "Image too small (… px): it will look blurry in print.") or whose orientation differs from the page ("The image does not have the page's orientation: a large part will be cropped."); nothing is shown for a suitable image, without an image, or for an SVG image. Before rendering, the server brings each background image larger than the page down to the page size at 300 dpi, cropped from the center as when displayed (`book_builder.fit_background`, Pillow, in the assembly process, journal stage `fit_backgrounds`): JPEG at quality 90, or PNG if the image has transparency; an image already small enough, an SVG or unreadable image is kept as is. A 5,616 × 3,744 px photo (5.2 MB) thus becomes a 2,480 × 3,508 px JPEG (1.6 MB) in A4: on Toolforge, the cover rendering by WeasyPrint goes from 2.0 s to 0.7 s; the peak memory of the assembly from 328 to 283 MB (the shrinking decodes the whole image but only resizes the visible part, `resize(box=…)`); the PDF gains almost nothing, since WeasyPrint already recompressed the photo. The cover image lies under the title, subtitle, author and cover note, whose color depends on the image (`book_builder.cover_text_style`, Pillow): the server measures the luminance of the part of the image visible behind the text (area inside the margins, top 65% of the usable height); black text if 95% of that area is light enough for a 4.5:1 contrast, white if 95% is dark enough, otherwise (high-contrast image, SVG or unreadable image) black text, with no band (the semi-transparent white band was removed at the user's request; the chosen text color applies as it is). The introduction pages have no image. With a last page image, one more page is added after the license, without margins or text, entirely covered by the image (`book_builder.build_back_cover_html`, journal stage `render_back_cover`); the logo, date and links stay on the license. Each volume of a book in volumes repeats both images. Tests: `tests/test_backgrounds.py`.

* **Colors and Wikipedia logo** (Editing step, under each of the two background images: "Background color" box with a color picker, "Wikipedia logo" box): `cover_color` and `back_color` (`#rrggbb`, `null` without a color, any other value refused by the server; `null` by default for both, box unchecked in the interface: the cover is white, like Wikipedia pages; the default blue `#273c75` of 1.13.1 was removed at the user's request), `cover_logo` and `back_logo` (booleans; logo on the cover by default, box checked, at the user's request; no logo on the last page by default). The color fills the whole page, under the background image if there is one (`background-color` of `@page`). Cover text (Editing step, under the cover background image: "Text color" box with a picker, "Font" list): `cover_text_color` (`#rrggbb`, `null` by default for the automatic color described below, box unchecked) colors the title, subtitle, author and cover note; `cover_font` (`serif` by default, `sans-serif` or `monospace`, any other value refused) picks the title font, DejaVu Serif, DejaVu Sans or DejaVu Sans Mono (`book_builder.COVER_FONTS`, fonts already installed by the `Dockerfile` and the `Aptfile`); the introduction and the other generated pages keep DejaVu Serif. Cover layout, after Wikipedia headings: text `#202122`; 28 pt title in normal weight, underlined by a solid 0.75 pt grey rule (`#a2a9b1`); subtitle and author in 11 pt bold DejaVu Sans, without a rule; cover note in 11 pt DejaVu Sans; the title and its rule across the full width of the text area. Without a chosen text color, on a cover without an image, the text turns white when the color is dark (relative luminance under 0.5, `book_builder.color_text_style`), otherwise it stays black; with an image, the image decides, as before. The Wikipedia logo (`app/static/WikipediaLogo.png`, a 480 px copy of the [Wikipedia-logo-v2.svg](https://commons.wikimedia.org/wiki/File:Wikipedia-logo-v2.svg) file from Wikimedia Commons, CC BY-SA 3.0, version 1 by Nohat from a concept by Paullusmagnus; trademark of the Wikimedia Foundation, recalled under the fields) goes at the bottom right of the cover (25 mm wide, inside the margins) and of the last page (25 mm wide and 15 mm from the edge at most, less on a small page). The logo printed after the license is `Wikipedia2bookLogoPrintTransparent.png`, a transparent-background version of `Wikipedia2bookLogoPrint.png` (kept as it is). A color or the logo on the last page is enough to create the end page after the license, even without an image (`book_builder.has_back_cover`); this last page, like the cover, has no page number (`BookAssembly.stamp_page_numbers(skip_last=True)`). Tests: `tests/test_backgrounds.py` (`ColorAndLogoTest`), `tests/test_pdf_stream.py`.

* Adds a conclusion page with a bookmark, if a conclusion was entered — after the table of contents, even when it is placed at the end of the book, and before the license.

* If page numbering is on, overlays a page number at the bottom of every page of the assembled document (except the cover and the background last page).

* Merges everything into a single PDF file and makes it available for download, named after the book title.

* **Assembly on temporary disk**: each recomposed PDF (article, imported document, generated page) is written to a temporary folder of its own for the generation, instead of staying in memory. The book is assembled by PyMuPDF (MuPDF library) in two steps: merging the files in batches of 20, each batch added to the merged file as an incremental update and then released from memory, deleting the part files right away, then reopening that file to add bookmarks, table of contents links and page numbers, and writing the final PDF, also in this folder, then sent to the user in chunks (`/api/pdf/stream` as well as `/api/pdf`, which announces its size). The folder is deleted as soon as sending ends, the generation fails or the user abandons it. Each download keeps its slot until its PDF is recomposed and written: at most 2 or 4 raw PDFs (section 1.2 of the technical specification) are in memory at the same time, even on a server with limited CPU. Server memory therefore hardly grows with the size of the book any more: on a test book of 100 articles and 197 MB, the peak goes from 1,100 MB to 158 MB, from 2,130 MB to 200 MB for 200 articles and 393 MB, and to 262 MB for 300 articles and 590 MB (local measurements, section 1.12 of the technical specification). Streams are copied as they are, without decompression or recompression: the final PDF has the same size as before.

* **Numbering without rewriting the pages**: each page number is added in two small streams placed around the page's existing content, which is neither read again nor rewritten (MuPDF's built-in Helvetica font). The former overlay of a page of numbers rewrote the content of every page without compressing it: a 100-article book weighed 173 MB instead of 96 (local measurement, 16/11/2026).

* **Limit of 300 articles per book, on every host**: beyond that, generation is refused at once (HTTP 413, `detail` = `{"code": "too_many_articles", "count", "limit", "message"}`), on `/api/pdf`, `/api/pdf/stream` and the direct generation endpoints. It is a deliberate limit, to spare the Wikimedia PDF service (each book downloads all its articles from it) and the container memory, which the limit test almost fills around 600 articles (section 1.12 of the technical specification). The value (300 on Toolforge in 1.8.7 and 1.8.8, 2,000 in 1.8.9 and 1.9.0, 300 everywhere since 1.9.1) stays below the measured memory limit of Toolforge, between 800 and 1,000 articles. The interface offers no choice: beyond the limit, it splits the book into volumes by itself (see below); the alert window with the translated message ("This book has {count} articles, but generation is limited to {limit} articles per book…") only remains for a volume the server would still refuse. Two environment variables, set in the `Dockerfile` (`ENV`) or passed to the container (`docker run -e`), configure a deployment: `WIKIPEDIA2BOOK_ARTICLE_LIMIT` (maximum number of articles per book, `0` = no limit; `300` in the `Dockerfile`, and 300 as well when it is not set, on Toolforge as elsewhere) and `WIKIPEDIA2BOOK_DOWNLOADS` (simultaneous downloads per book: 1 to 2 outside Toolforge, Wikimedia robot policy, 1 to 4 on Toolforge; `2` in the `Dockerfile`). An invalid value prevents the server from starting, with an explicit message (`main.deployment_settings`). The article limit is set from the container memory: about 250 MB for the server and the assembly process, plus 2 to 2.5 MB per article at the peak, with a wide margin for several users (README, "Deploying your own container"; measurements in section 1.12 of the technical specification).

* **Memory checked before each stage** (`app/resource_gate.py`, `MEMORY_GATE` in `main.py`): before downloading an article, a document or a background image, before refitting an article and before assembling the book, the generation estimates the memory the stage needs from the size of the files: download 10 MB per file (its size is not known yet, so the reserve depends on the number of files downloaded at the same time), refitting 5 MB + 25 times the size of the received PDF, assembly 100 MB + 2.5 times the size of the refitted articles + 35 times that of the background images (factors measured on 2026-11-17, section 1.12 of the technical specification). The stage only starts if the memory used by the container (cgroup), plus the reserves of the running stages, plus its estimate, stays under a share of the container limit: `WIKIPEDIA2BOOK_MEMORY_RATIO`, 0.95 by default (`0` = no check; any value outside 0 to 1 prevents startup). Otherwise it waits, with no time limit, for its turn in order of arrival (a big stage is not overtaken by small ones), and the progress window shows "Server busy: your book resumes as soon as there is enough memory (waiting: 14 s)…" (stream event `{"type": "busy", "seconds"}`, sent again every 10 s, key `progress.busy`). A stage always starts when no other has a reserve, so that a book larger than the margin is still made, alone; with no known memory limit (local machine), nothing waits. Closing the window abandons the wait. Each wait of at least one second is recorded in the generation journal (`memory_wait` stage), and `/api/health/details` gives the state of the check (`memory_gate`).

* **Disk space checked before each download and before the assembly**: same mechanism (`DISK_GATE`), on the disk of the temporary folder (`shutil.disk_usage`): an article or document download only starts if the used space of the disk, plus the running reserves, plus 30 MB (size of the refitted file, unknown before the download, `DOWNLOAD_DISK_BYTES`) stays under `WIKIPEDIA2BOOK_DISK_RATIO` of its size, 0.95 by default (`0` = no check). The reserve lasts until the refitted file is written, which then counts in the used space; the wait shows the same "Server busy" and is recorded in the journal (`memory_wait`, `reason` = `disk`). On Toolforge, this disk is shared with other tools (146 GB, about 49 GB used on 2026-11-17); disk space has never run short yet. Before the assembly, the same check reserves 50 MB + 2 times the size of the refitted articles (`assembly_disk_reserve`: the merged file is written while the parts still exist, then the final book next to the merged file), kept until the end of the assembly (`reason` = `assembly_disk` in the journal).

* **Server memory given back and contained** (since the simultaneous generation tests of section 1.12 of the technical specification): (1) glibc limits its memory arenas (`MALLOC_ARENA_MAX=2` in the `Dockerfile` and the `Procfile`) and gives freed memory back to the system after each article and at the end of each generation (`resource_gate.release_memory`, `malloc_trim`); (2) each generation is admitted at the entry, before loading anything, against a separate budget of `WIKIPEDIA2BOOK_GENERATIONS_RATIO` of the container limit (0.5 by default): it reserves 25 MB + 3 times the size of the base64 data of the received book (imported documents, background images) + 15 MB per background image given by its address (`generation_reserve`), kept until it ends; the following ones wait at the very start, with the same "Server busy" (`reason` = `generation` in the journal); this budget is separate from the stage check, which it would otherwise block forever; (3) background images, downloaded or imported, are written to the generation's temporary folder and removed from the book passed to the assembly, which reads them back (`background_files`); (4) refitting each article or document happens in a worker process (`isolation.run_in_worker`, 2 processes, a new one for each task, which gives all its memory back when it ends), no longer in the server process; a stopped worker process (out of memory) stops the generation with an explicit message. Downloads stay in the server process, where the Wikimedia policy limit of 2 simultaneous downloads is shared by all books.
* **Volumes**: the breaks placed in the Organization step (section 6) delimit the volumes first; the automatic split below then applies to each volume still above the limit. With breaks and no excess, "Generate PDF" likewise generates one volume per request and announces "This book is generated in {count} volumes, downloaded one after the other."; the hint under the counter only appears if the automatic split adds volumes. `/api/version` also returns `article_limit` (the server limit, `null` without a limit), read when the page loads. When the book has more Wikimedia articles than this limit (imported documents do not count), the Organization step announces it under the counter ("Above {limit} articles, the book will be generated in {count} volumes, each with its own page numbering."), and "Generate PDF" generates the volumes one after the other, each through a separate `/api/pdf/stream` request, without asking anything. The split follows the order of the Organization step and cuts between two chapters; a chapter is cut only if it exceeds the limit on its own, and its title is then repeated at the start of the next volume. Each volume is a complete book: cover titled "{title} — Volume {n}/{total}", table of contents, chapter pages, page numbering starting again at 1, licence page; the introduction is only in the first volume, the conclusion only in the last. The files are named `<book-name>-1.pdf`, `<book-name>-2.pdf`, etc.; the browser may ask for permission to download several files. The progress card shows "Volume {n} of {total}" above the current step, and the retry after a crash resumes the current volume, not the whole book. If the limit could not be read (`/api/version` unreachable), the server's first `too_many_articles` refusal provides the limit and generation restarts in volumes. The API does not change: it still generates one book per request, and a caller that wants volumes sends one `Project` per volume.

* **Assembly in a separate process**: once all the articles are downloaded and recomposed, the rest of the generation (WeasyPrint renders of the cover, table of contents, chapter pages, license and conclusion, then merging, bookmarks, links, numbering and writing the final PDF) runs in a separate process, started for this generation (`app/isolation.py`, `forkserver` method: the modules are loaded once and for all in the process that starts the others). This process sends progress to the server through a pipe, writes the final PDF to the temporary folder, then exits: the assembly memory, several hundred MB for a large book (section 1.12 of the technical specification), is given back to the system at the end of each generation instead of staying with the server. If it runs out of memory and is stopped, the generation fails with an explicit message ("L'assemblage du livre s'est arrêté (code …), probablement faute de mémoire : essayez avec moins d'articles.", server messages are in French); the server itself is stopped only if the platform stops the whole container. If the user abandons the generation, the process is stopped at once. Each assembly stage is recorded, with memory, in the generation journal (section 1.3 of the technical specification).

* **Lighter generated pages**: the table of contents of a large book is rendered in blocks of 100 entries (`book_builder.GENERATED_BLOCK_ENTRIES`), each in a separate WeasyPrint render, so that render memory does not grow with the book; each block starts on a new page, and the heading appears only in the first. The table of contents no longer uses a flexible box (the page number is floated), and all generated pages set the DejaVu Serif and DejaVu Sans fonts. The license page no longer contains the list of articles: it fits on one page whatever the size of the book.

Throughout generation, a status window shows the current step as "Step n / total", with its label (in the interface language) and a progress bar. The steps are, in order: downloading each article (one step per article, with its title; up to 4 articles are downloaded from Wikipedia at the same time on Toolforge, 2 on the other hosts (section 1.2 of the technical specification), and each step is shown when its download starts — the order of the articles in the book does not depend on it; if a download fails, the others are abandoned and the error of the first failing article, in book order, is shown) or preparing each imported document, computing page numbers (if numbering is on), composing the cover and the table of contents, assembling the pages in the book format, numbering the pages (if enabled), finalizing the file, then the browser downloading the PDF ("Downloading the PDF: 45%", key `progress.download`, last step, counted in the total by the server but shown by the browser as the bytes arrive). The total is known from the start. Each message is sent when its step begins: article recomposition runs in a separate thread (`asyncio.to_thread`) and assembly in a separate process, which leaves the server free to send progress and to answer other users during a generation. The window closes at the end, on success as well as on failure.

On the server side, this progress is sent by the `POST /api/pdf/stream` endpoint, which returns an NDJSON stream (one JSON line per event): `{"type": "progress", "step", "total", "code", "title"?}` for each step, `{"type": "wait", "seconds"}` at the start of each pause imposed by Wikimedia (section 8; duration rounded up to the second, not counted as a step), `{"type": "missing", "title", "url"}` for an article whose page does not exist or no longer exists (section 8, removed from the book, not counted as a step), then `{"type": "done", "size"}` immediately followed by the `size` bytes of the PDF, in binary and without encoding (sent in 256 KB chunks), or `{"type": "error", "detail"}` if generation fails along the way. The browser reads the JSON lines up to the `done` message, then gathers the PDF bytes; if it receives fewer than `size`, it shows "the connection to the server was interrupted before the end". **Retry after a crash**: when generation is cut off by a server crash — connection lost or stream interrupted before the end, server unreachable, or a 502, 503 or 504 response from the proxy during a restart ("no healthy upstream" on Toolforge) —, the browser waits until the server answers `GET /health` again (checked every 3 s, for at most 2 min), then starts the generation again from the beginning, with a message in the status window ("The server was interrupted: attempt 1, generation starts again from scratch…"). It does so twice automatically; after that, it asks the user before each new attempt, and stops on the error if they decline. An error returned by the server itself (`error` event: article not found, Wikipedia refusal, invalid request…) is never retried: it is shown at once. An empty selection is refused before the stream starts (HTTP error 400). The `POST /api/pdf` endpoint, which returns the PDF file directly without progress, remains available for direct use of the API.

Two high-level generation endpoints also return a PDF file directly: `POST /api/books/generate` receives an explicit list of article references (title or URL), the metadata and the main layout settings; `POST /api/books/generate-from-wikipedia-book` receives the URL of a Wikipedia book page and an optional book title. In the latter case, every article listed by Wikipedia is included in its order of appearance and selected for generation, together with the chapters (`;` lines) and, unless `book_subtitle` is provided, the subtitle (`=== … ===` line) of the book page, as with the import in the interface (section 3.1). `POST /api/books/structure` returns this reading without generating a PDF (`articles`, `subtitle`, `chapters` in the book's chapter format, `unassigned_first` true when articles precede the first chapter); `POST /api/books/import` returns only the list of articles. Without `book_title`, the book title (cover, bookmark, PDF file name) is the last part of the book page name: `Utilisateur:X/Livres/Les épaves` gives "Les épaves", `Livre:Animaux` gives "Animaux". The `book_conclusion` parameter (GET and POST) sets the text of the conclusion page; it is empty by default (no conclusion page), as in the web interface. These endpoints keep no book on the server side.

### 11.2 Result

The resulting PDF is:

* Printable and structured with navigation bookmarks.

* Consistent, on every page, with the format and orientation chosen for the book.

* Faithful to the content of the official Wikipedia PDF for articles, and of each imported document.

* Compatible with common PDF readers.

### 11.3 Error handling

On failure, the software shows an explicit message. Possible errors are:

* No article selected before export.

* Invalid URL, article title or language code.

* Book page or article not found on Wikipedia.

* Wikipedia API unreachable, or official PDF unavailable/invalid for an article: the whole generation fails, without producing a partial book.

* Unexpected failure while assembling the PDF.

## 12\. User interface

**Home page and FAQ.** The service address (`/`, for example https://wikipedia2book.toolforge.org/) opens a clean home page (`app/static/home.html`): the logo, a tagline ("Turn Wikipedia pages into a print-ready PDF book."), a drawing of the three steps — 1 "Add your sources" (six small cards labelled "Wikipedia", "Book", "Page", "Images", "PDF" and "Web" going into a machine), 2 "Organize the book" (cards moved up and down), 3 "Generate the PDF" (a document and a few settings) —, a large "Create your first PDF for free" button that opens the application, a "See an example book" link that opens in a new tab the PDF of the example book *Wrecks of Saint-Pierre harbor*, already generated every day on the documentation site (https://gmoulard.github.io/wikipedia2book/static/Wrecks-of-Saint-Pierre-harbor.pdf, section 1.6 of the technical specification) and a "Questions? Read the FAQ" link. Its top bar shows the logo and the "FAQ" and "Open the app" links. The FAQ (`/faq`, `app/static/faq.html`, same bar) answers, with questions that unfold on click: how much does it cost (nothing: no account and no ads, free software hosted by Wikimedia Cloud), can I keep my PDF, is my data stored, how do I continue my book later (JSON export and import), is there a size limit (300 articles, volumes beyond that, 15 MB per imported image or PDF), under which license is my book, can I print, share or sell the book, which sources can I use, what if the generation fails (with the "Report a problem on GitHub" link to the bug report form); it ends with the same "Create your first PDF for free" button. Both pages are translated into the 12 interface languages (`home.*` and `faq.*` keys of `i18n.js`), without a language selector: they use the language chosen in the application or, failing that, the browser's (section 12.1). They follow the light/dark theme, switch to right to left in Arabic and Persian, and the three steps stack up on a small screen.

**Installable application (PWA).** The site can be installed on a phone as an application named "Wikipedia2Book", with the logo as its icon (manifest `app/static/manifest.webmanifest`, service worker `/sw.js`). The installed application is only a link to the production site: it opens on the home page (`/`), full screen, and keeps nothing offline. On a phone or tablet (touch screen), the home page shows below the FAQ link a small "Wikipedia2Book on mobile" link: it is always shown; when the browser allows direct installation (Chrome, Edge, Samsung Internet on Android), it opens its install window, otherwise it shows the steps to follow: on iPhone and iPad, "On iPhone or iPad: tap “Share”, then “Add to Home Screen”.", elsewhere "On Android: open the browser menu ⋮, then “Install app” or “Add to Home screen”.". It appears neither on a computer nor in the already installed application.

The application itself is at `/app`; the logo of its top bar leads back to the home page. Links published before version 1.15.0 to `/` with a `json=`, `source=` or `wiki=` parameter (section 2) are redirected to `/app` with the same parameters (HTTP 307) and therefore still open the book; `/` without these parameters shows the home page.

The application is a single page, organized in three steps reachable through tabs. The step tabs are shown directly below the top bar: the book title and the cover note are not shown above the steps, they are entered only in the Editing step (part A, "Book identity").

**Default title:** if the book title field is left empty, the title used (cover, root bookmark, name of the PDF and JSON files) is that of the book's first Wikipedia article, in the order defined in the Organization step (failing a Wikipedia article, the first imported document). This default title is shown greyed out in the empty field, so that the user knows what will be printed; it is computed at generation time and is not saved in the book. A title imported from a Wikipedia book page (section 3.1) or entered by the user always takes precedence.

* 01 — Sources: adding the main articles (shown under the "Your articles" heading) and exploring links (discovered articles, shown under the "Suggestions" heading).

* 02 — Organization: reordering articles, imported documents, chapters and volumes.

* 03 — Editing, in four blocks: A "Book identity" (cover image and colors, text color and font, Wikipedia logo, title, subtitle, author, cover note), B "Content" (introduction, page numbering, table of contents: none, at the start, at the end, conclusion), C "Last page" (image, color or logo of the end page) and D "Print format" (paper size, orientation, margin preset and fine margin settings). The blocks go two per row (A and B, then C and D), one per row on a small screen.

At the bottom of the Sources and Organization steps, a "Next step: …" button opens the next step and scrolls back to the top of the page.

The logo in the top bar grows to 5 cm square when the mouse hovers over it, then returns to its size.

The footer shows the logo, the API connection status, a link to the project's Git repository (https://github.com/gmoulard/wikipedia2book, opened in a new tab), then the version number, the commit, the date and the author of the deployment.

A top bar lets the user, at any time, open a saved book ("Open" button, JSON import), save the book on their computer ("Save" button, JSON export) and start PDF generation. It also shows whether the current book has been saved. On smartphones, the "Open" and "Save" buttons show only their icon and the application name is hidden, so that the bar fits the width of the screen.

The interface can be used on desktop, tablet and smartphone, and follows the system's light/dark theme.

Its look follows Wikimedia's Codex design system (colors, buttons, tabs, fields, 2 px corners, sans-serif system fonts and serif headings as on Wikipedia), to fit into the Wikimedia environment. No font or resource is loaded from a third-party service (no Google Fonts).

### 12.1 Interface languages

The interface (labels, buttons, messages) is available in French, English, Spanish, Portuguese, Italian, German, Dutch, Turkish, Chinese, Japanese, Arabic and Persian, through a selector in the top bar. Arabic and Persian are displayed right to left: the whole page then switches to `rtl` writing direction (`dir` attribute of the document), and goes back to `ltr` for the other languages. The chosen language is remembered in the browser (it is not saved in the book or in the JSON export) and detected automatically on the first visit from the browser language, falling back to English when it is not one of the 12 languages.

This interface language is independent of the language of the Wikipedia articles (section 3), which remains a separate per-article setting. It does not apply to error messages returned by the server. It is, however, sent to the server when the PDF is generated (`language` parameter of `/api/pdf` and `/api/pdf/stream`, French by default, any value other than the 12 interface languages is refused): the titles and labels added by the application to the PDF are then written in that language — "Introduction", "Table of contents", the "Chapter" mention on chapter pages, "No chapter", "Conclusion", "License", the "Edition of …" mention under the logo at the end of the book, as well as the corresponding bookmarks. The generated pages carry the chosen language (`lang` attribute) and switch to right-to-left writing for Arabic and Persian. The license page is written entirely in that language: translated official name of the CC BY-SA 4.0 license, link to the version of the license deed in that language on creativecommons.org, reuse conditions, notices about media, imported documents and the unofficial nature of the book. Text entered by the user (title, introduction, conclusion, chapter titles) and the content of Wikipedia articles are never translated.

### 12.2 Administration page

Service monitoring page reserved for administrators, at `/admin` (for example https://wikipedia2book.toolforge.org/admin). No page of the interface links to it, and it is not indexed by search engines (`noindex`).

* **Sign-in with the Wikimedia account** (Meta-Wiki OAuth 2.0, "identification only" application: it can neither read nor change anything on the user's behalf):
  1. the "Sign in with Wikimedia" button leads to `/admin/login`, which redirects to `https://meta.wikimedia.org/w/rest.php/oauth2/authorize` with a random state, kept 10 minutes in a signed cookie (`w2b_oauth_state`);
  2. Wikimedia redirects to `/admin/callback`, which checks the state, exchanges the code for a token (`oauth2/access_token`), then reads the username (`oauth2/resource/profile`);
  3. if that name is in the list of administrators, a signed session cookie is set (`w2b_admin`: HttpOnly, Secure over HTTPS, SameSite=Lax, limited to the `/admin` path, 2 hours). Otherwise the page shows "This Wikimedia account is not a Wikipedia2Book administrator.", with no session.
  * The Wikimedia token is not kept. The server stays stateless: the session lives entirely in the cookie, signed by a key drawn when the server starts. A restart therefore invalidates sessions, and you have to sign in again.
  * Each call checks that the name is still in the list. `/admin/logout` erases the cookie.
* **Administrators**: `WIKIPEDIA2BOOK_ADMINS` variable, Wikimedia usernames written in UTF-8 hexadecimal and separated by commas. To get the value for a name: `python -c "print('Example'.encode().hex())"`. Without the variable, three default accounts (`DEFAULT_ADMINS_HEX`, the same value as on Toolforge); an invalid value prevents startup. Names are compared as on MediaWiki (first letter in upper case, `_` read as a space).
* **Configuration**:
  * `WIKIPEDIA2BOOK_OAUTH_CLIENT_ID` and `WIKIPEDIA2BOOK_OAUTH_CLIENT_SECRET`: OAuth 2.0 application registered on [Special:OAuthConsumerRegistration](https://meta.wikimedia.org/wiki/Special:OAuthConsumerRegistration/propose/oauth2), as "User identity verification only", approved automatically;
  * `WIKIPEDIA2BOOK_OAUTH_CALLBACK`: the callback address registered in the application, `https://wikipedia2book.toolforge.org/admin/callback` for Toolforge (set in the `Procfile`).
  * One application is needed per host, since the callback address differs. Without these three values, the page says that sign-in is not configured.
* **Indicators**, refreshed every 30 s:
  * **System and container**: host, platform, system, Python version, running time, processors and container limit (`cpu.max`), load over 1, 5 and 15 minutes, server processor time, threads, open files, processes and their limit (`pids.current`, `pids.max`), out-of-memory kills (`oom_kill` from `memory.events`), refitting processes, library versions (FastAPI, Starlette, Uvicorn, Pydantic, httpx, WeasyPrint, pypdf, PyMuPDF, Pillow, reportlab); a missing value (outside Linux, without cgroup) shows "—".
  * **Server**: version and commit, start time, generations in progress, container memory and its limit, process memory, free temporary space, stages waiting (memory, disk, entry). This is the data of `/api/health/details`.
  * **Usage**: requests over 24 and 48 hours, generations per status, articles and documents of the latest generations.
  * **Performance**, over successful generations: median, 90th percentile and longest duration, median per article, median PDF size, memory peak of a generation, total "Server busy" wait.
  * **Limits and alerts**: server settings and limit crossings.
  * **Latest generations** (log, start, status, duration, articles, size, wait, memory peak, version) and **requests per hour**. The number of each generation opens its detail page (`/admin/generation?id=<n>`): summary (status, start, duration, size, version, language, articles, documents, chapters, format, numbering, table of contents, error), **downloads** (type, downloaded address, size, download time, refitting time, pages, moment), **stages** (moment, stage, process, memory, details) a "Download the journal (JSON)" button that saves the journal of that generation (`/admin/api/generations/{id}`) and a "Download the request (JSON)" button that saves the requested book, in the interface's file format (`wikipedia2book-workspace`, to reopen with "Open" to reproduce the generation; `/admin/api/generations/{id}/request`). The content of images and documents imported from the computer is not kept (`data_base64` empty, `removed_base64_chars` gives its size); a request over 1 MB is not kept, and the oldest requests are forgotten beyond 30 MB in all or when their generation leaves the journal (message "The request of this generation is no longer in memory…").
  * **Refused addresses**: the last 500 addresses (`http…`) refused by Wikipedia2Book (4xx errors of `/api/sources/resolve`, `/api/articles`, `/api/books/structure`, `/api/pdf/from-source`, `/api/pdf/from-json`: address outside Wikimedia, page not found, page that is not a content page…), with the last refusal, the number of refusals, the HTTP code and the reason. A Wikimedia error (5xx) is not listed.
  * All this data is in memory only, with no IP address: 48 hours of requests, up to the last 1,000 generations with their requests and the last 500 refused addresses, lost at restart.
* **API**: `GET /admin/api/session` gives `configured` (sign-in configured) and `user` (signed-in administrator, or `null`); `GET /admin/api/summary` gives every indicator (`user`, `version`, `server`, `settings`, `usage`, `performance`, `recent`), never cached, with the administrator session only (otherwise HTTP 401, `detail.code` = `admin_login_required`). Neither is counted in the requests per hour. `GET /admin/api/generations/{id}` gives the journal of one generation and `GET /admin/api/generations/{id}/request` its request (JSON file as an attachment, 404 when no longer in memory), with the same session; `summary` also contains `refused_urls`. These routes are not in the public API description (`/docs`, `/openapi.json`). `/api/health/details` and `/api/health/generations` are reserved for monitoring with a token (section 1.3 of the technical specification).
* **Protection**:
  * security headers on `/admin`, `/admin/*` and `/api/health/*`: `Content-Security-Policy` (no outside source, no display inside another site's frame), `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`;
  * `/admin/login` and `/admin/callback`, which require no identification, are limited in calls per minute; beyond that, "Too many sign-in attempts: try again in a minute." and an alert;
  * the page and its API only read: no action changes the server.
* Texts in the 12 interface languages (`admin.*` keys). Tests: `tests/test_admin.py`.

## 15\. Compliance with Wikipedia licenses

The software must comply with the licenses that apply to content retrieved from Wikipedia.

Wikipedia texts are generally published under the Creative Commons Attribution-ShareAlike license (CC BY-SA). Each article keeps, in the official Wikipedia PDF included in the book, the license and attribution notices as generated by Wikipedia itself.

The software:

* Keeps the link to each original article.

* Adds to the book a "License" page, just after the conclusion, stating that the texts of Wikipedia and of the other projects under the same license (Wikibooks, Wikivoyage, Wikiversity, Wikiquote, Wiktionary) are under the Creative Commons Attribution-ShareAlike 4.0 International license (CC BY-SA 4.0), naming the projects present in the book, with the link to the license, a summary of the reuse conditions, and a sentence stating that the authors of each article are credited by the link to its source at the end of the article ("Ce document provient de…" in the Wikipedia PDF: a permanent link to the reproduced version, whose history lists the authors). It no longer repeats the list of articles with their address and that of their history ("Sources and authors", up to 1.9.4), redundant with this link. Imported documents are listed there as not covered by this license. If the book contains Wikisource texts, the page states that they are mostly in the public domain, the others (translations, recent editions) being under the license shown on their Wikisource page, usually CC BY-SA 4.0; if it contains Wikinews articles, that they are under the Creative Commons Attribution license (CC BY), in the version shown on their page; the CC BY-SA statement is shown only if the book contains at least one page of a project under that license. This page also states that the book is not an official publication of the projects it takes pages from (Wikipedia by default) or of the Wikimedia Foundation; the project names are those of the interface language (`site_*` in `PDF_LABELS`, for example "Wikilivres" in French, "Wikibooks" in English); it is written entirely in the interface language (section 12.1).

* Does not alter the content, credits or license notices printed by Wikipedia in its own PDF.

* Does not present the generated book as an official Wikipedia publication.

Images and media embedded by Wikipedia in its PDF export keep their own license notices; the software does not extract them separately and does not perform any independent license check.

**Wikipedia2Book license.** Wikipedia2Book is free software, distributed under the [GNU Affero General Public License v3.0](https://www.gnu.org/licenses/agpl-3.0.html) (AGPL-3.0). The full text is in the [LICENSE](https://github.com/gmoulard/wikipedia2book/blob/main/LICENSE) file.

In short, you may use, study, modify and redistribute this software, provided that any modified version you distribute is published under the same license with its source code. Because this is the *Affero* GPL, this obligation also applies when a modified version is only offered as a network service: its users must be able to obtain its source code.

This license covers the application's code only. The books it generates are made of Wikipedia content, published under its own license ([CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)), which is stated on the license page of each generated PDF.

Each source file starts with a short AGPL-3.0 license header.

## 16\. Acceptance criteria

The current version is considered functional if the following points are validated:

* Adding several main articles (URL, title, search, Wikipedia book page) from a single field, the type of input being recognized automatically.

* Exploration of internal links with configurable depth (API).

* Detection of duplicates among discovered articles.

* Display of an article's links in page order or in alphabetical order, filtering by title and adding to the book in one click.

* Manual selection of articles; no automatic addition of discovered articles.

* Reordering articles and creating chapters.

* Import of a Wikipedia book page keeping the real order of the articles, its subtitle and its chapters.

* Import of images or PDFs as documents included in the book, just like articles.

* Placement of the table of contents anywhere in the book, or removal.

* Retrieval of the official PDF of each selected article at export time.

* Choice of paper format, orientation and margins, including the binding margin.

* Generation of a printable PDF in which every page follows the chosen format and orientation, with cover, table of contents, navigation bookmarks and pagination (on by default); the table of contents then gives the page of each chapter and each article.

* The PDF generation button is always visible and active.

* Download of the generated PDF.

* Export and then import of the book through a local JSON file, named after the book title.

* Change of the interface language (12 languages, section 12.1) without reloading the page.

* Automatic, non-destructive suggestion of the book's introduction and author from the first article added.

## 18\. Status and future developments

Most of the functional core described in this document is implemented: a single in-memory book, adding and exploring articles, manual selection, organization into chapters, configurable formats and margins, PDF generation with navigation bookmarks.

Possible developments, not implemented to date:

* Filtering the exploration by language or by article category.

* Error logging and rate limiting of API requests.

* Broader automated test coverage (today: Python syntax, page numbering/table of contents, imported documents, Wikipedia API, translations, Toolviews statistics script, and the flow of `/api/pdf` and `/api/pdf/stream` through `tests/test_pdf_stream.py` — with Wikipedia and WeasyPrint simulated: the real rendering of pages by WeasyPrint and the interface are not covered).

* Rare Chinese characters (僻字) in the official Wikisource PDF: checked in November 2026, some characters of the CJK extensions B and later leave a blank there (LiberationSerif font without the glyph, for example 𡼢 U+21F22 in "大南寔錄/大南寔錄前編/卷10" on zh.wikisource.org), only those Wikisource provides as images are shown; the application does not change this PDF: reported to Wikimedia on 2026-11-18 (https://phabricator.wikimedia.org/T445303). Request made by PacmanD on the technical Village pump of the Chinese Wikipedia (November 2026), whose other part — importing a whole work from its contents page — is done (section 3.1).

Any development must preserve the core principles of the software, in particular the user's full control over the selection of articles and the handling of a single book at a time.

<!-- {% endraw %} -->
