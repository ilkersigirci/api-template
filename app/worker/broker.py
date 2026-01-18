from typing import Any

import taskiq_fastapi
from taskiq import (
    AsyncBroker,
    AsyncResultBackend,
    InMemoryBroker,
    SmartRetryMiddleware,
)
from taskiq.instrumentation import TaskiqInstrumentor
from taskiq.schedule_sources import LabelScheduleSource
from taskiq.scheduler.scheduler import TaskiqScheduler
from taskiq_aio_pika import AioPikaBroker
from taskiq_redis import RedisAsyncResultBackend

from app.core.settings import Environment, OLTPLogMethod, settings
from app.worker.middlewares import CustomDashboardMiddleware

if settings.OLTP_LOG_METHOD != OLTPLogMethod.NONE:
    TaskiqInstrumentor().instrument()

# NOTE: Test uses InMemoryResultBackend
if settings.ENVIRONMENT == Environment.TEST:
    broker: AsyncBroker = InMemoryBroker()
else:
    result_backend: AsyncResultBackend[Any] = RedisAsyncResultBackend(
        redis_url=str(settings.REDIS_URL.with_path(f"/{settings.REDIS_TASK_DB}")),
    )

    middlewares = [
        SmartRetryMiddleware(
            default_retry_count=5,
            default_delay=10,
            use_jitter=True,
            use_delay_exponent=True,
            max_delay_exponent=120,
        ),
    ]

    if settings.TASKIQ_DASHBOARD_URL:
        middlewares.append(
            CustomDashboardMiddleware(
                url=settings.TASKIQ_DASHBOARD_URL,
                api_token=settings.TASKIQ_DASHBOARD_API_TOKEN,
                broker_name=settings.TASKIQ_BROKER_NAME,
            )
        )

    broker: AsyncBroker = (
        AioPikaBroker(
            str(settings.RABBITMQ_URL),
        )
        .with_result_backend(result_backend)
        .with_middlewares(*middlewares)
    )

    scheduler = TaskiqScheduler(
        broker=broker,
        sources=[LabelScheduleSource(broker)],
    )

taskiq_fastapi.init(broker, "app.api.application:get_app")
