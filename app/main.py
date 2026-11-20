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
import hashlib
import importlib.metadata
import itertools
import json
import math
import os
import platform
import queue
import re
import secrets
import shutil
import socket
import subprocess
import tempfile
import threading
import time
from collections import deque
from collections.abc import Mapping
from datetime import datetime, timedelta, timezone
from io import BytesIO
from pathlib import Path
from urllib.parse import quote, urlsplit

from typing import Any

from fastapi import Body, FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.datastructures import Headers
from starlette.staticfiles import NotModifiedResponse
from pypdf import PdfReader

from app.book_builder import (
    build_chapter_page_html,
    build_back_cover_html,
    has_back_cover,
    build_conclusion_page_html,
    build_cover_html,
    fit_background,
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
from app.admin import (
    ADMIN_PATH,
    SESSION_COOKIE,
    SESSION_S,
    STATE_COOKIE,
    STATE_S,
    OAuthError,
    admin_settings,
    authorize_url,
    monitor_token_setting,
    require_admin,
    require_monitor,
    session_cookie,
    session_user,
    state_cookie,
    state_matches,
    wikimedia_username,
)
from app.explorer import discover_related_articles
from app.isolation import WORKER_PROCESSES, IsolatedProcessDied, preload, run_in_thread, run_in_worker, run_isolated
from app.resource_gate import Reservation, ResourceGate, release_memory
from app.request_limits import Alerts, ClosingStreamingResponse, GenerationLimits, LimitRefused, RequestGuard, client_keys, count_setting
from app import wikipedia_api
from app.json_source import JsonSourceError, download, fetch_project, project_from_payload
from app.html_document import HTML_PAGE_BYTES, HTML_TYPES, html_for_print
from app.volumes import book_volumes, volume_project
from app.models import (
    Article,
    ArticleRequest,
    BookChapter,
    BookImage,
    BookImportRequest,
    BookGenerationRequest,
    BookWikitextRequest,
    Project,
    ProjectExplorationRequest,
    SourceRequest,
    Site,
    SourceResolution,
    UploadedDocument,
    VolumePlan,
    VolumeSummary,
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
    SUBPAGE_BOOK_MIN,
    SUBPAGE_BOOK_SITES,
    WIKIPEDIA_PDF_PAPERS,
    WIKIMEDIA_HOST,
    MediaWikiClient,
    article_pdf_url,
    MediaWikiError,
    MediaWikiPageNotFound,
    WikipediaBook,
    FULL_TEXT_PAGES,
    article_url,
    book_wikitext_title,
    is_book_listing,
    is_printable_wikitext,
    parse_article_url,
    parse_book_wikitext,
    parse_printable_wikitext,
    printable_wikitext_title,
    validate_language,
    wikimedia_file_page,
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
MEGABYTE = 1_000_000
# NE PAS baisser ces estimations sans nouvelles mesures : recomposition d'un article environ 25 fois la taille de son PDF (6 Mo pour 0,2 Mo, 281 Mo pour 13,4 Mo), assemblage 92 Mo au départ puis environ 2,3 fois la taille des articles (+58 Mo pour 25,6 Mo, 253 pages), réduction d'une image de fond environ 35 fois sa taille (5,2 Mo de JPEG), mesurés le 2026-11-17 ; trop basses, elles laissent repasser la mémoire au-dessus de la limite.
DOWNLOAD_RESERVE_BYTES = 10 * MEGABYTE
# NE PAS descendre sous la taille d'un gros PDF recomposé (le fichier écrit dans le dossier temporaire fait environ 1,1 fois le PDF téléchargé, jusqu'à une vingtaine de Mo pour les plus gros articles) : sa taille n'est pas connue avant le téléchargement.
DOWNLOAD_DISK_BYTES = 30 * MEGABYTE
ASSEMBLY_DISK_BASE_BYTES = 50 * MEGABYTE
GENERATION_BASE_BYTES = 25 * MEGABYTE
INLINE_FACTOR = 3
# NE PAS descendre sous deux fois la taille des articles : merge_files écrit le fichier fusionné pendant que les parties existent encore, puis BookAssembly écrit le livre final à côté du fichier fusionné.
ASSEMBLY_DISK_FACTOR = 2
FIT_BASE_BYTES = 5 * MEGABYTE
FIT_FACTOR = 25
ASSEMBLY_BASE_BYTES = 100 * MEGABYTE
ASSEMBLY_FACTOR = 2.5
BACKGROUND_FACTOR = 35


def ratio_setting(environ: Mapping[str, str], name: str, default: float = 0.95) -> float:
    text = environ.get(name, "").strip()
    if not text:
        return default
    try:
        ratio = float(text)
    except ValueError:
        ratio = -1.0
    if not 0 <= ratio <= 1:
        raise ValueError(f"{name} doit être compris entre 0 (pas de contrôle) et 1 (reçu : {text!r}).")
    return ratio


def fit_reserve(size: int) -> int:
    return FIT_BASE_BYTES + FIT_FACTOR * size


def assembly_reserve(article_bytes: int, background_bytes: int) -> int:
    return int(ASSEMBLY_BASE_BYTES + ASSEMBLY_FACTOR * article_bytes + BACKGROUND_FACTOR * background_bytes)


def generation_reserve(project: Project, selected: list) -> int:
    inline = sum(len(item.data_base64 or "") for item in selected if isinstance(item, UploadedDocument))
    remote_images = 0
    for image in (project.cover_image, project.back_image):
        if image is not None:
            inline += len(image.data_base64 or "")
            remote_images += image.url is not None
    return GENERATION_BASE_BYTES + INLINE_FACTOR * inline + remote_images * REMOTE_FILE_BYTES


def assembly_disk_reserve(article_bytes: int) -> int:
    return ASSEMBLY_DISK_BASE_BYTES + ASSEMBLY_DISK_FACTOR * article_bytes


def busy_event(waited_s: float) -> dict:
    return {"type": "busy", "seconds": math.floor(waited_s)}
REMOTE_FILE_BYTES = 15 * 1024 * 1024
BACKGROUND_TYPES = {"image/png", "image/jpeg", "image/gif", "image/webp", "image/svg+xml"}
DOCUMENT_TYPES = {"image/png", "image/jpeg", "image/gif", "image/webp", "application/pdf"}


class RemoteFileError(ValueError):
    pass


async def fetch_remote_file(url: str, accepted: set[str], label: str) -> tuple[bytes, str]:
    file_page = wikimedia_file_page(url)
    if file_page is not None:
        try:
            async with MediaWikiClient() as client:
                url = await client.get_file_url(*file_page)
        except MediaWikiError as error:
            raise RemoteFileError(f"{label[0].upper()}{label[1:]} n’a pas pu être trouvé ({error}) : {url}") from error
    try:
        data, content_type = await download(url, REMOTE_FILE_BYTES, label)
    except JsonSourceError as error:
        advice = " Téléchargez le fichier depuis votre navigateur, puis importez-le." if error.refused else ""
        raise RemoteFileError(f"{error}{advice}") from error
    if content_type not in accepted:
        raise RemoteFileError(f"{label[0].upper()}{label[1:]} n’est pas d’un type accepté ({content_type or 'type inconnu'}) : {url}")
    return data, content_type
PDF_STREAM_CHUNK = 256 * 1024
SECURITY_HEADERS = {
    "Content-Security-Policy": "default-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'",
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
}

app = FastAPI(title="Wikipedia2Book", version=VERSION)
static_directory = Path(__file__).parent / "static"
PDF_LANGUAGE_PATTERN = "^(" + "|".join(PDF_LABELS) + ")$"


def _content_etag(path: str) -> str:
    return '"' + hashlib.sha256(Path(path).read_bytes()).hexdigest()[:32] + '"'


class ContentStaticFiles(StaticFiles):
    # NE PAS revenir à l'empreinte de Starlette (date et taille) ni remettre Last-Modified : sur Toolforge, tous les fichiers sont datés de 1980, un navigateur qui revalide par la date reçoit 304 à chaque version et garde un ancien i18n.js.
    def file_response(self, full_path, stat_result, scope, status_code: int = 200) -> Response:
        etag = _content_etag(str(full_path))
        response = FileResponse(full_path, status_code=status_code, stat_result=stat_result, headers={"etag": etag})
        del response.headers["last-modified"]
        if self.is_not_modified(response.headers, Headers(scope=scope)):
            return NotModifiedResponse(response.headers)
        return response


app.mount("/static", ContentStaticFiles(directory=static_directory), name="static")
HOURLY_STATS_PATH = "/api/stats/hourly"
HEALTH_DETAILS_PATH = "/api/health/details"
GENERATION_LOG_PATH = "/api/health/generations"
UNCOUNTED_PATHS = {HOURLY_STATS_PATH, HEALTH_DETAILS_PATH, GENERATION_LOG_PATH}
HOURLY_KEEP = 48
hourly_hits: dict[str, int] = {}
started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
started_monotonic = time.monotonic()
CGROUP_DIRECTORY = Path("/sys/fs/cgroup")
PROCESS_STATUS = Path("/proc/self/status")
TEMPORARY_PREFIX = "wikipedia2book-"
UNLIMITED_BYTES = 2**60
generations_in_progress = 0
GENERATION_LOG_KEEP = 1000
# NE PAS relever ce plafond sans mesure : une étape du journal prend environ 760 octets en mémoire (mesuré le 2026-11-17), 40 000 étapes environ 30 Mo ; un livre de 300 articles en compte environ 330.
GENERATION_LOG_STAGES = 40_000
generation_log: deque[dict] = deque()
generation_ids = itertools.count(1)
GENERATION_FILES_DAYS = 30
GENERATION_FILE_NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})\.jsonl$")
GENERATION_REQUEST_MAX_BYTES = 1_000_000
# NE PAS relever ce plafond sans mesure : les demandes sont gardées en mémoire, à côté du journal, jusqu'à ce total.
GENERATION_REQUESTS_BYTES = 30_000_000
generation_requests: dict[int, bytes] = {}
REFUSED_URLS_KEEP = 500
refused_urls: dict[str, dict] = {}
ISOLATE_ASSEMBLY = True


