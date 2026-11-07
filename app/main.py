import os
from datetime import timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Response, status
from fastapi.responses import FileResponse

from app.article_parser import extract_article_content
from app.book_builder import build_book_html
from app.explorer import discover_related_articles
from app.models import (
    Article,
    ArticleRequest,
    ExploreRequest,
    Project,
    ProjectCreate,
    ProjectUpdate,
    SelectionRequest,
    utc_now,
)
from app.pdf_generator import generate_pdf
from app.storage import JsonProjectStore
from app.wikipedia_api import MediaWikiClient, MediaWikiError, parse_article_url


app = FastAPI(title="Wikipedia2Book", version="0.1.0")
store = JsonProjectStore(os.getenv("WIKIPEDIA2BOOK_DATA_DIR", "data/projects"))
output_directory = Path(os.getenv("WIKIPEDIA2BOOK_OUTPUT_DIR", "output"))


def _get_project(project_id: str) -> Project:
    project = store.get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Projet introuvable.")
    return project


def _save(project: Project) -> Project:
    project.updated_at = utc_now()
    return store.save(project)


def _mediawiki_error(error: Exception) -> HTTPException:
    if isinstance(error, ValueError):
        return HTTPException(status_code=422, detail=str(error))
    return HTTPException(status_code=502, detail=str(error))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/projects", response_model=list[Project])
def list_projects() -> list[Project]:
    return store.list()


@app.post("/api/projects", response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate) -> Project:
    return store.save(Project(name=payload.name.strip(), description=payload.description.strip()))


@app.get("/api/projects/{project_id}", response_model=Project)
def get_project(project_id: str) -> Project:
    return _get_project(project_id)


@app.patch("/api/projects/{project_id}", response_model=Project)
def update_project(project_id: str, payload: ProjectUpdate) -> Project:
    project = _get_project(project_id)
    changes = payload.model_dump(exclude_unset=True)
    if "name" in changes:
        changes["name"] = changes["name"].strip()
    if "description" in changes:
        changes["description"] = changes["description"].strip()
    return _save(project.model_copy(update=changes))


@app.delete("/api/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: str) -> Response:
    if not store.delete(project_id):
        raise HTTPException(status_code=404, detail="Projet introuvable.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


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


@app.post("/api/projects/{project_id}/articles", response_model=Project, status_code=status.HTTP_201_CREATED)
async def add_main_article(project_id: str, payload: ArticleRequest) -> Project:
    project = _get_project(project_id)
    try:
        language, title = (
            parse_article_url(payload.url) if payload.url else (payload.language, payload.title)
        )
        async with MediaWikiClient() as client:
            article = await client.get_article(title, language)
    except (MediaWikiError, ValueError) as error:
        raise _mediawiki_error(error) from error

    if any(item.key == article.key for item in project.main_articles):
        raise HTTPException(status_code=409, detail="Cet article principal est déjà dans le projet.")
    article.selected = True
    article.content_html, article.references_html = extract_article_content(
        article.content_html, article.language
    )
    project.main_articles.append(article)
    return _save(project)


@app.delete("/api/projects/{project_id}/articles/{language}/{page_id}", response_model=Project)
def remove_article(project_id: str, language: str, page_id: int) -> Project:
    project = _get_project(project_id)
    key = f"{language}:{page_id}"
    project.main_articles = [article for article in project.main_articles if article.key != key]
    project.discovered_articles = [
        article for article in project.discovered_articles if article.key != key
    ]
    return _save(project)


@app.post("/api/projects/{project_id}/explore", response_model=Project)
async def explore_project(project_id: str, payload: ExploreRequest) -> Project:
    project = _get_project(project_id)
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
    return _save(project)


@app.put("/api/projects/{project_id}/selection", response_model=Project)
def update_selection(project_id: str, payload: SelectionRequest) -> Project:
    project = _get_project(project_id)
    selected_keys = set(payload.article_keys)
    for article in project.main_articles + project.discovered_articles:
        article.selected = article.key in selected_keys
    return _save(project)


@app.post("/api/projects/{project_id}/pdf")
async def create_pdf(project_id: str) -> FileResponse:
    project = _get_project(project_id)
    selected = [
        article
        for article in project.main_articles + project.discovered_articles
        if article.selected
    ]
    if not selected:
        raise HTTPException(status_code=400, detail="Sélectionnez au moins un article avant l’export.")

    try:
        async with MediaWikiClient() as client:
            for index, article in enumerate(selected):
                if not article.content_html:
                    fresh_article = await client.get_article(article.title, article.language)
                    article.content_html = fresh_article.content_html
                    article.summary = fresh_article.summary
                    article.url = fresh_article.url
                    article.last_modified = fresh_article.last_modified
                article.content_html, article.references_html = extract_article_content(
                    article.content_html, article.language
                )
                selected[index] = article
    except (MediaWikiError, ValueError) as error:
        raise _mediawiki_error(error) from error

    try:
        pdf_data = generate_pdf(build_book_html(project, selected))
        output_directory.mkdir(parents=True, exist_ok=True)
        pdf_path = output_directory / f"Wikipedia2Book-{project.id}.pdf"
        pdf_path.write_bytes(pdf_data)
    except Exception as error:
        raise HTTPException(status_code=500, detail="La génération du PDF a échoué.") from error
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=pdf_path.name,
    )
