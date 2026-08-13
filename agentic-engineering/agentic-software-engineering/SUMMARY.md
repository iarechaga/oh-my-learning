# Agentic Software Engineering - Subject Summary

A comprehensive recap of this subject, concept by concept.

**Progress note:** all 6 lessons are `drafted`; none have been discussed yet, so
mastery is pending across the board and no weak spots are recorded. This summary will
gain depth (especially on the concepts you find hard) as discussions happen - the
"Focus areas" section at the bottom will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom
(dependency-ordered).

## Concepts

- **[agentic-software-engineering/01] Where coding agents run** - a coding agent is an
  agentic loop whose tools happen to be file/shell/test operations; what differs
  between products is where that loop executes and who watches it run - three durable
  execution models (IDE-integrated, terminal-native, cloud/async) with different
  trust and feedback-loop implications. ([lesson](lessons/01-where-coding-agents-run.md))
- **[agentic-software-engineering/02] Vibe coding vs controlled agent use** - not "bad
  practice" versus "good practice" but two ends of a real spectrum, each correct for
  different stakes; the professional skill is choosing where a given piece of work
  belongs, not defaulting to one end.
  ([lesson](lessons/02-vibe-coding-vs-controlled-agent-use.md))
- **[agentic-software-engineering/03] Spec-driven development** - treats a versioned
  spec, not the generated code, as the primary artifact; emerged in 2025 specifically
  as a structural fix to three documented failure modes of unconstrained agentic
  coding - intent drift, context decay, and unverifiable output.
  ([lesson](lessons/03-spec-driven-development.md))
- **[agentic-software-engineering/04] Plan-then-execute workflows** - a separate
  decision from having a spec: does the agent go straight to code, or produce an
  explicit, reviewable, reversible-step plan first? Turns one large hard-to-review
  change into small checkable ones, at the cost of an extra round-trip.
  ([lesson](lessons/04-plan-then-execute-workflows.md))
- **[agentic-software-engineering/05] Code review for agent-generated work** -
  genuinely not the same activity as reviewing a human's code: no author to interrogate,
  no ego/defensiveness, unlimited re-review - but a new dominant risk, fluent
  confidently-wrong code, replaces the sloppy-looking mistakes human review is tuned
  to catch. ([lesson](lessons/05-code-review-for-agent-generated-work.md))
- **[agentic-software-engineering/06] Autonomous software engineering** - staff-level
  trust calibration for how much unsupervised scope to grant an agent, reasoned from
  blast radius, reversibility, and per-task-category evidence quality tracked over
  time, not a fixed one-time autonomy grant.
  ([lesson](lessons/06-autonomous-software-engineering.md))

## Focus areas

None yet - no discussions have been held. After each discussion, the recorded weak
spots and misconceptions will be aggregated here, with extra detail on the concepts
rated `shaky` or `not-yet`.
