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
import contextlib
import itertools
import json
import math
import os
import re
import shutil
import subprocess
import tempfile
import time
from collections import deque
from collections.abc import Mapping
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pypdf import PdfReader

from app.book_builder import (
    build_chapter_page_html,
    build_back_cover_html,
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
    toc_block_count,
    toc_slot_index,
)
from app.explorer import discover_related_articles
from app.isolation import IsolatedProcessDied, preload, run_in_thread, run_isolated
from app.json_source import JsonSourceError, fetch_project
from app.models import (
    Article,
    ArticleRequest,
    BookChapter,
    BookImportRequest,
    BookGenerationRequest,
    Project,
    ProjectExplorationRequest,
    SourceRequest,
    Site,
    SourceResolution,
    UploadedDocument,
    WikipediaBookGenerationRequest,
    WikipediaBookImport,
    utc_now,
)
from app.pdf_generator import (
    BookAssembly,
    OutlineEntry,
    fit_pdf_to_format,
    generate_pdf,
    image_to_pdf,
    internal_links,
    merge_files,
)
from app.version import VERSION
from app.wikipedia_api import (
    MEDIA_CONCURRENCY,
    ON_TOOLFORGE,
    WIKIPEDIA_PDF_PAPERS,
    MediaWikiClient,
    MediaWikiError,
    MediaWikiPageNotFound,
    article_url,
    parse_article_url,
    validate_language,
)


PROJECT_NAMESPACES_START = 100
TOOLFORGE_DOWNLOADS = 4
DEFAULT_ARTICLE_LIMIT = 300


def deployment_settings(environ: Mapping[str, str], on_toolforge: bool) -> tuple[int | None, int]:
    limit_text = environ.get("WIKIPEDIA2BOOK_ARTICLE_LIMIT", "").strip()
    if not limit_text:
        # NE PAS supprimer cette limite par défaut, sur aucun hébergement : chaque livre télécharge tous ses articles auprès du service PDF de Wikimédia. Sa valeur (300, choix de l'utilisateur) reste sous la limite mesurée de la mémoire de Toolforge (800 à 1 000 articles avec 2 Gio, docs/testLimitetoolforge.md) ; au-delà, l'interface découpe le livre en volumes.
        article_limit = DEFAULT_ARTICLE_LIMIT
    elif limit_text.isdigit():
        article_limit = int(limit_text) or None
    else:
        raise ValueError(f"WIKIPEDIA2BOOK_ARTICLE_LIMIT doit être un entier positif, ou 0 pour ne pas limiter (reçu : {limit_text!r}).")
    # NE PAS autoriser plus de MEDIA_CONCURRENCY téléchargements hors Toolforge : la politique robots de Wikimédia l'interdit, seul Toolforge en est exempté.
    maximum = TOOLFORGE_DOWNLOADS if on_toolforge else MEDIA_CONCURRENCY
    downloads_text = environ.get("WIKIPEDIA2BOOK_DOWNLOADS", "").strip()
    if not downloads_text:
        return article_limit, maximum
    if not downloads_text.isdigit() or not 1 <= int(downloads_text) <= maximum:
        raise ValueError(f"WIKIPEDIA2BOOK_DOWNLOADS doit être compris entre 1 et {maximum} sur cet hébergement (reçu : {downloads_text!r}).")
    return article_limit, int(downloads_text)


ARTICLE_LIMIT, DOWNLOAD_CONCURRENCY = deployment_settings(os.environ, ON_TOOLFORGE)
PDF_STREAM_CHUNK = 256 * 1024

app = FastAPI(title="Wikipedia2Book", version=VERSION)
static_directory = Path(__file__).parent / "static"
PDF_LANGUAGE_PATTERN = "^(" + "|".join(PDF_LABELS) + ")$"
app.mount("/static", StaticFiles(directory=static_directory), name="static")
HOURLY_STATS_PATH = "/api/stats/hourly"
HEALTH_DETAILS_PATH = "/api/health/details"
GENERATION_LOG_PATH = "/api/health/generations"
UNCOUNTED_PATHS = {HOURLY_STATS_PATH, HEALTH_DETAILS_PATH, GENERATION_LOG_PATH}
HOURLY_KEEP = 48
hourly_hits: dict[str, int] = {}
started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
CGROUP_DIRECTORY = Path("/sys/fs/cgroup")
PROCESS_STATUS = Path("/proc/self/status")
TEMPORARY_PREFIX = "wikipedia2book-"
UNLIMITED_BYTES = 2**60
generations_in_progress = 0
GENERATION_LOG_KEEP = 50
generation_log: deque[dict] = deque(maxlen=GENERATION_LOG_KEEP)
generation_ids = itertools.count(1)
ISOLATE_ASSEMBLY = True


