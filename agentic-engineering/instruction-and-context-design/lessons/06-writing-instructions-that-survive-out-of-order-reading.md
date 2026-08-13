---
id: instruction-and-context-design/06
subject: instruction-and-context-design
title: Writing Instructions That Survive Being Read Out of Order
slug: writing-instructions-that-survive-out-of-order-reading
status: drafted
mastery:
seniority: senior
source: "Liu et al., Lost in the Middle: How Language Models Use Long Contexts, arXiv:2307.03172 (2023-2024); RIFT: Reordered Instruction Following Testbed, arXiv:2601.18924 (2026); Beyond the Prompt: An Empirical Study of Cursor Rules, arXiv:2512.18925 (2025); this repository's own AGENTS.md and agent-docs/ dispatcher as a case study (2026)"
durability: durable
prerequisites: [instruction-and-context-design/04]
created: 2026-08-10
updated: 2026-08-10
---

# Writing Instructions That Survive Being Read Out of Order

## TL;DR
A document written for deferred loading (lessons 03-05) will not always be read where its author imagined it - it might load third instead of first, alongside unrelated material, in a session where the always-loaded top-level instructions have already scrolled out of the model's effective attention, or in a different order than any other on-demand document it references. Writing instructions that survive this means treating every loadable unit as if it might be the *only* thing the model currently has clear attention on, not as a chapter that can lean on what came before it.

## The idea
Most writing - including most technical documentation - is authored and read the way a book is: front matter sets up context, later sections build on earlier ones, and the reader experiences the material in the order the author chose. A system prompt with everything loaded once, at the start, in a fixed sequence, inherits this assumption more or less safely, because the order really is fixed.

Deferred loading breaks that assumption on purpose. The whole point of lessons 03-05 is that different pieces of instruction load at different times, triggered independently, by different conditions, often in a session where several other on-demand resources have already loaded (or will load later) in an order nobody controls in advance. A document that says "as established above" or "building on the previous section's rule" is making a bet about sequence that deferred loading does not honor. Worse, even material that *did* load in the "right" order isn't safe from a second, independent problem: long contexts don't treat every position equally. Empirical work on long-context models shows a robust U-shaped accuracy curve - information at the very start or very end of the context is used reliably, while functionally identical information placed in the middle is used markedly worse, degrading by over 30 percentage points in some measurements (Liu et al., 2023-2024, arXiv:2307.03172). An instruction that depended on being read early, in a context where it actually lands in the middle after several other resources loaded around it, can be technically present and still functionally invisible. Writing for this environment means each loadable document has to be robust on two axes: contents-can-arrive-in-any-order, and position-in-context-is-not-guaranteed-favorable.

## How it works

### Self-containment: never require a preceding section to exist
The single highest-leverage habit is writing every on-demand document as if it might be the only thing currently loaded besides the always-loaded core. That means:
- Restate the minimum context needed to act correctly, rather than assuming the reader arrived via a linear path. If a rule only makes sense given a piece of background, either state that background briefly or point explicitly to where it lives (by name, not by "as mentioned earlier").
- Avoid phrases that encode positional assumptions: "as above," "per the previous section," "continuing from," "now that we've covered X." These are silent dependencies on read order that a linear document can afford and a deferred-loading document cannot.
- Prefer named, resolvable references over positional ones: "see the retry-policy rules in `agent-docs/error-handling.md`" survives being read in any order; "see the retry-policy rules above" does not, because "above" stops meaning anything the moment the document is read on its own.

### Redundancy as a deliberate cost, not an accident
Linear-document instinct treats repetition as a flaw to edit out - say a constraint once, refer back to it everywhere else. In a deferred-loading system, this instinct actively creates risk: if the one canonical statement of a constraint lives in a document that doesn't happen to load for a given task, every other document that merely referenced it inherits a gap. The RIFT study (arXiv:2601.18924, 2026), built specifically to test instruction-following when prompt order is scrambled while content is held constant, found that strong performance under linear ordering does not predict strong performance once the same instructions are reordered - suggesting models lean on positional/sequential cues more than authors assume, and that content which depended on a specific neighbor being present nearby degrades when that neighbor moves or disappears. The practical response is to restate a small number of genuinely load-bearing constraints wherever they're needed, even at the cost of saying the same sentence in two or three places, rather than centralizing them once and hoping every dependent document loads alongside the source.

