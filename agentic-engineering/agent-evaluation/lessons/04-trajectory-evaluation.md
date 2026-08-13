---
id: agent-evaluation/04
subject: agent-evaluation
title: "Trajectory Evaluation: Scoring the Path, Not Just the Outcome"
slug: trajectory-evaluation
status: drafted
mastery:
seniority: senior
source: "Anthropic Engineering: Writing effective tools for AI agents (2025-09-11); Confident AI, \"LLM Agent Evaluation Metrics in 2026: Tool Calling, Task Completion, Reasoning, and Trace-Based Evals\" (2026); Langfuse, \"AI agent evaluation: trajectory, tool calls, and task completion\" (2026); Atlan, \"How to Measure Agent Trajectory: The Path, Not the Answer\" (2026)"
durability: durable
prerequisites: [agent-evaluation/03]
created: 2026-08-10
updated: 2026-08-10
---

# Trajectory Evaluation: Scoring the Path, Not Just the Outcome

## TL;DR
Outcome-only evaluation asks one question - did the agent's final answer satisfy the task - and that question systematically misses agents that got the right answer through an unreliable, wasteful, or unsafe path. Trajectory evaluation scores the full sequence of plan-act-observe steps (`tool-use-agentic-loop/03`) an agent took to get there: which tools it called, in what order, with what arguments, and whether each step was actually necessary. A correct outcome from a fragile trajectory is a system that "works until it doesn't," and outcome-only scoring cannot tell you which agents are which.

## The idea
`agent-evaluation/01` introduced the refund-agent example: two trajectories, same final account balance, but one skipped a required eligibility check and only ended up correct because a lucky recovery masked the mistake. `agent-evaluation/03` gave you a way to grade open-ended output quality with a judge. Trajectory evaluation combines both ideas and turns them on the *process*, not just the product: instead of asking a judge "is this final answer good," you ask it (or a programmatic checker) "was every step in this sequence of tool calls and decisions justified, correct, and efficient, given what the agent knew at that point?"

The motivation is production risk, not academic completeness. An agent that reaches a correct outcome via a convoluted, retry-heavy, or precondition-skipping path is more expensive per run (more tool calls, more tokens, more latency), and more fragile under small changes to the task (the same flawed reasoning that happened to recover this time is not guaranteed to recover next time). Shipping an agent whose evaluation only checked outcomes is shipping a system whose actual reliability characteristics you have not measured.

## How it works

### The trajectory as a first-class evaluation object
Recall the loop structure from `tool-use-agentic-loop/03`: PLAN -> ACT -> OBSERVE, repeated, producing a sequence of (plan, tool call, observation) triples until a final answer. That whole sequence - not just the final answer at the end - is the trajectory. Trajectory evaluation treats this sequence as the thing being scored, typically along several distinct dimensions rather than one aggregate pass/fail:

- **Tool correctness** - was each tool call the right tool for that step, with correctly-formed and appropriate arguments?
- **Step efficiency** - were there redundant, repeated, or unnecessary calls that added cost and latency without adding information?
- **Plan adherence / precondition checking** - did the agent verify necessary conditions (permissions, eligibility, current state) before taking consequential actions, rather than acting first and discovering problems after?
- **Safety** - did any step in the trajectory take an irreversible or high-risk action without appropriate justification or a check step first?

### Worked example: two research-agent trajectories, same final answer
Task: "What's our current p99 latency for the checkout API, and has it regressed this week?" Both trajectories below end with the same correct final answer.

```
Trajectory A (4 tool calls)
  1. query_metrics(service="checkout", metric="p99_latency", window="7d")
     -> observation: time series showing a rise from 180ms to 340ms on day 5
  2. query_deploys(service="checkout", window="7d")
     -> observation: a deploy landed on day 5, matching the latency rise
  3. read_diff(deploy_id=<day-5 deploy>)
     -> observation: diff adds a synchronous call to a fraud-check service
  4. final answer: "p99 rose from 180ms to 340ms this week, correlated with
     the day-5 deploy that added a synchronous fraud-check call - likely cause."

Trajectory B (9 tool calls)
  1. query_metrics(service="checkout", metric="p50_latency", window="7d")
     -> observation: p50 looks flat (wrong metric - task asked for p99)
  2. query_metrics(service="checkout", metric="p99_latency", window="7d")
     -> observation: same rise as Trajectory A found on step 1
  3. query_metrics(service="checkout", metric="p99_latency", window="7d")
     -> observation: identical call repeated, no new information
  4. query_logs(service="checkout", window="7d")
     -> observation: large, mostly irrelevant log dump
  5. query_metrics(service="payments", metric="p99_latency", window="7d")
     -> observation: unrelated service, no bearing on the task
  6. query_deploys(service="checkout", window="7d")
     -> observation: same deploy found on day 5
  7. read_diff(deploy_id=<day-5 deploy>)
     -> observation: same fraud-check finding as Trajectory A
  8. query_metrics(service="checkout", metric="p99_latency", window="7d")
     -> observation: re-confirms step 2's finding, adds nothing
  9. final answer: same correct conclusion as Trajectory A
```

