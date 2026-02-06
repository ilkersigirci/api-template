import torch
import torch.nn as nn
import torch.optim as optim
from api_shared.tasks.ml import MLTrainingResult
from loguru import logger

from worker.broker import broker


class SimpleLinearModel(nn.Module):
    def __init__(self, input_size: int, output_size: int):
        super().__init__()
        self.linear = nn.Linear(input_size, output_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.linear(x)


@broker.task(task_name="train_model")
async def train_model_task(
    dataset_id: str,
    model_config: dict,
    hyperparameters: dict,
) -> MLTrainingResult:
    """
    Train an ML model with given configuration.

    Args:
        dataset_id: Identifier for the training dataset.
        model_config: Model architecture configuration.
        hyperparameters: Training hyperparameters.

    Returns:
        Training results and model metadata.
    """
    logger.info(f"Starting model training for dataset: {dataset_id}")

    input_size = model_config.get("input_size", 10)
    output_size = model_config.get("output_size", 1)
    epochs = hyperparameters.get("epochs", 5)
    lr = hyperparameters.get("learning_rate", 0.01)
    batch_size = hyperparameters.get("batch_size", 32)

    model = SimpleLinearModel(input_size, output_size)
    criterion = nn.MSELoss()
    optimizer = optim.SGD(model.parameters(), lr=lr)

    X_train = torch.randn(batch_size, input_size)
    y_train = torch.randn(batch_size, output_size)

    final_loss = 0.0
    for epoch in range(epochs):
        optimizer.zero_grad()
        outputs = model(X_train)
        loss = criterion(outputs, y_train)
        loss.backward()
        optimizer.step()
        final_loss = loss.item()
        logger.debug(f"Epoch {epoch + 1}/{epochs}, Loss: {final_loss:.4f}")

    result = MLTrainingResult(
        dataset_id=dataset_id,
        model_id=f"model_{dataset_id}_v1",
        training_metrics={
            "final_loss": final_loss,
            "epochs": epochs,
            "learning_rate": lr,
        },
        status="completed",
    )

    logger.info("Model training completed")
    return result
