# SentryKit Overview

SentryKit provides a policy-driven guard engine that inspects every step of an agent run. It ingests the user goal, system constraints, retrieved documents, tool calls, and final answer, then surfaces drift, hallucinations, or unsafe behavior before the result is returned to an end user.

Unlike opaque classifiers, the runtime relies on deterministic heuristics and extractor utilities. Every finding includes the evidence and reasoning that triggered it, which keeps post-incident reviews grounded and auditable.

## Key capabilities

- Deterministic drift, hallucination, poisoning, jailbreak, tool firewall, and data leak checks
- Structured verdicts with JSON metadata and ready-to-share HTML reports
- Policy objects that capture organization-specific allow-lists and thresholds
- Adapters for popular agent frameworks so one set of rules covers multiple stacks

Head to the [examples](examples.md) section for offline demos or explore the [core API](core_api.md) reference for integration details.

## Interactive demo

Install the optional `demo` extra and launch the FastAPI UI to walk through three contrasting agent scenarios. Each button spins up a `GuardEngine` evaluation, highlights the triggered findings, and links to the rendered HTML audit report.

```bash
pip install -e ".[demo]"
uvicorn demo_app.main:app --reload
```
