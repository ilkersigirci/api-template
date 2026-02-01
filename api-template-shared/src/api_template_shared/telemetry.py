import logfire
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
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

from api_template_shared.core.settings import OLTPLogMethod, settings


def setup_opentelemetry_worker():
    """Setup OpenTelemetry instrumentation for worker."""
    if settings.OLTP_LOG_METHOD == OLTPLogMethod.NONE:
        return

    if settings.OLTP_LOG_METHOD == OLTPLogMethod.LOGFIRE:
        logfire.configure(environment=settings.ENVIRONMENT.value)
        logfire.instrument_system_metrics()
        logfire.instrument_httpx()
        logfire.instrument_redis()

        # FIXME: Breaks the loguru logger format. Fix this
        # if settings.OLTP_STD_LOGGING_ENABLED is True:
        #     logger.configure(handlers=[logfire.loguru_handler()])

        return

    resource = Resource(
        attributes={
            SERVICE_NAME: getattr(settings, "PROJECT_NAME", "api-template-worker"),
            TELEMETRY_SDK_LANGUAGE: "python",
            DEPLOYMENT_ENVIRONMENT: settings.ENVIRONMENT,
        },
    )
    trace_provider = TracerProvider(resource=resource)
    otlp_exporter = OTLPSpanExporter(endpoint=settings.OTLP_ENDPOINT, insecure=True)
    trace_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    RedisInstrumentor().instrument(tracer_provider=trace_provider)
    if getattr(settings, "OLTP_STD_LOGGING_ENABLED", False):
        LoggingInstrumentor().instrument(tracer_provider=trace_provider)
    trace.set_tracer_provider(trace_provider)


# TODO: Does this need in the worker?
def stop_opentelemetry() -> None:  # pragma: no cover
    """Disables opentelemetry instrumentation."""
    if settings.OLTP_LOG_METHOD in [OLTPLogMethod.NONE, OLTPLogMethod.LOGFIRE]:
        return

    RedisInstrumentor().uninstrument()
