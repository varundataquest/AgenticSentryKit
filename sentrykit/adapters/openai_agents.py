"""OpenAI Agents SDK integration."""

from __future__ import annotations

import importlib
from typing import Any, Dict

from ..claim_extractors.autoclaims import generate_claims
from ..engine import GuardEngine
from ..errors import AdapterImportError
from ..models import ContextChunk, RunInput, RunOutput, ToolCall
from ..policy import Policy


def _ensure_dependency() -> None:
    if importlib.util.find_spec("openai") is None:
        raise AdapterImportError(
            "OpenAI Agents SDK is not installed. Install sentrykit with the 'openai_agents' extra."
        )


def sentrykit_guardrail(
    ctx: Dict[str, Any],
    agent: Any,
    output: Dict[str, Any],
    *,
    engine: GuardEngine | None = None,
    policy: Policy | None = None,
) -> Dict[str, Any]:
    """Evaluate an agent output and return guardrail metadata."""

    _ensure_dependency()
    policy = policy or Policy()
    engine = engine or GuardEngine(policy)

    goal = str(ctx.get("goal", ""))
    constraints = [str(item) for item in ctx.get("constraints", [])]
    messages = [(str(msg.get("role", "user")), str(msg.get("content", ""))) for msg in ctx.get("messages", [])]
    contexts = [
        ContextChunk(source=str(chunk.get("source", "unknown")), text=str(chunk.get("text", "")))
        for chunk in ctx.get("contexts", [])
    ]
    tool_calls = [
        ToolCall(name=str(call.get("name", "")), args=dict(call.get("args", {}))) for call in ctx.get("tool_calls", [])
    ]

    output_text = str(output.get("text", ""))
    claims = output.get("claims") or []
    run_output = RunOutput(text=output_text, claims=claims)
    if policy.require_claims and not run_output.claims:
        evidence_url = ctx.get("default_evidence_url")
        run_output.claims = generate_claims(run_output, evidence_url)

    run = RunInput(
        goal=goal,
        constraints=constraints,
        messages=messages,
        contexts=contexts,
        tool_calls=tool_calls,
        output=run_output,
    )
    verdict = engine.evaluate(run)
    return {
        "blocked": verdict.blocked,
        "verdict": verdict,
        "output_info": {
            "reason": verdict.reason,
            "score": verdict.score,
            "findings": [finding.details for finding in verdict.findings],
        },
    }
