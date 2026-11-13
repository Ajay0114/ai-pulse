
import asyncio
import logging

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Article, ArticleEmbedding
from app.ai.services.article_embedding import ArticleEmbeddingService


BATCH_SIZE = 10
REQUEST_DELAY_SECONDS = 1

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("ai-pulse-embeddings")


async def main():
    service = ArticleEmbeddingService()

    # Find relevant articles without an embedding for this model.
    with SessionLocal() as db:
        existing_ids = (
            select(ArticleEmbedding.article_id)
            .where(
                ArticleEmbedding.model_name == service.model_name
            )
        )

        article_ids = db.scalars(
            select(Article.id)
            .where(
                Article.relevance_status == "relevant",
                Article.processing_status == "processed",
                ~Article.id.in_(existing_ids),
            )
            .order_by(Article.published_at.asc())
        ).all()

    total = len(article_ids)

    logger.info("Embedding model: %s", service.model_name)
    logger.info("Articles requiring embeddings: %s", total)

    successful = 0
    skipped = 0
    failed = 0

    for batch_start in range(0, total, BATCH_SIZE):
        batch = article_ids[batch_start:batch_start + BATCH_SIZE]

        logger.info(
            "Batch %s | Articles %s-%s of %s",
            batch_start // BATCH_SIZE + 1,
            batch_start + 1,
            batch_start + len(batch),
            total,
        )

        for article_id in batch:
            with SessionLocal() as db:
                try:
                    article = db.get(Article, article_id)

                    if not article:
                        skipped += 1
                        continue

                    created = await service.create_for_article(
                        db=db,
                        article=article,
                    )

                    db.commit()

                    if created:
                        successful += 1
                        logger.info(
                            "EMBEDDED | %s",
                            article.title,
                        )
                    else:
                        skipped += 1
                        logger.info(
                            "SKIPPED | Existing embedding | %s",
                            article.title,
                        )

                except Exception:
                    db.rollback()
                    failed += 1
                    logger.exception(
                        "Embedding failed | Article ID: %s",
                        article_id,
                    )

            await asyncio.sleep(REQUEST_DELAY_SECONDS)

    logger.info("========== EMBEDDING SUMMARY ==========")
    logger.info("Total selected: %s", total)
    logger.info("Created: %s", successful)
    logger.info("Skipped: %s", skipped)
    logger.info("Failed: %s", failed)
    logger.info("========================================")


if __name__ == "__main__":
    asyncio.run(main())
