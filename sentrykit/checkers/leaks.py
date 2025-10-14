"""Secret and PII leakage detection."""

from __future__ import annotations

import math
import re
from typing import Iterable, List

from ..models import Finding, RunInput
from ..utils.redact import redact_secrets

_SECRET_REGEXES = [
    re.compile(r"sk-[a-z0-9]{16,}", re.I),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"ASIA[0-9A-Z]{16}"),
    re.compile(r"ssh-rsa [A-Za-z0-9+/=]{40,}"),
    re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----[\s\S]+?-----END [A-Z ]+PRIVATE KEY-----"),
]

_PII_REGEXES = [
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    re.compile(r"\b\+?1?[-.\s]?(?:\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}\b"),
]


def _shannon_entropy(value: str) -> float:
    frequencies = {ch: value.count(ch) for ch in set(value)}
    length = len(value)
    return -sum((freq / length) * math.log2(freq / length) for freq in frequencies.values())


def _scan(text: str, patterns: Iterable[re.Pattern[str]]) -> List[str]:
    matches: List[str] = []
    for pattern in patterns:
        matches.extend(pattern.findall(text))
    return matches


def run(run: RunInput) -> List[Finding]:
    findings: List[Finding] = []
    texts = []
    if run.output:
        texts.append(run.output.text)
        for claim in run.output.claims:
            texts.append(claim.statement)
    for chunk in run.contexts:
        texts.append(chunk.text)

    blob = "\n".join(texts)
    for match in _scan(blob, _SECRET_REGEXES):
        if _shannon_entropy(match) < 3.5:
            continue
        findings.append(
            Finding(
                kind="data_leak",
                severity="high",
                details="Detected potential secret in output",
                evidence={"value": redact_secrets(match)},
            )
        )

    pii_hits = _scan(blob, _PII_REGEXES)
    if pii_hits:
        findings.append(
            Finding(
                kind="data_leak",
                severity="medium",
                details="Detected potential PII",
                evidence={"samples": [redact_secrets(hit) for hit in pii_hits[:5]]},
            )
        )

    return findings