def _current_hour() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H")


@app.middleware("http")
async def count_hourly_hits(request: Request, call_next):
    if request.url.path not in UNCOUNTED_PATHS:
        hour = _current_hour()
        hourly_hits[hour] = hourly_hits.get(hour, 0) + 1
        while len(hourly_hits) > HOURLY_KEEP:
            del hourly_hits[min(hourly_hits)]
    return await call_next(request)


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


@app.get(HOURLY_STATS_PATH)
def hourly_stats(response: Response) -> dict:
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Cache-Control"] = "no-store"
    return {"started": started_at, "now": _current_hour(), "hours": dict(sorted(hourly_hits.items()))}


def _read_bytes(path: Path) -> int | None:
    try:
        value = path.read_text().strip()
    except OSError:
        return None
    if not value.isdigit():
        return None
    number = int(value)
    return None if number >= UNLIMITED_BYTES else number


def _process_memory() -> dict[str, int | None]:
    values: dict[str, int] = {}
    try:
        for line in PROCESS_STATUS.read_text().splitlines():
            name, _, rest = line.partition(":")
            if name in ("VmRSS", "VmHWM") and rest.split():
                values[name] = int(rest.split()[0]) * 1024
    except OSError:
        pass
    return {"process_rss_bytes": values.get("VmRSS"), "process_peak_rss_bytes": values.get("VmHWM")}


def _container_memory() -> dict[str, int | float | None]:
    if (CGROUP_DIRECTORY / "memory.current").exists():
        used = _read_bytes(CGROUP_DIRECTORY / "memory.current")
        limit = _read_bytes(CGROUP_DIRECTORY / "memory.max")
        peak = _read_bytes(CGROUP_DIRECTORY / "memory.peak")
    else:
        legacy = CGROUP_DIRECTORY / "memory"
        used = _read_bytes(legacy / "memory.usage_in_bytes")
        limit = _read_bytes(legacy / "memory.limit_in_bytes")
        peak = _read_bytes(legacy / "memory.max_usage_in_bytes")
    return {
        "used_bytes": used,
        "limit_bytes": limit,
        "peak_bytes": peak,
        "used_percent": round(used * 100 / limit, 1) if used is not None and limit else None,
        **_process_memory(),
    }


def _generation_files_bytes(directory: str) -> int:
    total = 0
    with os.scandir(directory) as entries:
        for entry in entries:
            if entry.name.startswith(TEMPORARY_PREFIX) and entry.is_dir(follow_symlinks=False):
                for root, _, files in os.walk(entry.path):
                    for name in files:
                        try:
                            total += os.path.getsize(os.path.join(root, name))
                        except OSError:
                            pass
    return total


def _temporary_space() -> dict[str, int]:
    directory = tempfile.gettempdir()
    usage = shutil.disk_usage(directory)
    return {"free_bytes": usage.free, "total_bytes": usage.total, "generation_files_bytes": _generation_files_bytes(directory)}


@app.get(HEALTH_DETAILS_PATH)
def health_details(response: Response) -> dict:
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Cache-Control"] = "no-store"
    return {
        "version": app.version,
        "started": started_at,
        "now": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generations_in_progress": generations_in_progress,
        "memory": _container_memory(),
        "temporary": _temporary_space(),
    }


@app.get(GENERATION_LOG_PATH)
def generation_journal(response: Response) -> dict:
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Cache-Control"] = "no-store"
    return {
        "version": app.version,
        "started": started_at,
        "now": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generations": list(reversed(generation_log)),
    }


