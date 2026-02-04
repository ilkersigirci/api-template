from typing import Any

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

from api_shared.core.settings import (
    Environment,
    OLTPLogMethod,
    settings,
)

if settings.TASKIQ_DASHBOARD_URL:
    from api_shared.middlewares.dashboard import DashboardMiddleware

if settings.OLTP_LOG_METHOD != OLTPLogMethod.NONE:
    TaskiqInstrumentor().instrument()


def _create_broker(
    queue_name: str,
    routing_key: str,
    exchange_name: str,
    broker_name: str,
) -> AsyncBroker:
    """Create a configured taskiq broker instance.

    Args:
        queue_name: Name of the queue for this broker.
        routing_key: Routing key for message routing.
        exchange_name: Name of the RabbitMQ exchange.
        broker_name: Name identifier for the broker.

    Returns:
        Configured AsyncBroker instance.
    """
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
            DashboardMiddleware(
                url=settings.TASKIQ_DASHBOARD_URL,
                api_token=settings.TASKIQ_DASHBOARD_API_TOKEN,
                broker_name=broker_name,
            )
        )

    return (
        AioPikaBroker(
            str(settings.RABBITMQ_URL),
            queue_name=queue_name,
            routing_key=routing_key,
            exchange_name=exchange_name,
        )
        .with_result_backend(result_backend)
        .with_middlewares(*middlewares)
    )


# NOTE: Test uses InMemoryResultBackend
if settings.ENVIRONMENT == Environment.TEST:
    broker: AsyncBroker = InMemoryBroker()
    ml_broker: AsyncBroker = InMemoryBroker()
else:
    # Regular worker broker
    broker: AsyncBroker = _create_broker(
        queue_name=settings.TASKIQ_WORKERS_QUEUE,
        routing_key=settings.TASKIQ_WORKERS_ROUTING_KEY,
        exchange_name=settings.TASKIQ_WORKERS_EXCHANGE,
        broker_name=f"{settings.TASKIQ_BROKER_NAME}-workers",
    )

    # ML worker broker
    ml_broker: AsyncBroker = _create_broker(
        queue_name=settings.TASKIQ_ML_QUEUE,
        routing_key=settings.TASKIQ_ML_ROUTING_KEY,
        exchange_name=settings.TASKIQ_ML_EXCHANGE,
        broker_name=f"{settings.TASKIQ_BROKER_NAME}-ml",
    )

    scheduler = TaskiqScheduler(
        broker=broker,
        sources=[LabelScheduleSource(broker)],
    )
