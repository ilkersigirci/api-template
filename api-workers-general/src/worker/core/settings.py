from api_shared.core.settings import SharedBaseSettings
from pydantic import Field
from pydantic_settings import SettingsConfigDict


class Settings(SharedBaseSettings):
    HATCHET_WORKER_NAME: str = Field(default="general-worker")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()  # type: ignore[call-arg]
