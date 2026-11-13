
import asyncio
import json

from app.ai.services.article_relevance import ArticleRelevanceService
from app.db.session import SessionLocal
from app.models.article import Article


ARTICLE_IDS = [
    # Main feed samples
    "85a011af-2287-461e-9e7a-9f1655a1daec",
    "27011586-debc-42f1-876f-5f6d19ebb8b0",
    "d89ff6a0-cc5c-4a87-87ec-b335194ba4c0",
    "5a9655aa-2243-406b-b134-f7801b4d01f0",
    "fa848166-1dd5-4540-84ef-fff7633c98c3",
    "e5ce6b8b-1dee-4ed4-a1ac-9c0ba5a98545",

    # Research samples
    "10a7659f-fbe2-4a57-968b-e4f42be6c5b3",
    "3457fe11-fa1f-4b25-9cb2-e27e78618e3c",
    "1f6b9c79-f274-4016-9ec7-dfb98ca86fc4",
    "1a6c6065-db58-4627-9e1e-6687b118bec7",
    "f79c13ee-3455-4a52-9c7b-d44b7e10706e",
    "791fcecc-5c4e-432c-b6fc-6edfd2d90c9b",
]


def load_articles():
    with SessionLocal() as db:
        articles = (
            db.query(Article)
            .filter(Article.id.in_(ARTICLE_IDS))
            .all()
        )

        article_data = []

        for article in articles:
            article_data.append({
                "id": str(article.id),
                "title": article.title,
                "description": (
                    article.description
                    or article.content
                    or ""
                ),
                "source": (
                    article.source.name
                    if article.source
                    else ""
                ),
                "url": article.original_url or "",
                "old_score": article.relevance_score,
                "old_feed": article.feed_type,
                "old_status": article.relevance_status,
            })

        return article_data


async def evaluate():
    articles = load_articles()

    if not articles:
        print("No evaluation articles found.")
        return

    if len(articles) != len(ARTICLE_IDS):
        print(
            f"WARNING: Expected {len(ARTICLE_IDS)} articles, "
            f"found {len(articles)}."
        )

    classifier = ArticleRelevanceService()

    results = []

    print(f"\nEvaluating {len(articles)} articles...\n")

    for index, article in enumerate(articles, start=1):
        print(
            f"[{index}/{len(articles)}] "
            f"Classifying: {article['title']}"
        )

        try:
            new_result = await classifier.classify(
                title=article["title"],
                description=article["description"],
                source_name=article["source"],
                source_url=article["url"],
            )

            result = {
                "id": article["id"],
                "title": article["title"],
                "source": article["source"],
                "old": {
                    "score": article["old_score"],
                    "feed": article["old_feed"],
                    "status": article["old_status"],
                },
                "new": new_result,
                "changed": (
                    article["old_feed"] != new_result["feed_type"]
                    or article["old_status"]
                    != new_result["relevance_status"]
                ),
                "error": None,
            }

        except Exception as exc:
            result = {
                "id": article["id"],
                "title": article["title"],
                "source": article["source"],
                "old": {
                    "score": article["old_score"],
                    "feed": article["old_feed"],
                    "status": article["old_status"],
                },
                "new": None,
                "changed": None,
                "error": str(exc),
            }

        results.append(result)

        if result["new"]:
            print(
                f"  Old: {result['old']['score']} / "
                f"{result['old']['feed']}"
            )
            print(
                f"  New: {result['new']['relevance_score']} / "
                f"{result['new']['feed_type']}"
            )
        else:
            print(f"  ERROR: {result['error']}")

        print()

    successful = [
        item for item in results
        if item["new"] is not None
    ]

    print("\n========== EVALUATION SUMMARY ==========")
    print(f"Total articles : {len(results)}")
    print(f"Successful     : {len(successful)}")
    print(f"Failed         : {len(results) - len(successful)}")
    print(
        f"Changed feed/status: "
        f"{sum(item['changed'] is True for item in successful)}"
    )

    print("\nNEW FEED DISTRIBUTION:")

    distribution = {}

    for item in successful:
        feed = item["new"]["feed_type"]
        distribution[feed] = distribution.get(feed, 0) + 1

    print(json.dumps(distribution, indent=2))

    print("\nNEW CLASSIFICATIONS:")
    print(json.dumps(results, indent=2, ensure_ascii=False))

    with open(
        "relevance_evaluation_results.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        "\nResults saved to "
        "relevance_evaluation_results.json"
    )


if __name__ == "__main__":
    asyncio.run(evaluate())
