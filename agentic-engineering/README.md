# Agentic Engineering

The `agentic-engineering` **domain** of this learning repository. It covers how to
work effectively with LLMs at an advanced level and how to build, wire, and operate
the agent capabilities that exist today: prompting and context engineering, tool use
and the agentic loop, the instruction/context scaffolding that shapes what an agent
sees and when, interoperability protocols (MCP), multi-agent orchestration, agentic
software engineering practice, evaluation, and security/cost/operations.

Concept IDs are subject-scoped (e.g. `tool-use-agentic-loop/03`,
`instruction-and-context-design/04`), so this `agentic-engineering/` folder organizes
files on disk without changing how you refer to a concept.

## A field without a canonical book, by design

Every other domain in this repository anchors each subject to one canonical, stable
book. This domain cannot: there is no consolidated book on working with LLM agents,
and the concrete landscape (which products exist, which protocols dominate, what a
given API supports) changes on a timescale of months, not years. Rather than force a
fake anchor or refuse to teach a moving target, this domain is built around an
explicit split:

- **Eight subjects teach durable capability** - the mechanics, trade-offs, and failure
  modes of prompting, context, tool use, instruction design, protocols, orchestration,
  evaluation, and security/operations. These age slowly because they describe how the
  underlying problem behaves, not which product solves it today. Named products appear
  only as swappable, boxed-off examples inside a lesson - never as what the concept
  *is*.
- **One subject, `landscape-snapshot`, is explicitly a dated snapshot** - the current
  products, frameworks, and file formats that exemplify the durable concepts taught
  elsewhere. It is reviewed on a fixed cadence and is expected to be rewritten, not
  just corrected, over time.

Each lesson's `source:` front matter cites primary vendor/spec documentation, papers,
and dated practitioner write-ups instead of a single book - see the "Sources" note in
each subject `README.md` below. The full policy - what counts as durable vs
perishable, the `durability`/`next_review` front-matter fields, the review cadence,
and what this means for versioning - is documented in
[agent-docs/fast-moving-domain-policy.md](../agent-docs/fast-moving-domain-policy.md).
Read it before authoring or reviewing any lesson in this domain.

## Subjects

Ordered by dependency - each subject builds on the ones before it.

| Subject | What it is | Lessons | Index |
| --- | --- | --- | --- |
| **[Prompting & Context Engineering](prompting-context-engineering/README.md)** | How a model actually consumes what you give it, advanced prompting and its limits, and the context window as a finite, manageable budget. | 10 | [prompting-context-engineering/README.md](prompting-context-engineering/README.md) |
| **[Tool Use & the Agentic Loop](tool-use-agentic-loop/README.md)** | Function calling mechanics, the plan-act-observe loop, harness vs scaffolding, and knowing when to stop. | 8 | [tool-use-agentic-loop/README.md](tool-use-agentic-loop/README.md) |
| **[Instruction & Context Design](instruction-and-context-design/README.md)** | Engineering the scaffolding around an agent: structured metadata, always-loaded vs on-demand instructions, trigger design, and authoring skills, hooks, and commands. | 11 | [instruction-and-context-design/README.md](instruction-and-context-design/README.md) |
| **[Model Context Protocol & Agent Interoperability](model-context-protocol/README.md)** | Why MCP exists, its architecture and primitives, building and trusting servers, and the wider interoperability picture. | 7 *(scaffold)* | [model-context-protocol/README.md](model-context-protocol/README.md) |
| **[Multi-Agent Systems & Orchestration](multi-agent-orchestration/README.md)** | Subagents, orchestration patterns, coordination mechanisms, and the failure modes unique to multiple agents working together. | 7 *(scaffold)* | [multi-agent-orchestration/README.md](multi-agent-orchestration/README.md) |
| **[Agentic Software Engineering](agentic-software-engineering/README.md)** | Where coding agents run, vibe coding vs controlled use, spec-driven development, and reviewing agent-generated work. | 6 *(scaffold)* | [agentic-software-engineering/README.md](agentic-software-engineering/README.md) |
| **[Evaluating & Testing Agentic Systems](agent-evaluation/README.md)** | Why agent evaluation isn't unit testing, benchmarks, LLM-as-judge, trajectory evaluation, and regression testing for agent behavior. | 7 *(scaffold)* | [agent-evaluation/README.md](agent-evaluation/README.md) |
| **[Security, Cost, and Production Operations](agent-security-and-operations/README.md)** | The prompt-injection threat model, least-privilege permissions, token economics, observability, and operating agent fleets. | 8 *(scaffold)* | [agent-security-and-operations/README.md](agent-security-and-operations/README.md) |
| **[Landscape Snapshot](landscape-snapshot/README.md)** | A dated survey of today's coding agents, orchestration frameworks, protocols, benchmarks, model pricing, and file formats - the one subject in this domain built to be rewritten, not preserved. | 7 *(scaffold)* | [landscape-snapshot/README.md](landscape-snapshot/README.md) |

All nine subjects are scaffolded (concept lists and indexes ready). Three are fully
authored - **Prompting & Context Engineering** (10/10), **Tool Use & the Agentic Loop**
(8/8), and **Instruction & Context Design** (11/11); the remaining six have lesson
bodies not yet authored.

The track moves from raw model behavior (Prompting & Context Engineering), to giving
that model the ability to act (Tool Use & the Agentic Loop), to engineering everything
that shapes what it sees and when (Instruction & Context Design), to interoperability
(MCP), to composing several agents (Multi-Agent Systems & Orchestration), to applying
all of it to software engineering specifically (Agentic Software Engineering), to
knowing whether any of it actually works (Evaluating & Testing Agentic Systems), to
running it safely and affordably in production (Security, Cost, and Production
Operations) - and closes with a dated snapshot of the concrete landscape
(Landscape Snapshot) that the other eight deliberately keep at arm's length.

No existing domain is a hard prerequisite for starting here - `prompting-context-engineering`
is a valid entry point for a learner with general programming background. Several
higher-band concepts cross-link into existing domains as soft prerequisites:
`agentic-software-engineering` into `software-engineering/legacy-code` (reviewing
unfamiliar generated code), `agent-evaluation` into `software-quality/unit-testing`
and `technical-leadership/how-to-measure-anything` (testing mindset and calibration),
and `agent-security-and-operations` into `devops-reliability/sre` (observability,
incident response) and `technical-leadership/staff-engineer` (organizational
governance). See each subject's `README.md` for the specific concept.

See each subject's `README.md` for its concept index and progress, and the root
[SUMMARY.md](../SUMMARY.md) for the cross-domain overview.
