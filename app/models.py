from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Article(BaseModel):
    page_id: int | None = Field(default=None, ge=1)
    title: str
    language: str
    url: str
    summary: str = ""
    origin_title: str | None = None
    depth: int = Field(default=0, ge=0)
    selected: bool = False

    @property
    def key(self) -> str:
        if self.page_id is not None:
            return f"{self.language}:{self.page_id}"
        return f"{self.language}:title:{self.title.lower()}"


class UploadedDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(min_length=1, max_length=300)
    kind: Literal["image", "pdf"]
    mime_type: str = Field(min_length=1, max_length=100)
    data_base64: str = Field(min_length=1, max_length=30_000_000)
    selected: bool = True

    @property
    def key(self) -> str:
        return f"doc:{self.id}"


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
    toc_position: Literal["start", "end"] = "start"
    page_numbers: bool = False
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class ArticleRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=300)
    url: str | None = Field(default=None, max_length=2048)
    language: str = Field(default="fr", pattern=r"^[a-z0-9-]{2,12}$")
    page_id: int | None = Field(default=None, ge=1)
    summary: str = Field(default="", max_length=1000)

    @model_validator(mode="after")
    def require_one_source(self):
        if bool(self.title) == bool(self.url):
            raise ValueError("Fournissez un titre ou une URL, mais pas les deux.")
        return self


class BookImportRequest(BaseModel):
    url: str = Field(min_length=1, max_length=2048)


class ProjectExplorationRequest(BaseModel):
    project: Project
    max_depth: int = Field(default=1, ge=0, le=3)
    max_articles: int = Field(default=30, ge=1, le=200)
