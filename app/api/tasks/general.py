"""Workers broker task endpoints."""

from typing import cast

from api_shared.services.redis.deps import get_redis_pool
from api_shared.tasks.general import (
    NestedModel,
    PydanticParseInput,
    failing_process,
    long_running_process,
    pydantic_parse_check,
)
from api_shared.utils.task_status_manager import TaskStatus, TaskStatusManager
from fastapi import APIRouter, HTTPException
from redis.asyncio import Redis
from taskiq import ResultGetError
from taskiq_redis import RedisAsyncResultBackend

from app.api.tasks.schemas import (
    FailingTaskParams,
    PydanticParseParams,
    TaskOut,
    TaskParams,
    TaskResult,
)
from app.core.broker import broker_manager

router = APIRouter(prefix="/tasks/general", tags=["tasks"])

workers_broker = broker_manager.get_broker("general")


@router.post("/", response_model=TaskOut)
async def trigger_task(params: TaskParams) -> TaskOut:
    """
    Trigger a long-running task.
    """
    task = await long_running_process.kiq(duration=params.duration)
    return TaskOut(task_id=task.task_id)


@router.post("/fail", response_model=TaskOut)
async def trigger_failing_task(params: FailingTaskParams) -> TaskOut:
    """
    Trigger a task that will fail.
    """
    task = await failing_process.kiq(error_message=params.error_message)
    return TaskOut(task_id=task.task_id)


@router.post("/pydantic", response_model=TaskOut)
async def trigger_pydantic_parse(params: PydanticParseParams) -> TaskOut:
    """
    Trigger a task that tests Pydantic BaseModel parsing.
    """
    input_data = PydanticParseInput(
        text=params.text,
        count=params.count,
        nested=NestedModel(
            name=params.nested.name,
            value=params.nested.value,
            tags=params.nested.tags,
        ),
    )
    task = await pydantic_parse_check.kiq(data=input_data)
    return TaskOut(task_id=task.task_id)


@router.get("/{task_id}", response_model=TaskResult)
async def get_task_result(task_id: str) -> TaskResult:
    """
    Get the status and result of a task.
    """
    try:
        redis_pool = await get_redis_pool()
        async with Redis.from_pool(redis_pool) as redis_client:
            metadata = await TaskStatusManager.get_task_metadata(task_id, redis_client)

        if not metadata:
            raise HTTPException(
                status_code=404, detail="Task not found or result expired"
            )

        status = metadata.get("status", TaskStatus.QUEUED)
        result_data = None
        error_msg = metadata.get("error")

        # Early return for non-completed tasks
        if status not in (TaskStatus.FINISHED, TaskStatus.FAILED):
            return TaskResult(
                task_id=task_id,
                status=status,
                result=None,
                error=error_msg,
            )

        # Task is finished or failed, try to get result
        backend = cast(RedisAsyncResultBackend, workers_broker.result_backend)

        if not await backend.is_result_ready(task_id):
            return TaskResult(
                task_id=task_id,
                status=status,
                result=None,
                error=error_msg,
            )

        # Result is ready, fetch it
        result = await backend.get_result(task_id)
        result_data = result.return_value if not result.is_err else None
        if result.is_err and not error_msg:
            error_msg = str(result.error)

        return TaskResult(
            task_id=task_id,
            status=status,
            result=result_data,
            error=error_msg,
        )

    except HTTPException:
        raise
    except ResultGetError as exc:
        raise HTTPException(
            status_code=404, detail="Task not found or result expired"
        ) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
