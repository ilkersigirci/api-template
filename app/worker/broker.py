from typing import Any

import taskiq_fastapi
from taskiq import AsyncBroker, AsyncResultBackend, InMemoryBroker
from taskiq_aio_pika import AioPikaBroker
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend  # noqa: F401

from app.core.settings import Environment, settings

if settings.ENVIRONMENT == Environment.TEST:
    # NOTE: By default uses InMemoryResultBackend
    broker: AsyncBroker = InMemoryBroker()
else:
    result_backend: AsyncResultBackend[Any] = RedisAsyncResultBackend(
        redis_url=str(settings.REDIS_URL.with_path("/1")),
    )

    # broker: AsyncBroker = ListQueueBroker(
    #     str(settings.REDIS_URL.with_path("/1"))
    # ).with_result_backend(result_backend)

    broker: AsyncBroker = AioPikaBroker(
        str(settings.RABBITMQ_URL),
    ).with_result_backend(result_backend)

taskiq_fastapi.init(broker, "app.api.application:get_app")
