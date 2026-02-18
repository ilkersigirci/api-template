from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import pytest
from app.api.tasks.deps import get_runner
from fastapi import FastAPI
from hatchet_sdk.clients.rest.models.api_resource_meta import APIResourceMeta
from hatchet_sdk.clients.rest.models.v1_task_status import V1TaskStatus
from hatchet_sdk.clients.rest.models.v1_workflow_run import V1WorkflowRun
from hatchet_sdk.clients.rest.models.v1_workflow_run_details import V1WorkflowRunDetails
from httpx import AsyncClient
from starlette import status


@dataclass
class FakeRunRef:
    workflow_run_id: str
    result_payload: Any = None

    async def aio_result(self) -> Any:
        return self.result_payload


class FakeStub:
    def __init__(self, workflow_run_id: str):
        self._workflow_run_id = workflow_run_id
        self.last_input: Any = None

    async def aio_run_no_wait(self, input: Any) -> FakeRunRef:
        self.last_input = input
        return FakeRunRef(workflow_run_id=self._workflow_run_id)


class FakeRuns:
    def __init__(self):
        self.status: V1TaskStatus = V1TaskStatus.QUEUED
        self.result_payload: Any = None
        self.error_status: str = "FAILED"

    async def aio_get_status(self, workflow_run_id: str) -> V1TaskStatus:
        return self.status

    def get_run_ref(self, workflow_run_id: str) -> FakeRunRef:
        return FakeRunRef(workflow_run_id=workflow_run_id, result_payload=self.result_payload)

    async def aio_get(self, workflow_run_id: str) -> V1WorkflowRunDetails:
        now = datetime.now(timezone.utc)
        output = self.result_payload if self.status == V1TaskStatus.COMPLETED else {}
        error_message = self.error_status if self.status == V1TaskStatus.FAILED else None

        run = V1WorkflowRun(
            metadata=APIResourceMeta(
                id=workflow_run_id,
                createdAt=now,
                updatedAt=now,
            ),
            status=self.status,
            tenantId="00000000-0000-0000-0000-000000000000",
            displayName=workflow_run_id,
            workflowId="workflow-1",
            output=output,
            errorMessage=error_message,
            input={},
            createdAt=now,
        )
        return V1WorkflowRunDetails(
            run=run,
            taskEvents=[],
            shape=[],
            tasks=[],
        )


class FakeStubs:
    def __init__(self):
        self.created: dict[str, FakeStub] = {}

    def task(self, name: str, **kwargs: Any) -> FakeStub:
        stub = FakeStub(workflow_run_id=f"{name}-run-id")
        self.created[name] = stub
        return stub


class FakeHatchet:
    def __init__(self):
        self.stubs = FakeStubs()
        self.runs = FakeRuns()


class FakeExternalRunner:
    def __init__(self, hatchet: FakeHatchet):
        self.hatchet = hatchet

    async def trigger_task(
        self,
        *,
        name: str,
        input: Any,
        input_validator: type[Any] | None = None,
        output_validator: type[Any] | None = None,
    ) -> V1WorkflowRun:
        stub = self.hatchet.stubs.task(
            name=name,
            input_validator=input_validator,
            output_validator=output_validator,
        )
        run_ref = await stub.aio_run_no_wait(input=input)
        return (await self.hatchet.runs.aio_get(run_ref.workflow_run_id)).run

    async def get_task(self, task_id: str) -> V1WorkflowRunDetails:
        return await self.hatchet.runs.aio_get(task_id)


@pytest.fixture
def fake_hatchet(fastapi_app: FastAPI) -> FakeHatchet:
    fake = FakeHatchet()
    runner = FakeExternalRunner(fake)
    fastapi_app.dependency_overrides[get_runner] = lambda: runner
    return fake


@pytest.mark.anyio
async def test_trigger_general_task(
    fastapi_app: FastAPI, client: AsyncClient, fake_hatchet: FakeHatchet
) -> None:
    response = await client.post("/api/v1/tasks/general/long-running", json={"duration": 2})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["metadata"]["id"] == "long_running_process-run-id"
    assert fake_hatchet.stubs.created["long_running_process"].last_input.duration == 2


@pytest.mark.anyio
async def test_general_task_result_completed(client: AsyncClient, fake_hatchet: FakeHatchet) -> None:
    fake_hatchet.runs.status = V1TaskStatus.COMPLETED
    fake_hatchet.runs.result_payload = {"elapsed": 1.23}

    response = await client.get("/api/v1/tasks/general/some-run-id")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["run"]["status"] == "COMPLETED"
    assert response.json()["run"]["output"]["elapsed"] == 1.23


@pytest.mark.anyio
async def test_trigger_ml_training_task(client: AsyncClient, fake_hatchet: FakeHatchet) -> None:
    payload = {
        "dataset_id": "ds-1",
        "model_configuration": {"input_size": 8, "output_size": 2},
        "hyperparameters": {"epochs": 1, "learning_rate": 0.01, "batch_size": 4},
    }
    response = await client.post("/api/v1/tasks/ml/training", json=payload)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["metadata"]["id"] == "train_model-run-id"
    assert fake_hatchet.stubs.created["train_model"].last_input.dataset_id == "ds-1"


@pytest.mark.anyio
async def test_ml_task_result_failed(client: AsyncClient, fake_hatchet: FakeHatchet) -> None:
    fake_hatchet.runs.status = V1TaskStatus.FAILED
    fake_hatchet.runs.error_status = "FAILED"

    response = await client.get("/api/v1/tasks/ml/some-run-id")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["run"]["status"] == "FAILED"
    assert response.json()["run"]["errorMessage"] == "FAILED"
