---
id: agent-security-and-operations/07
subject: agent-security-and-operations
title: "Failure Modes and Verification: Hallucination, Silent Drift, and Trust Calibration"
slug: failure-modes-and-verification
status: drafted
mastery:
seniority: staff
source: "Anthropic Engineering, \"An update on recent Claude Code quality reports\" (2026-04-23); arXiv:2601.04170 Agent Drift - Quantifying Behavioral Degradation in Multi-Agent LLM Systems Over Extended Interactions (2026-01-07); arXiv:2509.18970 LLM-based Agents Suffer from Hallucinations - A Survey of Taxonomy, Methods, and Directions (2025); arXiv:2601.05214 Internal Representations as Indicators of Hallucinations in Agent Tool Selection (2026); Foundra, \"Your AI Agent Demo Lies. Production Is the Test.\" (2026-07-09); Digital Applied, \"Building an AI Agent Evaluation Pipeline: 2026 Methodology\" (2026)"
durability: durable
prerequisites: [agent-evaluation/04]
created: 2026-08-10
updated: 2026-08-10
---

# Failure Modes and Verification: Hallucination, Silent Drift, and Trust Calibration

## TL;DR
`agent-evaluation/04` scored a trajectory once, before shipping. A deployed agent keeps running after that score is recorded, and three things keep happening that no pre-deployment eval can see: the model produces confidently wrong output (hallucination), the system underneath the agent changes without anyone flipping a "new version" switch (silent drift), and real production traffic stops resembling the eval set it was graded against (distribution shift). Trust calibration for a running system is not "did it pass the eval" - it is a continuous, re-askable question that needs its own live verification machinery, separate from the one-time gate.

## The idea
An evaluation suite answers a yes/no question at a fixed point in time: given this test set, this model, this prompt, and this tool wiring, is the agent good enough to ship? `agent-evaluation/04` extended that question from "is the final answer right" to "was the whole trajectory defensible" - but it is still a snapshot, run against a fixed set of test cases, on a fixed configuration, before deployment.

Production breaks all three of those fixed points. The test set was necessarily a sample of the task space, not the whole thing, so hallucination on inputs the eval never covered is still possible even after a clean pass. The configuration underneath the agent is not actually fixed - model providers ship updates, prompts get tuned, tool schemas change, caching layers get "optimized" - and none of that reliably triggers a re-run of the eval suite that gated the original launch. And the traffic hitting the agent in production is not the eval set; real users ask things the test-case authors didn't anticipate, in proportions the eval never modeled.

The result is a category distinction that staff-level operators have to hold cleanly: evaluation is a pre-deployment gate, verification is a continuous production discipline. An agent that passed its eval yesterday is not thereby verified today. Trust in a deployed system has to be re-earned continuously, with signals that exist specifically because the eval-time signals go stale.

## How it works

### Three distinct failure classes, not one
It's tempting to lump every "the agent got worse" complaint into one bucket, but the three failure classes below have different causes, different detection signals, and different fixes. Conflating them means applying the wrong fix.

