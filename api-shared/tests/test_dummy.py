from hatchet_sdk.clients.rest.models.v1_task_status import V1TaskStatus


def test_hatchet_status_values():
    assert V1TaskStatus.QUEUED.value == "QUEUED"
    assert V1TaskStatus.RUNNING.value == "RUNNING"
    assert V1TaskStatus.COMPLETED.value == "COMPLETED"
    assert V1TaskStatus.FAILED.value == "FAILED"
    assert V1TaskStatus.CANCELLED.value == "CANCELLED"
