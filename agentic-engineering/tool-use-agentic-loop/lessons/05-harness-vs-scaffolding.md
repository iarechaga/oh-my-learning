---
id: tool-use-agentic-loop/05
subject: tool-use-agentic-loop
title: "Harness vs Scaffolding: What Wraps the Model and What the Model Works From"
slug: harness-vs-scaffolding
status: drafted
mastery:
seniority: senior
source: "Hugging Face blog: Harness, Scaffold, and the AI Agent Terms Worth Getting Right (2026); Addy Osmani: Agent Harness Engineering (2026); Wikipedia: Agent harness (2026); Anthropic engineering blog: Effective context engineering for AI agents (2025)"
durability: durable
prerequisites: [tool-use-agentic-loop/03]
created: 2026-08-10
updated: 2026-08-10
---

# Harness vs Scaffolding: What Wraps the Model and What the Model Works From

## TL;DR
"Agent = Model + Harness" is a useful shorthand, but it collapses two distinct layers that are worth separating precisely: the **harness** is the execution/control layer that calls the model, dispatches its tool calls, and decides when to stop; the **scaffolding** is what the model actually works from on any given turn - its instructions, its available tools, and the format its outputs and observations take. The harness runs the loop; the scaffolding is what's inside the loop's context window. Getting this distinction right matters because most agent quality problems are scaffolding problems wearing a harness-shaped disguise, or vice versa, and fixing the wrong layer wastes real engineering time.

## The idea
By the time you've built the agentic loop from lesson 03 - plan, act, observe, repeat - you have something that works, in the narrow sense that it runs. But "the agent" is really two separable concerns bolted together, and conflating them is the single most common source of confused agent-engineering conversations in 2026. One concern is: *what code actually drives this loop?* Something has to call the model's API, parse its response for tool calls, execute those tool calls, feed results back, and decide when the loop is done. That's infrastructure - it's the same shape of problem regardless of which task the agent is doing. The other concern is: *what does the model actually see and work from when it's asked to reason?* System prompt, tool descriptions, the format of past results, any injected context - that's content, and it's highly task-specific.

The industry settled on **harness** for the first concern and **scaffolding** for the second, though - as with most fast-moving terminology - usage isn't perfectly uniform: some products (several coding-agent CLIs among them) use "harness" loosely as an umbrella term for the whole system, folding scaffolding in as one of its components rather than treating the two as parallel, equally-weighted layers. Both usages agree on the underlying distinction even when they disagree on where to draw the outer boundary; this lesson uses the narrower, more precise pairing because it's the one that actually helps you diagnose problems.

Why the distinction earns its own lesson: it changes where you look when an agent misbehaves. A model that never stops looping, calls the wrong tool-execution code, or crashes on a malformed API response has a harness bug. A model that has the right tools and the right control loop but keeps making bad decisions, ignoring instructions, or misusing a tool has a scaffolding problem - the harness is working exactly as designed, faithfully executing decisions made from bad material. Debugging the wrong layer - rewriting the control loop when the actual issue is a vague tool description, or rewriting the system prompt when the actual issue is that the harness silently drops tool-call errors - burns time without fixing anything.

## How it works

### The harness: the execution layer
The harness is the code that makes an agent actually run. Concretely, it is responsible for:
- **Calling the model** - constructing the API request each turn, including whatever the scaffolding says should be in it.
- **Parsing and dispatching tool calls** - reading the model's `tool_use` blocks, routing each to the correct handler/function, executing it (sequentially or in parallel, per lesson 04), and capturing the result or error.
- **Feeding results back** - assembling `tool_result` blocks (or the equivalent) into the next turn's request.
- **Deciding when to stop** - detecting a final answer, a termination condition, a budget exhausted, or an unrecoverable error (this is the subject of lesson 08).
- **Cross-cutting infrastructure** - retry logic, timeouts, logging/tracing, sandboxing and permission enforcement, session/state persistence across turns.

None of this is specific to any one task. The same harness code that drives a coding agent could, with a different scaffold loaded into it, drive a customer-support agent or a research agent - the loop mechanics (call, dispatch, feed back, decide when to stop) are identical; only the content flowing through them changes.

### The scaffolding: what the model works from
The scaffolding is the content the harness assembles and hands to the model each turn - the material the model actually reasons over, not the code that moves that material around. Concretely:
- **System/developer instructions** - the persona, constraints, and behavioral guidance (lesson 02 of the prerequisite subject covers instruction anatomy).
- **Tool definitions and descriptions** - what tools exist, their schemas, and how well-described they are (lesson 02 of this subject).
- **Context management policy** - what conversation history, retrieved documents, and prior results are included, summarized, or dropped on this turn (the context-engineering subject covers this in depth).
- **Response/observation format** - how tool results are structured when handed back to the model, how errors are represented, whether outputs are constrained to a schema.

