import pytest
from api_shared.tasks.ml import MLInferenceInput, MLTrainingInput
from worker.tasks.ml_inference import ml_inference_task
from worker.tasks.ml_training import train_model_task


@pytest.mark.anyio
async def test_ml_inference_logic() -> None:
    payload = MLInferenceInput(
        model_id="model-1",
        input_data={"features": [0.1, 0.2, 0.3], "num_classes": 3},
    )

    result = await ml_inference_task.aio_mock_run(input=payload)

    assert result.model_id == "model-1"
    assert len(result.predictions) == 3
    assert 0 <= result.confidence <= 1


@pytest.mark.anyio
async def test_ml_training_logic() -> None:
    payload = MLTrainingInput(
        dataset_id="dataset-1",
        model_configuration={"input_size": 4, "output_size": 1},
        hyperparameters={"epochs": 1, "learning_rate": 0.01, "batch_size": 4},
    )

    result = await train_model_task.aio_mock_run(input=payload)

    assert result.dataset_id == "dataset-1"
    assert result.model_id.startswith("model_dataset-1")
    assert "final_loss" in result.training_metrics
