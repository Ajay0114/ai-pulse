import uuid

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.associations import article_entities


class Entity(Base, TimestampMixin):
    __tablename__ = "entities"

    __table_args__ = (
        UniqueConstraint(
            "name",
            "entity_type",
            name="uq_entity_name_type",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
    )

    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    canonical_name: Mapped[str | None] = mapped_column(
        String(300),
        nullable=True,
    )

    articles: Mapped[list["Article"]] = relationship(
        secondary=article_entities,
        back_populates="entities",
    )