import ipaddress
from enum import StrEnum
from typing import Annotated

from pydantic import (
    AfterValidator,
    AnyHttpUrl,
    Field,
    PlainValidator,
    TypeAdapter,
)
from pydantic_settings import BaseSettings, SettingsConfigDict
from yarl import URL

AnyHttpUrlAdapter = TypeAdapter(AnyHttpUrl)

CustomHttpUrlStr = Annotated[
    str,
    PlainValidator(AnyHttpUrlAdapter.validate_strings),
    AfterValidator(lambda x: str(x).rstrip("/")),
]


class Environment(StrEnum):
    """Possible environments."""

    DEV = "dev"
    TEST = "test"
    PROD = "prod"


class OLTPLogMethod(StrEnum):
    NONE = "none"
    MANUAL = "manual"
    LOGFIRE = "logfire"


class RunMode(StrEnum):
    NONE = "none"
    API = "api"
    WORKER = "worker"


def _should_use_http_scheme(host: str) -> bool:
    """Check if the host should use HTTP scheme instead of HTTPS.

    Uses HTTP for:
    - IP addresses (IPv4 or IPv6)
    - Simple hostnames without dots (like docker hostnames: redis, postgres, etc.)

    Uses HTTPS for:
    - Domain names with dots (like redis.example.com)

    Args:
        host: The host string to check.

    Returns:
        True if should use HTTP scheme, False if should use HTTPS.
    """
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        pass

    return "." not in host


class SharedBaseSettings(BaseSettings):
    """Base settings class with common configuration shared across all services."""

    ENVIRONMENT: Environment = Field(
        default=Environment.DEV,
        description="Application environment (dev, test, prod).",
    )
    OLTP_LOG_METHOD: OLTPLogMethod = Field(
        default=OLTPLogMethod.NONE,
        description="OpenTelemetry logging method (none, manual, logfire).",
    )
    OTLP_ENDPOINT: CustomHttpUrlStr | None = Field(
        default=None,
        description="OpenTelemetry GRPC endpoint for OTLP exporter.",
    )
    OLTP_STD_LOGGING_ENABLED: bool = Field(
        default=False,
        description="Enable standard logging integration with OpenTelemetry.",
    )
    RABBITMQ_HOST: str = Field(
        default="localhost",
        description="RabbitMQ server hostname or IP address.",
    )
    RABBITMQ_PORT: int = Field(
        default=5672,
        description="RabbitMQ server port.",
    )
    RABBITMQ_USERNAME: str = Field(
        description="RabbitMQ authentication username.",
    )
    RABBITMQ_PASSWORD: str = Field(
        description="RabbitMQ authentication password.",
    )
    RABBITMQ_VHOST: str = Field(
        default="/",
        description="RabbitMQ virtual host.",
    )
    REDIS_PORT: int = Field(
        default=6379,
        description="Redis server port.",
    )
    REDIS_HOST: str = Field(
        default="localhost",
        description="Redis server hostname or IP address.",
    )
    REDIS_USER: str | None = Field(
        default=None,
        description="Redis authentication username.",
    )
    REDIS_PASS: str = Field(
        description="Redis authentication password.",
    )
    REDIS_BASE: str | None = Field(
        default=None,
        description="Redis database base path.",
    )
    REDIS_TASK_DB: int = Field(
        default=1,
        ge=1,
        le=16,
        description="Redis database number for taskiq result backend. Must be between 1-16.",
    )
    REDIS_MAX_CONNECTION_POOL_SIZE: int | None = Field(
        default=None,
        description="Maximum number of connections in Redis connection pool.",
    )
    TASKIQ_RESULT_EX_TIME: int = Field(
        default=86400 * 2,
        description="TTL for taskiq results and task monitoring data in Redis (in seconds). Defaults to 2 days.",
    )
    RUN_MODE: RunMode = Field(
        default=RunMode.NONE,
        description="Application run mode api or worker).",
    )
    TASKIQ_DASHBOARD_HOST: str | None = Field(
        default=None,
        description="Taskiq dashboard server hostname or IP address.",
    )
    TASKIQ_DASHBOARD_PORT: int = Field(
        default=8001,
        description="Taskiq dashboard server port.",
    )
    TASKIQ_DASHBOARD_API_TOKEN: str = Field(
        default="supersecret",
        description="API token for Taskiq dashboard authentication.",
    )
    TASKIQ_BROKERS_CONFIG_FILE: str | None = Field(
        default=None,
        description="Path to YAML file containing broker configurations.",
    )

    @property
    def TASKIQ_DASHBOARD_URL(self) -> str | None:
        """Assemble Taskiq Dashboard URL from settings.

        Returns:
            Taskiq Dashboard URL.
        """
        if self.TASKIQ_DASHBOARD_HOST is None:
            return None

        return f"http://{self.TASKIQ_DASHBOARD_HOST}:{self.TASKIQ_DASHBOARD_PORT}"

    @property
    def REDIS_URL(self) -> str:
        """Assemble REDIS URL from settings.

        Returns:
            Redis URL.
        """
        path = f"/{self.REDIS_BASE}" if self.REDIS_BASE is not None else ""
        scheme = "redis" if _should_use_http_scheme(self.REDIS_HOST) else "rediss"

        base_url = URL.build(
            scheme=scheme,
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            user=self.REDIS_USER,
            password=self.REDIS_PASS,
            path=path,
        )

        return str(base_url.with_path(f"/{settings.REDIS_TASK_DB}"))

    @property
    def RABBITMQ_URL(self) -> str:
        """Assemble RabbitMQ URL from settings.

        Returns:
            RabbitMQ URL.
        """
        scheme = "amqp" if _should_use_http_scheme(self.RABBITMQ_HOST) else "amqps"

        return str(
            URL.build(
                scheme=scheme,
                host=self.RABBITMQ_HOST,
                port=self.RABBITMQ_PORT,
                user=self.RABBITMQ_USERNAME,
                password=self.RABBITMQ_PASSWORD,
                path=self.RABBITMQ_VHOST,
            )
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        # env_prefix="FASTAPI_TEMPLATE_SHARED_",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = SharedBaseSettings()  # type: ignore[call-arg]
