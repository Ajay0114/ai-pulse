import uuid

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class ArticleSummary(Base, TimestampMixin):
    __tablename__ = "article_summaries"

    __table_args__ = (
        UniqueConstraint(
            "article_id",
            "model_name",
            "language",
            name="uq_article_summary_model_language",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    article_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("articles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    model_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    language: Mapped[str] = mapped_column(
        String(20),
        default="en",
        nullable=False,
    )

    short_summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    detailed_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    why_it_matters: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    industry_impact: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    article: Mapped["Article"] = relationship(
        back_populates="summaries",
    )