"""Worker tasks that use the 'general' broker."""

from api_shared.broker import broker_manager

# This will raise RuntimeError if general broker is not enabled
workers_broker = broker_manager.get_broker("general")

from api_shared.tasks.general.complex_task import (
    LongRunningProcessResult,
    long_running_process,
)
from api_shared.tasks.general.dummy import add_one, add_one_with_retry
from api_shared.tasks.general.failing_task import failing_process
from api_shared.tasks.general.pydantic_parse_task import (
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
