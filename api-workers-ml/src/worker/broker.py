"""
ML Worker-specific broker initialization.

This module ensures that OpenTelemetry is set up before the broker is initialized.
Import the broker from this module in ML worker code.
"""

from worker.core.telemetry import setup_opentelemetry_worker

# NOTE: Should be called before importing the broker
setup_opentelemetry_worker()

from api_shared.broker import ml_broker as broker, scheduler  # noqa: E402

__all__ = ["broker", "scheduler"]
