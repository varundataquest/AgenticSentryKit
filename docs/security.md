# Security & Privacy

SentryKit is designed for environments where runs may contain sensitive information. The default configuration emphasizes transparency while avoiding accidental disclosure:

- Secrets detected in findings are masked through `redact_secrets` before they reach logs or reports.
- Policies restrict outbound tool calls and evidence domains, giving you a straightforward allow-list to audit.
- Unit tests and examples stay offline. Use `httpx_mock`, `respx`, or the included fixtures when writing new coverage.

In production, forward guardrail logs to your central observability stack, enable per-run retention policies, and consider layering additional classifiers or rate limits for workloads with strict compliance requirements.
