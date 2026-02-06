# from typing import Annotated

# from app.api.redis.deps import get_redis_pool
# from loguru import logger
# from redis.asyncio import ConnectionPool, Redis
# from taskiq import TaskiqDepends

# from api_shared.broker import broker_manager

# broker = broker_manager.get_broker("general")


# @broker.task
# async def my_redis_task(
#     key: str,
#     val: str,
#     pool: Annotated[ConnectionPool, TaskiqDepends(get_redis_pool)],
# ):
#     async with Redis(connection_pool=pool) as redis:
#         await redis.set(name=key, value=val)
#         logger.debug(f"Set key {key} with value {val} in Redis using connection pool")
