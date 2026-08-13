---
id: multi-agent-orchestration/03
subject: multi-agent-orchestration
title: "Orchestration Patterns: Deterministic Workflows vs Autonomous Delegation"
slug: orchestration-patterns
status: drafted
mastery:
seniority: senior
source: "Anthropic, Building Effective AI Agents (Dec 2024, updated 2026); Anthropic Engineering, How we built our multi-agent research system (Jun 2025); Zylos Research, Graph-Based Agent Workflow Orchestration in Production: The 2026 Landscape (Apr 2026); Hugging Face, Mengkang Hu, Workflow vs. Agent: a Policy-vs-Script Perspective (2026)"
durability: durable
prerequisites: [multi-agent-orchestration/02]
created: 2026-08-10
updated: 2026-08-10
---

# Orchestration Patterns: Deterministic Workflows vs Autonomous Delegation

## TL;DR
Once you have decided that a task benefits from more than one agent (`multi-agent-orchestration/01`) and how a single delegation boundary works (`multi-agent-orchestration/02`), a second, independent design decision remains: who decides the sequence of agent activity - a developer, fixed in code ahead of time (a **deterministic workflow**), or the agents themselves, at runtime, based on what they observe (**autonomous delegation**)? This is a spectrum, not a binary, and where a given system should sit on it is a genuine senior-level trade-off between predictability and adaptability, not a question with one universally correct answer.

## The idea
`tool-use-agentic-loop/03` already drew this same distinction once, inside a single agent: a fixed pipeline of tool calls versus a genuine agentic loop where each step's plan depends on the last step's observation. This lesson is that identical distinction, one level up, applied to how multiple agents relate to each other rather than how one agent relates to its own tool calls.

At one end of the spectrum, a **deterministic workflow** has its control flow - which agent runs when, in what order, under what branching conditions - fixed by a developer in code before the task ever runs. An LLM may still do real, non-trivial work inside any given step (write this section, classify this ticket, decide which of three known branches to take), but the *graph* of possible paths through the system is fixed in advance; the model chooses a value, not a structure. At the other end, **autonomous delegation** hands that structural decision to the agents themselves: a lead agent decides, at runtime, how many subagents to spawn, what to ask each one, in what order, and how to combine their results, and none of that shape is knowable by reading the code ahead of time - it depends on what the task and the intermediate results turn out to be.

Neither end is "more advanced" than the other, and this is the trap junior-to-mid reasoning about this topic tends to fall into: autonomous delegation is not the sophisticated upgrade to workflows, and workflows are not a training-wheels version of agents. They are different tools solving different shapes of uncertainty, and the actual engineering skill is diagnosing which shape a given task has.

## How it works

### The spectrum, not the binary
Real systems rarely sit at a pure extreme. It is more useful to think of orchestration design as a spectrum with recognizable landmarks:

```
 fully deterministic                                    fully autonomous
 --------------------------------------------------------------------------
 | fixed sequence  | fixed graph with  | fixed roles,      | fully open
 | of steps, LLM   | LLM-chosen        | LLM decides        | delegation:
 | fills in each   | branching at      | sequence and       | agent decides
 | step's content  | specific points   | count within        | whether to
 |                 |                   | that role set       | delegate at all,
 |                 |                   |                     | to whom, how
 --------------------------------------------------------------------------
```

At the leftmost landmark, a workflow always runs "extract data, then classify, then generate report" in that fixed order, with an LLM producing the content at each step but never deciding to skip, reorder, or repeat a step. A step further right, the graph itself branches at runtime based on an LLM's classification ("if the ticket is billing-related, route to the billing-specialist step; otherwise route to general support") - still a fixed, enumerable set of paths, but which path is taken is now a runtime decision. Further right still, a lead agent has a fixed roster of specialist roles it can call on but decides for itself, each run, which ones it needs and in what order - the roles are fixed, the sequence is not. At the rightmost landmark, nothing is fixed at all: an agent decides whether delegation is even warranted, invents its own scope for a subagent's briefing on the fly, and decides when it has gathered enough to stop.

