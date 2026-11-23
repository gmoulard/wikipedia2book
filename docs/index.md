# Wikipedia2Book

<table><tr><td>
<a href="https://wikipedia2book.toolforge.org/"><img src="https://gmoulard.github.io/wikipedia2book/static/Wikipedia2bookLogo.png" alt="Wikipedia2Book logo" width="100"></a>
</td><td><a href="https://wikipedia2book.toolforge.org/"><strong>Wikipedia2Book</strong></a> is a web application that allows you to compile a book in a printable PDF format.
Users can select a Wikipedia book or specific articles, explore related links, organize content into chapters and volumes, and configure the layout before exporting the final PDF file.
Available for: Wikipedia, Wikisource, Wikibooks, Wikivoyage, Wikiversity, Wikiquote, Wiktionary, and Wikinews.
</td></tr></table>

## Features

Wikipedia2Book turns a selection of Wikimedia pages into one printable book. It never rewrites the articles: each one is included through the official PDF that Wikipedia (or the other Wikimedia project) produces for it, so the text, images and references are exactly those of the wiki. The application only adds what a book needs around them, such as a cover, a table of contents, chapter pages, a license page and page numbers, and it resizes every page to the paper format you choose. Everything happens in your browser, in three steps (Sources, Organization, Editing): nothing is stored on the server, and you keep your work by saving the book as a JSON file that you can open again later. The interface is available in 12 languages (French, English, Spanish, Portuguese, Italian, German, Dutch, Turkish, Chinese, Japanese, Arabic and Persian, the last two right to left), and the headings added to the PDF follow the language you choose.

**Search.** The Sources step has a single input field, and you never have to say what you are typing. Enter the title of an article, the address of a page or the name of a Wikipedia book page, and the application asks Wikipedia what it is, following redirects. When no page has exactly that title, Wikipedia's search results appear under the field while you type and can be added with one click. The "All" choice in the language list searches the same title in every proposed language at once. Once an article is in the book, its "Related articles" button lists the articles it links to, in the order in which they appear in the page. You can filter that list or sort it alphabetically, and add each suggestion yourself: nothing is ever added without your choice. A help page, available in the 12 languages, shows with examples everything the field accepts.

![Sources step: your articles and the suggestions taken from the links of an article](static/screen-sources.png)

**Sources.** Besides Wikipedia, the field accepts pages from Wikisource, Wikibooks, Wikivoyage, Wikiversity, Wikiquote, Wiktionary and Wikinews, by their address or by an interwiki prefix such as `b:Title` or `voy:en:Lyon`, and each one is printed with its own project's official PDF. A Wikipedia book page (`Book:…` or `User:…/Books/…`) brings all its articles in their real order, with its chapters and subtitle. The table of contents of a Wikibooks book or of a Wikisource work can be imported in full, chapters included, and a Wikibooks printable version is read like a book. You can also paste a whole list of pages, one per line, with bullets, `[[wiki links]]`, Markdown links or language prefixes, or paste the source text of a book page. A book saved as JSON and published online opens directly from its address, and the PDF is always made from the current version of each page.

**Organization.** The second step shows the book as a single list that reads from top to bottom. You reorder articles by drag and drop, create chapters and give them a title, and each article belongs to the chapter placed above it. Next to the articles, you can add your own images and PDF files, either from your computer or by their address (a Wikimedia Commons file page works), and even any web page, which the server converts to PDF. Each imported document gets a title of its own that replaces the file name in the book. A large book can be split into volumes where you want. Above 300 articles, the application splits it into volumes by itself, between chapters, and generates one PDF per volume.

![Organization step: articles, an imported image and a chapter in one list](static/screen-organization.png)