**Hallucination** - the model produces plausible-sounding but false content, or calls a tool with plausible-sounding but wrong arguments, independent of any change to the system. A 2025 survey of LLM-agent hallucination (arXiv:2509.18970) taxonomizes this into intrinsic hallucination (contradicting the agent's own retrieved context or prior steps) and extrinsic hallucination (unverifiable claims not grounded in any available source) - both of which show up in agent trajectories as a tool call built on a fabricated precondition, or a final answer citing a fact no tool ever returned. A January 2026 paper (arXiv:2601.05214) shows tool-selection hallucination specifically can be detected in real time by probing the model's internal representations during the same forward pass that produces the tool call, rather than waiting to check the tool's output after the fact - useful because by the time a hallucinated tool call's *result* looks wrong, the call (and any side effect) has often already happened.

**Silent behavioral drift** - the agent's behavior changes because something underneath it changed, without a corresponding change to the eval gate. This is the failure class that pre-deployment evaluation is structurally blind to, because eval-then-ship assumes the thing being evaluated stays the thing running in production.

**Distribution shift** - the agent's behavior didn't change and nothing underneath it changed, but the input distribution moved. An agent tuned and evaluated against a curated test set can be quietly wrong on the long tail of real user requests that test set never sampled. Foundra's July 2026 review of production agent data reports 6,259 deployed agents achieving a 56.6% success rate across 4.5 million real test runs - "barely better than a coin flip" against the much higher pass rates the same agents typically show on their pre-deployment benchmarks - and separate 2026 evaluation-pipeline research cites a roughly 37% gap between lab benchmark scores and real-world deployment performance for enterprise agents. Both numbers describe the same mechanism: a benchmark distribution is not a production distribution, and a system graded against the former is not thereby graded against the latter.

### Worked example: a real silent-drift incident, dissected
In April 2026, Anthropic published a public postmortem after roughly six weeks of user reports that Claude Code's output quality had degraded. The postmortem traced the degradation to three overlapping *product-layer* changes, explicitly not a change to the underlying model weights:

1. On March 4, the default reasoning effort for Claude Code was switched from high to medium, to reduce a UI issue where the interface appeared frozen during long thinking periods.
2. On March 26, an optimization meant to clear stale thinking sections from sessions idle over an hour shipped with a bug that cleared them on every turn for the rest of a session instead.
3. On April 16, a new system-prompt verbosity cap shipped alongside a model update.

None of these three changes touched the model itself, and none of them individually looked like the kind of change that would trigger a "re-run the eval suite" reflex - a UI latency fix, a caching optimization, a prompt tweak. Each was reasonable in isolation. The combined effect was six weeks of degraded output that users could feel and articulate as "Claude got worse," while every artifact anyone might have checked (the model card, the API version, the weights) said nothing had changed. This is silent drift in its purest form: the failure is real, the trigger is a product-layer or prompt-layer change rather than a model swap, and the standard "did the model change" question that most teams ask first produces a reassuring but wrong "no."

The generalizable lesson for anyone operating an agent built on a third-party model: your effective system includes every layer between the raw model and the user - reasoning-effort settings, system prompts, tool schemas, caching behavior, context-window management - and a change to any of those layers can silently move behavior just as much as a model weight update would, while being far less likely to trip a "this needs re-evaluation" alarm.

### Worked example: quantifying drift instead of just noticing it
A January 2026 paper (arXiv:2601.04170) proposes the Agent Stability Index (ASI), a composite metric across twelve dimensions grouped into four weighted categories: response consistency (0.30 - output semantic similarity, decision-pathway stability, confidence calibration), tool usage patterns (0.25 - tool selection, sequencing, parameterization stability), inter-agent coordination (0.25 - consensus agreement rate, handoff efficiency, role adherence), and behavioral boundaries (0.20 - output length stability, error-pattern emergence, human-intervention rate). Across roughly 800 simulated multi-agent workflows, the paper reports a 42% drop in task success and a 3.2x increase in required human interventions as drift accumulated over extended interaction sequences, with mitigation strategies (episodic memory consolidation, drift-aware routing, adaptive behavioral anchoring) reducing that drift by over 80% in the mission-critical workflows tested.

The point of a metric like this is not the specific twelve dimensions - it's the shift from "someone noticed the agent seems worse" (which is what happened for six weeks before Anthropic's postmortem shipped) to a number you can graph, alert on, and correlate against known change events (a deploy, a prompt edit, a provider model bump). Silent drift stays silent for exactly as long as nobody is measuring a stability signal continuously; the moment something is graphed continuously, drift becomes a visible line instead of a diffuse, hard-to-substantiate user complaint.

### Trust calibration for a deployed system is a different question than trust calibration for one eval run
`agent-evaluation/04` calibrates trust once, against a judge, before ship: "given this trajectory on this test case, was every step defensible?" Production trust calibration asks a structurally different, continuously-repeated question: "given everything happening right now - this specific request, this specific trajectory, the current drift signal, the current distribution of inputs - how much should this particular action be trusted to run autonomously?"

