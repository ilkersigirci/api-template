from typing import Annotated

from pydantic import BaseModel, Field


class EchoMessage(BaseModel):
    """Simple message model."""

    message: Annotated[str, Field(description="Message to be echoed.")]
