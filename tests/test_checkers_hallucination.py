from __future__ import annotations

from pathlib import Path

from sentrykit.checkers.hallucination import run
from sentrykit.models import Claim, Extraction, RunInput, RunOutput

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "pages"


def _make_run(claim: Claim) -> RunInput:
    return RunInput(
        goal="",
        constraints=[],
        messages=[],
        contexts=[],
        tool_calls=[],
        output=RunOutput(text="", claims=[claim]),
    )


def test_hallucination_pass() -> None:
    html = (FIXTURES / "austin.html").read_text(encoding="utf-8")
    claim = Claim(
        statement="Pay is $5,500 per month",
        evidence_urls=["file://local"],
        extraction=Extraction(kind="contains", pattern="Pay", must_include="$5,500"),
    )
    findings = run(_make_run(claim), fetcher=lambda url: html)
    assert not findings


def test_hallucination_fail() -> None:
    html = (FIXTURES / "austin.html").read_text(encoding="utf-8")
    claim = Claim(
        statement="Pay is $9,999 per month",
        evidence_urls=["file://local"],
        extraction=Extraction(kind="contains", pattern="Pay", must_include="$9,999"),
    )
    findings = run(_make_run(claim), fetcher=lambda url: html)
    assert findings
    assert findings[0].severity == "high"
