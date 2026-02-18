import asyncio

import pytest
from api_shared.tasks.general import (
    FailingProcessInput,
    LongRunningProcessInput,
    NestedModel,
    PydanticParseInput,
)
from worker.tasks.complex_task import long_running_process
from worker.tasks.failing_task import failing_process
from worker.tasks.pydantic_parse_task import pydantic_parse_check


@pytest.mark.anyio
async def test_long_running_process_logic(monkeypatch: pytest.MonkeyPatch) -> None:
    async def no_sleep(_: float) -> None:
        return None

    monkeypatch.setattr(asyncio, "sleep", no_sleep)
    result = await long_running_process.aio_mock_run(
        input=LongRunningProcessInput(duration=1)
    )

    assert result.end_time >= result.start_time
    assert result.elapsed >= 0


@pytest.mark.anyio
async def test_failing_process_logic() -> None:
    with pytest.raises(RuntimeError, match="boom"):
        await failing_process.aio_mock_run(
            input=FailingProcessInput(error_message="boom")
        )


@pytest.mark.anyio
async def test_pydantic_parse_logic() -> None:
    payload = PydanticParseInput(
        text="hello",
        count=3,
        nested=NestedModel(name="n1", value=4, tags=["x"]),
    )

    result = await pydantic_parse_check.aio_mock_run(input=payload)

    assert result.received_text == "hello"
    assert result.received_count == 3
    assert result.doubled_count == 6
    assert result.received_nested.name == "n1"
