---
id: tool-use-agentic-loop/08
subject: tool-use-agentic-loop
title: "When to Stop: Termination Conditions and Runaway-Loop Prevention"
slug: when-to-stop
status: drafted
mastery:
seniority: staff
source: "Claude API Docs: How the agent loop works (2026); arXiv:2510.16492 Check Yourself Before You Wreck Yourself - Selectively Quitting Improves LLM Agent Safety (2025); arXiv:2606.28733 Agentic Abstention - Do Agents Know When to Stop Instead of Act? (2026); FutureAGI: What Is Runaway Cost? (2026); Inkog: AI Agent Infinite Loop Detection & Prevention (2026); MatrixTrak: How to Stop AI Agents from Looping Forever - Guardrails & Stop Rules (2026)"
durability: durable
prerequisites: [tool-use-agentic-loop/03, tool-use-agentic-loop/07]
created: 2026-08-10
updated: 2026-08-10
---

# When to Stop: Termination Conditions and Runaway-Loop Prevention

## TL;DR
An agentic loop with no explicit stop condition does not fail gracefully - it fails expensively, either by looping on a task it cannot complete or by declaring success on a task it didn't actually finish. There is no single correct termination mechanism; fixed iteration caps, cost/time budgets, no-progress detection, confidence-based self-assessment, and human checkpoints each catch a different failure and miss others, and staff-level judgment is choosing which combination to compose for a given task's blast radius - not picking one and calling it solved.

## The idea
Lesson 03 described the agentic loop's basic shape: plan, act, observe, repeat, until some notion of "done." That "until done" is where most descriptions of the loop go quiet, and it is exactly the part that matters once an agent runs unsupervised. A loop that keeps calling tools forever is not a theoretical edge case - it is one of the most commonly documented failure modes of production agent systems, and it fails in a way that is uniquely bad compared to a traditional program hanging: every additional iteration is a paid model call, and every iteration that includes a tool call is a chance to do further, real-world damage (another email sent, another retry of a failing write, another API call against a rate-limited or metered service).

The problem is genuinely hard, not merely under-engineered, for a structural reason: an LLM has no reliable internal signal for "I am not making progress" or "I have actually finished." It can be prompted to say "I'm done" and it can be wrong - confidently reporting success on an incomplete task, or continuing to "try one more thing" on a task that was never going to succeed. This is the same probabilistic-versus-deterministic tension from `prompting-context-engineering/06`: asking the model to self-regulate its own stopping point is asking a probabilistic system to enforce a guarantee, and probabilistic self-assessment is not a guarantee. The staff-level skill is recognizing that termination is a *system design problem spanning several independent mechanisms*, each catching a different way the loop can go wrong, and none of them sufficient alone.

## How it works

### The four broad classes of termination mechanism, and what each one actually catches
Mentally sort termination mechanisms by what they check:

1. **Fixed iteration / turn caps.** A hard ceiling on the number of loop iterations (or tool-use turns) regardless of what happened in them. Cheap to implement, trivially auditable, and catches the purely mechanical infinite loop - the agent that keeps calling the same failing tool with the same arguments forever. It does not know or care whether progress is being made; it only counts.
2. **Cost / time budgets.** A ceiling on wall-clock time or cumulative spend (tokens, tool-call cost, dollars), independent of iteration count. This catches the case a turn cap misses: a small number of iterations that are individually expensive (a long-running tool call, a huge context window re-sent every turn) that would blow the budget well before hitting a turn-count ceiling. It also directly targets the actual harm - runaway *cost* - rather than a proxy for it.
3. **No-progress / plateau detection.** Compares the agent's state (its plan, its partial output, the tool results it's getting) across recent iterations, and stops if nothing meaningfully changed - the agent is technically still looping but going in circles, re-reading the same file, re-trying a subtly different phrasing of a query that keeps returning the same empty result. This catches a failure that a turn cap and a budget both miss entirely: a loop that's well within its budget and turn count but is provably not converging.
4. **Explicit stop conditions / verifiable done-checks.** A concrete, checkable definition of "done" set *before* the loop starts (tests pass, a specific file exists with expected content, a structured output validates against a schema) rather than the agent's own narrative judgment that it's finished. This catches the failure the first three miss: an agent that stops *too early*, declaring victory on an incomplete task, or one that would otherwise run productively but has no way to recognize it has already succeeded.

