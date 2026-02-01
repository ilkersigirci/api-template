import random
from datetime import datetime

from loguru import logger

from api_template_shared.broker import broker


@broker.task
async def add_one(value: int) -> int:
    return value + 1


@broker.task(retry_on_error=True, max_retries=5, delay=15)
async def add_one_with_retry(value: int) -> int:
    # Randomly fail 50% of the time
    if random.random() < 0.5:  # noqa: PLR2004
        raise RuntimeError("Random failure in add_one_with_retry")

    return value + 1


@broker.task(
    schedule=[
        {
            "cron": "*/2 * * * *",  # type: str, either cron or time should be specified. Runs every 2 minutes.
            "cron_offset": None,  # type: str | timedelta | None, can be omitted.
            "time": None,  # type: datetime | None, either cron or time should be specified.
            "args": [1],  # type List[Any] | None, can be omitted.
            "kwargs": {},  # type: Dict[str, Any] | None, can be omitted.
            "labels": {},  # type: Dict[str, Any] | None, can be omitted.
        }
    ]
)
async def add_one_scheduled(value: int) -> int:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Current time: {current_time}")

    return value + 1


@broker.task
async def parse_int(val: str) -> int:
    return int(val)
