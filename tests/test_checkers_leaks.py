from __future__ import annotations

from sentrykit.checkers.leaks import run
from sentrykit.models import Claim, Extraction, RunInput, RunOutput


def test_leak_detection() -> None:
    output = RunOutput(
        text="Here is a secret sk-ABCDEF1234567890 and email test@example.com",
        claims=[Claim(statement="sk-ABCDEF1234567890", evidence_urls=[], extraction=Extraction(kind="contains", pattern="", must_include=None))],
    )
    run_input = RunInput(
        goal="",
        constraints=[],
        messages=[],
        contexts=[],
        tool_calls=[],
        output=output,
    )
    findings = run(run_input)
    assert findings
    assert any(f.severity == "high" for f in findings)
    assert any("samples" in f.evidence for f in findings)
