"""Test stub of LangChain callbacks."""

from __future__ import annotations

from typing import Any, Dict, List


class BaseCallbackHandler:
    """Minimal callback handler interface used for tests."""

    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any) -> None:
        return None

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        return None

    def on_retriever_end(self, documents: List[Any], **kwargs: Any) -> None:
        return None

    def on_tool_end(self, output: Any, *, name: str | None = None, **kwargs: Any) -> None:
        return None

    def on_chat_model_start(self, serialized: Dict[str, Any], messages: List[List[Dict[str, Any]]], **kwargs: Any) -> None:
        return None
