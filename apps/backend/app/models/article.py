import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.associations import article_categories, article_tags, article_entities
from datetime import datetime, timezone



class Article(Base, TimestampMixin):
    __tablename__ = "articles"

    __table_args__ = (
        UniqueConstraint(
            "source_id",
            "external_id",
            name="uq_article_source_external_id",
        ),
        Index("ix_articles_published_at", "published_at"),
        Index("ix_articles_discovered_at", "discovered_at"),
        Index("ix_articles_source_published", "source_id", "published_at"),
        Index("ix_articles_importance", "importance_score"),
        Index("ix_articles_content_type", "content_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sources.id", ondelete="RESTRICT"),
        nullable=False,
    )

    story_cluster_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("story_clusters.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    external_id: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    title: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    original_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    canonical_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    author: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    content_type: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    language: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    importance_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    engagement_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    content_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )

    processing_status: Mapped[str] = mapped_column(
        String(30),
        default="pending",
        nullable=False,
    )

    source: Mapped["Source"] = relationship(
        back_populates="articles",
    )

    story_cluster: Mapped["StoryCluster | None"] = relationship(
        back_populates="articles",
    )

    categories: Mapped[list["Category"]] = relationship(
        secondary=article_categories,
        back_populates="articles",
    )

    tags: Mapped[list["Tag"]] = relationship(
        secondary=article_tags,
        back_populates="articles",
    )

    entities: Mapped[list["Entity"]] = relationship(
        secondary=article_entities,
        back_populates="articles",
    )

    summaries: Mapped[list["ArticleSummary"]] = relationship(
        back_populates="article",
        cascade="all, delete-orphan",
    )

    embeddings: Mapped[list["ArticleEmbedding"]] = relationship(
        back_populates="article",
        cascade="all, delete-orphan",
    )