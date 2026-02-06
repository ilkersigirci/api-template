from api_shared.core.settings import RunMode, SharedBaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(SharedBaseSettings):
    RUN_MODE: RunMode = RunMode.WORKER

    model_config = SettingsConfigDict(
        env_file=".env",
        # env_prefix="API_TEMPLATE_WORKER_",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()  # type: ignore[call-arg]
