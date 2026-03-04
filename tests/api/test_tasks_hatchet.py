import pytest
from fastapi import FastAPI
from hatchet_sdk.clients.rest.models.v1_task_status import V1TaskStatus
from httpx import AsyncClient
from starlette import status


@pytest.mark.anyio
async def test_trigger_general_task(
    fastapi_app: FastAPI, client: AsyncClient, fake_hatchet
) -> None:
    url = fastapi_app.url_path_for("trigger_task")
    response = await client.post(url, json={"duration": 2})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["metadata"]["id"] == "long_running_process-run-id"
    assert fake_hatchet.stubs.created["long_running_process"].last_input.duration == 2


@pytest.mark.anyio
async def test_general_task_result_completed(
    fastapi_app: FastAPI, client: AsyncClient, fake_hatchet
) -> None:
    fake_hatchet.runs.status = V1TaskStatus.COMPLETED
    fake_hatchet.runs.result_payload = {"elapsed": 1.23}

    url = fastapi_app.url_path_for("get_task_result", task_id="some-run-id")
    response = await client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["run"]["status"] == "COMPLETED"
    assert response.json()["run"]["output"]["elapsed"] == 1.23


@pytest.mark.anyio
async def test_trigger_ml_training_task(
    fastapi_app: FastAPI, client: AsyncClient, fake_hatchet
) -> None:
    payload = {
        "dataset_id": "ds-1",
        "model_configuration": {"input_size": 8, "output_size": 2},
        "hyperparameters": {"epochs": 1, "learning_rate": 0.01, "batch_size": 4},
    }
    url = fastapi_app.url_path_for("trigger_ml_training")
    response = await client.post(url, json=payload)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["metadata"]["id"] == "train_model-run-id"
    assert fake_hatchet.stubs.created["train_model"].last_input.dataset_id == "ds-1"


@pytest.mark.anyio
async def test_ml_task_result_failed(
    fastapi_app: FastAPI, client: AsyncClient, fake_hatchet
) -> None:
    fake_hatchet.runs.status = V1TaskStatus.FAILED
    fake_hatchet.runs.error_status = "FAILED"

    url = fastapi_app.url_path_for("get_ml_task_result", task_id="some-run-id")
    response = await client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["run"]["status"] == "FAILED"
    assert response.json()["run"]["errorMessage"] == "FAILED"
