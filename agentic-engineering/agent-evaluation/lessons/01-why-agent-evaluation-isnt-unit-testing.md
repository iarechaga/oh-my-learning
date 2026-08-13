---
id: agent-evaluation/01
subject: agent-evaluation
title: "Why Agent Evaluation Isn't Unit Testing: Non-Determinism and Trajectories"
slug: why-agent-evaluation-isnt-unit-testing
status: drafted
mastery:
seniority: mid
source: "Anthropic Engineering: Writing effective tools for AI agents (2025-09-11); Datagrid: 4 Testing Frameworks for AI Agents When Traditional QA Fails (2026); Netguru: Testing AI Agents - Why Unit Tests Aren't Enough (2026); SitePoint: Testing AI Agents - Validating Non-Deterministic Behavior (2026)"
durability: durable
prerequisites: [tool-use-agentic-loop/03]
created: 2026-08-10
updated: 2026-08-10
---

# Why Agent Evaluation Isn't Unit Testing: Non-Determinism and Trajectories

## TL;DR
A unit test rests on `assert(f(x) == y)`: one input, one correct output, checked by exact comparison. An agentic loop (`tool-use-agentic-loop/03`) breaks every leg of that contract at once - the same input can legitimately produce different, equally correct outputs (non-determinism), there is often no single correct output to assert against (open-ended tasks), and correctness depends on the multi-step path the agent took, not just what it said at the end (trajectories). Agent evaluation is a different discipline built to cope with all three, not a stricter version of unit testing.

## The idea
Traditional software testing works because the system under test is (mostly) a pure function of its inputs. Call `discount(price=100, code="SAVE10")` a thousand times and you get `90` a thousand times; if it ever returns `91`, that is unambiguously a bug. This is what makes `assert_equal(actual, expected)` a sufficient testing primitive for most of software engineering: correctness is binary, and the same input reproduces the same output, so one test run generalizes to all future runs of the same input.

An LLM-driven agent violates both halves of that assumption. First, token generation is sampled, not computed - even at the same temperature and the same prompt, the model can emit a different sequence of tokens on different calls, which can mean a different tool gets picked, a different argument gets passed, or a differently-worded (but equally correct) final answer gets produced. Second, and more fundamentally, many agent tasks do not have one correct output to sample toward in the first place: "research this topic and summarize the tradeoffs" has many valid summaries, not one golden string. Third, an agent operating through the plan-act-observe loop (`tool-use-agentic-loop/03`) accumulates a *trajectory* - a sequence of tool calls, observations, and intermediate decisions - and that trajectory itself carries information about reliability that the final answer alone hides. Two agents can land on the identical final answer while one got there by reading the right file once and the other got there by guessing, failing, retrying, and guessing again until something worked. `assert_equal` on the final string cannot tell these apart, and the second agent is a production risk the first is not.

None of this means agents are untestable. It means the testing *primitive* has to change: from "does output equal expected value" to "is this output, and the path that produced it, an acceptable answer to an open-ended question" - a judgment call, not a comparison.

## How it works

### The assert-equal contract, and where it actually still holds
Not every part of an agent is non-deterministic. The plan-act-observe loop from `tool-use-agentic-loop/03` has a deterministic layer underneath the model's judgment calls: the code that parses a tool-call request into a function invocation, the code that validates arguments against a schema, the code that routes a parsed request to the right handler, the code that formats a tool's raw result back into the model's context. None of that code samples tokens - it is ordinary software, and ordinary unit tests are still the right tool for it. The mistake is not "unit tests are useless for agents"; it is assuming they cover the part of the system that actually decides what the agent does, which they do not.

```
[ User request ]
      |
      v
[ Model: PLAN - samples tokens, non-deterministic ]  <- unit tests can't cover this
      |
      v
[ Code: parse tool call, validate args, route ]      <- unit tests DO cover this
      |
      v
[ Tool executes; Code: format result into context ]  <- unit tests DO cover this
      |
      v
[ Model: PLAN again, conditioned on new context ]     <- unit tests can't cover this
      |
     ...
```

