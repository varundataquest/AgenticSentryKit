# Checkers

SentryKit ships with a focused set of heuristics tuned for agent-style workloads. Each checker operates on the shared `RunInput` model and emits `Finding` objects that feed into risk scoring and policy enforcement.

- **Hallucination.** Verifies each claim against its cited evidence by fetching the referenced HTML or text and applying deterministic extractors. Missing snippets produce high-severity findings with redacted context for easy debugging.
- **Goal drift.** Parses the goal, constraints, and output for locations, dates, pay, and company size cues. It distinguishes between Austin and nearby metro cities, highlights timeframe mismatches, and reports when minimum pay thresholds are missed.
- **Context poisoning.** Looks for override phrases (“ignore previous instructions”, “disregard policy”, and similar) inside retrieved documents and flags tool calls that target off-policy domains.
- **Jailbreak.** Detects jailbreak prompts such as “do anything now” or “devmode++” before the agent adopts a less-restricted persona.
- **Tool firewall.** Ensures every tool invocation appears on the policy allow-list, catching unexpected names or orchestrator bugs.
- **Data leak.** Runs secret and PII scans on agent output using entropy checks and targeted regexes. Any captured evidence is redacted through the shared utilities so reports stay safe to distribute.

You can extend the guard engine by adding new checker modules that follow the same function signature and return type.
