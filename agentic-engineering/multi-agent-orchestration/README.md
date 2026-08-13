# Multi-Agent Systems & Orchestration

When splitting work across more than one agent actually helps, subagent delegation
with context isolation, the orchestration patterns that structure how agents
coordinate (deterministic workflows vs autonomous delegation), the frameworks
landscape as a source of durable architectural patterns, and the failure modes unique
to multiple agents working together.

**Sources:** primary orchestration-framework documentation, papers on multi-agent
coordination and its failure modes, and dated practitioner write-ups. No single
canonical book exists for this field. See each lesson's `source:` front matter for its
specific citations, and
[agent-docs/fast-moving-domain-policy.md](../../agent-docs/fast-moving-domain-policy.md).

**How to use this subject:** read a lesson on your own, then ask to *discuss
`multi-agent-orchestration/<NN>`* (e.g. *"discuss `multi-agent-orchestration/03`"*).
Concepts are ordered by dependency, so top-to-bottom is a sensible reading order.

**Seniority baseline:** senior (lessons range mid->staff).

**Durability:** durable - every concept below is expected to age slowly; the current
named frameworks that exemplify each orchestration pattern live in
`landscape-snapshot/02`. See
[agent-docs/fast-moving-domain-policy.md](../../agent-docs/fast-moving-domain-policy.md).

## Concepts

| ID  | Concept | Seniority | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | --------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | Single-agent vs multi-agent: when splitting actually helps | mid | drafted | — | — | [lesson](lessons/01-single-agent-vs-multi-agent.md) | — |
| 02  | Subagents: delegation with context isolation | mid | drafted | — | — | [lesson](lessons/02-subagents-delegation-with-context-isolation.md) | — |
| 03  | Orchestration patterns: deterministic workflows vs autonomous delegation | senior | drafted | — | — | [lesson](lessons/03-orchestration-patterns.md) | — |
| 04  | Coordination mechanisms: shared state, message passing, and task lists | senior | drafted | — | — | [lesson](lessons/04-coordination-mechanisms.md) | — |
| 05  | Orchestration architecture patterns: graph-based, role-based, and deterministic-script approaches | senior | drafted | — | — | [lesson](lessons/05-orchestration-architecture-patterns.md) | — |
| 06  | Multi-agent failure modes: coordination overhead and emergent behavior | staff | drafted | — | — | [lesson](lessons/06-multi-agent-failure-modes.md) | — |
| 07  | Governance in multi-agent systems: authorization propagation | staff | drafted | — | — | [lesson](lessons/07-governance-in-multi-agent-systems.md) | — |

**Status:** `drafted` (lesson written) · `discussed` (at least one discussion held).
**Mastery:** `solid` · `partial` · `shaky` · `not-yet` - set from the most recent
discussion's verdict; empty until first discussed.
**Cross-subject prerequisites**: `01` builds on `tool-use-agentic-loop/03`; `02` builds
on `prompting-context-engineering/10`; `07` cross-links to
`agent-security-and-operations/03`. All named per lesson in front matter and prose.
