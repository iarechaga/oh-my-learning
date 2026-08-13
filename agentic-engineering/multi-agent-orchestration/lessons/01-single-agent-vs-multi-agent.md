---
id: multi-agent-orchestration/01
subject: multi-agent-orchestration
title: "Single-Agent vs Multi-Agent: When Splitting Actually Helps"
slug: single-agent-vs-multi-agent
status: drafted
mastery:
seniority: mid
source: "Anthropic Engineering, How we built our multi-agent research system (Jun 2025); Anthropic/Claude blog, When to use multi-agent systems (and when not to) (2026); arXiv:2604.02460, Single-Agent LLMs Outperform Multi-Agent Systems on Multi-Hop Reasoning Under Equal Thinking Token Budgets (2026); arXiv:2605.09104, Token Economics for LLM Agents: A Dual-View Study from Computing and Economics (2026)"
durability: durable
prerequisites: [tool-use-agentic-loop/03]
created: 2026-08-10
updated: 2026-08-10
---

# Single-Agent vs Multi-Agent: When Splitting Actually Helps

## TL;DR
Splitting a task across multiple agents is not a free upgrade over a single agentic loop (`tool-use-agentic-loop/03`) - it trades a large, predictable increase in token cost and coordination complexity for two specific benefits: context isolation (each agent's working memory stays clean and focused) and true parallelism (independent lines of work happen simultaneously instead of serially). Whether that trade is worth making depends entirely on whether the subtasks are genuinely independent; when they are not, multiple agents are strictly worse than one.

## The idea
A single agentic loop already handles a huge range of tasks: it plans, acts, observes, and repeats within one continuously accumulating context. The question this lesson answers is when it stops being enough - and the honest answer is: less often than the volume of multi-agent tooling and hype in 2025-2026 would suggest.

The temptation to reach for multiple agents is understandable. A single agent's context window is finite, and a single agent can only do one thing at a time. Multiple agents seem to solve both problems at once: split the context, split the work. But every agent you add is not a free helper - it is a full additional model invocation with its own prompt, its own reasoning tokens, and its own results that someone (a human, or another agent) has to read, reconcile, and act on. The real design question is not "would more agents help," which is almost always true in isolation for some narrow slice of the problem, but "does the benefit of splitting exceed the compounding cost of coordinating," which is true far less often than intuition suggests.

## How it works

### The two genuine benefits of splitting
**Context isolation.** A single agent's context is one continuously growing history - everything it has read, tried, and observed stays in that one window, and per `prompting-context-engineering/10`, an overloaded context degrades quality (distraction, confusion, occasionally poisoning). Splitting a task across agents means each agent gets its own clean context, scoped only to its piece of the problem. A subagent investigating "does library A support feature X" never has to carry the token weight of libraries B and C's investigations, and never has its judgment on A clouded by irrelevant detail from the others.

**Parallelism.** A single agentic loop is fundamentally serial: plan, act, observe, plan, act, observe - one step waits for the previous one's result. Multiple agents working on genuinely independent subtasks can run those subtasks concurrently, turning wall-clock time that would have been additive (do A, then B, then C) into something closer to the time of the slowest single piece.

### The two real costs of splitting
**Token and dollar cost multiply, they do not just add.** Anthropic's own published measurements from building a production multi-agent research system found that agents in general already run about 4x the token cost of a plain chat interaction (because of tool-call round trips and accumulated context), and a multi-agent system running several such agents in parallel ran at roughly 15x the token cost of a single chat interaction. That is not a rounding error - it means a multi-agent architecture is only economically sound for tasks whose value clearly justifies an order-of-magnitude cost increase over a single agent, not for routine work.

**Coordination overhead grows with the number of agents, and it is not just a token cost.** Someone has to decide how to split the task, write a clear enough brief for each agent that it does not duplicate or miss work, and then reconcile the returned results into one coherent answer. Anthropic's write-up on their research system is candid about the early failure modes this produces in practice: agents spawning far more subagents than a query warranted (fifty-plus for questions that needed a handful), agents duplicating each other's work because task boundaries were vague, and agents burning budget searching for sources that did not exist. None of these are token-cost problems in the narrow sense - they are coordination-design problems that only exist because more than one agent is involved.

### The load-bearing test: are the subtasks actually independent?
This is the single most important diagnostic in this lesson, and it comes directly from what practitioners have found in production. Splitting only pays off when the subtasks are genuinely independent - each one can be completed using only the information it starts with, without needing an intermediate result from a sibling subtask. When that independence is real, parallel agents each explore their own slice and the wins (isolation, wall-clock speedup) are real and large. When it is not real - when subagent B actually needs subagent A's finding to do its job correctly - splitting does not remove the dependency, it just adds an expensive detour: B either has to guess, wait idly for A while still being billed as a running agent, or the whole system falls back to a serial hand-off between agents that is strictly worse than one agent doing both steps in the same context, because now there is also a briefing/handoff cost (`prompting-context-engineering/10`) layered on top of the serial work.

### Worked example: a research query that splits cleanly
Consider the task "compare how library A, library B, and library C each handle connection pooling, and recommend one." The three sub-questions ("how does A handle pooling," "how does B," "how does C") are independent of each other - answering the question about B requires nothing that comes out of investigating A. A single agent doing this serially would read A's docs, read B's docs, read C's docs, one after another, in one accumulating context that now holds three libraries' worth of implementation detail it has to hold onto simultaneously to write the final comparison. A multi-agent split - one subagent per library, each returning a short structured summary of just that library's pooling behavior - runs the three investigations concurrently, keeps each subagent's context focused on exactly one library, and hands the lead agent three clean summaries to synthesize instead of three libraries' worth of raw exploration noise. This is close to the ideal case: independent subtasks, parallelism available, and a natural isolation boundary.

### Worked example: a task that looks splittable but is not
Consider "debug why this checkout flow intermittently loses items from the cart." A tempting split: one agent investigates the frontend cart state, one investigates the backend session storage, one investigates the payment webhook handler. This looks parallel - three components, three agents - but the actual bug lives in the interaction between them, and no agent knows which component is at fault until it has seen what the others found. The frontend agent might report "cart state looks correct on submit," the backend agent might report "session storage looks correct," and the webhook agent might report "webhook payload looks correct" - three true, locally-correct findings that do nothing to explain the intermittent loss, because the actual defect is a race condition across the boundary between two of them. A single agent (or, per `multi-agent-orchestration/02`, one agent that sequentially delegates a scoped investigation once it has a specific hypothesis) that reads across all three components in one continuous context, able to notice "the frontend submits before the backend session write completes" only because it can compare both pieces of evidence side by side, will find this bug faster than three isolated agents each convinced their own piece is fine. This is the pattern Anthropic's own guidance calls out explicitly: work requiring heavy dependencies between agents, including most debugging and most coding tasks, is a poor fit for multi-agent splitting.

### A simple decision framework
Given a candidate task, ask, in order:
1. **Would a single agent's context become genuinely overloaded** (too much unrelated detail to hold at once) if it did the whole task itself? If not, you likely do not need to split at all - the isolation benefit is not buying you anything a single well-managed context (`prompting-context-engineering/10`) does not already handle.
2. **Are the candidate subtasks actually independent** - can each be completed correctly without an intermediate result from another? If any subtask needs another's output mid-flight, splitting adds coordination cost without removing the dependency; keep it in one context or use a deliberate serial hand-off, not parallel agents.
3. **Does the task's value justify roughly an order of magnitude more tokens** than a single agent would spend? If the task is routine, low-stakes, or cheap to redo if wrong, the 15x-ish cost multiplier from parallel multi-agent execution is very likely not worth paying.
4. Only if the answers are "yes, genuinely overloaded," "yes, genuinely independent," and "yes, worth the cost" does splitting across agents clear the bar.

## Pros
- Keeps each agent's working context focused and uncluttered, which improves the quality of that agent's own reasoning on its slice of the problem.
- Enables real wall-clock parallelism on tasks with genuinely independent subtasks, which a single serial loop structurally cannot provide.
- Scales naturally to breadth-first tasks (many independent things to check) in a way a single agent's serial loop does not.

## Cons
- Multiplies token and dollar cost by roughly an order of magnitude versus a single agent, per published production measurements - not a marginal increase.
- Adds real coordination overhead: task decomposition has to be deliberate, briefs have to be specific enough to avoid duplication or gaps, and results have to be reconciled by someone.
- Actively hurts on tasks with real cross-subtask dependencies - splitting does not remove a dependency, it just adds a detour and a rejoining cost on top of it.
- Introduces new failure surface unique to having multiple agents at all (covered fully in `multi-agent-orchestration/06`): redundant work, agents talking past each other, and results that individually look correct but collectively miss the real problem.

## Alternatives
- **Single agentic loop** (`tool-use-agentic-loop/03`) — the default; stays the right choice for any task whose subtasks are not genuinely independent, or whose value does not clearly justify a large cost multiplier.
- **Single agent with sequential subagent delegation** (`multi-agent-orchestration/02`) — one agent that delegates a scoped, isolated piece of work to a subagent and waits for its result before continuing, rather than running many agents concurrently; captures the context-isolation benefit without requiring true independence between every subtask.
- **Single agent with retrieval or memory** (`prompting-context-engineering/09`) — extends one agent's effective reach without adding another agent at all, appropriate when the problem is really "too much information to hold at once" rather than "genuinely separable lines of work."

## When to use it
Reach for multiple agents when a task decomposes into subtasks that are genuinely independent of each other, the task is high-value enough to justify roughly an order-of-magnitude increase in token cost over a single agent, and either parallel wall-clock speed or clean context isolation per subtask would provide a real, measurable benefit - breadth-first research across several unrelated sources being the clearest recurring example.

## When NOT to use it
Do not split when the subtasks have real dependencies on each other's intermediate results (most debugging, most single-codebase coding tasks, anything where an early finding should change how a later step proceeds) - splitting there adds cost and coordination overhead while doing nothing to remove the dependency, and often produces confidently wrong answers from agents that each only saw part of the picture. Do not split for routine or low-stakes tasks where a single agent's context was never going to be a real constraint - the cost multiplier is not justified by the marginal quality gain.

## Key takeaways / mental model
More agents is not more capability by default - it is a specific trade: real isolation and real parallelism, purchased at a real and large cost in tokens, dollars, and coordination complexity. The trade only pays off when subtasks are genuinely independent; when they are not, splitting does not remove the dependency between them, it just adds an expensive layer of hand-offs on top of it. Before adding a second agent to anything, ask whether the subtasks could truly be completed in isolation from each other - if the honest answer is no, the fix is better context management within one agent, not more agents.

## Self-check questions
1. A teammate proposes splitting "summarize this quarter's five biggest customer complaints from support tickets" into five parallel agents, one per complaint category. Walk through the decision framework above and decide whether this splits well, and why.
2. Using the checkout-bug worked example, explain specifically why three agents each returning "my component looks fine" can all be individually correct and still collectively fail to find the bug. What single-agent behavior would have caught it?
3. A single agent is not overloaded (its context is well within budget) but the task has four genuinely independent sub-investigations with generous time pressure to finish fast. Would you split it anyway? Justify your answer against the decision framework's four questions.
4. Anthropic's published numbers put multi-agent token cost at roughly 15x a single chat interaction. Describe a concrete task where you would judge that multiplier worth paying, and one superficially similar task where you would not, and explain what specifically differs between them.
5. A task looks independent on the surface (three components to check) but you suspect the real defect might be an interaction between components. What would you look for, before committing to a multi-agent split, to test whether that suspicion is right?

## References
- Anthropic Engineering, "How we built our multi-agent research system" (June 2025) - https://www.anthropic.com/engineering/multi-agent-research-system
- Claude by Anthropic, "When to use multi-agent systems (and when not to)" (2026) - https://claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them
- "Single-Agent LLMs Outperform Multi-Agent Systems on Multi-Hop Reasoning Under Equal Thinking Token Budgets," arXiv:2604.02460 (2026) - https://arxiv.org/pdf/2604.02460
- "Token Economics for LLM Agents: A Dual-View Study from Computing and Economics," arXiv:2605.09104 (2026) - https://arxiv.org/html/2605.09104v1
