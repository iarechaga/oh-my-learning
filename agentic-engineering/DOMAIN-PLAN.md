# Domain plan: Agentic Engineering (draft, pending review)

Status: **planning document, not yet a scaffolded domain**. No subjects, lessons, or
domain `README.md` exist yet. This file is a working artifact for reviewing scope
before running Workflow A (see `agent-docs/learning-workflows.md`); it should be
deleted or folded into the domain `README.md` once the human approves the plan and
scaffolding begins.

## Why this domain

Working effectively with LLMs at an advanced level, and using the agent capabilities
that exist today, is now a distinct engineering discipline from both "software
engineering" (writing code) and "architecture" (designing systems). It has its own
failure modes (context rot, tool misuse, prompt injection), its own economics (token
cost, latency, caching), and its own body of practice (context engineering, agent
harness design, multi-agent orchestration) that does not fit cleanly inside any
existing domain. It also matches the repo's public roadmap item on agent-assisted
programming (Claude Code, opencode, harnesses, building agents).

## Proposed domain slug and name

**`agentic-engineering`** - "Agentic Engineering"

Alternatives considered and rejected:
- `ai-agents` - too narrow; would awkwardly host prompting/context-engineering content
  that is not agentic on its own.
- `llm-engineering` - undersells the agent-loop, tool-use, and orchestration material,
  which is the more novel/differentiated part of the domain.
- `working-with-llms` - reads as a how-to guide title, inconsistent with the other
  domain names (`Domain Modeling`, `Technical Leadership`, etc.), which name a
  discipline, not an activity.

## Proposed subjects (4)

Division rationale: split by **layer of abstraction**, the same way `architecture`
splits by book/scope. Each layer builds on the one before it.

### 1. `prompting-and-context` - Prompting & Context Engineering
Baseline: junior-mid. The foundation: how the model actually consumes what you give
it, and the engineering discipline of managing that input over a session.

| # | Concept | Seniority | Depends on |
|---|---|---|---|
| 01 | How LLMs process a prompt (tokens, attention, no hidden state between calls) | junior | - |
| 02 | Prompting techniques and their real limits (zero/few-shot, chain-of-thought, decomposition - what breaks and why) | junior | 01 |
| 03 | Instruction hierarchy: system vs developer vs user prompts | junior | 01 |
| 04 | Context window mechanics and "lost in the middle" | mid | 01 |
| 05 | Structured output and schema-constrained generation | mid | 02 |
| 06 | Context engineering: deciding what belongs in the context window | mid | 04 |
| 07 | Context compaction and long-running session management | senior | 06 |
| 08 | Retrieval-augmented generation vs long context: when to use which | senior | 04, 06 |
| 09 | Prompt caching: mechanics and its effect on cost, latency, and prompt design | mid | 04 |

### 2. `tool-use-and-agents` - Tool Use, Function Calling & Agentic Loops
Baseline: mid-senior. How a model stops being a text generator and starts taking
actions: calling tools, looping, planning, and coordinating with other agents.

| # | Concept | Seniority | Depends on |
|---|---|---|---|
| 01 | Function calling / tool use mechanics | mid | prompting-and-context/01 |
| 02 | Designing good tools for an agent (description quality, granularity, error surfaces) | mid | 01 |
| 03 | The agentic loop: plan-act-observe and termination conditions | mid | 01 |
| 04 | Model Context Protocol (MCP): architecture and why a standard emerged | senior | 01, 02 |
| 05 | Planning strategies: single-shot, ReAct, plan-and-execute, tree-of-thought | senior | 03 |
| 06 | Multi-agent orchestration patterns (subagents, supervisor/worker, handoffs) | senior | 03, 05 |
| 07 | Memory across sessions vs conversation memory | senior | prompting-and-context/07 |
| 08 | Human-in-the-loop and approval gates | senior | 03 |

### 3. `agent-harnesses-and-coding-workflows` - Agent Harnesses & Agentic Coding Workflows
Baseline: mid-senior. How the agentic loop gets productized into a tool a developer
actually drives day to day, and how that changes the coding workflow itself.

| # | Concept | Seniority | Depends on |
|---|---|---|---|
| 01 | What a harness is and what it adds beyond a raw model | mid | tool-use-and-agents/03 |
| 02 | Anatomy of a coding-agent harness (tool loop, permission model, context injection) | senior | 01, tool-use-and-agents/04 |
| 03 | Comparing harness shapes: terminal-native, IDE-native, autonomous/background | mid | 01 |
| 04 | Permission models and sandboxing for coding agents | senior | 02 |
| 05 | Reusable capabilities: skills, slash-commands, custom subagents | mid | tool-use-and-agents/06 |
| 06 | Parallel and background agents; worktrees and isolation | senior | 02, 05 |
| 07 | Agentic git/PR workflows and code review by agents | mid | 03 |
| 08 | Building a custom agent with an agent SDK | senior | 02, tool-use-and-agents/06 |

### 4. `evaluation-safety-and-economics` - Evaluating, Securing, and Operating LLM Systems
Baseline: senior-staff. Once you can build agentic systems, how do you know they
work, keep working, stay safe, and stay affordable?