### Break #1: non-determinism defeats exact-match assertions
Consider an agent asked "what's a reasonable retry policy for this HTTP client?" Run it three times at the same (nonzero) temperature and you might get: "exponential backoff starting at 100ms, capped at 5 retries," "retry up to 5 times with exponential backoff from 100ms," and "use exponential backoff (base 100ms, max 5 attempts)." All three are the same correct answer, worded differently - `assert_equal(actual, "exponential backoff starting at 100ms, capped at 5 retries")` fails on two of three runs despite the agent being right every time. Lowering temperature to 0 narrows but does not eliminate this: many production agents call tools whose own outputs are time- or state-dependent (a search API returning slightly different top results on different days, a file system returning different content after a prior write), so the agent's downstream tokens shift even when the model's own sampling is pinned.

### Break #2: many agent tasks have no single right answer to assert against
A unit test needs a ground truth to compare to. "Summarize this codebase's architecture," "investigate why this alert fired," and "propose three approaches to this refactor" do not have one correct string - they have a *space* of acceptable answers and a much larger space of unacceptable ones (wrong, incomplete, fabricated, missing the actual root cause). Testing this requires a way to judge membership in the acceptable set, not comparison to one member of it. This is the problem `agent-evaluation/03` (LLM-as-judge) and `agent-evaluation/02` (benchmarks with graded rubrics) exist to solve - grading against criteria instead of grading against one fixed string.

### Break #3: trajectories carry information the final answer hides
Take a support agent asked to refund an order. Trajectory A: check order status, confirm it's eligible, issue the refund, done - three tool calls, each one necessary. Trajectory B: issue the refund immediately without checking eligibility, notice the order was already refunded (a tool error), issue a second refund, notice the double-refund from a follow-up balance check, and issue a compensating reversal - four extra tool calls, and it happens to net out to the same final account balance as Trajectory A. An evaluation that only checks "is the final balance correct" scores both trajectories as passing. An evaluation that scores the trajectory (`agent-evaluation/04`) catches that Trajectory B skipped a required precondition check and only "worked" because of a lucky recovery - exactly the kind of latent failure mode that will not recover so luckily on a future run, since the recovery itself depended on non-deterministic model behavior.

### What a layered response looks like in practice
Treating "agent testing" as one discipline conflates a deterministic layer that behaves like normal software with a probabilistic layer that does not. A workable structure keeps them separate: run ordinary unit tests against the deterministic scaffolding (tool-call parsing, argument validation, routing, formatting - the boxes in the diagram above that are not the model), and run rubric- or judge-based evaluation (`agent-evaluation/02`, `agent-evaluation/03`) plus trajectory scoring (`agent-evaluation/04`) against everything that depends on the model's sampled output. Collapsing the two - trying to `assert_equal` your way through the model's output, or conversely never unit-testing the plumbing because "the agent is non-deterministic anyway" - is the mistake this lesson is naming.

## Pros
- Naming the break explicitly stops teams from writing brittle exact-match tests that fail on every model or prompt update for reasons that have nothing to do with correctness.
- Separating the deterministic scaffolding from the probabilistic core lets you keep cheap, fast, reliable unit tests exactly where they still work, instead of discarding testing discipline entirely.
- Recognizing trajectories as evaluable surfaces failure modes (lucky recoveries, unnecessary tool calls, skipped preconditions) that outcome-only checking hides until they fail in production without a fallback.

## Cons
- Rubric- and judge-based evaluation (the replacement for exact-match) is inherently less precise than a boolean assertion - a judge can be wrong, inconsistent, or biased (`agent-evaluation/03`), so evaluation confidence is probabilistic too, not binary pass/fail.
- Building and maintaining evaluation criteria, rubrics, and judge prompts is real engineering work with its own cost, unlike writing `assert_equal`, which is close to free once you know the expected value.
- Teams that don't make this distinction often overcorrect into "nothing about agents is testable," skipping unit tests for the deterministic layer that would have caught real bugs cheaply.

