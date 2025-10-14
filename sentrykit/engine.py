"""Core guard engine orchestrating all checkers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Sequence

from . import checkers
from .models import Finding, RunInput, Verdict
from .policy import Policy
from .report import html as html_report
from .utils.logging import get_logger

_LOGGER = get_logger(__name__)

_SEVERITY_SCORES = {"low": 0.2, "medium": 0.5, "high": 1.0}

Checker = Callable[..., List[Finding]]


@dataclass(slots=True)
class GuardEngine:
    policy: Policy

    def _run_checker(self, func: Checker, *args, **kwargs) -> List[Finding]:
        try:
            return func(*args, **kwargs)
        except Exception as exc:  # pragma: no cover - defensive path
            _LOGGER.exception("checker_failure", extra={"_sk_checker": func.__module__})
            return [
                Finding(
                    kind="internal_error",
                    severity="low",
                    details=f"Checker {func.__module__} failed: {exc}",
                    evidence={"checker": func.__module__},
                )
            ]

    def evaluate(self, run: RunInput) -> Verdict:
        findings: List[Finding] = []

        findings.extend(self._run_checker(checkers.tool_firewall.run, run, self.policy))
        findings.extend(self._run_checker(checkers.poisoning.run, run, self.policy))
        findings.extend(self._run_checker(checkers.jailbreak.run, run))
        findings.extend(self._run_checker(checkers.leaks.run, run))
        findings.extend(
            self._run_checker(
                checkers.drift.run,
                run,
                min_pay=self.policy.min_pay_threshold,
                treat_metro_minor=self.policy.treat_metro_as_minor,
                min_company_size=self.policy.min_company_size,
            )
        )
        findings.extend(self._run_checker(checkers.hallucination.run, run))

        score = sum(_SEVERITY_SCORES.get(finding.severity, 0.0) for finding in findings)

        blocked = self._should_block(findings)
        reason = "; ".join(sorted({finding.kind for finding in findings})) if findings else "No findings"

        verdict = Verdict(blocked=blocked, reason=reason, score=score, findings=findings)
        verdict.report = html_report.render(verdict)
        return verdict

    def _should_block(self, findings: Sequence[Finding]) -> bool:
        if not self.policy.block_on:
            return False
        for finding in findings:
            keys = {
                finding.kind,
                f"{finding.kind}:any",
                f"{finding.kind}:{finding.severity}",
            }
            classification = finding.evidence.get("classification")
            if isinstance(classification, str):
                keys.add(f"{finding.kind}:{classification}")
            if finding.severity == "high":
                keys.add(f"{finding.kind}:high")
            if keys & self.policy.block_on:
                return True
        return False
