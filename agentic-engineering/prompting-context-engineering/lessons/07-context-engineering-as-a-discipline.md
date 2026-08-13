---
id: prompting-context-engineering/07
subject: prompting-context-engineering
title: "Context Engineering as a Discipline: The Context Window as a Budget"
slug: context-engineering-as-a-discipline
status: drafted
mastery:
seniority: senior
source: "Anthropic docs: Effective context engineering for AI agents (2025); Sourcegraph blog: Context Engineering - A Practical Guide for AI Agents (2026); dbreunig.com: How Long Contexts Fail (2025); arXiv:2602.07962 LOCA-bench: Benchmarking Language Agents Under Controllable and Extreme Context Growth (2026); arXiv:2604.21816 Tool Attention Is All You Need (2026)"
durability: durable
prerequisites: [prompting-context-engineering/01]
created: 2026-08-10
updated: 2026-08-10
---

# Context Engineering as a Discipline: The Context Window as a Budget

## TL;DR
A context window is not a bucket you fill until it's full - it is a finite, shared resource where every token you add competes for the model's limited attention and pushes something else (cost, latency, focus) out. Context engineering is the discipline of deliberately deciding what earns a place in that budget, on every single turn, instead of defaulting to "include everything that might be relevant." This lesson is the pivot of the whole subject: lessons 01-06 were about crafting a good single prompt; from here on, the unit of engineering is the whole session.

## The idea
Lesson 01 established that a context window is finite - a fixed maximum number of tokens the model can attend to per call. It is tempting to treat "finite" as meaning "generous, and only relevant when you're close to the limit." That framing is the mistake this lesson corrects. A 200K-token or 1M-token window is not a warehouse where you're safe until the shelves are full; it behaves more like working memory or a fixed attention budget: everything you place in it competes for the same limited "attention" the model has to distribute across every token, and the model's ability to find and correctly weigh the one fact that matters degrades as the amount of surrounding, competing material grows - even when the window is nowhere near its hard limit.

This is why the framing shift matters. Prompt engineering (lessons 02-05) asks "how do I phrase this one request well?" Context engineering asks a structurally different question: "of everything I *could* put in front of the model on this turn - conversation history, tool outputs, retrieved documents, instructions, prior reasoning - what should actually be here, and what should I leave out, summarize, or fetch only when needed?" The second question does not exist for a single, one-shot prompt. It becomes unavoidable the moment you build an agent that runs many turns, calls tools, accumulates history, and has to keep making good decisions on turn 40 with the same discipline it had on turn 1.

Anthropic's engineering team, writing on this shift in 2025, frames context engineering as the natural evolution of prompt engineering: prompting cares about wording a single request, while context engineering cares about curating the entire set of tokens available to the model across a multi-step task - "finding the smallest possible set of high-signal tokens that maximize the likelihood of the desired outcome," not the largest set that fits.

## How it works

### Why "more context" is not free, even inside the limit
Three independent costs accrue with every added token, well before you hit the hard ceiling of the window:

1. **Attention dilution.** Transformer-based models compute attention over every token relative to every other token. As the volume of context grows, the "signal" of any one relevant fact gets diluted among the "noise" of everything else present, and empirically, model accuracy on needle-in-haystack-style retrieval and reasoning tasks measurably degrades as context grows - well before the token limit is reached, not just near it. This is sometimes called "context rot": longer contexts correlate with declining reliability of retrieval and reasoning, even when the needed information is technically present somewhere in the window.
2. **Latency and cost.** Every token in the context is a token the model has to process on every single call in that session, and in most pricing models, every token costs money whether or not the model ends up using it. A bloated context slows every subsequent turn and multiplies spend across a long-running session, not just the turn where the bloat was introduced.
3. **Distraction from the task at hand.** A large volume of tangentially relevant history can cause the model to pattern-match against past steps - repeating an earlier action, re-deriving an already-answered sub-question, or anchoring on stale information - rather than reasoning fresh about the current step. (This failure mode, along with poisoning and confusion, is covered in depth in lesson 08; the point here is only that it is a direct consequence of treating the window as unlimited.)

None of these costs require you to exceed the window's token limit to bite. This is the core reason "budget" is the right mental model and "bucket" is not: a bucket only matters when it overflows; a budget matters on every single allocation decision, because every token spent has an opportunity cost even when there's room left.

### The budget framing, concretely
Treat the context window the way you'd treat a fixed hourly meeting slot with a long agenda: you don't fill an hour just because you have an hour; you decide what earns the fifteen minutes it will take, and what gets a one-line summary, or gets skipped in favor of "read the doc yourself if you need it." Applied to an agent's context window, the recurring allocation questions on every turn are:

