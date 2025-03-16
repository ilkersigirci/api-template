from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.core.telemetry import setup_opentelemetry, stop_opentelemetry


@asynccontextmanager
async def lifespan_setup(
    app: FastAPI,
) -> AsyncGenerator[None, None]:  # pragma: no cover
    """
    Actions to run on application startup.

    This function uses fastAPI app to store data
    in the state, such as db_engine.

    app: the fastAPI application.
    return: function that actually performs actions.
    """

    app.middleware_stack = None
    # _setup_db(app)
    setup_opentelemetry(app)
    app.middleware_stack = app.build_middleware_stack()

    yield
    # await app.state.db_engine.dispose()

    stop_opentelemetry(app)
