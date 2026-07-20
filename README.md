<!-- jr-brand:start -->
<div align="center">
  <a href="https://jannikreinhard.com/">
    <img src="https://raw.githubusercontent.com/JayRHa/.github/main/assets/readme/tool.svg" alt="Jannik Reinhard — AI, Cloud and Endpoint Management" width="100%">
  </a>
  <h1>Microsoft Foundry Observability Kit</h1>
  <p><strong>Production observability kit for Microsoft Foundry agents: OpenTelemetry tracing bootstrap, continuous evaluation rules and a KQL query pack for Application Insights.</strong></p>
  <p>
  <a href="https://jannikreinhard.com/"><img src="https://img.shields.io/badge/Website-0A5FC0?style=flat-square&amp;logo=wordpress&amp;logoColor=white" alt="Website"></a>
  <a href="https://github.com/JayRHa"><img src="https://img.shields.io/badge/GitHub-081427?style=flat-square&amp;logo=github&amp;logoColor=white" alt="GitHub"></a>
  <a href="https://www.linkedin.com/in/jannik-r/"><img src="https://img.shields.io/badge/LinkedIn-0795FF?style=flat-square&amp;logo=linkedin&amp;logoColor=white" alt="LinkedIn"></a>
  <a href="https://x.com/jannik_reinhard"><img src="https://img.shields.io/badge/X-081427?style=flat-square&amp;logo=x&amp;logoColor=white" alt="X"></a>
  <a href="https://www.youtube.com/@ModernDevMgmt/featured"><img src="https://img.shields.io/badge/YouTube-0A5FC0?style=flat-square&amp;logo=youtube&amp;logoColor=white" alt="YouTube"></a>
</p>
  <p><sub>Tool · App · CLI · Python · Practical by design</sub></p>
</div>
<!-- jr-brand:end -->

## Overview

Everything I wire up before a **Microsoft Foundry** agent goes to production:
client-side OpenTelemetry tracing, a continuous evaluation rule on live
traffic, and a KQL query pack for Application Insights.

Foundry stores agent traces in Application Insights using the OpenTelemetry
GenAI semantic conventions. That means the interesting questions — where does
the latency come from, which tool calls fail, what does a run cost — are one
KQL query away. This kit collects the pieces so you do not rebuild them per
project.

## What Is in Here

| Piece | File | What it gives you |
|-------|------|-------------------|
| Tracing bootstrap | `setup_tracing.py` | One import to instrument your agent code (Azure Monitor or local OTLP/Aspire) |
| Continuous evaluation | `continuous_eval.py` | Creates an evaluation rule that scores sampled live traffic (groundedness, task adherence, safety) |
| Query pack | `queries/*.kql` | Ready-made App Insights queries: latency breakdown, tool errors, token cost, eval scores |

## Prerequisites

- Python 3.10+, `az login`
- A Microsoft Foundry project with an **Application Insights resource
  connected** (portal: Agents > Traces > Connect) — server-side traces then
  flow with zero code
- For continuous evaluation: the project managed identity needs the
  **Foundry User** role
- To read traces: **Log Analytics Reader** on the App Insights resource

## Quickstart

```bash
git clone https://github.com/JayRHa/foundry-observability-kit.git
cd foundry-observability-kit
pip install -r requirements.txt
cp .env.example .env
```

### 1. Instrument your agent code

```python
from setup_tracing import init_tracing

init_tracing()          # Azure Monitor via the project's App Insights
# init_tracing(local=True)   # or: local OTLP endpoint (Aspire dashboard)

# ... your azure-ai-projects agent code runs traced from here on
```

### 2. Put continuous evaluation on live traffic

```bash
python continuous_eval.py --agent my-agent \
  --evaluators groundedness task_adherence violence \
  --max-hourly-runs 100
```

Scores land in Application Insights next to the traces.

### 3. Ask the telemetry questions

Open Application Insights > Logs and paste anything from `queries/`:

- `latency_breakdown.kql` — where runs spend their time (model vs tools)
- `tool_errors.kql` — failing tool calls with arguments
- `token_usage.kql` — token consumption per agent/day, cost estimate
- `eval_scores.kql` — continuous evaluation score trend
- `slow_runs.kql` — P95 outliers with full span context

## Production notes

- **Content capture off in prod.** `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT`
  logs full prompts/responses — great in dev, a privacy problem in production.
  `init_tracing()` keeps it off unless you opt in.
- **Sample, don't evaluate everything.** Evaluators cost tokens; 100 runs/hour
  is the default ceiling and usually plenty for a regression signal.
- **Alert on trends:** evaluation score regression, run success rate < 95%,
  token anomalies. The queries in this repo are written to be alert-ready.

## Related

- Blog: [jannikreinhard.com](https://jannikreinhard.com) — Microsoft Foundry
  observability deep dive
- [Trace agents in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/trace-agent-setup)
- [Monitor agents dashboard](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/how-to-monitor-agents-dashboard)

## Disclaimer

Community tooling, not an official Microsoft project. The GenAI tracing
switch and evaluation rules API are preview surfaces — span names and
attributes may still evolve.

## License

MIT — see [LICENSE](LICENSE).

<!-- jr-brand-footer:start -->

---

<div align="center">
  <p><sub>Built and maintained by <a href="https://jannikreinhard.com/">Jannik Reinhard</a> · Microsoft MVP for Security and AI Platform.</sub></p>
  <p><a href="https://www.buymeacoffee.com/jannikreinf">Support the open-source work</a></p>
  <p><strong>Stay healthy, Cheers Jannik</strong></p>
</div>

<!-- jr-brand-footer:end -->
