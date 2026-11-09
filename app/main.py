import base64
import subprocess
from io import BytesIO
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pypdf import PdfReader, PdfWriter

from app.book_builder import (
    build_book_html,
    build_chapter_page_html,
    build_conclusion_page_html,
    ordered_article_groups,
    page_size_mm,
)
from app.explorer import discover_related_articles
from app.models import (
    Article,
    ArticleRequest,
    BookImportRequest,
    Project,
    ProjectExplorationRequest,
    UploadedDocument,
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


app = FastAPI(title="Wikipedia2Book", version="0.8.0")
static_directory = Path(__file__).parent / "static"
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
        full = (os.environ.get("GIT_COMMIT")
                or os.environ.get("RAILWAY_GIT_COMMIT_SHA")
                or "unknown")
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


@app.post("/api/pdf")
async def create_pdf(project: Project) -> Response:
    selected: list[Article | UploadedDocument] = [
        item
        for item in project.main_articles + project.discovered_articles + project.uploaded_documents
        if item.selected
    ]
    if not selected:
        raise HTTPException(status_code=400, detail="Sélectionnez au moins un article avant l’export.")

    try:
        groups = ordered_article_groups(project, selected)
        writer = PdfWriter()
        streams: list[BytesIO] = []
        page_width_mm, page_height_mm = page_size_mm(project)

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
            for _, items in groups:
                for item in items:
                    if item.key in item_pdfs:
                        continue
                    item_pdfs[item.key] = (
                        await client.get_article_pdf(item.title, item.language)
                        if isinstance(item, Article)
                        else document_pdf(item)
                    )

        article_pages: dict[str, int] = {}
        chapter_pages: list[int | None] = [None] * len(groups)
        if project.page_numbers:
            front_pages = len(PdfReader(BytesIO(generate_pdf(build_book_html(project, selected)))).pages)
            cursor = front_pages + 1
            for index, (chapter_title, items) in enumerate(groups):
                if chapter_title:
                    chapter_pages[index] = cursor
                    cursor += 1
                for item in items:
                    article_pages[item.key] = cursor
                    cursor += len(PdfReader(BytesIO(item_pdfs[item.key])).pages)

        front_matter = generate_pdf(build_book_html(project, selected, article_pages, chapter_pages))
        root_outline = writer.add_outline_item(
            project.book_title or project.name,
            append_pdf(front_matter),
        )

        for chapter_title, items in groups:
            chapter_outline = root_outline
            if chapter_title:
                chapter_page = generate_pdf(build_chapter_page_html(project, chapter_title))
                chapter_outline = writer.add_outline_item(
                    chapter_title,
                    append_pdf(chapter_page),
                    parent=root_outline,
                )
            for item in items:
                item_page = append_pdf(item_pdfs[item.key])
                writer.add_outline_item(item.title, item_page, parent=chapter_outline)

        if project.conclusion:
            conclusion_page = generate_pdf(build_conclusion_page_html(project))
            writer.add_outline_item(
                "Conclusion",
                append_pdf(conclusion_page),
                parent=root_outline,
            )

        if project.page_numbers:
            stamp_page_numbers(writer)

        output = BytesIO()
        writer.write(output)
        pdf_data = output.getvalue()
    except Exception as error:
        if isinstance(error, MediaWikiError):
            raise _mediawiki_error(error) from error
        raise HTTPException(status_code=500, detail="La génération du PDF a échoué.") from error
    return Response(
        content=pdf_data,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{project.book_title or project.name}.pdf"'},
    )
