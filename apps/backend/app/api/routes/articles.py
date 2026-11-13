
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.article import get_articles, get_article_by_id
from app.schemas.article import ArticleResponse, ArticleListResponse

router = APIRouter()


@router.get("/", response_model=ArticleListResponse)
def list_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    source_id: UUID | None = None,
    content_type: str | None = None,
    feed_type: str | None = Query(None, pattern="^(main|research)$"),
    category: str | None = None,
    published_from: datetime | None = None,
    published_to: datetime | None = None,
    sort_by: str = Query("newest", pattern="^(newest|oldest|importance)$"),
    db: Session = Depends(get_db),
):
    if published_from and published_to and published_from > published_to:
        raise HTTPException(
            status_code=400,
            detail="published_from cannot be later than published_to",
        )

    articles, total = get_articles(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        source_id=source_id,
        content_type=content_type,
        feed_type=feed_type,
        category=category,
        published_from=published_from,
        published_to=published_to,
        sort_by=sort_by,
    )

    total_pages = (total + page_size - 1) // page_size

    return ArticleListResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        articles=articles,
    )


@router.get("/latest", response_model=ArticleListResponse)
def latest_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    feed_type: str | None = Query(None, pattern="^(main|research)$"),
    db: Session = Depends(get_db),
):
    articles, total = get_articles(
        db=db,
        page=page,
        page_size=page_size,
        feed_type=feed_type,
        sort_by="newest",
    )

    return ArticleListResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
        articles=articles,
    )


@router.get("/{article_id}", response_model=ArticleResponse)
def article_detail(
    article_id: UUID,
    db: Session = Depends(get_db),
):
    article = get_article_by_id(db, article_id)

    if not article:
        raise HTTPException(
            status_code=404,
            detail="Article not found",
        )

    return article