- **System/developer instructions** - almost always worth their token cost; they're read on every turn and shape everything else. But bloated, over-specified instructions (see lesson 02 for the anatomy) are still a cost, not a free good - a 3,000-token system prompt that repeats itself is 3,000 tokens not spent on something else.
- **Conversation/tool-call history** - the fastest-growing and most commonly over-included category. Not every prior tool result needs to stay verbatim in context forever; many are only relevant for the one or two turns immediately after they were fetched.
- **Retrieved documents** - worth including only the passages that are actually relevant to the current step, not an entire source document "just in case" (this tension is explored fully in lesson 09, on retrieval and memory).
- **Few-shot examples** (lesson 03) - valuable per-call, but each example has a real token cost; more examples is not automatically better once the marginal example stops changing behavior.

### Worked example: a token budget for a coding agent's single turn
Consider an agent with a 200K-token context window mid-way through a long coding task. Suppose the following demands compete for space on this one turn:

```
Item                                   Tokens    Notes
------------------------------------------------------------------
System prompt + tool definitions        8,000    fixed cost, every turn
Full conversation history so far      140,000    30 turns of raw tool output
Current file being edited                3,000    directly relevant
Retrieved "similar past bug" doc        12,000    marginal relevance
Test suite output (full, verbose)       25,000    mostly noise, one failure matters
------------------------------------------------------------------
Total if everything is kept            188,000    94% of the 200K window
```

At 188K of 200K tokens, you are not "safe because you're under the limit." You are one more multi-thousand-token tool result away from truncation forcing an unplanned drop of *something*, and worse, per the attention-dilution point above, the model's ability to find the one line in that 140,000-token history that actually matters for the next decision is already measurably worse than it would be with a tighter, curated context. A context-engineering pass over the same turn might look like:

```
Item                                   Tokens    Decision
------------------------------------------------------------------
System prompt + tool definitions        8,000    keep as-is
Conversation history                   15,000    summarized: prior turns
                                                  compacted to decisions +
                                                  outcomes, not raw output
Current file being edited                3,000    keep, directly relevant
Retrieved "similar past bug" doc            0    dropped: not relevant to
                                                  the current failing test
Test suite output                        2,000    keep only the failing
                                                  test's stack trace, not
                                                  the full green-test log
------------------------------------------------------------------
Total                                   28,000    14% of the 200K window
```

Same window, same model, radically different amount of "signal per token" - and, per the studies on context-length-correlated accuracy decline, a materially better chance the model correctly weighs the one failing test that actually matters for the next step. The fix was not a bigger window; it was refusing to spend the window on things that weren't earning their place.

### Worked example: why "just use a bigger context window" doesn't solve this
It's tempting to treat context engineering as a problem that model providers will solve by shipping ever-larger windows.

> **Example (Aug 2026):** context windows across major providers as of mid-2026 commonly range from roughly 128K to 1M+ tokens depending on model and tier, and some vendors offer this at standard per-token pricing with no long-context premium. Check current vendor docs for exact numbers and pricing - they change every few months.

A bigger window changes the point at which the *hard* ceiling truncates your context; it does not change the *soft* degradation from attention dilution, and it does not change the per-token latency and cost of every call. Moving from a 200K to a 1M window means you can now technically fit five times as much - it does not mean you should, and empirically, stuffing a 1M window with everything you have available tends to reproduce the same degraded-accuracy pattern at a larger scale, not eliminate it. The budget discipline does not go away as windows grow; if anything it becomes more important, because the temptation to stop curating grows right along with the room to be lazy.

### The recurring allocation loop
Concretely, context engineering as a discipline means running this loop on every turn of a long-running agent, not once at the start of a session:

```
Before each model call:
  1. What does the model actually need to make THIS decision well?
  2. Of what's currently in context, what's stale, redundant, or
     no longer load-bearing for the current step?
  3. Can stale material be summarized/compacted instead of kept
     verbatim? (full technique in lesson 10)
  4. Is there something the model needs that ISN'T in context yet,
     and should be fetched now rather than kept "just in case"
     for the whole session? (retrieval strategy, lesson 09)
  5. Allocate the remaining budget to what earns it; drop the rest.
```

This loop is why context engineering is described as a discipline rather than a technique: it is a standing practice applied on every turn of a session, not a one-time setup step you configure and forget.

## Pros
- **Directly improves reliability**, not just cost - curated context measurably reduces the attention-dilution and distraction failure modes that raw token-limit headroom does nothing to prevent.
- **Reduces latency and spend simultaneously** with the reliability gain, since fewer tokens processed per call is strictly cheaper and faster, not a trade-off against quality when done well.
- **Scales to long-horizon tasks.** Sessions that would otherwise degrade over dozens of turns (context rot) can run much longer when context is actively managed rather than left to accumulate.
- **Forces explicit reasoning about information architecture** - what actually matters for a decision - which tends to surface design flaws (redundant tool calls, over-verbose tool outputs) that would otherwise hide inside "the model will figure it out."