def _current_hour() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H")


@app.middleware("http")
async def count_hourly_hits(request: Request, call_next):
    if request.url.path not in UNCOUNTED_PATHS and not request.url.path.startswith((GENERATION_LOG_PATH + "/", ADMIN_PATH + "/api/")):
        hour = _current_hour()
        hourly_hits[hour] = hourly_hits.get(hour, 0) + 1
        while len(hourly_hits) > HOURLY_KEEP:
            del hourly_hits[min(hourly_hits)]
    return await call_next(request)


@app.middleware("http")
async def revalidate_web_app_files(request: Request, call_next):
    response = await call_next(request)
    if request.url.path in ("/", ADMIN_PATH, ADMIN_PATH + "/generation") or request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-cache"
    if request.url.path == ADMIN_PATH or request.url.path.startswith((ADMIN_PATH + "/", "/api/health/")):
        response.headers.update(SECURITY_HEADERS)
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


def _container_used_and_limit() -> tuple[int | None, int | None]:
    memory = _container_memory()
    return memory["used_bytes"], memory["limit_bytes"]


def _container_limit_only() -> tuple[int | None, int | None]:
    return 0, _container_memory()["limit_bytes"]


def _disk_used_and_total() -> tuple[int | None, int | None]:
    usage = shutil.disk_usage(tempfile.gettempdir())
    return usage.used, usage.total


MEMORY_GATE = ResourceGate(_container_used_and_limit, ratio_setting(os.environ, "WIKIPEDIA2BOOK_MEMORY_RATIO"))
DISK_GATE = ResourceGate(_disk_used_and_total, ratio_setting(os.environ, "WIKIPEDIA2BOOK_DISK_RATIO"))
# NE PAS faire passer les générations par MEMORY_GATE : une génération admise garde sa réserve jusqu'à la fin ; dans le même contrôle que ses étapes, elle les bloquerait toutes, sans fin. Ce budget à part ne compte que les réserves des générations admises.
GENERATION_GATE = ResourceGate(_container_limit_only, ratio_setting(os.environ, "WIKIPEDIA2BOOK_GENERATIONS_RATIO", 0.5))
# NE PAS limiter par adresse IP sur Toolforge : son proxy masque les visiteurs, tous arrivent avec la même adresse privée ; d'où la limite globale (50 générations simultanées, 200 par minute), en plus du jeton du navigateur.
GENERATION_LIMITS = GenerationLimits(
    count_setting(os.environ, "WIKIPEDIA2BOOK_CLIENT_GENERATIONS", 5),
    count_setting(os.environ, "WIKIPEDIA2BOOK_CLIENT_PER_MINUTE", 20),
    count_setting(os.environ, "WIKIPEDIA2BOOK_TOTAL_GENERATIONS", 50 if ON_TOOLFORGE else 0),
    count_setting(os.environ, "WIKIPEDIA2BOOK_TOTAL_PER_MINUTE", 200 if ON_TOOLFORGE else 0),
)
WAITING_GENERATIONS = count_setting(os.environ, "WIKIPEDIA2BOOK_WAITING_GENERATIONS", 100)
CLIENT_IP_HEADER = os.environ.get("WIKIPEDIA2BOOK_CLIENT_IP_HEADER", "").strip().lower()
ALERTS = Alerts()
app.add_middleware(
    RequestGuard,
    limits=lambda: GENERATION_LIMITS,
    waiting=lambda: len(GENERATION_GATE.queue),
    max_waiting=lambda: WAITING_GENERATIONS,
    alerts=lambda: ALERTS,
    ip_header=lambda: CLIENT_IP_HEADER,
)
wikipedia_api.on_api_throttle = lambda waited: ALERTS.raise_alert("wikimedia_api_throttle", waited_s=round(waited, 1))


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


@app.get(HEALTH_DETAILS_PATH, include_in_schema=False)
def health_details(request: Request, response: Response) -> dict:
    require_monitor(request, MONITOR_TOKEN)
    response.headers["Cache-Control"] = "no-store"
    return _health_payload()


def _health_payload() -> dict:
    return {
        "version": app.version,
        "started": started_at,
        "now": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generations_in_progress": generations_in_progress,
        "memory": _container_memory(),
        "memory_gate": MEMORY_GATE.state(),
        "disk_gate": DISK_GATE.state(),
        "generation_gate": GENERATION_GATE.state(),
        "request_limits": {**GENERATION_LIMITS.state(), "waiting_limit": WAITING_GENERATIONS},
        "alerts": ALERTS.state(),
        "temporary": _temporary_space(),
    }


@app.get(GENERATION_LOG_PATH, include_in_schema=False)
def generation_journal(request: Request, response: Response) -> dict:
    require_monitor(request, MONITOR_TOKEN)
    response.headers["Cache-Control"] = "no-store"
    return {
        "version": app.version,
        "started": started_at,
        "now": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generations": list(reversed(generation_log)),
    }


@app.get(GENERATION_LOG_PATH + "/{generation_id}", include_in_schema=False)
def generation_journal_entry(generation_id: int, request: Request, response: Response) -> dict:
    require_monitor(request, MONITOR_TOKEN)
    response.headers["Cache-Control"] = "no-store"
    return _generation_entry(generation_id)


def _generation_request(generation_id: int) -> Response:
    data = generation_requests.get(generation_id)
    if data is None:
        raise HTTPException(status_code=404, detail=f"La demande de la génération {generation_id} n’est plus en mémoire (trop grosse, trop ancienne ou effacée au redémarrage).")
    return Response(content=data, media_type="application/json", headers={"Cache-Control": "no-store", "Content-Disposition": f'attachment; filename="wikipedia2book-request-{generation_id}.json"'})