| # | Concept | Seniority | Depends on |
|---|---|---|---|
| 01 | Why LLM systems need evals (non-determinism, regression risk) | senior | prompting-and-context/02 |
| 02 | Building evals: golden sets, metrics, LLM-as-judge, and its pitfalls | senior | 01 |
| 03 | Agent failure modes and verification strategies (hallucination, tool misuse, drift, looping) | senior | tool-use-and-agents/03 |
| 04 | Prompt injection and agent security (least privilege, sandboxing, the agentic OWASP risks) | senior | agent-harnesses-and-coding-workflows/04 |
| 05 | Cost and latency management (model routing, caching, batching) | staff | prompting-and-context/09 |
| 06 | Observability and tracing for agentic systems | staff | 02, 03 |
| 07 | When NOT to use an agent (decomposing back to deterministic code) | staff | 03, 06 |

**Total: 32 concepts across 4 subjects.**

## Fit with the 8 existing domains and cross-domain prerequisites

- **`software-engineering`** - agentic coding workflows produce code judged by the
  same craft standards (clean code, refactoring). `agent-harnesses-and-coding-workflows/07`
  (agentic PR/review workflows) assumes familiarity with that domain's review/quality
  lessons.
- **`software-quality`** - `evaluation-safety-and-economics/02` (building evals) is a
  direct extension of unit-testing/xUnit test-design principles to a non-deterministic
  system; recommend it as a soft prerequisite, not a hard one.
- **`devops-reliability`** - `evaluation-safety-and-economics/06` (observability and
  tracing) reuses SRE observability concepts (SLOs, telemetry) applied to agent traces.
- **`technical-leadership`** - `evaluation-safety-and-economics/07` (when NOT to use an
  agent) is a judgment-under-ambiguity concept in the same register as staff/principal
  lessons in that domain; no hard dependency, but worth cross-linking.
- No existing domain is a hard prerequisite for entry: `prompting-and-context` is
  designed to be a valid starting point for a learner with general programming
  background and no prior exposure to this repo's other domains.

## The anchoring problem (needs a decision before scaffolding)

Every existing subject anchors to one canonical, stable book (`ddia`, `clean-code`,
`staff-engineer`, ...). This domain has no equivalent: there is no single canonical
book on "working with LLM agents," and whatever exists today may be outdated in
6-12 months given the pace of harness/protocol change.

**Recommendation: do not force a single book.** Anchor each subject to a **primary
references list** instead of a source book:
- Official/primary documentation (model provider engineering blogs, the MCP
  specification, harness documentation) as the closest thing to ground truth for
  fast-moving facts.
- Foundational papers for durable ideas that predate and outlive any one product
  (e.g. the ReAct pattern, tool-use/function-calling papers, context-window/attention
  behavior).
- Practitioner-distilled writing only where it captures a genuinely stable pattern,
  not a specific tool's current UI.

Two content-writing rules to keep this from rotting silently:
1. **Favor durable principles over point-in-time product facts** in "How it works" -
   e.g. teach "an agent loop needs a termination condition" (durable) rather than
   "Tool X's default max-turns is 50" (rots fast).
2. **Date every claim that is genuinely time-bound**, inline in prose (e.g. "as of
   2026-08, Claude Code's subagents each carry their own model and permission scope")
   so a future reader knows to verify rather than assume it is still true. This is a
   prose convention, not a schema change.

## What this implies for repo assumptions - flagging, not deciding unilaterally

1. **Subject `README.md` format.** `agent-docs/repository-model.md` specifies a
   "source book" line. This domain needs a documented exception: **"Primary
   references"** (a short list) instead of a single book title. This is a small,
   additive documentation change to `repository-model.md`, not a breaking one - it
   does not change any existing subject's README.
2. **Front-matter schema / freshness tracking.** I considered adding a `verified:
   <date>` front-matter field distinct from `updated`, to make staleness
   machine-checkable. Per `agent-docs/release-policy.md`, "restructuring the
   front-matter schema" is explicitly called out as a **MAJOR** (breaking) change,
   which conflicts with this repo just having reached the "stable, structure-frozen"
   `1.0.0` milestone.
   **I'm not deciding this one for you.** Two honest options:
   - **(a) No schema change (recommended for now).** Keep freshness signals in
     prose only: a "Last verified: `<date>`" line in each subject `README.md`
     (not front matter) plus the inline dating convention above. This keeps the
     domain addition a clean MINOR release, at the cost of freshness not being
     machine-checkable or catalog-visible.
   - **(b) Add the `verified` front-matter field.** More rigorous and greppable,
     but is a schema change that arguably deserves a `2.0.0` under the repo's own
     rules, and it would apply repo-wide (or you'd need to special-case one domain,
     which is its own inconsistency).
3. **The "lessons are permanent" implicit assumption.** Every other domain's lessons
   describe durable engineering knowledge (a load-balancing algorithm does not change
   meaning in a year). This domain will have lessons that are more likely to need
   periodic re-authoring, not just new-lesson growth. That's a real, ongoing
   maintenance cost this domain introduces that the other 8 do not have - worth
   accepting consciously rather than discovering later.

## What this plan is not

No lessons, subjects, or domain `README.md` are created by this plan. Nothing here
is committed to the concept-ID/prerequisite scheme until the human approves scope,
per Workflow A step 2 ("propose ... confirm scope with the human before
mass-authoring").
