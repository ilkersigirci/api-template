import torch
import torch.nn as nn
from api_shared.tasks.ml import MLInferenceResult
from loguru import logger

from worker.broker import broker


class SimpleModel(nn.Module):
    def __init__(self, input_size: int, output_size: int):
        super().__init__()
        self.linear = nn.Linear(input_size, output_size)
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.softmax(self.linear(x))


@broker.task(task_name="ml_inference")
async def ml_inference_task(model_id: str, input_data: dict) -> MLInferenceResult:
    """
    Perform ML inference on input data.

    Args:
        model_id: Identifier for the ML model to use.
        input_data: Input data for inference.

    Returns:
        Inference results.
    """
    logger.info(f"Running ML inference with model: {model_id}")

    features = input_data.get("features", [1.0] * 10)
    input_tensor = torch.tensor([features], dtype=torch.float32)

    input_size = len(features)
    output_size = input_data.get("num_classes", 3)
    model = SimpleModel(input_size, output_size)
    model.eval()

    with torch.no_grad():
        output = model(input_tensor)
        predictions = output[0].tolist()
        confidence = float(torch.max(output).item())

    result = MLInferenceResult(
        model_id=model_id,
        predictions=predictions,
        confidence=confidence,
        status="success",
    )

    logger.info("ML inference completed")
    return result
