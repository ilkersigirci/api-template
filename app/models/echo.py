from typing import Annotated

from pydantic import BaseModel, Field


class Message(BaseModel):
    """Simple message model."""

    message: Annotated[str, Field(description="Message to be echoed.")]
