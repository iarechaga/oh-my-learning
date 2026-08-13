# Security, Cost, and Production Operations

The threat model that makes prompt injection structurally hard to eliminate,
least-privilege tool permissions and scoped credentials, human-in-the-loop gates for
irreversible actions, token economics (routing, caching, budgets), observability for
non-deterministic runs, failure modes and verification, and what it takes to operate a
fleet of agents with organizational accountability.

**Sources:** primary security-research publications on prompt injection and agent
threat models, primary vendor documentation on permissions and observability, and
dated practitioner write-ups on cost/FinOps practice. No single canonical book exists
for this field. See each lesson's `source:` front matter for its specific citations,
and
[agent-docs/fast-moving-domain-policy.md](../../agent-docs/fast-moving-domain-policy.md).

**How to use this subject:** read a lesson on your own, then ask to *discuss
`agent-security-and-operations/<NN>`* (e.g. *"discuss `agent-security-and-operations/02`"*).
Concepts are ordered by dependency, so top-to-bottom is a sensible reading order.

**Seniority baseline:** senior (lessons range mid->principal).

**Durability:** durable - every concept below is expected to age slowly; concrete cost
figures and pricing tiers used as examples are dated inline and the current numbers
live in `landscape-snapshot/05`. See
[agent-docs/fast-moving-domain-policy.md](../../agent-docs/fast-moving-domain-policy.md).

## Concepts

| ID  | Concept | Seniority | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | --------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | The threat model: why agents can't reliably separate instructions from data | mid | drafted | — | — | [lesson](lessons/01-the-threat-model.md) | — |
| 02  | Prompt injection: direct, indirect, and defense-in-depth | senior | drafted | — | — | [lesson](lessons/02-prompt-injection.md) | — |
| 03  | Least-privilege tool permissions and scoped credentials | senior | drafted | — | — | [lesson](lessons/03-least-privilege-tool-permissions.md) | — |
| 04  | Human-in-the-loop gates for irreversible actions | senior | drafted | — | — | [lesson](lessons/04-human-in-the-loop-gates.md) | — |
| 05  | Token economics: model routing, caching, and budget design | senior | drafted | — | — | [lesson](lessons/05-token-economics.md) | — |
| 06  | Observability for agents: tracing, logging, and debugging non-determinism | staff | drafted | — | — | [lesson](lessons/06-observability-for-agents.md) | — |
| 07  | Failure modes and verification: hallucination, silent drift, and trust calibration | staff | drafted | — | — | [lesson](lessons/07-failure-modes-and-verification.md) | — |
| 08  | Operating agent fleets: governance, incident response, and organizational risk | principal | drafted | — | — | [lesson](lessons/08-operating-agent-fleets.md) | — |

**Status:** `drafted` (lesson written) · `discussed` (at least one discussion held).
**Mastery:** `solid` · `partial` · `shaky` · `not-yet` - set from the most recent
discussion's verdict; empty until first discussed.
**Cross-subject prerequisites**: `01` builds on `tool-use-agentic-loop/03`; `03` builds
on `model-context-protocol/05`; `05` builds on `tool-use-agentic-loop/06`; `06` builds
on `multi-agent-orchestration/04` and cross-links to `devops-reliability/sre`; `07`
builds on `agent-evaluation/04`; `08` cross-links to `technical-leadership/staff-engineer`.
All named per lesson in front matter and prose.
