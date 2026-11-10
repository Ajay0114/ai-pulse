from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories import source as source_repo
from app.schemas.source import (
    SourceCreate,
    SourceResponse,
    SourceUpdate,
)

router = APIRouter(prefix="/sources", tags=["Sources"])


@router.get("/", response_model=dict)
def list_sources(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    source_type: str | None = None,
    platform: str | None = None,
    health_status: str | None = None,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
):
    sources, total = source_repo.get_sources(
        db=db,
        skip=skip,
        limit=limit,
        source_type=source_type,
        platform=platform,
        health_status=health_status,
        is_active=is_active,
    )

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [
            SourceResponse.model_validate(source).model_dump(mode="json", by_alias=True)
            for source in sources
        ],
    }


@router.get("/{source_id}", response_model=SourceResponse)
def get_source(
    source_id: UUID,
    db: Session = Depends(get_db),
):
    source = source_repo.get_source(db, source_id)

    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found",
        )

    return source


@router.post(
    "/",
    response_model=SourceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_source(
    source_data: SourceCreate,
    db: Session = Depends(get_db),
):
    try:
        return source_repo.create_source(db, source_data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A source with this name and source type already exists",
        )


@router.put("/{source_id}", response_model=SourceResponse)
def update_source(
    source_id: UUID,
    source_data: SourceUpdate,
    db: Session = Depends(get_db),
):
    source = source_repo.get_source(db, source_id)

    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found",
        )

    try:
        return source_repo.update_source(db, source, source_data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A source with this name and source type already exists",
        )


@router.delete("/{source_id}", response_model=SourceResponse)
def deactivate_source(
    source_id: UUID,
    db: Session = Depends(get_db),
):
    source = source_repo.get_source(db, source_id)

    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found",
        )

    return source_repo.deactivate_source(db, source)


@router.patch("/{source_id}/toggle", response_model=SourceResponse)
def toggle_source(
    source_id: UUID,
    db: Session = Depends(get_db),
):
    source = source_repo.get_source(db, source_id)

    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found",
        )

    source_data = SourceUpdate(is_active=not source.is_active)

    return source_repo.update_source(db, source, source_data)