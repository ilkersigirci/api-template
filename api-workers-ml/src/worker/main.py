import asyncio

from api_shared.tasks.ml import ml_inference_task
from loguru import logger

from worker.broker import broker
from worker.tasks.ml_inference import ml_inference_task  # noqa: F811
from worker.tasks.ml_training import train_model_task  # noqa: F401


async def main() -> None:
    """
    Example main function to test ML worker broker.

    This demonstrates how to kick ML tasks and wait for results.
    """
    await broker.startup()

    # Send an ML inference task to the broker
    logger.info("Kicking ML inference task...")
    task = await ml_inference_task.kiq(
        model_id="test_model_v1",
        input_data={"features": [1.0, 2.0, 3.0], "batch_size": 1},
    )

    # Wait for the result
    logger.info(f"Waiting for task {task.task_id} to complete...")
    result = await task.wait_result(timeout=10)

    logger.debug(f"Task execution took: {result.execution_time} seconds.")
    if not result.is_err:
        logger.debug(f"Returned value: {result.return_value}")
    else:
        logger.debug("Error found while executing task.")
        logger.error(f"Error: {result.error}")

    await broker.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
