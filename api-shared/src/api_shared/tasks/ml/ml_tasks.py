"""
ML inference task definitions.

This module defines ML tasks that are implemented in the ML worker package.
"""

from pydantic import BaseModel

from api_shared.broker import broker_manager

ml_broker = broker_manager.get_broker("ml")


class MLInferenceResult(BaseModel):
    """Result model for ML inference tasks."""

    model_id: str
    predictions: list
    confidence: float
    status: str


@ml_broker.task(task_name="ml_inference")
async def ml_inference_task(model_id: str, input_data: dict) -> MLInferenceResult:
    """
    Perform ML inference on input data.

    This task is implemented in the ML worker package.
    It will be processed by ML workers listening to the 'taskiq_ml' queue.

    Args:
        model_id: Identifier for the ML model to use.
        input_data: Input data for inference.

    Returns:
        Inference results with predictions and confidence scores.
    """
    raise NotImplementedError("This task is implemented in the ML worker package")


class MLTrainingResult(BaseModel):
    """Result model for ML training tasks."""

    dataset_id: str
    model_id: str
    training_metrics: dict
    status: str


@ml_broker.task(task_name="train_model")
async def train_model_task(
    dataset_id: str,
    model_config: dict,
    hyperparameters: dict,
) -> MLTrainingResult:
    """
    Train an ML model with given configuration.

    This task is implemented in the ML worker package.
    It will be processed by ML workers listening to the 'taskiq_ml' queue.

    Args:
        dataset_id: Identifier for the training dataset.
        model_config: Model architecture configuration.
        hyperparameters: Training hyperparameters.

    Returns:
        Training results and model metadata.
    """
    raise NotImplementedError("This task is implemented in the ML worker package")