Outcome-only scoring calls both trajectories a pass - the final answers are identical and correct. Trajectory scoring does not: Trajectory B wastes a call on the wrong metric (tool correctness), repeats the same p99 query twice more with no new information (step efficiency), and pulls in an unrelated service's data that never gets used (efficiency again). At roughly double the tool calls and a proportional increase in tokens and latency, Trajectory B is a materially worse agent run that happens to land on the same words at the end - exactly the gap `agent-evaluation/01` warned outcome-only checking cannot see.

### Worked example: when the trajectory reveals a real correctness risk, not just waste
Task: "Cancel subscription sub_881 for this customer." Trajectory C: check the customer's account for an active subscription matching that ID, confirm no pending invoice would be forfeited, then cancel. Trajectory D: cancel sub_881 immediately, then (after the fact) look up the customer's account and discover sub_881 belonged to a *different* customer than the one requesting the cancellation - and, because the IDs happened to collide with an already-cancelled subscription, the cancel call was a silent no-op, so the final system state looks unchanged and an outcome check reports "task completed successfully."

This is a sharper case than the efficiency example above: Trajectory D isn't just wasteful, it skipped the precondition check that would have caught a wrong-customer cancellation attempt, and it only avoided causing real damage because of an unrelated coincidence (the ID had already been cancelled). A trajectory-level check that specifically looks for "was ownership/eligibility verified before a destructive action" catches this as a near-miss; an outcome-only check, seeing "subscription sub_881 is cancelled, as requested," reports success and leaves the missing precondition check completely uncaught until it fires on a real, non-coincidental customer account.

### Scoring mechanisms: programmatic checks plus LLM-as-judge on the trace
Some trajectory dimensions are programmatically checkable without a judge at all - counting duplicate tool calls, checking whether a required tool (like a permission check) appears anywhere before a flagged "sensitive" tool, measuring total tool-call count and comparing it against a baseline. Others require judgment - "was this tool call actually justified given what the agent knew at that point" is closer to the open-ended grading problem `agent-evaluation/03` covers, just applied to each step (or the step sequence as a whole) instead of to the final answer alone. Production trajectory-evaluation setups typically combine both: cheap programmatic checks catch the mechanical cases (duplicate calls, missing precondition steps, wrong-tool-for-task), and a judge, calibrated per `agent-evaluation/03` (position-bias-aware, cross-model-family where relevant), handles the more nuanced "was this reasoning path defensible" cases that resist a simple rule.

### What trajectory evaluation cannot tell you on its own
Trajectory evaluation is not a substitute for outcome evaluation - it is a complement to it. A trajectory can look clean, efficient, and well-justified at every step and still arrive at a wrong final answer if, for instance, the agent's interpretation of the task itself was subtly off from the start. The two evaluation layers catch different failure classes: outcome evaluation catches "the agent solved the wrong problem correctly," trajectory evaluation catches "the agent solved the right problem unreliably." A mature evaluation setup runs both and treats a pass as requiring both layers to agree, not either one alone.

## Pros
- Surfaces reliability and safety risk that identical, correct final answers can completely hide - exactly the gap that makes outcome-only evaluation insufficient for agents making consequential, tool-driven decisions.
- Cheaper failure modes (redundant calls, wrong tool selection) are often programmatically detectable without needing a judge at all, making part of trajectory evaluation fast and inexpensive to run continuously.
- Gives you a diagnostic, not just a verdict: a failing trajectory shows you exactly which step went wrong, which is far more actionable for debugging than a failing outcome score with no path information.

