"""OpenTelemetry setup for traces and correlation IDs."""
import os
from contextvars import ContextVar

# Set to disable OTel when OTEL_EXPORTER_OTLP_ENDPOINT is not set
OTEL_ENABLED = bool(os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"))

correlation_id_var: ContextVar[str | None] = ContextVar("correlation_id", default=None)


def get_correlation_id() -> str | None:
    return correlation_id_var.get()


def set_correlation_id(cid: str) -> None:
    correlation_id_var.set(cid)


def init_otel() -> None:
    """Initialize OpenTelemetry if OTEL_EXPORTER_OTLP_ENDPOINT is set."""
    if not OTEL_ENABLED:
        return
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

        provider = TracerProvider()
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
        trace.set_tracer_provider(provider)
    except ImportError:
        pass
