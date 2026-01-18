from pydantic import BaseModel, Field


class TaskParams(BaseModel):
    duration: int = Field(
        default=10, ge=1, le=60, description="Duration of the task in seconds"
    )


class FailingTaskParams(BaseModel):
    error_message: str = Field(
        default="This is a deliberate error",
        description="Message to be raised in exception",
    )


class TaskOut(BaseModel):
    task_id: str


class TaskResult(BaseModel):
    task_id: str
    status: str
    result: dict | None = None
    error: str | None = None
