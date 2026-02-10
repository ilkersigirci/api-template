from api_shared.services.redis.deps import get_redis_pool
from fastapi import APIRouter
from redis.asyncio import Redis

from app.api.redis.schemas import RedisValueDTO

router = APIRouter(prefix="/redis", tags=["redis"])


@router.get("/", response_model=RedisValueDTO)
async def get_redis_value(key: str) -> RedisValueDTO:
    """
    Get value from redis.

    :param key: redis key, to get data from.
    :param redis_pool: redis connection pool.
    :returns: information from redis.
    """
    redis_pool = await get_redis_pool()

    async with Redis(connection_pool=redis_pool) as redis:
        redis_value = await redis.get(key)
    return RedisValueDTO(
        key=key,
        value=redis_value,
    )


@router.put("/")
async def set_redis_value(
    redis_value: RedisValueDTO,
) -> None:
    """
    Set value in redis.

    :param redis_value: new value data.
    :param redis_pool: redis connection pool.
    """
    if redis_value.value is not None:
        redis_pool = await get_redis_pool()
        async with Redis(connection_pool=redis_pool) as redis:
            await redis.set(name=redis_value.key, value=redis_value.value)
