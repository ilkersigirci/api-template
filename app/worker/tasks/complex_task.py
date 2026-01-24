from pydantic import BaseModel

from app.worker.broker import broker


class LongRunningProcessResult(BaseModel):
    start_time: float
    end_time: float
    elapsed: float
    status: str


@broker.task(task_name="long_running_process")
async def long_running_process_placeholder(duration: int = 5) -> None:
    """
    Simulates a long-running process by sleeping.
    """
