---
id: instruction-and-context-design/03
subject: instruction-and-context-design
title: "Always-Loaded vs On-Demand: Drawing the Line in a System Prompt"
slug: always-loaded-vs-on-demand
status: drafted
mastery:
seniority: mid
source: "Anthropic engineering blog: Effective context engineering for AI agents (2025); Anthropic platform docs: Agent Skills overview (2026); Anthropic platform docs: Skill authoring best practices (2026); explainx.ai: Steering Claude Code - All 7 Instruction Methods Explained (2026)"
durability: durable
prerequisites: [instruction-and-context-design/01, prompting-context-engineering/07]
created: 2026-08-10
updated: 2026-08-10
---

# Always-Loaded vs On-Demand: Drawing the Line in a System Prompt

## TL;DR
Every piece of instruction content an agent might need falls into one of two regimes: permanently resident in context (paid for on every single turn, guaranteed present) or deferred and fetched only when relevant (paid for only on the turns that need it, never guaranteed present unless something correctly decides to fetch it). Neither regime is free, and the decision of where to draw the line - what's important and universal enough to always pay for, versus what's rare or narrow enough to defer - is one of the highest-leverage design choices in building an agent's scaffolding.

## The idea
Lessons 01 and 02 set up the pieces: instructions live on distinct surfaces (01), and structured metadata is what makes deferring a surface's full content practical (02). This lesson is about the actual decision those pieces exist to support: for any given piece of guidance, should it be always-loaded or on-demand? This is not a technical question about which mechanism to use - it's a judgment call about a trade-off that the prerequisite context-engineering lesson already named: always-loaded content is guaranteed present but taxes every turn forever; on-demand content is free until needed but depends on a correct triggering decision (lesson 04) to ever show up at all.

Get the line wrong in one direction and you bloat every session with content most turns never use, reproducing the exact "context as bucket, not budget" mistake prompting-context-engineering/07 warns against. Get it wrong in the other direction and you create silent gaps: an agent that needed a piece of guidance on turn one, before anything had triggered its loading, and simply didn't have it - a failure with no error message, because from the model's perspective there was nothing to be wrong about; it never knew the content existed to be missing. Drawing this line well is the central design skill this whole subject builds toward across lessons 04-11.

## How it works

### The two costs, stated precisely
Always-loaded content costs `tokens_per_item * number_of_turns_in_session`, recurring every single call regardless of whether that turn needs it. On-demand content costs `token_size_of_body` only on the (hopefully rare) turns where it's actually triggered, plus a small fixed cost for its metadata (lesson 02) on every turn while it remains a candidate - but it costs *zero times the guarantee it will be there when needed*, because that guarantee depends entirely on the triggering mechanism working correctly (lesson 04) and on the underlying assumption holding: that the content genuinely isn't needed until some detectable signal appears.

This second cost - the reliability cost of deferral - is easy to under-weight because it doesn't show up as a token count. It shows up as an intermittent, hard-to-reproduce failure: the agent behaves correctly nineteen times out of twenty because the trigger correctly fires, and on the twentieth, phrased slightly differently, it doesn't, and the agent silently proceeds without guidance nobody would have called optional.

### A worked decision procedure
Given a candidate piece of guidance, three questions in sequence do most of the work of deciding where it belongs:

```
1. Does the agent need this on the FIRST turn it could possibly
   be relevant, before any tool call or user turn could serve as
   a trigger? --> if yes, strongly favor always-loaded. There is
   no "turn zero" trigger to defer to.

2. Is this needed on most sessions/turns of this agent's typical
   use, or a small minority? --> majority favors always-loaded
   (the deferred mechanism's fixed overhead per trigger isn't
   worth it if it fires almost every time anyway); minority
   favors on-demand.

3. Is the consequence of the agent NOT having this when it's
   actually needed severe (safety, data loss, a rule that must
   never be silently skipped) or merely suboptimal (a nicer
   phrasing, a faster but non-critical procedure)?
   --> severe pushes toward always-loaded, OR toward a
   deterministic surface outside model judgment entirely (a
   hook, lesson 10) rather than trusting a trigger description
   at all; merely-suboptimal tolerates on-demand's small residual
   risk of a missed trigger.
```

None of these questions alone is decisive - they combine. A rule needed on turn one, in every session, with severe consequences if missed (question 1: yes, question 2: majority, question 3: severe) is an unambiguous always-loaded candidate, or better, a hook. A narrow procedure needed in maybe one session in twenty, where the worst case of missing it is "the agent does something slightly less efficient and the user corrects it" (question 1: no, question 2: minority, question 3: mild) is an unambiguous on-demand candidate.