**Editing.** The last step gathers everything that makes the object a book. For the cover, you set the title, subtitle, author and a short note, and you can add a background image, a background color, the text color and font, and the Wikipedia logo. The default cover is white, in the style of Wikipedia headings. You can write an introduction and a conclusion, choose whether pages are numbered, and place the table of contents at the start or at the end of the book, or leave it out. An optional last page can carry its own image, color or logo. Finally, you choose the paper size (A0 to A6, Letter, Legal or a custom size), the orientation and the margins, including a binding margin for printing.

![Editing step: book identity and content](static/screen-editing.png)

**The generated PDF, the API and administration.** The "Generate PDF" button downloads the official PDF of every article, recomposes every page to the chosen format and assembles the book while a window shows each step. The result has bookmarks for navigation, page numbers that run across the whole book, a table of contents whose entries link to their pages, and a license page that credits each article under CC BY-SA 4.0. If the server crashes, generation restarts by itself. Every feature of the interface is also available through an HTTP API, documented at `/docs`: you can, for example, get the PDF of a book saved as JSON with a single address (`/api/pdf/from-json?url=…`) or build a book from a list of sources (`/api/pdf/from-source`). Administrators sign in with their Wikimedia account on an `/admin` page that shows the state of the server, the latest generations with their stages and memory use, and the addresses the service refused, without ever recording who made a request.

## Important addresses

| What | Address |
| --- | --- |
| Home page (production, Toolforge) | <https://wikipedia2book.toolforge.org/> |
| Application | <https://wikipedia2book.toolforge.org/app> |
| Frequently asked questions | <https://wikipedia2book.toolforge.org/faq> |
| Pre-production (Northflank, follows `main`) | <https://prod--wikipedia2book--wkvpbnfj6h4v.code.run/> |
| Example book opened in the application | <https://wikipedia2book.toolforge.org/?json=https://gmoulard.github.io/wikipedia2book/static/Wrecks-of-Saint-Pierre-harbor.json> |
| Example PDF generated on request | <https://wikipedia2book.toolforge.org/api/pdf/from-json?url=https%3A%2F%2Fgmoulard.github.io%2Fwikipedia2book%2Fstatic%2FWrecks-of-Saint-Pierre-harbor.json&language=en> |
| Example PDF, regenerated every day | <https://gmoulard.github.io/wikipedia2book/static/Wrecks-of-Saint-Pierre-harbor.pdf> |
| Example book (JSON file) | <https://gmoulard.github.io/wikipedia2book/static/Wrecks-of-Saint-Pierre-harbor.json> |
| Interactive API documentation | <https://wikipedia2book.toolforge.org/docs> |
| Administration page | <https://wikipedia2book.toolforge.org/admin> |
| Search help | <https://gmoulard.github.io/wikipedia2book/helpSearch.en.html> |
| Usage statistics | <https://gmoulard.github.io/wikipedia2book/stats.html> |
| Documentation site | <https://gmoulard.github.io/wikipedia2book/> |
| Source code | <https://github.com/gmoulard/wikipedia2book> |
| Wikidata item | <https://www.wikidata.org/wiki/Q142203097> |

## Technology stack

<p align="left">
  <!-- Project status, license & archive -->
  <a href="https://github.com/gmoulard/wikipedia2book/actions/workflows/deploy-toolforge.yml"><img src="https://github.com/gmoulard/wikipedia2book/actions/workflows/deploy-toolforge.yml/badge.svg" alt="Deploy to Toolforge"></a>
  <a href="https://github.com/gmoulard/wikipedia2book/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-AGPL--3.0-blue" alt="License: AGPL-3.0"></a>
  <a href="https://archive.softwareheritage.org/browse/origin/?origin_url=https://github.com/gmoulard/wikipedia2book"><img src="https://archive.softwareheritage.org/badge/origin/https://github.com/gmoulard/wikipedia2book/" alt="SWH Origin"></a>
  <a href="https://archive.softwareheritage.org/swh:1:dir:9c7c016d9603a4b0201ad64535767a353031bd91;origin=https://github.com/gmoulard/wikipedia2book;visit=swh:1:snp:3b1fa78021c1ad7819b82a6f38f200a9f3bfa85e;anchor=swh:1:rev:d0cd2a14a00fb848f2555a9ee62c4147230e6080"><img src="https://archive.softwareheritage.org/badge/swh:1:dir:9c7c016d9603a4b0201ad64535767a353031bd91/" alt="SWH Directory"></a>
  <a href="https://github.com/gmoulard/wikipedia2book/blob/main/CODE_OF_CONDUCT.md"><img src="https://img.shields.io/badge/Code_of_Conduct-MediaWiki-3366cc" alt="Code of Conduct"></a>
  <img src="https://img.shields.io/badge/vibe-coded-blueviolet" alt="Vibe Coded">
