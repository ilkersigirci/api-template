from typing import cast

from fastapi import APIRouter, HTTPException
from taskiq import ResultGetError
from taskiq_redis import RedisAsyncResultBackend

from app.api.tasks.schemas import FailingTaskParams, TaskOut, TaskParams, TaskResult
from app.worker.broker import broker
from app.worker.tasks.complex_task import long_running_process_placeholder
from app.worker.tasks.failing_task import failing_process_placeholder

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskOut)
async def trigger_task(params: TaskParams) -> TaskOut:
    """
    Trigger a long-running task.
    """
    task = await long_running_process_placeholder.kiq(duration=params.duration)
    return TaskOut(task_id=task.task_id)


@router.post("/fail", response_model=TaskOut)
async def trigger_failing_task(params: FailingTaskParams) -> TaskOut:
    """
    Trigger a task that will fail.
    """
    task = await failing_process_placeholder.kiq(error_message=params.error_message)
    return TaskOut(task_id=task.task_id)


@router.get("/{task_id}", response_model=TaskResult)
async def get_task_result(task_id: str) -> TaskResult:
    """
    Get the status and result of a task.
    """
    try:
        # Check if the result backend is configured
        if not broker.result_backend:
            raise HTTPException(
                status_code=500, detail="Result backend is not configured"
            )

        # Assume usage of Redis backend
        backend = cast(RedisAsyncResultBackend, broker.result_backend)

        if await backend.is_result_ready(task_id):
            result = await backend.get_result(task_id)

            status = "completed"
            if result.is_err:
                status = "failed"

            return TaskResult(
                task_id=task_id,
                status=status,
                result=result.return_value if not result.is_err else None,
                error=str(result.error) if result.is_err else None,
            )
        return TaskResult(
            task_id=task_id,
            status="pending",
            result=None,
            error=None,
        )

    except ResultGetError as exc:
        raise HTTPException(
            status_code=404, detail="Task not found or result expired"
        ) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
