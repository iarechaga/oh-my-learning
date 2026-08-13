---
id: multi-agent-orchestration/02
subject: multi-agent-orchestration
title: "Subagents: Delegation with Context Isolation"
slug: subagents-delegation-with-context-isolation
status: drafted
mastery:
seniority: mid
source: "Anthropic Engineering, How we built our multi-agent research system (Jun 2025); Anthropic, Effective context engineering for AI agents (Sep 2025); Claude Code Docs, Subagents in the SDK (2026); ClaudeWorld, Subagents & Context Isolation (2026)"
durability: durable
prerequisites: [multi-agent-orchestration/01, prompting-context-engineering/10]
created: 2026-08-10
updated: 2026-08-10
---

# Subagents: Delegation with Context Isolation

## TL;DR
A subagent is a delegation boundary: a parent agent hands off a scoped piece of work to a helper that runs in its own fresh, isolated context, does the work (however much exploration that takes), and reports back only a distilled result - not its full working trace. The parent's context stays clean regardless of how much scratch work the subagent did, at the cost of a real briefing tax (the subagent knows nothing except what the parent explicitly tells it) and a real trust tax (the parent only sees what the subagent chose to report).

## The idea
`multi-agent-orchestration/01` established that splitting work across agents only pays off when a subtask is genuinely separable and the cost is justified. This lesson is about the specific mechanism that makes that split actually work in practice: how does a parent agent hand off a piece of work such that it gets the isolation benefit without losing all continuity with the rest of the task?

The answer is a hard context boundary, not a soft one. `prompting-context-engineering/10` already introduced this idea in the single-agent case as "handoff" - stopping work in one context and starting a fresh one, carrying forward only what is deliberately passed. Subagent delegation is that same handoff mechanism used specifically to spin off a bounded piece of work from within an ongoing parent task, rather than to end a task and hand it to a full replacement. The parent keeps running; the subagent is a scoped detour, not a takeover.

What makes this pattern load-bearing rather than a mere implementation detail is what it buys you structurally: a subagent can explore as aggressively and messily as the problem requires - reading dozens of files, trying and discarding approaches, running long searches - and none of that exploration ever touches the parent's context. Only the return value crosses the boundary. This is qualitatively different from the parent doing the same exploration itself and then compacting it afterward (`prompting-context-engineering/10`): compaction still carries the shape and residue of everything that happened, compressed; a subagent boundary carries across nothing but what is explicitly returned.

## How it works

### The three parts of a delegation boundary
Every subagent delegation, regardless of the specific product implementing it, has the same three structural pieces:

- **The briefing (parent to subagent):** a self-contained prompt the parent constructs, containing everything the subagent needs to do its job - because the subagent starts with no visibility into the parent's history, files already read, or decisions already made. Whatever the briefing omits is simply unavailable to the subagent; there is no "let me check what the parent knows" fallback.
- **The isolated run (inside the subagent):** the subagent executes its own full agentic loop (`tool-use-agentic-loop/03`) - plan, act, observe, repeat - inside a context window that starts fresh and accumulates only what that subagent itself does. This can be arbitrarily long and exploratory without any cost to the parent's context budget.
- **The report (subagent to parent):** when the subagent finishes, it returns a distilled result - commonly a short structured summary, not the raw trace of everything it tried. The parent's context grows by only this summary, regardless of whether the subagent's own run took 5 tool calls or 500.

```
  PARENT CONTEXT                         SUBAGENT CONTEXT (fresh)
  ---------------                        -------------------------
  ...accumulated history...
        |
        | briefing (only this crosses)
        v
                                    -->   [ fresh context starts here ]
                                          PLAN -> ACT -> OBSERVE
                                          PLAN -> ACT -> OBSERVE
                                          ... (as many iterations as needed,
                                               none of this is visible
                                               to the parent) ...
                                          PLAN -> ACT -> OBSERVE -> done
        ^
        | report (only this crosses back)
        |
  ...parent continues, context grew
  by only the report, not the run...
```

