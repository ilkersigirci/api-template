import torch
from api_shared.tasks.ml import ML_INFERENCE_TASK, MLInferenceInput, MLInferenceResult
from hatchet_sdk import Context
from loguru import logger
from torch import nn

from worker.runner import hatchet


class SimpleModel(nn.Module):
    def __init__(self, input_size: int, output_size: int):
        super().__init__()
        self.linear = nn.Linear(input_size, output_size)
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.softmax(self.linear(x))


@hatchet.task(
    name=ML_INFERENCE_TASK,
    input_validator=MLInferenceInput,
)
async def ml_inference_task(input: MLInferenceInput, ctx: Context) -> MLInferenceResult:
    logger.info("Running ML inference with model: {}", input.model_id)
    ctx.log(f"ML inference started for model_id={input.model_id}")

    features = input.input_data.get("features", [1.0] * 10)
    input_tensor = torch.tensor([features], dtype=torch.float32)

    input_size = len(features)
    output_size = input.input_data.get("num_classes", 3)
    model = SimpleModel(input_size, output_size)
    model.eval()

    with torch.no_grad():
        output = model(input_tensor)
        predictions = output[0].tolist()
        confidence = float(torch.max(output).item())

    result = MLInferenceResult(
        model_id=input.model_id,
        predictions=predictions,
        confidence=confidence,
    )

    logger.info("ML inference completed")
    return result
