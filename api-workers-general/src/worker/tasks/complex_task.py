import asyncio
from time import time

from api_shared.tasks.general import (
    LONG_RUNNING_PROCESS_TASK,
    LongRunningProcessInput,
    LongRunningProcessResult,
)
from hatchet_sdk import Context
from loguru import logger

from worker.runner import hatchet


@hatchet.task(
    name=LONG_RUNNING_PROCESS_TASK,
    input_validator=LongRunningProcessInput,
)
async def long_running_process(
    input: LongRunningProcessInput,
    ctx: Context,
) -> LongRunningProcessResult:
    start_time = time()
    logger.info("Starting long running process for {} seconds.", input.duration)
    ctx.log(f"Starting long running process for {input.duration} seconds")

    await asyncio.sleep(input.duration)

    end_time = time()
    elapsed = end_time - start_time
    logger.info("Finished long running process. Elapsed: {:.2f}s", elapsed)

    return LongRunningProcessResult(
        start_time=start_time,
        end_time=end_time,
        elapsed=elapsed,
    )
