"""Redaction utilities for secrets."""

from __future__ import annotations

import re

_SECRET_PATTERNS = [
    re.compile(r"(sk-[a-z0-9]{16,})", re.IGNORECASE),
    re.compile(r"(AKIA[0-9A-Z]{16})"),
    re.compile(r"(ASIA[0-9A-Z]{16})"),
    re.compile(r"(ssh-rsa [A-Za-z0-9+/=]+)"),
    re.compile(r"(-----BEGIN [A-Z ]+PRIVATE KEY-----[\s\S]+?-----END [A-Z ]+PRIVATE KEY-----)", re.MULTILINE),
]


def _mask(value: str) -> str:
    if len(value) <= 8:
        return "*" * len(value)
    return f"{'*' * (len(value) - 4)}{value[-4:]}"


def redact_secrets(text: str) -> str:
    """Mask known secrets inside text."""

    redacted = text
    for pattern in _SECRET_PATTERNS:
        matches = list(pattern.finditer(redacted))
        for match in matches:
            full = match.group(1)
            redacted_val = _mask(full)
            redacted = redacted.replace(full, redacted_val)
    return redacted
