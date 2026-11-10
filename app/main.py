import base64
import json
import subprocess
from io import BytesIO
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pypdf import PdfReader, PdfWriter

from app.book_builder import (
    build_chapter_page_html,
    build_conclusion_page_html,
    build_cover_html,
    PDF_LABELS,
    build_license_page_html,
    build_toc_html,
    ordered_article_groups,
    page_size_mm,
    pdf_label,
)
from app.explorer import discover_related_articles
from app.models import (
    Article,
    ArticleRequest,
    BookImportRequest,
    BookGenerationRequest,
    Project,
    ProjectExplorationRequest,
    UploadedDocument,
    WikipediaBookGenerationRequest,
    utc_now,
)
from app.pdf_generator import fit_pdf_to_format, generate_pdf, image_to_pdf, stamp_page_numbers
from app.wikipedia_api import (
    MediaWikiClient,
    MediaWikiError,
    MediaWikiPageNotFound,
    article_url,
    parse_article_url,
    validate_language,
)


app = FastAPI(title="Wikipedia2Book", version="0.20.1")
static_directory = Path(__file__).parent / "static"
PDF_LANGUAGE_PATTERN = "^(" + "|".join(PDF_LABELS) + ")$"
app.mount("/static", StaticFiles(directory=static_directory), name="static")


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
    try:
        language, title = parse_article_url(payload.url)
        async with MediaWikiClient() as client:
            titles = await client.get_book_links(title, language, limit=200)
    except (MediaWikiError, ValueError) as error:
        raise _mediawiki_error(error) from error
    if not titles:
        raise HTTPException(
            status_code=422,
            detail="Cette page de livre ne contient aucun lien vers des articles Wikipédia.",
        )
    return [
        Article(
            title=article_title,
            language=language,
            url=article_url(language, article_title),
            selected=True,
        )
        for article_title in titles
    ]


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

    def append_pdf(pdf_data: bytes) -> int:
        stream = BytesIO(fit_pdf_to_format(pdf_data, page_width_mm, page_height_mm))
        streams.append(stream)
        page_number = len(writer.pages)
        writer.append(stream)
        return page_number

    def document_pdf(document: UploadedDocument) -> bytes:
        data = base64.b64decode(document.data_base64)
        if document.kind == "pdf":
            return data
        return image_to_pdf(data, page_width_mm, page_height_mm)

    item_pdfs: dict[str, bytes] = {}
    async with MediaWikiClient() as client:
        for item in unique_items:
            if isinstance(item, Article):
                yield progress("fetch_article", title=item.title)
                item_pdfs[item.key] = await client.get_article_pdf(item.title, item.language)
            else:
                yield progress("prepare_document", title=item.title)
                item_pdfs[item.key] = document_pdf(item)

    toc_at_start = project.toc_position != "end"

    article_pages: dict[str, int] = {}
    chapter_pages: list[int | None] = [None] * len(groups)
    if project.page_numbers:
        yield progress("compute_page_numbers")
        cursor = len(PdfReader(BytesIO(generate_pdf(build_cover_html(project, language)))).pages) + 1
        if project.table_of_contents and toc_at_start:
            cursor += len(PdfReader(BytesIO(generate_pdf(build_toc_html(project, selected, language=language)))).pages)
        for index, (chapter_title, items) in enumerate(groups):
            if chapter_title:
                chapter_pages[index] = cursor
                cursor += 1
            for item in items:
                article_pages[item.key] = cursor
                cursor += len(PdfReader(BytesIO(item_pdfs[item.key])).pages)

    yield progress("cover_and_toc")
    toc = (
        generate_pdf(build_toc_html(project, selected, article_pages, chapter_pages, language))
        if project.table_of_contents
        else None
    )
    cover = generate_pdf(build_cover_html(project, language))

    yield progress("assemble")
    root_outline = writer.add_outline_item(
        project.book_title or project.name,
        append_pdf(cover),
    )
    if project.table_of_contents and toc_at_start:
        writer.add_outline_item(pdf_label(language, "toc"), append_pdf(toc), parent=root_outline)

    for chapter_title, items in groups:
        chapter_outline = root_outline
        if chapter_title:
            chapter_page = generate_pdf(build_chapter_page_html(project, chapter_title, language))
            chapter_outline = writer.add_outline_item(
                chapter_title,
                append_pdf(chapter_page),
                parent=root_outline,
            )
        for item in items:
            item_page = append_pdf(item_pdfs[item.key])
            writer.add_outline_item(item.title, item_page, parent=chapter_outline)

    if project.table_of_contents and not toc_at_start:
        writer.add_outline_item(pdf_label(language, "toc"), append_pdf(toc), parent=root_outline)

    writer.add_outline_item(
        pdf_label(language, "license"),
        append_pdf(generate_pdf(build_license_page_html(project, selected, language))),
        parent=root_outline,
    )

    if project.conclusion:
        conclusion_page = generate_pdf(build_conclusion_page_html(project, language))
        writer.add_outline_item(
            pdf_label(language, "conclusion"),
            append_pdf(conclusion_page),
            parent=root_outline,
        )

    if project.page_numbers:
        yield progress("stamp_page_numbers")
        stamp_page_numbers(writer)

    yield progress("finalize")
    output = BytesIO()
    writer.write(output)
    yield {"type": "done", "pdf": output.getvalue()}


@app.post("/api/pdf")
async def create_pdf(
    project: Project, language: str = Query(default="fr", pattern=PDF_LANGUAGE_PATTERN)
) -> Response:
    return await _create_pdf_response(project, language)


async def _create_pdf_response(project: Project, language: str) -> Response:
    selected = _selected_items(project)
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
        headers={"Content-Disposition": f'attachment; filename="{project.book_title or project.name}.pdf"'},
    )


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
    page_format: str,
    orientation: str,
    page_numbers: bool,
    table_of_contents: bool,
    language: str,
) -> Response:
    try:
        source_language, source_title = parse_article_url(url)
        articles = await import_wikipedia_book(BookImportRequest(url=url))
        if book_author is None:
            async with MediaWikiClient() as client:
                _, book_author = await client.get_intro_and_creator(source_title, source_language)
    except (MediaWikiError, ValueError) as error:
        raise _mediawiki_error(error) from error
    book_title = (book_title or source_title)[:200]
    project = Project(
        name=(book_title or "Wikipedia2Book")[:120],
        book_title=book_title,
        book_subtitle=book_subtitle or "",
        book_author=book_author or "",
        main_articles=articles,
        page_format=page_format,
        orientation=orientation,
        page_numbers=page_numbers,
        table_of_contents=table_of_contents,
    )
    return await _create_pdf_response(project, language)


@app.post("/api/pdf/stream")
async def create_pdf_stream(
    project: Project, language: str = Query(default="fr", pattern=PDF_LANGUAGE_PATTERN)
) -> StreamingResponse:
    selected = _selected_items(project)

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
