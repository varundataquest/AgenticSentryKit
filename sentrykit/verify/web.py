"""HTTP utilities for deterministic verification fetches."""

from __future__ import annotations

import time
import urllib.error
import urllib.request
from typing import Final

from ..errors import NetworkError
from ..utils.logging import get_logger

_LOGGER = get_logger(__name__)

_DEFAULT_TIMEOUT: Final[float] = 5.0
_DEFAULT_RETRIES: Final[int] = 2
_USER_AGENT: Final[str] = "sentrykit/0.1.0"


def _make_request(url: str) -> urllib.request.Request:
    return urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})


def fetch_text(url: str, *, timeout: float | None = None) -> str:
    """Fetch text content from a URL with retries and structured logging."""

    timeout_value = timeout or _DEFAULT_TIMEOUT
    last_error: Exception | None = None
    for attempt in range(_DEFAULT_RETRIES + 1):
        try:
            request = _make_request(url)
            with urllib.request.urlopen(request, timeout=timeout_value) as response:  # type: ignore[arg-type]
                status = response.getcode() or 200
                if status >= 400:
                    raise NetworkError(f"HTTP {status} for {url}")
                body = response.read().decode("utf-8", errors="replace")
                return body
        except (urllib.error.URLError, urllib.error.HTTPError, NetworkError) as exc:
            last_error = exc
            _LOGGER.warning(
                "web_fetch_failed",
                extra={"_sk_url": url, "_sk_attempt": attempt, "_sk_error": str(exc)},
            )
            if attempt < _DEFAULT_RETRIES:
                time.sleep(0.2 * (attempt + 1))
    raise NetworkError(f"Failed to fetch {url}: {last_error}")
