from loguru import logger
from redis.asyncio import ConnectionPool, Redis
from taskiq import TaskiqDepends

from app.api.redis.deps import get_redis_pool
from app.worker.broker import broker


@broker.task
async def my_redis_task(
    key: str,
    val: str,
    pool: ConnectionPool = TaskiqDepends(get_redis_pool),  # noqa: B008
):
    async with Redis(connection_pool=pool) as redis:
        await redis.set(name=key, value=val)
        logger.debug(f"Set key {key} with value {val} in Redis using connection pool")
