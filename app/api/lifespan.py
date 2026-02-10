from contextlib import asynccontextmanager
from typing import AsyncGenerator

from api_shared.services.redis.deps import redis_state
from api_shared.services.redis.lifespan import close_redis_pool, init_redis_pool
from fastapi import FastAPI

from app.core.broker import broker_manager
from app.core.telemetry import setup_opentelemetry, setup_prometheus, stop_opentelemetry
from app.db.utils import setup_db


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

    await broker_manager.startup_all()

    setup_db(app)

    setup_opentelemetry(app)

    # Initialize Redis connection pool
    redis_state.redis_pool = await init_redis_pool()

    setup_prometheus(app)
    app.middleware_stack = app.build_middleware_stack()

    yield

    await broker_manager.shutdown_all()

    await app.state.db_engine.dispose()

    await close_redis_pool(redis_state.redis_pool)

    stop_opentelemetry(app)
