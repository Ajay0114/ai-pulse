
from sqlalchemy.orm import Session

from app.ai.providers.openrouter import OpenRouterProvider
from app.core.config import settings
from app.models import Article, ArticleEmbedding


class ArticleEmbeddingService:
    """Generate and persist semantic embeddings for AI Pulse articles."""

    def __init__(self):
        self.provider = OpenRouterProvider()
        self.model_name = settings.EMBEDDING_MODEL

    async def generate_embedding(self, article: Article) -> list[float]:
        """Generate an embedding from the article's content."""

        parts = [
            f"Title: {article.title}",
            f"Description: {article.description or ''}",
            f"Content: {article.content or ''}",
        ]

        text = "\n\n".join(parts).strip()

        if not article.title:
            raise ValueError("Article title is required for embedding.")

        return await self.provider.embed(text)

    async def create_for_article(
        self,
        db: Session,
        article: Article,
    ) -> bool:
        """
        Generate and store an embedding if one does not already exist.

        Returns True if a new embedding was created, otherwise False.
        The caller controls the database transaction.
        """

        existing = db.query(ArticleEmbedding).filter(
            ArticleEmbedding.article_id == article.id,
            ArticleEmbedding.model_name == self.model_name,
        ).first()

        if existing:
            return False

        vector = await self.generate_embedding(article)

        if len(vector) != 1536:
            raise ValueError(
                f"Expected 1536 dimensions, received {len(vector)}."
            )

        embedding = ArticleEmbedding(
            article_id=article.id,
            model_name=self.model_name,
            embedding=vector,
        )

        db.add(embedding)
        db.flush()

        return True


article_embedding_service = ArticleEmbeddingService()
