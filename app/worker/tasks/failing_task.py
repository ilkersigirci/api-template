from loguru import logger

from app.worker.broker import broker


@broker.task
async def failing_process(error_message: str = "This is a deliberate error") -> None:
    """
    A task that intentionally fails to demonstrate error handling.
    """
    logger.info(f"Starting failing process with message: {error_message}")

    # Simulate some work slightly before failing? Not strictly necessary.

    raise RuntimeError(error_message)
