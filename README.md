# Wikipedia2Book

<p align="center"><img src="app/static/Wikipedia2bookLogo.png" alt="Wikipedia2Book logo" width="180"></p>


Wikipedia2Book is a web application that allows you to compile a book in a printable PDF format. 
Users can select a Wikipedia book or specific articles, explore related links, organize content into chapters and volumes, and configure the layout before exporting the final PDF file. 
Available for: Wikipedia, Wikisource, Wikibooks, Wikivoyage, Wikiversity, Wikiquote, Wiktionary, and Wikinews.


## Features

- A single book, built in browser memory; its state can be exported/imported as a JSON file.
- A single input field for an article URL, a Wikipedia book page or a title: the kind of page is detected automatically on Wikipedia (`POST /api/sources/resolve`); the full content is only fetched at generation time.
- Import the list of articles from a Wikipedia book page, in their actual order.
- Pages of the other Wikimedia projects (Wikisource, Wikibooks, Wikivoyage, Wikiversity, Wikiquote, Wiktionary, Wikinews) accepted by URL or interwiki prefix (`b:Title`, `voy:fr:Title`), with the project's official PDF.
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
- WeasyPrint for the cover, chapter pages, license page (CC BY-SA 4.0, with article sources) and conclusion; pypdf to recompose pages to the book format; PyMuPDF to assemble the book on temporary disk in batches, so that large books do not run out of memory, and to add bookmarks, links and page numbers; reportlab for converting imported images to PDF.
- Docker for deployment.

## Documentation 

- [documentation](https://gmoulard.github.io/wikipedia2book/) on site GitHub Pages

Functional and technical details 
- [SPECIFICATIONS.fr.md](docs/SPECIFICATIONS.fr.md) (French, the reference version).
- [SPECIFICATIONS.en.md](docs/SPECIFICATIONS.en.md) (English translation) 

## Deployment

### Production deployment
- [web app](https://wikipedia2book.toolforge.org)
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
│   ├── explorer.py              # Breadth-first exploration of internal links
│   ├── book_builder.py          # HTML for cover, table of contents, chapters, license and conclusion
│   ├── pdf_generator.py         # WeasyPrint rendering, page fitting, page numbers, image import
│   ├── isolation.py             # Runs the book assembly in a separate process (memory given back after each book)
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
│   ├── toolforge-hourly.sh, toolforge_hourly.py  # Hits per hour from the Toolforge webservice logs
│   ├── update-stats.sh          # Statistics update run by GitHub Actions (daily and before each deployment)
│   ├── toolviews_chart.py       # Usage charts page for GitHub Pages
│   ├── perf_check.py, perf/     # Performance workshop run before each production release
│   └── limit_check.py           # Limit test: largest book a deployment can generate (section 13.12)
├── tests/                       # unittest suite (no network, WeasyPrint stubbed when missing)
├── .github/workflows/           # Toolforge deployment, Toolviews stats, GitHub Pages, tag check, performance check
├── Dockerfile                   # Image used by Northflank
├── Procfile, Aptfile, .python-version, toolforge-fonts.conf  # Toolforge buildpacks
├── toolinfo.json                # Toolhub metadata
├── CITATION.cff                 # Citation metadata
├── codemeta.json                # CodeMeta software metadata
├── requirements.txt             # Python dependencies
├── .claude/skills/              # Git submodule (gmoulard/claude_skills): generic Claude Code procedures code-style, spec-sync, debug-frontend, release, deploy-production
├── docs/                        # Documentation site (GitHub Pages source)
│   ├── SPECIFICATIONS.fr.md     # Reference behaviour (French original)
│   ├── SPECIFICATIONS.en.md     # English translation of the specifications
│   ├── toolviews.csv, toolforge_hourly.csv, stats.md  # Usage statistics and their charts (generated)
│   ├── comparison-mediawiki2latex.md  # Comparison with mediawiki2latex
│   ├── testLimitetoolforge.md   # Limit test results on Toolforge, by version (French)
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

## Deploying your own container

Two settings control how heavy a generation can be. They are environment variables, set in the `Dockerfile` (`ENV` line) and read when the server starts:

| Variable | Default in the `Dockerfile` | Meaning |
|---|---|---|
| `WIKIPEDIA2BOOK_ARTICLE_LIMIT` | `300` (also the default when the variable is not set, on every host) | Maximum number of articles per book. Beyond it, the API refuses the book at once (HTTP 413, code `too_many_articles`); the web interface reads the limit from `/api/version` and generates the book in several volumes instead, each under the limit. `0` lifts the limit. |
| `WIKIPEDIA2BOOK_DOWNLOADS` | `2` | Number of article PDFs downloaded from Wikipedia at the same time for a book. |

Change them in the `Dockerfile` and rebuild the image, or override them when starting the container, without rebuilding:

```bash
docker run --rm -p 8000:8000 -e WIKIPEDIA2BOOK_ARTICLE_LIMIT=100 -e WIKIPEDIA2BOOK_DOWNLOADS=1 wikipedia2book
```

The server refuses to start with an invalid value and says why.

**Number of parallel downloads.** It can only be lowered, to `1`, not raised above `2`: the [Wikimedia robot policy](https://wikitech.wikimedia.org/wiki/Robot_policy) limits the PDF service to a few simultaneous requests, and the server enforces at most 2 downloads and 25 Mbps for the whole process, whatever this setting. Only the Toolforge instance, which the policy exempts, downloads 4 PDFs at a time. Lower it to `1` to make generation gentler on Wikimedia and on a small server, at the cost of a longer download phase.

**Article limit and container memory.** Lifting the limit (`0`) is safe only if the container has enough memory: a book that does not fit makes the platform stop and restart the whole container, which also cuts the generations of every other user. Set the limit from the memory of your container, with margin for several users at once. Measurements with real articles (about 17 pages per article):

| Container memory | Largest book generated | Notes |
|---|---|---|
| 256 MB | under 20 articles | Northflank: restart at 20 articles, already very slow at 10 |
| 2 GiB | about 800 articles (14,000 pages, 780 MB of PDF) | Toolforge: failure at 1,000 articles; the official instance limits books to 300 articles (larger ones are generated in volumes) |

Count about 250 MB for the server and the assembly process themselves, plus roughly 2 to 2.5 MB per article at the peak, and keep the limit well below what your container can hold, for example a third to a half: with 2 GiB, that gives a few hundred articles; with 256 MB, nothing is left for a book of any size. To find the real maximum of your deployment, run the limit test against it (it can make the server restart, so not during busy hours):

```bash
python scripts/limit_check.py --base-url https://your-server --search 50
```

It doubles the number of articles until the first failure, then narrows down by bisection. Add `--save-pdf ./tmp` to keep each generated book (`./tmp` is ignored by git). `GET /api/health/details` shows the memory of the container and its limit, and `GET /api/health/generations` the memory reached at each stage of the last generations (details in section 13 of the [specifications](docs/SPECIFICATIONS.en.md)).


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

