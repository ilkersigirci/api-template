from fastapi import APIRouter
from loguru import logger

from app.api.echo.schemas import EchoMessage

router = APIRouter(prefix="/echo", tags=["echo"])


@router.post("/", response_model=EchoMessage)
async def send_echo_message(incoming_message: EchoMessage) -> EchoMessage:
    """Sends echo back to user.

    Args:
        incoming_message: incoming message.

    Returns:
        message same as the incoming.
    """
    logger.error(f"Echo dummy log error: {incoming_message}")
    print(f"Echo dummy print: {incoming_message}")  # noqa: T201

    return incoming_message