### Worked example: applying the procedure to five real candidates
```
Candidate                          Q1: turn-  Q2: most    Q3: severity   Decision
                                    zero need? sessions?   if missed
------------------------------------------------------------------------------------
A. "Always respond in the         Yes        Yes          Mild-moderate  Always-
   user's preferred language"                              (annoying,     loaded
                                                             not harmful)
B. "How to run our internal       No         No (rare      Moderate       On-demand
   data-migration script            (only after            (wrong data    (skill)
   safely, with dry-run first)"     user asks)              migration
                                                             if skipped)
C. "Never execute a destructive   Yes        Yes           Severe         Always-
   shell command without                                    (data loss)   loaded, AND
   confirmation"                                                          a hook
                                                                           (lesson 10)
D. "Format code review comments   No         Minority      Mild           On-demand
   using our team's specific        (only on   (only code    (cosmetic)   (skill)
   emoji-prefix convention"          review     review
                                     tasks)     tasks)
E. "Company name and product      Yes        Yes           Mild-moderate  Always-
   terminology to use                                       (confusing    loaded
   consistently"                                             but not
                                                              harmful)
```

Notice candidate C: severity alone was enough to push it past "always-loaded" into "don't even trust always-loaded system-prompt text for this - back it with a deterministic hook that enforces the rule outside model judgment." This is the always-loaded/on-demand line intersecting with a different axis entirely (model-judged versus deterministic, lesson 10) - the two decisions are related but not the same question, and severity is usually what forces you to consider the deterministic option at all.

### Worked example: a token accounting for the line
Take a coding agent running roughly 30 turns per session, 500 sessions a month, with three candidate pieces of guidance under consideration:

```
Item                Size      If always-loaded          If on-demand
                               (cost/month, 30 turns/    (cost/month, assumes
                               session x 500 sessions)    triggers correctly
                                                           on the 15% of
                                                           sessions that need it)
--------------------------------------------------------------------------------
Coding style rules   200 tok   200 x 30 x 500             (n/a - needed almost
(needed nearly                 = 3,000,000 tokens/mo       every session; treat
every session)                                             as always-loaded)
Legacy API migration 3,000 tok 3,000 x 30 x 500            (3,000 x 30 x 75
guide (needed ~15%             = 45,000,000 tokens/mo       sessions) + (~120 tok
of sessions)                                                metadata x 30 x 500
                                                             all sessions)
                                                            = 6,750,000 +
                                                             1,800,000
                                                            = 8,550,000 tokens/mo
```

The migration guide, if always-loaded, would cost roughly 5x what it costs deferred - a direct, quantified argument for on-demand in this case. The style rules, by contrast, are needed on nearly every session, so the on-demand path's fixed per-turn metadata overhead (paid on every session regardless) approaches the always-loaded cost anyway, while adding the reliability risk of a missed trigger for no real savings - the calculation itself tells you to just always-load it. This is the always-loaded/on-demand line made concrete: it moves depending on actual usage frequency, not on a fixed rule about content "type."

### Why the line is dynamic, not a one-time decision
The frequency term in that accounting - how often a piece of content actually turns out to be needed - is an empirical fact about usage, not a property fixed at authoring time. A piece of content correctly deferred because it was rare when the agent launched can become common as usage patterns shift (a legacy migration guide gets used constantly during a six-month migration push, then goes back to being rare afterward). The always-loaded/on-demand line is something to revisit periodically against real usage data, not a decision made once and left alone - this connects directly to lesson 09's discussion of evaluating whether a deferred piece of content is actually being triggered when it should be.

> **Example (Aug 2026):** this repository draws exactly this line in its own `AGENTS.md`. The "Core loop" and "Non-negotiables" sections are always-loaded - short, universal, needed on essentially every session regardless of task. Each `agent-docs/*.md` file is on-demand, deferred behind a one-line trigger description in the dispatcher ("before cutting a release... read agent-docs/release-policy.md"). The file itself states the reasoning implicitly: release-policy content would be wasted context on the vast majority of sessions that never touch a release, while the core loop's "know the learner before advising" is relevant to literally every session and earns its permanent place. This is one plain-text implementation of the line-drawing decision, not a template to copy verbatim - the decision procedure in this lesson applies regardless of what mechanism ultimately defers the content.

## Pros
- **Directly optimizes the cost side of the context budget** (prompting-context-engineering/07) by ensuring the always-loaded portion of context is genuinely the minimal set that earns its permanent place, not an accumulated pile of "might be useful someday."
- **Makes reliability trade-offs explicit and inspectable.** Once you've deliberately drawn the line, "why doesn't the agent know X" has a legible answer - either X was deliberately deferred and its trigger didn't fire (a lesson 04/05 problem) or X was never captured anywhere (an authoring gap) - rather than a shrug.
- **Scales the agent's effective knowledge far beyond what always-loaded content alone could hold**, by using the tiered-cost structure from lesson 02 to keep a much larger total library of guidance available without taxing every turn.
- **Surfaces genuinely severe rules for extra scrutiny.** The exercise of asking "what's the consequence of missing this" naturally identifies which rules are important enough to also need a deterministic backstop (lesson 10), rather than leaving every rule's enforcement purely to model judgment.

