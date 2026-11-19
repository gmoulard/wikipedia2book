# Wikipedia2Book

<table><tr><td>
<a href="https://wikipedia2book.toolforge.org/"><img src="https://gmoulard.github.io/wikipedia2book/static/Wikipedia2bookLogo.png" alt="Wikipedia2Book logo"></a>
</td><td><a href="https://wikipedia2book.toolforge.org/"><strong>Wikipedia2Book</strong></a> is a web application that allows you to compile a book in a printable PDF format.
Users can select a Wikipedia book or specific articles, explore related links, organize content into chapters and volumes, and configure the layout before exporting the final PDF file.
Available for: Wikipedia, Wikisource, Wikibooks, Wikivoyage, Wikiversity, Wikiquote, Wiktionary, and Wikinews.
</td></tr></table>

## Features je ne suis pas un readme

Assemble the official PDFs of Wikipedia (and other Wikimedia projects) pages into a single printable book.

* A single input field takes an article URL, a Wikipedia "book" page or a plain title; the page type is detected automatically, and the full content is only downloaded at generation time.
* Import the articles of a Wikipedia "book" page in their original order.
* Pages from Wikisource, Wikibooks, Wikivoyage, Wikiversity, Wikiquote, Wiktionary and Wikinews are accepted by URL or interwiki prefix (`b:Title`, `voy:fr:Title`), using each project's official PDF.
* Explore internal links with a configurable depth and number of articles; discovered articles are never added automatically, you pick the ones to keep.
* Organize articles into chapters and volumes with drag and drop.
* Add your own images or PDF files alongside the articles.
* Customize the title, author, table of contents, page format and cover image.
* Generate the book with navigation bookmarks, continuous page numbering and a table of contents.
* Interface in 12 languages: French, English, Spanish, Portuguese, Italian, German, Dutch, Turkish, Chinese, Japanese, Arabic and Persian (right-to-left for Arabic and Persian). The headings the app adds to the PDF (table of contents, chapters, conclusion, license, bookmarks…) follow the interface language.

## Documentation 

- [documentation](https://gmoulard.github.io/wikipedia2book/) on site GitHub Pages

Every document is listed in [docs.md](docs.md):
- functional specification: [FunctionalSpec.fr.md](FunctionalSpec.fr.md) (French, the reference version), [FunctionalSpec.en.md](FunctionalSpec.en.md) (English translation);
- technical specification: [TechnicalSpec.fr.md](TechnicalSpec.fr.md), [TechnicalSpec.en.md](TechnicalSpec.en.md);
- version history: [CHANGELOG.fr.md](CHANGELOG.fr.md), [CHANGELOG.en.md](CHANGELOG.en.md);
- deployment (Toolforge production, Northflank pre-production, API documentation, examples): section 13.5 of the [technical specification](TechnicalSpec.en.md);
- running the application, with or without Docker, and deploying your own container (settings, article limit and memory, alerts): section 13.4 of the [technical specification](TechnicalSpec.en.md);
- administration page (`/admin`): section 12.2 of the [functional specification](FunctionalSpec.en.md), setup in section 13.7 of the [technical specification](TechnicalSpec.en.md);
- license (AGPL-3.0 for the code, CC BY-SA for the books): section 15 of the [functional specification](FunctionalSpec.en.md);
- code of conduct and citation: section 17 of the [technical specification](TechnicalSpec.en.md).

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
