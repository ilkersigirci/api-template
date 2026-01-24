import ipaddress
from enum import StrEnum
from pathlib import Path
from tempfile import gettempdir
from typing import Annotated

from pydantic import AfterValidator, AnyHttpUrl, Field, PlainValidator, TypeAdapter
from pydantic_settings import BaseSettings, SettingsConfigDict
from yarl import URL

TEMP_DIR = Path(gettempdir())

AnyHttpUrlAdapter = TypeAdapter(AnyHttpUrl)

CustomHttpUrlStr = Annotated[
    str,
    PlainValidator(lambda x: AnyHttpUrlAdapter.validate_strings(x)),
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


class Settings(BaseSettings):
    ENVIRONMENT: Environment = Environment.DEV
    OLTP_LOG_METHOD: OLTPLogMethod = OLTPLogMethod.NONE
    OTLP_ENDPOINT: CustomHttpUrlStr | None = Field(
        default=None,
        description="OpenTelemetry GRPC endpoint for OTLP exporter.",
    )
    OLTP_STD_LOGGING_ENABLED: bool = False
    WORKERS: int = 1
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USERNAME: str | None = None
    RABBITMQ_PASSWORD: str | None = None
    RABBITMQ_VHOST: str = "/"
    REDIS_PORT: int = 6379
    REDIS_HOST: str = "localhost"
    REDIS_USER: str | None = None
    REDIS_PASS: str | None = None
    REDIS_BASE: str | None = None
    REDIS_TASK_DB: int = Field(
        default=1,
        ge=1,
        le=16,
        description="Redis database number for taskiq result backend. Must be between 1-16.",
    )
    TASKIQ_DASHBOARD_HOST: str | None = None
    TASKIQ_DASHBOARD_PORT: int = 8001
    TASKIQ_DASHBOARD_API_TOKEN: str = "supersecret"
    TASKIQ_BROKER_NAME: str = "api-template-worker"

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
    def REDIS_URL(self) -> URL:
        """Assemble REDIS URL from settings.

        Returns:
            Redis URL.
        """
        path = f"/{self.REDIS_BASE}" if self.REDIS_BASE is not None else ""
        scheme = "redis" if _should_use_http_scheme(self.REDIS_HOST) else "rediss"

        return URL.build(
            scheme=scheme,
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            user=self.REDIS_USER,
            password=self.REDIS_PASS,
            path=path,
        )

    @property
    def RABBITMQ_URL(self) -> URL:
        """Assemble RabbitMQ URL from settings.

        Returns:
            RabbitMQ URL.
        """
        scheme = "amqp" if _should_use_http_scheme(self.RABBITMQ_HOST) else "amqps"

        return URL.build(
            scheme=scheme,
            host=self.RABBITMQ_HOST,
            port=self.RABBITMQ_PORT,
            user=self.RABBITMQ_USERNAME,
            password=self.RABBITMQ_PASSWORD,
            path=self.RABBITMQ_VHOST,
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        # env_prefix="API_TEMPLATE_WORKER_",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