## Alternatives
- **Keep using exact-match unit tests everywhere, including on the model's output** - works only for the narrow slice of agent behavior that is genuinely deterministic (fixed-temperature-zero, no external tool variance, single canonical answer); breaks down for almost any realistic multi-step agent, producing constant false failures.
- **Skip automated testing, rely on human spot-checks** - avoids the assert-equal mismatch entirely but doesn't scale past a handful of examples, catches regressions late (often only after a user reports one), and provides no automatable signal for CI/CD gates on model or prompt changes.
- **Golden-trajectory replay (record one accepted run, diff future runs against it)** - a middle ground: cheaper to build than a full rubric/judge system, but as brittle as exact-match once the trajectory itself is allowed to vary legitimately (a different but equally valid tool order), which is common in agents whose value is exactly that they are not scripted (`tool-use-agentic-loop/03`).

## When to use it
Reach for the probabilistic-evaluation mindset (rubrics, judges, trajectory scoring - the rest of this subject) as soon as an agent's correctness depends on model-sampled output: any agent making judgment calls about which tool to call, what argument values to use, or how to phrase a final answer to an open-ended request. This is the normal case for anything built on the agentic loop.

## When NOT to use it
Do not reach for judges or rubrics on the deterministic scaffolding underneath the loop - argument schema validation, tool-call parsing, routing logic, retry/backoff code, formatting. That code has no model sampling in it; ordinary unit tests are strictly better there (faster, free, unambiguous), and wrapping it in judge-based evaluation just adds cost and noise for no benefit.

## Key takeaways / mental model
Unit testing assumes: same input -> same output -> one correct output -> compare with `==`. Agentic loops break all three assumptions at once, because the model samples tokens, many tasks have no single correct output, and correctness depends on the path taken, not just the final string. The fix is not "don't test agents" - it's splitting the system into a deterministic layer (still unit-testable) and a model-driven layer (needs rubrics, judges, and trajectory scoring, covered in the rest of this subject) and applying the right tool to each.

## Self-check questions
1. A teammate writes `assert_equal(agent_response, "The capital of France is Paris.")` for an agent that answers geography questions, and it fails intermittently even though the agent is always factually correct. Diagnose which of the three breaks (non-determinism, no single right answer, trajectory-dependence) is responsible, and propose a fix that doesn't just lower the temperature to zero.
2. Give an example, different from the refund scenario above, of two trajectories that reach the same correct final answer but where one should still fail evaluation. What would a trajectory-level check need to look at to tell them apart?
3. Which parts of an agent's implementation remain safely unit-testable with `assert_equal`, and why does the presence of an LLM elsewhere in the system not contaminate that testability?
4. A junior engineer proposes recording one "golden" trajectory for a research agent and failing any future run that deviates from it. Explain why this is more brittle than it looks, using the agentic-loop property that plan steps are conditioned on observations (`tool-use-agentic-loop/03`).
5. Why is "the agent is non-deterministic, so we can't meaningfully test it" an overcorrection? Name one category of bug this mindset would let through unnoticed.

## References
- [Anthropic Engineering: Writing effective tools for AI agents](https://www.anthropic.com/engineering/writing-tools-for-agents) (2025-09-11)
- Datagrid, "4 Testing Frameworks for AI Agents When Traditional QA Fails" (2026), https://datagrid.com/blog/4-frameworks-test-non-deterministic-ai-agents
- Netguru, "Testing AI Agents: Why Unit Tests Aren't Enough" (2026), https://www.netguru.com/blog/testing-ai-agents
- SitePoint, "Testing AI Agents: Validating Non-Deterministic Behavior" (2026), https://www.sitepoint.com/testing-ai-agents-deterministic-evaluation-in-a-non-deterministic-world/
