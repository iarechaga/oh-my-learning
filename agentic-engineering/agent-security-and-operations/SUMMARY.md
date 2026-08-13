# Security, Cost, and Production Operations - Subject Summary

A comprehensive recap of this subject, concept by concept.

**Progress note:** all 8 lessons are `drafted`; none have been discussed yet, so
mastery is pending across the board and no weak spots are recorded. This summary will
gain depth (especially on the concepts you find hard) as discussions happen - the
"Focus areas" section at the bottom will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom
(dependency-ordered).

## Concepts

- **[agent-security-and-operations/01] The threat model** - a model reads one
  undifferentiated token stream with no reliable mechanism marking some tokens
  "trusted instruction" and others "untrusted data" - the architectural starting
  point for every other lesson in this subject.
  ([lesson](lessons/01-the-threat-model.md))
- **[agent-security-and-operations/02] Prompt injection** - direct (attacker talks to
  the agent) vs. indirect (attacker plants content the agent reads later), defended
  only by defense-in-depth - multiple overlapping controls, none sufficient alone.
  ([lesson](lessons/02-prompt-injection.md))
- **[agent-security-and-operations/03] Least-privilege tool permissions** - the layer
  that matters most doesn't depend on the model behaving correctly at all: give an
  agent only the tools/scopes/credentials its task actually requires, so even a fully
  "convinced" model can't do more damage than its narrow privilege allows.
  ([lesson](lessons/03-least-privilege-tool-permissions.md))
- **[agent-security-and-operations/04] Human-in-the-loop gates** - run autonomously
  through reversible steps, stop before anything that can't be cleanly undone; the
  gate's design determines whether it catches errors or becomes a rubber stamp.
  ([lesson](lessons/04-human-in-the-loop-gates.md))
- **[agent-security-and-operations/05] Token economics** - an agent costs 3-10x more
  than chat for the same nominal task because a turn hides a multi-step loop; control
  it with model routing by task complexity, caching, and explicit fail-fast budgets.
  ([lesson](lessons/05-token-economics.md))
- **[agent-security-and-operations/06] Observability for agents** - tracing
  infrastructure carries over from SRE practice; what's new is capturing why an agent
  decided what it did, since the same input can produce a different trace shape on
  different runs. ([lesson](lessons/06-observability-for-agents.md))
- **[agent-security-and-operations/07] Failure modes and verification** - a deployed
  agent keeps producing hallucination, silent drift, and distribution shift after its
  one-time pre-deployment eval score was recorded; trust calibration for a running
  system needs its own continuous, live verification.
  ([lesson](lessons/07-failure-modes-and-verification.md))
- **[agent-security-and-operations/08] Operating agent fleets** - a fleet of agents is
  not one agent scaled up; accountability stops being traceable past a certain
  delegation depth, and the principal-level job is making an explicit, defensible,
  org-communicated bet about where accountability lives.
  ([lesson](lessons/08-operating-agent-fleets.md))

## Focus areas

None yet - no discussions have been held. After each discussion, the recorded weak
spots and misconceptions will be aggregated here, with extra detail on the concepts
rated `shaky` or `not-yet`.
