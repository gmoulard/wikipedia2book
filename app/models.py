from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Article(BaseModel):
    page_id: int
    title: str
    language: str
    url: str
    summary: str = ""
    last_modified: datetime | None = None
    content_html: str = ""
    references_html: str = ""
    origin_title: str | None = None
    depth: int = Field(default=0, ge=0)
    selected: bool = False

    @property
    def key(self) -> str:
        return f"{self.language}:{self.page_id}"


class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=2000)
    main_articles: list[Article] = Field(default_factory=list)
    discovered_articles: list[Article] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=2000)


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)


class ArticleRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=300)
    url: str | None = Field(default=None, max_length=2048)
    language: str = Field(default="fr", pattern=r"^[a-z0-9-]{2,12}$")

    @model_validator(mode="after")
    def require_one_source(self):
        if bool(self.title) == bool(self.url):
            raise ValueError("Fournissez un titre ou une URL, mais pas les deux.")
        return self


class ExploreRequest(BaseModel):
    max_depth: int = Field(default=1, ge=0, le=3)
    max_articles: int = Field(default=30, ge=1, le=200)


class SelectionRequest(BaseModel):
    article_keys: list[str] = Field(default_factory=list)
