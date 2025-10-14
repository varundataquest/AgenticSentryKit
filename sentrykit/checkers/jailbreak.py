"""Jailbreak detection."""

from __future__ import annotations

from typing import List

from ..models import Finding, RunInput

_JAILBREAK_PHRASES = [
    "do anything now",
    "devmode++",
    "unlock hidden mode",
    "no rules apply",
]


def run(run: RunInput) -> List[Finding]:
    findings: List[Finding] = []
    texts = [run.goal, *(constraint for constraint in run.constraints), *(msg[1] for msg in run.messages)]
    if run.output:
        texts.append(run.output.text)
    blob = "\n".join(texts).lower()
    for phrase in _JAILBREAK_PHRASES:
        if phrase in blob:
            findings.append(
                Finding(
                    kind="jailbreak",
                    severity="high",
                    details=f"Detected jailbreak directive: {phrase}",
                    evidence={"phrase": phrase},
                )
            )
    return findings