@app.get(GENERATION_LOG_PATH + "/{generation_id}/request", include_in_schema=False)
def generation_journal_request(generation_id: int, request: Request) -> Response:
    require_monitor(request, MONITOR_TOKEN)
    return _generation_request(generation_id)


def _generation_entry(generation_id: int) -> dict:
    for generation in generation_log:
        if generation["id"] == generation_id:
            return {"version": app.version, "started": started_at, "generation": generation}
    raise HTTPException(status_code=404, detail=f"La génération {generation_id} n’est plus dans le journal (50 dernières générations, effacé au redémarrage).")


ADMIN = admin_settings(os.environ)
MONITOR_TOKEN = monitor_token_setting(os.environ)
# NE PAS desserrer ces limites ni les retirer : /admin/login et /admin/callback ne demandent aucune identification, et chaque retour fait deux requêtes vers Meta-Wiki.
ADMIN_LOGIN_LIMITS = GenerationLimits(0, 10, 0, 30)


def _secure_cookies() -> bool:
    return ADMIN.callback.startswith("https://")


@app.get("/admin", include_in_schema=False)
def admin_page() -> FileResponse:
    return FileResponse(static_directory / "admin.html", media_type="text/html")


@app.get("/admin/generation", include_in_schema=False)
def admin_generation_page() -> FileResponse:
    return FileResponse(static_directory / "admin-generation.html", media_type="text/html")


def _login_refused(request: Request) -> Response | None:
    try:
        ADMIN_LOGIN_LIMITS.admit(client_keys((request.client or (None,))[0], {name.lower(): value for name, value in request.headers.items()}, CLIENT_IP_HEADER)).release()
    except LimitRefused as refusal:
        ALERTS.raise_alert(f"admin_{refusal.reason}", path=request.url.path, limit=refusal.limit)
        return RedirectResponse("/admin?error=too_many", status_code=302)
    return None


@app.get("/admin/login", include_in_schema=False)
def admin_login(request: Request) -> Response:
    refused = _login_refused(request)
    if refused is not None:
        return refused
    if not ADMIN.configured:
        return RedirectResponse("/admin?error=not_configured", status_code=302)
    state = secrets.token_urlsafe(24)
    response = RedirectResponse(authorize_url(ADMIN, state), status_code=302)
    response.set_cookie(STATE_COOKIE, state_cookie(state), max_age=STATE_S, httponly=True, secure=_secure_cookies(), samesite="lax", path=ADMIN_PATH)
    return response


@app.get("/admin/callback", include_in_schema=False)
async def admin_callback(request: Request, code: str = Query(default="", max_length=2048), state: str = Query(default="", max_length=256), error: str = Query(default="", max_length=256)) -> Response:
    refused = _login_refused(request)
    if refused is not None:
        return refused
    if error or not code:
        return RedirectResponse("/admin?error=denied", status_code=302)
    if not state_matches(request.cookies.get(STATE_COOKIE), state):
        return RedirectResponse("/admin?error=state", status_code=302)
    try:
        user = await wikimedia_username(ADMIN, code)
    except OAuthError as failure:
        print(json.dumps({"admin_login_failed": str(failure)}, ensure_ascii=False), flush=True)
        return RedirectResponse("/admin?error=oauth", status_code=302)
    if user not in ADMIN.admins:
        return RedirectResponse("/admin?error=forbidden", status_code=302)
    response = RedirectResponse("/admin", status_code=302)
    response.delete_cookie(STATE_COOKIE, path=ADMIN_PATH)
    # NE PAS élargir le chemin du cookie : limité à /admin, il n'est jamais envoyé au reste de l'application.
    response.set_cookie(SESSION_COOKIE, session_cookie(user), max_age=SESSION_S, httponly=True, secure=_secure_cookies(), samesite="lax", path=ADMIN_PATH)
    return response


@app.get("/admin/logout", include_in_schema=False)
def admin_logout() -> Response:
    response = RedirectResponse("/admin", status_code=302)
    response.delete_cookie(SESSION_COOKIE, path=ADMIN_PATH)
    return response


@app.get(ADMIN_PATH + "/api/session", include_in_schema=False)
def admin_session(request: Request, response: Response) -> dict:
    response.headers["Cache-Control"] = "no-store"
    return {"configured": ADMIN.configured, "user": session_user(request, ADMIN)}


LIBRARIES = ("fastapi", "starlette", "uvicorn", "pydantic", "httpx", "weasyprint", "pypdf", "pymupdf", "pillow", "reportlab")
PROCESS_FD_DIRECTORY = Path("/proc/self/fd")


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text().strip()
    except OSError:
        return None


def _cgroup_cpu_limit() -> float | None:
    text = _read_text(CGROUP_DIRECTORY / "cpu.max")
    parts = (text or "").split()
    if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit() or int(parts[1]) == 0:
        return None
    return round(int(parts[0]) / int(parts[1]), 2)


def _cgroup_counters(name: str) -> dict[str, int]:
    counters = {}
    for line in (_read_text(CGROUP_DIRECTORY / name) or "").splitlines():
        key, _, value = line.partition(" ")
        if value.strip().isdigit():
            counters[key] = int(value)
    return counters


def _process_threads() -> int | None:
    for line in (_read_text(PROCESS_STATUS) or "").splitlines():
        name, _, value = line.partition(":")
        if name == "Threads" and value.strip().isdigit():
            return int(value)
    return None


def _open_files() -> int | None:
    try:
        return len(os.listdir(PROCESS_FD_DIRECTORY))
    except OSError:
        return None


def _library_versions() -> dict[str, str | None]:
    versions = {}
    for name in LIBRARIES:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    return versions


def system_info() -> dict:
    load = os.getloadavg() if hasattr(os, "getloadavg") else None
    times = os.times()
    pids_max = _read_text(CGROUP_DIRECTORY / "pids.max")
    return {
        "host": socket.gethostname(),
        "platform": "toolforge" if ON_TOOLFORGE else "container",
        "os": platform.platform(),
        "python": platform.python_version(),
        "pid": os.getpid(),
        "uptime_s": round(time.monotonic() - started_monotonic),
        "cpu_count": os.cpu_count(),
        "cpu_limit": _cgroup_cpu_limit(),
        "load_average": [round(value, 2) for value in load] if load else None,
        "process_cpu_s": round(times.user + times.system, 1),
        "threads": _process_threads(),
        "open_files": _open_files(),
        "processes": _read_bytes(CGROUP_DIRECTORY / "pids.current"),
        "processes_limit": int(pids_max) if pids_max and pids_max.isdigit() else None,
        "oom_kills": _cgroup_counters("memory.events").get("oom_kill"),
        "worker_processes": WORKER_PROCESSES,
        "isolate_assembly": ISOLATE_ASSEMBLY,
        "libraries": _library_versions(),
    }


