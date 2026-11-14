# This file is part of Wikipedia2Book
# <https://github.com/gmoulard/wikipedia2book>.
# Copyright (c) 2026 Guillaume Moulard.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import asyncio
import base64
import json
import re
import subprocess
from io import BytesIO
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pypdf import PdfReader, PdfWriter

from app.book_builder import (
    build_chapter_page_html,
    build_conclusion_page_html,
    build_cover_html,
    PDF_LABELS,
    TOC_LINK_PREFIX,
    build_license_page_html,
    book_slots,
    build_toc_html,
    ordered_article_groups,
    page_size_mm,
    pdf_label,
    toc_slot_index,
)
from app.explorer import discover_related_articles
from app.models import (
    DEFAULT_BOOK_CONCLUSION,
    Article,
    ArticleRequest,
    BookChapter,
    BookImportRequest,
    BookGenerationRequest,
    Project,
    ProjectExplorationRequest,
    SourceRequest,
    SourceResolution,
    UploadedDocument,
    WikipediaBookGenerationRequest,
    WikipediaBookImport,
    utc_now,
)
from app.pdf_generator import (
    add_internal_links,
    fit_pdf_to_format,
    generate_pdf,
    image_to_pdf,
    internal_links,
    stamp_page_numbers,
)
from app.wikipedia_api import (
    WIKIPEDIA_PDF_PAPERS,
    MediaWikiClient,
    MediaWikiError,
    MediaWikiPageNotFound,
    article_url,
    parse_article_url,
    validate_language,
)


app = FastAPI(title="Wikipedia2Book", version="1.6.10")
static_directory = Path(__file__).parent / "static"
PDF_LANGUAGE_PATTERN = "^(" + "|".join(PDF_LABELS) + ")$"
app.mount("/static", StaticFiles(directory=static_directory), name="static")


@app.middleware("http")
async def revalidate_web_app_files(request: Request, call_next):
    response = await call_next(request)
    if request.url.path == "/" or request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-cache"
    return response


@app.get("/", include_in_schema=False)
def web_app() -> FileResponse:
    return FileResponse(static_directory / "index.html", media_type="text/html")


def _mediawiki_error(error: Exception) -> HTTPException:
    if isinstance(error, ValueError):
        return HTTPException(status_code=422, detail=str(error))
    if isinstance(error, MediaWikiPageNotFound):
        return HTTPException(status_code=404, detail=str(error))
    return HTTPException(status_code=502, detail=str(error))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/version")
def version() -> dict[str, str]:
    try:
        commit = subprocess.check_output(
            ["git", "log", "-1", "--format=%H|%h|%ci|%an"], text=True, stderr=subprocess.DEVNULL
        ).strip()
        full, short, date, author = commit.split("|")
        return {"version": app.version, "commit": full, "short": short, "date": date, "author": author}
    except Exception:
        import os
        full = next(
            (value for value in (os.environ.get("GIT_COMMIT"), os.environ.get("RAILWAY_GIT_COMMIT_SHA"))
             if value and value != "unknown"),
            "",
        )
        return {
            "version": app.version,
            "commit": full,
            "short": full[:7],
            "date": os.environ.get("GIT_DATE", ""),
            "author": os.environ.get("GIT_AUTHOR", ""),
        }


@app.get("/api/search")
async def search_articles(
    query: str = Query(min_length=2, max_length=200),
    language: str = Query(default="fr", pattern=r"^[a-z0-9-]{2,12}$"),
    limit: int = Query(default=10, ge=1, le=20),
) -> list[dict]:
    try:
        async with MediaWikiClient() as client:
            return await client.search(query, language, limit)
    except (MediaWikiError, ValueError) as error:
        raise _mediawiki_error(error) from error


@app.get("/api/articles/intro")
async def article_intro(
    title: str = Query(min_length=1, max_length=300),
    language: str = Query(default="fr", pattern=r"^[a-z0-9-]{2,12}$"),
) -> dict[str, str]:
    try:
        async with MediaWikiClient() as client:
            introduction, creator = await client.get_intro_and_creator(title, language)
    except (MediaWikiError, ValueError) as error:
        raise _mediawiki_error(error) from error
    return {"introduction": introduction, "author": creator}