@app.get("/api/version")
def version() -> dict[str, str | int | None]:
    return {**_version_details(), "article_limit": ARTICLE_LIMIT}


def _version_details() -> dict[str, str]:
    try:
        commit = subprocess.check_output(
            ["git", "log", "-1", "--format=%H|%h|%ci|%an"], text=True, stderr=subprocess.DEVNULL
        ).strip()
        full, short, date, author = commit.split("|")
        return {"version": app.version, "commit": full, "short": short, "date": date, "author": author}
    except Exception:
        full = os.environ.get("GIT_COMMIT", "")
        if full == "unknown":
            full = ""
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
    site: Site = "wikipedia",
) -> list[dict]:
    try:
        async with MediaWikiClient() as client:
            return await client.search(query, language, limit, site)
    except (MediaWikiError, ValueError) as error:
        raise _mediawiki_error(error) from error


@app.get("/api/articles/intro")
async def article_intro(
    title: str = Query(min_length=1, max_length=300),
    language: str = Query(default="fr", pattern=r"^[a-z0-9-]{2,12}$"),
    site: Site = "wikipedia",
) -> dict[str, str]:
    try:
        async with MediaWikiClient() as client:
            introduction, creator = await client.get_intro_and_creator(title, language, site)
    except (MediaWikiError, ValueError) as error:
        raise _mediawiki_error(error) from error
    return {"introduction": introduction, "author": creator}


@app.post("/api/articles", response_model=Article, status_code=201)
def add_article_reference(payload: ArticleRequest) -> Article:
    try:
        language, title, site = (
            parse_article_url(payload.url) if payload.url else (payload.language, payload.title, payload.site)
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
        site=site,
        url=payload.url or article_url(language, title, site),
        summary=payload.summary,
        selected=True,
    )


@app.post("/api/books/import", response_model=list[Article])
async def import_wikipedia_book(payload: BookImportRequest) -> list[Article]:
    return (await read_wikipedia_book(payload)).articles


@app.post("/api/books/structure", response_model=WikipediaBookImport)
async def read_wikipedia_book(payload: BookImportRequest) -> WikipediaBookImport:
    try:
        language, title = _book_page_url(payload.url)
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
        language, title, site = parse_article_url(text) if is_url else (validate_language(payload.language), text, payload.site)
        async with MediaWikiClient() as client:
            page = await client.get_page(title, language, site)
            if page is None:
                if is_url:
                    raise MediaWikiPageNotFound(f"La page « {title} » est introuvable sur {language}.{site}.org.")
                return SourceResolution(kind="search", results=await client.search(title, language, 8, site))
            title, namespace = page
            # NE PAS réduire à l'espace principal hors Wikipédia, ni se fier au marquage « contenu » de l'API : les pages d'auteur de Wikisource sont dans un espace propre au projet dont le numéro change selon la langue (102 en français, 106 en espagnol, non marqué « contenu »).
            if namespace == 0 or (site != "wikipedia" and namespace >= PROJECT_NAMESPACES_START and namespace % 2 == 0):
                return SourceResolution(
                    kind="article",
                    article=Article(
                        title=title, language=language, site=site, url=article_url(language, title, site), selected=True
                    ),
                )
            if site != "wikipedia":
                raise ValueError(f"Seules les pages de contenu de {language}.{site}.org (textes, pages d’auteur…) sont acceptées.")
            return SourceResolution(
                kind="book", book=await _wikipedia_book(client, language, title), book_title=_book_name(title)
            )
    except (MediaWikiError, ValueError) as error:
        raise _mediawiki_error(error) from error


def _book_page_url(url: str) -> tuple[str, str]:
    language, title, site = parse_article_url(url)
    if site != "wikipedia":
        raise ValueError("Les pages de livre ne sont lues que sur Wikipédia.")
    return language, title


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
    articles = sum(isinstance(item, Article) for item in selected)
    if ARTICLE_LIMIT is not None and articles > ARTICLE_LIMIT:
        raise HTTPException(status_code=413, detail={
            "code": "too_many_articles",
            "count": articles,
            "limit": ARTICLE_LIMIT,
            "message": (
                f"Ce livre compte {articles} articles : la génération est limitée à {ARTICLE_LIMIT} articles par livre, "
                "une limite volontaire pour ménager les serveurs de Wikimédia."
            ),
        })
    return selected


