# Wikipedia2Book

<p align="center"><img src="app/static/Wikipedia2bookLogo.png" alt="Wikipedia2Book logo" width="180"></p>


Wikipedia2Book is a web application for composing a printable PDF book directly from Wikipedia articles: one book at a time, ready as soon as the page opens. The user picks articles, explores related links, organizes the content into chapters and configures the layout before exporting.

## Features

- A single book, built in browser memory; its state can be exported/imported as a JSON file.
- A single input field for an article URL, a Wikipedia book page or a title: the kind of page is detected automatically on Wikipedia (`POST /api/sources/resolve`); the full content is only fetched at generation time.
- Import the list of articles from a Wikipedia book page, in their actual order.
- Book introduction and author suggested automatically from the first article added.
- Exploration of Wikipedia internal links with configurable depth and number of articles.
- Manual selection of the articles to include; discovered articles are never added automatically.
- Organization of articles into chapters, reorderable by drag and drop, and configuration of the book format.
- Import of personal images or PDFs, integrated into the book like articles.
- Book generation by assembling the official full PDFs downloaded from Wikipedia, with navigation bookmarks and continuous page numbering (table of contents included).
- Interface available in 12 languages: French, English, Spanish, Portuguese, Italian, German, Dutch, Turkish, Chinese, Japanese, Arabic and Persian (Arabic and Persian right-to-left). The titles the app adds to the generated PDF (table of contents, chapter, conclusion, license, bookmarks…) follow the interface language.

## Architecture

- Python and FastAPI for the backend.
- HTML, CSS and JavaScript for the web interface (single page, no framework).
- Official MediaWiki API for search and exploration; official PDF endpoint to fetch full articles at export time.
- JSON exchanged with the API, with no server-side persistence.
- WeasyPrint for the cover, chapter pages, license page (CC BY-SA 4.0, with article sources) and conclusion; pypdf to merge PDFs in memory; reportlab for page numbers and for converting imported images to PDF.
- Docker for deployment.

Documentation site (GitHub Pages): https://gmoulard.github.io/wikipedia2book/

Functional and technical details are described in [SPECIFICATIONS.en.md](docs/SPECIFICATIONS.en.md) (English translation) and [SPECIFICATIONS.fr.md](docs/SPECIFICATIONS.fr.md) (French, the reference version).

## Repository structure

```
wikipedia2book/
├── app/                         # FastAPI application (stateless server)
│   ├── main.py                  # API endpoints and PDF assembly (progress streamed as NDJSON)
│   ├── models.py                # Pydantic models: the whole book state (Project, Article, UploadedDocument)
│   ├── wikipedia_api.py         # Single MediaWiki client: search, links, book pages, official PDFs
│   ├── explorer.py              # Breadth-first exploration of internal links
│   ├── book_builder.py          # HTML for cover, table of contents, chapters, license and conclusion
│   ├── pdf_generator.py         # WeasyPrint rendering, page fitting, page numbers, image import
│   └── static/                  # Single-page web interface (no framework)
│       ├── index.html
│       ├── app.js               # Front-end logic
│       ├── i18n.js              # Interface translations (12 languages)
│       ├── styles.css
│       └── Wikipedia2bookLogo.png
├── scripts/
│   ├── docker-build.sh          # Docker build with git commit/date/author injected
│   ├── toolforge-deploy.sh      # Deployment script run in the Toolforge tool account
│   ├── toolviews_stats.py       # Daily Toolviews usage statistics (not part of the app)
│   └── toolviews_chart.py       # Usage charts page for GitHub Pages
├── tests/                       # unittest suite (no network, WeasyPrint stubbed when missing)
├── .github/workflows/           # Toolforge deployment, Toolviews stats, GitHub Pages
├── Dockerfile                   # Image used by Railway and Northflank
├── Procfile, Aptfile, .python-version, toolforge-fonts.conf  # Toolforge buildpacks
├── toolinfo.json                # Toolhub metadata
├── CITATION.cff                 # Citation metadata
├── codemeta.json                # CodeMeta software metadata
├── requirements.txt             # Python dependencies
├── docs/                        # Documentation site (GitHub Pages source)
│   ├── SPECIFICATIONS.fr.md     # Reference behaviour (French original)
│   ├── SPECIFICATIONS.en.md     # English translation of the specifications
│   ├── toolviews.csv, stats.md  # Daily usage statistics and their charts (generated)
│   └── _includes/head-custom.html  # Mermaid rendering on the site
├── CODE_OF_CONDUCT.md
└── LICENSE                      # GNU AGPL v3.0
```

## Project status

The repository contains the FastAPI backend and the matching web interface. It lets you build the book in browser memory, search for or add references without downloading the full content, explore Wikipedia links, control the selection, organize chapters and set up the cover. At generation time, the full PDFs of the selected articles are fetched from Wikipedia and merged in memory. The server stores neither the book nor the PDFs: the user explicitly imports and downloads a JSON file from the interface.

## Running the application

With Python 3.12 and the system dependencies required by WeasyPrint installed:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The web interface is available at `http://localhost:8000` and the interactive API documentation at `http://localhost:8000/docs`.

The container can be run directly:

```bash
sh scripts/docker-build.sh
docker run --rm -p 8000:8000 wikipedia2book
```

The `scripts/docker-build.sh` script automatically injects the git commit, date and author into the image via `--build-arg`, so the footer displays the correct version.

The application is then reachable at `http://localhost:8000`.

## Deployment Toolforge
- [web app](https://wikipedia2book.toolforge.org)
- [API](https://wikipedia2book.toolforge.org/docs)

## dev
- [Northflank](https://prod--wikipedia2book--wkvpbnfj6h4v.code.run) 
- [Railway](https://wikipedia2book-production.up.railway.app/)

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

## Code of Conduct

The development of this software is covered by a [Code of Conduct](CODE_OF_CONDUCT.md).

## License

Wikipedia2Book is free software, distributed under the [GNU Affero General Public License v3.0](https://www.gnu.org/licenses/agpl-3.0.html) (AGPL-3.0). The full text is in the [LICENSE](LICENSE) file.

In short, you may use, study, modify and redistribute this software, provided that any modified version you distribute is published under the same license with its source code. Because this is the *Affero* GPL, this obligation also applies when a modified version is only offered as a network service: its users must be able to obtain its source code.

This license covers the application's code only. The books it generates are made of Wikipedia content, published under its own license ([CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)), which is stated on the license page of each generated PDF.

Each source file starts with a short AGPL-3.0 license header.

## Citation

If you use Wikipedia2Book in your work, please cite the archived release on [Software Heritage](https://archive.softwareheritage.org/swh:1:dir:9c7c016d9603a4b0201ad64535767a353031bd91;origin=https://github.com/gmoulard/wikipedia2book;visit=swh:1:snp:3b1fa78021c1ad7819b82a6f38f200a9f3bfa85e;anchor=swh:1:rev:d0cd2a14a00fb848f2555a9ee62c4147230e6080):

```bibtex
@software{moulard_wikipedia2book_2026,
  author  = {Moulard, Guillaume},
  title   = {Wikipedia2Book},
  version = {v1.6.4},
  year    = {2026},
  url     = {https://github.com/gmoulard/wikipedia2book},
  license = {AGPL-3.0-only},
  note    = {SWHID: swh:1:dir:9c7c016d9603a4b0201ad64535767a353031bd91}
}
```

Machine-readable citation metadata is also available in [`CITATION.cff`](CITATION.cff) and [`codemeta.json`](codemeta.json).

