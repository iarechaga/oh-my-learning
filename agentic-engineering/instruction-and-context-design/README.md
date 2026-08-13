# Instruction & Context Design

Practical engineering of the scaffolding that surrounds an agent: every place it reads
instructions from, what earns a permanent slot in context versus what gets deferred,
how a trigger description makes an agent load the right thing at the right moment (and
how that fails), and how to turn a recurring need into a skill, a hook, or a command
instead of repeating yourself in every prompt. This is the practice of deciding what an
agent always knows, what it learns on demand, and how that demand gets triggered
correctly - arguably the most differentiated, least-written-about material in this
domain, and the one closest to this repository's own operating model (`AGENTS.md`
dispatching to `agent-docs/` on documented triggers is itself a specimen of the
pattern taught here - used as one worked example among others, not as the subject).

**Sources:** primary harness/agent-framework documentation on configuration,
instructions, and skills; dated practitioner engineering write-ups on context and
prompt design; this repository's own `AGENTS.md`/`agent-docs/` dispatcher as one
concrete, inspectable case study. No single canonical book exists for this field. See
each lesson's `source:` front matter for its specific citations, and
[agent-docs/fast-moving-domain-policy.md](../../agent-docs/fast-moving-domain-policy.md).

**How to use this subject:** read a lesson on your own, then ask to *discuss
`instruction-and-context-design/<NN>`* (e.g. *"discuss `instruction-and-context-design/04`"*).
Concepts are ordered by dependency, so top-to-bottom is a sensible reading order.

**Seniority baseline:** senior (lessons range mid->staff).

**Durability:** durable - every concept below is expected to age slowly; concrete file
formats and syntax used as examples are kept swappable and point to
`landscape-snapshot/06` for the current specifics. See
[agent-docs/fast-moving-domain-policy.md](../../agent-docs/fast-moving-domain-policy.md).

## Concepts

| ID  | Concept | Seniority | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | --------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | The scaffolding surface: every place an agent reads instructions from | mid | drafted | — | — | [lesson](lessons/01-the-scaffolding-surface.md) | — |
| 02  | Structured metadata as cheap signal: front matter, schemas, and machine-readable config | mid | drafted | — | — | [lesson](lessons/02-structured-metadata-as-cheap-signal.md) | — |
| 03  | Always-loaded vs on-demand: drawing the line in a system prompt | mid | drafted | — | — | [lesson](lessons/03-always-loaded-vs-on-demand.md) | — |
| 04  | Designing trigger descriptions: how an agent decides what to load | senior | drafted | — | — | [lesson](lessons/04-designing-trigger-descriptions.md) | — |
| 05  | Failure modes of deferred loading: over-triggering, under-triggering, and silent gaps | senior | drafted | — | — | [lesson](lessons/05-failure-modes-of-deferred-loading.md) | — |
| 06  | Writing instructions that survive being read out of order | senior | drafted | — | — | [lesson](lessons/06-writing-instructions-that-survive-out-of-order-reading.md) | — |
| 07  | What a skill is and when it's worth building one | mid | drafted | — | — | [lesson](lessons/07-what-a-skill-is.md) | — |
| 08  | Authoring a skill end to end: trigger, body, and supporting files | senior | drafted | — | — | [lesson](lessons/08-authoring-a-skill-end-to-end.md) | — |
| 09  | Evaluating whether a skill actually works | senior | drafted | — | — | [lesson](lessons/09-evaluating-whether-a-skill-works.md) | — |
| 10  | Hooks, slash commands, and other deterministic levers vs model-judged triggers | senior | drafted | — | — | [lesson](lessons/10-hooks-commands-and-deterministic-levers.md) | — |
| 11  | Choosing the right primitive: instructions, tools, skills, hooks, and commands | staff | drafted | — | — | [lesson](lessons/11-choosing-the-right-primitive.md) | — |

**Status:** `drafted` (lesson written) · `discussed` (at least one discussion held).
**Mastery:** `solid` · `partial` · `shaky` · `not-yet` - set from the most recent
discussion's verdict; empty until first discussed.
**Cross-subject prerequisites**: `01` and `03` build on
`prompting-context-engineering/07`; `04` builds on `tool-use-agentic-loop/02`; `09`
cross-links to `agent-evaluation` for the general evaluation methodology applied here;
`11` is deliberately incomplete on first read and points forward to
`model-context-protocol` and `multi-agent-orchestration`, which add MCP servers and
subagents as further primitives to weigh. All named per lesson in front matter and
prose.
