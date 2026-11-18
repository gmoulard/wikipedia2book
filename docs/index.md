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

## Architecture

- Python and FastAPI for the backend.
- HTML, CSS and JavaScript for the web interface (single page, no framework).
- Official MediaWiki API for search and exploration; official PDF endpoint to fetch full articles at export time.
- JSON exchanged with the API, with no server-side persistence.
- WeasyPrint for the cover, chapter pages, license page (CC BY-SA 4.0, with article sources) and conclusion; pypdf to recompose pages to the book format; PyMuPDF to assemble the book on temporary disk in batches, so that large books do not run out of memory, and to add bookmarks, links and page numbers; reportlab for converting imported images to PDF.
- Docker for deployment.

## Documentation 

- [documentation](https://gmoulard.github.io/wikipedia2book/) on site GitHub Pages

Every document is listed in [docs.md](docs.md):
- functional specification: [FunctionalSpec.fr.md](FunctionalSpec.fr.md) (French, the reference version), [FunctionalSpec.en.md](FunctionalSpec.en.md) (English translation);
- technical specification: [TechnicalSpec.fr.md](TechnicalSpec.fr.md), [TechnicalSpec.en.md](TechnicalSpec.en.md);
- version history: [CHANGELOG.fr.md](CHANGELOG.fr.md), [CHANGELOG.en.md](CHANGELOG.en.md).

Running the application, enabling the administration page and deploying your own container: section 20 of the [technical specification](TechnicalSpec.en.md#20-running-and-deploying-an-instance). Code of Conduct and how to cite Wikipedia2Book: section 21 of the [functional specification](FunctionalSpec.en.md#21-code-of-conduct-and-citation).

## Deployment

### Production deployment
- [web app](https://wikipedia2book.toolforge.org) - exemple  [PDF](https://wikipedia2book.toolforge.org/api/pdf/from-json?url=https%3A%2F%2Fgmoulard.github.io%2Fwikipedia2book%2Fstatic%2FWrecks-of-Saint-Pierre-harbor.json
) / [website](https://wikipedia2book.toolforge.org/?json=https://gmoulard.github.io/wikipedia2book/static/Wrecks-of-Saint-Pierre-harbor.json)


- [API](https://wikipedia2book.toolforge.org/docs)
- [Toolforge usage](https://gmoulard.github.io/wikipedia2book/stats.html)

### developement 
- [Northflank](https://prod--wikipedia2book--wkvpbnfj6h4v.code.run) 

## Repository structure

```
wikipedia2book/
├── app/                         # FastAPI application (stateless server)
│   ├── main.py                  # API endpoints and PDF assembly (progress streamed as NDJSON)
│   ├── models.py                # Pydantic models: the whole book state (Project, Article, UploadedDocument)
│   ├── wikipedia_api.py         # Single MediaWiki client: search, links, book pages, official PDFs
│   ├── admin.py                 # Administration page: Wikimedia sign-in of administrators
│   ├── explorer.py              # Breadth-first exploration of internal links
│   ├── json_source.py           # Downloads a JSON book from a URL for /api/pdf/from-json
│   ├── book_builder.py          # HTML for cover, table of contents, chapters, license and conclusion
│   ├── pdf_generator.py         # WeasyPrint rendering, page fitting, page numbers, image import
│   ├── isolation.py             # Runs the book assembly in a separate process (memory given back after each book)
│   ├── resource_gate.py           # Makes each generation stage wait while the server lacks memory or disk space
│   ├── request_limits.py        # Abuse protection: request size, generations per client, send timeout, alerts
│   └── static/                  # Single-page web interface (no framework)
│       ├── index.html
│       ├── app.js               # Front-end logic
│       ├── i18n.js              # Interface translations (12 languages)
│       ├── admin.html, admin.js, admin.css   # Administration page (/admin)
│       ├── styles.css
│       ├── Wikipedia2bookLogo.png
│       ├── WikipediaLogo.png  # Wikipedia logo from Commons (CC BY-SA 3.0, Wikimedia trademark), optional on the cover and last page
│       └── testPerformanceReference.json   (reference book of the benchmark)
├── scripts/
│   ├── docker-build.sh          # Docker build with git commit/date/author injected
│   ├── toolforge-deploy.sh      # Deployment script run in the Toolforge tool account
│   ├── toolviews_stats.py       # Daily Toolviews usage statistics (not part of the app)
│   ├── toolforge-hourly.sh, toolforge_hourly.py  # Hits per hour from the Toolforge webservice logs
│   ├── update-stats.sh          # Statistics update run by GitHub Actions (daily and before each deployment)
│   ├── toolviews_chart.py       # Usage charts page for GitHub Pages
│   ├── benchmark.py, benchmark/     # Benchmark run before each production release
│   ├── benchmark_table.py       # Builds the benchmark results table of the specifications from docs/benchmark-results.csv
│   └── limit_check.py           # Limit test: largest book a deployment can generate (section 13.12)
├── tests/                       # unittest suite (no network, WeasyPrint stubbed when missing)
├── .github/workflows/           # Toolforge deployment, Toolviews stats, GitHub Pages, tag check, benchmark, security
├── Dockerfile                   # Image used by Northflank
├── Procfile, Aptfile, .python-version, toolforge-fonts.conf  # Toolforge buildpacks
├── toolinfo.json                # Toolhub metadata
├── CITATION.cff                 # Citation metadata
├── codemeta.json                # CodeMeta software metadata
├── requirements.txt             # Python dependencies
├── .claude/skills/              # Git submodule (gmoulard/claude_skills): generic Claude Code procedures code-style, spec-sync, debug-frontend, release, deploy-production
├── docs/                        # Documentation site (GitHub Pages source)
│   ├── docs.md                  # List of every document
│   ├── FunctionalSpec.fr.md, FunctionalSpec.en.md  # Functional specification (French original, English translation)
│   ├── TechnicalSpec.fr.md, TechnicalSpec.en.md    # Technical specification
│   ├── CHANGELOG.fr.md, CHANGELOG.en.md            # Version history
│   ├── _config.yml              # Just the Docs theme for the site
│   ├── benchmark-results.csv    # Every benchmark measurement, for analysis
│   ├── toolviews.csv, toolforge_hourly.csv, stats.md  # Usage statistics and their charts (generated)
│   ├── comparison-mediawiki2latex.md  # Comparison with mediawiki2latex
│   ├── comparison-ws-export.md  # Comparison with WS Export
│   ├── helpSearch.<lang>.md  # User guide for the source field in the 12 interface languages (French is the reference)
│   ├── tests-manuels.md  # Manual tests of the source field, browser and API (in French)
│   ├── testLimitetoolforge.md   # Limit test results on Toolforge, by version (French)
│   └── _includes/head_custom.html  # Mermaid rendering and statistics chart on the site
├── CODE_OF_CONDUCT.md
└── LICENSE                      # GNU AGPL v3.0
```

## Project status

The repository contains the FastAPI backend and the matching web interface. It lets you build the book in browser memory, search for or add references without downloading the full content, explore Wikipedia links, control the selection, organize chapters and set up the cover. At generation time, the full PDFs of the selected articles are fetched from Wikipedia and merged in memory. The server stores neither the book nor the PDFs: the user explicitly imports and downloads a JSON file from the interface.

## Technology stack

<p align="left">
  <!-- Project status, license & archive -->
  <a href="https://github.com/gmoulard/wikipedia2book/actions/workflows/deploy-toolforge.yml"><img src="https://github.com/gmoulard/wikipedia2book/actions/workflows/deploy-toolforge.yml/badge.svg" alt="Deploy to Toolforge"></a>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/license-AGPL--3.0-blue" alt="License: AGPL-3.0"></a>
  <a href="https://archive.softwareheritage.org/browse/origin/?origin_url=https://github.com/gmoulard/wikipedia2book"><img src="https://archive.softwareheritage.org/badge/origin/https://github.com/gmoulard/wikipedia2book/" alt="SWH Origin"></a>
  <a href="https://archive.softwareheritage.org/swh:1:dir:9c7c016d9603a4b0201ad64535767a353031bd91;origin=https://github.com/gmoulard/wikipedia2book;visit=swh:1:snp:3b1fa78021c1ad7819b82a6f38f200a9f3bfa85e;anchor=swh:1:rev:d0cd2a14a00fb848f2555a9ee62c4147230e6080"><img src="https://archive.softwareheritage.org/badge/swh:1:dir:9c7c016d9603a4b0201ad64535767a353031bd91/" alt="SWH Directory"></a>
  <a href="./CODE_OF_CONDUCT.md"><img src="https://img.shields.io/badge/Code_of_Conduct-MediaWiki-3366cc" alt="Code of Conduct"></a>
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

## License

Wikipedia2Book is free software, distributed under the [GNU Affero General Public License v3.0](https://www.gnu.org/licenses/agpl-3.0.html) (AGPL-3.0). The full text is in the [LICENSE](https://github.com/gmoulard/wikipedia2book/blob/main/LICENSE) file.

In short, you may use, study, modify and redistribute this software, provided that any modified version you distribute is published under the same license with its source code. Because this is the *Affero* GPL, this obligation also applies when a modified version is only offered as a network service: its users must be able to obtain its source code.

This license covers the application's code only. The books it generates are made of Wikipedia content, published under its own license ([CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)), which is stated on the license page of each generated PDF.

Each source file starts with a short AGPL-3.0 license header.
