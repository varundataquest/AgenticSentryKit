from __future__ import annotations

from sentrykit.checkers.drift import run
from sentrykit.models import RunInput, RunOutput


BASE_GOAL = "Find Austin internship paying $5,000 per month for Summer 2026"
BASE_CONSTRAINTS = ["Company must have 50 employees"]


def make_run(output_text: str) -> RunInput:
    return RunInput(
        goal=BASE_GOAL,
        constraints=list(BASE_CONSTRAINTS),
        messages=[],
        contexts=[],
        tool_calls=[],
        output=RunOutput(text=output_text),
    )


def test_drift_none() -> None:
    findings = run(make_run("Great Austin internship paying $5,500 per month in Summer 2026"), min_pay=5000)
    assert not findings


def test_drift_major_location() -> None:
    findings = run(make_run("Found Dallas role paying $5,500"), min_pay=5000)
    assert findings
    assert findings[0].severity == "high"


def test_drift_pay() -> None:
    findings = run(make_run("Austin internship paying $4,000 per month"), min_pay=5000)
    assert findings
    assert "below threshold" in findings[0].details