def _percentile(values: list[float], share: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return ordered[max(0, math.ceil(share * len(ordered)) - 1)]


def _generation_row(generation: dict) -> dict:
    stages = generation.get("stages", [])
    return {
        "id": generation["id"],
        "started": generation["started"],
        "version": generation.get("version"),
        "status": generation["status"],
        "duration_s": generation.get("duration_s"),
        "articles": generation.get("articles", 0),
        "documents": generation.get("documents", 0),
        "page_format": generation.get("page_format"),
        "size_bytes": generation.get("size_bytes"),
        "waited_s": round(sum(stage.get("waited_s", 0) for stage in stages if stage.get("stage") == "memory_wait"), 1),
        "peak_rss_bytes": max((stage.get("peak_rss_bytes") or 0 for stage in stages), default=0) or None,
        "error": generation.get("error"),
    }


def admin_summary_payload(user: str) -> dict:
    rows = [_generation_row(generation) for generation in reversed(generation_log)]
    done = [row for row in rows if row["status"] == "done" and row["duration_s"] is not None]
    durations = [row["duration_s"] for row in done]
    statuses: dict[str, int] = {}
    for row in rows:
        statuses[row["status"]] = statuses.get(row["status"], 0) + 1
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).strftime("%Y-%m-%dT%H")
    hours = dict(sorted(hourly_hits.items()))
    median = _percentile(durations, 0.5)
    return {
        "user": user,
        "version": _version_details(),
        "server": _health_payload(),
        "system": system_info(),
        "settings": {
            "on_toolforge": ON_TOOLFORGE,
            "article_limit": ARTICLE_LIMIT,
            "downloads": DOWNLOAD_CONCURRENCY,
            "memory_ratio": MEMORY_GATE.ratio,
            "disk_ratio": DISK_GATE.ratio,
            "generations_ratio": GENERATION_GATE.ratio,
        },
        "usage": {
            "hours": hours,
            "hits_24h": sum(count for hour, count in hours.items() if hour > since),
            "hits_48h": sum(hours.values()),
            "generations": statuses,
            "articles": sum(row["articles"] for row in rows),
            "documents": sum(row["documents"] for row in rows),
        },
        "performance": {
            "generations": len(done),
            "median_s": median,
            "p90_s": _percentile(durations, 0.9),
            "max_s": max(durations, default=None),
            "median_s_per_article": _percentile([row["duration_s"] / row["articles"] for row in done if row["articles"]], 0.5),
            "median_size_bytes": _percentile([row["size_bytes"] for row in done if row["size_bytes"]], 0.5),
            "max_peak_rss_bytes": max((row["peak_rss_bytes"] or 0 for row in rows), default=0) or None,
            "waited_s": round(sum(row["waited_s"] for row in rows), 1),
        },
        "recent": rows,
        "refused_urls": list(reversed(refused_urls.values())),
    }


@app.get(ADMIN_PATH + "/api/summary", include_in_schema=False)
def admin_summary(request: Request, response: Response) -> dict:
    user = require_admin(request, ADMIN)
    response.headers["Cache-Control"] = "no-store"
    return admin_summary_payload(user)


@app.get(ADMIN_PATH + "/api/generations/{generation_id}", include_in_schema=False)
def admin_generation(generation_id: int, request: Request, response: Response) -> dict:
    require_admin(request, ADMIN)
    response.headers["Cache-Control"] = "no-store"
    return _generation_entry(generation_id)


@app.get(ADMIN_PATH + "/api/generations/{generation_id}/request", include_in_schema=False)
def admin_generation_request(generation_id: int, request: Request) -> Response:
    require_admin(request, ADMIN)
    return _generation_request(generation_id)


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


ALL_LANGUAGES = "all"
# NE PAS élargir à toutes les Wikipédias : plus de 300 langues, autant de requêtes vers Wikimédia pour une seule recherche ; même liste que le sélecteur #articleLanguage de l'interface.
SEARCH_LANGUAGES = ("fr", "en", "de", "es", "it", "pt", "nl")
MAX_SEARCH_LANGUAGES = 12
RESOLVE_SEARCH_LIMIT = 5


def search_languages(languages: list[str]) -> list[str]:
    chosen = list(dict.fromkeys(validate_language(language) for language in languages if language and language != ALL_LANGUAGES))
    if len(chosen) > MAX_SEARCH_LANGUAGES:
        raise ValueError(f"La recherche dans toutes les langues accepte {MAX_SEARCH_LANGUAGES} langues au plus.")
    return chosen or list(SEARCH_LANGUAGES)


async def search_all_languages(client: MediaWikiClient, query: str, languages: list[str], limit: int, site: Site) -> list[dict]:
    answers = await asyncio.gather(*(client.search(query, language, limit, site) for language in languages), return_exceptions=True)
    failures = [answer for answer in answers if isinstance(answer, Exception)]
    if len(failures) == len(answers):
        raise failures[0]
    for failure in failures:
        if not isinstance(failure, (MediaWikiError, ValueError)):
            raise failure
    return [item for answer in answers if not isinstance(answer, Exception) for item in answer]


@app.get("/api/search")
async def search_articles(
    query: str = Query(min_length=2, max_length=200),
    language: str = Query(default="fr", pattern=r"^[a-z0-9-]{2,12}$"),
    limit: int = Query(default=10, ge=1, le=20),
    site: Site = "wikipedia",
    languages: str = Query(default="", max_length=200),
) -> list[dict]:
    try:
        async with MediaWikiClient() as client:
            if language == ALL_LANGUAGES:
                return await search_all_languages(client, query, search_languages(languages.split(",")), limit, site)
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
        refusal = _mediawiki_error(error)
        note_refused_url(payload.url or "", refusal)
        raise refusal from error
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
        refusal = _mediawiki_error(error)
        note_refused_url(payload.url, refusal)
        raise refusal from error


@app.post("/api/books/from-wikitext", response_model=SourceResolution)
async def read_book_wikitext(payload: BookWikitextRequest) -> SourceResolution:
    try:
        language = validate_language(payload.language)
    except ValueError as error:
        raise _mediawiki_error(error) from error
    if is_printable_wikitext(payload.wikitext):
        book = parse_printable_wikitext(payload.wikitext)
        if not book.chapters:
            raise HTTPException(status_code=422, detail="Ce texte ne contient aucune page incluse {{:…}} d’un livre de Wikilivres.")
        return SourceResolution(kind="book", book=_book_import(book, language, "wikibooks"), book_title=printable_wikitext_title(payload.wikitext))
    book = parse_book_wikitext(payload.wikitext, limit=200)
    if not book.chapters:
        raise HTTPException(status_code=422, detail="Ce texte ne contient aucun lien [[…]] vers un article Wikipédia.")
    return SourceResolution(kind="book", book=_book_import(book, language, "wikipedia"), book_title=book_wikitext_title(payload.wikitext))


@app.post("/api/sources/resolve", response_model=SourceResolution)
async def resolve_source(payload: SourceRequest) -> SourceResolution:
    try:
        async with MediaWikiClient() as client:
            return await _resolve_source(client, payload.input, payload.language, payload.site, payload.languages)
    except (MediaWikiError, ValueError) as error:
        refusal = _mediawiki_error(error)
        note_refused_url(payload.input, refusal)
        raise refusal from error


async def _resolve_source(client: MediaWikiClient, text: str, default_language: str, default_site: Site, languages: list[str] = ()) -> SourceResolution:
    text = text.strip()
    if not text:
        raise ValueError("Saisissez une URL, une page de livre ou un titre Wikipédia.")
    is_url = bool(re.match(r"^[a-z]+://", text, re.IGNORECASE))
    if not is_url and default_language == ALL_LANGUAGES:
        return SourceResolution(kind="search", results=await search_all_languages(client, text, search_languages(list(languages)), RESOLVE_SEARCH_LIMIT, default_site))
    language, title, site = parse_article_url(text) if is_url else (validate_language(default_language), text, default_site)
    page = await client.get_page(title, language, site)
    if page is None:
        if is_url:
            raise MediaWikiPageNotFound(f"La page « {title} » est introuvable sur {language}.{site}.org.")
        return SourceResolution(kind="search", results=await client.search(title, language, 8, site))
    title, namespace = page
    # NE PAS réduire à l'espace principal hors Wikipédia, ni se fier au marquage « contenu » de l'API : les pages d'auteur de Wikisource sont dans un espace propre au projet dont le numéro change selon la langue (102 en français, 106 en espagnol, non marqué « contenu »).
    if namespace == 0 or (site != "wikipedia" and namespace >= PROJECT_NAMESPACES_START and namespace % 2 == 0):
        article = Article(title=title, language=language, site=site, url=article_url(language, title, site), selected=True)
        if site == "wikibooks" and namespace == 0 and "/" in title and title.rsplit("/", 1)[1].casefold() in FULL_TEXT_PAGES:
            printable = await _printable_version(client, title, language)
            if printable is not None:
                return printable
        if site in SUBPAGE_BOOK_SITES and namespace == 0:
            subpage_book = await client.get_subpage_book(title, language, site)
            if sum(len(pages) for _, pages in subpage_book.chapters) >= SUBPAGE_BOOK_MIN:
                return SourceResolution(
                    kind="subpages", article=article, book=_book_import(subpage_book, language, site), book_title=_book_name(title)
                )
        return SourceResolution(kind="article", article=article)
    if site != "wikipedia":
        content = await client.get_wikitext(title, language, site) or ""
        book = parse_book_wikitext(content, limit=200) if is_book_listing(content) else None
        if book is None or not book.chapters:
            raise ValueError(f"Seules les pages de contenu de {language}.{site}.org (textes, pages d’auteur…) et les compilations ou pages de livre sont acceptées.")
        return SourceResolution(kind="book", book=_book_import(book, language, site), book_title=_book_name(title))
    return SourceResolution(kind="book", book=await _wikipedia_book(client, language, title), book_title=_book_name(title))


