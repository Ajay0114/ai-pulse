
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.ai.services.article_enrichment import (
    ArticleEnrichmentService,
)
from app.ai.services.article_persistence import (
    ArticlePersistenceService,
)
from app.models import Article


class ArticleProcessor:
    def __init__(self):
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

        # Capture article data before calling the LLM.
        title = article.title
        description = article.description or article.content or ""
        source_name = article.source.name if article.source else ""
        source_url = article.original_url

        try:
            # Step 1: Generate AI enrichment.
            result = await self.enrichment_service.enrich(
                title=title,
                description=description,
                source_name=source_name,
                source_url=source_url,
            )

            # Step 2: Persist enrichment in one transaction.
            self.persistence_service.save_enrichment(
                db=db,
                article_id=article_id,
                result=result,
            )

            db.commit()

            return {
                "success": True,
                "article_id": str(article_id),
                "title": title,
                "enrichment": result,
            }

        except Exception:
            db.rollback()
            raise


article_processor = ArticleProcessor