None of these four addresses the same failure as the others. A system that only has a turn cap will still burn its full budget on a plateaued loop that happens to fit inside the cap. A system that only has cost budgets will still let a genuinely stuck agent spend its entire budget doing nothing useful. A system with only no-progress detection can still be fooled by an agent that superficially varies its actions each turn without ever converging. This is why production-grade agent harnesses layer several of these rather than picking one.

### Worked example: composing the layers for a coding agent
Consider an autonomous coding agent tasked with "fix the failing test in `payment.py`." A staff-level termination design might compose:
- **Explicit stop condition (primary "done" signal):** the loop terminates successfully the moment the target test suite passes - a verifiable, automated check, not the agent's self-report of "I believe this is fixed."
- **No-progress detection (catches thrashing):** if three consecutive iterations produce a diff that reverts or duplicates the previous iteration's change (a common signature of an agent flailing between two wrong fixes), stop and escalate rather than continue - re-trying the same two wrong answers indefinitely is not "still trying," it's stuck.
- **Fixed iteration cap (backstop):** a hard ceiling (e.g., 25 tool-use turns) that fires even if no-progress detection has a blind spot, ensuring the loop cannot run indefinitely no matter what.
- **Cost/time budget (independent backstop):** a wall-clock or token ceiling that fires even if the iteration count alone wouldn't have been hit yet - protecting against the case where a small number of turns are individually very expensive.

> **Example (Aug 2026):** the Claude Agent SDK's agent loop exposes both a turn-count ceiling (`max_turns`) and a spend ceiling (`max_budget_usd`); hitting either one ends the loop with an explicit "max turns/budget reached" result rather than letting the loop continue silently - illustrating the turn-cap-plus-cost-budget pairing in a concrete product, though the exact parameter names and defaults are specific to that SDK and not a universal standard.

If the loop is stopped by the no-progress detector or either backstop rather than the explicit stop condition, that is itself a signal worth surfacing distinctly from a clean success - "gave up after N turns without passing tests" is a materially different outcome than "passed tests," and collapsing them into one undifferentiated "loop ended" state throws away information a human reviewing the run needs.

### Worked example: confidence-based stopping, and why it is a signal, not a guarantee
An alternative to hard caps is asking the model to self-report confidence at each step - e.g., produce a structured response with both an action and a 1-5 confidence score, and stop (or escalate to a human) when confidence drops below a threshold, or when the model itself proposes to "quit" rather than continue guessing. Research on this approach (arXiv:2510.16492, "Check Yourself Before You Wreck Yourself") shows that giving an agent an explicit quitting option, calibrated against its own uncertainty, measurably improves safety outcomes compared to an agent that always has to produce *some* action.

The staff-level caveat: confidence-based stopping is a *behavioral* signal, not an *architectural* guarantee. A model's self-reported confidence can be miscalibrated - overconfident on exactly the inputs where it's wrong, which is often correlated with the inputs an adversary or an unusual edge case would produce. Confidence-based stopping is valuable as an additional layer that can catch cases a hard cap misses (stopping *productively early* when the agent genuinely doesn't know what to do next, rather than burning the rest of its budget guessing), but it cannot be the *only* mechanism protecting against runaway cost or runaway damage, for the same reason a prompt cannot be the only enforcement of a hard business rule (`prompting-context-engineering/06`): it is a probabilistic signal, and the backstops that must never fail (a cost ceiling that protects a real budget, a turn cap that protects a rate-limited downstream system) need to be enforced in code the model does not control.

### Worked example: the human-checkpoint trade-off, quantified
A financial-operations agent is authorized to process reimbursement requests. Two termination-adjacent designs:
- **Fully autonomous with a cost budget:** the agent processes requests up to a $10,000/day cumulative budget, then stops. Fast, no human latency, but a single subtly-wrong classification rule can burn the entire daily budget on incorrect reimbursements before anyone notices, because "under budget" is not the same as "correct."
- **Human checkpoint above a per-transaction threshold:** the agent processes any request under $500 autonomously and pauses for explicit human approval above that - a stop condition triggered not by loop exhaustion but by the *stakes* of the specific action about to be taken.

These are not mutually exclusive, and the trade-off is not "autonomy versus safety" in the abstract - it's *latency and human attention cost* traded against *blast radius of an undetected error*. A $10,000/day budget ceiling bounds the worst case at $10,000/day of wrong reimbursements; a $500 per-transaction human gate bounds the worst *single* mistake at $500 regardless of how many requests run, at the cost of a human being in the loop for every transaction above that line. The staff-level call is setting the threshold based on what a single bad decision can cost versus what reviewing every transaction above that line costs in human time - not defaulting to "always ask a human" (which erases the point of automating the task) or "never ask" (which erases the backstop for exactly the class of error that a budget ceiling doesn't catch).

