
import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.ai.services.article_processor import ArticleProcessor
from app.db.session import SessionLocal
from app.models import Article

# Maximum articles processed in one execution.
BATCH_SIZE = 500

# Rolling publication-date window.
LOOKBACK_DAYS = 365

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("ai-pulse-bulk-processor")


async def process_all_articles():
    processor = ArticleProcessor()

    started_at = datetime.now(timezone.utc)
    cutoff = started_at - timedelta(days=LOOKBACK_DAYS)

    stats = {
        "total": 0,
        "success": 0,
        "failed": 0,
    }

    # Select only pending articles from the last 365 days.
    with SessionLocal() as db:
        article_ids = db.scalars(
            select(Article.id)
            .where(
                Article.processing_status == "pending",
                Article.published_at >= cutoff,
                Article.published_at <= started_at,
            )
            .order_by(Article.published_at.asc())
            .limit(BATCH_SIZE)
        ).all()

    stats["total"] = len(article_ids)

    logger.info("========== AI ENRICHMENT BATCH ==========")
    logger.info("Started       : %s", started_at)
    logger.info("Lookback days : %s", LOOKBACK_DAYS)
    logger.info("Date cutoff   : %s", cutoff)
    logger.info("Batch limit   : %s", BATCH_SIZE)
    logger.info("Articles queued: %s", stats["total"])

    if not article_ids:
        logger.info("No eligible pending articles found.")
        return

    for index, article_id in enumerate(article_ids, start=1):
        db = SessionLocal()

        try:
            result = await processor.process(
                db=db,
                article_id=article_id,
            )

            stats["success"] += 1

            logger.info(
                "[%s/%s] SUCCESS | %s",
                index,
                stats["total"],
                result["title"],
            )

        except Exception as exc:
            stats["failed"] += 1

            logger.exception(
                "[%s/%s] FAILED | Article ID: %s | Error: %s",
                index,
                stats["total"],
                article_id,
                str(exc),
            )

            # ArticleProcessor rolls back the failed transaction.
            # Mark the article as failed separately.
            try:
                article = db.get(Article, article_id)

                if article and article.processing_status != "processed":
                    article.processing_status = "failed"
                    db.commit()

            except Exception:
                db.rollback()
                logger.exception(
                    "Could not update failed status for %s",
                    article_id,
                )

        finally:
            db.close()

        if index % 10 == 0 or index == stats["total"]:
            logger.info(
                "PROGRESS: %s/%s | Successful: %s | Failed: %s",
                index,
                stats["total"],
                stats["success"],
                stats["failed"],
            )

    completed_at = datetime.now(timezone.utc)

    logger.info("========== BATCH SUMMARY ==========")
    logger.info("Total queued : %s", stats["total"])
    logger.info("Successful   : %s", stats["success"])
    logger.info("Failed       : %s", stats["failed"])
    logger.info("Started      : %s", started_at)
    logger.info("Completed    : %s", completed_at)
    logger.info("===================================")


if __name__ == "__main__":
    asyncio.run(process_all_articles())
