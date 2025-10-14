from __future__ import annotations

from sentrykit.engine import GuardEngine
from sentrykit.models import ContextChunk, Finding, RunInput, RunOutput, ToolCall
from sentrykit.policy import Policy


class DummyChecker:
    @staticmethod
    def run(_: RunInput) -> list[Finding]:
        return [Finding(kind="goal_drift", severity="high", details="Mismatch")]


def test_engine_scoring_and_block(monkeypatch) -> None:
    policy = Policy(block_on={"goal_drift"})
    engine = GuardEngine(policy)

    run = RunInput(
        goal="Test",
        constraints=[],
        messages=[],
        contexts=[],
        tool_calls=[],
        output=RunOutput(text=""),
    )

    verdict = engine.evaluate(run)
    assert verdict.score == 0
    assert not verdict.blocked

    monkeypatch.setattr("sentrykit.checkers.drift.run", lambda run, **_: [Finding("goal_drift", "high", "Mismatch")])
    verdict = engine.evaluate(run)
    assert verdict.blocked
    assert verdict.score >= 1.0


def test_engine_internal_error(monkeypatch) -> None:
    policy = Policy(block_on={"internal_error"})
    engine = GuardEngine(policy)
    run = RunInput(goal="Test", constraints=[], messages=[], contexts=[], tool_calls=[], output=RunOutput(text=""))

    def boom(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr("sentrykit.checkers.hallucination.run", boom)
    verdict = engine.evaluate(run)
    assert any(f.kind == "internal_error" for f in verdict.findings)
