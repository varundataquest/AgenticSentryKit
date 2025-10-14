"""Policy definitions for SentryKit guardrails."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class Policy:
    """Represents guardrail policy configuration."""

    allowed_tool_names: set[str] = field(default_factory=set)
    allowed_url_domains: set[str] = field(default_factory=set)
    require_claims: bool = True
    block_on: set[str] = field(default_factory=set)
    min_company_size: int | None = None
    min_pay_threshold: int | None = None
    treat_metro_as_minor: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the policy to a JSON-friendly dict."""

        return {
            "allowed_tool_names": sorted(self.allowed_tool_names),
            "allowed_url_domains": sorted(self.allowed_url_domains),
            "require_claims": self.require_claims,
            "block_on": sorted(self.block_on),
            "min_company_size": self.min_company_size,
            "min_pay_threshold": self.min_pay_threshold,
            "treat_metro_as_minor": self.treat_metro_as_minor,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Policy":
        """Create a policy from a dictionary."""

        return cls(
            allowed_tool_names=set(data.get("allowed_tool_names", [])),
            allowed_url_domains=set(data.get("allowed_url_domains", [])),
            require_claims=bool(data.get("require_claims", True)),
            block_on=set(data.get("block_on", [])),
            min_company_size=data.get("min_company_size"),
            min_pay_threshold=data.get("min_pay_threshold"),
            treat_metro_as_minor=bool(data.get("treat_metro_as_minor", True)),
        )

    def copy(self) -> "Policy":
        """Return a shallow copy of the policy."""

        return Policy.from_dict(self.to_dict())
