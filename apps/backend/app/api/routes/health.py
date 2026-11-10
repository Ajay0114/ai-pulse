from datetime import datetime, timezone

import redis
from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import engine
from app.core.config import settings


router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    services = {}

    # PostgreSQL health check
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        services["postgresql"] = "healthy"

    except SQLAlchemyError:
        services["postgresql"] = "unhealthy"

    # Redis health check
    try:
        redis_client = redis.Redis.from_url(
            settings.REDIS_URL,
            socket_connect_timeout=3,
            socket_timeout=3,
            decode_responses=True,
        )

        redis_client.ping()
        services["redis"] = "healthy"
        redis_client.close()

    except redis.RedisError:
        services["redis"] = "unhealthy"

    overall_status = (
        "healthy"
        if all(status == "healthy" for status in services.values())
        else "degraded"
    )

    return {
        "status": overall_status,
        "service": settings.APP_NAME,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dependencies": services,
    }