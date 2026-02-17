from api_shared.tasks.general import (
    PydanticParseInput,
    PydanticParseResult,
)
from loguru import logger

from worker.broker import broker


@broker.task(task_name="pydantic_parse_check")
async def pydantic_parse_check(data: PydanticParseInput) -> PydanticParseResult:
    """
    Tests taskiq's ability to parse and serialize Pydantic BaseModels.
    """
    logger.info(f"Received Pydantic model: {data}")
    logger.info(f"Nested model: {data.nested}")

    result = PydanticParseResult(
        received_text=data.text,
        received_count=data.count,
        received_nested=data.nested,
        doubled_count=data.count * 2,
    )

    logger.info(f"Returning Pydantic result: {result}")
    return result
