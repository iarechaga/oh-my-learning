# Landscape Snapshot

A dated survey of the concrete products, frameworks, protocols, benchmarks, pricing,
and file formats that exemplify the durable concepts taught in the other eight
subjects of this domain. This is the **one subject in `agentic-engineering` built to be
rewritten, not preserved** - every lesson here names specific products and is expected
to date. Read the other subjects for the concepts that outlast this one.

**Sources:** current product documentation, pricing pages, benchmark leaderboards, and
recent (dated) practitioner comparisons - deliberately the most perishable sources in
the domain. See each lesson's `source:` front matter once authored, and
[agent-docs/fast-moving-domain-policy.md](../../agent-docs/fast-moving-domain-policy.md)
for the review policy this subject follows.

**How to use this subject:** read a lesson on your own, then ask to *discuss
`landscape-snapshot/<NN>`* (e.g. *"discuss `landscape-snapshot/01`"*). There is no
strong dependency order between concepts `01`-`06` - each maps to one durable subject
elsewhere in the domain and can be read once that subject is covered. `07` is a
capstone and reads best last.

**Seniority baseline:** mid (lessons range mid->staff).

**Durability: perishable, by design.** This subject is reviewed on a fixed quarterly
cadence, not opportunistically like the rest of the domain. Every concept below is
tagged `durability: perishable` in its lesson front matter once authored (except `07`,
which is durable methodology despite living here), with a `next_review` date - when
that date has passed, the row below is stale and it is safe to assume so without
reading the lesson. See
[agent-docs/fast-moving-domain-policy.md](../../agent-docs/fast-moving-domain-policy.md)
for the full policy, the review workflow, and what this implies for versioning and the
changelog.

## Concepts

| ID  | Concept | Seniority | Durability | Next review | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | --------- | ---------- | ------------ | ------ | ------- | -------------- | ------ | ------- |
| 01  | Coding agent products today: terminal, IDE, and cloud options | mid | perishable | — (set on authoring) | drafted | — | — | [lesson](lessons/01-coding-agent-products-today.md) | — |
| 02  | Orchestration frameworks today: LangGraph, CrewAI, AutoGen, and alternatives | mid | perishable | — (set on authoring) | drafted | — | — | [lesson](lessons/02-orchestration-frameworks-today.md) | — |
| 03  | Interoperability protocols beyond MCP: what else exists today | mid | perishable | — (set on authoring) | drafted | — | — | [lesson](lessons/03-interoperability-protocols-beyond-mcp.md) | — |
| 04  | Benchmarks and leaderboards in use today | mid | perishable | — (set on authoring) | drafted | — | — | [lesson](lessons/04-benchmarks-and-leaderboards-today.md) | — |
| 05  | Model capability tiers and pricing today | mid | perishable | — (set on authoring) | drafted | — | — | [lesson](lessons/05-model-capability-tiers-and-pricing-today.md) | — |
| 06  | Skill and instruction file formats today | mid | perishable | — (set on authoring) | drafted | — | — | [lesson](lessons/06-skill-and-instruction-file-formats-today.md) | — |
| 07  | Where to track what changed: staying current after this domain ages | staff | durable | n/a | drafted | — | — | [lesson](lessons/07-where-to-track-what-changed.md) | — |

**Status:** `drafted` (lesson written) · `discussed` (at least one discussion held).
**Mastery:** `solid` · `partial` · `shaky` · `not-yet` - set from the most recent
discussion's verdict; empty until first discussed.
**Next review** is set the moment a lesson is authored (typically its `created` date
plus one quarter), not before - there is nothing to review yet. See
[agent-docs/fast-moving-domain-policy.md](../../agent-docs/fast-moving-domain-policy.md).
**Cross-subject prerequisites**: `01`->`agentic-software-engineering/01`,
`02`->`multi-agent-orchestration/05`, `03`->`model-context-protocol/03`,
`04`->`agent-evaluation/02`, `05`->`agent-security-and-operations/05`,
`06`->`instruction-and-context-design/08`. All named per lesson in front matter and
prose.
