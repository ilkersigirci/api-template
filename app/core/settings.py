from enum import StrEnum
from pathlib import Path
from tempfile import gettempdir

from api_template_shared.core.settings import RunMode, SharedBaseSettings
from pydantic import Field
from pydantic_settings import SettingsConfigDict

TEMP_DIR = Path(gettempdir())


class LogLevel(StrEnum):
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class Settings(SharedBaseSettings):
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["*"])
    DB_ECHO: bool = False
    DB_FILE: str = "db.sqlite3"
    HOST: str = "0.0.0.0"
    LOG_LEVEL: LogLevel = LogLevel.INFO
    PORT: int = 8000
    PROJECT_NAME: str = "FastAPI Template"
    PROMETHEUS_DIR: Path = Field(
        default=TEMP_DIR / "prom",
        description="This variable is used to define multiproc_dir.It's required for [uvi|guni]corn projects.",
    )
    RELOAD: bool = False
    RUN_MODE: RunMode = RunMode.API
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    UVICORN_WORKERS: int = 1

    @property
    def DB_URL(self) -> str:
        """Assemble database URL from settings.

        Return:
            Database URL.
        """
        return f"sqlite+aiosqlite:///{self.DB_FILE}"

    model_config = SettingsConfigDict(
        env_file=".env",
        # env_prefix="API_TEMPLATE_",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()  # type: ignore[call-arg]