That reframing has two consequences. First, the unit of trust shrinks from "the agent, in general" to "this action, right now" - which is exactly why `agent-security-and-operations/04`'s human-in-the-loop gates key off the stakes of the specific action rather than a blanket trust level for the whole agent. Second, the verification machinery has to run continuously rather than once: live trajectory sampling with the same dimensions `agent-evaluation/04` used pre-deployment, but applied to a rolling sample of real production runs rather than a fixed eval set; a stability metric (ASI-style or simpler) tracked over time and alerted on; and staged rollout (canary or shadow deployment) whenever anything in the effective system changes - model version, prompt, tool schema, or a "harmless" product-layer setting like the reasoning-effort toggle in the worked example above - precisely because the Claude Code incident shows that a change not touching the model can still be the thing that breaks trust.

### What verification catches that evaluation cannot, and vice versa
Pre-deployment evaluation is cheap to run exhaustively (you control the test set) and catches issues before any real user is exposed to them - it is the only layer that can stop a badly broken agent from shipping at all. Production verification is the only layer that can catch drift introduced after ship, hallucination on inputs the eval set never sampled, and distribution shift as real usage evolves. Neither substitutes for the other, for the same structural reason `agent-evaluation/04` gives for why outcome and trajectory evaluation are complements rather than alternatives: they catch different failure classes, and a system that only has one of the two has an entire class of failure it cannot see.

## Pros
- Separating hallucination, drift, and distribution shift into distinct failure classes means the fix matches the actual cause (a grounding/verification check for hallucination; a stability metric and change-gated rollout for drift; broader eval-set sampling or live trajectory review for distribution shift) instead of a generic "the agent seems worse" response that treats all three the same.
- Continuous production verification catches exactly the failures a one-time pre-deployment eval is structurally blind to - most concretely, changes to the system that don't look like "a new model" but change behavior anyway.
- A quantified stability signal (ASI-style or simpler) converts "users are complaining the agent feels off" from an anecdote into a graphable, alertable metric with a timeline that can be correlated against deploys.

## Cons
- Continuous verification is materially more infrastructure than a pre-deployment eval suite: it needs live trace capture, a rolling judge or programmatic check running against real (not curated) traffic, and a dashboard someone actually watches - all recurring cost, not a one-time investment.
- Drift detection has a lag by construction: a metric built on "compare current behavior to a recent baseline" cannot flag drift before enough post-change data accumulates to diverge from that baseline, so there is always some window between a change landing and drift becoming visible - the Claude Code incident's six weeks is the realistic scale of that window without continuous monitoring, not the floor with it.
- Hallucination-detection techniques that probe internal model representations (as in arXiv:2601.05214) are provider- and architecture-specific, and unavailable at all when the agent runs against a model behind an API that doesn't expose those internals - which is the common case for most teams building on a hosted model rather than a self-hosted one.

## Alternatives
- **Eval-only, no production verification** - run the pre-deployment eval suite, ship, and treat the eval pass as an ongoing guarantee. Cheaper, but per the worked examples above, structurally blind to drift and to the eval-set-versus-production-traffic gap; only defensible for low-stakes agents where a stale eval result causing a wrong action has negligible cost.
- **User-report-driven detection ("wait for complaints")** - the actual path the Claude Code incident took before the postmortem: quality degraded for weeks before enough user reports triggered an investigation. Costs nothing to build, but the cost is paid in the incident's blast radius and duration; a continuous stability signal exists specifically to shrink that window.
- **Full re-evaluation on every change** - re-run the entire eval suite before shipping any change to model, prompt, or tool schema, treating every change as equivalent to a new launch. More rigorous than nothing, but doesn't catch changes nobody thought to gate (a UI latency fix that happens to touch reasoning effort, a caching "optimization") - which is exactly the category the Claude Code postmortem's three causes fall into. Continuous production monitoring exists as a backstop for precisely the changes that don't get flagged as eval-worthy in advance.

