---
id: landscape-snapshot/02
subject: landscape-snapshot
title: "Orchestration Frameworks Today: LangGraph, CrewAI, AutoGen, and Alternatives"
slug: orchestration-frameworks-today
status: drafted
mastery:
seniority: mid
source: "QubitTool, 2026 AI Agent Framework Showdown (2026); OpenAgents Blog, CrewAI vs LangGraph vs AutoGen vs OpenAgents (2026); Microsoft Learn, Microsoft Agent Framework Overview (2026); alexbevi.com, Two Lineages, One Framework: How AutoGen and Semantic Kernel Became the Microsoft Agent Framework (2026); jasonmoon.dev, Microsoft Agent Framework RC (2026); TrueFoundry, Best Multi-agent Orchestration Frameworks in 2026 (2026)"
durability: perishable
next_review: 2026-11
prerequisites: [multi-agent-orchestration/05]
created: 2026-08-10
updated: 2026-08-10
---

# Orchestration Frameworks Today: LangGraph, CrewAI, AutoGen, and Alternatives

## TL;DR
`multi-agent-orchestration/05` names three durable control-flow patterns - graph-based, role-based, and deterministic-script - independent of any framework. As of August 2026, LangGraph is the clearest current implementation of graph-based orchestration, CrewAI the clearest implementation of role-based orchestration, and Microsoft's newly-merged Agent Framework (AutoGen + Semantic Kernel) plus OpenAI's Agents SDK and Anthropic's Claude Agent SDK cover deterministic-script and hybrid shapes. The single biggest 2026 development is consolidation: Microsoft merged two previously separate frameworks into one, and community AG2 forked off Microsoft's now-maintenance-mode original AutoGen.

> **Snapshot date: August 2026.** This lesson is tagged `durability: perishable` and reviewed quarterly (`next_review: 2026-11`) - treat every specific product name, version, and number below as accurate as of the date above, not as a permanent fact. See `agent-docs/fast-moving-domain-policy.md`.

## The idea
`multi-agent-orchestration/05` deliberately named frameworks only as boxed, swappable examples, because the pattern - who decides what happens next: a pre-drawn graph, a role-negotiating model, or plain code - outlives any one implementation. This lesson inverts that: it is entirely about the implementations, mapped explicitly onto that lesson's three patterns, so a practitioner picking a framework today has a concrete shortlist instead of having to rediscover the landscape from scratch.

2026's headline story is consolidation and specialization rather than proliferation. Two previously independent Microsoft projects (AutoGen and Semantic Kernel) merged into one production SDK in April 2026. Microsoft's original AutoGen effectively entered maintenance mode, and its open-source community forked a successor, AG2, to keep the conversational-agent lineage moving. Meanwhile LangGraph and CrewAI both matured well past their original scope - LangGraph adding durable execution and first-class human-in-the-loop support, CrewAI adding A2A protocol support (see `landscape-snapshot/03`) and enterprise features - while OpenAI's Agents SDK grew out of an experimental project (Swarm) into a production offering with sandboxed execution.

## How it works

### Mapping frameworks to the three durable patterns

| Pattern (from `multi-agent-orchestration/05`) | Framework(s) that most directly implement it (2026) | What distinguishes it |
| --- | --- | --- |
| Graph-based | **LangGraph** (LangChain) | Directed graph of nodes/conditional edges authored ahead of time, checkpointable and inspectable independent of any one run; durable execution and human-in-the-loop are first-class as of 2026. |
| Role-based | **CrewAI** | Agents get a role, goal, backstory, and tool set; run in a designer-specified sequence or under a manager agent that delegates hierarchically at runtime; reached v1.14 with A2A protocol support in 2026. |
| Role-based (conversational variant) | **AG2** (community fork of AutoGen) | Multi-agent conversation loops - agents negotiate, critique, and iteratively refine each other's output (e.g., a Coder agent and a Reviewer agent going back and forth); AG2 introduced event-driven architecture and async message passing after forking from Microsoft's original AutoGen. |
| Deterministic-script / hybrid | **Microsoft Agent Framework** (merged AutoGen + Semantic Kernel, shipped 1.0 April 2026) | Combines AutoGen's simple multi-agent abstractions with Semantic Kernel's enterprise features (session-based state, type safety, filters, telemetry) and adds "workflows" - explicit developer control over multi-agent execution paths, closer to deterministic-script than either predecessor alone. |
| Deterministic-script / hybrid | **OpenAI Agents SDK** | Evolved from the experimental Swarm project into a production SDK with sandboxed execution and a harness system; uses an explicit "handoff" model rather than either a pre-drawn graph or open-ended role negotiation - code decides when a handoff occurs. |
| Deterministic-script (coding-agent-specific) | **Claude Agent SDK** (Anthropic) | Gives simplicity over LangGraph's fine-grained graph control; the "Tool Runner" pattern - orchestrator code calls an agent, the agent calls tools, code decides the next call - is the same deterministic-script idea `multi-agent-orchestration/05` illustrates with production coding-agent tooling. |

