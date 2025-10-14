"""Claim extraction helpers for demos."""

from __future__ import annotations

from typing import List

from ..models import Claim, Extraction, RunOutput


def generate_claims(output: RunOutput, evidence_url: str | None = None) -> List[Claim]:
    """Generate naive claims from free-form text."""

    sentences = [sentence.strip() for sentence in output.text.split(".") if sentence.strip()]
    claims: List[Claim] = []
    for sentence in sentences[:3]:
        claims.append(
            Claim(
                statement=sentence,
                evidence_urls=[evidence_url] if evidence_url else [],
                extraction=Extraction(kind="contains", pattern=sentence[:40], must_include=sentence[:20]),
            )
        )
    return claims
