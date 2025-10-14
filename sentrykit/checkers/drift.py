"""Goal drift detection heuristics."""

from __future__ import annotations

import re
from typing import List, Optional, Set

from ..models import Finding, RunInput

_LOCATION_KEYWORDS: dict[str, Set[str]] = {
    "austin": {"austin", "austin, tx", "austin texas", "atx", "austin metro"},
    "dallas": {"dallas", "dallas, tx", "dfw", "dallas metro"},
    "round rock": {"round rock"},
    "cedar park": {"cedar park"},
    "pflugerville": {"pflugerville"},
    "leander": {"leander"},
    "remote": {"remote", "work from anywhere"},
}

_AUSTIN_METRO = {"round rock", "cedar park", "pflugerville", "leander"}

_SEASON_PATTERN = re.compile(r"(spring|summer|fall|autumn|winter)\s+(20\d{2})", re.I)
_PAY_PATTERN = re.compile(
    r"\$?([0-9]{1,3}(?:,[0-9]{3})*|[0-9]{4,})\s*(?:per\s*month|/month|monthly|a month)",
    re.I,
)
_COMPANY_SIZE_PATTERN = re.compile(r"(\d{2,})\s*(?:\+\s*)?(?:employees|people|staff)\b", re.I)


def _extract_locations(text: str) -> Set[str]:
    lowered = text.lower()
    hits: Set[str] = set()
    for canonical, keywords in _LOCATION_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            hits.add(canonical)
    return hits


def _extract_timeframes(text: str) -> Set[str]:
    return {" ".join(match).lower() for match in _SEASON_PATTERN.findall(text)}


def _extract_pay(text: str) -> Optional[int]:
    match = _PAY_PATTERN.search(text)
    if not match:
        return None
    digits = match.group(1).replace(",", "")
    try:
        return int(digits)
    except ValueError:  # pragma: no cover - defensive
        return None


def _extract_company_size(text: str) -> Optional[int]:
    match = _COMPANY_SIZE_PATTERN.search(text)
    if not match:
        return None
    return int(match.group(1))


def _classify_location(
    desired: Set[str], observed: Set[str], *, treat_metro_minor: bool
) -> tuple[str, Set[str]] | None:
    if not desired or not observed:
        return None

    disallowed: Set[str] = set()
    minor_hits: Set[str] = set()

    for location in observed:
        if location in desired:
            continue
        is_minor = False
        if treat_metro_minor:
            for target in desired:
                if target == "austin" and location in _AUSTIN_METRO:
                    is_minor = True
                    break
        if is_minor:
            minor_hits.add(location)
        else:
            disallowed.add(location)

    if disallowed:
        return "major", disallowed
    if minor_hits:
        return "minor", minor_hits
    return None


def min_pay_threshold(text: str) -> Optional[int]:
    return _extract_pay(text)


def run(
    run: RunInput,
    min_pay: int | None = None,
    *,
    treat_metro_minor: bool = True,
    min_company_size: int | None = None,
) -> List[Finding]:
    """Evaluate goal drift against the provided run."""

    baseline_text = " ".join([run.goal, *run.constraints])
    output_text = run.output.text if run.output else ""

    desired_locations = _extract_locations(baseline_text)
    observed_locations = _extract_locations(output_text)

    findings: List[Finding] = []

    classification = _classify_location(desired_locations, observed_locations, treat_metro_minor=treat_metro_minor)
    if classification:
        label, offending = classification
        severity = "medium" if label == "minor" else "high"
        findings.append(
            Finding(
                kind="goal_drift",
                severity=severity,
                details="Response references disallowed location(s)",
                evidence={
                    "expected": sorted(desired_locations),
                    "observed": sorted(observed_locations),
                    "classification": label,
                    "offending": sorted(offending),
                },
            )
        )

    desired_timeframes = _extract_timeframes(baseline_text)
    observed_timeframes = _extract_timeframes(output_text)
    if desired_timeframes and observed_timeframes and desired_timeframes.isdisjoint(observed_timeframes):
        findings.append(
            Finding(
                kind="goal_drift",
                severity="high",
                details="Response timeframe deviates from requested goal",
                evidence={
                    "expected": sorted(desired_timeframes),
                    "observed": sorted(observed_timeframes),
                    "classification": "major",
                },
            )
        )

    effective_min_pay = min_pay or min_pay_threshold(baseline_text)
    observed_pay = _extract_pay(output_text)
    if effective_min_pay and observed_pay and observed_pay < effective_min_pay:
        findings.append(
            Finding(
                kind="goal_drift",
                severity="high",
                details=f"Pay ${observed_pay} below threshold ${effective_min_pay}",
                evidence={
                    "expected_min": effective_min_pay,
                    "observed": observed_pay,
                    "classification": "major",
                },
            )
        )

    effective_company_size = min_company_size or _extract_company_size(baseline_text)
    observed_company_size = _extract_company_size(output_text)
    if effective_company_size and observed_company_size and observed_company_size < effective_company_size:
        findings.append(
            Finding(
                kind="goal_drift",
                severity="high",
                details="Company size below requested minimum",
                evidence={
                    "expected_min": effective_company_size,
                    "observed": observed_company_size,
                    "classification": "major",
                },
            )
        )

    return findings
