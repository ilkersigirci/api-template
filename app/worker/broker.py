from typing import Any

import taskiq_fastapi
from taskiq import (
    AsyncBroker,
    AsyncResultBackend,
    InMemoryBroker,
    SmartRetryMiddleware,
)
from taskiq.schedule_sources import LabelScheduleSource
from taskiq.scheduler.scheduler import TaskiqScheduler
from taskiq_aio_pika import AioPikaBroker
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend  # noqa: F401

from app.core.settings import Environment, settings

if settings.ENVIRONMENT == Environment.TEST:
    # NOTE: By default uses InMemoryResultBackend
    broker: AsyncBroker = InMemoryBroker()
else:
    result_backend: AsyncResultBackend[Any] = RedisAsyncResultBackend(
        redis_url=str(settings.REDIS_URL.with_path(f"/{settings.REDIS_TASK_DB}")),
    )

    # broker: AsyncBroker = ListQueueBroker(
    #     str(settings.REDIS_URL.with_path("/1"))
    # ).with_result_backend(result_backend)

    broker: AsyncBroker = (
        AioPikaBroker(
            str(settings.RABBITMQ_URL),
        )
        .with_result_backend(result_backend)
        .with_middlewares(
            SmartRetryMiddleware(
                default_retry_count=5,
                default_delay=10,
                use_jitter=True,
                use_delay_exponent=True,
                max_delay_exponent=120,
            )
        )
    )

    scheduler = TaskiqScheduler(
        broker=broker,
        sources=[LabelScheduleSource(broker)],
    )

taskiq_fastapi.init(broker, "app.api.application:get_app")
