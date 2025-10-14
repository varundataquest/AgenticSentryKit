"""URL helpers."""

from __future__ import annotations

from urllib.parse import urlparse


def domain_of(url: str) -> str:
    """Return the normalized domain of a URL."""

    parsed = urlparse(url)
    if parsed.scheme == "file":
        return "file"
    netloc = parsed.netloc or parsed.path
    if not netloc:
        return ""
    netloc = netloc.lower()
    if "@" in netloc:
        netloc = netloc.split("@", 1)[1]
    if ":" in netloc:
        netloc = netloc.split(":", 1)[0]
    return netloc.encode("idna").decode("ascii")
