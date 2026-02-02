from pydantic import BaseModel

from api_shared.broker import broker


class LongRunningProcessResult(BaseModel):
    start_time: float
    end_time: float
    elapsed: float
    status: str


@broker.task(task_name="long_running_process")
async def long_running_process(duration: int = 5) -> LongRunningProcessResult:
    """
    Simulates a long-running process by sleeping.
    """
    raise NotImplementedError("This task is implemented in the worker package")
