from fastapi import APIRouter
from loguru import logger

from app.models.echo import Message

router = APIRouter()


@router.post("/", response_model=Message)
async def send_echo_message(incoming_message: Message) -> Message:
    """Sends echo back to user.

    Args:
        incoming_message: incoming message.

    Returns:
        message same as the incoming.
    """
    logger.error(f"Echo dummy log error: {incoming_message}")
    print(f"Echo dummy print: {incoming_message}")  # noqa: T201

    return incoming_message
