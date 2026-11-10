from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class SourceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    source_type: str = Field(min_length=2, max_length=50)
    platform: str | None = None

    base_url: HttpUrl | None = None
    feed_url: HttpUrl | None = None
    description: str | None = None

    language: str | None = "en"
    region: str | None = None

    poll_interval_minutes: int = Field(default=30, ge=5)
    priority: int = Field(default=5, ge=1, le=10)

    metadata_: dict[str, Any] = Field(
        default_factory=dict,
        alias="metadata",
    )

    model_config = ConfigDict(populate_by_name=True)


class SourceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=200)
    source_type: str | None = None
    platform: str | None = None

    base_url: HttpUrl | None = None
    feed_url: HttpUrl | None = None
    description: str | None = None

    language: str | None = None
    region: str | None = None

    poll_interval_minutes: int | None = Field(default=None, ge=5)
    priority: int | None = Field(default=None, ge=1, le=10)

    is_active: bool | None = None

    metadata_: dict[str, Any] | None = Field(
        default=None,
        alias="metadata",
    )

    model_config = ConfigDict(populate_by_name=True)


class SourceResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    id: UUID
    name: str
    source_type: str
    platform: str | None
    base_url: str | None
    feed_url: str | None
    description: str | None
    language: str | None
    region: str | None
    poll_interval_minutes: int
    last_fetched_at: datetime | None
    next_fetch_at: datetime | None
    health_status: str
    consecutive_failures: int
    priority: int
    is_active: bool

    metadata_: dict[str, Any] = Field(
        validation_alias="metadata_",
        serialization_alias="metadata",
    )

    created_at: datetime
    updated_at: datetime