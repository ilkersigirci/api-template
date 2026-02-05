from api_shared.broker import broker_manager

broker = broker_manager.get_broker("workers")


@broker.task(task_name="failing_process")
async def failing_process(
    error_message: str = "This is a deliberate error",
) -> None:
    """
    A task that intentionally fails to demonstrate error handling.
    """
    raise NotImplementedError("This task is implemented in the worker package")
