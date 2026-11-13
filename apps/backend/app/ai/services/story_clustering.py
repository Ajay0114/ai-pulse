
from datetime import timedelta

from sqlalchemy.orm import Session

from app.models import Article, ArticleEmbedding


class StoryClusteringService:
    """
    Discovers potential story clusters using article embedding similarity.

    This service is read-only. It does not create StoryCluster records
    or modify Article records.
    """

    def __init__(
        self,
        similarity_threshold: float = 0.88,
        max_days_apart: int = 14,
        max_candidates: int = 10,
    ):
        self.similarity_threshold = similarity_threshold
        self.max_days_apart = max_days_apart
        self.max_candidates = max_candidates

    def find_candidates(self, db: Session) -> list[dict]:
        articles = (
            db.query(Article)
            .join(
                ArticleEmbedding,
                ArticleEmbedding.article_id == Article.id,
            )
            .filter(
                Article.relevance_status == "relevant",
                Article.processing_status == "processed",
            )
            .order_by(Article.published_at.desc())
            .all()
        )

        candidates = []
        seen_pairs = set()

        for article in articles:
            embedding = (
                db.query(ArticleEmbedding)
                .filter(
                    ArticleEmbedding.article_id == article.id,
                )
                .first()
            )

            if not embedding or not article.published_at:
                continue

            distance = ArticleEmbedding.embedding.cosine_distance(
                embedding.embedding
            )

            matches = (
                db.query(Article, ArticleEmbedding, distance.label("distance"))
                .join(
                    ArticleEmbedding,
                    ArticleEmbedding.article_id == Article.id,
                )
                .filter(
                    Article.id != article.id,
                    Article.relevance_status == "relevant",
                    Article.processing_status == "processed",
                    Article.published_at >= (
                        article.published_at
                        - timedelta(days=self.max_days_apart)
                    ),
                    Article.published_at <= (
                        article.published_at
                        + timedelta(days=self.max_days_apart)
                    ),
                )
                .order_by(distance.asc())
                .limit(self.max_candidates)
                .all()
            )

            for matched_article, _, match_distance in matches:
                similarity = 1 - float(match_distance)

                if similarity < self.similarity_threshold:
                    continue

                pair = tuple(sorted([str(article.id), str(matched_article.id)]))

                if pair in seen_pairs:
                    continue

                seen_pairs.add(pair)

                candidates.append(
                    {
                        "article_1_id": str(article.id),
                        "article_1_title": article.title,
                        "article_1_source_id": str(article.source_id),
                        "article_1_published_at": article.published_at.isoformat(),
                        "article_2_id": str(matched_article.id),
                        "article_2_title": matched_article.title,
                        "article_2_source_id": str(matched_article.source_id),
                        "article_2_published_at": (
                            matched_article.published_at.isoformat()
                        ),
                        "similarity": round(similarity, 4),
                    }
                )

        candidates.sort(
            key=lambda item: item["similarity"],
            reverse=True,
        )

        return candidates


story_clustering_service = StoryClusteringService()
