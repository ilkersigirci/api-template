from taskiq import TaskiqState

from api_shared.services.redis.deps import redis_state
from api_shared.services.redis.lifespan import close_redis_pool, init_redis_pool


async def worker_startup(state: TaskiqState) -> None:
    """Initialize resources when worker starts

    You can add other startup tasks here, such as initializing database connections, models, etc.
    ."""
    redis_state.redis_pool = await init_redis_pool()


async def worker_shutdown(state: TaskiqState) -> None:
    """Cleanup resources when worker shuts down."""
    if redis_state.redis_pool is None:
        raise RuntimeError("Redis pool is not initialized")

    await close_redis_pool(redis_state.redis_pool)
