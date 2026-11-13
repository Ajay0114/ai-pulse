
import asyncio
from app.ai.services.article_relevance import ArticleRelevanceService


async def main():
    service = ArticleRelevanceService()

    test_articles = [
        {
            "title": "OpenAI releases a major new AI model",
            "description": (
                "The company announced a new frontier model "
                "with improved reasoning and coding capabilities."
            ),
            "source_name": "OpenAI Blog",
            "source_url": "https://openai.com/news/",
        },
        {
            "title": "Researchers demonstrate a major AI reasoning breakthrough",
            "description": (
                "Researchers introduce a novel technique that "
                "significantly improves reasoning performance."
            ),
            "source_name": "arXiv",
            "source_url": "https://arxiv.org/",
        },
        {
            "title": "Best weekend travel destinations",
            "description": (
                "A guide to popular travel destinations and hotels."
            ),
            "source_name": "Travel Blog",
            "source_url": "https://example.com/travel",
        },
    ]

    for index, article in enumerate(test_articles, start=1):
        print(f"\nTEST {index}: {article['title']}")

        try:
            result = await service.classify(**article)
            print(result)
        except Exception as exc:
            print(f"CLASSIFICATION FAILED: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
