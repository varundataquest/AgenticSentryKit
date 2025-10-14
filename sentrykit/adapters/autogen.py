"""Microsoft AutoGen integration."""

from __future__ import annotations

import importlib
from typing import Any, Callable, Dict

from ..engine import GuardEngine
from ..errors import AdapterImportError, PolicyViolationError
from ..models import ContextChunk, RunInput, RunOutput, ToolCall
from ..policy import Policy


def _ensure_dependency() -> None:
    if importlib.util.find_spec("autogen") is None:
        raise AdapterImportError("AutoGen is not installed. Install sentrykit with the 'autogen' extra.")


def register_reply(agent: Any, policy: Policy, engine: GuardEngine | None = None) -> None:
    """Register a reply interceptor for an AutoGen agent."""

    _ensure_dependency()
    engine = engine or GuardEngine(policy)

    original_reply: Callable[..., Any] = getattr(agent, "reply", None)
    if original_reply is None:
        raise AdapterImportError("Agent does not expose a reply method for interception.")

    def _wrapped_reply(*args: Any, **kwargs: Any) -> Any:
        result = original_reply(*args, **kwargs)
        message = result.get("content", "") if isinstance(result, dict) else str(result)
        run = RunInput(
            goal=str(getattr(agent, "goal", "")),
            constraints=[],
            messages=[("assistant", message)],
            contexts=[ContextChunk(source="autogen", text=str(getattr(agent, "context", "")))],
            tool_calls=[ToolCall(name=call.get("name", ""), args=dict(call.get("args", {}))) for call in getattr(agent, "tool_calls", [])],
            output=RunOutput(text=message),
        )
        verdict = engine.evaluate(run)
        if verdict.blocked:
            raise PolicyViolationError(verdict.reason)
        return result

    setattr(agent, "reply", _wrapped_reply)
