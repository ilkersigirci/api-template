from dataclasses import dataclass

from redis.asyncio import BlockingConnectionPool


@dataclass
class RedisState:
    redis_pool: BlockingConnectionPool | None = None


# Global Redis connection pool
redis_state = RedisState()


async def get_redis_pool() -> BlockingConnectionPool:
    if redis_state.redis_pool is None:
        raise RuntimeError("Redis pool is not initialized")
    return redis_state.redis_pool
