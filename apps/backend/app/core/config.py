from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "AI Pulse API"
    APP_ENV: str = "development"
    DEBUG: bool = True

    API_V1_PREFIX: str = "/api/v1"
    FRONTEND_URL: str = "http://localhost:3000"

    DATABASE_URL: str
    DB_ECHO: bool = False

    REDIS_URL: str = "redis://localhost:6380/0"
    LLM_PROVIDER: str = "openrouter"
    OPENROUTER_API_KEY: str = ""
    LLM_MODEL: str = "openai/gpt-4.1-mini"
    EMBEDDING_MODEL: str = "openai/text-embedding-3-small"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()