
import hashlib
import logging
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urldefrag

import feedparser
import httpx
from bs4 import BeautifulSoup
from sqlalchemy import or_, select

from app.db.session import SessionLocal
from app.models.article import Article
from app.models.ingestion_log import IngestionLog
from app.models.source import Source

logger = logging.getLogger(__name__)

USER_AGENT = "AI-Pulse/0.1 (+https://localhost)"

# First fetch after a reset: only consider the previous 24 hours.
INITIAL_LOOKBACK = timedelta(hours=24)

# Subsequent fetches: overlap the last successful fetch by 2 hours.
FETCH_OVERLAP = timedelta(hours=2)

# Limit initial research candidates from each arXiv feed.
MAX_ARXIV_CANDIDATES_PER_FEED = 10

# Lightweight prefilter. The relevance classifier makes the final decision.
ARXIV_SIGNAL_TERMS = (
    "large language model",
    "language model",
    "reasoning",
    "agent",
    "agentic",
    "multimodal",
    "vision-language",
    "vision language",
    "alignment",
    "inference",
    "training",
    "fine-tuning",
    "finetuning",
    "benchmark",
    "evaluation",
    "retrieval",
    "rag",
    "diffusion",
    "robotics",
    "robot",
    "safety",
    "long context",
    "memory",
    "tool use",
    "synthetic data",
    "efficient attention",
    "model compression",
    "mixture of experts",
    "reinforcement learning",
    "computer use",
    "code generation",
    "world model",
)


def clean_html(value: str | None) -> str | None:
    if not value:
        return None

    soup = BeautifulSoup(value, "html.parser")
    text = soup.get_text(" ", strip=True)
    return text or None


def normalize_url(url: str | None) -> str | None:
    if not url:
        return None

    return urldefrag(url.strip())[0]


def parse_published_date(entry) -> datetime | None:
    date_value = entry.get("published") or entry.get("updated")

    if not date_value:
        return None

    try:
        parsed = parsedate_to_datetime(date_value)

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)

        return parsed.astimezone(timezone.utc)

    except (TypeError, ValueError, OverflowError):
        try:
            from dateutil import parser

            parsed = parser.parse(date_value)

            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)

            return parsed.astimezone(timezone.utc)

        except (TypeError, ValueError, OverflowError):
            return None


def extract_entry_content(entry) -> str | None:
    content_items = entry.get("content", [])

    if content_items:
        content = content_items[0].get("value")

        if content:
            return clean_html(content)

    return clean_html(
        entry.get("summary") or entry.get("description")
    )


def create_content_hash(title: str, url: str) -> str:
    value = f"{title.strip().lower()}|{url}"
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def is_arxiv_source(source: Source) -> bool:
    return "arxiv" in (source.name or "").lower()


def is_high_signal_arxiv_entry(entry) -> bool:
    title = entry.get("title") or ""
    description = (
        entry.get("summary")
        or entry.get("description")
        or ""
    )

    searchable_text = (
        f"{title} {description}"
    ).lower()

    return any(
        term in searchable_text
        for term in ARXIV_SIGNAL_TERMS
    )


