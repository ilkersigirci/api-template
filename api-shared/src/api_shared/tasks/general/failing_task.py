from pydantic import BaseModel, Field

FAILING_PROCESS_TASK = "failing_process"


class FailingProcessInput(BaseModel):
    error_message: str = Field(
        default="This is a deliberate error",
        description="Message to be raised in exception.",
    )