### Worked example: a coding agent delegating a codebase-wide investigation
A parent agent is implementing a new feature and needs to know "does any existing code already implement rate limiting, and if so, where and how." Handling this in the parent's own context would mean searching broadly, opening a dozen candidate files, reading most of them, and discarding the ones that turn out irrelevant - all of that exploration piling into the same context the parent needs to stay clear-headed for the actual feature work.

Instead, the parent delegates: "Search this codebase for any existing rate-limiting implementation. Report back: whether one exists, its file path(s), the specific mechanism used (e.g. token bucket, fixed window), and whether it is reusable for a new endpoint, in under 200 words. Do not make any code changes." The subagent runs its own loop - greps for "rate limit," "throttle," "bucket"; opens four candidate files; reads two of them in full; determines one is dead code and one is the real implementation; inspects that one closely enough to characterize its mechanism. That might be fifteen tool calls and several thousand tokens of exploration. None of it reaches the parent. The parent's context grows by one paragraph: "Found an existing token-bucket rate limiter in `middleware/throttle.py`, currently used only on the `/upload` endpoint; it is generic enough to reuse by registering the new endpoint's key, no structural changes needed." The parent now has exactly what it needs to proceed, at a fraction of the context cost of having done the search itself.

### Worked example: a briefing failure and what it costs
Consider the same setup, but with a thinner briefing: "Check if we already have rate limiting." The subagent, with no scope or output format specified, might spend its run investigating three unrelated systems that happen to also throttle something (an email-sending queue, a background job scheduler, and the actual HTTP rate limiter), and return a long, unstructured report covering all three because it had no signal about which one the parent actually cares about, or how much detail to include. The parent now has to spend its own context reading and filtering that oversized report to extract the one relevant fact - which defeats a meaningful fraction of the isolation benefit the delegation was supposed to provide. This mirrors the recall/precision trade-off from `prompting-context-engineering/10`'s discussion of handoff briefings: a briefing that is too thin produces a subagent that either guesses wrong about scope or over-reports out of caution, and either failure pushes cost back onto the parent.

### The trust problem: the parent only sees what the subagent chose to report
Because the report is the only channel back, the parent has no way to verify a subagent's summary except by trusting it or by redoing the work itself (which defeats the purpose). If a subagent's report is subtly wrong - it missed a second, more relevant implementation because its search terms were too narrow, say - the parent has no mechanism to notice this from inside its own context; the missing information is not merely compressed, as it would be after compaction, it was simply never generated. This is a structurally different failure than an overloaded single context: a single agent that missed something can, in principle, go back and look again because the raw material is still in its history somewhere; a parent that received an incomplete subagent report has no raw material to go back to at all. Well-specified briefings (clear scope, clear output format, explicit instruction to flag uncertainty) reduce this risk but cannot eliminate it - which is precisely why delegation is reserved for subtasks whose isolation benefit is worth this loss of verifiability, per the decision framework in `multi-agent-orchestration/01`.

### Delegation versus a plain tool call
It is worth being precise about what makes this "delegation with context isolation" rather than just "a tool call that happens to invoke a language model." A regular tool call (`tool-use-agentic-loop/01`) returns a single, usually structured and predictable result from a deterministic function. A subagent delegation hands off an open-ended objective to something that itself runs a full agentic loop, makes its own judgment calls about how to pursue that objective, and returns a result whose content and quality depend on decisions the parent never sees being made. The parent is trading direct control over the how for a clean context and, when running several such delegations concurrently, real parallelism (`multi-agent-orchestration/01`).

> **Example (Aug 2026):** several coding-agent products let a main session spawn subagents that run with their own isolated context and permissions and report back a summary to the parent - the exact configuration mechanism (dedicated config files, in-line tool parameters, or something else) and terminology ("subagent," "worker," "task") differs per product.

