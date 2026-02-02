from pydantic import BaseModel

from api_shared.broker import broker


class NestedModel(BaseModel):
    name: str
    value: int
    tags: list[str]


class PydanticParseInput(BaseModel):
    text: str
    count: int
    nested: NestedModel


class PydanticParseResult(BaseModel):
    received_text: str
    received_count: int
    received_nested: NestedModel
    doubled_count: int
    status: str


@broker.task(task_name="pydantic_parse_check")
async def pydantic_parse_check(data: PydanticParseInput) -> PydanticParseResult:
    """
    Tests taskiq's ability to parse and serialize Pydantic BaseModels.
    """
    raise NotImplementedError("This task is implemented in the worker package")
