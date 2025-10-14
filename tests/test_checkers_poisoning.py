from __future__ import annotations

from pathlib import Path

from sentrykit.checkers.poisoning import run
from sentrykit.models import ContextChunk, RunInput, RunOutput, ToolCall
from sentrykit.policy import Policy

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "contexts"


def make_run(context_text: str, domain: str) -> RunInput:
    return RunInput(
        goal="",
        constraints=[],
        messages=[],
        contexts=[ContextChunk(source="ctx", text=context_text)],
        tool_calls=[ToolCall(name="fetch", args={"url": f"https://{domain}/"})],
        output=RunOutput(text=""),
    )


def test_poisoning_phrase_detection() -> None:
    text = FIXTURES / "poisoned.txt"
    run_input = make_run(text.read_text(encoding="utf-8"), "example.com")
    findings = run(run_input, Policy())
    assert findings
    assert findings[0].kind == "context_poisoning"


def test_poisoning_off_policy_domain() -> None:
    run_input = make_run("clean", "bad.com")
    policy = Policy(allowed_url_domains={"good.com"})
    findings = run(run_input, policy)
    assert findings
    assert findings[0].severity == "medium"