### Why runaway loops are expensive in practice, not just in theory
This isn't a hypothetical worst case. Documented incidents include agent sessions that accumulated tens of thousands of dollars in API spend within hours from a single misbehaving session - typically some combination of a tool call that fails and gets retried identically, or two cooperating agents each waiting on and re-prompting the other in a cycle that never resolves. The common thread in both cases: *every individual step looked locally reasonable* (a retry after a failure is a sensible instinct; responding to another agent's message is a sensible instinct), and the failure was only visible in aggregate - which is exactly the class of failure that per-step reasoning (including the model's own) is bad at catching, and that an external, code-enforced ceiling is good at catching.

## Pros
- **Bounds worst-case cost and damage** to a known, designed-for ceiling instead of an unbounded tail risk.
- **Composability**: layering several mechanisms (cap + budget + no-progress + explicit done-check) closes the gaps any single one leaves open, without requiring any one mechanism to be perfect.
- **Surfaces a distinct, informative failure state** ("stopped without succeeding") instead of forcing every loop exit through the same undifferentiated path as a clean success.
- **Decouples the safety guarantee from model behavior.** Hard caps and budgets enforced in the harness hold even when the model's self-assessment is wrong, miscalibrated, or adversarially manipulated.

## Cons
- **Every hard cap is also a source of premature termination.** A turn cap or budget set too conservatively kills legitimately long-running, valid tasks - there is no cap that is simultaneously always-safe and never-too-restrictive; it has to be tuned per task class, and that tuning is itself an ongoing cost.
- **No-progress detection is heuristic and can be gamed or fooled**, by design: an agent that varies its output superficially between iterations without converging can evade a naive similarity check, and one that occasionally makes tiny genuine progress can trigger a false stop on a plateau detector tuned too aggressively.
- **Confidence-based stopping inherits the model's calibration problems** - it is most likely to fail silently exactly where the model is most confidently wrong, which is not a random or diagnosable subset of cases.
- **Human checkpoints reintroduce the latency and attention cost that autonomy was meant to remove**, and if the threshold is set wrong (too low), the "autonomous" agent becomes a human-gated one in practice, undermining the reason it was built.

## Alternatives
- **Unbounded execution with only downstream monitoring/alerting** - let the loop run and rely on external observability (spend dashboards, anomaly alerts) to catch problems after the fact. Preferable only for fully sandboxed, zero-real-world-side-effect experimentation where cost is the only risk and a delayed alert is an acceptable response time; not appropriate for anything with tool access to production systems.
- **Single fixed iteration cap only** - the simplest possible mechanism, easy to reason about and audit. Preferable for low-stakes, well-scoped tasks where the task is either clearly bounded (a handful of tool calls) or where the cost of over-running slightly is genuinely negligible; insufficient once tasks are open-ended or tool calls carry real-world consequences, per the worked examples above.
- **Full manual (no autonomous loop at all) - human confirms every single step.** Preferable when the operation's stakes are high enough, or so rare, that the overhead of building any of the above mechanisms isn't justified by the volume of work being automated.
- **Reflection-only self-termination (no external caps, model decides when done via internal chain-of-thought review)** - relies entirely on the model reasoning about its own state. Preferable only in low-stakes prototyping where getting a fast signal on model self-assessment quality matters more than production safety; per the confidence-based stopping discussion above, this alone is not a safe default for anything with real consequences.

## When to use it
Every agentic loop that runs with any degree of autonomy - more than a single tool call per human turn, or any tool call with a real-world side effect - needs an explicit termination design, composed from at least a hard backstop (iteration cap or cost/time budget, ideally both) plus a verifiable done-check appropriate to the task. Scale the sophistication (no-progress detection, confidence-based early stopping, tiered human checkpoints) to the blast radius: the more expensive a stuck loop or a wrong "success" declaration would be, the more layers earn their complexity cost.

## When NOT to use it
Do not over-engineer termination for tasks that are inherently single-shot or trivially bounded (a single tool call answering a single question) - a fixed low cap is sufficient and building no-progress detection or confidence-based escalation for a task that structurally cannot loop more than once or twice is wasted design effort. Similarly, don't substitute an elaborate termination system for fixing a root cause that keeps triggering it: if the same task type hits the no-progress detector constantly, that's frequently a sign the task decomposition or tool design (lessons 02-06) is wrong, not that the termination logic needs to be smarter about tolerating the thrashing.

## Key takeaways / mental model
Termination is not one decision, it's several independent questions layered together: has this run too many times (iteration cap)? has this cost too much (budget)? is this actually going anywhere (no-progress detection)? is the task verifiably finished (explicit stop condition)? does this specific action's stakes require a human before it fires (checkpoint)? A model's own belief that it's done, or its own confidence score, is useful evidence for one of these questions - never a substitute for the ones that must hold regardless of what the model believes. Design the backstops first, enforced outside the model's control; layer the smarter, model-informed signals on top once the floor is safe.

## Self-check questions
1. An agent has a max_turns cap of 20 and a cost budget of $5, and it hits neither - it plateaus at turn 8, repeating a nearly identical failed tool call each time, and keeps going until turn 20. Which of the four termination mechanism classes would have caught this earlier, and why didn't the cap or budget catch it?
2. A staff engineer proposes replacing a fixed iteration cap with confidence-based stopping ("let the model decide when to give up") for a customer-support agent that can issue refunds. Argue both for and against this change, and state what you'd want to keep as a backstop regardless of the outcome.
3. For the reimbursement-agent example, the per-transaction human-checkpoint threshold is currently set at $500. Walk through what happens to blast radius and human workload if it's moved to $50, and if it's moved to $5,000. What information would you want before choosing a number, and what tension are you actually trading off?
4. An agent's harness declares a task "done" purely based on the model's final message saying "I've completed the task." Identify which termination mechanism class is missing, and rewrite the stop condition so it doesn't depend on the model's self-report.
5. Two cooperating agents are stuck re-prompting each other indefinitely, each individually "making progress" by responding to the other's latest message. Why would a naive no-progress detector (comparing each agent's own state across its own turns) fail to catch this, and what would you check instead?

## References
- [How the agent loop works - Claude API Docs](https://platform.claude.com/docs/en/agent-sdk/agent-loop)
- arXiv:2510.16492 - Check Yourself Before You Wreck Yourself: Selectively Quitting Improves LLM Agent Safety
- arXiv:2606.28733 - Agentic Abstention: Do Agents Know When to Stop Instead of Act?
- [FutureAGI: What Is Runaway Cost?](https://futureagi.com/glossary/runaway-cost/)
- [Inkog: AI Agent Infinite Loop Detection & Prevention](https://inkog.io/glossary/infinite-loop-ai-agent)
- [MatrixTrak: How to Stop AI Agents from Looping Forever - Guardrails & Stop Rules](https://matrixtrak.com/blog/agents-loop-forever-how-to-stop)
- `agentic-engineering/prompting-context-engineering/lessons/06-limits-of-prompting.md` (probabilistic-versus-deterministic enforcement, referenced for the confidence-based stopping caveat)
- `agentic-engineering/tool-use-agentic-loop/lessons/07-designing-for-recoverable-failure.md` (prerequisite: retry budgets as a related but distinct bounding mechanism)
