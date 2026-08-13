---
id: prompting-context-engineering/08
subject: prompting-context-engineering
title: "Context Failure Modes: Poisoning, Distraction, and Confusion"
slug: context-failure-modes
status: drafted
mastery:
seniority: senior
source: "Drew Breunig, How Long Contexts Fail and How to Fix Them (dbreunig.com, Jun 2025); Anthropic, Effective context engineering for AI agents (Sep 2025); Laban et al., LLMs Get Lost In Multi-Turn Conversation, arXiv:2505.06120 (May 2025); Berkeley Function-Calling Leaderboard (ongoing, referenced 2025)"
durability: durable
prerequisites: [prompting-context-engineering/07]
created: 2026-08-10
updated: 2026-08-10
---

# Context Failure Modes: Poisoning, Distraction, and Confusion

## TL;DR
A long or cluttered context window does not fail silently in one uniform way - it fails through at least four distinct, nameable mechanisms: poisoning (bad information gets echoed forward), distraction (too much history crowds out trained behavior), confusion (irrelevant content gets used anyway because it's there), and clash (new information contradicts old information already in context). Naming the mechanism tells you which fix applies; treating "the context is too long" as one undifferentiated problem leads to the wrong fix.

## The idea
Lesson 07 established that the context window is a finite, per-turn budget, not an unlimited scratchpad. This lesson is about what actually goes wrong when that budget is mismanaged. "The agent got worse as the conversation went on" is a symptom, not a diagnosis. Four different underlying causes can produce that symptom, and each one demands a different fix:

- If a **hallucination** got written into the context and the agent keeps citing it, more context will not help - you need to catch and remove the bad claim (poisoning).
- If the context is simply **too voluminous**, relative to what the model was trained to attend to at that length, the fix is to shrink it (distraction).
- If the context contains **content the model doesn't need** for the current step but still "sees," the fix is to prune it, not to add clarifying instructions on top (confusion).
- If the context contains **two things that disagree**, the fix is to resolve or remove the contradiction, not to add more content hoping the model picks the right one (clash).

This taxonomy - poisoning, distraction, confusion, clash - was named and popularized by practitioner Drew Breunig in mid-2025, synthesizing patterns independently documented by model vendors (notably Google's Gemini 2.5 technical report) and academic benchmarks. It has since become common vocabulary in context-engineering discussions. The names are not officially standardized across every vendor, but the underlying mechanisms are real, reproducible, and durable regardless of which vendor's terminology you use.

## How it works

### Context poisoning: an error that gets re-referenced
Poisoning happens when a hallucination or factual error enters the context - typically written there by the model itself, in a summary, a "current goals" field, or a memory note - and then gets treated as ground truth on every subsequent turn, because the model has no mechanism to distinguish "something I asserted earlier" from "something that is actually true."

**Worked example.** Google's Gemini 2.5 technical report documented this directly in an agent that played Pokemon over an extended session. The agent maintained a running "goals and summary" section of its own context, regenerated each turn from its own prior state. At some point the agent hallucinated an incorrect belief about the game state (e.g., believing it had already obtained an item it had not) and wrote that belief into its persistent summary. On every subsequent turn, the agent re-read its own summary, treated the false claim as established fact, and used it to justify further actions - including, in observed cases, pursuing goals that were now impossible given the (real) game state. The agent didn't just make one bad move; it built an increasingly elaborate plan on top of a false premise, because the false premise was sitting in the same context slot as true premises, with no marker distinguishing them.

**Why more context doesn't fix it.** You cannot out-context a poisoned claim. Feeding the agent more correct information doesn't overwrite the false belief sitting in its summary - the model still re-reads and re-trusts its own prior assertion unless something actively intervenes (a human correction, a validation step that flags the contradiction, or a compaction pass that drops the false claim rather than carrying it forward).

**Mitigation pattern:** validate before persisting (don't let unverified model output become "memory" without a check), keep provenance on claims that get carried across turns (was this observed, or asserted by the model?), and treat compaction/summarization as an opportunity to drop suspect claims rather than dutifully preserve everything including the errors.

### Context distraction: history crowds out training
Distraction happens when the sheer volume of accumulated context causes the model to lean on pattern-matching against its own recent history instead of synthesizing a fresh plan the way its training would otherwise produce. The model isn't confused about facts - it's over-anchored on "what have I been doing" rather than "what should I do."

**Worked example with numbers.** In the same Gemini-plays-Pokemon setting, researchers observed that once the accumulated context passed roughly 100,000 tokens, the agent showed a measurable shift: it began favoring repetition of actions drawn from its own extensive action history over generating novel plans appropriate to the current situation - even when the current situation called for something new. Separately, Databricks' long-context research found that task correctness for Llama 3.1 405B began degrading around the 32,000-token mark on certain tasks, well short of that model's stated context window. The pattern generalizes: a model's *usable* context (where behavior stays reliable) is typically much shorter than its *advertised* context window, and smaller models hit their distraction ceiling earlier than larger ones. This is sometimes called "context rot" - not a hard cliff, but a gradient where recall precision and reasoning quality degrade as token count climbs, even well inside the advertised limit.

**Mitigation pattern:** compact or summarize before you approach the model's *effective* usable length (not its advertised maximum), prefer fresh context via sub-agent delegation for genuinely new subtasks (lesson 10), and treat "the window still has room" as a weak signal - track effective degradation, not just remaining token budget.

### Context confusion: irrelevant content still gets used
Confusion happens when content that is not relevant to the current step is nonetheless present in the context, and the model uses it anyway - not because it's wrong to do so, but because attention doesn't have a clean way to fully ignore something that's sitting right there. If you put something in the context, the model has to pay some attention to it, whether or not that attention helps.

**Worked example with numbers.** The Berkeley Function-Calling Leaderboard, which tests models' ability to select and call the correct tool from a list, consistently shows every model's accuracy degrading as the number of available tools grows - even when the extra tools are irrelevant to the task and the context window has ample room for all of them. A sharper case: a quantized Llama 3.1 8B model was tested on the GeoEngine benchmark with a full toolset of 46 available tools, and failed; the same model, given a pruned set of only the 19 tools actually relevant to the benchmark's tasks, succeeded - despite having more than enough context window to hold all 46 either way. The failure wasn't a capacity problem. It was that the extra 27 irrelevant tool definitions, simply by being present, pulled the model toward wrong or malformed tool calls.

**Why this differs from distraction.** Distraction is about *volume relative to training*; confusion is about *relevance*. You can trigger confusion with a short context if enough of it is irrelevant to the current step - a 5,000-token context with 4,000 tokens of unrelated tool schemas can confuse a model that would do fine with a 5,000-token context that's all on-topic.

**Mitigation pattern:** dynamic/just-in-time tool loading (only expose the tools relevant to the current step, not the agent's full toolset at all times), scope retrieval tightly rather than broadly, and resist the instinct to "just include it, more information can't hurt" - it can.

### Context clash: new information contradicts old information
Clash happens when information added later in the context conflicts with information already present, and the model has to somehow reconcile - or, more often, fails to cleanly reconcile - the contradiction. Unlike poisoning (one false thing repeated) or confusion (irrelevant clutter), clash is specifically about two *present, in-context* pieces of information disagreeing with each other.

**Worked example with numbers.** A 2025 study from Microsoft Research and Salesforce Research (Laban et al., "LLMs Get Lost In Multi-Turn Conversation," arXiv:2505.06120) took single-prompt benchmark tasks and converted them into multi-turn conversations, where the full task specification arrived incrementally across several turns rather than all at once - deliberately creating opportunities for early assumptions to clash with later clarifications. Across 15 models from eight vendors and over 200,000 simulated conversations, performance dropped by an average of 39% compared to the single-turn version of the same tasks. The drop was sharpest for OpenAI's o3, which fell from 98.1% in single-turn to 64.1% in multi-turn - on tasks that were, in principle, identical. The paper's diagnosis: models tend to commit to an assumption early (based on an incomplete initial specification), attempt a premature final answer built on that assumption, and then fail to cleanly revise when a later turn's information contradicts it. The model doesn't lose competence so much as it loses reliability - it "gets lost" and does not recover within the conversation.

**Why this matters for agents specifically.** Multi-turn clash is not a hypothetical for agentic workflows - it's close to the default shape of a long-running agent session, where the user, the tool outputs, and the agent's own prior turns keep adding information over time. An agent that commits early to a plan based on incomplete information, then receives a tool result that contradicts that plan, is exactly the clash scenario from the paper.

**Mitigation pattern:** where feasible, front-load complete specifications rather than dribbling requirements across turns; when contradictions are detected, prefer explicit resolution (state the contradiction, ask, or overwrite the stale claim) over silently appending the new information and hoping the model weighs it correctly; and treat "conversation continues indefinitely in one context" as a design smell for tasks where requirements are likely to evolve - starting a fresh, re-specified context can outperform patching an old one (this connects directly to compaction and handoff, lesson 10).

### Telling the four apart in practice
A simple diagnostic: ask what changes if you remove the suspect content.
- Remove a specific false claim and behavior corrects itself -> **poisoning**.
- Remove *volume* (shrink everything proportionally) and behavior corrects itself -> **distraction**.
- Remove specific *irrelevant* items (not false, just off-topic) and behavior corrects itself -> **confusion**.
- The content that's causing trouble is two true-at-different-times statements that disagree -> **clash**.

These are not mutually exclusive within one bad session - a long-running agent can accumulate a poisoned claim, an overgrown history, an oversized toolset, and a stale assumption all at once. Diagnosing which one dominates the current failure is what determines whether you compact, prune, validate, or re-specify.

## Pros
- Gives you a shared, precise vocabulary for what would otherwise be a vague "the agent got dumber" complaint, which makes the failure debuggable instead of mysterious.
- Each failure mode implies a specific, different fix, so correct diagnosis directly shortens the path to a working mitigation.
- The taxonomy is grounded in reproducible, cross-vendor evidence (leaderboards, published technical reports, controlled benchmarks), not folklore.

## Cons
- The taxonomy is descriptive, not a detector - nothing automatically tells you which failure mode you're looking at; you still have to do the diagnostic work (see "telling the four apart," above).
- Real failures are frequently mixed (a bit of distraction plus a bit of confusion), and treating them as cleanly separable can lead to over-engineering a fix for the wrong dominant cause.
- The specific thresholds (100k tokens, 32k tokens, 46 vs 19 tools) are measurements from specific models and benchmarks at a point in time; they illustrate the *shape* of the problem, not universal constants for every model.

## Alternatives
- **Treat it as one undifferentiated "context is too long" problem and just truncate or summarize everything uniformly.** Simpler to implement, but it wastes effort compacting content that wasn't the actual problem (e.g., aggressively summarizing a short, clean context to fix what was actually a tool-clash issue) and can accidentally discard the one piece of information that would have resolved a clash.
- **Rely purely on bigger context windows / better base models to "solve" this by brute force.** Newer, larger models do push the distraction and confusion thresholds later, but published context-rot research shows the gradient persists well inside advertised limits even for frontier models as of 2025-2026 - it is a shifted curve, not an eliminated one.
- **Vendor-specific "context health" tooling** (dashboards or evals that flag degraded recall at length) - useful as instrumentation, but this is a perishable, product-specific implementation of the same durable diagnostic idea described here; see the domain's `landscape-snapshot` subject for what exists concretely as of a given date.

## When to use it
Use this taxonomy any time an agent's behavior degrades over the course of a session and you need to decide *what to fix* rather than just "add more instructions and hope." It's especially valuable for debugging long-running agentic sessions, tool-heavy agents with large toolsets, and any workflow where information arrives incrementally across turns (which is most real agentic workflows).

## When NOT to use it
Don't reach for this taxonomy as a substitute for basic prompt debugging on short, single-turn tasks - if a one-shot prompt with a 500-token context fails, the problem is much more likely to be prompt clarity or a genuine model capability gap (see lesson 06) than any of these four context-scale failure modes, which all require some accumulation of context to manifest.

## Key takeaways / mental model
Ask "what changed, and what would removing it fix?" before reaching for "make the context bigger" or "make the context smaller" as a blanket move:
- **Poisoning** - a false claim is being echoed. Fix: validate and excise, don't just add more.
- **Distraction** - there's too much history relative to what the model can still use well. Fix: compact or delegate to fresh context.
- **Confusion** - irrelevant content is present and gets used anyway. Fix: prune to relevance, load just-in-time.
- **Clash** - two things in context disagree. Fix: resolve or remove the contradiction explicitly; don't let it ride.

## Self-check questions
1. An agent working a multi-hour research task starts citing a source that does not actually exist in any of its retrieved documents, and keeps citing it in later steps. Which failure mode is this, and what's the first thing you should check before deciding on a fix?
2. Your agent has a 200,000-token context window, and the session is only 40,000 tokens in, but tool-selection accuracy has already visibly dropped. Why might "the context window isn't full yet" be the wrong frame here, and what would you check instead?
3. A user provides a task specification across five separate messages, adding a new constraint each time. By message five, the agent's plan still reflects assumptions from message one and never incorporated the constraint added in message three. Name the failure mode and propose two different mitigations - one that changes how the user should have specified the task, one that changes how the agent should handle it.
4. You're debugging a degraded agent session and you suspect either distraction or confusion, but you're not sure which. Describe a controlled experiment (what you'd change and hold constant) that would let you tell them apart.
5. Why does "just give the model a bigger context window" fail to fully solve distraction, confusion, and clash, even though it plausibly helps with situations that look like poisoning (more room to include corrective information)?

## References
- Drew Breunig, "How Long Contexts Fail and How to Fix Them" (dbreunig.com, June 2025) - https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html
- Anthropic, "Effective context engineering for AI agents" (September 2025) - https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Laban et al., "LLMs Get Lost In Multi-Turn Conversation," arXiv:2505.06120 (May 2025) - https://arxiv.org/abs/2505.06120
- Berkeley Function-Calling Leaderboard - https://gorilla.cs.berkeley.edu/leaderboard.html
