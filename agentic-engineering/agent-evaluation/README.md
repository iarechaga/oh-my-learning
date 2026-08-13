# Evaluating & Testing Agentic Systems

Why evaluating an agent isn't unit testing (non-determinism, trajectories, no single
right answer), how to read a benchmark's methodology and its blind spots, LLM-as-judge
design and its known biases, scoring a trajectory rather than just the outcome, offline
vs online evaluation, and regression testing for prompts and agent behavior.

**Sources:** primary evaluation-framework documentation, benchmark papers and their
methodology sections, and dated practitioner write-ups on LLM-as-judge practice. No
single canonical book exists for this field. See each lesson's `source:` front matter
for its specific citations, and
[agent-docs/fast-moving-domain-policy.md](../../agent-docs/fast-moving-domain-policy.md).

**How to use this subject:** read a lesson on your own, then ask to *discuss
`agent-evaluation/<NN>`* (e.g. *"discuss `agent-evaluation/03`"*). Concepts are ordered
by dependency, so top-to-bottom is a sensible reading order.

**Seniority baseline:** senior (lessons range mid->staff).

**Durability:** durable - every concept below is expected to age slowly; the current
named benchmarks and leaderboards live in `landscape-snapshot/04`. See
[agent-docs/fast-moving-domain-policy.md](../../agent-docs/fast-moving-domain-policy.md).

## Concepts

| ID  | Concept | Seniority | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | --------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | Why agent evaluation isn't unit testing: non-determinism and trajectories | mid | drafted | — | — | [lesson](lessons/01-why-agent-evaluation-isnt-unit-testing.md) | — |
| 02  | What benchmarks measure and their blind spots | mid | drafted | — | — | [lesson](lessons/02-what-benchmarks-measure.md) | — |
| 03  | LLM-as-judge: design, calibration, and known biases | senior | drafted | — | — | [lesson](lessons/03-llm-as-judge.md) | — |
| 04  | Trajectory evaluation: scoring the path, not just the outcome | senior | drafted | — | — | [lesson](lessons/04-trajectory-evaluation.md) | — |
| 05  | Offline vs online evaluation: what runs before ship vs in production | senior | drafted | — | — | [lesson](lessons/05-offline-vs-online-evaluation.md) | — |
| 06  | Regression testing for prompts and agent behavior | staff | drafted | — | — | [lesson](lessons/06-regression-testing-for-agent-behavior.md) | — |
| 07  | Multi-judge and debate-based evaluation | staff | drafted | — | — | [lesson](lessons/07-multi-judge-and-debate-based-evaluation.md) | — |

**Status:** `drafted` (lesson written) · `discussed` (at least one discussion held).
**Mastery:** `solid` · `partial` · `shaky` · `not-yet` - set from the most recent
discussion's verdict; empty until first discussed.
**Cross-subject prerequisites**: `01` builds on `tool-use-agentic-loop/03` and
cross-links to `software-quality/unit-testing` for the general testing mindset; `03`
cross-links to `technical-leadership/how-to-measure-anything` for calibration under
uncertainty. All named per lesson in front matter and prose.
