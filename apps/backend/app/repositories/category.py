from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.article import Article
from app.models.associations import article_categories
from app.models.category import Category


def get_categories(db: Session) -> list[dict]:
    rows = db.execute(
        select(
            Category.id,
            Category.name,
            Category.slug,
            func.count(Article.id).label("article_count"),
        )
        .select_from(Category)
        .join(
            article_categories,
            article_categories.c.category_id == Category.id,
        )
        .join(Article, Article.id == article_categories.c.article_id)
        .where(Article.relevance_status == "relevant")
        .group_by(Category.id, Category.name, Category.slug)
        .order_by(func.count(Article.id).desc())
    ).all()

    return [
        {
            "id": row.id,
            "name": row.name,
            "slug": row.slug,
            "article_count": row.article_count,
        }
        for row in rows
    ]
