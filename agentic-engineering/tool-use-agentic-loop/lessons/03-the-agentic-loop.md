---
id: tool-use-agentic-loop/03
subject: tool-use-agentic-loop
title: "The Agentic Loop: Plan, Act, Observe, Repeat"
slug: the-agentic-loop
status: drafted
mastery:
seniority: mid
source: "Anthropic Platform docs: How tool use works (2026); arXiv:2210.03629 ReAct - Synergizing Reasoning and Acting in Language Models (2023, ICLR); AddyOsmani.com: Plan-Act-Observe Loop - Agentic Engineering Glossary (2026); Data Science Dojo: Agentic loops explained - From ReAct to loop engineering (2026)"
durability: durable
prerequisites: [tool-use-agentic-loop/01]
created: 2026-08-10
updated: 2026-08-10
---

# The Agentic Loop: Plan, Act, Observe, Repeat

## TL;DR
A single tool call - the model emits a request, your code runs it, the result goes back in - is not yet "agentic." What makes something an *agent* is that this round trip happens repeatedly, with each result feeding the model's next decision about what to do next, continuing under the model's own judgment until it decides the task is done or something external stops it. This repeating cycle - conventionally described as **plan, act, observe, repeat** - is the load-bearing structure underneath essentially every autonomous AI system built since 2023, and every later concept in this domain (parallel calls, harnesses, failure recovery, termination conditions) is a refinement of one part of this loop.

## The idea
`tool-use-agentic-loop/01` walked through one tool call end to end: the model requests `get_weather`, your code executes it, the result comes back, the model answers. That is a complete, useful interaction - and it is also, on its own, not meaningfully different from calling a function inside an `if` statement. Nothing about a single round trip requires the model to *decide* anything more sophisticated than "should I call this one tool, yes or no."

The shift to "agent" happens at the moment the *loop itself*, not any single call, becomes the unit of behavior: the model's output on each turn is not just "the final answer" or "one tool request," but a judgment call, made fresh every iteration, about what to do given everything observed so far - including whether to keep going at all. A research assistant that searches once and reports what it found is a single tool call. A research assistant that searches, reads what came back, notices a gap, searches again with a refined query, reads a source that contradicts the first one, decides to check a third source, and only then writes a synthesis - that is an agentic loop. The difference is not the number of tools available; it's that each step's plan is conditioned on the *outcome of the previous step*, not on a plan fixed in advance by a human or a static script.

This pattern was named and popularized as **ReAct** (Reason + Act) in a 2023 paper, which showed that interleaving explicit reasoning traces with actions - "think about what to do, do it, observe what happened, think again" - outperformed either pure reasoning (chain-of-thought with no tools) or pure acting (tool calls with no explicit reasoning) on tasks requiring both multi-step reasoning and interaction with an external environment. The reasoning step turned out to matter mechanically, not just cosmetically: because the model is autoregressive (`prompting-context-engineering/01`), generating explicit "here's what I've learned and here's what I should do next" text before the next action *conditions* that action's tokens on a coherent plan, which measurably improves the model's ability to track progress, catch its own mistakes, and adjust course mid-task compared to jumping straight to the next tool call.

## How it works

### The three phases of one iteration
Every pass through the loop has the same three-part shape, regardless of the specific vendor or framework running it:

- **Plan (reason):** given everything in context - the original task, every prior action, every prior observation - the model decides what to do next. In practice this is often an explicit chunk of generated reasoning text ("the search returned three candidates; the second looks most relevant, I should read it in full before deciding") immediately preceding a tool call, though some harnesses suppress or hide this text from the end user while still relying on it internally.
- **Act:** the model emits a structured tool call (the mechanism from `tool-use-agentic-loop/01`), and the calling application executes it - a search, a file read, a code execution, an API call.
- **Observe:** the tool's result is fed back into the model's context as a new turn, becoming part of "everything in context" for the *next* plan step.

```
        +-------------------------------------------+
        |                                             |
        v                                             |
  [ PLAN: reason over context, decide next action ]    |
        |                                             |
        v                                             |
  [ ACT: emit tool call -> application executes ]      |
        |                                             |
        v                                             |
  [ OBSERVE: result appended to context ]              |
        |                                             |
        +----------- done? ----no----------------------+
                       |
                      yes
                       |
                       v
               [ final answer ]
```

The loop is not a fixed number of iterations decided in advance; it is a `while` condition. Concretely, in a widely used implementation pattern, the calling application checks a status signal on every model response (commonly something like a `stop_reason` field indicating "I want to call a tool" versus "I am done"), and keeps re-entering the loop for as long as that signal says "not done yet." The loop terminates when the model itself emits a final answer with no further tool call, or when some external limit (covered fully in `tool-use-agentic-loop/08`) cuts it off first.