</p>

<p align="left">
  <!-- Frontend -->
  <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript"><img src="https://img.shields.io/badge/JavaScript-vanilla-f7df1e?logo=javascript&logoColor=black" alt="JavaScript"></a>
  <a href="https://developer.mozilla.org/en-US/docs/Web/HTML"><img src="https://img.shields.io/badge/HTML5-e34f26?logo=html5&logoColor=white" alt="HTML5"></a>
  <a href="https://developer.mozilla.org/en-US/docs/Web/CSS"><img src="https://img.shields.io/badge/CSS3-1572b6?logo=css3&logoColor=white" alt="CSS3"></a>
  <img src="https://img.shields.io/badge/i18n-12_languages-green" alt="12 interface languages">
</p>

<p align="left">
  <!-- Backend -->
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.12-3776ab?logo=python&logoColor=white" alt="Python 3.12"></a>
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white" alt="FastAPI"></a>
  <a href="https://docs.pydantic.dev/"><img src="https://img.shields.io/badge/Pydantic-e92063?logo=pydantic&logoColor=white" alt="Pydantic"></a>
  <a href="https://www.uvicorn.org/"><img src="https://img.shields.io/badge/Uvicorn-222" alt="Uvicorn"></a>
</p>

<p align="left">
  <!-- PDF & content -->
  <a href="https://weasyprint.org/"><img src="https://img.shields.io/badge/WeasyPrint-HTML_to_PDF-c03a2b" alt="WeasyPrint"></a>
  <a href="https://pypdf.readthedocs.io/"><img src="https://img.shields.io/badge/pypdf-merge-4b8bbe" alt="pypdf"></a>
  <a href="https://www.reportlab.com/"><img src="https://img.shields.io/badge/ReportLab-page_numbers-6d4c41" alt="ReportLab"></a>
  <a href="https://www.mediawiki.org/wiki/API:Main_page"><img src="https://img.shields.io/badge/MediaWiki-API-36c?logo=mediawiki&logoColor=white" alt="MediaWiki API"></a>
  <a href="https://creativecommons.org/licenses/by-sa/4.0/"><img src="https://img.shields.io/badge/content-CC_BY--SA_4.0-lightgrey?logo=creativecommons" alt="Wikipedia content: CC BY-SA 4.0"></a>
</p>

<p align="left">
  <!-- Deployment & tests -->
  <a href="https://wikipedia2book.toolforge.org"><img src="https://img.shields.io/badge/Toolforge-deployed-3366cc?logo=wikimedia-commons&logoColor=white" alt="Toolforge"></a>
  <a href="https://www.docker.com/"><img src="https://img.shields.io/badge/Docker-2496ed?logo=docker&logoColor=white" alt="Docker"></a>
  <a href="https://github.com/gmoulard/wikipedia2book/actions"><img src="https://img.shields.io/badge/GitHub_Actions-CI%2FCD-2088ff?logo=githubactions&logoColor=white" alt="GitHub Actions"></a>
  <a href="https://docs.python.org/3/library/unittest.html"><img src="https://img.shields.io/badge/tests-unittest-0a9edc" alt="unittest"></a>
</p>
