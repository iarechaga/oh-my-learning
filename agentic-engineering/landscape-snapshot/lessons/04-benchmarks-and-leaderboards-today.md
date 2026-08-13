---
id: landscape-snapshot/04
subject: landscape-snapshot
title: "Benchmarks and Leaderboards in Use Today"
slug: benchmarks-and-leaderboards-today
status: drafted
mastery:
seniority: mid
source: "codeant.ai, SWE-bench Leaderboard 2026 (2026); SiliconReport, OpenAI Abandons SWE-Bench Verified, Citing Widespread Data Contamination and Flawed Tests (2026); morphllm.com, SWE-bench Pro Leaderboard (2026) (2026); buildmvpfast.com, SWE-bench Contamination & AI Coding Leaderboards (2026); benchmarkingagents.com, Tau-Bench 2026: Customer-Service Agent Eval, Methodology, Tiers (2026); sierra-research/tau2-bench, GitHub (accessed Aug 2026); METR, Time Horizon 1.1 (2026); codersera.com, AI Agent Benchmarks 2026: Who Leads SWE-bench & GAIA (2026); iclr-blogposts.github.io, Ready For General Agents? Let's Test It. (ICLR Blogposts 2026)"
durability: perishable
next_review: 2026-11
prerequisites: [agent-evaluation/02]
created: 2026-08-10
updated: 2026-08-10
---

# Benchmarks and Leaderboards in Use Today

## TL;DR
`agent-evaluation/02` teaches that a benchmark score answers "how did this agent do on this specific, possibly-contaminated, possibly-narrow, possibly-saturated task set" - not "is this agent good." As of August 2026, the benchmarks actually in active use are SWE-bench Verified (now openly contested, with OpenAI publicly abandoning it over contamination) and its harder successor SWE-bench Pro, tau²-bench (successor to the original tau-bench, testing tool-agent-user interaction with policy adherence), Terminal-Bench (terminal/shell competence), GAIA and WebArena (general-assistant and web-browsing tasks), and METR's Time Horizon suite (how long a task an agent can complete autonomously) - each with documented, current limitations worth knowing before citing its number.

> **Snapshot date: August 2026.** This lesson is tagged `durability: perishable` and reviewed quarterly (`next_review: 2026-11`) - treat every specific product name, version, and number below as accurate as of the date above, not as a permanent fact. See `agent-docs/fast-moving-domain-policy.md`.

## The idea
`agent-evaluation/02` establishes the three structural blind spots every benchmark can have - contamination, narrow task distribution, and saturation/overfitting - and the discipline for reading a benchmark responsibly (check the task set's provenance, the scoring method's strength, the distribution match to your use case, and the harness used to produce the score). This lesson applies that discipline to the specific benchmarks a practitioner would actually encounter on a leaderboard or in a vendor's marketing claim today, and reports what 2026 audits have found for each one - including, in one case, a benchmark's own creator-adjacent lab publicly walking away from it.

The single most important 2026 development is that the durable lesson's abstract warning about contamination stopped being hypothetical for the field's most-cited benchmark: OpenAI announced it would no longer use SWE-bench Verified for evaluating its coding models, after an internal audit found that frontier models from multiple labs could reproduce verbatim solutions to some tasks, and that 59.4% of a sample of 138 previously-unsolved "hard" problems contained material test flaws. This is the exact failure mode `agent-evaluation/02`'s worked example describes (contamination and weak tests inflating a reported score), now documented at the scale of an entire widely-cited leaderboard rather than one audited benchmark.

## How it works

### Coding-agent benchmarks: SWE-bench Verified and SWE-bench Pro
**SWE-bench Verified** has been the most-cited coding-agent benchmark for several years, built from real-world GitHub issues paired with accepted fixes. As of 2026, it is in an unusual position: still widely reported on leaderboards, but with its most prominent user (OpenAI) publicly stating it will stop relying on it, citing systemic contamination and flawed test cases. This matters beyond OpenAI specifically - if contamination is severe enough that a lab abandons the benchmark for its own model evaluation, scores other labs continue to report on it should be read with the same skepticism.