### Worked example: a coding agent fixing a failing test
Consider an agent asked to "make the failing test pass" in a codebase, with tools for reading files, editing files, and running the test suite:

```
Iteration 1
  PLAN:    "I don't know why the test is failing yet. I should run it
            first to see the actual error."
  ACT:     run_tests()
  OBSERVE: "FAILED test_discount: expected 0.9, got 1.0"

Iteration 2
  PLAN:    "The discount isn't being applied. I should find where
            discount logic lives before touching anything."
  ACT:     read_file("pricing.py")
  OBSERVE: [contents of pricing.py, showing a discount() function
            that has an early `return price` before the discount
            multiplication line]

Iteration 3
  PLAN:    "Found it - an early return skips the discount line.
            I'll remove the early return."
  ACT:     edit_file("pricing.py", ...)
  OBSERVE: "edit applied successfully"

Iteration 4
  PLAN:    "I should verify the fix actually worked before declaring
            success, not just trust that the edit was correct."
  ACT:     run_tests()
  OBSERVE: "PASSED test_discount"

Iteration 5
  PLAN:    "The test passes now, and nothing else in the observation
            suggests new failures. Task complete."
  ACT:     (none - final answer)
  -> "Fixed: removed an early return in pricing.py that was
      skipping the discount calculation. test_discount now passes."
```

Notice what makes this "agentic" rather than "a script that calls four tools in order": nothing in the human's original request specified *which* file to read, *what* the bug was, or that a fourth verification step was needed at all. Each plan step was produced fresh, conditioned on the specific content of the *previous* observation - iteration 2's plan exists only because iteration 1's observation revealed a specific failing assertion; iteration 4 exists only because the model, on its own judgment, decided a successful-looking edit still needed verification before it could be trusted. A fixed script ("read pricing.py, then edit line 12, then run tests") would have been faster for this exact case and would have completely failed on a differently-shaped bug. The loop's value is precisely that its shape is not fixed in advance.

