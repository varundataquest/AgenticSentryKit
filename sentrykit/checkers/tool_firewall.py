"""Tool firewall checker."""

from __future__ import annotations

from typing import List

from ..models import Finding, RunInput
from ..policy import Policy


def run(run: RunInput, policy: Policy) -> List[Finding]:
    findings: List[Finding] = []
    allowed = policy.allowed_tool_names
    if not allowed:
        return findings
    for call in run.tool_calls:
        if call.name not in allowed:
            findings.append(
                Finding(
                    kind="tool_firewall",
                    severity="high",
                    details=f"Tool {call.name} not in allow-list",
                    evidence={"tool": call.name},
                )
            )
    return findings