## When to use it
Build continuous production verification (drift monitoring, rolling trajectory sampling, staged rollout on any change to the effective system) for any agent whose actions carry real cost, whose usage volume or diversity will exceed what a pre-deployment eval set can represent, or that depends on a third-party model provider who can change behavior underneath you without notice. The more autonomous the agent and the further its input distribution is from something a small curated test set can capture, the more this shifts from "nice to have" to load-bearing.

## When NOT to use it
Skip the full continuous-verification build-out for a narrow, low-volume, low-stakes agent where a stale eval result causing an occasional wrong action is genuinely cheap to absorb, and where the team lacks the observability investment (`agent-security-and-operations/06`) to make live monitoring meaningful anyway - a stability dashboard nobody watches is not verification, it's decoration. In that case, a periodic (not continuous) re-run of the eval suite on a fixed cadence is a reasonable, cheaper middle ground.

## Key takeaways / mental model
Evaluation answers "was this good enough to ship," asked once, before anyone real is exposed. Verification answers "is this still good enough right now," asked continuously, after real exposure has started - and it has to be asked continuously because the model, the prompt, the tools, and the traffic hitting the agent are all capable of changing without tripping the alarm that would normally trigger a re-eval. Hallucination, silent drift, and distribution shift are three different failure classes with three different fixes; the Claude Code postmortem is the concrete reminder that "drift" doesn't require a model swap - a reasoning-effort toggle, a caching bug, and a verbosity cap were enough, in combination, to degrade output for six weeks with nothing in the model card ever changing.

## Self-check questions
1. An agent's eval suite passed cleanly last quarter and nothing about the model version has changed since. A user reports the agent "feels off." Using the three failure classes in this lesson, list two changes that could explain the complaint without any model weights changing, and explain how you'd distinguish between them.
2. Why does the Claude Code postmortem count as "silent drift" rather than simply "a bug," given that all three root causes were known, deliberate product changes at the time they shipped? What made the drift silent despite the causes being individually documented?
3. `agent-evaluation/04` scores a trajectory once, pre-deployment, against a fixed test set. Explain concretely why a clean trajectory-evaluation pass last month does not imply the same agent is still trustworthy on today's production traffic - name at least one mechanism from each of the three failure classes in this lesson.
4. A teammate proposes: "let's just re-run the full eval suite every time we deploy any change, and skip building continuous production monitoring." Using the Claude Code worked example, identify a category of change this proposal would miss, and explain why.
5. The Agent Stability Index example reports a 3.2x increase in human interventions as drift accumulated. Why is "human interventions increased" itself a useful drift signal, distinct from the accuracy-based dimensions in the same framework?

## References
- Anthropic Engineering, ["An update on recent Claude Code quality reports"](https://www.anthropic.com/engineering/april-23-postmortem) (2026-04-23)
- arXiv:2601.04170 - Agent Drift: Quantifying Behavioral Degradation in Multi-Agent LLM Systems Over Extended Interactions (2026-01-07)
- arXiv:2509.18970 - LLM-based Agents Suffer from Hallucinations: A Survey of Taxonomy, Methods, and Directions (2025)
- arXiv:2601.05214 - Internal Representations as Indicators of Hallucinations in Agent Tool Selection (2026)
- Foundra, ["Your AI Agent Demo Lies. Production Is the Test."](https://www.foundra.ai/key-reads/ai-agent-production-reliability-testing-2026) (2026-07-09)
- Digital Applied, ["Building an AI Agent Evaluation Pipeline: 2026 Methodology"](https://www.digitalapplied.com/blog/ai-agent-evaluation-pipeline-2026-testing-methodology) (2026)
- `agentic-engineering/agent-evaluation/lessons/04-trajectory-evaluation.md` (prerequisite: trajectory scoring extended here from a pre-deployment gate into a continuous production discipline)