def _apply_default_book_title(project: Project, selected: list[Article | UploadedDocument]) -> None:
    if project.book_title.strip():
        return
    ordered = [item for _, items in ordered_article_groups(project, selected) for item in items]
    first = next((item for item in ordered if isinstance(item, Article)), ordered[0])
    project.book_title = first.title[:200]


def _pdf_error_detail(error: Exception) -> str:
    if isinstance(error, (MediaWikiError, ValueError, IsolatedProcessDied)):
        return str(error)
    return "La génération du PDF a échoué."


def _memory_snapshot() -> dict[str, int | None]:
    memory = _container_memory()
    return {
        "container_bytes": memory["used_bytes"],
        "rss_bytes": memory["process_rss_bytes"],
        "peak_rss_bytes": memory["process_peak_rss_bytes"],
    }


class GenerationRecord:
    # NE PAS y mettre de titre, d'adresse IP ni rien qui identifie l'utilisateur : le journal est public (GET /api/health/generations) et recopié dans les journaux de la plateforme.
    def __init__(self, project: Project, selected: list[Article | UploadedDocument], language: str) -> None:
        self.started = time.monotonic()
        self.data: dict = {
            "id": next(generation_ids),
            "started": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "version": VERSION,
            "language": language,
            "articles": sum(isinstance(item, Article) for item in selected),
            "documents": sum(isinstance(item, UploadedDocument) for item in selected),
            "chapters": len(project.chapters),
            "page_format": project.page_format,
            "orientation": project.orientation,
            "page_numbers": project.page_numbers,
            "table_of_contents": project.table_of_contents,
            "status": "running",
            "stages": [],
        }
        generation_log.append(self.data)
        self.stage("start", "server", _memory_snapshot())

    def _elapsed(self) -> float:
        return round(time.monotonic() - self.started, 1)

    def stage(self, name: str, process: str, memory: dict, **details) -> None:
        event = {"at_s": self._elapsed(), "stage": name, "process": process, **memory, **details}
        self.data["stages"].append(event)
        # NE PAS enlever cette écriture sur la sortie standard : quand la plateforme arrête tout le conteneur faute de mémoire, le journal en mémoire disparaît avec le serveur et seuls les journaux de la plateforme gardent la dernière étape atteinte.
        print(json.dumps({"generation": self.data["id"], **event}), flush=True)

    def finish(self, status: str, **details) -> None:
        self.data.update(status=status, duration_s=self._elapsed(), **details)
        print(json.dumps({"generation": self.data["id"], "status": status, "duration_s": self.data["duration_s"], **details}), flush=True)


async def build_book_pdf(project: Project, selected: list[Article | UploadedDocument], language: str):
    # NE PAS garder le livre en mémoire : chaque PDF va dans ce dossier temporaire, supprimé à la fin de la génération (serveur sans état), y compris quand le client abandonne.
    global generations_in_progress
    generations_in_progress += 1
    record = GenerationRecord(project, selected, language)
    status, details = "aborted", {}
    try:
        with tempfile.TemporaryDirectory(prefix=TEMPORARY_PREFIX) as workdir:
            events = _build_book_pdf(project, selected, language, Path(workdir), record)
            try:
                async for event in events:
                    if event["type"] == "done":
                        status, details = "done", {"size_bytes": event["size"]}
                    yield event
            finally:
                await events.aclose()
    except Exception as error:
        status, details = "error", {"error": str(error) if isinstance(error, IsolatedProcessDied) else type(error).__name__}
        raise
    finally:
        generations_in_progress -= 1
        record.finish(status, **details)


def _page_count(pdf_data: bytes) -> int:
    return len(PdfReader(BytesIO(pdf_data)).pages)


def _fit_to_file(pdf_data: bytes, path: Path, page_width_mm: float, page_height_mm: float) -> tuple[Path, int]:
    # NE PAS sauter fit_pdf_to_format, même pour une page déjà au bon format : c'est lui qui décide (recomposition ou simple ajustement de la taille).
    fitted = fit_pdf_to_format(pdf_data, page_width_mm, page_height_mm)
    path.write_bytes(fitted)
    return path, _page_count(fitted)


