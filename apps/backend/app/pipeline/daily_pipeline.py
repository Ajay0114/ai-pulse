
import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Article
from app.services.rss_ingestion import ingest_all_healthy_sources
from app.ai.services.article_processor import ArticleProcessor

logger = logging.getLogger("ai-pulse-daily-pipeline")

BATCH_SIZE = 500
LOOKBACK_DAYS = 365


async def run_daily_pipeline():
    started_at = datetime.now(timezone.utc)

    summary = {
        "ingestion": None,
        "enrichment_queued": 0,
        "enrichment_success": 0,
        "enrichment_failed": 0,
    }

    logger.info("========== AI PULSE DAILY PIPELINE ==========")

    # STEP 1: RSS ingestion
    logger.info("Starting RSS ingestion...")

    ingestion_result = ingest_all_healthy_sources()
    summary["ingestion"] = ingestion_result

    logger.info(
        "RSS ingestion completed | Created: %s | Failed sources: %s",
        ingestion_result["created"],
        ingestion_result["failed_sources"],
    )

    # STEP 2: Find pending articles within the rolling 365-day window.
    cutoff = datetime.now(timezone.utc) - __import__("datetime").timedelta(
        days=LOOKBACK_DAYS
    )

    with SessionLocal() as db:
        article_ids = db.scalars(
            select(Article.id)
            .where(
                Article.processing_status == "pending",
                Article.published_at >= cutoff,
                Article.published_at <= datetime.now(timezone.utc),
            )
            .order_by(Article.published_at.asc())
            .limit(BATCH_SIZE)
        ).all()

    summary["enrichment_queued"] = len(article_ids)

    logger.info("Articles queued for enrichment: %s", len(article_ids))

    # STEP 3: AI enrichment
    processor = ArticleProcessor()

    for index, article_id in enumerate(article_ids, start=1):
        db = SessionLocal()

        try:
            result = await processor.process(
                db=db,
                article_id=article_id,
            )

            summary["enrichment_success"] += 1

            logger.info(
                "[%s/%s] SUCCESS | %s",
                index,
                len(article_ids),
                result["title"],
            )

        except Exception:
            summary["enrichment_failed"] += 1

            logger.exception(
                "[%s/%s] FAILED | Article ID: %s",
                index,
                len(article_ids),
                article_id,
            )

            try:
                article = db.get(Article, article_id)

                if article and article.processing_status != "processed":
                    article.processing_status = "failed"
                    db.commit()

            except Exception:
                db.rollback()
                logger.exception("Could not update failed article status")

        finally:
            db.close()

    completed_at = datetime.now(timezone.utc)

    logger.info("========== DAILY PIPELINE SUMMARY ==========")
    logger.info("RSS articles created : %s", ingestion_result["created"])
    logger.info("Enrichment queued    : %s", summary["enrichment_queued"])
    logger.info("Enrichment successful: %s", summary["enrichment_success"])
    logger.info("Enrichment failed    : %s", summary["enrichment_failed"])
    logger.info("Started              : %s", started_at)
    logger.info("Completed            : %s", completed_at)
    logger.info("=============================================")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    asyncio.run(run_daily_pipeline())
