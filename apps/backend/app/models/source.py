import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    DateTime,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Source(Base, TimestampMixin):
    __tablename__ = "sources"

    __table_args__ = (
        UniqueConstraint(
            "name",
            "source_type",
            name="uq_source_name_type",
        ),
        Index("ix_sources_type_active", "source_type", "is_active"),
        Index("ix_sources_next_fetch", "next_fetch_at", "is_active"),
        Index("ix_sources_health", "health_status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    source_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    platform: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    base_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    feed_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    language: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    region: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    poll_interval_minutes: Mapped[int] = mapped_column(
        Integer,
        default=30,
        nullable=False,
    )

    last_fetched_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    next_fetch_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    health_status: Mapped[str] = mapped_column(
        String(30),
        default="unknown",
        nullable=False,
    )

    consecutive_failures: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        default=5,
        nullable=False,
    )

    metadata_: Mapped[dict] = mapped_column(
        "metadata",
        JSONB,
        default=dict,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    articles: Mapped[list["Article"]] = relationship(
        back_populates="source",
    )