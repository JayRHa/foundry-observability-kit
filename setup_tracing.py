"""Tracing bootstrap for Microsoft Foundry agent code.

Call init_tracing() once at startup. Two modes:
  - default: export to the Application Insights resource connected to your
    Foundry project (client spans get stitched to the server-side traces)
  - local=True: export OTLP to localhost:4317 (e.g. the Aspire dashboard)
    for instant feedback while developing, no cloud round trip
"""
import os

from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()


def init_tracing(local: bool = False, capture_content: bool = False) -> None:
    """Instrument azure-ai-projects agent + inference calls with OpenTelemetry.

    capture_content=True records full prompts/responses in spans.
    Keep it OFF in production - it stores user content in telemetry.
    """
    os.environ.setdefault("AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING", "true")
    if capture_content:
        os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "true"

    if local:
        _init_local_otlp()
    else:
        _init_azure_monitor()

    from azure.ai.projects.telemetry import AIProjectInstrumentor
    AIProjectInstrumentor().instrument()


def _init_azure_monitor() -> None:
    from azure.ai.projects import AIProjectClient
    from azure.monitor.opentelemetry import configure_azure_monitor

    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    project = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
    conn = project.telemetry.get_application_insights_connection_string()
    if not conn:
        raise RuntimeError(
            "No Application Insights connected to the Foundry project. "
            "Portal: Agents > Traces > Connect.")
    configure_azure_monitor(connection_string=conn)


def _init_local_otlp() -> None:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor

    provider = TracerProvider(
        resource=Resource.create({"service.name": os.environ.get("OTEL_SERVICE_NAME", "foundry-agent-dev")}))
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
    trace.set_tracer_provider(provider)


if __name__ == "__main__":
    # smoke test: local mode does not need any Azure resources
    init_tracing(local=True, capture_content=True)
    print("tracing initialized (local OTLP) - point an Aspire dashboard at :4317")
