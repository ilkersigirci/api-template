from api_shared.core.telemetry import setup_opentelemetry_worker
from api_shared.hatchet_client import get_hatchet

from worker.core.settings import settings

setup_opentelemetry_worker(settings)
hatchet = get_hatchet()


def build_worker(workflows: list[object]):
    return hatchet.worker(
        name=settings.HATCHET_WORKER_NAME,
        slots=settings.HATCHET_WORKER_SLOTS,
        workflows=workflows,
    )


__all__ = ["build_worker", "hatchet"]
