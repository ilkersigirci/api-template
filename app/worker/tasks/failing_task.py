from app.worker.broker import broker


@broker.task(task_name="failing_process")
async def failing_process_placeholder(
    error_message: str = "This is a deliberate error",
) -> None:
    """
    A task that intentionally fails to demonstrate error handling.
    """
