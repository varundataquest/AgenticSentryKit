"""AWS Strands Agents integration."""

from __future__ import annotations

import importlib
from typing import Any, Dict

from ..engine import GuardEngine
from ..errors import AdapterImportError, PolicyViolationError
from ..models import ContextChunk, RunInput, RunOutput, ToolCall
from ..policy import Policy


def _ensure_dependency() -> None:
    if importlib.util.find_spec("strands") is None and importlib.util.find_spec("aws_strands") is None:
        raise AdapterImportError("AWS Strands Agents SDK is not installed. Install sentrykit with the 'strands' extra.")


class StrandsGuardHook:
    """Hook to attach to AWS Strands agent pipelines."""

    def __init__(self, policy: Policy, engine: GuardEngine | None = None) -> None:
        _ensure_dependency()
        self.policy = policy
        self.engine = engine or GuardEngine(policy)

    def on_after_invocation(self, invocation: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate an invocation result. Register via agent.register_hook."""

        result = invocation.get("result", {})
        output_text = str(result.get("text", ""))
        run = RunInput(
            goal=str(invocation.get("goal", "")),
            constraints=[str(c) for c in invocation.get("constraints", [])],
            messages=[(msg.get("role", "user"), msg.get("content", "")) for msg in invocation.get("messages", [])],
            contexts=[ContextChunk(source=ctx.get("source", "strands"), text=ctx.get("text", "")) for ctx in invocation.get("contexts", [])],
            tool_calls=[ToolCall(name=call.get("name", ""), args=dict(call.get("args", {}))) for call in invocation.get("tool_calls", [])],
            output=RunOutput(text=output_text),
        )
        verdict = self.engine.evaluate(run)
        if verdict.blocked:
            raise PolicyViolationError(verdict.reason)
        invocation["verdict"] = verdict
        return invocation
