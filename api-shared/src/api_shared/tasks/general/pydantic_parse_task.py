from pydantic import BaseModel, Field

PYDANTIC_PARSE_CHECK_TASK = "pydantic_parse_check"


class NestedModel(BaseModel):
    name: str
    value: int
    tags: list[str]


class PydanticParseInput(BaseModel):
    text: str = Field(default="test", description="Text to send")
    count: int = Field(default=5, ge=1, description="Count to send")
    nested: NestedModel = Field(
        default_factory=lambda: NestedModel(name="default", value=42, tags=["a", "b"])
    )


class PydanticParseResult(BaseModel):
    received_text: str
    received_count: int
    received_nested: NestedModel
    doubled_count: int
