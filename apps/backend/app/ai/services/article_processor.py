
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.ai.services.article_enrichment import (
    ArticleEnrichmentService,
)
from app.ai.services.article_persistence import (
    ArticlePersistenceService,
)
from app.ai.services.article_relevance import (
    ArticleRelevanceService,
)
from app.models import Article


class ArticleProcessor:

    def __init__(self):
        self.relevance_service = ArticleRelevanceService()
        self.enrichment_service = ArticleEnrichmentService()
        self.persistence_service = ArticlePersistenceService()

    async def process(
        self,
        db: Session,
        article_id: UUID,
    ) -> dict[str, Any]:

        article = db.query(Article).filter(
            Article.id == article_id
        ).first()

        if not article:
            raise ValueError(f"Article not found: {article_id}")

        title = article.title
        description = article.description or article.content or ""
        source_name = article.source.name if article.source else ""
        source_url = article.original_url

        try:
            # Step 1: Classify article relevance.
            relevance = await self.relevance_service.classify(
                title=title,
                description=description,
                source_name=source_name,
                source_url=source_url,
            )

            # Step 2: Persist classification.
            self.persistence_service.save_relevance(
                db=db,
                article_id=article_id,
                result=relevance,
            )

            # Step 3: Exclude irrelevant articles.
            if relevance["relevance_status"] == "irrelevant":
                article.processing_status = "skipped"
                db.commit()

                return {
                    "success": True,
                    "article_id": str(article_id),
                    "title": title,
                    "relevance": relevance,
                    "processing_status": "skipped",
                    "message": "Article excluded from AI Pulse feeds.",
                }

            # Step 4: Enrich relevant articles.
            enrichment = await self.enrichment_service.enrich(
                title=title,
                description=description,
                source_name=source_name,
                source_url=source_url,
            )

            # Step 5: Persist enrichment.
            self.persistence_service.save_enrichment(
                db=db,
                article_id=article_id,
                result=enrichment,
            )

            # Step 6: Commit classification and enrichment together.
            db.commit()

            return {
                "success": True,
                "article_id": str(article_id),
                "title": title,
                "relevance": relevance,
                "enrichment": enrichment,
                "processing_status": "processed",
            }

        except Exception:
            db.rollback()
            raise


article_processor = ArticleProcessor()
