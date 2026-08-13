---
id: instruction-and-context-design/04
subject: instruction-and-context-design
title: "Designing Trigger Descriptions: How an Agent Decides What to Load"
slug: designing-trigger-descriptions
status: drafted
mastery:
seniority: senior
source: "Anthropic platform docs: Skill authoring best practices (2026); Anthropic platform docs: Agent Skills overview (2026); Anthropic engineering blog: Writing effective tools for AI agents (2025); explainx.ai: Steering Claude Code - All 7 Instruction Methods Explained (2026)"
durability: durable
prerequisites: [instruction-and-context-design/03, tool-use-agentic-loop/02]
created: 2026-08-10
updated: 2026-08-10
---

# Designing Trigger Descriptions: How an Agent Decides What to Load

## TL;DR
When content is deferred (lesson 03), something has to decide, on every turn, whether *this* piece of content is relevant to *this* task. That something is usually not an index lookup or a keyword match - it's the model itself, reading a short natural-language description and making a judgment call about relevance, the same kind of inference it makes about everything else. Writing a description that reliably produces the right judgment - firing when it should, staying quiet when it shouldn't - is a distinct, learnable skill with its own failure patterns, and it is the mechanism that makes or breaks every on-demand surface in this subject.

## The idea
It's tempting to picture deferred-loading the way a search engine works: content has some tags or keywords, a query comes in, and a matching algorithm decides what's relevant. That model is wrong for how agent triggering actually works in 2026, and the difference matters enormously for how you write descriptions. There is no fixed vocabulary of keywords being matched against. Instead, a short piece of metadata (lesson 02's structured description) sits in the model's context, and on each turn the model reads the current task and asks itself, in the same way it reasons about anything else, "does this description describe something relevant to what I'm doing right now?" Anthropic's own guidance is explicit that a skill's name and description are read by the model to determine whether to trigger it - this is inference, not lookup.

This is a fundamentally different design problem than writing a good search index. A keyword index rewards exhaustive coverage of possible query terms. A trigger description rewards something closer to what makes a good elevator pitch: conveying, compactly and unambiguously, both what the thing is and specifically when someone should reach for it - phrased the way the need for it actually shows up in a real task, not the way its internal documentation would describe it. Get this wrong and you get one of two failure shapes: the model reads a vague or narrow description and doesn't recognize the current task as a match (under-triggering, explored fully in lesson 05), or it reads an overly broad description and fires on tasks that don't actually need it, wasting the token budget lesson 03 was trying to protect and sometimes actively confusing the model with irrelevant loaded content (over-triggering).

## How it works

### The judgment-call mechanism, concretely
Picture the model's reasoning, on a turn where three deferred skills' descriptions sit in its context alongside the user's actual request:

```
Context contains (metadata only, per lesson 02):
  - "pdf-processing: Extracts text and tables from PDF files, fills
     forms, merges documents. Use when working with PDF files or
     when the user mentions PDFs, forms, or document extraction."
  - "db-migrations: Runs database schema migrations safely,
     including dry-run validation. Use when the user asks to run,
     write, or review a database migration, or mentions schema
     changes to a table."
  - "commit-messages: Generates descriptive commit messages by
     analyzing git diffs. Use when the user asks for help writing
     commit messages or reviewing staged changes."

User's current message: "Can you pull the line items out of this
invoice and total them up?"
```

Nothing in this message contains the literal string "PDF" or "form" - the model has to infer that "pull the line items out of this invoice" describes a task that the pdf-processing skill's description covers, if the invoice is in fact a PDF (visible from an attached file, say). This is exactly the inferential step that separates trigger-description design from keyword indexing: a description that only listed the keywords "PDF, forms, extraction" and stopped there would rely on the model happening to already know that "invoice" and "line items" are the kind of task a PDF-extraction tool handles - a much weaker bet than a description that explicitly names common real-world phrasings of the task, not just the tool's internal vocabulary.

### What makes a description actually work: three properties
Three properties recur across every well-documented case of trigger descriptions that fire reliably, and their absence recurs across cases that don't.

**1. Specificity - naming the concrete task, not the abstract category.** A description that says what the content *is* in the author's own vocabulary, without saying what real tasks it applies to, forces the model to bridge a gap it may or may not bridge correctly. Compare:

```
Vague (relies on the model inferring applicability):
  description: "Helps with documents"

Specific (states applicability directly):
  description: "Extract text and tables from PDF files, fill
  forms, merge documents. Use when working with PDF files or
  when the user mentions PDFs, forms, or document extraction."
```

The vague version isn't wrong, exactly - it's not false - but it makes the model do all the inferential work of connecting "helps with documents" to a concrete request like "grab the numbers from this invoice." The specific version does that connecting work for the model, in the description itself, at authoring time - a much more reliable place to do it than at inference time under task pressure.

**2. Matching how tasks actually get phrased, not how the content's author thinks about it.** This is the property most often missed by capable, technically precise authors, because the gap is invisible to them: the person who built the skill thinks about it in terms of its internal name and mechanism, but the person using it (or the model, standing in for them) describes their need in completely different, more concrete, more surface-level language.

```
Task: "Can you clean up this data and make it presentable?"

Author's internal framing:                Actual user phrasing patterns:
  "Applies statistical outlier removal      "clean up this data"
   and canonical schema normalization       "make it presentable"
   to tabular datasets"                     "this spreadsheet is a mess"
                                             "fix the formatting"
```

A description written purely from the author's internal framing ("statistical outlier removal and canonical schema normalization") will very likely fail to fire on "clean up this data and make it presentable," even though that request is precisely what the content handles. A description written to also include the plain-language phrasings a real user or task would actually use ("Use when cleaning messy tabular data, fixing spreadsheet formatting, or normalizing inconsistent data") closes that gap directly. This is why Anthropic's own guidance recommends deliberately including "specific triggers/contexts for when to use it," explicitly naming terms the way real requests use them, not just the domain vocabulary the author is fluent in.

**3. Calibrated breadth - neither over-broad nor over-narrow.** Breadth is the axis most prone to overcorrection. An over-narrow description matches only the exact phrasing the author imagined and misses every real variant:

```
Over-narrow:
  description: "Use when the user says the exact phrase
  'run database migration'."
```

This fires only on that literal phrase and silently misses "can you update the schema," "I need to add a column," or "let's apply the pending migrations" - all of which describe the same underlying task in different words.

An over-broad description, overcorrecting in the other direction, matches nearly anything adjacent to its domain and fires when it shouldn't:

```
Over-broad:
  description: "Use for anything related to databases."
```

This will very plausibly fire on "what's a good database for a small project" (a question about choosing a database, not about running a migration) or "explain what a foreign key is" (a conceptual question, unrelated to this specific migration procedure) - loading a 2,000-token migration guide into context for a task that had nothing to do with running one, reproducing exactly the wasted-budget cost lesson 03's decision procedure was trying to avoid.

The calibrated middle ground names the task specifically enough to exclude the over-broad false positives, while covering enough real phrasings to catch the over-narrow false negatives:

```
Calibrated:
  description: "Runs database schema migrations safely, including
  dry-run validation and foreign-key constraint checks. Use when
  the user asks to run, write, or review a database migration,
  add or change a table's schema, or mentions pending schema
  changes."
```

### Worked example: rewriting a bad description end to end
Take a real progression from a first-draft description to a working one, showing each fix and the failure it addresses.

```
Draft 1 (too narrow, author's-eye-view):
  "Formats commit messages per our internal convention document."
  Problem: doesn't say WHEN to use it in task terms; "our internal
  convention document" is jargon the model has no other context for.

Draft 2 (adds trigger language, still narrow):
  "Formats commit messages per our internal convention document.
  Use when the user asks to format a commit message."
  Problem: still misses "help me write a commit message," "can you
  summarize these changes for the commit," "what should this
  commit say" - all real phrasings that never use the word "format."

Draft 3 (broadens trigger phrasing, calibrated):
  "Generates descriptive commit messages by analyzing a git diff,
  following this repository's message conventions. Use when the
  user asks for help writing, drafting, or reviewing a commit
  message, or asks what a commit should say about staged changes."
  Result: fires on the phrasings that actually occur, still scoped
  tightly enough not to fire on unrelated git questions like
  "how do I revert a commit."
```

Each revision targets a specific, nameable failure mode - draft 1 to draft 2 fixed missing trigger language entirely; draft 2 to draft 3 fixed narrow phrasing coverage. Neither revision made the description longer for its own sake; each addressed a concrete gap between how the description was worded and how the task actually shows up.

### Why this differs from ordinary prompt-writing advice
It's worth being explicit about why "write clearly" isn't sufficient advice here, even though it's necessary. Ordinary prompt or instruction writing is judged by whether the model, once it's reading the content, understands and follows it correctly. A trigger description is judged by an earlier, different question: whether the model, *before* reading the content, correctly predicts from the description alone whether reading it would help. That's a prediction task under uncertainty, not a comprehension task - and it's why specificity, real-phrasing coverage, and calibrated breadth (properties about matching a description against an unknown future task) matter here in a way they don't for, say, a step-by-step procedure the model reads after already knowing it's relevant.

### The character-budget constraint
Because descriptions live on the always-loaded surface (their metadata form, per lesson 02) even though their bodies are deferred, they compete for the same budget as everything else always-loaded, and most platforms cap them explicitly for this reason.

> **Example (Aug 2026):** in the Agent Skills open standard, a skill's description field is capped at 1,024 characters, and this cap exists precisely because the description sits in the always-loaded system-prompt budget across every candidate skill - a system with a hundred installed skills pays for a hundred descriptions on every turn regardless of which, if any, actually trigger. Exact limits vary by platform and change over time; the durable constraint is that description length is genuinely expensive at scale, which is a real design pressure toward concision, not just a stylistic preference.

This creates real tension with the specificity and real-phrasing-coverage properties above: naming every plausible real-world phrasing of a task can run long, while a tight budget rewards brevity. Resolving that tension is itself a design skill - prioritize the phrasings most likely to actually occur over exhaustive coverage of every conceivable variant, and trust that a reasonably capable model can still bridge minor gaps a perfectly-worded description would have closed explicitly.

## Pros
- **Scales relevance-judgment far beyond fixed keyword schemes.** Because the mechanism is inference over natural language, it naturally handles paraphrase, synonymy, and novel phrasings a rigid keyword or tag system would simply miss.
- **Improves measurably and cheaply.** Anthropic's own reporting on tool-description refinement found that small wording changes to descriptions produced large jumps in a coding agent's benchmark performance - description quality is a high-leverage, low-cost lever compared to changing the underlying model.
- **Keeps the authoring burden proportionate to the content's value.** A well-calibrated description is typically a few dozen to a couple hundred tokens of careful writing, in exchange for making a much larger body of content (lesson 02's tiering) usable without inflating the always-loaded budget.
- **Decouples triggering quality from body quality**, letting you iterate on "does this fire correctly" and "is the content itself good" as separate concerns, which makes debugging failures (lesson 05) far more tractable.