async def _build_book_pdf(
    project: Project, selected: list[Article | UploadedDocument], language: str, workdir: Path, record: "GenerationRecord"
):
    groups = ordered_article_groups(project, selected, language)
    page_width_mm, page_height_mm = page_size_mm(project)
    unique_items = list({item.key: item for _, items in groups for item in items}.values())
    total = len(unique_items) + 3 + (2 if project.page_numbers else 0)
    step = 0
    part_numbers = itertools.count()

    def progress(code: str, **params) -> dict:
        nonlocal step
        step += 1
        return {"type": "progress", "step": step, "total": total, "code": code, **params}

    def fit_to_file(pdf_data: bytes) -> tuple[Path, int]:
        return _fit_to_file(pdf_data, workdir / f"part-{next(part_numbers)}.pdf", page_width_mm, page_height_mm)

    def document_pdf(document: UploadedDocument) -> bytes:
        data = base64.b64decode(document.data_base64)
        if document.kind == "pdf":
            return data
        return image_to_pdf(data, page_width_mm, page_height_mm)

    fitted_items: dict[str, asyncio.Future[tuple[Path, int]]] = {}
    paper = WIKIPEDIA_PDF_PAPERS.get(project.page_format, "a4")
    started: asyncio.Queue[dict] = asyncio.Queue()
    # NE PAS dépasser DOWNLOAD_CONCURRENCY : hors Toolforge, la politique robots de Wikimédia est respectée avec 2 téléchargements simultanés (MediaWikiClient l'impose aussi pour tout le serveur) ; sur Toolforge, exempté, 4 par livre.
    slots_free = asyncio.Semaphore(DOWNLOAD_CONCURRENCY)

    async def load(client: MediaWikiClient, item: Article | UploadedDocument) -> None:
        async with slots_free:
            if isinstance(item, Article):
                await started.put(progress("fetch_article", title=item.title))
                data = await client.get_article_pdf(item.title, item.language, paper, item.site)
            else:
                await started.put(progress("prepare_document", title=item.title))
                data = await asyncio.to_thread(document_pdf, item)
            # NE PAS appeler pypdf directement ici : un calcul bloquant gèle le serveur et retarde l'envoi des messages de progression.
            fitted_items[item.key] = asyncio.ensure_future(asyncio.to_thread(fit_to_file, data))
            # NE PAS libérer le créneau avant la fin de la recomposition : sur un serveur au processeur limité (Toolforge), les PDF bruts téléchargés s'accumuleraient en mémoire en attendant d'être recomposés.
            await fitted_items[item.key]

    async with MediaWikiClient() as client:
        client.on_wait = lambda seconds: started.put_nowait({"type": "wait", "seconds": math.ceil(seconds)})
        downloads = [asyncio.ensure_future(load(client, item)) for item in unique_items]
        try:
            pending = set(downloads)
            while pending or not started.empty():
                if not started.empty():
                    yield started.get_nowait()
                    continue
                waiter = asyncio.ensure_future(started.get())
                finished, _ = await asyncio.wait(pending | {waiter}, return_when=asyncio.FIRST_COMPLETED)
                if waiter in finished:
                    yield waiter.result()
                else:
                    waiter.cancel()
                for task in sorted(finished - {waiter}, key=downloads.index):
                    pending.discard(task)
                    task.result()
        except BaseException:
            for task in downloads:
                task.cancel()
            for task in fitted_items.values():
                task.cancel()
            raise

    fitted = {key: task.result() for key, task in fitted_items.items()}
    record.stage("downloads_done", "server", _memory_snapshot(), article_pages=sum(count for _, count in fitted.values()))
    if ISOLATE_ASSEMBLY:
        preload(["app.main"])
    # NE PAS faire la suite dans le processus du serveur : les rendus WeasyPrint et l'assemblage y prennent plusieurs centaines de Mo que l'allocateur ne rend pas au système après la génération (relevé de /api/health/details sur Toolforge) ; un processus séparé rend tout en se terminant.
    runner = run_isolated if ISOLATE_ASSEMBLY else run_in_thread
    # NE PAS enlever aclosing : sans lui, un client qui abandonne laisse tourner le processus d'assemblage jusqu'au ramasse-miettes, pendant que son dossier temporaire est supprimé.
    async with contextlib.aclosing(runner(_finish_book, project, selected, language, workdir, fitted)) as messages:
        async for kind, value in messages:
            if kind == "result":
                output, size = value
                yield {"type": "done", "path": output, "size": size}
            elif "progress" in value:
                yield progress(value["progress"])
            else:
                record.stage(value["stage"], "assembly", value["memory"], server_rss_bytes=_memory_snapshot()["rss_bytes"], **value["details"])