## Cons
- **The decision requires real usage data to get right, and that data often doesn't exist yet at authoring time** - the token-accounting worked example assumed a known frequency (15% of sessions); a brand-new piece of content has no track record, forcing an initial guess that may need correcting later.
- **On-demand content has a nonzero chance of never triggering when it should**, and that failure is silent by construction (nothing in the interaction signals "a relevant thing existed and wasn't loaded") - this residual risk is the entire subject of lesson 05 and is a real cost, not a rounding error.
- **Drawing the line too aggressively toward on-demand fragments an agent's baseline competence** into a pile of narrow, individually-triggered fragments, which can produce an agent that behaves inconsistently depending on which fragments happened to fire, rather than one with a coherent, predictable baseline.
- **Revisiting the line as usage shifts is easy to neglect.** Without a habit of checking actual trigger frequency against the original assumption (lesson 09), a piece of content that should have been promoted or demoted often just stays wherever it was first placed, for years.

## Alternatives
- **Always-load everything (no deferral mechanism at all)** - the simplest possible design, appropriate only for a small, stable instruction set that comfortably fits the budget from prompting-context-engineering/07; breaks down exactly as described in lesson 01's worked example the moment the candidate content grows past what any reasonable always-loaded budget can absorb.
- **Defer everything except a minimal bootstrap** - maximizes token efficiency and minimizes the always-loaded footprint, but pushes all reliability risk onto the triggering mechanism and produces an agent with almost no guaranteed baseline behavior; usually too extreme in the other direction unless the triggering mechanism has been proven very reliable for this specific use case.
- **Load based on a fixed schedule or heuristic instead of relevance** (e.g., "load the migration guide every Monday" or "load it every 10th session") - avoids the judgment-call risk of model-based triggering entirely, but is a poor substitute for actual relevance and either wastes budget on sessions that don't need it or still misses sessions that do; occasionally useful as a coarse fallback, not a primary strategy.

## When to use it
Apply this line-drawing discipline any time you're deciding whether a new piece of guidance belongs in an agent's permanent, always-loaded instructions or should be deferred behind a trigger. It matters most once an agent's total candidate instruction content has grown large enough that "just always-load everything" would visibly bloat the budget, or once you have enough real usage data to make an informed frequency estimate rather than a guess.

## When NOT to use it
For a small, stable agent whose entire instruction set comfortably fits well within the context budget with room to spare, formally running this decision procedure per item is more process than the situation needs - just always-load it and revisit only if and when the budget starts to actually hurt. Also resist using "we might need it later" as sufficient justification for always-loading something now; that's exactly the reasoning the budget discipline in the prerequisite lesson warns against, and it's usually a sign the item should be deferred, not promoted.

## Key takeaways / mental model
Treat every candidate piece of guidance as facing a toll both ways: always-loaded content pays a small, certain toll on every single turn forever; on-demand content pays no toll most of the time but carries a nonzero chance of arriving too late or not at all on the turn it was actually needed. The line-drawing decision is not "which is better" in the abstract - it's a per-item calculation of frequency of need times severity of a miss, weighed against the recurring cost of guaranteeing presence. High frequency and high severity pulls toward always-loaded (or further, toward a deterministic hook); low frequency and low-to-moderate severity tolerates the residual risk of on-demand. The line moves as real usage data comes in - it is drawn once, provisionally, and revisited, not set in stone at design time.

## Self-check questions
1. A new agent feature needs a 1,500-token explanation of a rarely-used export format, needed in an estimated 5% of sessions, with a mild consequence if the agent occasionally gets the format slightly wrong. Walk through the three-question decision procedure and justify a placement.
2. Contrast two rules: "always use the customer's preferred currency symbol" and "never delete a customer's account without two confirmations." Both could technically be phrased as system-prompt text. Using this lesson's severity axis, explain why they should likely land on different surfaces even though both are "always relevant."
3. Six months after launch, you discover a piece of content originally deferred as a rare-use skill is now triggering on 60% of sessions because your user base's typical task shifted. What would you reconsider, and why does this lesson describe the always-loaded/on-demand line as dynamic rather than fixed?
4. Explain, without using the word "tokens," why an always-loaded rule and an on-demand rule carry fundamentally different kinds of risk, even when both are phrased with equal clarity.
5. A teammate argues "just always-load anything that's even remotely important, better safe than bloated." Using the token-accounting worked example, construct a concrete counter-argument showing where that reasoning breaks down.

## References
- [Anthropic engineering blog: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Anthropic platform docs: Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Anthropic platform docs: Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [explainx.ai: Steering Claude Code - All 7 Instruction Methods Explained (2026)](https://explainx.ai/blog/steering-claude-code-claude-md-skills-hooks-subagents-rules-2026)
- This repository's own `AGENTS.md` (accessed 2026-08)
