import torch
from api_shared.tasks.ml import TRAIN_MODEL_TASK, MLTrainingInput, MLTrainingResult
from hatchet_sdk import Context
from loguru import logger
from torch import nn, optim

from worker.runner import hatchet


class SimpleLinearModel(nn.Module):
    def __init__(self, input_size: int, output_size: int):
        super().__init__()
        self.linear = nn.Linear(input_size, output_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.linear(x)


@hatchet.task(
    name=TRAIN_MODEL_TASK,
    input_validator=MLTrainingInput,
)
async def train_model_task(input: MLTrainingInput, ctx: Context) -> MLTrainingResult:
    logger.info("Starting model training for dataset: {}", input.dataset_id)
    ctx.log(f"Model training started for dataset_id={input.dataset_id}")

    input_size = input.model_configuration.get("input_size", 10)
    output_size = input.model_configuration.get("output_size", 1)
    epochs = input.hyperparameters.get("epochs", 5)
    lr = input.hyperparameters.get("learning_rate", 0.01)
    batch_size = input.hyperparameters.get("batch_size", 32)

    model = SimpleLinearModel(input_size, output_size)
    criterion = nn.MSELoss()
    optimizer = optim.SGD(model.parameters(), lr=lr)

    x_train = torch.randn(batch_size, input_size)
    y_train = torch.randn(batch_size, output_size)

    final_loss = 0.0
    for epoch in range(epochs):
        optimizer.zero_grad()
        outputs = model(x_train)
        loss = criterion(outputs, y_train)
        loss.backward()
        optimizer.step()
        final_loss = loss.item()
        logger.debug("Epoch {}/{} , Loss: {:.4f}", epoch + 1, epochs, final_loss)

    result = MLTrainingResult(
        dataset_id=input.dataset_id,
        model_id=f"model_{input.dataset_id}_v1",
        training_metrics={
            "final_loss": final_loss,
            "epochs": epochs,
            "learning_rate": lr,
        },
    )

    logger.info("Model training completed")
    return result
