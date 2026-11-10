# Wikipedia2Book

Wikipedia2Book is a web application for composing a printable PDF book directly from Wikipedia articles, with no "project" creation step: a book is ready as soon as the page opens. The user picks articles, explores related links, organizes the content into chapters and configures the layout before exporting.

## Features

- A single book, built in browser memory; its state can be exported/imported as a JSON file.
- Add articles by title, URL or search; the full content is only fetched at generation time.
- Import the list of articles from the URL of a Wikipedia book page, in their actual order.
- Book introduction and author suggested automatically from the first article added.
- Exploration of Wikipedia internal links with configurable depth and number of articles.
- Manual selection of the articles to include; discovered articles are never added automatically.
- Organization of articles into chapters, reorderable by drag and drop, and configuration of the book format.
- Import of personal images or PDFs, integrated into the book like articles.
- Book generation by assembling the official full PDFs downloaded from Wikipedia, with navigation bookmarks and continuous page numbering (table of contents included).
- Interface available in 12 languages: French, English, Spanish, Portuguese, Italian, German, Dutch, Turkish, Chinese, Japanese, Arabic and Persian (Arabic and Persian right-to-left).

## Architecture

- Python and FastAPI for the backend.
- HTML, CSS and JavaScript for the web interface (single page, no framework).
- Official MediaWiki API for search and exploration; official PDF endpoint to fetch full articles at export time.
- JSON exchanged with the API, with no server-side persistence.
- WeasyPrint for the cover, chapter pages and conclusion; pypdf to merge PDFs in memory; reportlab for page numbers and for converting imported images to PDF.
- Docker for deployment.

Functional and technical details are described in [SPECIFICATIONS.md](SPECIFICATIONS.md) (in French).

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
sh docker-build.sh
docker run --rm -p 8000:8000 wikipedia2book
```

The `docker-build.sh` script automatically injects the git commit, date and author into the image via `--build-arg`, so the footer displays the correct version.

The application is then reachable at `http://localhost:8000`.

## Deployment

- [Northflank](https://prod--wikipedia2book--wkvpbnfj6h4v.code.run) (Prod--wikipedia2book--wkvpbnfj6h4v.code.run)
- [Railway](https://wikipedia2book-production.up.railway.app/)

The production API documentation is available on [Railway](https://wikipedia2book-production.up.railway.app/docs).
