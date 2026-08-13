# Landscape Snapshot - Subject Summary

A comprehensive recap of this subject, concept by concept.

**Progress note:** all 7 lessons are `drafted`; none have been discussed yet, so
mastery is pending across the board and no weak spots are recorded. This summary will
gain depth (especially on the concepts you find hard) as discussions happen - the
"Focus areas" section at the bottom will fill in from discussion records.

**This is the one perishable subject in `agentic-engineering`.** Lessons 01-06 are
tagged `durability: perishable`, `next_review: 2026-11`, and will need a quarterly
refresh (see [agent-docs/fast-moving-domain-policy.md](../../agent-docs/fast-moving-domain-policy.md));
lesson 07 is durable methodology. See the progress table in [README.md](README.md).

## Concepts

- **[landscape-snapshot/01] Coding agent products today** - who currently builds each
  of the three durable execution models: Claude Code/Codex CLI (terminal-native),
  Cursor/Copilot/Devin Desktop (IDE-integrated), Devin/Copilot coding agent/Codex Cloud
  (cloud/async), plus Amazon Q Developer spanning several.
  ([lesson](lessons/01-coding-agent-products-today.md))
- **[landscape-snapshot/02] Orchestration frameworks today** - LangGraph (graph-based),
  CrewAI (role-based), Microsoft's newly-merged Agent Framework plus OpenAI's and
  Anthropic's agent SDKs (deterministic-script/hybrid); 2026's big story is
  consolidation (AutoGen+Semantic Kernel merger, AG2 community fork).
  ([lesson](lessons/02-orchestration-frameworks-today.md))
- **[landscape-snapshot/03] Interoperability protocols beyond MCP** - A2A for
  agent-to-agent coordination (ACP merged into it), AG-UI for UI-facing streaming,
  AP2/x402 for agent payments, and ANP as an early-stage decentralized alternative.
  ([lesson](lessons/03-interoperability-protocols-beyond-mcp.md))
- **[landscape-snapshot/04] Benchmarks and leaderboards in use today** - SWE-bench
  Verified (now contested) and SWE-bench Pro, tau²-bench, Terminal-Bench, GAIA/WebArena,
  and METR's Time Horizon suite, each with documented current limitations.
  ([lesson](lessons/04-benchmarks-and-leaderboards-today.md))
- **[landscape-snapshot/05] Model capability tiers and pricing today** - the three
  major providers each sell roughly three comparable tiers (flagship, balanced,
  budget); the numbers behind the routing/caching/budget discipline taught in
  `agent-security-and-operations/05`.
  ([lesson](lessons/05-model-capability-tiers-and-pricing-today.md))
- **[landscape-snapshot/06] Skill and instruction file formats today** - `SKILL.md`'s
  strict two-field frontmatter and body guideline vs. `AGENTS.md`'s frontmatter-free
  always-loaded convention (this repository's own `AGENTS.md`/`CLAUDE.md` among them);
  the current syntax for the process taught in `instruction-and-context-design/08`.
  ([lesson](lessons/06-skill-and-instruction-file-formats-today.md))
- **[landscape-snapshot/07] Where to track what changed** - the durable capstone:
  lessons 01-06 will be wrong within months by design; this lesson teaches finding out
  what changed - primary sources over secondary aggregators, evaluating source
  reliability, and a sustainable review cadence.
  ([lesson](lessons/07-where-to-track-what-changed.md))

## Focus areas

None yet - no discussions have been held. After each discussion, the recorded weak
spots and misconceptions will be aggregated here, with extra detail on the concepts
rated `shaky` or `not-yet`.
