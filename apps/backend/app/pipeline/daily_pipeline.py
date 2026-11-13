
import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, or_, select

from app.db.session import SessionLocal
from app.models import Article
from app.services.rss_ingestion import ingest_all_healthy_sources
from app.ai.services.article_processor import ArticleProcessor


logger = logging.getLogger("ai-pulse-daily-pipeline")

BATCH_SIZE = 50
LOOKBACK_DAYS = 365
MAX_ATTEMPTS = 3
REQUEST_DELAY_SECONDS = 2

RETRY_DELAYS = {
    1: timedelta(minutes=5),
    2: timedelta(minutes=30),
}


async def run_daily_pipeline():

    started_at = datetime.now(timezone.utc)

    summary = {
        "ingestion": None,
        "articles_queued": 0,
        "classification_relevant": 0,
        "classification_irrelevant": 0,
        "enrichment_success": 0,
        "processing_failed": 0,
        "retry_scheduled": 0,
        "max_attempts_reached": 0,
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

    # STEP 2: Find pending articles and eligible retries.
    now = datetime.now(timezone.utc)

    cutoff = now - timedelta(days=LOOKBACK_DAYS)

    retry_eligible = or_(
        Article.processing_status == "pending",

        and_(
            Article.processing_status == "failed",
            Article.processing_attempts > 0,
            Article.processing_attempts < MAX_ATTEMPTS,
            Article.next_retry_at <= now,
        ),
    )

    with SessionLocal() as db:

        article_ids = db.scalars(
            select(Article.id)
            .where(
                retry_eligible,
                Article.published_at >= cutoff,
                Article.published_at <= now,
            )
            .order_by(Article.published_at.asc())
            .limit(BATCH_SIZE)
        ).all()

    summary["articles_queued"] = len(article_ids)

    logger.info(
        "Articles queued for classification/enrichment: %s",
        len(article_ids),
    )

    # STEP 3: Process articles.
    processor = ArticleProcessor()

    for index, article_id in enumerate(article_ids, start=1):

        db = SessionLocal()

        try:

            result = await processor.process(
                db=db,
                article_id=article_id,
            )

            if result["processing_status"] == "skipped":

                summary["classification_irrelevant"] += 1

                logger.info(
                    "[%s/%s] EXCLUDED | %s",
                    index,
                    len(article_ids),
                    result["title"],
                )

            else:

                summary["classification_relevant"] += 1
                summary["enrichment_success"] += 1

                logger.info(
                    "[%s/%s] PROCESSED | %s",
                    index,
                    len(article_ids),
                    result["title"],
                )

        except Exception as exc:

            summary["processing_failed"] += 1

            logger.exception(
                "[%s/%s] FAILED | Article ID: %s",
                index,
                len(article_ids),
                article_id,
            )

            try:

                db.rollback()

                article = db.get(Article, article_id)

                if article:

                    attempts = (article.processing_attempts or 0) + 1

                    article.processing_attempts = attempts
                    article.last_processing_error = str(exc)[:4000]
                    article.processing_status = "failed"

                    if attempts < MAX_ATTEMPTS:

                        retry_delay = RETRY_DELAYS[attempts]

                        article.next_retry_at = (
                            datetime.now(timezone.utc) + retry_delay
                        )

                        summary["retry_scheduled"] += 1

                        logger.warning(
                            "Retry scheduled | Article: %s | Attempt: %s "
                            "| Delay: %s",
                            article_id,
                            attempts,
                            retry_delay,
                        )

                    else:

                        article.next_retry_at = None

                        summary["max_attempts_reached"] += 1

                        logger.error(
                            "Maximum attempts reached | Article: %s",
                            article_id,
                        )

                    db.commit()

            except Exception:

                db.rollback()

                logger.exception(
                    "Could not update retry information for article: %s",
                    article_id,
                )

        finally:

            db.close()

        # Avoid sending requests too rapidly to OpenRouter.
        if index < len(article_ids):
            await asyncio.sleep(REQUEST_DELAY_SECONDS)

    # STEP 4: Pipeline summary.
    completed_at = datetime.now(timezone.utc)

    logger.info("========== DAILY PIPELINE SUMMARY ==========")
    logger.info("RSS articles created       : %s", ingestion_result["created"])
    logger.info("Articles queued            : %s", summary["articles_queued"])
    logger.info(
        "Relevant articles          : %s",
        summary["classification_relevant"],
    )
    logger.info(
        "Irrelevant articles        : %s",
        summary["classification_irrelevant"],
    )
    logger.info("Enrichment successful      : %s", summary["enrichment_success"])
    logger.info("Processing failed          : %s", summary["processing_failed"])
    logger.info("Retries scheduled          : %s", summary["retry_scheduled"])
    logger.info(
        "Maximum attempts reached   : %s",
        summary["max_attempts_reached"],
    )
    logger.info("Started                    : %s", started_at)
    logger.info("Completed                  : %s", completed_at)
    logger.info("=============================================")

    return summary


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    asyncio.run(run_daily_pipeline())
