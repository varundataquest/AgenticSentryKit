"""LangChain integration."""

from __future__ import annotations

import importlib
from typing import Any, Dict, List, Optional

from ..engine import GuardEngine
from ..errors import AdapterImportError, PolicyViolationError
from ..models import ContextChunk, RunInput, RunOutput, ToolCall
from ..policy import Policy

try:  # pragma: no cover - import guard
    _LC_CALLBACKS = importlib.import_module("langchain_core.callbacks")
    BaseCallbackHandler = getattr(_LC_CALLBACKS, "BaseCallbackHandler")
    _LANGCHAIN_AVAILABLE = True
except Exception:  # pragma: no cover - compatibility fallback
    try:
        _LC_CALLBACKS = importlib.import_module("langchain.callbacks.base")
        BaseCallbackHandler = getattr(_LC_CALLBACKS, "BaseCallbackHandler")
        _LANGCHAIN_AVAILABLE = True
    except Exception:  # pragma: no cover - missing dependency
        BaseCallbackHandler = object  # type: ignore[assignment]
        _LANGCHAIN_AVAILABLE = False


class SentryKitCallback(BaseCallbackHandler):
    """LangChain callback handler that evaluates final outputs."""

    def __init__(self, policy: Policy, engine: Optional[GuardEngine] = None) -> None:
        if not _LANGCHAIN_AVAILABLE:
            raise AdapterImportError(
                "LangChain is not installed. Install sentrykit with the 'langchain' extra."
            )
        super().__init__()
        self.policy = policy
        self.engine = engine or GuardEngine(policy)
        self._contexts: List[ContextChunk] = []
        self._tool_calls: List[ToolCall] = []
        self._messages: List[tuple[str, str]] = []
        self._goal: str = ""
        self._constraints: List[str] = []

    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any) -> None:  # noqa: D401
        self._goal = str(inputs.get("goal") or inputs.get("question") or inputs.get("input") or "")
        constraint = inputs.get("constraints")
        if isinstance(constraint, list):
            self._constraints = [str(item) for item in constraint]
        elif constraint:
            self._constraints = [str(constraint)]
        prompts = inputs.get("messages") or inputs.get("chat_history")
        if isinstance(prompts, list):
            for message in prompts:
                role = str(message.get("type") or message.get("role") or "user")
                content = str(message.get("content") or message.get("text") or "")
                self._messages.append((role, content))
        super().on_chain_start(serialized, inputs, **kwargs)

    def on_retriever_end(self, documents: List[Any], **kwargs: Any) -> None:  # noqa: D401
        for doc in documents:
            metadata = getattr(doc, "metadata", {})
            source = str(metadata.get("source", "retriever"))
            text = str(getattr(doc, "page_content", ""))
            self._contexts.append(ContextChunk(source=source, text=text))
        super().on_retriever_end(documents, **kwargs)

    def on_tool_end(self, output: Any, *, name: str | None = None, **kwargs: Any) -> None:  # noqa: D401
        args = kwargs.get("inputs") or {}
        if isinstance(args, dict):
            self._tool_calls.append(ToolCall(name=name or "tool", args=dict(args)))
        super().on_tool_end(output, name=name, **kwargs)

    def on_chat_model_start(self, serialized: Dict[str, Any], messages: List[List[Dict[str, Any]]], **kwargs: Any) -> None:  # noqa: D401,E501
        for thread in messages:
            for message in thread:
                role = str(message.get("role", "user"))
                content = str(message.get("content", ""))
                self._messages.append((role, content))
        super().on_chat_model_start(serialized, messages, **kwargs)

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:  # noqa: D401
        text = str(outputs.get("output_text") or outputs.get("result") or outputs.get("text") or "")
        claims = outputs.get("claims") or []
        run = RunInput(
            goal=self._goal,
            constraints=self._constraints,
            messages=self._messages,
            contexts=self._contexts,
            tool_calls=self._tool_calls,
            output=RunOutput(text=text, claims=claims),
        )
        verdict = self.engine.evaluate(run)
        if verdict.blocked:
            raise PolicyViolationError(verdict.reason)
        super().on_chain_end(outputs, **kwargs)
