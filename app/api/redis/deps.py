from typing import Annotated, AsyncGenerator

from fastapi import FastAPI
from redis.asyncio import Redis
from starlette.requests import Request
from taskiq import TaskiqDepends


async def get_redis_pool(
    request: Annotated[Request, TaskiqDepends()],
) -> AsyncGenerator[Redis, None]:
    """
    Returns connection pool.

    You can use it like this:

    >>> from redis.asyncio import ConnectionPool, Redis
    >>>
    >>> async def handler(redis_pool: ConnectionPool = Depends(get_redis_pool)):
    >>>     async with Redis(connection_pool=redis_pool) as redis:
    >>>         await redis.get('key')

    Pool is used, so you don't acquire connection till the end of the handler.

    Args:
        request: current request.

    Returns:
        Redis connection pool.
    """
    app: FastAPI = request.app

    return app.state.redis_pool
