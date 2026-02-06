"""ML broker task endpoints."""

from typing import cast

from api_shared.tasks.ml import ml_inference_task, train_model_task
from fastapi import APIRouter, HTTPException
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
        # Check if the result backend is configured
        if not ml_broker.result_backend:
            raise HTTPException(
                status_code=500, detail="Result backend is not configured"
            )

        # Assume usage of Redis backend
        backend = cast(RedisAsyncResultBackend, ml_broker.result_backend)

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
