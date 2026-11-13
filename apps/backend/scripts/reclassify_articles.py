
import argparse
import asyncio
import json
import logging
from collections import Counter
from pathlib import Path
from typing import Any

from sqlalchemy import select

from app.ai.services.article_relevance import ArticleRelevanceService
from app.ai.services.article_persistence import ArticlePersistenceService
from app.db.session import SessionLocal
from app.models import Article


BATCH_SIZE = 25
REQUEST_DELAY_SECONDS = 2

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BASE_DIR / "data" / "reclassification_errors.jsonl"

logger = logging.getLogger("ai-pulse-reclassification")


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def get_article_ids():
    with SessionLocal() as db:
        return db.scalars(
            select(Article.id).order_by(Article.published_at.asc())
        ).all()


def get_article_data(article_id):
    with SessionLocal() as db:
        article = db.query(Article).filter(
            Article.id == article_id
        ).first()

        if not article:
            return None

        return {
            "id": article.id,
            "title": article.title,
            "description": article.description or article.content or "",
            "source_name": article.source.name if article.source else "",
            "source_url": article.original_url or "",
        }


def record_error(article_id, error):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps({
            "article_id": str(article_id),
            "error": str(error),
        }) + "\n")


async def reclassify(dry_run: bool):
    classifier = ArticleRelevanceService()
    persistence = ArticlePersistenceService()

    article_ids = get_article_ids()

    total = len(article_ids)
    stats = Counter()
    failures = []

    logger.info("Articles found: %s", total)
    logger.info("Mode: %s", "DRY RUN" if dry_run else "LIVE")

    for batch_start in range(0, total, BATCH_SIZE):
        batch = article_ids[batch_start:batch_start + BATCH_SIZE]

        logger.info(
            "Starting batch %s | Articles %s-%s of %s",
            batch_start // BATCH_SIZE + 1,
            batch_start + 1,
            batch_start + len(batch),
            total,
        )

        for article_id in batch:
            data = get_article_data(article_id)

            if not data:
                stats["not_found"] += 1
                continue

            try:
                result: dict[str, Any] = await classifier.classify(
                    title=data["title"],
                    description=data["description"],
                    source_name=data["source_name"],
                    source_url=data["source_url"],
                )

                feed_type = result["feed_type"]
                relevance_status = result["relevance_status"]

                if dry_run:
                    stats[f"preview_{feed_type}"] += 1

                    logger.info(
                        "PREVIEW | %s | %s | Score: %s | %s",
                        feed_type.upper(),
                        data["title"],
                        result["relevance_score"],
                        result["importance_reason"],
                    )

                else:
                    with SessionLocal() as db:
                        article = db.get(Article, article_id)

                        if not article:
                            raise ValueError("Article disappeared before update")

                        persistence.save_relevance(
                            db=db,
                            article_id=article_id,
                            result=result,
                        )

                        if relevance_status == "irrelevant":
                            article.processing_status = "skipped"

                        elif article.processing_status != "processed":
                            article.processing_status = "pending"

                        db.commit()

                    stats[feed_type] += 1

                    logger.info(
                        "UPDATED | %s | %s | Score: %s",
                        feed_type.upper(),
                        data["title"],
                        result["relevance_score"],
                    )

            except Exception as exc:
                stats["failed"] += 1
                failures.append(str(article_id))
                record_error(article_id, exc)

                logger.exception(
                    "Failed article %s: %s",
                    article_id,
                    exc,
                )

            await asyncio.sleep(REQUEST_DELAY_SECONDS)

    logger.info("========== RECLASSIFICATION SUMMARY ==========")
    logger.info("Total articles: %s", total)

    for key, value in sorted(stats.items()):
        logger.info("%s: %s", key, value)

    logger.info("Failed article IDs: %s", failures)
    logger.info("===============================================")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Reclassify AI Pulse articles without enrichment."
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Persist classification results. Without this flag, runs in dry-run mode.",
    )

    args = parser.parse_args()

    configure_logging()

    asyncio.run(reclassify(dry_run=not args.apply))
