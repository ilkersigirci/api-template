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


class LogLevel(StrEnum):
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


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
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["*"]
    DB_ECHO: bool = False
    DB_FILE: str = "db.sqlite3"
    ENVIRONMENT: Environment = Environment.DEV
    HOST: str = "0.0.0.0"
    LOG_LEVEL: LogLevel = LogLevel.INFO
    OLTP_LOG_METHOD: OLTPLogMethod = OLTPLogMethod.NONE
    OTLP_ENDPOINT: CustomHttpUrlStr | None = Field(
        default=None,
        description="OpenTelemetry GRPC endpoint for OTLP exporter.",
    )
    OLTP_STD_LOGGING_ENABLED: bool = False
    PORT: int = 8000
    PROJECT_NAME: str = "FastAPI Template"
    RELOAD: bool = False
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    WORKERS: int = 1
    PROMETHEUS_DIR: Path = Field(
        default=TEMP_DIR / "prom",
        description="This variable is used to define multiproc_dir.It's required for [uvi|guni]corn projects.",
    )
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

    @property
    def DB_URL(self) -> str:
        """Assemble database URL from settings.

        Return:
            Database URL.
        """
        return f"sqlite+aiosqlite:///{self.DB_FILE}"

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
        # env_prefix="API_TEMPLATE_",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
