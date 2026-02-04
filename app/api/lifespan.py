from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.api.redis.utils import init_redis, shutdown_redis
from app.core.broker import broker, ml_broker
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

    if not broker.is_worker_process:
        await broker.startup()

    if not ml_broker.is_worker_process:
        await ml_broker.startup()

    setup_db(app)

    setup_opentelemetry(app)
    init_redis(app)
    setup_prometheus(app)
    app.middleware_stack = app.build_middleware_stack()

    yield

    if not broker.is_worker_process:
        await broker.shutdown()

    if not ml_broker.is_worker_process:
        await ml_broker.shutdown()

    await app.state.db_engine.dispose()

    await shutdown_redis(app)
    stop_opentelemetry(app)