### Worked example: a document-processing pipeline as a deterministic workflow
A company needs to process incoming vendor invoices: extract line items, validate them against a purchase order, and flag discrepancies for human review. The set of steps this needs is completely known in advance and does not change based on the content of any particular invoice - every invoice goes through extraction, then validation, then routing. A developer builds this as a fixed graph: an extraction step (an LLM call, since invoice layouts vary and a rigid parser would break on the first format change), a validation step (a deterministic comparison against the purchase order, no model needed), and a branching step (if discrepancies exist, route to a human-review queue; if not, route to auto-approval). The LLM is doing real, hard work in the extraction step - it has to actually understand an arbitrary invoice layout - but the *shape* of the pipeline is fixed: there is no invoice for which this system would decide, on its own, to add a fourth step or skip validation. This is the right choice specifically because the task's steps are known and stable; wrapping it in autonomous delegation would add unpredictability (will it always validate? will it decide validation is unnecessary for a certain vendor?) for zero benefit, since nothing about this task actually needs a model deciding the *structure*, only the *content* of the extraction step.

### Worked example: an incident-response investigation as autonomous delegation
An agent is asked to investigate why a production service's error rate spiked at 2am. Nobody can specify the sequence of investigative steps in advance, because the right next step depends entirely on what the previous step found: maybe the first check (recent deploys) turns up nothing, so the next check is infrastructure metrics, which reveals a downstream dependency's latency spike, which then requires investigating *that* service's logs, a system nobody had originally scoped as in-bounds. A fixed workflow graph would have to either enumerate every possible investigative branch in advance (impractical - the space of "what could have caused this" is not enumerable) or force the investigation into a rigid order that might waste time checking irrelevant systems before reaching the actual cause. Autonomous delegation - a lead agent that decides, based on each finding, what to check next and whether to delegate a deep investigation of a specific subsystem to a subagent - fits this task's actual shape: uncertain, branching in ways that are only knowable after the fact, exactly the profile `tool-use-agentic-loop/03` identified as needing a genuine loop rather than a fixed pipeline, now applied to which *agent* investigates what rather than which tool call runs next.

### The production-proven middle: a deterministic backbone with agentic steps
The dominant pattern that has emerged in production systems by 2026, according to both Anthropic's own guidance and independent analysis of production deployments, deliberately sits in the middle of the spectrum rather than at either extreme: a deterministic backbone - a fixed graph with defined states, transitions, and terminal conditions - that invokes agentic reasoning (including autonomous subagent delegation) only at specific, intentional steps, with control always returning to the backbone once that step completes. The backbone gives the overall system predictability, testability, and a clear place to add guardrails or human checkpoints; the agentic steps embedded inside it give the system the adaptive judgment that a purely rigid pipeline cannot provide. This is not a compromise born of timidity - it is a recognition that most real tasks are a mix of genuinely-known-in-advance structure (fetch the ticket, look up the customer, log the outcome) and genuinely-uncertain-in-advance judgment (what does this specific ticket actually need), and forcing the whole task to one end of the spectrum handles one half of that mix well and the other half badly.

### Diagnosing where a task belongs
The question to ask, sub-task by sub-task rather than for the whole system at once, mirrors the single-agent diagnostic from `tool-use-agentic-loop/03`: **if you ran this task ten times, would the sequence of steps differ across runs in a way that depends on what earlier steps found?** If the honest answer is "no, it's always the same steps in the same order, just with different content each time," that portion belongs in the deterministic part of the graph, even if an LLM is doing real work inside that step. If the honest answer is "yes, run 3 might need to check something run 7 never needed to," that portion needs autonomous judgment - either a genuine agentic loop within one agent, or, when the discovered work is separable and isolatable (`multi-agent-orchestration/01`, `/02`), autonomous delegation to subagents whose number and scope are not fixed in advance.

## Pros
- **Deterministic workflow**: predictable, testable (you can write a test for "given this input, this exact path is taken"), cheaper to run since there is no open-ended exploration, and easy to add guardrails, logging, or human checkpoints at known points.
- **Autonomous delegation**: adapts to task shapes that cannot be enumerated in advance, and can discover and act on branches nobody anticipated when the system was designed.
- **Deterministic backbone with agentic steps** (the common middle ground): captures most of the predictability of a workflow while still allowing genuine judgment exactly where the task needs it, rather than forcing an all-or-nothing choice.

## Cons
- **Deterministic workflow**: brittle against genuinely novel situations - a case the graph did not anticipate either gets forced through the wrong path or has nowhere to go at all.
- **Autonomous delegation**: unpredictable and hard to test in the traditional sense (the same input can legitimately take a different path on different runs), harder to debug, and - per `multi-agent-orchestration/01` - meaningfully more expensive in tokens and coordination overhead.
- **Deterministic backbone with agentic steps**: requires genuine design skill to draw the boundary correctly; drawing it wrong (too much forced into the rigid backbone, or too much left open to agentic judgment) reproduces the failure mode of whichever extreme you drifted toward.

