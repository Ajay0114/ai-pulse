from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.source import Source
from app.schemas.source import SourceCreate, SourceUpdate


def get_source(db: Session, source_id: UUID) -> Source | None:
    return db.get(Source, source_id)


def get_sources(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    source_type: str | None = None,
    platform: str | None = None,
    health_status: str | None = None,
    is_active: bool | None = None,
) -> tuple[list[Source], int]:

    query = select(Source)

    if source_type:
        query = query.where(Source.source_type == source_type)

    if platform:
        query = query.where(Source.platform == platform)

    if health_status:
        query = query.where(Source.health_status == health_status)

    if is_active is not None:
        query = query.where(Source.is_active == is_active)

    total = len(db.scalars(query).all())

    sources = db.scalars(
        query.order_by(Source.priority.asc(), Source.name.asc())
        .offset(skip)
        .limit(limit)
    ).all()

    return list(sources), total


def create_source(db: Session, source_data: SourceCreate) -> Source:
    data = source_data.model_dump()

    for field in ("base_url", "feed_url"):
        if data.get(field) is not None:
            data[field] = str(data[field])

    source = Source(**data)

    db.add(source)
    db.commit()
    db.refresh(source)

    return source


def update_source(
    db: Session,
    source: Source,
    source_data: SourceUpdate,
) -> Source:

    data = source_data.model_dump(exclude_unset=True)

    for field in ("base_url", "feed_url"):
        if data.get(field) is not None:
            data[field] = str(data[field])

    for field, value in data.items():
        setattr(source, field, value)

    db.commit()
    db.refresh(source)

    return source


def deactivate_source(db: Session, source: Source) -> Source:
    source.is_active = False

    db.commit()
    db.refresh(source)

    return source