### Make each unit re-enterable, not just self-contained
Self-containment covers *what* a document assumes; re-enterability covers *when* it can be read. A document is re-enterable if a reader (human or model) landing on it mid-session, without having seen it load before, can act on it correctly the first time, and a reader who has already seen it once (because it reloaded, or because a summary of it persisted after the original text was compacted out) doesn't get confused by seeing it again. Two techniques make this concrete:
- **State the trigger condition inside the document itself**, not only in the external metadata that caused it to load (lesson 02). If a document says "this applies when you are about to commit code" at its own top, a reader who encounters it without having seen the metadata that triggered it (for instance, after a context compaction event that kept the body but dropped the surrounding session history) still knows when it's relevant.
- **Make instructions idempotent** - safe to re-apply if read twice. A rule phrased as "do X" is idempotent by default; a rule phrased as "do X in addition to whatever you already did" is not, because a model that has already partially completed X once and now re-reads the instruction has to reconstruct state it may not actually have. Prefer stating the end condition ("ensure X is true") over the incremental action ("also do X"), because the end-condition phrasing gives the same correct behavior whether this is the first or the third time the document has been read this session.

### A worked example: rewriting a fragile instruction
Original, written with linear-reading assumptions (imagine this as one paragraph inside a larger onboarding document, referencing a rule stated three paragraphs earlier):

> "As discussed above, always confirm the target environment before running the deploy script. Once confirmed, proceed as normal."

This fails hard the moment it's the only paragraph that loads (e.g., because a trigger fired on "deploy script" specifically, pulling in just this on-demand snippet without its surrounding document): "as discussed above" points at nothing, "confirm... before running" doesn't say what confirmation looks like or what "normal" means without the missing context, and there's no signal for what to do if this loads a second time after confirmation already happened.

Rewritten to survive isolated, repeated, and reordered loading:

> "Before running any deploy script, confirm the target environment (staging or production) with the requester if it is not already explicit in the task. If the environment has already been confirmed earlier in this session, do not re-ask - proceed directly. Never run a deploy script against production without an explicit, current-session confirmation of that environment."

