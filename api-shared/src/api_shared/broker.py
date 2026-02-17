from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, ValidationError
from taskiq import (
    AsyncBroker,
    AsyncResultBackend,
    InMemoryBroker,
    SmartRetryMiddleware,
    TaskiqEvents,
)
from taskiq.instrumentation import TaskiqInstrumentor
from taskiq.schedule_sources import LabelScheduleSource
from taskiq.scheduler.scheduler import TaskiqScheduler
from taskiq_aio_pika import AioPikaBroker
from taskiq_redis import RedisAsyncResultBackend

from api_shared.core.settings import Environment, OLTPLogMethod, settings
from api_shared.middlewares.task_status import TaskStatusMiddleware
from api_shared.utils.worker_lifespan import worker_shutdown, worker_startup

if settings.TASKIQ_DASHBOARD_URL:
    from api_shared.middlewares.dashboard import DashboardMiddleware

if settings.OLTP_LOG_METHOD != OLTPLogMethod.NONE:
    TaskiqInstrumentor().instrument()


class BrokerConfigSchema(BaseModel):
    """Pydantic model for broker configuration validation."""

    queue: str = Field(..., description="Queue name for this broker's tasks")
    routing_key: str = Field(
        default="#", description="Routing key pattern for message routing"
    )
    exchange: str = Field(..., description="Exchange name for this broker")
    description: str | None = Field(
        default=None, description="Description of the broker's purpose"
    )


class BrokersConfigSchema(BaseModel):
    """Pydantic model for the complete brokers YAML file."""

    brokers: dict[str, BrokerConfigSchema] = Field(
        ..., description="Broker configurations"
    )


class BrokerManager:
    """Manages taskiq broker instances and provides access to them."""

    def __init__(self):
        """Initialize the broker manager and create all configured brokers."""
        self._brokers: dict[str, AsyncBroker] = {}
        self._scheduler: TaskiqScheduler | None = None
        self._broker_configs: dict[str, BrokerConfigSchema] = {}
        self._load_broker_configs()
        self._initialize_brokers()

    def _load_broker_configs(self) -> None:
        """Load and validate broker configurations from YAML file.

        Raises:
            FileNotFoundError: If the broker config file doesn't exist.
            ValidationError: If the YAML structure is invalid.
        """
        if settings.TASKIQ_BROKERS_CONFIG_FILE:
            config_path = Path(settings.TASKIQ_BROKERS_CONFIG_FILE)
        else:
            config_path = (
                Path(__file__).parent.parent.parent / "configs" / "brokers.yml"
            )

        if not config_path.exists():
            raise FileNotFoundError(
                f"Broker configuration file not found: {config_path}. "
                f"Create the file or set TASKIQ_BROKERS_CONFIG_FILE environment variable."
            )

        with config_path.open("r") as f:
            raw_config = yaml.safe_load(f)

        try:
            validated_config = BrokersConfigSchema.model_validate(raw_config)
        except ValidationError as e:
            raise ValueError(
                f"Invalid broker configuration in {config_path}:\n{e}"
            ) from e

        self._broker_configs = validated_config.brokers

    def _create_broker(
        self, broker_name: str, broker_config: BrokerConfigSchema
    ) -> AsyncBroker:
        """Create a configured taskiq broker instance.

        Args:
            broker_name: Name identifier for the broker.
            broker_config: Broker configuration object.

        Returns:
            Configured AsyncBroker instance.
        """
        result_backend: AsyncResultBackend[Any] = RedisAsyncResultBackend(
            redis_url=settings.REDIS_URL,
            result_ex_time=settings.TASKIQ_RESULT_EX_TIME,
        )

        middlewares = [
            SmartRetryMiddleware(
                default_retry_count=5,
                default_delay=10,
                use_jitter=True,
                use_delay_exponent=True,
                max_delay_exponent=120,
            ),
            TaskStatusMiddleware(
                redis_url=settings.REDIS_URL,
                max_connection_pool_size=settings.REDIS_MAX_CONNECTION_POOL_SIZE,
                retry_on_timeout=True,
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
                settings.RABBITMQ_URL,
                queue_name=broker_config.queue,
                routing_key=broker_config.routing_key,
                exchange_name=broker_config.exchange,
            )
            .with_result_backend(result_backend)
            .with_middlewares(*middlewares)
        )

    def _initialize_brokers(self) -> None:
        """Initialize all configured brokers."""
        # NOTE: For testing, create in-memory brokers for all configured brokers
        if settings.ENVIRONMENT == Environment.TEST:
            self._brokers = {
                broker_name: InMemoryBroker() for broker_name in self._broker_configs
            }
        else:
            for broker_name, broker_config in self._broker_configs.items():
                self._brokers[broker_name] = self._create_broker(
                    broker_name, broker_config
                )

        if settings.ENVIRONMENT != Environment.TEST:
            workers_broker = self._brokers.get("general")
            if workers_broker:
                self._scheduler = TaskiqScheduler(
                    broker=workers_broker,
                    sources=[LabelScheduleSource(workers_broker)],
                )

    def get_broker(self, name: str) -> AsyncBroker:
        """Get a broker by name.

        Args:
            name: Name of the broker to retrieve.

        Returns:
            AsyncBroker instance.

        Raises:
            RuntimeError: If the broker is not enabled.
        """
        broker = self._brokers.get(name)
        if broker is None:
            raise RuntimeError(
                f"Broker '{name}' is not enabled. Enable it in the broker configuration file."
            )
        return broker

    def get_all_brokers(self) -> dict[str, AsyncBroker]:
        """Get all configured brokers.

        Returns:
            Dictionary mapping broker names to broker instances.
        """
        return self._brokers.copy()

    async def startup_all(self) -> None:
        """Start up all configured brokers.

        Only starts brokers that are not in worker process mode.
        """
        for broker_instance in self._brokers.values():
            if not broker_instance.is_worker_process:
                await broker_instance.startup()

    async def shutdown_all(self) -> None:
        """Shut down all configured brokers.

        Only shuts down brokers that are not in worker process mode.
        """
        for broker_instance in self._brokers.values():
            if not broker_instance.is_worker_process:
                await broker_instance.shutdown()

    @property
    def scheduler(self) -> TaskiqScheduler | None:
        """Get the scheduler instance if available.

        Returns:
            TaskiqScheduler instance or None if not configured.
        """
        return self._scheduler


# Create singleton instance
broker_manager = BrokerManager()

# TODO: Add this to only worker broker part.
for _, broker_instance in broker_manager.get_all_brokers().items():
    broker_instance.add_event_handler(TaskiqEvents.WORKER_STARTUP, worker_startup)
    broker_instance.add_event_handler(TaskiqEvents.WORKER_SHUTDOWN, worker_shutdown)
