# Evaluating & Testing Agentic Systems - Subject Summary

A comprehensive recap of this subject, concept by concept.

**Progress note:** all 7 lessons are `drafted`; none have been discussed yet, so
mastery is pending across the board and no weak spots are recorded. This summary will
gain depth (especially on the concepts you find hard) as discussions happen - the
"Focus areas" section at the bottom will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom
(dependency-ordered).

## Concepts

- **[agent-evaluation/01] Why agent evaluation isn't unit testing** - an agentic loop
  breaks the assert-equal contract on all three fronts at once: non-determinism, no
  single correct output, and correctness depending on the multi-step path taken, not
  just the final answer. ([lesson](lessons/01-why-agent-evaluation-isnt-unit-testing.md))
- **[agent-evaluation/02] What benchmarks measure and their blind spots** - a
  benchmark score is "how well on this specific finite task set, scored this specific
  way," and every qualifier is a place it can mislead - contamination, narrow task
  distribution, or saturation/overfitting.
  ([lesson](lessons/02-what-benchmarks-measure.md))
- **[agent-evaluation/03] LLM-as-judge** - using a second model to apply correctness
  criteria at scale is far cheaper than human review but inherits documented biases -
  position, verbosity, and self-preference - that can silently invalidate verdicts
  unless the judge is designed to resist them.
  ([lesson](lessons/03-llm-as-judge.md))
- **[agent-evaluation/04] Trajectory evaluation** - outcome-only scoring misses agents
  that got the right answer through an unreliable, wasteful, or unsafe path; scoring
  the full plan-act-observe sequence catches "works until it doesn't" systems that
  outcome checking cannot. ([lesson](lessons/04-trajectory-evaluation.md))
- **[agent-evaluation/05] Offline vs online evaluation** - offline (curated set,
  pre-ship, full ground truth) tells you a change is safe to ship; online (sampled
  live traffic, tight latency/cost budget) tells you what you shipped is still
  working - neither substitutes for the other.
  ([lesson](lessons/05-offline-vs-online-evaluation.md))
- **[agent-evaluation/06] Regression testing for prompts and agent behavior** -
  without a deterministic pass/fail signal, a useful regression suite replaces
  exact-match assertions with paired statistical comparisons against a pinned
  baseline; building it well is a staff-level recurring cost/coverage trade-off.
  ([lesson](lessons/06-regression-testing-for-agent-behavior.md))
- **[agent-evaluation/07] Multi-judge and debate-based evaluation** - a single judge
  is one biased estimator that a "better" judge model doesn't fix, since the biases
  are structural; multi-judge panels average out uncorrelated bias, debate protocols
  resolve disagreement through argument - not interchangeable, and neither free.
  ([lesson](lessons/07-multi-judge-and-debate-based-evaluation.md))

## Focus areas

None yet - no discussions have been held. After each discussion, the recorded weak
spots and misconceptions will be aggregated here, with extra detail on the concepts
rated `shaky` or `not-yet`.
