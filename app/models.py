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

import binascii
from base64 import b64decode
from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


Site = Literal["wikipedia", "wikisource", "wikibooks", "wikivoyage", "wikiversity", "wikiquote", "wiktionary", "wikinews"]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Article(BaseModel):
    page_id: int | None = Field(default=None, ge=1)
    title: str
    language: str
    site: Site = "wikipedia"
    url: str
    summary: str = ""
    origin_title: str | None = None
    depth: int = Field(default=0, ge=0)
    selected: bool = False

    # NE PAS préfixer les clés Wikipédia : elles doivent rester identiques à celles des fichiers JSON déjà exportés (chapitres, ordre) ; garder aligné avec articleKey dans app.js.
    @property
    def key(self) -> str:
        prefix = "" if self.site == "wikipedia" else f"{self.site}:"
        if self.page_id is not None:
            return f"{prefix}{self.language}:{self.page_id}"
        return f"{prefix}{self.language}:title:{self.title.lower()}"


REMOTE_URL = r"^https://[^\s]+$"
# NE PAS laisser Pillow ouvrir tous les formats qu'il reconnaît : une image annoncée PNG mais contenant de l'EPS serait confiée à Ghostscript, qui peut exécuter du code ; seuls des formats décodés par Pillow lui-même.
SAFE_IMAGE_FORMATS = ("PNG", "JPEG", "GIF", "WEBP", "BMP", "TIFF")


def _one_source(data_base64: str | None, url: str | None, mime_type: str | None) -> None:
    if (data_base64 is None) == (url is None):
        raise ValueError("Indiquez soit l’adresse du fichier (url), soit son contenu (data_base64), pas les deux.")
    if data_base64 is not None and not mime_type:
        raise ValueError("Type de fichier (mime_type) manquant pour un contenu base64.")


class UploadedDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(min_length=1, max_length=300)
    kind: Literal["image", "pdf", "html"]
    mime_type: str = Field(default="", max_length=100)
    data_base64: str | None = Field(default=None, min_length=1, max_length=30_000_000)
    url: str | None = Field(default=None, max_length=2048, pattern=REMOTE_URL)
    selected: bool = True

    @model_validator(mode="after")
    def single_source(self) -> "UploadedDocument":
        if self.kind == "html" and self.url is None:
            raise ValueError("Une page web est donnée par son adresse (url), jamais par son contenu.")
        _one_source(self.data_base64, self.url, self.mime_type)
        return self

    @property
    def key(self) -> str:
        return f"doc:{self.id}"


class BookImage(BaseModel):
    title: str = Field(default="", max_length=300)
    mime_type: str | None = Field(default=None, pattern=r"^image/(png|jpeg|gif|webp|svg\+xml)$")
    data_base64: str | None = Field(default=None, min_length=1, max_length=30_000_000)
    url: str | None = Field(default=None, max_length=2048, pattern=REMOTE_URL)

    @field_validator("data_base64")
    @classmethod
    def decodable(cls, value: str | None) -> str | None:
        if value is None:
            return value
        try:
            b64decode(value, validate=True)
        except binascii.Error as error:
            raise ValueError("Image illisible : contenu base64 invalide.") from error
        return value

    @model_validator(mode="after")
    def single_source(self) -> "BookImage":
        _one_source(self.data_base64, self.url, self.mime_type)
        return self


