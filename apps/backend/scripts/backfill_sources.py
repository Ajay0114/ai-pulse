
import argparse
import logging

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.source import Source
from app.services.rss_ingestion import ingest_source

logger = logging.getLogger("ai-pulse-backfill")


def backfill_all_sources(lookback_days: int) -> dict:
    with SessionLocal() as db:
        source_ids = db.scalars(
            select(Source.id).where(
                Source.is_active.is_(True),
                Source.source_type == "rss",
            ).order_by(Source.priority.desc())
        ).all()

    summary = {
        "total_sources": len(source_ids),
        "successful_sources": 0,
        "failed_sources": 0,
        "discovered": 0,
        "created": 0,
        "skipped": 0,
        "details": [],
    }

    for source_id in source_ids:
        result = ingest_source(source_id, backfill_days=lookback_days)

        summary["details"].append(result)
        summary["discovered"] += result["discovered"]
        summary["created"] += result["created"]
        summary["skipped"] += result["skipped"]

        if result["status"] == "success":
            summary["successful_sources"] += 1
        else:
            summary["failed_sources"] += 1

        logger.info(
            "%s | %s | Created: %s | Skipped: %s | Error: %s",
            result["source"],
            result["status"],
            result["created"],
            result["skipped"],
            result["error"] or "None",
        )

    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "One-time historical backfill for AI Pulse RSS sources. "
            "Safe to re-run: articles are deduplicated by canonical URL, "
            "so nothing already stored is fetched twice. Each source's "
            "actual backfill depth is limited by how far back its own "
            "feed currently reaches - most blog feeds only expose their "
            "most recent items, and arXiv's feed is a same-day "
            "announcement list regardless of the requested window. "
            "This only fetches and stores articles; it does not call "
            "the LLM, so it has no OpenRouter cost."
        )
    )

    parser.add_argument(
        "--days",
        type=int,
        default=365,
        help="How many days back to accept entries from (default 365).",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    summary = backfill_all_sources(lookback_days=args.days)

    print("\n========== BACKFILL SUMMARY ==========")
    print(f"Lookback days        : {args.days}")
    print(f"Sources              : {summary['total_sources']}")
    print(f"Successful           : {summary['successful_sources']}")
    print(f"Failed               : {summary['failed_sources']}")
    print(f"Discovered           : {summary['discovered']}")
    print(f"Created              : {summary['created']}")
    print(f"Skipped              : {summary['skipped']}")
    print("=======================================")

    for item in summary["details"]:
        print(
            f"{item['source']}: "
            f"{item['status']} | "
            f"Window: {item['fetch_window']} | "
            f"Created: {item['created']} | "
            f"Skipped: {item['skipped']} | "
            f"Error: {item['error'] or 'None'}"
        )
