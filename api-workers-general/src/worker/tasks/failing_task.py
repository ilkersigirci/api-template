from api_shared.tasks.general import FAILING_PROCESS_TASK, FailingProcessInput
from hatchet_sdk import Context
from loguru import logger

from worker.runner import hatchet


@hatchet.task(
    name=FAILING_PROCESS_TASK,
    input_validator=FailingProcessInput,
)
async def failing_process(input: FailingProcessInput, ctx: Context) -> None:
    logger.info("Starting failing process with message: {}", input.error_message)
    ctx.log(f"About to fail task with message: {input.error_message}")

    raise RuntimeError(input.error_message)
