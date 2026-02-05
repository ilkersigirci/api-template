"""Worker tasks that use the 'workers' broker."""

from api_shared.broker import broker_manager

# This will raise RuntimeError if workers broker is not enabled
workers_broker = broker_manager.get_broker("workers")

from api_shared.tasks.workers.complex_task import (
    LongRunningProcessResult,
    long_running_process,
)
from api_shared.tasks.workers.dummy import add_one, add_one_with_retry
from api_shared.tasks.workers.failing_task import failing_process
from api_shared.tasks.workers.pydantic_parse_task import (
    NestedModel,
    PydanticParseInput,
    PydanticParseResult,
    pydantic_parse_check,
)

__all__ = [
    "LongRunningProcessResult",
    "NestedModel",
    "PydanticParseInput",
    "PydanticParseResult",
    "add_one",
    "add_one_with_retry",
    "failing_process",
    "long_running_process",
    "pydantic_parse_check",
]