### LangGraph: the graph pattern's current reference implementation
LangGraph leads the space on raw adoption as of 2026 - reported at roughly 34.5 million monthly downloads, ~33,900 GitHub stars, and around 400 verified enterprise production deployments. Its core contribution beyond the bare graph-based pattern is durability: graph state can be checkpointed and resumed, and human-in-the-loop interrupts are a first-class primitive rather than something bolted on. Practitioner sources describe it as giving "the most control at the cost of more boilerplate" relative to simpler SDKs - consistent with the graph-based pattern's inherent trade-off (auditability and bounded transitions, paid for in upfront design cost) from `multi-agent-orchestration/05`.

### CrewAI: the role pattern's current reference implementation
CrewAI optimizes for accessibility and rapid iteration - practitioner benchmarks describe a "20 lines to start" learning curve built around its role-based DSL (role, goal, backstory, tools per agent). Reported 2026 adoption: ~5.2 million monthly downloads, 44,000+ GitHub stars, and roughly 60% Fortune 500 adoption cited for business-automation use cases. Its 2026 additions - A2A protocol support (`landscape-snapshot/03`) and enterprise features - extend the role-based pattern's central risk from `multi-agent-orchestration/05` (a manager agent's sequencing decision is a non-reproducible model output) into cross-organization settings, where that non-determinism now also crosses a network boundary.

### AutoGen's split: Microsoft Agent Framework vs. community AG2
This is the framework landscape's most consequential 2026 event and worth tracking closely because it changes which artifact you'd actually adopt under the name "AutoGen":
- **Microsoft Agent Framework** (public preview announced October 2025, RC March 2026, 1.0 shipped April 3, 2026) is the *official* successor to both AutoGen and Semantic Kernel, built by the same teams, for .NET and Python. It folds AutoGen's conversational multi-agent abstractions into Semantic Kernel's enterprise-grade state management, type safety, and telemetry, and adds an explicit workflow layer for controlling multi-agent execution paths.
- **AG2** is the open-source community's continuation of the *original* AutoGen conversational-agent lineage, maintained independently after Microsoft's strategic pivot left the original AutoGen repo without active major feature development. AG2 prioritizes conversational richness and code execution, and introduced event-driven, async message passing as its own direction.

Sources agree Microsoft Agent Framework is the sanctioned enterprise path and AG2 is the community path, but disagree somewhat on how much overlap or migration friction exists between the two for teams currently on pre-merger AutoGen - treat that specific migration question as unsettled as of this writing and worth verifying directly against each project's own docs before committing.

### OpenAI Agents SDK and the handoff model
OpenAI's Agents SDK sits between LangGraph's explicit graph and CrewAI's open-ended role negotiation: it uses a "handoff" primitive where one agent's code explicitly transfers control to another, named agent - a middle point on `multi-agent-orchestration/05`'s "how much of the next-step decision is model vs. human-authored structure" axis. Its evolution from the experimental Swarm project to a production SDK with sandboxed execution mirrors the general 2026 trend of frameworks maturing from research prototypes toward production-hardened tooling.

## Pros
- Consolidation (Microsoft Agent Framework) reduces the number of half-maintained options a team has to evaluate, and community forks (AG2) preserve continuity for teams already invested in a lineage that a vendor deprioritized.
- Every framework above now has some story for cross-agent, cross-vendor communication via A2A (`landscape-snapshot/03`), so a pattern choice at the framework level is increasingly decoupled from an interoperability choice.
- Adoption numbers (downloads, stars, verified production deployments) are unusually well-documented for this space in 2026, making it easier than in prior years to gauge real-world traction versus marketing claims - though these numbers should still be read with the same skepticism `agent-evaluation/02` teaches for benchmark leaderboards.

## Cons
- The AutoGen split (Microsoft Agent Framework vs. AG2) is exactly the kind of naming/governance churn this subject exists to absorb - a lesson written even six months earlier would have described a single, unforked AutoGen.
- Adoption metrics (downloads, GitHub stars) measure popularity, not correctness or fit for a given task - a framework being widely used says nothing about whether its underlying pattern (graph, role, or script) matches your specific control-flow needs, per `multi-agent-orchestration/05`.
- Framework choice is increasingly conflated with model choice and protocol choice (A2A, MCP) in vendor marketing; keeping the three questions - which pattern, which model, which interop protocol - separate takes deliberate effort.

