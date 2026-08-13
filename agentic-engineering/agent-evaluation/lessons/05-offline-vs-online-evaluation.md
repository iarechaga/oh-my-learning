---
id: agent-evaluation/05
subject: agent-evaluation
title: "Offline vs Online Evaluation: What Runs Before Ship vs in Production"
slug: offline-vs-online-evaluation
status: drafted
mastery:
seniority: senior
source: "qaskills.sh: Offline vs Online LLM Evaluation - When to Use Each (2026); Lyzr: Online vs Offline Evaluation in AI - 2026 Enterprise Guide; TrueFoundry: Online LLM Evaluation - Quality Monitoring at the Gateway (2026); MLflow: What Is Online Evaluation in ML - A 2026 Guide; Galileo: 10 Best Low-Latency LLM Evaluation Tools in 2026; arXiv:2411.13768 Evaluation-Driven Development and Operations of LLM Agents - A Process Model and Reference Architecture (2024/2025)"
durability: durable
prerequisites: [agent-evaluation/04]
created: 2026-08-10
updated: 2026-08-10
---

# Offline vs Online Evaluation: What Runs Before Ship vs in Production

## TL;DR
Offline evaluation runs a fixed, curated test set against a candidate change before it ships, with no latency budget and full access to ground truth; online evaluation scores a sample of live traffic after it ships, under a tight latency and cost budget and usually without ground truth. Neither one is optional and neither can substitute for the other: offline tells you whether a change is safe to ship, online tells you whether what you shipped is still working against inputs and drift no test set anticipated.

## The idea
Lesson 04 established that a trajectory can be scored on the path it took, not just its final answer. That scoring machinery has to run somewhere, and *where* it runs is a second, mostly independent design axis from *what* it scores. A trajectory judge, a tool-call correctness check, or a groundedness rubric can all be plugged into either an offline test-set run or an online production-sampling pipeline - the metric doesn't change, but the constraints around it change completely.

Offline evaluation is the direct descendant of a regression test suite: a known set of inputs, run against a candidate build, compared to a baseline, before anything reaches a user. It answers "did this change make things worse on the cases we already understand." Online evaluation is closer to production monitoring: a sample of what real users actually sent, scored after the fact (or async, off the request path), against inputs nobody wrote down in advance. It answers a different question - "is the thing we shipped still behaving, on the traffic we're actually getting now."

