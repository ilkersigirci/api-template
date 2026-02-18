from functools import cache

from hatchet_sdk import Hatchet
from hatchet_sdk.opentelemetry.instrumentor import HatchetInstrumentor
from opentelemetry.trace import get_tracer_provider

from api_shared.core.settings import OLTPLogMethod, settings


@cache
def get_hatchet() -> Hatchet:
    """Return a singleton Hatchet client.

    DI wires higher-level objects (e.g., `ExternalRunner`), while this cache
    avoids re-creating the underlying Hatchet client and its connections.
    """
    hatchet = Hatchet(debug=settings.ENVIRONMENT == "dev")
    if settings.OLTP_LOG_METHOD != OLTPLogMethod.NONE:
        HatchetInstrumentor(tracer_provider=get_tracer_provider()).instrument()
    return hatchet


__all__ = ["get_hatchet"]
