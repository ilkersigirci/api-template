from typing import Annotated

from pydantic import (
    AfterValidator,
    AnyHttpUrl,
    PlainValidator,
    TypeAdapter,
)
from pydantic_settings import BaseSettings

AnyHttpUrlAdapter = TypeAdapter(AnyHttpUrl)

CustomHttpUrlStr = Annotated[
    str,
    PlainValidator(lambda x: AnyHttpUrlAdapter.validate_strings(x)),
    AfterValidator(lambda x: str(x).rstrip("/")),
]


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "FastAPI Template"

    ENVIRONMENT: str = "dev"

    # CORS configuration
    CORS_ORIGINS: list[CustomHttpUrlStr] = []

    # JWT configuration
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # OpenTelemetry settings
    TELEMETRY_ENABLED: bool = False
    OTLP_ENDPOINT: CustomHttpUrlStr = ""

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
