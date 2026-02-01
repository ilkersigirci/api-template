import logfire
from api_shared.core.settings import OLTPLogMethod
from fastapi import FastAPI
from loguru import logger  # noqa: F401
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
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

from app.core.settings import settings


def setup_opentelemetry(app):  # pragma: no cover
    """Setup OpenTelemetry instrumentation for FastAPI."""
    if settings.OLTP_LOG_METHOD == OLTPLogMethod.NONE:
        return

    excluded_endpoints = [
        app.url_path_for("health_check"),
        app.url_path_for("openapi"),
        app.url_path_for("swagger_ui_html"),
        app.url_path_for("swagger_ui_redirect"),
        app.url_path_for("redoc_html"),
        "/metrics",
    ]
    excluded_urls = ",".join(excluded_endpoints)

    if settings.OLTP_LOG_METHOD == OLTPLogMethod.LOGFIRE:
        logfire.configure(environment=settings.ENVIRONMENT.value)

        logfire.instrument_system_metrics()

        logfire.instrument_httpx()

        logfire.instrument_fastapi(app, excluded_urls=excluded_urls)
        logfire.instrument_redis()

        # FIXME: Breaks the loguru logger format. Fix this
        # if settings.OLTP_STD_LOGGING_ENABLED is True:
        #     logger.configure(handlers=[logfire.loguru_handler()])

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
    otlp_exporter = OTLPSpanExporter(endpoint=settings.OTLP_ENDPOINT, insecure=True)
    trace_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    FastAPIInstrumentor.instrument_app(
        app, tracer_provider=trace_provider, excluded_urls=excluded_urls
    )

    RedisInstrumentor().instrument(tracer_provider=trace_provider)

    # Instrument Python logging
    if settings.OLTP_STD_LOGGING_ENABLED is True:
        LoggingInstrumentor().instrument(tracer_provider=trace_provider)

    # Set the trace provider as the global default
    trace.set_tracer_provider(trace_provider)


def stop_opentelemetry(app: FastAPI) -> None:  # pragma: no cover
    """Disables opentelemetry instrumentation."""
    if settings.OLTP_LOG_METHOD in [OLTPLogMethod.NONE, OLTPLogMethod.LOGFIRE]:
        return

    FastAPIInstrumentor().uninstrument_app(app)
    RedisInstrumentor().uninstrument()


def setup_prometheus(app: FastAPI) -> None:  # pragma: no cover
    """Enables prometheus integration."""
    PrometheusFastApiInstrumentator(should_group_status_codes=False).instrument(
        app,
    ).expose(app, should_gzip=True, name="prometheus_metrics")
