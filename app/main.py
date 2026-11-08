from io import BytesIO
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pypdf import PdfWriter

from app.book_builder import (
    build_book_html,
    build_chapter_page_html,
    build_conclusion_page_html,
    ordered_article_groups,
)
from app.explorer import discover_related_articles
from app.models import (
    Article,
    ArticleRequest,
    BookImportRequest,
    Project,
    ProjectExplorationRequest,
    utc_now,
)
from app.pdf_generator import generate_pdf
from app.wikipedia_api import (
    MediaWikiClient,
    MediaWikiError,
    MediaWikiPageNotFound,
    article_url,
    parse_article_url,
    validate_language,
)


app = FastAPI(title="Wikipedia2Book", version="0.1.0")
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
    selected = [
        article
        for article in project.main_articles + project.discovered_articles
        if article.selected
    ]
    if not selected:
        raise HTTPException(status_code=400, detail="Sélectionnez au moins un article avant l’export.")

    try:
        groups = ordered_article_groups(project, selected)
        writer = PdfWriter()
        streams: list[BytesIO] = []

        def append_pdf(pdf_data: bytes) -> int:
            stream = BytesIO(pdf_data)
            streams.append(stream)
            page_number = len(writer.pages)
            writer.append(stream)
            return page_number

        front_matter = generate_pdf(
            build_book_html(
                project,
                selected,
                include_articles=False,
                include_conclusion=False,
            )
        )
        root_outline = writer.add_outline_item(
            project.book_title or project.name,
            append_pdf(front_matter),
        )

        async with MediaWikiClient() as client:
            for chapter_title, articles in groups:
                chapter_outline = root_outline
                if chapter_title:
                    chapter_page = generate_pdf(build_chapter_page_html(project, chapter_title))
                    chapter_outline = writer.add_outline_item(
                        chapter_title,
                        append_pdf(chapter_page),
                        parent=root_outline,
                    )
                for article in articles:
                    article_pdf = await client.get_article_pdf(article.title, article.language)
                    article_page = append_pdf(article_pdf)
                    writer.add_outline_item(article.title, article_page, parent=chapter_outline)

        if project.conclusion:
            conclusion_page = generate_pdf(build_conclusion_page_html(project))
            writer.add_outline_item(
                "Conclusion",
                append_pdf(conclusion_page),
                parent=root_outline,
            )

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
        headers={"Content-Disposition": f'attachment; filename="Wikipedia2Book-{project.id}.pdf"'},
    )