async def _printable_version(client: MediaWikiClient, title: str, language: str) -> SourceResolution | None:
    summary_title = title.rsplit("/", 1)[0]
    content = await client.get_wikitext(title, language, "wikibooks") or ""
    if is_printable_wikitext(content):
        book = parse_printable_wikitext(content)
        if book.chapters:
            printable = Article(title=title, language=language, site="wikibooks", url=article_url(language, title, "wikibooks"), selected=True)
            return SourceResolution(
                kind="book", article=printable, book=_book_import(book, language, "wikibooks"), book_title=printable_wikitext_title(content) or _book_name(summary_title)
            )
    summary = Article(title=summary_title, language=language, site="wikibooks", url=article_url(language, summary_title, "wikibooks"), selected=True)
    subpage_book = await client.get_subpage_book(summary_title, language, "wikibooks")
    if sum(len(pages) for _, pages in subpage_book.chapters) >= SUBPAGE_BOOK_MIN:
        return SourceResolution(kind="subpages", article=summary, book=_book_import(subpage_book, language, "wikibooks"), book_title=_book_name(summary_title))
    return None


INTERWIKI_SITES = {"w": "wikipedia", "s": "wikisource", "b": "wikibooks", "voy": "wikivoyage", "v": "wikiversity", "q": "wikiquote", "wikt": "wiktionary", "n": "wikinews"}
MAX_URL_SOURCES = 50


# NE PAS modifier sans aligner parseSourceLine et INTERWIKI_SITES dans app.js : une ligne du champ Sources et un paramètre source= doivent désigner la même page.
def parse_source_line(line: str, default_language: str) -> tuple[str, str, Site] | None:
    text = re.sub(r"^(?:\d+[.)]|[#*•\-–]+)\s*", "", line.strip()).strip()
    if not text:
        return None
    markdown = re.match(r"^\[[^\]]*\]\((.+)\)$", text)
    if markdown:
        return markdown.group(1).strip(), default_language, "wikipedia"
    wikilink = re.match(r"^\[\[\s*:?([^\]|]+?)\s*(?:\|[^\]]*)?\]\]", text)
    if wikilink:
        text = wikilink.group(1)
    if re.match(r"^[a-z]+://", text, re.IGNORECASE):
        return text, default_language, "wikipedia"
    language, site = None, None
    while prefixed := re.match(r"^([a-z][a-z-]*):(.+)$", text):
        if site is None and prefixed.group(1) in INTERWIKI_SITES:
            site = INTERWIKI_SITES[prefixed.group(1)]
        elif language is None and re.fullmatch(r"[a-z]{2,3}(?:-[a-z]{2,8})?", prefixed.group(1)):
            language = prefixed.group(1)
        else:
            break
        text = prefixed.group(2).strip()
    return text, language or default_language, site or "wikipedia"


async def project_from_sources(sources: list[str], wiki_language: str, with_summary: bool) -> Project:
    articles: list[Article] = []
    chapters: list[BookChapter] = []
    names: list[str] = []
    subtitle = ""
    async with MediaWikiClient() as client:
        for line in sources:
            parsed = parse_source_line(line, wiki_language)
            if parsed is None:
                continue
            resolved = await _resolve_source(client, *parsed)
            if resolved.kind == "search":
                raise MediaWikiPageNotFound(f"Aucune page ne correspond exactement à « {line.strip()} ».")
            if resolved.kind == "article":
                articles.append(resolved.article)
                continue
            if resolved.kind == "subpages" and with_summary:
                articles.append(resolved.article)
            articles.extend(resolved.book.articles)
            chapters.extend(resolved.book.chapters)
            names.append(resolved.book_title)
            subtitle = subtitle or resolved.book.subtitle
    unique = list({article.key: article for article in articles}.values())
    if not unique:
        raise ValueError("Aucune page à mettre dans le livre.")
    in_chapters = {key for chapter in chapters for key in chapter.article_keys}
    name = names[0] if len(names) == 1 else ""
    return Project(
        name=(name or unique[0].title)[:120],
        book_title=name[:200],
        book_subtitle=subtitle[:300],
        main_articles=unique,
        chapters=chapters,
        unassigned_first=bool(chapters) and unique[0].key not in in_chapters,
    )


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
    return _book_import(book, language, "wikipedia")