@app.post("/api/articles", response_model=Article, status_code=201)
def add_article_reference(payload: ArticleRequest) -> Article:
    try:
        language, title = (
            parse_article_url(payload.url) if payload.url else (payload.language, payload.title)
        )
        language = validate_language(language)
        title = title.strip()
        if not title:
            raise ValueError("Le titre de l’article ne peut pas être vide.")
    except ValueError as error:
        raise _mediawiki_error(error) from error
    return Article(
        page_id=payload.page_id,
        title=title,
        language=language,
        url=payload.url or article_url(language, title),
        summary=payload.summary,
        selected=True,
    )


@app.post("/api/books/import", response_model=list[Article])
async def import_wikipedia_book(payload: BookImportRequest) -> list[Article]:
    return (await read_wikipedia_book(payload)).articles


@app.post("/api/books/structure", response_model=WikipediaBookImport)
async def read_wikipedia_book(payload: BookImportRequest) -> WikipediaBookImport:
    try:
        language, title = parse_article_url(payload.url)
        async with MediaWikiClient() as client:
            return await _wikipedia_book(client, language, title)
    except (MediaWikiError, ValueError) as error:
        raise _mediawiki_error(error) from error


@app.post("/api/sources/resolve", response_model=SourceResolution)
async def resolve_source(payload: SourceRequest) -> SourceResolution:
    text = payload.input.strip()
    is_url = bool(re.match(r"^[a-z]+://", text, re.IGNORECASE))
    try:
        if not text:
            raise ValueError("Saisissez une URL, une page de livre ou un titre Wikipédia.")
        language, title = parse_article_url(text) if is_url else (validate_language(payload.language), text)
        async with MediaWikiClient() as client:
            page = await client.get_page(title, language)
            if page is None:
                if is_url:
                    raise MediaWikiPageNotFound(f"La page Wikipédia « {title} » est introuvable.")
                return SourceResolution(kind="search", results=await client.search(text, language, 8))
            title, namespace = page
            if namespace == 0:
                return SourceResolution(
                    kind="article",
                    article=Article(title=title, language=language, url=article_url(language, title), selected=True),
                )
            return SourceResolution(
                kind="book", book=await _wikipedia_book(client, language, title), book_title=_book_name(title)
            )
    except (MediaWikiError, ValueError) as error:
        raise _mediawiki_error(error) from error


async def _wikipedia_book(client: MediaWikiClient, language: str, title: str) -> WikipediaBookImport:
    book = await client.get_book(title, language, limit=200)
    if not book.chapters:
        raise HTTPException(
            status_code=422,
            detail="Cette page de livre ne contient aucun lien vers des articles Wikipédia.",
        )
    articles: list[Article] = []
    chapters: list[BookChapter] = []
    for chapter_title, titles in book.chapters:
        chapter_articles = [
            Article(title=article_title, language=language, url=article_url(language, article_title), selected=True)
            for article_title in titles
        ]
        articles.extend(chapter_articles)
        if chapter_title:
            chapters.append(
                BookChapter(title=chapter_title[:120], article_keys=[article.key for article in chapter_articles])
            )
    return WikipediaBookImport(
        articles=articles,
        subtitle=book.subtitle[:300],
        chapters=chapters,
        unassigned_first=bool(chapters) and not book.chapters[0][0],
    )


@app.post("/api/explore", response_model=Project)
async def explore_project(payload: ProjectExplorationRequest) -> Project:
    project = payload.project
    if not project.main_articles or payload.max_depth == 0:
        return project
    try:
        async with MediaWikiClient() as client:
            discovered = await discover_related_articles(
                client, project.main_articles, payload.max_depth, payload.max_articles
            )
    except (MediaWikiError, ValueError) as error:
        raise _mediawiki_error(error) from error

    known = {article.key for article in project.main_articles + project.discovered_articles}
    project.discovered_articles.extend(article for article in discovered if article.key not in known)
    project.updated_at = utc_now()
    return project