**SWE-bench Pro**, built by Scale AI in response to these concerns, uses 1,865 multi-language tasks drawn from private codebases that are legally inaccessible to model trainers, structurally preventing the contamination pathway that affected Verified. The practical consequence is a large score gap: models scoring 80%+ on Verified reach only about 46-57% on Pro, which 2026 sources treat as evidence that Verified's high scores substantially reflect contamination and benchmark-specific optimization rather than a matching real capability jump. SWE-bench Pro is not itself free of methodology concerns, however - a cited 2026 audit found its own automated verifier has roughly a 32% error rate, meaning score differences of 2-3 points between models on Pro may not be statistically meaningful, and a separate ICSE 2026 paper found 7.2-8.4% of patches accepted by the original (non-Verified) SWE-bench were functionally incorrect despite being marked as passing.

### Tool-and-user-interaction benchmarks: tau²-bench (successor to tau-bench)
**tau²-bench** is the current version of Sierra's tau-bench line, evaluating agents on tool-use combined with realistic user dialogue across domains (retail and airline customer service are the most-cited). Its distinguishing feature relative to a pure coding benchmark is that it scores policy adherence and multi-turn user interaction, not just a single correct final action. 2026 critiques note two structural limits: it assumes a conversational, user-messaging interaction shape that doesn't transfer to non-conversational agent tasks (making it incompatible, in an agent-agnostic sense, with benchmarks like Terminal-Bench or WebArena), and its two domains (retail, airline) are narrow - strong tau²-bench performance demonstrates competence at retail-and-airline-shaped business workflows specifically, not customer service in general, which is the exact "narrow task distribution" blind spot `agent-evaluation/02` describes in the abstract.

### Terminal/shell benchmarks: Terminal-Bench
**Terminal-Bench** has become the standard benchmark for evaluating agents operating in a terminal environment - directly relevant to the terminal-native execution model from `landscape-snapshot/01`. As the market for evaluation environments has grown in 2026, practitioner guidance flags a task-quality concern specific to this fast-growing category: pressure to ship new tasks quickly, sometimes without thorough adversarial review of the verification logic that decides pass/fail, which is a newer variant of the "weak scoring method" blind spot `agent-evaluation/02` warns about.