## Cons
- **Real engineering overhead.** Deciding what to keep, summarize, or drop on every turn is nontrivial work compared to "just append everything," and getting it wrong (dropping something that turns out to matter) creates its own failure mode.
- **Summarization/compaction introduces its own risk of information loss** - a badly compacted summary can silently drop the one detail that mattered, which is harder to detect than an obviously truncated context (full treatment in lesson 10).
- **No universal recipe.** What's "signal" versus "noise" is task-specific and often only obvious in hindsight; a generic context-budgeting policy tuned for one agent can under- or over-prune for a different one.
- **Easy to over-invest early.** For short, simple, few-turn tasks, aggressive context curation is often unnecessary complexity - see "When NOT to use it."

## Alternatives
- **Just use a larger context window and include everything** - simpler to build, and adequate for short sessions or low-stakes tasks where attention dilution and cost don't yet matter. Fails as sessions get longer or higher-stakes, per the worked examples above.
- **Fixed truncation (drop oldest N tokens when near the limit)** - cheaper to implement than deliberate curation, but indiscriminate: it can just as easily drop something load-bearing as something irrelevant, with no judgment about which is which. Reasonable as a last-resort safety net, not as a primary strategy.
- **Retrieval-augmented generation** (lesson 09) - a specific context-engineering technique for the "what to fetch" half of the loop above; not a replacement for the budgeting discipline as a whole, since retrieved content still has to compete for the same finite space once fetched.
- **Fine-tuning the model on domain knowledge** - moves some information out of context entirely and into the model's weights, reducing the per-call budget pressure for that information. Preferable for stable, high-volume, unchanging knowledge; unhelpful for information that changes turn to turn (current file state, live tool results), which is most of what fills an agent's context in practice.

## When to use it
Apply context-engineering discipline to any agent or workflow that runs multiple turns, calls tools repeatedly, accumulates conversation history, or operates over a long horizon (many minutes to hours of autonomous operation). The longer or more autonomous the session, the more the budget discipline pays for itself - this is exactly the regime where "just include everything" silently degrades without an obvious error message telling you it happened.

## When NOT to use it
Skip heavy context-curation machinery for short, single- or few-turn interactions where the full available context is small relative to the window and the session ends before accumulation becomes a problem - a one-shot classification call or a short Q&A exchange doesn't need a compaction strategy. Building summarization pipelines and retrieval gating for a task that completes in three turns is over-engineering; save that investment for sessions that are actually long-horizon.

## Key takeaways / mental model
Stop picturing the context window as a bucket with a fill line ("we're fine, we're under the limit"). Picture it as a budget you allocate every turn, where every token included is a token that (a) cost money and latency to process, (b) diluted the model's attention away from every other token, and (c) has to be actively worth that cost - not merely "possibly relevant." The recurring question is not "does this fit?" but "does this earn its place, right now, for this decision?" Everything else in this subject from here on - failure modes (08), retrieval and memory (09), compaction and handoff (10) - is a specific technique for answering that question well.

## Self-check questions
1. Explain, without using the word "limit," why a context window at 40% capacity can still produce worse agent performance than the same window at 15% capacity with more carefully chosen content.
2. Your agent's context window has grown to 90% full after 25 turns of a long debugging session, and the model just repeated a diagnostic step it already ran on turn 6. Using the concepts in this lesson, describe what's likely happening and what you'd do about it before the next turn.
3. A colleague argues "we should just upgrade to the model with the 1M-token window and stop worrying about context curation." Give the strongest counter-argument using the cost categories from this lesson.
4. Walk through the five-step allocation loop for a customer-support agent about to respond to message 12 in a long support thread that includes several resolved side-issues from earlier in the conversation. What would you keep, summarize, and drop?
5. Design a rough token budget (like the worked examples in this lesson) for a research agent that has: a 6,000-token system prompt, 50,000 tokens of accumulated web-search results from earlier steps, a 20,000-token document it just needs to answer one question, and a 400K-token context window. What would you include as-is, summarize, or drop, and why?

## References
- [Anthropic docs: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Sourcegraph blog: Context Engineering - A Practical Guide for AI Agents (2026)](https://sourcegraph.com/blog/context-engineering)
- [dbreunig.com: How Long Contexts Fail](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html)
- arXiv:2602.07962 - LOCA-bench: Benchmarking Language Agents Under Controllable and Extreme Context Growth
- arXiv:2604.21816 - Tool Attention Is All You Need: Dynamic Tool Gating and Lazy Schema Loading for Eliminating the MCP/Tools Tax in Scalable Agentic Workflows
