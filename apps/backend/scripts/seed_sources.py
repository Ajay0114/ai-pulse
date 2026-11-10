import json
from pathlib import Path

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.source import Source


CATALOG_PATH = Path(__file__).resolve().parents[1] / "data" / "source_catalog.json"


def seed_sources():
    with CATALOG_PATH.open("r", encoding="utf-8") as file:
        catalog = json.load(file)

    created = 0
    skipped = 0
    failed = 0

    with SessionLocal() as db:
        for item in catalog:
            try:
                existing = db.scalar(
                    select(Source).where(
                        Source.name == item["name"],
                        Source.source_type == item["source_type"],
                    )
                )

                if existing:
                    skipped += 1
                    print(f"SKIPPED: {item['name']}")
                    continue

                data = item.copy()
                data["metadata_"] = data.pop("metadata", {})

                source = Source(**data)

                db.add(source)
                db.commit()

                created += 1
                print(f"CREATED: {item['name']}")

            except Exception as exc:
                db.rollback()
                failed += 1
                print(f"FAILED: {item.get('name', 'Unknown')} - {exc}")

    print("\n========== SOURCE IMPORT SUMMARY ==========")
    print(f"Total catalog entries : {len(catalog)}")
    print(f"Created               : {created}")
    print(f"Skipped               : {skipped}")
    print(f"Failed                : {failed}")
    print("===========================================")


if __name__ == "__main__":
    seed_sources()