def _selected_items(project: Project) -> list[Article | UploadedDocument]:
    selected = [
        item
        for item in project.main_articles + project.discovered_articles + project.uploaded_documents
        if item.selected
    ]
    if not selected:
        raise HTTPException(status_code=400, detail="Sélectionnez au moins un article avant l’export.")
    return selected


def _apply_default_book_title(project: Project, selected: list[Article | UploadedDocument]) -> None:
    if project.book_title.strip():
        return
    ordered = [item for _, items in ordered_article_groups(project, selected) for item in items]
    first = next((item for item in ordered if isinstance(item, Article)), ordered[0])
    project.book_title = first.title[:200]


def _pdf_error_detail(error: Exception) -> str:
    if isinstance(error, (MediaWikiError, ValueError)):
        return str(error)
    return "La génération du PDF a échoué."


async def build_book_pdf(project: Project, selected: list[Article | UploadedDocument], language: str):
    groups = ordered_article_groups(project, selected, language)
    writer = PdfWriter()
    streams: list[BytesIO] = []
    page_width_mm, page_height_mm = page_size_mm(project)
    unique_items = list({item.key: item for _, items in groups for item in items}.values())
    total = len(unique_items) + 3 + (2 if project.page_numbers else 0)
    step = 0

    def progress(code: str, **params) -> dict:
        nonlocal step
        step += 1
        return {"type": "progress", "step": step, "total": total, "code": code, **params}

    # NE PAS appeler WeasyPrint ni pypdf directement ici : un calcul bloquant gèle le serveur et retarde l'envoi des messages de progression.
    async def render(html: str) -> bytes:
        return await asyncio.to_thread(generate_pdf, html)

    def fit(pdf_data: bytes) -> "asyncio.Future[bytes]":
        # NE PAS sauter fit_pdf_to_format, même pour une page déjà au bon format : c'est lui qui décide (recomposition ou simple ajustement de la taille).
        return asyncio.ensure_future(asyncio.to_thread(fit_pdf_to_format, pdf_data, page_width_mm, page_height_mm))

    async def append_fitted(fitted: bytes) -> int:
        stream = BytesIO(fitted)
        streams.append(stream)
        page_number = len(writer.pages)
        await asyncio.to_thread(writer.append, stream)
        return page_number

    async def append_pdf(pdf_data: bytes) -> int:
        return await append_fitted(await fit(pdf_data))

    def page_count(pdf_data: bytes) -> int:
        return len(PdfReader(BytesIO(pdf_data)).pages)

    def document_pdf(document: UploadedDocument) -> bytes:
        data = base64.b64decode(document.data_base64)
        if document.kind == "pdf":
            return data
        return image_to_pdf(data, page_width_mm, page_height_mm)

    item_pdfs: dict[str, bytes] = {}
    fitted_items: dict[str, asyncio.Future[bytes]] = {}
    paper = WIKIPEDIA_PDF_PAPERS.get(project.page_format, "a4")
    try:
        async with MediaWikiClient() as client:
            for item in unique_items:
                if isinstance(item, Article):
                    yield progress("fetch_article", title=item.title)
                    item_pdfs[item.key] = await client.get_article_pdf(item.title, item.language, paper)
                else:
                    yield progress("prepare_document", title=item.title)
                    item_pdfs[item.key] = await asyncio.to_thread(document_pdf, item)
                fitted_items[item.key] = fit(item_pdfs[item.key])
    except BaseException:
        for task in fitted_items.values():
            task.cancel()
        raise

    slots = book_slots(groups)
    toc_at = toc_slot_index(project, groups, slots)

    article_pages: dict[str, int] = {}
    chapter_pages: list[int | None] = [None] * len(groups)
    cover: bytes | None = None
    if project.page_numbers:
        yield progress("compute_page_numbers")
        cover = await render(build_cover_html(project, language))
        cursor = page_count(cover) + 1
        toc_pages = (
            page_count(await render(build_toc_html(project, selected, language=language)))
            if toc_at is not None and toc_at < len(slots)
            else 0
        )
        for index, (kind, value) in enumerate(slots):
            if index == toc_at:
                cursor += toc_pages
            if kind == "chapter":
                chapter_pages[value] = cursor
                cursor += 1
            else:
                article_pages[value.key] = cursor
                cursor += await asyncio.to_thread(page_count, item_pdfs[value.key])

    yield progress("cover_and_toc")
    toc = (
        await render(build_toc_html(project, selected, article_pages, chapter_pages, language))
        if project.table_of_contents
        else None
    )
    if cover is None:
        cover = await render(build_cover_html(project, language))

    yield progress("assemble")
    root_outline = writer.add_outline_item(
        project.book_title or project.name,
        await append_pdf(cover),
    )
    chapter_outline = root_outline
    toc_start: int | None = None
    targets: dict[str, int] = {}
    for index, (kind, value) in enumerate(slots):
        if index == toc_at:
            toc_start = await append_pdf(toc)
            writer.add_outline_item(pdf_label(language, "toc"), toc_start, parent=root_outline)
        if kind == "chapter":
            chapter_title = groups[value][0]
            chapter_page = await render(build_chapter_page_html(project, chapter_title, language))
            targets[f"chapter:{value}"] = await append_pdf(chapter_page)
            chapter_outline = writer.add_outline_item(chapter_title, targets[f"chapter:{value}"], parent=root_outline)
        else:
            item_page = await append_fitted(await fitted_items[value.key])
            targets.setdefault(value.key, item_page)
            writer.add_outline_item(value.title, item_page, parent=chapter_outline)
    if toc_at == len(slots):
        toc_start = await append_pdf(toc)
        writer.add_outline_item(pdf_label(language, "toc"), toc_start, parent=root_outline)
    if toc_start is not None:
        add_internal_links(
            writer,
            toc_start,
            page_count(toc),
            TOC_LINK_PREFIX,
            internal_links(toc, TOC_LINK_PREFIX, page_width_mm, page_height_mm),
            targets,
        )

    writer.add_outline_item(
        pdf_label(language, "license"),
        await append_pdf(await render(build_license_page_html(project, selected, language))),
        parent=root_outline,
    )

    if project.conclusion:
        conclusion_page = await render(build_conclusion_page_html(project, language))
        writer.add_outline_item(
            pdf_label(language, "conclusion"),
            await append_pdf(conclusion_page),
            parent=root_outline,
        )

    if project.page_numbers:
        yield progress("stamp_page_numbers")
        await asyncio.to_thread(stamp_page_numbers, writer)

    yield progress("finalize")
    output = BytesIO()
    await asyncio.to_thread(writer.write, output)
    yield {"type": "done", "pdf": output.getvalue()}


