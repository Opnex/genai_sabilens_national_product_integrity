"""
api/app.py
----------
FastAPI application factory for the SabiLens NAFDAC RAG service.

This file only wires the router into the app and sets metadata.
All routing logic lives in api/routes.py.

Start the server:
    uvicorn api.app:app --host 0.0.0.0 --port 8000

Interactive docs:
    http://localhost:8000/docs   (Swagger UI)
    http://localhost:8000/redoc  (ReDoc)
"""

from fastapi import FastAPI
from config.settings import settings
from api.routes import router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""

    app = FastAPI(
        title       = settings.API_TITLE,
        version     = settings.API_VERSION,
        description = (
            "SabiLens A3 Regulatory RAG API — "
            "NAFDAC food product verification for counterfeit detection in Nigeria."
        ),
        docs_url    = "/docs",
        redoc_url   = "/redoc",
    )

    app.include_router(router)

    @app.get("/", tags=["Root"])
    async def root():
        """Root ping — confirms the service is running."""
        return {
            "service": settings.API_TITLE,
            "version": settings.API_VERSION,
            "status" : "running",
            "docs"   : "/docs",
        }

    return app


app = create_app()