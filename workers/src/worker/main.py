import asyncio

from api_template_shared.broker import broker
from loguru import logger

from worker.tasks.dummy import (  # noqa: F401
    add_one,
    add_one_with_retry,
)


async def main() -> None:
    await broker.startup()

    # Send the task to the broker.
    task = await add_one.kiq(1)
    # task = await add_one_with_retry.kiq(1)

    # Wait for the result.
    result = await task.wait_result(timeout=2)
    logger.debug(f"Task execution took: {result.execution_time} seconds.")
    if not result.is_err:
        logger.debug(f"Returned value: {result.return_value}")
    else:
        logger.debug("Error found while executing task.")
    await broker.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