class BookChapter(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(min_length=1, max_length=120)
    article_keys: list[str] = Field(default_factory=list)


class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=2000)
    main_articles: list[Article] = Field(default_factory=list)
    discovered_articles: list[Article] = Field(default_factory=list)
    uploaded_documents: list[UploadedDocument] = Field(default_factory=list)
    book_title: str = Field(default="", max_length=200)
    book_subtitle: str = Field(default="", max_length=300)
    book_author: str = Field(default="", max_length=200)
    introduction: str = Field(default="", max_length=20000)
    conclusion: str = Field(default="", max_length=20000)
    cover_image: BookImage | None = None
    back_image: BookImage | None = None
    # NE PAS revenir à None par défaut : couverture bleue rgb(39, 60, 117) demandée par l'utilisateur ; garder aligné avec normalizeProject (app.js) et le sélecteur de couverture (index.html). null explicite = sans couleur.
    cover_color: str | None = Field(default="#273c75", pattern=r"^#[0-9a-fA-F]{6}$")
    back_color: str | None = Field(default=None, pattern=r"^#[0-9a-fA-F]{6}$")
    cover_logo: bool = False
    back_logo: bool = False
    page_format: Literal["A0", "A1", "A2", "A3", "A4", "A5", "A6", "Letter", "Legal", "custom"] = "A4"
    custom_width_mm: float = Field(default=148, ge=50, le=1000)
    custom_height_mm: float = Field(default=210, ge=50, le=1000)
    orientation: Literal["portrait", "landscape"] = "portrait"
    margin_top_mm: float = Field(default=18, ge=0, le=100)
    margin_bottom_mm: float = Field(default=18, ge=0, le=100)
    margin_inside_mm: float = Field(default=18, ge=0, le=100)
    margin_outside_mm: float = Field(default=16, ge=0, le=100)
    margin_binding_mm: float = Field(default=0, ge=0, le=40)
    article_order: list[str] = Field(default_factory=list)
    chapters: list[BookChapter] = Field(default_factory=list)
    toc_position: str = Field(default="start", max_length=320, pattern=r"^(start|end|before:.+)$")
    unassigned_first: bool = False
    volume_breaks: list[str] = Field(default_factory=list, max_length=500)
    table_of_contents: bool = True
    page_numbers: bool = True
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class ArticleRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=300)
    url: str | None = Field(default=None, max_length=2048)
    language: str = Field(default="fr", pattern=r"^[a-z0-9-]{2,12}$")
    site: Site = "wikipedia"
    page_id: int | None = Field(default=None, ge=1)
    summary: str = Field(default="", max_length=1000)

    @model_validator(mode="after")
    def require_one_source(self):
        if bool(self.title) == bool(self.url):
            raise ValueError("Fournissez un titre ou une URL, mais pas les deux.")
        return self


class BookImportRequest(BaseModel):
    url: str = Field(min_length=1, max_length=2048)


class WikipediaBookImport(BaseModel):
    articles: list[Article]
    subtitle: str = ""
    chapters: list[BookChapter] = Field(default_factory=list)
    unassigned_first: bool = False


class VolumeSummary(BaseModel):
    volume: int
    title: str
    articles: int
    documents: int
    keys: list[str]


class VolumePlan(BaseModel):
    limit: int | None
    volumes: list[VolumeSummary]


class BookWikitextRequest(BaseModel):
    wikitext: str = Field(min_length=1, max_length=200_000)
    language: str = Field(default="fr", pattern=r"^[a-z0-9-]{2,12}$")


class SourceRequest(BaseModel):
    input: str = Field(min_length=1, max_length=2048)
    language: str = Field(default="fr", pattern=r"^[a-z0-9-]{2,12}$")
    site: Site = "wikipedia"
    languages: list[str] = Field(default=[], max_length=12)


class SourceResolution(BaseModel):
    kind: Literal["article", "book", "subpages", "search"]
    article: Article | None = None
    book: WikipediaBookImport | None = None
    book_title: str = ""
    results: list[dict] = []


class WikipediaBookGenerationRequest(BookImportRequest):
    book_title: str | None = Field(default=None, max_length=200)
    book_subtitle: str | None = Field(default=None, max_length=300)
    book_author: str | None = Field(default=None, max_length=200)
    book_conclusion: str = Field(default="", max_length=20000)
    page_format: Literal["A0", "A1", "A2", "A3", "A4", "A5", "A6", "Letter", "Legal", "custom"] = "A4"
    orientation: Literal["portrait", "landscape"] = "portrait"
    page_numbers: bool = True
    table_of_contents: bool = True


class ProjectExplorationRequest(BaseModel):
    project: Project
    max_depth: int = Field(default=1, ge=0, le=3)
    max_articles: int = Field(default=30, ge=1, le=200)


class BookGenerationRequest(BaseModel):
    articles: list[ArticleRequest] = Field(min_length=1, max_length=200)
    book_title: str = Field(default="", max_length=200)
    book_subtitle: str = Field(default="", max_length=300)
    book_author: str = Field(default="", max_length=200)
    introduction: str = Field(default="", max_length=20000)
    conclusion: str = Field(default="", max_length=20000)
    page_format: Literal["A0", "A1", "A2", "A3", "A4", "A5", "A6", "Letter", "Legal", "custom"] = "A4"
    custom_width_mm: float = Field(default=148, ge=50, le=1000)
    custom_height_mm: float = Field(default=210, ge=50, le=1000)
    orientation: Literal["portrait", "landscape"] = "portrait"
    margin_top_mm: float = Field(default=18, ge=0, le=100)
    margin_bottom_mm: float = Field(default=18, ge=0, le=100)
    margin_inside_mm: float = Field(default=18, ge=0, le=100)
    margin_outside_mm: float = Field(default=16, ge=0, le=100)
    margin_binding_mm: float = Field(default=0, ge=0, le=40)
    toc_position: Literal["start", "end"] = "start"
    table_of_contents: bool = True
    page_numbers: bool = True
