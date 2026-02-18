from api_shared.tasks.general import (
    PYDANTIC_PARSE_CHECK_TASK,
    PydanticParseInput,
    PydanticParseResult,
)
from hatchet_sdk import Context
from loguru import logger

from worker.runner import hatchet


@hatchet.task(
    name=PYDANTIC_PARSE_CHECK_TASK,
    input_validator=PydanticParseInput,
)
async def pydantic_parse_check(
    input: PydanticParseInput,
    ctx: Context,
) -> PydanticParseResult:
    logger.info("Received Pydantic model: {}", input)
    ctx.log(f"Processing Pydantic payload: text={input.text}")

    result = PydanticParseResult(
        received_text=input.text,
        received_count=input.count,
        received_nested=input.nested,
        doubled_count=input.count * 2,
    )

    logger.info("Returning Pydantic result: {}", result)
    return result