Critically, scaffolding is not "static config set once at agent creation" - a context-management policy that decides what to summarize or drop each turn (compaction, handoff) is scaffolding logic even though it runs dynamically throughout the session, because its job is to shape what the model sees, not to execute what the model decided.

### A worked example: locating a bug in the right layer
Consider a coding agent that, partway through a long refactor, starts repeatedly re-reading the same file it already read ten turns ago, wasting turns and tokens. Where's the bug?

```
Symptom: agent re-reads a file it already read

Harness-layer questions:                Scaffolding-layer questions:
- Is the tool-call dispatcher            - Is the file's content actually
  correctly executing the read             still in the model's context,
  and returning a result?                  or was it dropped/summarized
- Is there a bug silently swallowing       away by a context-management
  the result before it reaches the         policy that discarded it too
  next turn's context?                     aggressively?
- Is the loop's stop condition           - Is the tool description for
  irrelevant here (the loop isn't          "read_file" ambiguous about
  ending, it's just wasteful)?             whether results are cached?
                                          - Does the system prompt tell
                                            the model it can trust its own
                                            memory of prior reads, or does
                                            it implicitly encourage
                                            re-verification?
```

If the tool-call dispatcher is executing correctly and returning results, and the loop's control flow is otherwise sound, the harness is doing its job - the bug is almost certainly scaffolding: the file's content isn't durably available to the model when it needs it (a context-engineering problem, see the compaction lesson in the prerequisite subject), or the model has no signal that it already has this information. Rewriting the tool-dispatch code would not fix this; changing what's in context, or how results are represented, would.

### A second worked example: a harness bug that looks like a model problem
Now consider an agent that occasionally "hallucinates" a tool result - it proceeds as if a tool call succeeded and returned data, when in fact the call errored. On the surface this looks like a model reasoning failure. But trace it: if the harness's error-handling path silently converts a tool execution exception into an empty or malformed `tool_result` block instead of an explicit error message, the model is reasoning correctly from what it was shown - it was never told the call failed. This is a harness bug (error handling swallowed the failure) masquerading as a scaffolding or model-quality problem. The fix is in the execution layer: propagate errors as explicit, well-formatted content the model can see and react to, not silence them.

