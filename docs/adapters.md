# Adapters

Adapters translate framework-specific callbacks into the shared `RunInput` schema and hand the data to `GuardEngine`. The goal is to keep the policy logic identical whether you are experimenting with LangChain or shipping on the OpenAI Agents SDK.

| Framework | Entry point | Notes |
| --- | --- | --- |
| OpenAI Agents SDK | `sentrykit.adapters.openai_agents.sentrykit_guardrail` | Wraps agent replies and returns tripwire metadata you can forward to the platform’s guardrail interface. |
| LangChain | `SentryKitCallback` | Drop-in callback handler that accumulates retriever documents, tool calls, and the final output. Blocks by raising `PolicyViolationError`. |
| Microsoft AutoGen | `register_reply` | Intercepts replies before they are sent to the next participant and replaces the message when a block occurs. |
| AWS Strands Agents | `StrandsGuardHook` | Attach to the `on_after_invocation` hook to evaluate each step’s output within a Strands workflow. |
| CrewAI | `run_with_guard` | Executes a crew, collects the final plan and tool invocations, and enforces the verdict before returning results to the caller. |

Every adapter module contains inline usage notes and links back to the relevant example in `examples/` so you can see the wiring in practice.