def ingest_source(source_id) -> dict:
    started_at = datetime.now(timezone.utc)

    result = {
        "source": None,
        "discovered": 0,
        "created": 0,
        "skipped": 0,
        "status": "failed",
        "error": None,
        "fetch_window": None,
    }

    with SessionLocal() as db:
        source = db.get(Source, source_id)

        if not source:
            result["error"] = "Source not found"
            return result

        result["source"] = source.name

        # Capture the last successful fetch before making the request.
        # Failed fetches must never advance this watermark.
        last_successful_fetch = source.last_fetched_at

        if last_successful_fetch is None:
            fetch_cutoff = started_at - INITIAL_LOOKBACK
            result["fetch_window"] = "initial_24_hours"
        else:
            if last_successful_fetch.tzinfo is None:
                last_successful_fetch = last_successful_fetch.replace(
                    tzinfo=timezone.utc
                )

            fetch_cutoff = (
                last_successful_fetch.astimezone(timezone.utc)
                - FETCH_OVERLAP
            )
            result["fetch_window"] = "incremental_with_2h_overlap"

        log = IngestionLog(
            source_id=source.id,
            status="running",
            records_discovered=0,
            records_created=0,
            records_skipped=0,
            started_at=started_at,
        )

        db.add(log)
        db.flush()

        try:
            if not source.feed_url:
                raise ValueError("RSS feed URL is missing")

            response = httpx.get(
                source.feed_url,
                headers={"User-Agent": USER_AGENT},
                timeout=30,
                follow_redirects=True,
            )
            response.raise_for_status()

            parsed_feed = feedparser.parse(response.content)

            if not parsed_feed.entries:
                raise ValueError("RSS feed contains no entries")

            result["discovered"] = len(parsed_feed.entries)

            now = datetime.now(timezone.utc)
            eligible_entries = []

            # First filter by publication date.
            for entry in parsed_feed.entries:
                published_at = parse_published_date(entry)

                if (
                    published_at is None
                    or published_at < fetch_cutoff
                    or published_at > now
                ):
                    result["skipped"] += 1
                    continue

                title = (entry.get("title") or "").strip()
                original_url = entry.get("link")
                canonical_url = normalize_url(original_url)

                if not title or not original_url or not canonical_url:
                    result["skipped"] += 1
                    continue

                eligible_entries.append(
                    (published_at, entry, title, original_url, canonical_url)
                )

            # arXiv produces a high volume of routine papers.
            # Keep only high-signal candidates, with a per-feed cap.
            if is_arxiv_source(source):
                eligible_entries = [
                    item
                    for item in eligible_entries
                    if is_high_signal_arxiv_entry(item[1])
                ]

                eligible_entries.sort(
                    key=lambda item: item[0],
                    reverse=True,
                )

                selected_entries = eligible_entries[
                    :MAX_ARXIV_CANDIDATES_PER_FEED
                ]

                result["skipped"] += (
                    len(eligible_entries) - len(selected_entries)
                )

                eligible_entries = selected_entries

            # Insert eligible articles, checking duplicates globally
            # across all sources using canonical URL.
            for (
                published_at,
                entry,
                title,
                original_url,
                canonical_url,
            ) in eligible_entries:

                existing = db.scalar(
                    select(Article.id)
                    .where(Article.canonical_url == canonical_url)
                    .limit(1)
                )

                if existing:
                    result["skipped"] += 1
                    continue

                external_id = (
                    entry.get("id")
                    or entry.get("guid")
                    or original_url
                )
                external_id = str(external_id)[:500]

                description = clean_html(
                    entry.get("summary") or entry.get("description")
                )

                content = extract_entry_content(entry)

                article = Article(
                    source_id=source.id,
                    external_id=external_id,
                    title=title[:1000],
                    original_url=original_url,
                    canonical_url=canonical_url,
                    author=entry.get("author") or None,
                    description=description,
                    content=content,
                    content_type="article",
                    language=source.language or "en",
                    published_at=published_at,
                    discovered_at=datetime.now(timezone.utc),
                    content_hash=create_content_hash(
                        title,
                        canonical_url,
                    ),
                    processing_status="pending",
                )

                db.add(article)
                db.flush()

                result["created"] += 1

            completed_at = datetime.now(timezone.utc)

            # Advance the watermark only after a successful fetch.
            source.last_fetched_at = completed_at
            source.health_status = "healthy"
            source.consecutive_failures = 0
            source.next_fetch_at = completed_at + timedelta(
                minutes=source.poll_interval_minutes
            )

            log.status = "success"
            log.records_discovered = result["discovered"]
            log.records_created = result["created"]
            log.records_skipped = result["skipped"]
            log.completed_at = completed_at

            result["status"] = "success"

            db.commit()

        except Exception as exc:
            db.rollback()

            logger.exception(
                "RSS ingestion failed for source %s",
                source_id,
            )

            result["status"] = "failed"
            result["error"] = str(exc)

            # Reload source after rollback.
            source = db.get(Source, source_id)

            if source:
                now = datetime.now(timezone.utc)

                # Do not update last_fetched_at here.
                # It represents the last successful fetch.
                source.health_status = (
                    "blocked"
                    if isinstance(exc, httpx.HTTPStatusError)
                    and exc.response.status_code in (401, 403, 429)
                    else "failing"
                )

                source.consecutive_failures = (
                    source.consecutive_failures or 0
                ) + 1

                delay = min(
                    source.poll_interval_minutes
                    * 2 ** min(source.consecutive_failures, 6),
                    1440,
                )

                source.next_fetch_at = now + timedelta(minutes=delay)

            failure_log = IngestionLog(
                source_id=source_id,
                status="failed",
                records_discovered=result["discovered"],
                records_created=0,
                records_skipped=result["skipped"],
                error_message=str(exc)[:5000],
                started_at=started_at,
                completed_at=datetime.now(timezone.utc),
            )

            db.add(failure_log)
            db.commit()

    return result


def ingest_all_healthy_sources() -> dict:
    now = datetime.now(timezone.utc)

    with SessionLocal() as db:
        source_ids = db.scalars(
            select(Source.id).where(
                Source.is_active.is_(True),
                Source.source_type == "rss",
                Source.health_status.in_(["healthy", "failing"]),
                or_(
                    Source.next_fetch_at.is_(None),
                    Source.next_fetch_at <= now,
                ),
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
        result = ingest_source(source_id)

        summary["details"].append(result)
        summary["discovered"] += result["discovered"]
        summary["created"] += result["created"]
        summary["skipped"] += result["skipped"]

        if result["status"] == "success":
            summary["successful_sources"] += 1
        else:
            summary["failed_sources"] += 1

    return summary


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    summary = ingest_all_healthy_sources()

    print("\n========== RSS INGESTION SUMMARY ==========")
    print(f"Sources       : {summary['total_sources']}")
    print(f"Successful    : {summary['successful_sources']}")
    print(f"Failed        : {summary['failed_sources']}")
    print(f"Discovered    : {summary['discovered']}")
    print(f"Created       : {summary['created']}")
    print(f"Skipped       : {summary['skipped']}")
    print("===========================================")

    for item in summary["details"]:
        print(
            f"{item['source']}: "
            f"{item['status']} | "
            f"Window: {item['fetch_window']} | "
            f"Created: {item['created']} | "
            f"Skipped: {item['skipped']} | "
            f"Error: {item['error'] or 'None'}"
        )
