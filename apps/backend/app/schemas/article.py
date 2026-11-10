
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ArticleSourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    platform: str | None = None


class ArticleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_id: UUID
    title: str
    original_url: str
    canonical_url: str | None = None
    author: str | None = None
    description: str | None = None
    content: str | None = None
    content_type: str
    language: str | None = None
    published_at: datetime | None = None
    discovered_at: datetime
    importance_score: float | None = None
    engagement_count: int | None = None
    processing_status: str
    source: ArticleSourceResponse


class ArticleListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    articles: list[ArticleResponse]
