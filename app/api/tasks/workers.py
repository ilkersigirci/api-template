"""Workers broker task endpoints."""

from typing import cast

from api_shared.tasks.workers import (
    NestedModel,
    PydanticParseInput,
    failing_process,
    long_running_process,
    pydantic_parse_check,
)
from fastapi import APIRouter, HTTPException
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

router = APIRouter(prefix="/tasks", tags=["tasks"])

workers_broker = broker_manager.get_broker("workers")


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
        # Check if the result backend is configured
        if not workers_broker.result_backend:
            raise HTTPException(
                status_code=500, detail="Result backend is not configured"
            )

        # Assume usage of Redis backend
        backend = cast(RedisAsyncResultBackend, workers_broker.result_backend)

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
