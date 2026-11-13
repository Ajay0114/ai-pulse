
import re
from typing import Any
from uuid import UUID

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Article, ArticleSummary, Category, Tag, Entity


def create_slug(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")[:120]


class ArticlePersistenceService:

    def _get_or_create_category(
        self,
        db: Session,
        name: str,
    ) -> Category:
        slug = create_slug(name)

        category = db.query(Category).filter(
            or_(
                func.lower(Category.name) == name.lower(),
                Category.slug == slug,
            )
        ).first()

        if category:
            return category

        category = Category(name=name, slug=slug)
        db.add(category)
        db.flush()

        return category

    def _get_or_create_tag(
        self,
        db: Session,
        name: str,
    ) -> Tag:
        slug = create_slug(name)

        tag = db.query(Tag).filter(
            or_(
                func.lower(Tag.name) == name.lower(),
                Tag.slug == slug,
            )
        ).first()

        if tag:
            return tag

        tag = Tag(name=name, slug=slug)
        db.add(tag)
        db.flush()

        return tag

    def save_relevance(
        self,
        db: Session,
        article_id: UUID,
        result: dict[str, Any],
    ) -> Article:

        article = db.query(Article).filter(
            Article.id == article_id
        ).first()

        if not article:
            raise ValueError(f"Article not found: {article_id}")

        # 1. Save relevance classification
        article.relevance_status = result["relevance_status"]
        article.relevance_score = float(result["relevance_score"])
        article.feed_type = result["feed_type"]
        article.importance_reason = result["importance_reason"]

        # 2. Keep classification separate from enrichment.
        # The caller controls the transaction.
        db.flush()

        return article

    def save_enrichment(
        self,
        db: Session,
        article_id: UUID,
        result: dict[str, Any],
    ) -> Article:

        article = db.query(Article).filter(
            Article.id == article_id
        ).first()

        if not article:
            raise ValueError(f"Article not found: {article_id}")

        # 1. Update article fields
        article.content_type = result["content_type"]
        article.importance_score = float(result["importance_score"])

        # 2. Save category
        category_name = result["category"].strip()

        if category_name:
            category = self._get_or_create_category(
                db, category_name
            )

            if category not in article.categories:
                article.categories.append(category)

        # 3. Save topics as tags
        for topic in result["topics"]:
            topic = topic.strip()

            if not topic:
                continue

            tag = self._get_or_create_tag(db, topic)

            if tag not in article.tags:
                article.tags.append(tag)

        # 4. Save companies, models and tools as entities
        entity_groups = {
            "companies": "company",
            "models": "model",
            "tools": "tool",
        }

        for field, entity_type in entity_groups.items():
            for entity_name in result[field]:
                entity_name = entity_name.strip()

                if not entity_name:
                    continue

                entity = db.query(Entity).filter(
                    func.lower(Entity.name) == entity_name.lower(),
                    Entity.entity_type == entity_type,
                ).first()

                if not entity:
                    entity = Entity(
                        name=entity_name,
                        entity_type=entity_type,
                    )
                    db.add(entity)
                    db.flush()

                if entity not in article.entities:
                    article.entities.append(entity)

        # 5. Save or update article summary
        model_name = settings.LLM_MODEL

        summary = db.query(ArticleSummary).filter(
            ArticleSummary.article_id == article.id,
            ArticleSummary.model_name == model_name,
            ArticleSummary.language == "en",
        ).first()

        detailed_summary = "\n".join(
            f"- {point}" for point in result["key_points"]
        )

        if not summary:
            summary = ArticleSummary(
                article_id=article.id,
                model_name=model_name,
                language="en",
                short_summary=result["summary"],
                detailed_summary=detailed_summary,
                why_it_matters=result["importance_reason"],
            )
            db.add(summary)
        else:
            summary.short_summary = result["summary"]
            summary.detailed_summary = detailed_summary
            summary.why_it_matters = result["importance_reason"]

        # 6. Update processing status
        article.processing_status = "processed"

        # Caller controls the transaction
        db.flush()

        return article


article_persistence_service = ArticlePersistenceService()