The reason both are needed rather than one being "the real one": an offline suite is bounded by the imagination of whoever wrote it. It cannot contain the multi-turn conversation that drifts in a way no one scripted, the adversarial input a user tries on day 40, the upstream API that started returning a slightly different error format last Tuesday, or the slow degradation that only shows up in aggregate over a week of traffic. Online evaluation is the only mechanism that sees the actual distribution of inputs a system faces. But it cannot replace offline evaluation either, because it has no reliable ground truth (nobody hand-labeled the correct answer to a live user's query in real time) and it runs under a latency and cost budget that rules out the expensive, thorough scoring an offline suite can afford to run overnight.

## How it works

### The two pipelines, side by side
| Dimension | Offline evaluation | Online evaluation |
| --- | --- | --- |
| When it runs | Pre-ship: CI, pre-release gate | Post-ship: on live production traffic |
| Input source | Curated, fixed test set | Real user traffic, sampled |
| Ground truth | Usually available (labeled expected outcomes) | Usually absent; reference-free proxies instead |
| Latency budget | None - can run overnight | Tight - must not sit on the user-facing request path |
| Cost budget | Generous relative to a single release | Must not rival inference cost at scale; forces sampling |
| Coverage | Everything the test-writer anticipated | Whatever the live distribution actually contains |
| Typical metrics | Exact/semantic match, task success rate, LLM-judge with rubric and reference answer | Reference-free LLM-judge rubrics, user signals (retries, thumbs-down, abandonment), heuristic guardrails (PII, safety), operational metrics (latency, error rate) |
| Failure mode if skipped | Ships a regression nobody caught before users hit it | Blind to drift, long-tail inputs, and slow degradation between releases |

### Worked example: offline gating a prompt change
A team changes the system prompt of a support agent to be "more concise." Before shipping, they run the offline suite: 200 golden cases stratified across intents, each scored on a groundedness rubric and a task-completion check against a known expected outcome. The gate is a floor threshold - e.g. mean groundedness must stay at or above 0.92, matching the pre-change baseline - plus a paired-comparison check per case (old prompt vs new prompt on the identical input) rather than comparing two independently-noisy aggregate scores. This offline run costs a few CPU-minutes to a few dollars of judge-model calls, has zero latency constraint (it runs in CI, not in front of a user), and catches the concise rewrite that also silently dropped a required disclaimer on 12 of the 200 cases - a regression an online sample might not surface for days, if the disclaimer-dropping cases happen to be rare in live traffic that week.

### Worked example: online sampling in production
The same agent, now shipped, faces live traffic the offline suite never saw: a user asking in a regional dialect, a user chaining three unrelated requests in one turn, a backend API that started timing out intermittently. Running the full offline-grade judge on every one of these in real time is both too slow (an LLM-judge call can add 1000ms+, unacceptable on a user-facing path) and too expensive (scoring 100% of traffic with a frontier-tier judge can cost more than the inference generating the answers in the first place). The practical pattern: score asynchronously, off the request path, after the user already has their response, and sample rather than score everything - typically 1-10% of traces, with the exact rate set by traffic volume (high-traffic systems can sample as low as 1% and still get statistically useful counts; lower-traffic systems need a higher rate to accumulate enough samples), plus 100% of traces already flagged by cheap heuristic guardrails (PII detectors, safety classifiers) or by low-confidence signals from the agent itself. A fast heuristic gate (sub-200ms) runs on everything; a slower, more expensive judge runs only on the sample and the flagged subset.

### Worked example: the ground-truth problem, concretely
Offline evaluation on the support agent knows the "correct" resolution for each of its 200 golden cases because a human wrote it down when building the suite. Online evaluation has no such label for live traffic - nobody pre-wrote the correct answer to the actual question a real user asked ten seconds ago. This forces online metrics to be reference-free: an LLM-judge scoring the response against a rubric ("did this response address the user's stated request, without inventing information") rather than against a known-correct answer, combined with behavioral proxies that correlate with quality without requiring ground truth - did the user retry the request, did they escalate to a human, did they give a thumbs-down, did the conversation end in fewer or more turns than the historical median for this intent. None of these proxies is as precise as a labeled offline score; they are what's available at production scale and speed, and they're treated as trend signals with uncertainty rather than as a verdict on any single interaction.

### The hybrid loop that connects them
The two pipelines are not independent forever - the practice that keeps offline evaluation from going stale is a feedback loop: production failures caught by online evaluation (a flagged trace, a user-reported bad response, a guardrail trip) get triaged, labeled with the correct expected behavior, and promoted into the offline golden set. The next release is now gated against the exact failure that slipped through last time. Skip this loop and the two systems drift apart - the offline suite keeps testing an increasingly outdated slice of behavior while online evaluation keeps rediscovering the same class of failure release after release, because nothing closes the loop back into the pre-ship gate.

## Pros
- **Offline**: reproducible, cheap relative to production risk, catches known regressions before any user is affected, and can afford ground truth and expensive judges because there's no latency pressure.
- **Online**: the only view of the actual live input distribution, catches drift and long-tail failures no test-writer anticipated, and directly measures what's happening to real users right now rather than a proxy population.
- **Together**: they close a loop - online findings become tomorrow's offline test cases, so the safety net widens release over release instead of staying static.

## Cons
- **Offline**: bounded by the imagination and effort of whoever wrote the test set; a suite that never gets refreshed with real failures gives false confidence while drift accumulates invisibly underneath it.
- **Online**: sampling means most individual production failures are simply never scored at all (a bad response outside the 1-10% sample, and not flagged by a guardrail, is invisible); reference-free proxies are noisier and less precise than labeled offline metrics; latency and cost constraints rule out the most thorough judges for anything but the flagged subset.
- **Both**: neither pipeline alone tells the full story, and running both is real infrastructure - a labeled golden set that needs maintenance, plus an async scoring pipeline, sampling logic, and a triage process to promote findings between them.

## Alternatives
- **Offline only, no production monitoring** - cheaper to build, but blind to everything that happens after ship; acceptable only for low-stakes, low-traffic, or short-lived systems where the cost of an undetected production regression is genuinely negligible.
- **Online only, no pre-ship gate** - "ship and watch" catches regressions only after real users have already been affected by them, and forgoes the one setting where expensive, ground-truth-backed evaluation is affordable; defensible only for very low-blast-radius experiments.
- **Shadow/canary evaluation** - run the new version alongside the old one on a slice of live traffic before fully shipping, scoring both with the same online pipeline and comparing. A middle position between offline and full-online: sees real traffic like online evaluation, but gates the release like offline evaluation, at the cost of needing traffic-splitting infrastructure.

## When to use it
Run offline evaluation as a release gate on every change that can alter agent behavior - prompt edits, tool changes, model swaps, config changes - before it reaches users; it is the cheapest point to catch a known-shape regression. Run online evaluation continuously on every production system with real users, sampled to fit its latency and cost budget, specifically to catch what the offline suite structurally cannot see. Use both together for anything with meaningful blast radius, and route every production failure the online pipeline surfaces back into the offline golden set.

## When NOT to use it
Do not build a full online sampling pipeline for a system with negligible traffic or blast radius where offline gating alone already covers the realistic risk - the async infrastructure, sampling logic, and triage process are real ongoing cost that needs traffic volume to justify it. Do not treat an offline pass as clearance to skip online monitoring on anything user-facing; a green offline suite says nothing about the live input distribution it was never exposed to. And do not run an expensive, ground-truth-style judge on 100% of production traffic as a shortcut to "more thorough" online evaluation - at scale that cost can exceed the inference cost of the system being evaluated, for marginal gain over a well-chosen sample plus guardrail-triggered full coverage.

## Key takeaways / mental model
Offline answers "is this change safe to ship" using a fixed, labeled test set with no time or cost pressure. Online answers "is what we shipped still working" using a sampled slice of real traffic under a tight latency and cost budget, without reliable ground truth. They test different things by construction, not by choice, and the loop that keeps them both useful is mundane: every real production failure the online pipeline finds should become a new offline test case, so the pre-ship gate keeps getting sharper instead of staying frozen at whatever the test-writer thought of on day one.

## Self-check questions
1. A team ships a prompt change after it passes the full offline suite at 0.94 mean groundedness (above the 0.92 gate). Two weeks later, online monitoring flags a cluster of low-confidence responses on a phrasing of the request the offline suite never included. Was the offline gate wrong to pass this change? What should happen next?
2. Why can't online evaluation simply run the same ground-truth-based metrics offline evaluation uses, just on live traffic instead of a fixed set?
3. A system has 50,000 requests/day. Explain why scoring 100% of them with a frontier-tier LLM judge is a bad default, and propose a concrete sampling and gating scheme (rates, what triggers full coverage) that still catches high-risk cases.
4. Describe the loop that should exist between an online evaluation finding and the offline test suite. What breaks if that loop doesn't exist?
5. For a low-traffic internal tool used by five people, argue whether a full online sampling pipeline is worth building, and what you'd do instead.

## References
- [Offline vs Online LLM Evaluation: When to Use Each (2026) - qaskills.sh](https://qaskills.sh/blog/offline-vs-online-llm-evaluation-2026)
- [Online vs Offline Evaluation in AI: 2026 Enterprise Guide - Lyzr](https://www.lyzr.ai/blog/online-vs-offline-ai-evaluation/)
- [Online LLM Evaluation: Quality Monitoring at the Gateway - TrueFoundry](https://www.truefoundry.com/blog/online-llm-evaluation-gateway)
- [What Is Online Evaluation in ML: A 2026 Guide - MLflow](https://mlflow.org/articles/what-is-online-evaluation-in-ml-a-2026-guide/)
- [10 Best Low-Latency LLM Evaluation Tools in 2026 - Galileo](https://galileo.ai/blog/best-low-latency-llm-evaluation-tools)
- arXiv:2411.13768 - Evaluation-Driven Development and Operations of LLM Agents: A Process Model and Reference Architecture
- `agentic-engineering/agent-evaluation/lessons/04-trajectory-evaluation.md` (prerequisite: the metrics this lesson's two pipelines both consume)