## Pros
- The parent's context stays clean and small regardless of how much exploratory work a delegated subtask required - the core benefit that makes this worth the overhead at all.
- Lets a subagent explore aggressively (try dead ends, read broadly, backtrack) without any of that exploration cost landing in the parent's budget.
- Composable with parallelism (`multi-agent-orchestration/01`): several independent delegations can run concurrently, each with its own isolated context.
- Produces a natural audit boundary - the briefing and the report are both compact, reviewable artifacts, unlike a sprawling single-context trace.

## Cons
- The briefing is the subagent's entire world; anything it omits is simply unavailable, with no fallback the way a single continuous context has.
- The parent cannot verify a report's completeness except by trusting it or redoing the work, which defeats the point of delegating.
- Real coordination cost: someone (often the parent agent itself, via its own reasoning) has to decide what belongs in the briefing and how to parse and act on the report.
- Adds latency for a single, non-parallelized delegation compared to just doing the work in the parent's own context, since spinning up a fresh context and later reconciling its output is not free.

## Alternatives
- **Doing the work directly in the parent's context** — no isolation, but no briefing or trust tax either; correct when the work is small enough that context pollution was never a real risk.
- **Compaction** (`prompting-context-engineering/10`) — compresses the parent's own accumulated history in place rather than boundary-isolating a subtask; the right tool when the work is one continuous thread rather than a separable piece.
- **Deterministic tool call** (`tool-use-agentic-loop/01`) — when the sub-task genuinely has one right procedure and does not need model judgment at all, a plain function call is cheaper and more predictable than spinning up a subagent to do it.

## When to use it
Delegate to a subagent when a piece of work is genuinely separable from the parent's main thread, would require enough exploration to meaningfully pollute the parent's context if done in place, and can be specified with a briefing precise enough that the subagent does not need anything beyond it to succeed.

## When NOT to use it
Skip delegation when the work is small enough that context pollution was never a real risk - the briefing and reconciliation overhead would cost more than it saves. Also skip it when the subtask is not actually separable from the parent's ongoing reasoning (it needs to see decisions the parent is still making, or the parent needs to see the subagent's reasoning process, not just its conclusion) - per `multi-agent-orchestration/01`'s independence test, forcing a real dependency through a delegation boundary just adds a briefing tax on top of the underlying coupling.

## Key takeaways / mental model
A subagent delegation is a hard context wall with exactly two doors: the briefing going in, the report coming out. Everything that happens between those two doors is invisible to the parent, which is the entire point - it is what makes the isolation benefit real rather than cosmetic. That same wall is the cost: the subagent knows only what the briefing says, and the parent knows only what the report says, so the quality of a delegation is bounded by the quality of both of those compressed artifacts, not by how good the subagent's actual work was.

## Self-check questions
1. A parent agent delegates "review this pull request" with no further detail. List three ways this briefing is underspecified, and for each, describe the kind of report failure it is likely to cause.
2. Explain, in your own words, why a parent cannot simply "ask the subagent to elaborate" the way it could ask a colleague a follow-up question mid-task. What structural property of the delegation boundary makes this hard?
3. Compare delegating a task to a subagent versus compacting the parent's own context (`prompting-context-engineering/10`) for the same underlying task: an agent needs to read and summarize twelve related config files scattered across a repo before making one small change. Which fits better, and what specifically about this task's shape drives that answer?
4. A subagent returns a confident, well-formatted report that turns out to be based on a misunderstanding of the briefing's scope. Whose failure is this most likely to be, and what change to the delegation would you make to reduce the chance of a recurrence?
5. Give one concrete example of work that looks delegable at first glance but actually needs to happen inside the parent's own context because the parent needs to see the subagent's reasoning, not just its conclusion.

## References
- Anthropic Engineering, "How we built our multi-agent research system" (June 2025) - https://www.anthropic.com/engineering/multi-agent-research-system
- Anthropic, "Effective context engineering for AI agents" (September 2025) - https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Claude Code Docs, "Subagents in the SDK" (2026) - https://code.claude.com/docs/en/agent-sdk/subagents
- ClaudeWorld, "Subagents & Context Isolation" (2026) - https://claude-world.com/tutorials/s04-subagents-and-context-isolation/
