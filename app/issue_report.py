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

import json
import queue
import re
import threading
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone

import httpx

from app.request_limits import count_setting
from app.wikipedia_api import USER_AGENT

ISSUE_LABEL = "generationProbleme"
DEFAULT_REPOSITORY = "gmoulard/wikipedia2book"
DEFAULT_ISSUES_PER_DAY = 20
GITHUB_API = "https://api.github.com"
GITHUB_TIMEOUT_S = 30
# NE PAS relever : GitHub refuse un corps d'issue ou de commentaire de plus de 65 536 caractères (HTTP 422), l'issue serait perdue.
GITHUB_TEXT_MAX = 60_000
MAX_COMMENTS = 25
REPOSITORY_NAME = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
issue_transport: httpx.BaseTransport | None = None


@dataclass
class IssueSettings:
    token: str
    repository: str
    per_day: int


@dataclass
class GenerationFailure:
    generation: dict
    error: str
    traceback: str
    request: bytes | None
    debug: dict = field(default_factory=dict)


def issue_settings(environ: Mapping[str, str]) -> IssueSettings:
    repository = environ.get("WIKIPEDIA2BOOK_ISSUE_REPOSITORY", "").strip() or DEFAULT_REPOSITORY
    if not REPOSITORY_NAME.match(repository):
        raise ValueError(f"WIKIPEDIA2BOOK_ISSUE_REPOSITORY doit être de la forme propriétaire/dépôt (reçu : {repository!r}).")
    return IssueSettings(
        environ.get("WIKIPEDIA2BOOK_GITHUB_TOKEN", "").strip(),
        repository,
        count_setting(environ, "WIKIPEDIA2BOOK_ISSUES_PER_DAY", DEFAULT_ISSUES_PER_DAY),
    )


def _block(text: str, language: str) -> str:
    longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}{language}\n{text}\n{fence}"


def _chunks(text: str, size: int) -> list[str]:
    return [text[start:start + size] for start in range(0, len(text), size)] or [""]


def issue_title(failure: GenerationFailure) -> str:
    generation = failure.generation
    summary = " ".join(failure.error.split())[:150]
    return f"{ISSUE_LABEL} : génération {generation['id']} ({generation.get('version')}) – {summary}"[:250]


def issue_sections(failure: GenerationFailure) -> list[tuple[str, str, str]]:
    generation = failure.generation
    journal = json.dumps(generation, ensure_ascii=False, indent=1)
    if failure.request is None:
        request = json.dumps({"missing": f"demande absente de la mémoire (plus de {generation.get('request_bytes')} octets ou effacée)"}, ensure_ascii=False)
    else:
        request = failure.request.decode("utf-8", errors="replace")
    return [
        ("Trace de l’erreur", failure.traceback or failure.error, "text"),
        ("Informations de débogage", json.dumps(failure.debug, ensure_ascii=False, indent=1), "json"),
        ("Journal de la génération", journal, "json"),
        ("Demande (livre JSON, à importer dans Wikipedia2Book)", request, "json"),
    ]


def issue_texts(failure: GenerationFailure, limit: int = GITHUB_TEXT_MAX) -> tuple[str, list[str]]:
    generation = failure.generation
    intro = "\n".join([
        f"La génération **{generation['id']}** a échoué le {generation.get('started')} après {generation.get('duration_s')} s.",
        "",
        f"**Erreur :** {' '.join(failure.error.split())}",
        "",
        f"Version {generation.get('version')}, langue `{generation.get('language')}`, {generation.get('articles')} articles, {generation.get('documents')} documents, {generation.get('chapters')} chapitres, format {generation.get('page_format')} {generation.get('orientation')}.",
        "",
        "Issue créée automatiquement par le serveur. La demande ci-dessous est le livre JSON à importer dans Wikipedia2Book pour reproduire l’erreur (contenu des fichiers importés retiré).",
    ])
    body = intro
    comments: list[str] = []
    overflow = False
    for title, text, language in issue_sections(failure):
        section = f"\n\n## {title}\n\n<details><summary>{title}</summary>\n\n{_block(text, language)}\n\n</details>"
        if not overflow and len(body) + len(section) <= limit:
            body += section
            continue
        overflow = True
        size = limit - len(title) - 200
        parts = _chunks(text, size)
        for index, part in enumerate(parts, 1):
            comments.append(f"## {title} ({index}/{len(parts)})\n\n{_block(part, language)}")
    if overflow:
        body += "\n\nLa suite est dans les commentaires de cette issue."
    if len(comments) > MAX_COMMENTS:
        dropped = len(comments) - MAX_COMMENTS + 1
        comments = comments[:MAX_COMMENTS - 1] + [f"{dropped} commentaires de plus n’ont pas été envoyés (plus de {MAX_COMMENTS} commentaires)."]
    return body, comments


class IssueReporter:
    # NE PAS envoyer dans le fil de la requête : un GitHub lent gèlerait tout le serveur ; un fil séparé, comme GenerationFiles.
    def __init__(self, settings: IssueSettings) -> None:
        self.settings = settings
        self.failures: queue.SimpleQueue = queue.SimpleQueue()
        self.sender: threading.Thread | None = None
        self.day: str | None = None
        self.sent_today = 0
        self.lock = threading.Lock()

    @property
    def enabled(self) -> bool:
        return bool(self.settings.token)

    def _allowed(self) -> bool:
        with self.lock:
            day = datetime.now(timezone.utc).date().isoformat()
            if day != self.day:
                self.day, self.sent_today = day, 0
            if self.settings.per_day and self.sent_today >= self.settings.per_day:
                return False
            self.sent_today += 1
            return True

    def report(self, failure: GenerationFailure) -> None:
        if not self.enabled:
            return
        if not self._allowed():
            failure.generation["issue"] = "quota"
            print(json.dumps({"issue_report_skipped": failure.generation["id"], "reason": "per_day", "limit": self.settings.per_day}), flush=True)
            return
        self.failures.put(failure)
        if self.sender is None:
            self.sender = threading.Thread(target=self._run, name="issue-report", daemon=True)
            self.sender.start()

    def _run(self) -> None:
        while True:
            self.send(self.failures.get())

    def send(self, failure: GenerationFailure) -> str | None:
        generation = failure.generation
        body, comments = issue_texts(failure)
        headers = {
            "Authorization": f"Bearer {self.settings.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": USER_AGENT,
        }
        issues = f"{GITHUB_API}/repos/{self.settings.repository}/issues"
        try:
            with httpx.Client(transport=issue_transport, timeout=GITHUB_TIMEOUT_S, headers=headers) as client:
                response = client.post(issues, json={"title": issue_title(failure), "body": body, "labels": [ISSUE_LABEL]})
                response.raise_for_status()
                issue = response.json()
                for comment in comments:
                    client.post(f"{issues}/{issue['number']}/comments", json={"body": comment}).raise_for_status()
        except (httpx.HTTPError, ValueError, KeyError) as error:
            status = error.response.status_code if isinstance(error, httpx.HTTPStatusError) else None
            generation["issue"] = "failed"
            print(json.dumps({"issue_report_error": f"{type(error).__name__}", "status": status, "generation": generation["id"], "repository": self.settings.repository}), flush=True)
            return None
        generation["issue"] = issue.get("html_url")
        print(json.dumps({"issue_report": generation["id"], "number": issue["number"]}), flush=True)
        return generation["issue"]