def _finish_book(
    project: Project,
    selected: list[Article | UploadedDocument],
    language: str,
    workdir: Path,
    fitted: dict[str, tuple[Path, int]],
    report,
) -> tuple[Path, int]:
    groups = ordered_article_groups(project, selected, language)
    page_width_mm, page_height_mm = page_size_mm(project)
    page_numbers = itertools.count()

    def step(code: str) -> None:
        report({"progress": code})

    def stage(name: str, **details) -> None:
        report({"stage": name, "memory": _memory_snapshot(), "details": details})

    def render(html: str) -> bytes:
        return generate_pdf(html)

    def place_file(pdf_data: bytes) -> tuple[Path, int]:
        return _fit_to_file(pdf_data, workdir / f"page-{next(page_numbers)}.pdf", page_width_mm, page_height_mm)

    stage("assembly_start")
    slots = book_slots(groups)
    toc_at = toc_slot_index(project, groups, slots)
    toc_blocks = toc_block_count(project, selected, language)

    article_pages: dict[str, int] = {}
    chapter_pages: list[int | None] = [None] * len(groups)
    cover: bytes | None = None
    if project.page_numbers:
        step("compute_page_numbers")
        cover = render(build_cover_html(project, language))
        stage("render_cover")
        cursor = _page_count(cover) + 1
        toc_pages = 0
        if toc_at is not None and toc_at < len(slots):
            for block in range(toc_blocks):
                toc_pages += _page_count(render(build_toc_html(project, selected, language=language, block=block)))
            stage("render_toc_count", blocks=toc_blocks, pages=toc_pages)
        for index, (kind, value) in enumerate(slots):
            if index == toc_at:
                cursor += toc_pages
            if kind == "chapter":
                chapter_pages[value] = cursor
                cursor += 1
            else:
                article_pages[value.key] = cursor
                cursor += fitted[value.key][1]

    step("cover_and_toc")
    toc: list[bytes] = []
    if toc_at is not None:
        toc = [
            render(build_toc_html(project, selected, article_pages, chapter_pages, language, block))
            for block in range(toc_blocks)
        ]
        stage("render_toc", blocks=toc_blocks)
    if cover is None:
        cover = render(build_cover_html(project, language))
        stage("render_cover")

    step("assemble")
    parts: list[Path] = []
    pages_so_far = 0

    def place(path: Path, count: int) -> int:
        nonlocal pages_so_far
        parts.append(path)
        pages_so_far += count
        return pages_so_far - count

    def place_pdf(pdf_data: bytes) -> int:
        return place(*place_file(pdf_data))

    toc_placed: list[tuple[int, bytes]] = []

    def place_toc() -> int:
        toc_placed.extend((place_pdf(block), block) for block in toc)
        return toc_placed[0][0]

    root = OutlineEntry(project.book_title or project.name, place_pdf(cover))
    chapter_entry = root
    targets: dict[str, int] = {}
    chapters = 0
    for index, (kind, value) in enumerate(slots):
        if index == toc_at:
            root.children.append(OutlineEntry(pdf_label(language, "toc"), place_toc()))
        if kind == "chapter":
            chapter_title = groups[value][0]
            targets[f"chapter:{value}"] = place_pdf(render(build_chapter_page_html(project, chapter_title, language)))
            chapter_entry = OutlineEntry(chapter_title, targets[f"chapter:{value}"])
            root.children.append(chapter_entry)
            chapters += 1
        else:
            item_page = place(*fitted[value.key])
            targets.setdefault(value.key, item_page)
            chapter_entry.children.append(OutlineEntry(value.title, item_page))
    stage("render_chapters", chapters=chapters)
    if toc_at == len(slots):
        root.children.append(OutlineEntry(pdf_label(language, "toc"), place_toc()))
    if project.conclusion:
        root.children.append(OutlineEntry(
            pdf_label(language, "conclusion"),
            place_pdf(render(build_conclusion_page_html(project, language))),
        ))
        stage("render_conclusion")
    # NE PAS remettre la conclusion après la licence : le logo et les liens suivent la licence et terminent le texte du livre, seule l'image de fond de dernière page vient après.
    license_start = place_pdf(render(build_license_page_html(project, selected, language)))
    root.children.append(OutlineEntry(pdf_label(language, "license"), license_start))
    stage("render_license")
    if project.back_image:
        place_pdf(render(build_back_cover_html(project)))
        stage("render_back_cover")

    merge_files(parts, workdir / "merged.pdf")
    stage("merge_parts", parts=len(parts), pages=pages_so_far)
    assembly = BookAssembly(workdir / "merged.pdf")
    try:
        stage("merge_reopen")
        assembly.add_outline([root])
        for start, block in toc_placed:
            assembly.link_toc(
                start,
                _page_count(block),
                TOC_LINK_PREFIX,
                internal_links(block, TOC_LINK_PREFIX, page_width_mm, page_height_mm),
                targets,
            )
        stage("outline_and_links")
        if project.page_numbers:
            step("stamp_page_numbers")
            assembly.stamp_page_numbers()
            stage("stamp_page_numbers")
        step("finalize")
        output = workdir / "book.pdf"
        size = assembly.save(output)
        stage("save", size_bytes=size)
        return output, size
    finally:
        assembly.close()


