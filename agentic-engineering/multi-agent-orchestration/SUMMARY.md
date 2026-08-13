# Multi-Agent Systems & Orchestration - Subject Summary

A comprehensive recap of this subject, concept by concept.

**Progress note:** all 7 lessons are `drafted`; none have been discussed yet, so
mastery is pending across the board and no weak spots are recorded. This summary will
gain depth (especially on the concepts you find hard) as discussions happen - the
"Focus areas" section at the bottom will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom
(dependency-ordered).

## Concepts

- **[multi-agent-orchestration/01] Single-agent vs multi-agent** - splitting a task
  across agents is not a free upgrade over one agentic loop; it trades a large,
  predictable rise in token cost and coordination complexity for context isolation and
  true parallelism, worth it only when subtasks are genuinely independent.
  ([lesson](lessons/01-single-agent-vs-multi-agent.md))
- **[multi-agent-orchestration/02] Subagents: delegation with context isolation** - a
  subagent runs a scoped piece of work in its own fresh context and reports back a
  distilled result, not its full trace - the parent stays clean at the cost of a
  briefing tax and a trust tax (the parent only sees what got reported).
  ([lesson](lessons/02-subagents-delegation-with-context-isolation.md))
- **[multi-agent-orchestration/03] Orchestration patterns** - who decides the sequence
  of agent activity: fixed in code ahead of time (deterministic workflow) or decided
  by the agents at runtime (autonomous delegation) - a spectrum, not a binary, and a
  genuine predictability-vs-adaptability trade-off.
  ([lesson](lessons/03-orchestration-patterns.md))
- **[multi-agent-orchestration/04] Coordination mechanisms** - how multiple agents
  avoid duplicating work or acting on stale information (coordinator, shared state,
  message passing, shared task queue) is a structural decision that determines a
  system's bottlenecks and failure modes, not interchangeable plumbing.
  ([lesson](lessons/04-coordination-mechanisms.md))
- **[multi-agent-orchestration/05] Orchestration architecture patterns** - three
  durable control-flow patterns re-appear under new framework names every year:
  graph-based (explicit state machine), role-based (personas that negotiate), and
  deterministic-script (code calls agents as functions).
  ([lesson](lessons/05-orchestration-architecture-patterns.md))
- **[multi-agent-orchestration/06] Multi-agent failure modes** - multiple agents add a
  failure surface that doesn't exist with one: coordination overhead, duplicated work,
  conflicting concurrent actions, and emergent behavior nobody designed - research puts
  production failure rates at 41-87%, mostly from coordination defects, not capability.
  ([lesson](lessons/06-multi-agent-failure-modes.md))
- **[multi-agent-orchestration/07] Governance in multi-agent systems** - when one agent
  delegates to another, what the delegate is actually allowed to do is an unsolved,
  actively-researched authorization-propagation problem - naive delegation
  over-permissions, naive re-scoping breaks legitimate workflows.
  ([lesson](lessons/07-governance-in-multi-agent-systems.md))

## Focus areas

None yet - no discussions have been held. After each discussion, the recorded weak
spots and misconceptions will be aggregated here, with extra detail on the concepts
rated `shaky` or `not-yet`.
