
from datetime import datetime
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.article import Article
from app.models.category import Category


def get_articles(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    source_id: UUID | None = None,
    content_type: str | None = None,
    feed_type: str | None = None,
    category: str | None = None,
    published_from: datetime | None = None,
    published_to: datetime | None = None,
    sort_by: str = "newest",
):
    query = select(Article).options(
        joinedload(Article.source),
        selectinload(Article.categories),
        selectinload(Article.tags),
        selectinload(Article.entities),
        selectinload(Article.summaries),
    )

    # Public feeds only ever show articles that passed editorial review.
    query = query.where(Article.relevance_status == "relevant")

    if feed_type:
        query = query.where(Article.feed_type == feed_type)

    if category:
        query = query.where(
            Article.categories.any(Category.slug == category)
        )

    if search:
        search_term = f"%{search.strip()}%"
        query = query.where(
            or_(
                Article.title.ilike(search_term),
                Article.description.ilike(search_term),
            )
        )

    if source_id:
        query = query.where(Article.source_id == source_id)

    if content_type:
        query = query.where(Article.content_type == content_type)

    if published_from:
        query = query.where(Article.published_at >= published_from)

    if published_to:
        query = query.where(Article.published_at <= published_to)

    total = db.scalar(
        select(func.count()).select_from(query.subquery())
    ) or 0

    if sort_by == "oldest":
        query = query.order_by(
            Article.published_at.asc().nullslast()
        )
    elif sort_by == "importance":
        query = query.order_by(
            Article.importance_score.desc().nullslast(),
            Article.published_at.desc().nullslast(),
        )
    else:
        query = query.order_by(
            Article.published_at.desc().nullslast(),
            Article.discovered_at.desc(),
        )

    articles = db.scalars(
        query.offset((page - 1) * page_size).limit(page_size)
    ).unique().all()

    return articles, total


def get_article_by_id(db: Session, article_id: UUID):
    return db.scalar(
        select(Article)
        .options(
            joinedload(Article.source),
            selectinload(Article.categories),
            selectinload(Article.tags),
            selectinload(Article.entities),
            selectinload(Article.summaries),
        )
        .where(Article.id == article_id)
    )
