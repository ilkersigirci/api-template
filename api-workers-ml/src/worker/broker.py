"""
ML Worker-specific broker initialization.

This module ensures that OpenTelemetry is set up before the broker is initialized.
Import the broker from this module in ML worker code.
"""

from api_shared.core.telemetry import setup_opentelemetry_worker

from worker.core.settings import settings

# NOTE: Should be called before importing the broker
setup_opentelemetry_worker(settings)

from api_shared.broker import broker_manager  # noqa: E402

broker = broker_manager.get_broker("ml")
scheduler = broker_manager.scheduler

__all__ = ["broker", "scheduler"]