### General-assistant and web benchmarks: GAIA and WebArena
**GAIA** evaluates general AI assistants across a broad task mix, and **WebArena** evaluates autonomous agents on realistic, multi-step web-browsing tasks in a self-hosted environment. As of 2026 leaderboard snapshots, top-model scores on GAIA are in the low-to-mid 70s percent range and on WebArena in the mid-to-high 60s percent range, against a WebArena human baseline cited around 78% - meaning the best agents as of this writing are reported as still below typical human performance on WebArena specifically, unlike some narrower coding benchmarks where agents have overtaken human baselines. Sources disagree somewhat on exact current leader and score depending on which evaluation harness (e.g., Princeton HAL vs. a vendor's own reported number) produced the figure - consistent with `agent-evaluation/02`'s point that harness choice alone can move scores by double digits.

### Long-horizon capability: METR's Time Horizon suite
**METR's Time Horizon** benchmark measures something structurally different from the task-completion benchmarks above: not "did the agent get this one task right," but "how long a task, in human-equivalent work time, can this agent complete autonomously at a 50% success rate." The metric has shown a long-running trend of roughly doubling every seven months (with some 2026 data suggesting a temporary acceleration to a 3-4 month doubling period before reportedly slowing back toward the original seven-month rate later in the year), and by early 2026 top models' 50%-success time horizon reached roughly 12 hours. METR's own January 2026 "Time Horizon 1.1" update expanded the task suite (from 170 to 228 tasks, doubling the count of 8-hour-plus tasks from 14 to 31) specifically because the previous suite was saturating at the high end - a direct, self-reported instance of the saturation blind spot `agent-evaluation/02` describes, complete with METR's own caveat that horizon estimates above 16 hours remain unreliable given the current suite's coverage.

### Comparison table

| Benchmark | What it measures | Known 2026 criticism/limitation |
| --- | --- | --- |
| SWE-bench Verified | Real GitHub issue fixes (single-turn) | Contamination severe enough that OpenAI publicly stopped using it; 59.4% of a hard-problem sample had flawed tests |
| SWE-bench Pro | Harder multi-language fixes, private codebases | Contamination-resistant by design, but own verifier has ~32% error rate; small score gaps may be noise |
| tau²-bench | Tool use + realistic multi-turn user dialogue, policy adherence | Conversational framing doesn't generalize to non-dialogue agents; only two domains (retail, airline) |
| Terminal-Bench | Terminal/shell task competence | Rapid task-authoring growth outpacing adversarial review of verification logic |
| GAIA | General AI assistant task breadth | Cross-harness score variance; exact leader disputed depending on evaluation harness |
| WebArena | Multi-step web-browsing tasks | Best agents still reported below the ~78% human baseline as of 2026 snapshots |
| METR Time Horizon | Autonomous task duration (50% success) | Suite itself needed expansion in 2026 due to saturation at the high end; >16h estimates flagged unreliable by METR itself |

## Pros
- 2026's most significant development - a lab publicly abandoning a leaderboard-standard benchmark over contamination - is a rare, unusually clear real-world confirmation of `agent-evaluation/02`'s abstract warning, making it a strong worked example for teaching the durable lesson.
- The emergence of harder, contamination-resistant successors (SWE-bench Pro) alongside the original benchmarks gives practitioners an actual choice between "widely-cited but compromised" and "newer, harder, but with its own unresolved verifier-reliability questions" - a genuine trade-off rather than a simple upgrade.
- METR's Time Horizon metric offers a fundamentally different axis (duration of autonomous work) than pass/fail task benchmarks, giving a second, complementary signal that doesn't share the same contamination pathway as a fixed task-and-answer benchmark.

## Cons
- The benchmark landscape's own reliability is currently in flux at exactly the moment practitioners most need a stable reference - citing "SWE-bench Verified: 80%" in August 2026 carries a different, weaker meaning than the same citation would have carried two years earlier.
- Cross-benchmark comparison remains hard: 2026 critiques note that even basic reporting conventions (what counts as a "pass," how aggregation is done) differ across tau²-bench, Terminal-Bench, and WebArena, so a practitioner cannot simply average scores across benchmarks to get a general capability picture.
- Several of the newer or harder benchmarks (SWE-bench Pro, GAIA cross-harness scores) have documented reliability concerns of their own (verifier error rate, harness-dependent leader) - "harder and newer" does not automatically mean "more trustworthy," which can surprise a reader who assumes the field's contamination problem was simply fixed by shipping SWE-bench Pro.

## Alternatives
- **`agent-evaluation/02`'s reading discipline alone, applied to whatever benchmark is current at the time** - the correct default when this lesson is past its `next_review` date; the four-question checklist (task provenance, scoring strength, distribution match, harness) works regardless of which specific benchmarks are in vogue.
- **A held-out evaluation set built from your own production traffic**, per `agent-evaluation/02`'s alternatives - directly answers "how does this agent do on my actual workload," sidestepping every contamination and narrow-distribution concern above, at the cost of losing cross-team and cross-vendor comparability.
- **Dynamic/continuously-refreshed benchmarks** that regenerate tasks after any given model's training cutoff - specifically designed to defeat the contamination pathway that compromised SWE-bench Verified, at the cost of run-to-run comparability.

## When to use it
Use this lesson when you need to know, right now, which specific benchmark score is worth taking seriously for a given claim: a coding-agent vendor citing SWE-bench Verified should be read more skeptically than one citing SWE-bench Pro (though not uncritically, given Pro's own verifier concerns); a customer-service-agent vendor citing tau²-bench should be understood as validating retail/airline-shaped workflows specifically, not customer service broadly; a claim about how long an agent can work unattended should be checked against METR's Time Horizon methodology and its own stated reliability ceiling.

## When NOT to use it
Do not use this lesson's specific benchmark criticisms as a permanent verdict - benchmark methodology is actively being patched (as METR's own 1.1 suite expansion shows), and a criticism valid in August 2026 may be addressed by `next_review`. Do not substitute any of these benchmarks, however current, for `agent-evaluation/02`'s underlying discipline of reading methodology before trusting a number - the specific benchmarks named here are illustrations of that discipline in action, not a replacement for applying it yourself to whatever benchmark comes next.

## Key takeaways / mental model
Every benchmark in this lesson is a current, specific instance of the general blind spots `agent-evaluation/02` teaches - and 2026 gave the field an unusually concrete, citable case of contamination doing real damage to a leaderboard's credibility (OpenAI's public departure from SWE-bench Verified). When you encounter a benchmark score - whether one of these or a new one that replaces them by the time you read this - ask the same four questions regardless of the benchmark's name: where did the tasks come from, how strong is the pass/fail decision, does the task distribution match your use case, and what harness produced the number.

