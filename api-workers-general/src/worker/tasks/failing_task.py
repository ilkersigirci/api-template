from loguru import logger

from worker.broker import broker


@broker.task(task_name="failing_process")
async def failing_process(error_message: str = "This is a deliberate error") -> None:
    """
    A task that intentionally fails to demonstrate error handling.
    """
    logger.info(f"Starting failing process with message: {error_message}")

    raise RuntimeError(error_message)
