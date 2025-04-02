import pytest
from app.worker.tasks.dummy import add_one


@pytest.mark.anyio
async def test_add_one():
    # Test with zero
    assert await add_one(0) == 1

    # Test with positive number
    assert await add_one(10) == 11

    # Test with negative number
    assert await add_one(-2) == -1


@pytest.mark.anyio
async def test_add_one_kiq():
    task = await add_one.kiq(10)
    result = await task.wait_result()

    assert result.return_value == 11
