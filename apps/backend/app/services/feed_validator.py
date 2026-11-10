
from datetime import datetime, timedelta, timezone

import feedparser
import httpx
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.source import Source


USER_AGENT = "AI-Pulse/0.1 (+https://localhost)"


def validate_feed(source: Source) -> dict:
    if not source.feed_url:
        return {
            "success": False,
            "error": "Feed URL is missing",
            "health_status": "failing",
        }

    try:
        response = httpx.get(
            source.feed_url,
            headers={"User-Agent": USER_AGENT},
            timeout=20,
            follow_redirects=True,
        )

        response.raise_for_status()

        parsed = feedparser.parse(response.content)

        if parsed.bozo and not parsed.entries:
            return {
                "success": False,
                "error": str(parsed.bozo_exception),
                "health_status": "failing",
            }

        if not parsed.entries:
            return {
                "success": False,
                "error": "Feed contains no entries or is not a valid feed",
                "health_status": "failing",
            }

        return {
            "success": True,
            "feed_title": parsed.feed.get("title"),
            "entry_count": len(parsed.entries),
            "latest_entry": parsed.entries[0].get("title"),
            "status_code": response.status_code,
        }

    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code

        return {
            "success": False,
            "error": f"HTTP {status_code}",
            "health_status": (
                "blocked"
                if status_code in (401, 403, 429)
                else "failing"
            ),
        }

    except httpx.RequestError as exc:
        return {
            "success": False,
            "error": str(exc),
            "health_status": "failing",
        }

    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "health_status": "failing",
        }


def validate_all_sources() -> dict:
    results = {
        "total": 0,
        "healthy": 0,
        "blocked": 0,
        "failed": 0,
        "details": [],
    }

    with SessionLocal() as db:
        sources = db.scalars(
            select(Source).where(
                Source.is_active.is_(True),
                Source.source_type == "rss",
            )
        ).all()

        for source in sources:
            results["total"] += 1

            print(f"Checking: {source.name}")

            result = validate_feed(source)
            now = datetime.now(timezone.utc)

            source.last_fetched_at = now

            if result["success"]:
                source.health_status = "healthy"
                source.consecutive_failures = 0
                source.next_fetch_at = now + timedelta(
                    minutes=source.poll_interval_minutes
                )
                results["healthy"] += 1

            else:
                health_status = result.get(
                    "health_status", "failing"
                )

                source.health_status = health_status
                source.consecutive_failures += 1

                # Longer backoff for blocked sources.
                if health_status == "blocked":
                    delay_minutes = 1440
                    results["blocked"] += 1
                else:
                    delay_minutes = min(
                        source.poll_interval_minutes
                        * 2 ** min(source.consecutive_failures, 6),
                        1440,
                    )
                    results["failed"] += 1

                source.next_fetch_at = now + timedelta(
                    minutes=delay_minutes
                )

            results["details"].append({
                "source": source.name,
                **result,
            })

            status_label = (
                "HEALTHY" if result["success"]
                else source.health_status.upper()
            )

            print(
                f"  {status_label}: "
                f"{result.get('feed_title') or result.get('error')}"
            )

        db.commit()

    return results


if __name__ == "__main__":
    summary = validate_all_sources()

    print("\n========== FEED VALIDATION SUMMARY ==========")
    print(f"Total feeds : {summary['total']}")
    print(f"Healthy     : {summary['healthy']}")
    print(f"Blocked     : {summary['blocked']}")
    print(f"Failed      : {summary['failed']}")
    print("=============================================")