## Cons
- **It's a judgment call, not a guarantee.** Even a well-written description can fail to fire on an unusually phrased request, or fire on a superficially similar but actually unrelated one - there is no formal correctness proof available the way there would be for a deterministic keyword match, which is precisely why lesson 05 exists as its own lesson.
- **Getting the breadth right requires iteration and real usage data**, not just careful first-draft writing - the over-narrow and over-broad failure modes are usually only visible once real, unpredictable task phrasings are tested against the description, not from reading it in isolation.
- **Competing descriptions can interfere with each other.** As the number of candidate skills/tools grows, increasingly similar descriptions can create genuine ambiguity about which of several plausible matches the model should pick, a problem that gets harder to manage purely through better wording as the library grows.
- **The character-budget constraint forces real trade-offs.** Comprehensive real-phrasing coverage and brevity pull in opposite directions, and there's no way to fully satisfy both at scale - authors have to prioritize, and that prioritization can be wrong.

## Alternatives
- **Fixed keyword or tag matching** - fast, deterministic, and easy to test formally (a keyword either appears or it doesn't), but brittle to paraphrase and synonymy in exactly the way the invoice/PDF worked example demonstrates; requires an ever-growing, manually maintained keyword list to approach the coverage a good natural-language description gets more naturally.
- **Always-loading instead of triggering** - sidesteps the triggering-accuracy problem entirely by removing the decision (lesson 03's always-loaded option), at the direct cost of the token budget the deferral was meant to protect; the right choice exactly when lesson 03's decision procedure favors it, not as a general workaround for hard-to-write descriptions.
- **A separate retrieval/classification model dedicated to routing** - can be tuned and evaluated more rigorously than relying on the same model's inline judgment, and can scale to very large libraries better than natural-language descriptions competing in one context window; adds real infrastructure (a second model or system to build, host, and keep in sync) that's only worth it once the candidate library is large enough that inline judgment demonstrably breaks down.
- **Explicit human invocation only (no model-judged triggering at all)** - removes triggering-accuracy risk entirely, since a human decides; trades away the automatic-discovery benefit that makes on-demand content useful in the first place, and pushes the burden of remembering what's available back onto the human (this is the slash-command alternative from lesson 01, formalized further in lesson 10).

## When to use it
Invest real, deliberate effort in trigger-description design any time you're building deferred content that needs to be discovered automatically - a skill, a tool, a retrievable document - rather than explicitly invoked. It's worth the most effort exactly where the stakes of lesson 03's severity axis are moderate-to-high (missing the trigger has a real cost) but not so severe that you'd back the rule with a deterministic mechanism instead (lesson 10) - the sweet spot where triggering quality is genuinely the thing standing between "the agent behaves correctly" and "it doesn't."

## When NOT to use it
Don't sink disproportionate effort into perfecting a trigger description for content that's rarely relevant and low-stakes when missed - a good-enough first draft, revisited only if evidence (lesson 09) shows it's actually under- or over-triggering, is proportionate. And don't reach for trigger-description design at all when the content in question genuinely needs a guarantee, not a judgment call - route that content to always-loaded (lesson 03) or a deterministic hook (lesson 10) instead of trying to write a description good enough to eliminate all risk of a missed inference, which isn't achievable by wording alone.

## Key takeaways / mental model
A trigger description is not a search index entry - it's closer to a well-written classified ad, read by a smart but literal-minded reader who has to decide, from that ad alone and before seeing anything else, whether to walk through the door. The reader doesn't share the author's internal vocabulary and won't connect dots the ad doesn't draw explicitly. Writing one well means naming the concrete task (not the abstract category), phrasing it the way the need actually shows up in the world (not the way the content's own documentation describes it), and calibrating breadth so the ad neither undersells (misses real customers) nor oversells (draws in people who don't actually want what's inside). Every under-triggering and over-triggering failure in lesson 05 traces back to one of these three properties being wrong.

## Self-check questions
1. Rewrite this description to fix its specificity problem, and explain what real task phrasings it would have missed as originally written: "description: Helps analyze data."
2. A skill's description says "Use when the user mentions Excel or spreadsheets." A user asks "can you total up column C in this file" without ever saying "Excel" or "spreadsheet," attaching an .xlsx file. Using the invoice/PDF worked example's reasoning, explain why this description is likely to under-trigger and rewrite it to fix the gap.
3. You're asked to review a description that reads: "Use for anything involving customer data." Identify which of the three properties (specificity, real-phrasing matching, calibrated breadth) it violates, and predict a concrete false-positive scenario where it would fire incorrectly.
4. Explain, in your own words, why "the model reads a description and judges relevance" is fundamentally different from "the system matches keywords against a query," and why that difference specifically favors natural-language descriptions over rigid tags for handling paraphrase.
5. You have a 1,024-character budget and a task domain with fifteen plausible real-world phrasings a user might use to request it. You can't fit all fifteen verbatim. Describe the prioritization approach you'd use to decide which phrasings earn a place in the description and which get left to the model's own inference.

## References
- [Anthropic platform docs: Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Anthropic platform docs: Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Anthropic engineering blog: Writing effective tools for AI agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [explainx.ai: Steering Claude Code - All 7 Instruction Methods Explained (2026)](https://explainx.ai/blog/steering-claude-code-claude-md-skills-hooks-subagents-rules-2026)
