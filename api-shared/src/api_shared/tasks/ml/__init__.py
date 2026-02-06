"""ML tasks that use the 'ml' broker."""

from api_shared.broker import broker_manager

# This will raise RuntimeError if ML broker is not enabled
ml_broker = broker_manager.get_broker("ml")

from api_shared.tasks.ml.ml_tasks import (
    MLInferenceResult,
    MLTrainingResult,
    ml_inference_task,
    train_model_task,
)

__all__ = [
    "MLInferenceResult",
    "MLTrainingResult",
    "ml_inference_task",
    "train_model_task",
]
