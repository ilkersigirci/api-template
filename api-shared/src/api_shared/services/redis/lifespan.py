from loguru import logger
from redis.asyncio import BlockingConnectionPool, Redis

from api_shared.core.settings import settings


async def init_redis_pool(
    redis_url: str = settings.REDIS_URL,
    max_connections: int = 50,
    retry_on_timeout: bool = True,
) -> BlockingConnectionPool:
    """Initialize the Redis connection pool."""
    try:
        redis_pool = BlockingConnectionPool.from_url(
            redis_url,
            max_connections=max_connections,
            retry_on_timeout=retry_on_timeout,
        )

        async with Redis.from_pool(redis_pool) as client:
            await client.ping()  # ty:ignore[invalid-await]
        logger.info(
            "Redis connection pool initialized successfully with URL: {}", redis_url
        )
        return redis_pool
    except Exception as e:
        logger.error("Failed to initialize Redis pool: {}", e)
        raise


async def close_redis_pool(redis_pool: BlockingConnectionPool) -> None:
    """Close the Redis connection pool."""
    await redis_pool.aclose()
    logger.info("Redis connection pool closed")
