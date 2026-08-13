# Tool Use & the Agentic Loop

How a model stops being a text generator and starts taking actions: the mechanics of
function calling, designing tool schemas a model can use reliably, the plan-act-observe
loop that turns single calls into an agent, and the harness/scaffolding distinction
that determines what actually wraps and drives the model.

**Sources:** primary model-provider documentation on function calling/tool use, the
ReAct paper and its successors, and dated practitioner engineering write-ups - no
single canonical book exists for this field. See each lesson's `source:` front matter
for its specific citations, and
[agent-docs/fast-moving-domain-policy.md](../../agent-docs/fast-moving-domain-policy.md).

**How to use this subject:** read a lesson on your own, then ask to *discuss
`tool-use-agentic-loop/<NN>`* (e.g. *"discuss `tool-use-agentic-loop/03`"*). Concepts
are ordered by dependency, so top-to-bottom is a sensible reading order.

**Seniority baseline:** senior (lessons range mid->staff).

**Durability:** durable - every concept below is expected to age slowly. See
[agent-docs/fast-moving-domain-policy.md](../../agent-docs/fast-moving-domain-policy.md).

## Concepts

| ID  | Concept | Seniority | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | --------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | Function calling mechanics: how models choose and emit tool calls | mid | drafted | — | — | [lesson](lessons/01-function-calling-mechanics.md) | — |
| 02  | Designing tool schemas: JSON Schema, typed arguments, and description quality | mid | drafted | — | — | [lesson](lessons/02-designing-tool-schemas.md) | — |
| 03  | The agentic loop: plan, act, observe, repeat | mid | drafted | — | — | [lesson](lessons/03-the-agentic-loop.md) | — |
| 04  | Parallel vs sequential tool calls: latency and correctness trade-offs | senior | drafted | — | — | [lesson](lessons/04-parallel-vs-sequential-tool-calls.md) | — |
| 05  | Harness vs scaffolding: what wraps the model and what the model works from | senior | drafted | — | — | [lesson](lessons/05-harness-vs-scaffolding.md) | — |
| 06  | Stateless vs stateful tool execution and retries | senior | drafted | — | — | [lesson](lessons/06-stateless-vs-stateful-tool-execution.md) | — |
| 07  | Designing for recoverable failure: idempotency, timeouts, and retry budgets | senior | drafted | — | — | [lesson](lessons/07-designing-for-recoverable-failure.md) | — |
| 08  | When to stop: termination conditions and runaway-loop prevention | staff | drafted | — | — | [lesson](lessons/08-when-to-stop.md) | — |

**Status:** `drafted` (lesson written) · `discussed` (at least one discussion held).
**Mastery:** `solid` · `partial` · `shaky` · `not-yet` - set from the most recent
discussion's verdict; empty until first discussed.
**Cross-subject prerequisites**: `01` and `03` build on
`prompting-context-engineering/03`; named per lesson in front matter and prose.
