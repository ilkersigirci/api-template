"""
Worker-specific broker initialization.

This module ensures that OpenTelemetry is set up before the broker is initialized.
Import the broker from this module in worker code instead of api_template_shared.broker.
"""

from worker.core.telemetry import setup_opentelemetry_worker

# NOTE: Should be called before importing the broker
setup_opentelemetry_worker()

from api_shared.broker import broker_manager  # noqa: E402

broker = broker_manager.get_broker("workers")
scheduler = broker_manager.scheduler

__all__ = ["broker", "scheduler"]