## Alternatives
- **Single agentic loop, no orchestration layer at all** (`tool-use-agentic-loop/03`) — appropriate when the task does not actually need multiple agents in the first place, per the independence and value tests in `multi-agent-orchestration/01`; not every uncertain task needs multi-agent orchestration, some just need one good loop.
- **Fully manual, human-orchestrated pipeline** — a human decides each step and which agent (if any) handles it, with no autonomous routing at all; appropriate when the cost of a wrong autonomous routing decision is unacceptably high and a human checkpoint on every routing decision is worth the lost speed.
- **Named orchestration frameworks and their specific graph/role abstractions** — the current landscape of concrete tools implementing points along this spectrum is covered in `landscape-snapshot/02`; this lesson is about the durable pattern, not which product's API to use.

## When to use it
Choose the deterministic end of the spectrum for the portions of a task whose steps are genuinely known and stable in advance, want testability, and where the cost of an LLM improvising the wrong structure (not just the wrong content) is unacceptable. Choose the autonomous end for the portions where the right next step depends on information only discoverable by taking earlier steps, and no advance enumeration of the possible paths is practical. Choose a deterministic backbone with embedded agentic steps - the pattern most production systems converge on - when a task is a genuine mix of both, which most non-trivial real-world tasks are.

## When NOT to use it
Do not force a deterministic workflow onto a task whose actual shape is exploratory and branching (per the incident-response example) - you will either miss cases the graph did not anticipate or pay to enumerate an impractically large branch space in advance. Do not reach for autonomous delegation on a task whose steps are actually fixed and known (per the invoice example) - you will pay the token, latency, and unpredictability cost of open-ended agent judgment for a structure that a human could have specified once, correctly, and cheaply.

## Key takeaways / mental model
"Deterministic vs autonomous" is a design axis about who decides the *structure* of multi-agent work, not a maturity ladder - it sits directly on top of the same "would the next step change if the last observation had come back differently" diagnostic that separates a single agentic loop from a fixed pipeline (`tool-use-agentic-loop/03`), now asked about which agent runs next rather than which tool call runs next. The production-tested default for non-trivial systems is not "pick one end," it is a deterministic backbone with defined states and transitions that deliberately invokes agentic (including delegated, multi-agent) judgment only at the specific steps that actually need it, with control always returning to the backbone afterward.

## Self-check questions
1. A team building a customer-support triage system debates whether to let an agent autonomously decide, per ticket, which of several specialist agents to invoke and in what order, versus fixing a graph with LLM-driven branching at specific decision points. Using the diagnostic in this lesson, what question would you ask about their ticket volume and diversity to make this call, and what answer would push you toward each option?
2. Explain why "the LLM is doing significant work inside a step" does not by itself mean the overall system is autonomous rather than a deterministic workflow. What is the actual distinguishing factor?
3. Take the incident-response worked example and describe what a deterministic-backbone-with-agentic-steps version of it might look like - which parts would you fix in the backbone, and which would you leave open to agentic judgment?
4. A senior engineer says "we should always start with the deterministic end and only add autonomy where we're forced to." Steelman this position, then describe a task shape where following it strictly would produce a clearly worse system than starting from the autonomous end.
5. Your team's fixed-workflow ticket router has started misrouting a growing fraction of tickets because the taxonomy of ticket types keeps expanding faster than the graph's branches. What does this observable symptom tell you about where on the spectrum this part of the system now belongs, and what would you change?

## References
- Anthropic, "Building Effective AI Agents" (December 2024, referenced in 2026 practitioner guidance) - https://www.anthropic.com/research/building-effective-agents
- Anthropic Engineering, "How we built our multi-agent research system" (June 2025) - https://www.anthropic.com/engineering/multi-agent-research-system
- Zylos Research, "Graph-Based Agent Workflow Orchestration in Production: The 2026 Landscape" (April 2026) - https://zylos.ai/research/2026-04-14-graph-based-agent-workflow-orchestration-production/
- Mengkang Hu, Hugging Face Blog, "Workflow vs. Agent: a Policy-vs-Script Perspective" (2026) - https://huggingface.co/blog/MengkangHu/workflow-vs-agent
