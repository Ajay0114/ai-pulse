from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health
from app.core.config import settings
from app.api.routes import sources
from app.api.routes import articles


app = FastAPI(
    title=settings.APP_NAME,
    description="Global AI News Intelligence Platform API",
    version="0.1.0",
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(sources.router, prefix="/api/v1", tags=["Sources"])

app.include_router(
    articles.router,
    prefix="/api/v1/articles",
    tags=["Articles"],
)


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to AI Pulse API",
        "version": "0.1.0",
        "docs": "/docs",
    }