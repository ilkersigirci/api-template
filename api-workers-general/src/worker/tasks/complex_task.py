import asyncio
from time import time

from api_shared.tasks.general import LongRunningProcessResult
from loguru import logger

from worker.broker import broker


@broker.task(task_name="long_running_process")
async def long_running_process(duration: int = 5) -> LongRunningProcessResult:
    """
    Simulates a long-running process by sleeping.
    """
    start_time = time()
    logger.info(f"Starting long running process for {duration} seconds.")

    await asyncio.sleep(duration)

    end_time = time()
    elapsed = end_time - start_time
    logger.info(f"Finished long running process. Elapsed: {elapsed:.2f}s")

    return LongRunningProcessResult(
        start_time=start_time,
        end_time=end_time,
        elapsed=elapsed,
    )