## Cons
- More expensive to build and run than outcome-only checking: it requires capturing the full trace (not just the final answer), defining what "justified" looks like per step, and often running an additional judge pass over the trace.
- Judging trajectory steps for "was this justified" inherits the same LLM-as-judge biases covered in `agent-evaluation/03` (position, verbosity, self-preference), now applied at the step level, which can be harder to calibrate than a single end-of-trajectory judgment.
- Overly strict trajectory scoring (penalizing any deviation from one "ideal" path) reintroduces the golden-trajectory brittleness `agent-evaluation/01` warns against - agentic loops are valuable precisely because their path isn't fixed in advance, so trajectory scoring has to grade "was this step defensible," not "did this match one canonical sequence."

## Alternatives
- **Outcome-only evaluation** (`agent-evaluation/01`, `agent-evaluation/02`) - cheaper and simpler, and sufficient when the task genuinely has no meaningful safety, cost, or reliability difference between valid paths; insufficient whenever the path itself carries risk, as both worked examples above show.
- **Golden-trajectory diffing** - compare each run against one recorded "ideal" trajectory step by step; cheaper to implement than judge-based trajectory scoring but brittle for the same reason noted in `agent-evaluation/01` - it penalizes legitimate variation in an agentic loop's path, not just genuine mistakes.
- **Process supervision during training rather than evaluation after the fact** - reward or penalize intermediate steps directly during model training/fine-tuning instead of scoring trajectories post hoc at evaluation time; shifts the mechanism from a testing discipline to a training discipline, and requires a different toolchain and much more infrastructure investment than adding a trajectory-scoring pass to an existing eval pipeline.

## When to use it
Use trajectory evaluation whenever an agent's actions carry cost, risk, or irreversibility beyond producing the final text answer: agents that call paid APIs, modify state (databases, subscriptions, files), or operate with elevated permissions. It's also valuable whenever you're optimizing for efficiency (latency, tool-call cost) and not just correctness, since outcome scoring is blind to waste by construction.

## When NOT to use it
Skip trajectory evaluation, or keep it lightweight, for low-stakes, read-only agents where any reasonable path to the correct answer is equally acceptable and equally cheap - a Q&A agent answering from a small, fast knowledge base has little to gain from step-by-step trajectory scoring beyond what outcome evaluation already tells you, and the added judge cost and calibration burden (per `agent-evaluation/03`) may not be worth it there.

## Key takeaways / mental model
Outcome evaluation asks "did it get there." Trajectory evaluation asks "how did it get there, and was every step along the way justified, efficient, and safe given what the agent knew at that point." The two catch different failure classes and neither substitutes for the other - a trajectory that looks clean can still reach a wrong answer, and an answer that looks right can still hide a trajectory that only worked by luck. Score both, and grade trajectory steps for "defensible," not "matches one fixed golden path," or you reintroduce the brittleness `agent-evaluation/01` already warned against.

## Self-check questions
1. In the metrics-agent worked example, Trajectory B reaches the same correct final answer as Trajectory A but makes roughly twice as many tool calls. Name two distinct trajectory-evaluation dimensions (from the four listed) that Trajectory B fails, and explain why an outcome-only check would miss both.
2. In the subscription-cancellation worked example, what specific check, if added to the trajectory scorer, would have caught Trajectory D's missing precondition step before it became a near-miss? Would this check need an LLM judge, or could it be programmatic?
3. Explain why grading a trajectory against one fixed "golden" sequence of tool calls is a step backward from what makes an agentic loop (`tool-use-agentic-loop/03`) valuable in the first place.
4. A teammate argues "if the outcome is always correct, why would I ever need trajectory evaluation - isn't the outcome what the user actually cares about?" Give a concrete scenario (cost, safety, or reliability) where they are wrong.
5. Which parts of trajectory evaluation can be done with cheap, programmatic checks with no LLM judge involved, and which parts genuinely require judgment? Why does that split matter for the cost of running trajectory evaluation continuously in CI?

## References
- [Anthropic Engineering: Writing effective tools for AI agents](https://www.anthropic.com/engineering/writing-tools-for-agents) (2025-09-11)
- Confident AI, "LLM Agent Evaluation Metrics in 2026: Tool Calling, Task Completion, Reasoning, and Trace-Based Evals" (2026), https://www.confident-ai.com/blog/llm-agent-evaluation-complete-guide
- Langfuse, "AI agent evaluation: trajectory, tool calls, and task completion" (2026), https://langfuse.com/resources/engineering/ai-agent-evaluation
- Atlan, "How to Measure Agent Trajectory: The Path, Not the Answer" (2026), https://atlan.com/know/ai-agent/ai-agent-trajectory-evaluation/
