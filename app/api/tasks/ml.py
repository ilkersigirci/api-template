"""ML broker task endpoints."""

from typing import cast

from api_shared.services.redis.deps import get_redis_pool
from api_shared.tasks.ml import ml_inference_task, train_model_task
from api_shared.utils.task_status_manager import TaskStatus, TaskStatusManager
from fastapi import APIRouter, HTTPException
from redis.asyncio import Redis
from taskiq import ResultGetError
from taskiq_redis import RedisAsyncResultBackend

from app.api.tasks.schemas import (
    MLInferenceParams,
    MLTrainingParams,
    TaskOut,
    TaskResult,
)
from app.core.broker import broker_manager

router = APIRouter(prefix="/tasks/ml", tags=["ml-tasks"])

ml_broker = broker_manager.get_broker("ml")


@router.post("/inference", response_model=TaskOut)
async def trigger_ml_inference(params: MLInferenceParams) -> TaskOut:
    """
    Trigger an ML inference task.

    This task will be processed by ML workers listening to the 'taskiq_ml' queue.
    """
    task = await ml_inference_task.kiq(
        model_id=params.model_id,
        input_data=params.input_data,
    )
    return TaskOut(task_id=task.task_id)


@router.post("/training", response_model=TaskOut)
async def trigger_ml_training(params: MLTrainingParams) -> TaskOut:
    """
    Trigger an ML model training task.

    This task will be processed by ML workers listening to the 'taskiq_ml' queue.
    """
    task = await train_model_task.kiq(
        dataset_id=params.dataset_id,
        model_config=params.model_configuration,
        hyperparameters=params.hyperparameters,
    )
    return TaskOut(task_id=task.task_id)


@router.get("/{task_id}", response_model=TaskResult)
async def get_ml_task_result(task_id: str) -> TaskResult:
    """
    Get the status and result of an ML task.
    """
    try:
        # Get Redis pool to fetch task metadata
        redis_pool = await get_redis_pool()
        async with Redis.from_pool(redis_pool) as redis_client:
            metadata = await TaskStatusManager.get_task_metadata(task_id, redis_client)

        # If no metadata found, task doesn't exist
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
        backend = cast(RedisAsyncResultBackend, ml_broker.result_backend)

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
