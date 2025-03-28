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


class Settings(BaseSettings):
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    API_V1_STR: str = "/api/v1"
    API_V2_STR: str = "/api/v2"
    CORS_ORIGINS: list[str] = ["*"]
    ENVIRONMENT: str = "dev"
    HOST: str = "127.0.0.1"
    LOG_LEVEL: LogLevel = LogLevel.INFO
    OTLP_ENDPOINT: CustomHttpUrlStr = "http://localhost"
    PORT: int = 8000
    PROJECT_NAME: str = "FastAPI Template"
    RELOAD: bool = False
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    TELEMETRY_ENABLED: bool = False
    TELEMETRY_LOGGING_ENABLED: bool = False
    WORKERS: int = 1
    PROMETHEUS_DIR: Path = Field(
        default=TEMP_DIR / "prom",
        description="This variable is used to define multiproc_dir.It's required for [uvi|guni]corn projects.",
    )
    REDIS_PORT: int = 6379
    REDIS_HOST: str = "localhost"
    REDIS_USER: str | None = None
    REDIS_PASS: str | None = None
    REDIS_BASE: str | None = None

    @property
    def REDIS_URL(self) -> URL:
        """Assemble REDIS URL from settings.

        Returns:
            Redis URL.
        """
        path = f"/{self.REDIS_BASE}" if self.REDIS_BASE is not None else ""

        return URL.build(
            scheme="redis",
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            user=self.REDIS_USER,
            password=self.REDIS_PASS,
            path=path,
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        # env_prefix="API_TEMPLATE_",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
