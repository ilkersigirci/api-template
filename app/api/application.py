from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.lifespan import lifespan_setup
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.log import configure_logging

APP_ROOT = Path(__file__).parent.parent


def get_app() -> FastAPI:
    """Get FastAPI application."""
    configure_logging()

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="0.0.1",
        docs_url=None,
        redoc_url=None,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan_setup,
        default_response_class=JSONResponse,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.API_V1_STR)

    # Adds static directory. This directory is used to access swagger files.
    app.mount("/static", StaticFiles(directory=APP_ROOT / "static"), name="static")

    return app