## Alternatives
- **`multi-agent-orchestration/05`'s pattern-first framework alone, with no framework chosen yet** - preferable when you need to decide *whether* your task's next-step decision is enumerable, negotiable, or fixed before picking any tool; that lesson is durable and won't need re-reading when this one goes stale.
- **A hand-rolled orchestration layer over a raw model API** - preferable for teams whose control-flow needs are simple enough that any of the above frameworks would be excess machinery, or whose requirements don't map cleanly onto any one framework's opinions.
- **A workflow/BPM engine with an LLM step embedded**, as `multi-agent-orchestration/05` also lists - preferable when the surrounding process has significant non-AI steps (approvals, external system calls) and agent orchestration isn't the dominant design problem.

## When to use it
Use this lesson to translate a pattern decision already made via `multi-agent-orchestration/05` into a concrete framework shortlist: graph-based points toward LangGraph, role-based toward CrewAI (or AG2 for a more conversational/critique-driven flavor of role negotiation), and deterministic-script/hybrid toward Microsoft Agent Framework's workflow layer, OpenAI's Agents SDK handoffs, or the Claude Agent SDK's Tool Runner pattern.

## When NOT to use it
Do not choose a framework by adoption numbers or brand recognition alone - a widely-used framework implementing the wrong pattern for your task's actual control-flow needs is still the wrong choice, per `multi-agent-orchestration/05`'s non-negotiable that the pattern is not a popularity contest. Do not treat this lesson's framework-to-pattern mapping as permanent; frameworks routinely add support for patterns outside their original design center (e.g., CrewAI adding more deterministic sequencing options, LangGraph adding more dynamic routing), which can blur these categories faster than a quarterly review cycle catches.

## Key takeaways / mental model
Every framework in this lesson is one current implementation of one of three durable patterns from `multi-agent-orchestration/05`. When a new framework appears, or when the AutoGen-style fragmentation happens again to some other project, first ask the pattern question - who decides what happens next - before evaluating the framework on its own terms. The framework names, download counts, and even company ownership (as the AutoGen/Semantic Kernel merger shows) are exactly what `next_review` exists to refresh; the pattern-first question is what to keep asking regardless.

## Self-check questions
1. A team wants to replace an aging AutoGen-based system in late 2026. Name the two paths now available to them and the trade-off between picking the officially-sanctioned successor versus the community fork.
2. Using `multi-agent-orchestration/05`'s axis (how much of "what happens next" is model-decided vs. fixed in advance), place LangGraph, CrewAI, and OpenAI's Agents SDK handoff model in relative order. Justify OpenAI's Agents SDK's position specifically.
3. CrewAI's 2026 addition of A2A protocol support lets crews built in CrewAI talk to agents built in other frameworks. Explain why this is an interoperability-layer addition (`landscape-snapshot/03`) rather than a change to CrewAI's underlying orchestration pattern.
4. Adoption numbers cited here (LangGraph's ~34.5M monthly downloads, CrewAI's ~60% Fortune 500 adoption) are impressive-sounding statistics. What would you want to verify about these numbers before using them to justify a framework choice to your team, drawing on the reading-a-benchmark discipline from `agent-evaluation/02`?

## References
- QubitTool, "2026 AI Agent Framework Showdown: LangGraph vs CrewAI vs AG2 vs Claude SDK vs Strands vs OpenAI" (2026), https://qubittool.com/blog/ai-agent-framework-comparison-2026
- OpenAgents Blog, "CrewAI vs LangGraph vs AutoGen vs OpenAgents - Best AI Agent Framework (2026)" (2026), https://openagents.org/blog/posts/2026-02-23-open-source-ai-agent-frameworks-compared
- techsy.io, "LangGraph vs CrewAI vs OpenAI Agents (Ship Test 2026)" (2026), https://techsy.io/en/blog/langgraph-vs-crewai-vs-openai-agents-sdk
- Microsoft Learn, "Microsoft Agent Framework Overview" (2026), https://learn.microsoft.com/en-us/agent-framework/overview/
- alexbevi.com, "Two Lineages, One Framework: How AutoGen and Semantic Kernel Became the Microsoft Agent Framework" (2026), https://alexbevi.com/blog/2026/06/18/two-lineages-one-framework-how-autogen-and-semantic-kernel-became-the-microsoft-agent-framework/
- jasonmoon.dev, "Microsoft Agent Framework RC: Semantic Kernel and AutoGen Merge into One SDK" (2026), https://jasonmoon.dev/blog/2026-03-10-microsoft-agent-framework-rc-unified
- Medium (Maneesh Kumar), "Microsoft Agent Framework - AutoGen + Semantic Kernel, Finally Merged" (2026), https://medium.com/@maneeshkumar52/microsoft-agent-framework-autogen-semantic-kernel-finally-merged-b9b3f17cf09c
- TrueFoundry, "Best Multi-agent Orchestration Frameworks in 2026" (2026), https://www.truefoundry.com/blog/multi-agent-orchestration-frameworks
- `agentic-engineering/multi-agent-orchestration/lessons/05-orchestration-architecture-patterns.md`, this repository - the durable pattern framework this lesson supplies current examples for
