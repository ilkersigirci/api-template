from pydantic import BaseModel, Field

LONG_RUNNING_PROCESS_TASK = "long_running_process"


class LongRunningProcessInput(BaseModel):
    duration: int = Field(
        default=10,
        ge=1,
        le=60,
        description="Duration of the task in seconds.",
    )


class LongRunningProcessResult(BaseModel):
    start_time: float
    end_time: float
    elapsed: float