def _book_import(book: WikipediaBook, language: str, site: Site) -> WikipediaBookImport:
    articles: list[Article] = []
    chapters: list[BookChapter] = []
    for chapter_title, titles in book.chapters:
        chapter_articles = [
            Article(title=article_title, language=language, site=site, url=article_url(language, article_title, site), selected=True)
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
            "volumes": len(book_volumes(project, ARTICLE_LIMIT)),
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


def _trim_generation_log() -> None:
    stages = sum(len(entry["stages"]) for entry in generation_log)
    while len(generation_log) > 1 and (len(generation_log) > GENERATION_LOG_KEEP or stages > GENERATION_LOG_STAGES):
        removed = generation_log.popleft()
        stages -= len(removed["stages"])
        generation_requests.pop(removed["id"], None)
    kept = sum(len(data) for data in generation_requests.values())
    for generation_id in list(generation_requests)[:-1]:
        if kept <= GENERATION_REQUESTS_BYTES:
            break
        kept -= len(generation_requests.pop(generation_id))


def _without_file_contents(value):
    if isinstance(value, dict):
        copy = {key: _without_file_contents(item) for key, item in value.items()}
        if isinstance(value.get("data_base64"), str):
            copy["data_base64"] = None
            copy["removed_base64_chars"] = len(value["data_base64"])
        return copy
    if isinstance(value, list):
        return [_without_file_contents(item) for item in value]
    return value


def _store_request(generation_id: int, project: Project) -> int:
    workspace = {"format": "wikipedia2book-workspace", "version": 1, "projects": [_without_file_contents(project.model_dump(mode="json"))]}
    data = json.dumps(workspace, ensure_ascii=False).encode("utf-8")
    if len(data) <= GENERATION_REQUEST_MAX_BYTES:
        generation_requests[generation_id] = data
    return len(data)


def note_refused_url(url: str, error: HTTPException) -> None:
    # NE PAS y ajouter l'adresse IP, le jeton du navigateur ni rien d'autre que l'adresse refusée : tableau en mémoire seulement, lu par la page d'admin (choix de l'utilisateur).
    url = url.strip()[:500]
    if error.status_code >= 500 or not re.match(r"^[a-z]+://", url, re.IGNORECASE):
        return
    detail = error.detail.get("message", "") if isinstance(error.detail, dict) else str(error.detail)
    entry = refused_urls.pop(url, {"url": url, "count": 0})
    entry.update(count=entry["count"] + 1, last=datetime.now(timezone.utc).isoformat(timespec="seconds"), status=error.status_code, reason=detail[:300])
    refused_urls[url] = entry
    while len(refused_urls) > REFUSED_URLS_KEEP:
        refused_urls.pop(next(iter(refused_urls)))


class GenerationFiles:
    # NE PAS écrire dans le fil de la requête : sur Toolforge le dossier est sur NFS, et une écriture bloquée gèlerait tout le serveur.
    def __init__(self, directory: str, days: int = GENERATION_FILES_DAYS) -> None:
        self.directory = Path(directory) if directory else None
        self.days = days
        self.pod = socket.gethostname()
        self.lines: queue.SimpleQueue = queue.SimpleQueue()
        self.writer: threading.Thread | None = None
        self.day: str | None = None
        self.failed = False

    def write(self, event: dict) -> None:
        if not self.directory:
            return
        now = datetime.now(timezone.utc)
        self.lines.put((now, json.dumps({"at": now.isoformat(timespec="seconds"), "pod": self.pod, **event})))
        if self.writer is None:
            self.writer = threading.Thread(target=self._run, name="generation-files", daemon=True)
            self.writer.start()

    def _run(self) -> None:
        while True:
            self.append(*self.lines.get())

    def append(self, now: datetime, line: str) -> None:
        day = now.date().isoformat()
        try:
            # NE PAS créer les dossiers parents : sans le montage NFS, le fichier irait sur le disque éphémère du conteneur sans que personne le sache.
            self.directory.mkdir(exist_ok=True)
            if day != self.day:
                self.purge(now)
                self.day = day
            with (self.directory / f"{day}.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(line + "\n")
            self.failed = False
        except OSError as error:
            if not self.failed:
                print(json.dumps({"generation_files_error": f"{type(error).__name__}: {error}", "directory": str(self.directory)}), flush=True)
            self.failed = True

    def purge(self, now: datetime) -> None:
        oldest = (now - timedelta(days=self.days - 1)).date().isoformat()
        for path in self.directory.iterdir():
            match = GENERATION_FILE_NAME.match(path.name)
            if match and match.group(1) < oldest:
                path.unlink(missing_ok=True)


generation_files = GenerationFiles(os.environ.get("WIKIPEDIA2BOOK_GENERATION_LOG_DIR", "").strip())


class GenerationRecord:
    # NE PAS y mettre de titre, d'adresse IP ni rien qui identifie l'utilisateur, hors des adresses téléchargées (paramètre url de stage, jamais recopié sur la sortie standard) : le journal est lu par la supervision et la page d'admin (GET /api/health/generations) et recopié dans les journaux de la plateforme.
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
        self.data["request_bytes"] = _store_request(self.data["id"], project)
        generation_log.append(self.data)
        _trim_generation_log()
        self.stage("start", "server", _memory_snapshot())

    def _elapsed(self) -> float:
        return round(time.monotonic() - self.started, 1)

    def stage(self, name: str, process: str, memory: dict, url: str | None = None, **details) -> None:
        event = {"at_s": self._elapsed(), "stage": name, "process": process, **memory, **details}
        # NE PAS écrire l'adresse sur la sortie standard : elle contient le titre de l'article ou l'adresse d'un fichier de l'utilisateur ; elle ne reste que dans le journal en mémoire, lu par la page d'admin et le jeton de supervision (choix de l'utilisateur).
        self.data["stages"].append({**event, "url": url} if url else event)
        # NE PAS enlever cette écriture sur la sortie standard : quand la plateforme arrête tout le conteneur faute de mémoire, le journal en mémoire disparaît avec le serveur et seuls les journaux de la plateforme gardent la dernière étape atteinte.
        line = {"generation": self.data["id"], **event}
        print(json.dumps(line), flush=True)
        generation_files.write(line)

    def finish(self, status: str, **details) -> None:
        _trim_generation_log()
        self.data.update(status=status, duration_s=self._elapsed(), **details)
        line = {"generation": self.data["id"], "status": status, "duration_s": self.data["duration_s"], **details}
        print(json.dumps(line), flush=True)
        generation_files.write(line)


async def build_book_pdf(project: Project, selected: list[Article | UploadedDocument], language: str):
    # NE PAS garder le livre en mémoire : chaque PDF va dans ce dossier temporaire, supprimé à la fin de la génération (serveur sans état), y compris quand le client abandonne.
    global generations_in_progress
    generations_in_progress += 1
    record = GenerationRecord(project, selected, language)
    status, details = "aborted", {}
    admitted: Reservation | None = None
    try:
        # NE PAS charger les images ni télécharger quoi que ce soit avant cette admission : à 100 générations simultanées, les données gardées par chacune hors des étapes contrôlées faisaient déborder le serveur (section 13.12).
        async for admission in _admitted(GENERATION_GATE, generation_reserve(project, selected)):
            if isinstance(admission, Reservation):
                admitted = admission
            else:
                yield admission
        if admitted.waited_s >= 1:
            record.stage("memory_wait", "server", _memory_snapshot(), reason="generation", waited_s=round(admitted.waited_s, 1), reserved_bytes=admitted.amount)
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
        if admitted is not None:
            admitted.release()
        generations_in_progress -= 1
        record.finish(status, **details)
        release_memory()


async def _admitted(gate: ResourceGate, amount: int):
    notices: asyncio.Queue[dict] = asyncio.Queue()
    task = asyncio.ensure_future(gate.acquire(amount, lambda waited: notices.put_nowait(busy_event(waited))))
    try:
        while not task.done():
            getter = asyncio.ensure_future(notices.get())
            finished, _ = await asyncio.wait({task, getter}, return_when=asyncio.FIRST_COMPLETED)
            if getter in finished:
                yield getter.result()
            else:
                getter.cancel()
    except BaseException:
        task.cancel()
        if task.done() and not task.cancelled() and task.exception() is None:
            task.result().release()
        raise
    yield task.result()


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
    remote_images = [field for field in ("cover_image", "back_image") if getattr(project, field) and getattr(project, field).url]
    # NE PAS retirer le + 1 : la dernière étape, le téléchargement du PDF, est affichée par le navigateur (showPdfDownload).
    total = len(unique_items) + len(remote_images) + 4 + (2 if project.page_numbers else 0)
    step = 0
    part_numbers = itertools.count()

    def progress(code: str, **params) -> dict:
        nonlocal step
        step += 1
        return {"type": "progress", "step": step, "total": total, "code": code, **params}

    def note_wait(reservation: Reservation, reason: str) -> None:
        if reservation.waited_s >= 1:
            record.stage("memory_wait", "server", _memory_snapshot(), reason=reason, waited_s=round(reservation.waited_s, 1), reserved_bytes=reservation.amount)

    async def fit_part(pdf_data: bytes) -> tuple[Path, int]:
        path = workdir / f"part-{next(part_numbers)}.pdf"
        if not ISOLATE_ASSEMBLY:
            return await asyncio.to_thread(_fit_to_file, pdf_data, path, page_width_mm, page_height_mm)
        preload(["app.main"])
        # NE PAS recomposer dans le processus du serveur : pypdf y prend environ 25 fois la taille du PDF, que l'allocateur ne rend pas ; un processus de travail recyclé après chaque article rend tout en se terminant.
        return await run_in_worker(_fit_to_file, pdf_data, path, page_width_mm, page_height_mm)

    async def document_data(document: UploadedDocument) -> tuple[bytes, str]:
        if document.url is None:
            return base64.b64decode(document.data_base64), document.kind
        started_at = time.monotonic()
        if document.kind == "html":
            data, kind = await html_page(document), "html"
        else:
            data, content_type = await fetch_remote_file(document.url, DOCUMENT_TYPES, f"le document « {document.title} »")
            kind = "pdf" if content_type == "application/pdf" else "image"
        record.stage("fetch_document", "server", _memory_snapshot(), url=document.url, duration_s=round(time.monotonic() - started_at, 2), size_bytes=len(data), pdf=kind == "pdf", html=kind == "html")
        return data, kind

    async def html_page(document: UploadedDocument) -> bytes:
        label = f"la page web « {document.title} »"
        # NE PAS télécharger une page Wikimédia par ce chemin : tout appel à Wikimédia passe par MediaWikiClient (User-Agent, limites de la politique robots) ; ces pages s'ajoutent par le champ Sources.
        if WIKIMEDIA_HOST.match(urlsplit(document.url).hostname or ""):
            raise RemoteFileError(f"{label[0].upper()}{label[1:]} est une page Wikimédia : ajoutez-la par le champ Sources, qui reprend son PDF officiel : {document.url}")
        try:
            page, content_type = await download(document.url, HTML_PAGE_BYTES, label)
        except JsonSourceError as error:
            advice = " Ouvrez la page dans votre navigateur, enregistrez-la en PDF (Imprimer, puis Enregistrer au format PDF) et importez ce fichier à l’étape Organisation." if error.refused else ""
            raise RemoteFileError(f"{error}{advice}") from error
        if content_type not in HTML_TYPES:
            raise RemoteFileError(f"{label[0].upper()}{label[1:]} n’est pas une page HTML ({content_type or 'type inconnu'}) : {document.url}")
        html = await html_for_print(page, document.url, lambda address, size, what: download(address, size, what), page_width_mm, page_height_mm)
        return html.encode("utf-8")

    async def document_pdf(data: bytes, kind: str) -> bytes:
        if kind == "image":
            return await asyncio.to_thread(image_to_pdf, data, page_width_mm, page_height_mm)
        if kind == "html":
            if not ISOLATE_ASSEMBLY:
                return await asyncio.to_thread(generate_pdf, data.decode("utf-8"))
            preload(["app.main"])
            # NE PAS rendre une page web dans le processus du serveur : une page lourde y prendrait beaucoup de mémoire, que l'allocateur ne rend pas.
            return await run_in_worker(generate_pdf, data.decode("utf-8"))
        return data

    # NE PAS garder les images de fond en mémoire ni dans le livre transmis à l'assemblage : chaque génération en garderait deux copies (octets et base64) pendant toute sa durée. Elles vont dans le dossier temporaire, supprimé à la fin de la génération ; une image donnée par son adresse est retéléchargée à chaque génération, seule l'adresse est enregistrée dans le JSON.
    background_files: dict[str, tuple[Path, str, str]] = {}
    for field in ("cover_image", "back_image"):
        image = getattr(project, field)
        if image is None:
            continue
        if image.url is None:
            data, content_type = base64.b64decode(image.data_base64), image.mime_type
        else:
            yield progress("fetch_image", title=image.title or image.url)
            async for admission in _admitted(MEMORY_GATE, DOWNLOAD_RESERVE_BYTES):
                if isinstance(admission, Reservation):
                    reservation = admission
                else:
                    yield admission
            note_wait(reservation, "fetch_image")
            started_at = time.monotonic()
            try:
                data, content_type = await fetch_remote_file(image.url, BACKGROUND_TYPES, f"l’image « {image.title or image.url} »")
            finally:
                reservation.release()
            record.stage("fetch_image", "server", _memory_snapshot(), url=image.url, image=field, duration_s=round(time.monotonic() - started_at, 2), size_bytes=len(data))
        path = workdir / f"{field}.image"
        path.write_bytes(data)
        background_files[field] = (path, content_type, image.title)
        del data
    project = project.model_copy(update={field: None for field in background_files})

    fitted_items: dict[str, asyncio.Future[tuple[Path, int]]] = {}
    missing: set[str] = set()
    paper = WIKIPEDIA_PDF_PAPERS.get(project.page_format, "a4")
    started: asyncio.Queue[dict] = asyncio.Queue()
    # NE PAS dépasser DOWNLOAD_CONCURRENCY : hors Toolforge, la politique robots de Wikimédia est respectée avec 2 téléchargements simultanés (MediaWikiClient l'impose aussi pour tout le serveur) ; sur Toolforge, exempté, 4 par livre.
    slots_free = asyncio.Semaphore(DOWNLOAD_CONCURRENCY)

    def announce_busy(waited: float) -> None:
        started.put_nowait(busy_event(waited))

    async def load(client: MediaWikiClient, item: Article | UploadedDocument) -> None:
        # NE PAS rendre la réserve de disque avant l'écriture du fichier recomposé : tant qu'il n'est pas écrit, la place qu'il prendra n'apparaît pas dans l'espace utilisé du disque.
        async with slots_free, DISK_GATE.reserve(DOWNLOAD_DISK_BYTES, announce_busy) as disk:
            note_wait(disk, "disk")
            async with MEMORY_GATE.reserve(DOWNLOAD_RESERVE_BYTES, announce_busy) as reservation:
                note_wait(reservation, "download")
                fetch_started = time.monotonic()
                if isinstance(item, Article):
                    await started.put(progress("fetch_article", title=item.title))
                    url = article_pdf_url(item.title, item.language, paper, item.site)
                    try:
                        data = await client.get_article_pdf(item.title, item.language, paper, item.site)
                    except MediaWikiPageNotFound:
                        missing.add(item.key)
                        await started.put({"type": "missing", "title": item.title, "url": article_url(item.language, item.title, item.site)})
                        record.stage("missing_article", "server", _memory_snapshot(), url=url)
                        return
                    kind = "pdf"
                else:
                    await started.put(progress("prepare_document", title=item.title))
                    url = item.url
                    data, kind = await document_data(item)
                download_s, size = round(time.monotonic() - fetch_started, 2), len(data)
            async with MEMORY_GATE.reserve(fit_reserve(len(data)), announce_busy) as reservation:
                note_wait(reservation, "fit")
                data = await document_pdf(data, kind)
                # NE PAS appeler pypdf directement ici : un calcul bloquant gèle le serveur et retarde l'envoi des messages de progression.
                fitted_items[item.key] = asyncio.ensure_future(fit_part(data))
                # NE PAS libérer le créneau avant la fin de la recomposition : sur un serveur au processeur limité (Toolforge), les PDF bruts téléchargés s'accumuleraient en mémoire en attendant d'être recomposés.
                # NE PAS attendre la recomposition sans shield : annuler ce téléchargement l'annulerait aussi, et la suppression du dossier temporaire n'attendrait plus son fil d'exécution.
                fit_started = time.monotonic()
                _, pages = await asyncio.shield(fitted_items[item.key])
            record.stage("download", "server", _memory_snapshot(), url=url, kind="article" if isinstance(item, Article) else "document", download_s=download_s, fit_s=round(time.monotonic() - fit_started, 2), size_bytes=size, pages=pages)
            data = None
            release_memory()

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
            # NE PAS annuler les recompositions en cours : annuler ne stoppe pas leur fil d'exécution, qui écrirait encore dans le dossier temporaire pendant sa suppression (échec « répertoire non vide » sous Windows).
            await asyncio.gather(*fitted_items.values(), return_exceptions=True)
            raise

    fitted = {key: task.result() for key, task in fitted_items.items()}
    # NE PAS arrêter la génération pour une page supprimée de Wikipédia (404) : le livre se fait sans elle, le navigateur la signale (événement missing).
    selected = [item for item in selected if item.key not in missing]
    if not selected:
        raise MediaWikiPageNotFound("Aucune page du livre n’existe sur Wikipédia : le PDF ne peut pas être généré.")
    record.stage("downloads_done", "server", _memory_snapshot(), article_pages=sum(count for _, count in fitted.values()))
    if ISOLATE_ASSEMBLY:
        preload(["app.main"])
    # NE PAS faire la suite dans le processus du serveur : les rendus WeasyPrint et l'assemblage y prennent plusieurs centaines de Mo que l'allocateur ne rend pas au système après la génération (relevé de /api/health/details sur Toolforge) ; un processus séparé rend tout en se terminant.
    runner = run_isolated if ISOLATE_ASSEMBLY else run_in_thread
    article_bytes = sum(path.stat().st_size for path, _ in fitted.values())
    background_bytes = sum(path.stat().st_size for path, _, _ in background_files.values())
    async for admission in _admitted(DISK_GATE, assembly_disk_reserve(article_bytes)):
        if isinstance(admission, Reservation):
            disk = admission
        else:
            yield admission
    note_wait(disk, "assembly_disk")
    try:
        async for admission in _admitted(MEMORY_GATE, assembly_reserve(article_bytes, background_bytes)):
            if isinstance(admission, Reservation):
                reservation = admission
            else:
                yield admission
    except BaseException:
        disk.release()
        raise
    note_wait(reservation, "assembly")
    try:
        # NE PAS enlever aclosing : sans lui, un client qui abandonne laisse tourner le processus d'assemblage jusqu'au ramasse-miettes, pendant que son dossier temporaire est supprimé.
        async with contextlib.aclosing(runner(_finish_book, project, selected, language, workdir, fitted, background_files)) as messages:
            async for kind, value in messages:
                if kind == "result":
                    output, size = value
                    yield {"type": "done", "path": output, "size": size}
                elif "progress" in value:
                    yield progress(value["progress"])
                else:
                    record.stage(value["stage"], "assembly", value["memory"], server_rss_bytes=_memory_snapshot()["rss_bytes"], **value["details"])
    finally:
        reservation.release()
        disk.release()


def _finish_book(
    project: Project,
    selected: list[Article | UploadedDocument],
    language: str,
    workdir: Path,
    fitted: dict[str, tuple[Path, int]],
    background_files: dict[str, tuple[Path, str, str]],
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

    def render_cover() -> bytes:
        started_at = time.monotonic()
        html = build_cover_html(project, language)
        stage("cover_html", duration_s=round(time.monotonic() - started_at, 2), background=project.cover_image is not None)
        return render(html)

    def place_file(pdf_data: bytes) -> tuple[Path, int]:
        return _fit_to_file(pdf_data, workdir / f"page-{next(page_numbers)}.pdf", page_width_mm, page_height_mm)

    stage("assembly_start")
    backgrounds = {
        field: BookImage(title=title, mime_type=mime_type, data_base64=base64.b64encode(path.read_bytes()).decode("ascii"))
        for field, (path, mime_type, title) in background_files.items()
    }
    project = project.model_copy(update=backgrounds)
    if backgrounds:
        started_at = time.monotonic()
        fitted_backgrounds = {field: fit_background(image, page_width_mm, page_height_mm) for field, image in backgrounds.items()}
        project = project.model_copy(update=fitted_backgrounds)
        stage(
            "fit_backgrounds",
            duration_s=round(time.monotonic() - started_at, 2),
            bytes_before=sum(len(image.data_base64 or "") * 3 // 4 for image in backgrounds.values()),
            bytes_after=sum(len(image.data_base64 or "") * 3 // 4 for image in fitted_backgrounds.values()),
        )
    slots = book_slots(groups)
    toc_at = toc_slot_index(project, groups, slots)
    toc_blocks = toc_block_count(project, selected, language)

    article_pages: dict[str, int] = {}
    chapter_pages: list[int | None] = [None] * len(groups)
    cover: bytes | None = None
    if project.page_numbers:
        step("compute_page_numbers")
        cover = render_cover()
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
        cover = render_cover()
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
    if has_back_cover(project):
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
            assembly.stamp_page_numbers(skip_last=has_back_cover(project))
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


VOLUME_QUERY = Query(default=None, ge=1, le=1000)


def _volume_of(project: Project, volume: int | None, language: str) -> Project:
    if volume is None:
        return project
    volumes = book_volumes(project, ARTICLE_LIMIT)
    if not volumes:
        raise HTTPException(status_code=400, detail="Sélectionnez au moins un article avant l’export.")
    if volume > len(volumes):
        raise HTTPException(status_code=422, detail=f"Ce livre compte {len(volumes)} volume(s) : le volume {volume} n’existe pas.")
    if len(volumes) == 1:
        return project
    return volume_project(project, volumes[volume - 1], volume - 1, len(volumes), language)


@app.post("/api/books/volumes", response_model=VolumePlan)
async def plan_book_volumes(project: Project, language: str = Query(default="fr", pattern=PDF_LANGUAGE_PATTERN)) -> VolumePlan:
    volumes = book_volumes(project, ARTICLE_LIMIT)
    return VolumePlan(
        limit=ARTICLE_LIMIT,
        volumes=[
            VolumeSummary(
                volume=index + 1,
                title=volume_project(project, items, index, len(volumes), language).book_title if len(volumes) > 1 else project.book_title,
                articles=sum(isinstance(item, Article) for item in items),
                documents=sum(isinstance(item, UploadedDocument) for item in items),
                keys=[item.key for item in items],
            )
            for index, items in enumerate(volumes)
        ],
    )


@app.post("/api/pdf")
async def create_pdf(
    project: Project, language: str = Query(default="fr", pattern=PDF_LANGUAGE_PATTERN), volume: int | None = VOLUME_QUERY
) -> Response:
    return await _create_pdf_response(_volume_of(project, volume, language), language)


@app.get("/api/pdf/from-source")
async def create_pdf_from_source(
    source: list[str] = Query(min_length=1, max_length=MAX_URL_SOURCES),
    language: str = Query(default="fr", pattern=PDF_LANGUAGE_PATTERN),
    wiki: str = Query(default="", max_length=12),
    summary: bool = False,
    volume: int | None = VOLUME_QUERY,
) -> Response:
    try:
        project = await project_from_sources(source, wiki or language, summary)
    except (MediaWikiError, ValueError) as error:
        refusal = _mediawiki_error(error)
        for item in source:
            note_refused_url(item, refusal)
        raise refusal from error
    return await _create_pdf_response(_volume_of(project, volume, language), language)


@app.get("/api/pdf/from-json")
async def create_pdf_from_json(
    url: str = Query(min_length=1, max_length=2048),
    language: str = Query(default="fr", pattern=PDF_LANGUAGE_PATTERN),
    volume: int | None = VOLUME_QUERY,
) -> Response:
    try:
        project = await fetch_project(url)
    except JsonSourceError as error:
        refusal = HTTPException(status_code=error.status_code, detail=str(error))
        note_refused_url(url, refusal)
        raise refusal from error
    return await _create_pdf_response(_volume_of(project, volume, language), language)


@app.post("/api/pdf/from-json")
async def create_pdf_from_json_body(
    payload: Any = Body(...),
    language: str = Query(default="fr", pattern=PDF_LANGUAGE_PATTERN),
    volume: int | None = VOLUME_QUERY,
) -> Response:
    try:
        project = project_from_payload(payload)
    except JsonSourceError as error:
        raise HTTPException(status_code=error.status_code, detail=str(error)) from error
    return await _create_pdf_response(_volume_of(project, volume, language), language)


@app.post("/api/pdf/from-wikitext")
async def create_pdf_from_wikitext(
    payload: BookWikitextRequest,
    language: str = Query(default="fr", pattern=PDF_LANGUAGE_PATTERN),
    volume: int | None = VOLUME_QUERY,
) -> Response:
    resolved = await read_book_wikitext(payload)
    book = resolved.book
    in_chapters = {key for chapter in book.chapters for key in chapter.article_keys}
    name = resolved.book_title or book.articles[0].title
    project = Project(
        name=name[:120],
        book_title=resolved.book_title[:200],
        book_subtitle=book.subtitle[:300],
        main_articles=book.articles,
        chapters=book.chapters,
        unassigned_first=bool(book.chapters) and book.articles[0].key not in in_chapters,
    )
    return await _create_pdf_response(_volume_of(project, volume, language), language)


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
        if isinstance(error, RemoteFileError):
            raise HTTPException(status_code=502, detail=str(error)) from error
        raise HTTPException(status_code=500, detail="La génération du PDF a échoué.") from error

    async def body():
        try:
            async for chunk in _pdf_chunks(done["path"]):
                yield chunk
        finally:
            await events.aclose()

    return ClosingStreamingResponse(
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
    project: Project, language: str = Query(default="fr", pattern=PDF_LANGUAGE_PATTERN), volume: int | None = VOLUME_QUERY
) -> StreamingResponse:
    project = _volume_of(project, volume, language)
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

    return ClosingStreamingResponse(
        events(),
        media_type="application/x-ndjson",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