@app.post("/api/pdf")
async def create_pdf(
    project: Project, language: str = Query(default="fr", pattern=PDF_LANGUAGE_PATTERN)
) -> Response:
    return await _create_pdf_response(project, language)


async def _create_pdf_response(project: Project, language: str) -> Response:
    selected = _selected_items(project)
    _apply_default_book_title(project, selected)
    try:
        async for event in build_book_pdf(project, selected, language):
            if event["type"] == "done":
                pdf_data = event["pdf"]
    except Exception as error:
        if isinstance(error, MediaWikiError):
            raise _mediawiki_error(error) from error
        raise HTTPException(status_code=500, detail="La génération du PDF a échoué.") from error
    return Response(
        content=pdf_data,
        media_type="application/pdf",
        headers={"Content-Disposition": _attachment_header(f"{project.book_title or project.name}.pdf")},
    )


def _attachment_header(filename: str) -> str:
    fallback = "".join(c if c.isascii() and c.isprintable() and c not in '"\\' else "_" for c in filename)
    return f"attachment; filename=\"{fallback}\"; filename*=UTF-8''{quote(filename, safe='')}"


@app.post("/api/books/generate", response_class=Response)
async def generate_book(
    payload: BookGenerationRequest, language: str = Query(default="fr", pattern=PDF_LANGUAGE_PATTERN)
) -> Response:
    articles = [add_article_reference(article) for article in payload.articles]
    options = payload.model_dump(exclude={"articles"})
    project = Project(
        name=payload.book_title or "Wikipedia2Book",
        main_articles=articles,
        **options,
    )
    return await _create_pdf_response(project, language)