## Self-check questions
1. A vendor advertises "80% on SWE-bench Verified." Using this lesson and `agent-evaluation/02`, list the specific reasons that number now deserves more scrutiny in August 2026 than it would have two years earlier.
2. SWE-bench Pro is contamination-resistant by design, yet this lesson still flags it as imperfect. What is the specific concern, and why does "harder benchmark" not automatically mean "more trustworthy benchmark"?
3. tau²-bench and Terminal-Bench are both described as incompatible with each other in an "agent-agnostic" sense. Explain what that incompatibility means in practice and why it prevents a practitioner from simply combining scores across the two into one capability picture.
4. METR expanded its Time Horizon task suite in January 2026 specifically because it was saturating at the high end. Connect this concretely to the saturation blind spot from `agent-evaluation/02` - what would have happened to the metric's usefulness if METR had not expanded the suite?
5. Your team is choosing a coding agent and can only check one benchmark score before a decision deadline. Given everything in this lesson, would you pick a SWE-bench Verified score or a SWE-bench Pro score, and what additional single check (from `agent-evaluation/02`'s four-question discipline) would you still insist on before trusting either?

## References
- codeant.ai, "SWE-bench Leaderboard 2026: All Model Scores, Rankings & What They Actually Mean" (2026), https://codeant.ai/blogs/swe-bench-scores
- SiliconReport, "OpenAI Abandons SWE-Bench Verified, Citing Widespread Data Contamination and Flawed Tests" (2026), https://www.siliconreport.com/openai-abandons-swe-bench-verified-citing-widespread-data-contamination-and-flawed-tests-6ebd9b34
- morphllm.com, "SWE-bench Pro Leaderboard (2026): Every Model Score, Benchmarks, and Price per Point" (2026), https://www.morphllm.com/swe-bench-pro
- buildmvpfast.com, "SWE-bench Contamination & AI Coding Leaderboards" (2026), https://www.buildmvpfast.com/blog/benchmark-contamination-ai-coding-leaderboard-swe-bench-2026
- benchmarkingagents.com, "Tau-Bench 2026: Customer-Service Agent Eval, Methodology, Tiers" (2026), https://benchmarkingagents.com/tau-bench/
- sierra-research/tau2-bench, GitHub repository (accessed Aug 2026), https://github.com/sierra-research/tau2-bench
- METR, "Time Horizon 1.1" (2026), https://metr.org/blog/2026-1-29-time-horizon-1-1/
- METR, "Measuring AI Ability to Complete Long Software Tasks" (2025), https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/
- codersera.com, "AI Agent Benchmarks 2026: Who Leads SWE-bench & GAIA" (2026), https://codersera.com/blog/ai-agent-benchmarks-state-of-leaderboard-may-2026/
- ICLR Blogposts 2026, "Ready For General Agents? Let's Test It." (2026), https://iclr-blogposts.github.io/2026/blog/2026/general-agent-evaluation/
- `agentic-engineering/agent-evaluation/lessons/02-what-benchmarks-measure.md`, this repository - the durable benchmark-reading discipline this lesson supplies current examples for
