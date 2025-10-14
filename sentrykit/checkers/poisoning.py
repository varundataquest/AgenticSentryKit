"""Context poisoning detection."""

from __future__ import annotations

from typing import Iterable, List

from ..models import Finding, RunInput
from ..policy import Policy
from ..utils.urls import domain_of

_DEFAULT_OVERRIDE_PHRASES = [
    "ignore previous instructions",
    "disregard policy",
    "override safety",
    "you are now evil",
    "reset your instructions",
]


def run(run: RunInput, policy: Policy | None = None, *, override_phrases: Iterable[str] | None = None) -> List[Finding]:
    phrases = {phrase.lower() for phrase in (override_phrases or _DEFAULT_OVERRIDE_PHRASES)}
    findings: List[Finding] = []

    for chunk in run.contexts:
        lowered = chunk.text.lower()
        for phrase in phrases:
            if phrase in lowered:
                findings.append(
                    Finding(
                        kind="context_poisoning",
                        severity="high",
                        details=f"Context chunk {chunk.source} contains override phrase",
                        evidence={"phrase": phrase, "source": chunk.source},
                    )
                )
                break

    if policy:
        allowed_domains = {domain.lower() for domain in policy.allowed_url_domains}
        for call in run.tool_calls:
            domain = domain_of(str(call.args.get("url", ""))) if isinstance(call.args, dict) else ""
            if domain and allowed_domains and domain not in allowed_domains:
                findings.append(
                    Finding(
                        kind="context_poisoning",
                        severity="medium",
                        details=f"Tool call {call.name} references off-policy domain {domain}",
                        evidence={"tool": call.name, "domain": domain},
                    )
                )
    return findings
