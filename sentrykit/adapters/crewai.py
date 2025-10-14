"""CrewAI integration."""

from __future__ import annotations

import importlib
from typing import Any, Callable, Dict

from ..engine import GuardEngine
from ..errors import AdapterImportError, PolicyViolationError
from ..models import ContextChunk, RunInput, RunOutput, ToolCall
from ..policy import Policy


def _ensure_dependency() -> None:
    if importlib.util.find_spec("crewai") is None:
        raise AdapterImportError("CrewAI is not installed. Install sentrykit with the 'crewai' extra.")


def run_with_guard(crew: Any, policy: Policy, engine: GuardEngine | None = None, **kwargs: Any) -> Any:
    """Execute a CrewAI crew with guard evaluation."""

    _ensure_dependency()
    engine = engine or GuardEngine(policy)

    result = crew.run(**kwargs)
    history = getattr(crew, "history", [])
    messages = [(msg.get("role", "user"), msg.get("content", "")) for msg in history]
    tool_calls = [ToolCall(name=call.get("name", ""), args=dict(call.get("args", {}))) for call in getattr(crew, "tool_calls", [])]
    contexts = [ContextChunk(source=ctx.get("source", "crew"), text=ctx.get("text", "")) for ctx in getattr(crew, "contexts", [])]

    output_text = result.get("output", "") if isinstance(result, dict) else str(result)
    run = RunInput(
        goal=str(getattr(crew, "goal", "")),
        constraints=[str(c) for c in getattr(crew, "constraints", [])],
        messages=messages,
        contexts=contexts,
        tool_calls=tool_calls,
        output=RunOutput(text=output_text),
    )
    verdict = engine.evaluate(run)
    if verdict.blocked:
        raise PolicyViolationError(verdict.reason)
    return result
