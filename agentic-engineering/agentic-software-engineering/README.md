# Agentic Software Engineering

Applying the rest of the domain specifically to writing software: the execution models
coding agents run under, the real distinction between vibe coding and controlled agent
use, spec-driven development, plan-then-execute workflows, reviewing agent-generated
work, and what changes once agents work asynchronously at PR granularity.

**Sources:** primary coding-agent product documentation, dated practitioner
engineering write-ups on agentic development practice, and this repository's own
`AGENTS.md`-driven workflow as one worked example among others. No single canonical
book exists for this field. See each lesson's `source:` front matter once authored,
and
[agent-docs/fast-moving-domain-policy.md](../../agent-docs/fast-moving-domain-policy.md).

**How to use this subject:** read a lesson on your own, then ask to *discuss
`agentic-software-engineering/<NN>`* (e.g. *"discuss `agentic-software-engineering/03`"*).
Concepts are ordered by dependency, so top-to-bottom is a sensible reading order.

**Seniority baseline:** senior (lessons range mid->staff).

**Durability:** durable - every concept below is expected to age slowly; the current
named coding-agent products that exemplify each execution model live in
`landscape-snapshot/01`. See
[agent-docs/fast-moving-domain-policy.md](../../agent-docs/fast-moving-domain-policy.md).

## Concepts

| ID  | Concept | Seniority | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | --------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | Where coding agents run: terminal, IDE, and cloud execution models | mid | drafted | — | — | [lesson](lessons/01-where-coding-agents-run.md) | — |
| 02  | Vibe coding vs controlled agent use: where the line actually is | mid | drafted | — | — | [lesson](lessons/02-vibe-coding-vs-controlled-agent-use.md) | — |
| 03  | Spec-driven development: specs as the source of truth | senior | drafted | — | — | [lesson](lessons/03-spec-driven-development.md) | — |
| 04  | Plan-then-execute workflows and task decomposition | senior | drafted | — | — | [lesson](lessons/04-plan-then-execute-workflows.md) | — |
| 05  | Code review for agent-generated work | senior | drafted | — | — | [lesson](lessons/05-code-review-for-agent-generated-work.md) | — |
| 06  | Autonomous software engineering: async agents and trust calibration | staff | drafted | — | — | [lesson](lessons/06-autonomous-software-engineering.md) | — |

**Status:** `drafted` (lesson written) · `discussed` (at least one discussion held).
**Mastery:** `solid` · `partial` · `shaky` · `not-yet` - set from the most recent
discussion's verdict; empty until first discussed.
**Cross-subject prerequisites**: `01` builds on `tool-use-agentic-loop/03`; `05`
cross-links to `software-engineering/legacy-code` (reviewing unfamiliar code applies
directly to reviewing generated code); `06` builds on
`multi-agent-orchestration/03`. All named per lesson in front matter and prose.