### What "agentic" is not: three things that look similar but aren't
- **A single tool call, however complex.** One `get_weather` call followed by an answer is tool use, not an agentic loop - there is no *second* decision made in light of the first result. (This is exactly the round trip covered in `tool-use-agentic-loop/01`; it becomes agentic only when the model's next move genuinely depends on what came back, and that dependency repeats.)
- **A fixed, pre-scripted pipeline of tool calls.** "Always call `search`, then always call `summarize`, then always call `send_email`" is a workflow, not an agentic loop, even if it's implemented using the same tool-call machinery - the sequence and the decision to proceed are fixed by the developer in advance, not decided by the model turn to turn based on what it observes. (Whether a scripted pipeline or a genuine loop is the right choice for a given task is itself a real design decision, covered in `tool-use-agentic-loop/05` under harness vs. scaffolding.)
- **Chain-of-thought reasoning with no tools at all.** A model "thinking step by step" through a math problem entirely in its own generated text is reasoning, but it is not acting on or observing anything outside its own context - there's no external environment providing new information the model didn't already have. ReAct's specific insight was that interleaving reasoning *with* real actions and real observations outperforms either one alone, because observations inject genuinely new information a closed reasoning chain cannot generate on its own.

### The loop's core dependency: observations must actually change the plan
The mechanism only earns the name "agentic" if observations are load-bearing - if the plan on iteration N+1 would genuinely differ depending on what iteration N observed. A loop that runs five tool calls but would have produced the exact same five calls regardless of any result along the way is not really using the "observe" step; it's a fixed pipeline wearing a loop's clothing. This is a useful diagnostic when debugging or designing an agent: for each step, ask "if the previous observation had come back differently, would this step have changed?" If the honest answer is consistently "no," the task may not need a loop at all - a simpler, cheaper, more predictable pipeline (per `tool-use-agentic-loop/05`) is likely the better design.

## Pros
- Handles genuinely open-ended tasks where the right sequence of actions cannot be known in advance - exactly the tasks a fixed pipeline cannot handle at all.
- Self-correcting within a run: because each plan step sees the actual outcome of the previous action, the loop can notice a wrong turn (a failed edit, an empty search result, a contradictory source) and adapt, rather than blindly continuing a pre-committed plan.
- The reasoning-then-acting interleaving (ReAct's core finding) produces more transparent, auditable decision traces than either silent tool-chaining or pure internal reasoning, which matters for debugging and for trusting an agent's output.

## Cons
- Non-deterministic and harder to test than a fixed pipeline: the same starting task can take a different number of iterations, touch different tools, or even reach a different (still valid) outcome on different runs, because each plan step is itself model output.
- Every iteration re-sends the growing history as input (per the statelessness mechanics of `prompting-context-engineering/01`), so cost and latency scale with the number of iterations, and a poorly bounded loop can run far longer, and far more expensively, than a human would expect.
- Without explicit termination discipline (`tool-use-agentic-loop/08`), the loop has no inherent reason to stop - it can oscillate (undo and redo the same fix), loop indefinitely on an unsolvable sub-task, or declare success prematurely, none of which a fixed pipeline is capable of doing in the same way.

## Alternatives
- **Single tool call / single round trip** (`tool-use-agentic-loop/01`) — the right choice whenever one piece of external information or one action fully answers the request; adding loop machinery around a task that never needs a second, observation-dependent decision is pure overhead.
- **Fixed pipeline / deterministic workflow of tool calls** — a developer-specified sequence of steps, each of which may call a tool, but where the sequence and branching logic are fixed in code rather than decided by the model at each step; strictly more predictable, testable, and cheaper to run than a loop, and the right choice whenever the actual steps needed are known and stable in advance (explored fully as "harness vs. scaffolding" trade-offs in `tool-use-agentic-loop/05`).
- **Human-in-the-loop, single-shot assistance** — the model proposes a plan or a single action and a human executes or approves each step manually; slower and non-autonomous by design, but appropriate when the cost of an autonomous wrong action is too high to accept without a human checkpoint on every step.

## When to use it
Reach for a genuine agentic loop when the task's correct sequence of actions cannot be known in advance and depends on information only discoverable by taking earlier actions - debugging an unfamiliar failure, researching a question whose sub-questions only become clear once initial results come in, navigating a codebase whose structure isn't known until it's explored. The hallmark to look for: if you cannot write down the exact sequence of tool calls a human expert would make before they've seen any results, the task needs a loop, not a script.

## When NOT to use it
Skip the loop - and use a single tool call or a fixed pipeline instead - whenever the needed sequence of actions is actually known and stable ahead of time (a report that always fetches the same three data sources in the same order), or when the task is answerable in one round trip. Building open-ended loop machinery for a task that never branches based on what it observes adds non-determinism, cost, and debugging surface for zero benefit; per the diagnostic above, if none of the plan steps would ever change based on an observation, you are looking at a pipeline problem wearing an agent costume.

## Key takeaways / mental model
An agentic loop is not "a model that can use tools" - `tool-use-agentic-loop/01` already gives you that. It is **repeated, observation-conditioned decision-making**: plan (reason over everything seen so far) -> act (emit and execute one tool call) -> observe (fold the real-world result back into context) -> repeat, until the model itself judges the task done or an external limit intervenes. The test for whether something deserves the name "agentic" is not how many tools it touches; it's whether the next step would have looked different if the last observation had come back differently. Everything later in this subject - running calls in parallel without breaking correctness, choosing loop versus pipeline, surviving a tool failure mid-loop, and knowing when to stop - is about making this one repeating cycle work well in practice.

## Self-check questions
1. A "research agent" always calls `search`, then always calls `read_top_result`, then always calls `summarize`, in that fixed order, regardless of what any step returns. Is this an agentic loop by the definition in this lesson? Justify your answer using the "would the next step change" diagnostic.
2. Walk through the coding-agent worked example above and identify the single observation that, if it had come back differently (say, the test still failed after the edit), would have most changed the shape of the rest of the loop. What would iteration 5 likely have looked like instead?
3. Explain, in terms of the autoregression mechanics from `prompting-context-engineering/01`, why generating explicit reasoning text ("the search returned three candidates...") immediately before a tool call can actually change which tool call gets emitted next, rather than being purely cosmetic.
4. A teammate proposes replacing an agentic loop that currently debugs failing builds with a fixed pipeline: "always check the log, always check the last diff, always revert." Under what circumstances would that be a strictly better design than the current loop, and under what circumstances would it fail?
5. Describe, without naming a specific product, what would have to be true of a task for you to say with confidence "this does not need an agentic loop at all" - and give one concrete example.

## References
- [Anthropic Platform docs: How tool use works](https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works)
- Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models," arXiv:2210.03629 (2023), ICLR 2023, https://arxiv.org/abs/2210.03629
- AddyOsmani.com, "Plan-Act-Observe Loop - Agentic Engineering Glossary" (2026), https://addyosmani.com/agentic-engineering/plan-act-observe/
- Data Science Dojo, "Agentic loops explained: From ReAct to loop engineering (2026 guide)" (2026), https://datasciencedojo.com/blog/agentic-loops-explained-from-react-to-loop-engineering-2026-guide/