The rewrite states its own trigger ("before running any deploy script"), defines what "confirm" means concretely (ask if not explicit), handles the reread case explicitly (don't re-ask if already confirmed this session - covering idempotency without assuming this is the first read), and states the actual constraint as an end condition ("never run... without... confirmation") rather than a fragile "proceed as normal" that depended on unstated context.

### A worked example from a real, inspectable system
This repository's own top-level `AGENTS.md` is a live specimen of exactly this problem and this technique, not a hypothetical. It dispatches to files in `agent-docs/` (for example `agent-docs/learning-workflows.md`, `agent-docs/git-policy.md`) that are explicitly *not* always loaded - each carries a documented trigger condition ("before committing, pushing, creating branches... read `agent-docs/git-policy.md`") and is meant to be read independently, in whatever order the session's actual needs dictate, possibly with `AGENTS.md` itself no longer fresh in the model's attention by the time a given `agent-docs/*.md` file loads several turns later. Consistent with the redundancy technique above, the load-bearing non-negotiables (English-only content on `main`, never fabricating progress, keeping IDs stable) are restated at the `AGENTS.md` level *and* echoed inside the specific `agent-docs/*.md` files where they're operationally relevant, rather than stated once centrally and merely referenced elsewhere - exactly because any given `agent-docs/*.md` file might be the only thing currently in view when a decision governed by that constraint gets made. This is one worked example of the pattern, not the definition of it - the same technique applies to any dispatcher-plus-detail-docs system, regardless of what it's called or which product implements it.

### Placement still matters even within a single loaded document
Because of the position-in-context effect (Liu et al., 2023-2024), the *internal* structure of a single on-demand document also matters, independent of load order across documents. The single most load-bearing constraint in a document is safest stated in its first sentence or two (a reader/model scanning quickly still catches it) and, where the format allows, restated at the very end as a closing reminder - not buried in paragraph four of an otherwise well-organized document, where it sits in exactly the position the U-shaped curve treats worst.

## Pros
- **Resilient to real deployment conditions.** Sessions genuinely do compact, truncate, and load resources in unpredictable orders; instructions written this way degrade gracefully instead of silently failing when the "expected" order doesn't hold.
- **Easier to test and review in isolation.** A self-contained, re-enterable document can be evaluated on its own - "does this make sense and give correct guidance if this is literally the only thing loaded" is a concrete, checkable question; a document full of "as above" references cannot be evaluated without reconstructing the whole book it was extracted from.
- **Naturally more robust to future restructuring.** Documents that don't lean on positional relationships to other documents survive being reordered, split, merged, or moved to a different location later, without silent breakage.

## Cons
- **Costs tokens.** Deliberate redundancy (restating a constraint in two or three places) is the opposite of DRY writing and directly consumes more of the context budget that deferred loading exists to conserve (lesson 03) - a real trade-off, not a free lunch.
- **Harder to author well.** Writing self-contained, order-independent prose takes more discipline and more editing passes than writing a linear narrative that can lean on "as established above"; it's easy to slip back into linear habits, especially for anyone maintaining documentation who is used to writing books, wikis, or onboarding docs meant to be read start to finish.
- **Can read as repetitive or stilted to a human who does read the whole thing in order** - the deliberate restatement that protects an out-of-order model reader looks like padding to a human skimming the source files top to bottom, and reviewers unfamiliar with this constraint sometimes "clean up" the redundancy, reintroducing the fragility it was protecting against.

## Alternatives
- **Enforce a fixed load order** - if the harness can guarantee documents always load in a specific, deterministic sequence, positional writing becomes safe again and this lesson's techniques are unnecessary overhead. This works only when the harness genuinely enforces the guarantee end to end (including after compaction/summarization events); the moment any part of the pipeline can reorder, drop, or independently trigger loads, the guarantee is false and instructions written to depend on it will eventually fail silently.
- **Centralize every cross-cutting constraint in the one always-loaded document** instead of restating it across on-demand documents - avoids redundancy entirely, but only works for the (typically small) set of constraints important enough to earn a permanent slot in the always-loaded core (lesson 03); most operationally-specific rules are too narrow to justify that cost, which is exactly why they were made on-demand in the first place.
- **Retrieval systems that reassemble a coherent, ordered bundle at query time** rather than relying on independently-triggered documents - shifts the ordering problem to the retrieval/assembly layer instead of the document author, which can help, but the position-in-context degradation (Liu et al.) still applies to whatever the retrieval layer hands the model, so this alternative narrows the problem without eliminating it.

## When to use it
Apply these techniques to any document that might load on demand, independently of other documents, in a session where the harness does not guarantee a fixed read order - which describes essentially every skill, reference doc, or dispatched instruction file in a deferred-loading system (lessons 03-05). It matters most for the small set of genuinely load-bearing constraints (safety rules, non-negotiables, anything whose violation is costly) - those are exactly the ones worth the redundancy cost.

## When NOT to use it
Don't apply order-independent writing discipline to a document that is provably, permanently part of a fixed linear sequence with no independent trigger of its own - for instance, numbered steps inside a single document that only ever loads as one unit have no out-of-order risk between them, because they're never read apart. Over-applying redundancy here just bloats a document that was never at risk. The judgment call is whether the *unit being loaded* (not the prose within it) could plausibly load independently, in a different order, or in isolation from its neighbors - if the harness's own loading mechanism guarantees otherwise, linear writing inside that unit is fine.

## Key takeaways / mental model
Write every on-demand document as if it were a single page torn out of a book and handed to someone who has never seen the rest of the book, who might be handed the same page twice, and who might receive it stapled in the middle of an unrelated stack rather than at the top. That reader needs the page to say what it needs to say on its own: what situation it applies to, what to do, and what "done" looks like - without "as discussed above," without assuming it's being read first, and without assuming it's the only page that will ever matter. The cost is some repetition; the alternative is a document that works perfectly in the one session where everything loaded in the author's intended order, and silently fails in every other session.

## Self-check questions
1. A document says "Continue following the escalation steps outlined previously once the customer has been verified." Identify every positional assumption baked into this sentence, and rewrite it to be self-contained.
2. Explain, in your own words, why "lost in the middle" (a finding about *position within a single context*) is a separate risk from "loaded out of order" (a finding about *which documents load at all, and in what sequence*) - and why a document author has to defend against both, not just one.
3. Your team wants to reduce documentation size by removing "redundant" restatements of a safety constraint that already appears in one canonical always-loaded document. Using this lesson's framing, what question would you ask before agreeing to that cleanup?
4. Give an example of an instruction phrased as an incremental action ("also do X") and rewrite it as an idempotent end-condition ("ensure X is true"). Explain what concretely breaks with the original phrasing if the document loads twice in one session.
5. A reviewer who always reads documentation top-to-bottom complains that a set of on-demand documents "keeps repeating itself" and asks you to consolidate. What trade-off would you explain to them, and under what condition would you agree the redundancy actually is excessive?

## References
- [Liu et al., Lost in the Middle: How Language Models Use Long Contexts (arXiv:2307.03172)](https://arxiv.org/abs/2307.03172)
- [RIFT: Reordered Instruction Following Testbed To Evaluate Instruction Following in Singular Multistep Prompt Structures (arXiv:2601.18924)](https://arxiv.org/html/2601.18924)
- [Beyond the Prompt: An Empirical Study of Cursor Rules (arXiv:2512.18925)](https://arxiv.org/pdf/2512.18925)
- This repository's own `AGENTS.md` and `agent-docs/*.md` dispatcher, as one inspectable case study of the pattern.