@app.post("/api/books/generate-from-wikipedia-book", response_class=Response)
async def generate_book_from_wikipedia_book_endpoint(
    payload: WikipediaBookGenerationRequest,
    language: str = Query(default="fr", pattern=PDF_LANGUAGE_PATTERN),
) -> Response:
    return await _generate_book_from_wikipedia_book(
        url=payload.url,
        book_title=payload.book_title,
        book_subtitle=payload.book_subtitle,
        book_author=payload.book_author,
        book_conclusion=payload.book_conclusion,
        page_format=payload.page_format,
        orientation=payload.orientation,
        page_numbers=payload.page_numbers,
        table_of_contents=payload.table_of_contents,
        language=language,
    )


@app.get("/api/books/generate-from-wikipedia-book", response_class=Response)
async def generate_book_from_wikipedia_book_get(
    url: str = Query(min_length=1, max_length=2048),
    book_title: str | None = Query(default=None, max_length=200),
    book_subtitle: str | None = Query(default=None, max_length=300),
    book_author: str | None = Query(default=None, max_length=200),
    book_conclusion: str = Query(default=DEFAULT_BOOK_CONCLUSION, max_length=20000),
    page_format: str = Query(default="A4", pattern=r"^(A[0-6]|Letter|Legal|custom)$"),
    orientation: str = Query(default="portrait", pattern=r"^(portrait|landscape)$"),
    page_numbers: bool = True,
    table_of_contents: bool = True,
    language: str = Query(default="fr", pattern=PDF_LANGUAGE_PATTERN),
) -> Response:
    response = await _generate_book_from_wikipedia_book(
        url=url,
        book_title=book_title,
        book_subtitle=book_subtitle,
        book_author=book_author,
        book_conclusion=book_conclusion,
        page_format=page_format,
        orientation=orientation,
        page_numbers=page_numbers,
        table_of_contents=table_of_contents,
        language=language,
    )
    response.headers["Cache-Control"] = "no-store"
    return response


async def _generate_book_from_wikipedia_book(
    url: str,
    book_title: str | None,
    book_subtitle: str | None,
    book_author: str | None,
    book_conclusion: str,
    page_format: str,
    orientation: str,
    page_numbers: bool,
    table_of_contents: bool,
    language: str,
) -> Response:
    try:
        source_language, source_title = parse_article_url(url)
        book = await read_wikipedia_book(BookImportRequest(url=url))
        if book_author is None:
            async with MediaWikiClient() as client:
                _, book_author = await client.get_intro_and_creator(source_title, source_language)
    except (MediaWikiError, ValueError) as error:
        raise _mediawiki_error(error) from error
    book_title = (book_title or _book_name(source_title))[:200]
    project = Project(
        name=(book_title or "Wikipedia2Book")[:120],
        book_title=book_title,
        book_subtitle=book.subtitle if book_subtitle is None else book_subtitle,
        book_author=book_author or "",
        conclusion=book_conclusion,
        main_articles=book.articles,
        chapters=book.chapters,
        unassigned_first=book.unassigned_first,
        page_format=page_format,
        orientation=orientation,
        page_numbers=page_numbers,
        table_of_contents=table_of_contents,
    )
    return await _create_pdf_response(project, language)


def _book_name(page_title: str) -> str:
    if "/" in page_title:
        return page_title.rsplit("/", 1)[1].strip() or page_title
    return page_title.split(":", 1)[-1].strip() or page_title


@app.post("/api/pdf/stream")
async def create_pdf_stream(
    project: Project, language: str = Query(default="fr", pattern=PDF_LANGUAGE_PATTERN)
) -> StreamingResponse:
    selected = _selected_items(project)
    _apply_default_book_title(project, selected)

    async def events():
        try:
            async for event in build_book_pdf(project, selected, language):
                if event["type"] == "done":
                    event = {"type": "done", "pdf_base64": base64.b64encode(event["pdf"]).decode("ascii")}
                yield json.dumps(event, ensure_ascii=False) + "\n"
        except Exception as error:
            yield json.dumps({"type": "error", "detail": _pdf_error_detail(error)}, ensure_ascii=False) + "\n"

    return StreamingResponse(
        events(),
        media_type="application/x-ndjson",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
