"""Typed dataclass models used across SentryKit."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Tuple


@dataclass(slots=True)
class Extraction:
    kind: Literal["css", "xpath", "regex", "contains"]
    pattern: str
    must_include: str | None = None


@dataclass(slots=True)
class Claim:
    statement: str
    evidence_urls: List[str]
    extraction: Extraction


@dataclass(slots=True)
class ContextChunk:
    source: str
    text: str


@dataclass(slots=True)
class ToolCall:
    name: str
    args: Dict[str, Any]


@dataclass(slots=True)
class RunOutput:
    text: str
    claims: List[Claim] = field(default_factory=list)


@dataclass(slots=True)
class RunInput:
    goal: str
    constraints: List[str]
    messages: List[Tuple[str, str]]
    contexts: List[ContextChunk]
    tool_calls: List[ToolCall]
    output: RunOutput | None = None


@dataclass(slots=True)
class Finding:
    kind: str
    severity: Literal["low", "medium", "high"]
    details: str
    evidence: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Report:
    html: str
    data: Dict[str, Any] = field(default_factory=dict)

    def to_html(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(self.html)


@dataclass(slots=True)
class Verdict:
    blocked: bool
    reason: str
    score: float
    findings: List[Finding]
    report: Optional[Report] = None
