from __future__ import annotations

import types
from typing import Any, Dict

import pytest

from sentrykit import GuardEngine, Policy
from sentrykit.adapters import autogen as autogen_adapter
from sentrykit.adapters import crewai as crewai_adapter
from sentrykit.adapters import strands as strands_adapter
from sentrykit.errors import PolicyViolationError


@pytest.fixture(autouse=True)
def stub_imports(monkeypatch: pytest.MonkeyPatch) -> None:
    original_find_spec = autogen_adapter.importlib.util.find_spec

    def fake_find_spec(name: str, *args: Any, **kwargs: Any):
        if name in {"autogen", "crewai", "strands", "aws_strands"}:
            return types.SimpleNamespace(name=name)
        return original_find_spec(name, *args, **kwargs)

    monkeypatch.setattr(autogen_adapter.importlib.util, "find_spec", fake_find_spec)
    monkeypatch.setattr(crewai_adapter.importlib.util, "find_spec", fake_find_spec)
    monkeypatch.setattr(strands_adapter.importlib.util, "find_spec", fake_find_spec)


def _policy() -> Policy:
    return Policy(block_on={"goal_drift"})


def test_autogen_adapter_blocks_goal_drift(monkeypatch: pytest.MonkeyPatch) -> None:
    policy = _policy()
    engine = GuardEngine(policy)

    class DummyAgent:
        goal = "Find Austin internship roles"
        context = ""
        tool_calls: list[Dict[str, Any]] = []

        def reply(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
            return {"content": "Here is a Dallas internship"}

    agent = DummyAgent()
    autogen_adapter.register_reply(agent, policy, engine=engine)

    with pytest.raises(PolicyViolationError):
        agent.reply()


def test_crewai_adapter_blocks_goal_drift(monkeypatch: pytest.MonkeyPatch) -> None:
    policy = _policy()
    engine = GuardEngine(policy)

    class DummyCrew:
        goal = "Locate Austin internships"
        constraints = ["Austin only"]
        history = []
        tool_calls: list[Dict[str, Any]] = []
        contexts: list[Dict[str, str]] = []

        def run(self, **_: Any) -> Dict[str, Any]:
            return {"output": "We found a Dallas internship"}

    crew = DummyCrew()

    with pytest.raises(PolicyViolationError):
        crewai_adapter.run_with_guard(crew, policy, engine=engine)


def test_strands_adapter_blocks_goal_drift() -> None:
    policy = _policy()
    engine = GuardEngine(policy)
    hook = strands_adapter.StrandsGuardHook(policy, engine=engine)

    invocation = {
        "goal": "Gather Austin internship listings",
        "constraints": ["Austin only"],
        "messages": [],
        "contexts": [],
        "tool_calls": [],
        "result": {"text": "Dallas role"},
    }

    with pytest.raises(PolicyViolationError):
        hook.on_after_invocation(invocation)
