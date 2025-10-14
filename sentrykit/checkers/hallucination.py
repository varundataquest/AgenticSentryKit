"""Claim verification checker for hallucination detection."""

from __future__ import annotations

from typing import Callable, List

from ..errors import ParseError
from ..models import Claim, Finding, RunInput
from ..utils.logging import get_logger
from ..utils.redact import redact_secrets
from ..verify import extract
from ..verify.web import fetch_text

_LOGGER = get_logger(__name__)

Fetcher = Callable[[str], str]


def _validate_contains(document: str, pattern: str, must_include: str | None) -> bool:
    probe = must_include or pattern
    return probe.lower() in document.lower()


def _apply_extraction(claim: Claim, document: str) -> bool:
    extraction = claim.extraction
    if extraction.kind == "css":
        text = extract.extract_css(document, extraction.pattern, extraction.must_include)
        target = extraction.must_include or extraction.pattern
        return target.lower() in text.lower()
    if extraction.kind == "xpath":
        text = extract.extract_xpath(document, extraction.pattern, extraction.must_include)
        target = extraction.must_include or extraction.pattern
        return target.lower() in text.lower()
    if extraction.kind == "regex":
        text = extract.extract_regex(document, extraction.pattern)
        if extraction.must_include and extraction.must_include.lower() not in text.lower():
            raise ParseError("Regex extraction missing required snippet")
        return True
    if extraction.kind == "contains":
        return _validate_contains(document, extraction.pattern, extraction.must_include)
    raise ParseError(f"Unsupported extraction kind: {extraction.kind}")


def _verify_claim(claim: Claim, fetcher: Fetcher) -> tuple[bool, list[str]]:
    errors: list[str] = []
    urls = claim.evidence_urls or []
    if not urls:
        return False, ["no_evidence_urls"]
    for url in urls:
        try:
            document = fetcher(url)
        except Exception as exc:  # pragma: no cover - defensive logging
            message = f"fetch_error:{exc}"
            errors.append(message)
            _LOGGER.debug("claim_fetch_error", extra={"_sk_url": url, "_sk_error": str(exc)})
            continue
        try:
            if _apply_extraction(claim, document):
                return True, []
        except ParseError as exc:
            message = f"parse_error:{exc}"
            errors.append(message)
            _LOGGER.debug(
                "claim_extraction_error",
                extra={"_sk_url": url, "_sk_error": str(exc), "_sk_pattern": claim.extraction.pattern},
            )
        except Exception as exc:  # pragma: no cover - defensive
            message = f"unexpected_error:{exc}"
            errors.append(message)
            _LOGGER.exception(
                "claim_unexpected_error",
                extra={"_sk_url": url, "_sk_error": str(exc), "_sk_pattern": claim.extraction.pattern},
            )
    return False, errors


def run(run: RunInput, fetcher: Fetcher | None = None) -> List[Finding]:
    """Verify output claims using deterministic extractors."""

    findings: List[Finding] = []
    output = run.output
    if not output or not output.claims:
        return findings

    fetch = fetcher or fetch_text
    for claim in output.claims:
        valid, errors = _verify_claim(claim, fetch)
        if not valid:
            findings.append(
                Finding(
                    kind="hallucination",
                    severity="high",
                    details=f"Claim lacks verifiable evidence: {redact_secrets(claim.statement)}",
                    evidence={
                        "statement": redact_secrets(claim.statement),
                        "urls": claim.evidence_urls,
                        "errors": [redact_secrets(error) for error in errors[:3]],
                    },
                )
            )
    return findings