async def _pdf_chunks(path: Path):
    with path.open("rb") as pdf:
        while chunk := await asyncio.to_thread(pdf.read, PDF_STREAM_CHUNK):
            yield chunk


@app.post("/api/pdf")
async def create_pdf(
    project: Project, language: str = Query(default="fr", pattern=PDF_LANGUAGE_PATTERN)
) -> Response:
    return await _create_pdf_response(project, language)


@app.get("/api/pdf/from-json")
async def create_pdf_from_json(
    url: str = Query(min_length=1, max_length=2048),
    language: str = Query(default="fr", pattern=PDF_LANGUAGE_PATTERN),
) -> Response:
    try:
        project = await fetch_project(url)
    except JsonSourceError as error:
        raise HTTPException(status_code=error.status_code, detail=str(error)) from error
    return await _create_pdf_response(project, language)


async def _create_pdf_response(project: Project, language: str) -> Response:
    selected = _selected_items(project)
    _apply_default_book_title(project, selected)
    events = build_book_pdf(project, selected, language)
    try:
        async for event in events:
            if event["type"] == "done":
                done = event
                break
    except Exception as error:
        await events.aclose()
        if isinstance(error, MediaWikiError):
            raise _mediawiki_error(error) from error
        raise HTTPException(status_code=500, detail="La génération du PDF a échoué.") from error

    async def body():
        try:
            async for chunk in _pdf_chunks(done["path"]):
                yield chunk
        finally:
            await events.aclose()

    return StreamingResponse(
        body(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": _attachment_header(f"{project.book_title or project.name}.pdf"),
            "Content-Length": str(done["size"]),
        },
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
    book_conclusion: str = Query(default="", max_length=20000),
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
        source_language, source_title = _book_page_url(url)
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
        book = build_book_pdf(project, selected, language)
        try:
            async for event in book:
                if event["type"] == "done":
                    yield json.dumps({"type": "done", "size": event["size"]}) + "\n"
                    async for chunk in _pdf_chunks(event["path"]):
                        yield chunk
                    return
                yield json.dumps(event, ensure_ascii=False) + "\n"
        except Exception as error:
            yield json.dumps({"type": "error", "detail": _pdf_error_detail(error)}, ensure_ascii=False) + "\n"
        finally:
            await book.aclose()

    return StreamingResponse(
        events(),
        media_type="application/x-ndjson",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