### Why the boundary is genuinely fuzzy in places, and why that's fine
Some things sit awkwardly across the line. Retry logic is clearly harness (it's control flow, not content) - but *what* an error message says when retried, and whether it's phrased in a way the model can act on, is scaffolding. Termination conditions (lesson 08) are harness (the mechanism that stops the loop) but the *criteria* for stopping are often expressed to the model as instructions, which is scaffolding content the harness then has to detect and act on. This fuzziness is normal and matches how the terminology is actually used in the field as of 2026 - the harness/scaffolding split is a useful diagnostic lens for "which layer do I fix," not a rigid architectural law with a court-admissible boundary. When in doubt, ask the operational question that actually matters: is this a bug in the code that runs the loop, or a problem with the material the model was given to reason over? That question resolves the fuzzy cases well enough to act on, even when a purist would quibble about exactly which bucket a given line of code belongs in.

> **Example (Aug 2026):** several coding-agent products document their own architecture using this vocabulary, though the exact boundary drawn differs per product. One vendor's own documentation states plainly that its CLI product "serves as the agentic harness" around its model, using "harness" as the broad umbrella term (folding scaffolding in as a component) rather than as a narrowly-scoped execution layer distinct from scaffolding. Treat the underlying distinction - execution/control code versus the content the model reasons over - as the durable concept, and the exact term boundaries as something to verify against current docs for whichever product you're discussing.

## Pros
- **Sharper debugging.** "Which layer is this bug in" is a fast, high-leverage triage question that narrows the search space immediately, instead of guessing between rewriting the loop and rewriting the prompt.
- **Enables independent iteration.** A team can improve the harness (better retry logic, better observability, better parallel dispatch) without touching scaffolding content, and vice versa - the two evolve on different cadences in practice, since harness changes are closer to normal software engineering and scaffolding changes are closer to prompt/context iteration.
- **Clarifies where reusability lives.** A well-built harness is largely task-agnostic and can be reused across many different agents; scaffolding is where task-specific behavior actually lives. This maps directly onto build-vs-buy decisions: teams increasingly buy or adopt a harness and invest their own effort in scaffolding.

## Cons
- **The boundary is genuinely fuzzy** in real systems (see the retry-logic and termination-condition examples above), so treating it as a hard architectural line rather than a diagnostic lens leads to unproductive arguments about which bucket a given piece of code belongs in.
- **Terminology is not fully standardized** - some products and writers use "harness" as the umbrella term for everything (including scaffolding), others use it narrowly for just the execution layer; readers have to infer which usage a given source intends.
- **Over-applying the framework to small systems is wasted ceremony** - a simple, single-purpose agent with no plans to swap models or contexts independently doesn't need the two concerns architected as separate modules; the distinction pays off most as a system's complexity or reuse surface grows.

## Alternatives
- **Treat the whole system as one undifferentiated "agent"** - simpler to talk about for small, single-purpose systems, but loses the diagnostic power of the split the moment something breaks and you need to know which layer to fix.
- **A finer-grained layering (SDK / framework / scaffolding / harness as four distinct terms)** - some practitioner writing distinguishes an underlying SDK (raw model-calling primitives) and a framework (opinionated structure on top) as further layers beneath harness and scaffolding. More precise for teams building infrastructure products, but more ceremony than most agent builders need; the two-layer harness/scaffolding split is usually sufficient for diagnosing and reasoning about a specific agent.
- **Model-centric framing ("just make the model better")** - assumes agent quality is purely a model capability problem. Fails to explain why the same model produces very different agent quality across different harnesses/scaffolds - most practical agent-quality gains in 2026 come from harness and scaffolding engineering, not from swapping the underlying model.

## When to use it
Reach for this distinction whenever you're debugging an agent that isn't behaving as expected, designing a new agent system, or evaluating whether to build vs. adopt an existing agent framework. It's especially valuable the moment a team is maintaining more than one agent, or considering swapping models under an existing agent - those are exactly the situations where knowing what's harness (reusable, model-agnostic) and what's scaffolding (task-specific, likely needs re-tuning per model) determines how much work a change actually requires.

## When NOT to use it
Don't bother formalizing the split for a small, one-off script that calls a model with one or two tools and has no ambitions to be reused, extended, or debugged by anyone else - the conceptual overhead of "which layer is this" isn't worth it below a certain complexity threshold. Also resist treating the boundary as load-bearing for architecture decisions in ambiguous cases (see Cons) - use it to guide where you look first, not as a rule you defend past the point it's helping.

## Key takeaways / mental model
Picture the harness as the stage machinery - the code that raises the curtain, cues the actor, and knows when to bring it back down - and the scaffolding as the script and props the actor actually works from. A bad performance could be a stagehand missing a cue (harness bug: something in the control/execution layer misfired) or a bad script (scaffolding problem: the instructions, tools, or context the model was given were wrong, ambiguous, or missing). The recurring diagnostic question when an agent misbehaves is not "is the model bad?" but "is this a bug in the code that runs the loop, or a problem with the material the model was handed to reason over?" - and the fuzzy cases (retry logic's error phrasing, termination criteria expressed as instructions) are exactly where both layers touch, which is normal, not a flaw in the model.

## Self-check questions
1. An agent occasionally calls a tool with arguments that don't match the tool's schema, causing a validation error the model then has to recover from. Is this more likely a harness problem or a scaffolding problem? What would you check first, and why?
2. Your team wants to swap the underlying model powering an existing agent from one vendor's model to another's. Using this lesson's framing, which parts of the system do you expect to carry over unchanged, and which parts do you expect to need re-tuning? Justify each.
3. Give an example (not from this lesson) of a bug that could plausibly be diagnosed as either a harness bug or a scaffolding problem depending on where exactly the failure originates, and explain what evidence would settle which layer is actually at fault.
4. A junior engineer says "let's just make the system prompt tell the model to retry failed tool calls up to 3 times." Explain, using this lesson's vocabulary, why this is solving a harness-shaped problem with a scaffolding-shaped fix, and what the more robust alternative would look like.
5. Why does the lesson claim the harness/scaffolding boundary is "genuinely fuzzy in places" rather than a clean architectural law? Give one concrete example of code that could reasonably be classified as either, and explain what makes it ambiguous.

## References
- [Hugging Face blog: Harness, Scaffold, and the AI Agent Terms Worth Getting Right](https://huggingface.co/blog/agent-glossary)
- [Addy Osmani: Agent Harness Engineering](https://addyosmani.com/blog/agent-harness-engineering/)
- [Wikipedia: Agent harness](https://en.wikipedia.org/wiki/Agent_harness)
- [Anthropic engineering blog: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
