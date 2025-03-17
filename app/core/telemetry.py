from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import (
    DEPLOYMENT_ENVIRONMENT,
    SERVICE_NAME,
    TELEMETRY_SDK_LANGUAGE,
    Resource,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_fastapi_instrumentator.instrumentation import (
    PrometheusFastApiInstrumentator,
)

from app.core.config import settings


def setup_opentelemetry(app):  # pragma: no cover
    """Setup OpenTelemetry instrumentation for FastAPI."""
    if not settings.TELEMETRY_ENABLED:
        return

    resource = Resource(
        attributes={
            SERVICE_NAME: settings.PROJECT_NAME,
            TELEMETRY_SDK_LANGUAGE: "python",
            DEPLOYMENT_ENVIRONMENT: settings.ENVIRONMENT,
        },
    )

    trace_provider = TracerProvider(resource=resource)

    # Create and register OTLP exporter
    if settings.OTLP_ENDPOINT:
        otlp_exporter = OTLPSpanExporter(endpoint=settings.OTLP_ENDPOINT, insecure=True)
        trace_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    excluded_endpoints = [
        app.url_path_for("health_check"),
        app.url_path_for("openapi"),
        app.url_path_for("swagger_ui_html"),
        app.url_path_for("swagger_ui_redirect"),
        app.url_path_for("redoc_html"),
        "/metrics",
    ]

    FastAPIInstrumentor.instrument_app(
        app,
        tracer_provider=trace_provider,
        excluded_urls=",".join(excluded_endpoints),
    )

    # Instrument Python logging
    if settings.TELEMETRY_LOGGING_ENABLED:
        LoggingInstrumentor().instrument(tracer_provider=trace_provider)

    # Set the trace provider as the global default
    trace.set_tracer_provider(trace_provider)


def stop_opentelemetry(app: FastAPI) -> None:  # pragma: no cover
    """Disables opentelemetry instrumentation."""
    if not settings.TELEMETRY_ENABLED:
        return

    FastAPIInstrumentor().uninstrument_app(app)


def setup_prometheus(app: FastAPI) -> None:  # pragma: no cover
    """Enables prometheus integration."""
    PrometheusFastApiInstrumentator(should_group_status_codes=False).instrument(
        app,
    ).expose(app, should_gzip=True, name="prometheus_metrics")
