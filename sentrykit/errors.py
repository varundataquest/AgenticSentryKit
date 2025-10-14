"""Custom exceptions for SentryKit."""

from __future__ import annotations


class SentryKitError(Exception):
    """Base exception for all SentryKit errors."""


class PolicyViolationError(SentryKitError):
    """Raised when a guard policy is violated."""


class NetworkError(SentryKitError):
    """Raised when an outbound network call fails."""


class ParseError(SentryKitError):
    """Raised when parsing of a payload or document fails."""


class AdapterImportError(SentryKitError):
    """Raised when an adapter dependency is missing."""
