# Prompting & Context Engineering

The foundation of the domain: how a model actually consumes what you give it, the
prompting techniques that reliably help (and the ones that are theater), and the
discipline of managing the context window as a finite, per-turn budget rather than an
unlimited scratchpad. Everything else in `agentic-engineering` assumes this.

**Sources:** primary model-provider documentation and engineering blogs, foundational
papers on prompting and context behavior, and dated practitioner write-ups - no single
canonical book exists for this field. See each lesson's `source:` front matter for its
specific citations, and
[agent-docs/fast-moving-domain-policy.md](../../agent-docs/fast-moving-domain-policy.md)
for why this domain cites this way.

**How to use this subject:** read a lesson on your own, then ask to *discuss
`prompting-context-engineering/<NN>`* (e.g. *"discuss `prompting-context-engineering/07`"*).
Concepts are ordered by dependency, so top-to-bottom is a sensible reading order.

**Seniority baseline:** senior (lessons range junior->staff).

**Durability:** durable - every concept below is expected to age slowly; this subject
has no `landscape-snapshot`-style perishable content of its own. See
[agent-docs/fast-moving-domain-policy.md](../../agent-docs/fast-moving-domain-policy.md).

## Concepts

| ID  | Concept | Seniority | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | --------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | What LLMs actually do: tokens, context windows, and autoregression | junior | drafted | — | — | [lesson](lessons/01-what-llms-actually-do.md) | — |
| 02  | Prompt anatomy: system, developer, user, and tool turns | junior | drafted | — | — | [lesson](lessons/02-prompt-anatomy.md) | — |
| 03  | Core prompting techniques: few-shot, role, and output formatting | mid | drafted | — | — | [lesson](lessons/03-core-prompting-techniques.md) | — |
| 04  | Chain-of-thought and reasoning effort: what actually helps and what's theater | mid | drafted | — | — | [lesson](lessons/04-chain-of-thought-and-reasoning-effort.md) | — |
| 05  | Structured output: constrained decoding and why it beats free-form parsing | mid | drafted | — | — | [lesson](lessons/05-structured-output.md) | — |
| 06  | The limits of prompting: why some failures aren't prompt problems | senior | drafted | — | — | [lesson](lessons/06-limits-of-prompting.md) | — |
| 07  | Context engineering as a discipline: the context window as a budget | senior | drafted | — | — | [lesson](lessons/07-context-engineering-as-a-discipline.md) | — |
| 08  | Context failure modes: poisoning, distraction, and confusion | senior | drafted | — | — | [lesson](lessons/08-context-failure-modes.md) | — |
| 09  | Retrieval and memory: RAG, long-term memory, and when to use which | senior | drafted | — | — | [lesson](lessons/09-retrieval-and-memory.md) | — |
| 10  | Context compaction and sub-agent handoff for long-horizon tasks | staff | drafted | — | — | [lesson](lessons/10-context-compaction-and-handoff.md) | — |

**Status:** `drafted` (lesson written) · `discussed` (at least one discussion held).
**Mastery:** `solid` · `partial` · `shaky` · `not-yet` - set from the most recent
discussion's verdict; empty until first discussed.
**Cross-subject prerequisites**: this subject has none - it is a valid entry point into
the domain. Concepts `07` and `10` are prerequisites for most other subjects here (see
their `README.md` files) and are named in prose/front matter where used.
