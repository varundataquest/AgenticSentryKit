"""HTML reporting helpers leveraging a lightweight template."""

from __future__ import annotations

from html import escape
from importlib import resources
from typing import Any, Dict, List

from ..models import Finding, Report, Verdict
from ..utils.redact import redact_secrets

_TEMPLATE_PATH = resources.files(__package__) / "templates" / "report.html.j2"


def _load_template() -> str:
    return _TEMPLATE_PATH.read_text(encoding="utf-8")


def _sanitize_value(value: Any) -> Any:
    if isinstance(value, str):
        return redact_secrets(value)
    if isinstance(value, list):
        return [_sanitize_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _sanitize_value(item) for key, item in value.items()}
    return value


def _stringify(value: Any) -> str:
    if isinstance(value, dict):
        return ", ".join(f"{key}: {_stringify(val)}" for key, val in value.items())
    if isinstance(value, (list, tuple, set)):
        return ", ".join(_stringify(item) for item in value)
    return str(value)


def _serialize_findings(findings: List[Finding]) -> List[Dict[str, Any]]:
    serialized: List[Dict[str, Any]] = []
    for finding in findings:
        sanitized_evidence = _sanitize_value(finding.evidence)
        serialized.append(
            {
                "kind": finding.kind,
                "severity": finding.severity,
                "details": redact_secrets(finding.details),
                "evidence": sanitized_evidence,
            }
        )
    return serialized


def _serialize_verdict(verdict: Verdict) -> Dict[str, Any]:
    return {
        "blocked": verdict.blocked,
        "score": verdict.score,
        "reason": redact_secrets(verdict.reason),
        "findings": _serialize_findings(verdict.findings),
    }


def _build_findings_section(data: Dict[str, Any]) -> str:
    findings: List[Dict[str, Any]] = data["findings"]
    if not findings:
        return "<p>No findings.</p>"
    rows: List[str] = []
    for finding in findings:
        evidence_items = "".join(
            f"<li><strong>{escape(str(key))}:</strong> {escape(_stringify(value))}</li>"
            for key, value in finding["evidence"].items()
        )
        rows.append(
            "<tr>"
            f"<td>{escape(finding['kind'])}</td>"
            f"<td class='severity-{escape(finding['severity'])}'>{escape(finding['severity'].title())}</td>"
            f"<td>{escape(finding['details'])}</td>"
            f"<td><ul>{evidence_items}</ul></td>"
            "</tr>"
        )
    table = (
        "<table>"
        "<thead><tr><th>Kind</th><th>Severity</th><th>Details</th><th>Evidence</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table>"
    )
    return table


def render(verdict: Verdict) -> Report:
    """Render a structured HTML report for a verdict."""

    data = _serialize_verdict(verdict)
    template = _load_template()
    status_class = "blocked" if data["blocked"] else "allowed"
    status_text = "Blocked" if data["blocked"] else "Allowed"
    findings_section = _build_findings_section(data)
    html = (
        template
        .replace("{{STATUS_CLASS}}", escape(status_class))
        .replace("{{STATUS_TEXT}}", escape(status_text))
        .replace("{{SCORE}}", f"{data['score']:.2f}")
        .replace("{{REASON}}", escape(data["reason"]))
        .replace("{{FINDINGS_SECTION}}", findings_section)
    )
    return Report(html=html, data=data)
