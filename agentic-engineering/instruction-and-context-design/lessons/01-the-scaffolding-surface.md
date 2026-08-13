---
id: instruction-and-context-design/01
subject: instruction-and-context-design
title: "The Scaffolding Surface: Every Place an Agent Reads Instructions From"
slug: the-scaffolding-surface
status: drafted
mastery:
seniority: mid
source: "Anthropic platform docs: Agent Skills overview (2026); Anthropic engineering blog: Writing effective tools for AI agents (2025); Anthropic engineering blog: Effective context engineering for AI agents (2025); explainx.ai: Steering Claude Code - All 7 Instruction Methods Explained (2026)"
durability: durable
prerequisites: [prompting-context-engineering/07]
created: 2026-08-10
updated: 2026-08-10
---

# The Scaffolding Surface: Every Place an Agent Reads Instructions From

## TL;DR
An agent never gets its behavior from one place. It is shaped by a set of distinct instruction surfaces - a system prompt, project-level configuration files, tool/function descriptions, on-demand skill bodies, deterministic hooks, and more - each with its own load timing, token cost, and reach. "Getting an agent to behave" is really the job of deciding, deliberately, which surface should carry which piece of guidance, because the surfaces are not interchangeable: the same instruction placed on the wrong surface either wastes budget every turn or silently never gets read at all.

## The idea
The prerequisite lesson (prompting-context-engineering/07) established that the context window is a finite budget, and that every token placed in it competes with every other token for the model's attention, cost, and latency. That lesson treated "context" as a single pool to be allocated wisely. This lesson opens that pool up and asks: allocated *from where*? A production agent's context on any given turn is not hand-assembled from a blank page - it is assembled by a harness (tool-use-agentic-loop/05) pulling from several different, structurally different sources, each of which was authored separately, updates on a different cadence, and gets read into context under different conditions.

This matters because the question "where should this instruction live?" has a real, consequential answer, and getting it wrong is one of the most common practical failures in agent engineering. Put a narrow, rarely-needed procedure in the system prompt and you pay its token cost on every single turn of every single session, forever, whether or not the task ever needs it - a direct violation of the budget discipline from the prerequisite lesson. Put a piece of guidance the agent needs on turn one into a file that's only read when explicitly referenced, and the agent will act without it and you'll never get an error message telling you why. The scaffolding surface is not a single wall you write instructions on; it's an ecosystem of walls, doors, and file cabinets, each suited to different information, and the engineering skill this whole subject teaches is choosing correctly among them.

## How it works

### Naming the surfaces
Different products name and slice these surfaces slightly differently, but the same handful of structural roles recur across essentially every mainstream coding-agent and agent-framework product as of 2026. It helps to sort them along two axes: **when do they load into context** (always, at the start of every session; on-demand, only when triggered; or never, they execute outside context entirely) and **who decides when they load** (a human wrote a hard rule that always fires; the model judges relevance from a description; or a deterministic system event fires it, no model judgment involved).

```
Surface                    When it loads              Who decides
--------------------------------------------------------------------------
System / developer prompt  Always, every turn          Fixed by design
Project instruction file   Always, session start       Fixed by design
Tool / function description Always (name+desc), full   Fixed (metadata) /
                            args only when called       model (invocation)
Skill / on-demand doc       Metadata always; body       Model judgment
                            only when triggered         (lesson 04)
Hook / deterministic script Never in context; fires     System event
                            on a lifecycle event         (lesson 10)
Slash command / macro       Never in context until      Explicit human
                            explicitly invoked           invocation
```

Concretely, in practice:
- **System / developer prompt** - the instructions injected on literally every call to the model, usually authored by whoever built the harness (the product vendor), not the end user. This is the most expensive surface per session, because its cost recurs every single turn.
- **Project-level instruction file** - a human- or team-authored file, usually loaded once at session start and kept in context (or re-injected after context compaction), that carries facts and conventions specific to this project: build commands, directory layout, house style, non-negotiable rules.
- **Tool/function descriptions** - the natural-language text plus schema attached to each callable tool. Every tool's *name and short description* is loaded whenever that tool is available (so the model knows the tool exists and roughly what it's for); the full argument schema and any longer usage notes are consulted when the model actually considers calling it.
- **Skills / on-demand documents** - content deliberately kept *out* of the always-loaded surfaces and pulled in only when a short piece of metadata (typically a name and a description) signals relevance to the current task. This is the deferred-loading pattern the rest of this subject is about (lessons 03-09).
- **Hooks and deterministic scripts** - code that runs in response to a lifecycle event (a file edit, a tool call, session start) and never itself occupies context; it can inject a message into context as a side effect, but the trigger for running it is not a model judgment call at all - it fires unconditionally on the event, every time (lesson 10).
- **Slash commands / macros** - a pre-written prompt or procedure a human explicitly invokes by name; it costs nothing until invoked, and unlike a skill, is never triggered by the model inferring relevance - a human decides.

### Worked example: routing five pieces of guidance to the right surface
Suppose you're building a coding agent and have five things you want it to know or do. The naive approach is "put it all in the system prompt." Walking through where each piece actually belongs makes the cost of that naive approach concrete:

```
Guidance                              Naive: system    Correct surface
                                       prompt cost
-----------------------------------------------------------------------
1. "Never run `rm -rf` without        ~15 tokens,       Hook (deterministic
   confirmation"                      every turn        block) - this must
                                                          never depend on the
                                                          model remembering;
                                                          a hook enforces it
                                                          outside model
                                                          judgment (lesson 10)
2. "This repo uses 2-space indent,    ~20 tokens,       Project instruction
   TypeScript strict mode"            every turn         file - true for
                                                          every session in
                                                          this project,
                                                          cheap, worth
                                                          always-on cost
3. "How to migrate this specific      ~2,000 tokens,    Skill - rare,
   legacy ORM's query syntax"         every turn even     specific, high
                                       on sessions that    token cost;
                                       never touch it      loaded only when
                                                            the task matches
4. "Read a file's contents"           Full schema        Tool description -
                                       always loaded       name+description
                                       (name+desc is        always on, full
                                       cheap; ~15          schema consulted
                                       tokens)              only at call time
5. "Run our release checklist"        ~500 tokens,       Slash command -
                                       every turn even      human explicitly
                                       on sessions that      invokes by name;
                                       never release         zero cost until
                                                              typed
```

Only items 2 and (the metadata sliver of) 4 genuinely earn a permanent, always-on slot. Item 1 is deterministic enough that model judgment shouldn't be in the loop at all. Items 3 and 5 are exactly the material the always-loaded-vs-on-demand distinction (lesson 03) exists to keep out of the hot path.

### Worked example: this repository as one instance of the pattern
This repository's own operating model is a small, inspectable specimen of exactly this surface-routing decision, worth walking through because it is a real file you can open.

> **Example (Aug 2026):** this repository's root `AGENTS.md` is the always-loaded surface - short, read at the start of every session, and it never contains the full detail of any single workflow. Instead it holds a dispatcher: one line per topic, each pointing to a file under `agent-docs/` (`learning-workflows.md`, `seniority-model.md`, `git-policy.md`, and others) that is loaded only when its documented trigger condition applies - "before authoring a lesson," "before committing," "before cutting a release." The full text of `agent-docs/release-policy.md` never enters context on a session that never touches a release. This is the always-loaded/on-demand split (lesson 03) implemented with plain files and natural-language trigger conditions instead of a formal skill-loading mechanism - one valid way to build the pattern, not the only one.

The interesting part for this lesson specifically is not the mechanism but the *surface-routing decision* it embodies: `AGENTS.md` itself is the "project instruction file" surface from the table above; each `agent-docs/*.md` file is functionally playing the role of an on-demand skill body, even though this repository doesn't use a dedicated skill-loading feature to implement it - the same structural idea (short always-on pointer, larger content deferred until triggered) can be built with nothing more than a markdown file and a disciplined convention of reading linked files before acting.

### Why the surfaces differ in reach, not just in load timing
A second axis, easy to miss, is *who the surface's author is* and *how far it reaches*. A system prompt is usually authored by the harness vendor and applies to every user of that product. A project instruction file is authored by a team and applies to everyone working in that repository. A skill might be authored by an individual and only installed in their personal environment. This matters for engineering the same way ownership boundaries matter in any layered system: a rule that needs to hold for every user of a product belongs on a different surface than a rule that's specific to one team's conventions, even if both could technically be phrased as "always follow this."

## Pros
- **Matches cost to value.** Routing guidance to the surface with the right load timing means expensive, rarely-needed content only costs tokens on the turns that actually need it - a direct, mechanical way to apply the context-budget discipline from the prerequisite lesson.
- **Matches enforcement strength to stakes.** Genuinely non-negotiable rules can be routed to a deterministic surface (a hook) that doesn't depend on the model remembering or prioritizing correctly, instead of hoping a system-prompt sentence gets obeyed under pressure.
- **Enables independent ownership and update cadence.** A vendor can update the system prompt, a team can update its project instruction file, and an individual can add a personal skill, without any of them needing write access to the others' surface.
- **Makes debugging tractable.** "The agent didn't know X" becomes a routing question - which surface was X supposed to live on, and did it actually load on this turn - rather than a vague appeal to "the model should have known."

## Cons
- **More moving parts to reason about.** A newcomer has to learn that instructions can come from half a dozen different places before they can predict what an agent will and won't know on a given turn; a single monolithic prompt is conceptually simpler, even though it scales worse.
- **Surface boundaries are not perfectly standardized across products.** What one vendor calls a "rule" another calls a "skill" or folds into "system prompt append" - the taxonomy in this lesson describes recurring structural roles, not a universal, product-agnostic API (see the harness/scaffolding lesson's note on inconsistent terminology).
- **Misrouting is a real, hard-to-detect failure mode.** Content routed to the wrong surface doesn't usually throw an error; it just quietly costs more than it should (over-included) or silently never gets read (under-included) - this exact failure category is the subject of lesson 05.
- **The right surface can change as usage patterns change.** A piece of guidance that was rare enough to defer to a skill can become common enough to deserve promotion to the always-loaded surface, and vice versa; the routing decision isn't "set once," it's periodically revisited.

## Alternatives
- **A single monolithic system prompt for everything** - simplest to reason about and to author, and genuinely adequate for a small, single-purpose agent with a short, stable instruction set. Breaks down as the instruction set grows: every addition taxes every single turn forever, and the prerequisite lesson's attention-dilution cost starts degrading reliability well before any token limit is hit.
- **Pure retrieval-augmented context (nothing "always loaded" except a minimal bootstrap)** - maximizes flexibility and minimizes fixed cost, but pushes the entire discovery problem onto the retrieval/trigger mechanism (lesson 04) and gives up the reliability of a small, guaranteed-present core of instructions that lesson 03 argues some content genuinely needs.
- **Configuration purely through code (no natural-language instructions at all, only deterministic logic)** - maximizes reliability for anything it covers, since there is no model-judgment step to fail, but cannot express the large fraction of real guidance that is heuristic, contextual, or requires judgment (see lesson 10 for exactly where this trade-off lands and where it doesn't).

## When to use it
Think in terms of "which surface does this belong on" any time you are adding new guidance to an agent - a new rule, a new piece of domain knowledge, a new procedure - rather than defaulting to "add it to the system prompt" or "add it to the project file" out of habit. It's especially worth doing deliberately once an agent's instruction set is being authored or maintained by more than one person, or once the always-loaded surfaces have grown large enough that you can feel the difference in latency or cost.

## When NOT to use it
For a tiny, single-session, single-purpose script that calls a model once or twice with a short, stable prompt, formally distinguishing surfaces is unnecessary ceremony - there's no session to accumulate cost across, no team to divide ownership among, and no on-demand mechanism worth building for content that's used every time anyway. Reach for a single prompt until the instruction set or the number of contributors grows enough to make the distinction pay for itself.

## Key takeaways / mental model
Picture an agent's instructions as a building with several distinct rooms, not one long corridor: a lobby everyone walks through on every visit (system prompt), a project noticeboard read once at the door (project instruction file), a reference desk you only approach when you have a specific question and the librarian's one-line card catalog entry tells you whether it's worth the walk (skills, lesson 04), a set of house rules enforced by the building's own locks regardless of what any visitor intends (hooks), and a set of buttons a visitor can press by name but that do nothing until pressed (slash commands). Every piece of guidance you write has a room it belongs in; the engineering job is choosing the room, not just writing the guidance well.

## Self-check questions
1. You're building an agent and want it to always refuse to commit directly to a `main` branch. Using this lesson's surface taxonomy, which surface(s) would you consider, and what would push you toward one over another?
2. A teammate proposes adding a 3,000-token "how to use our internal deployment tool" guide directly into the system prompt because "we want to make sure the agent always knows it." Using the reasoning from this lesson and its prerequisite, explain what's wrong with that plan and what you'd propose instead.
3. Pick any coding agent or agent product you have used or read about. Try to map its actual configuration surfaces (whatever it calls them) onto the six-row table in this lesson. Where does the mapping fit cleanly, and where does the product's terminology blur two structural roles from the table together?
4. Explain, in your own words, why "who decides when this loads" (fixed by design, model judgment, or a deterministic event) is a genuinely different question from "when does this load" (always, on-demand, or never in context) - and give an example of two surfaces that share one answer but differ on the other.
5. A rule currently lives in a rarely-triggered skill, but you've noticed the task it applies to now comes up in nearly every session. What would you consider changing, and why does this lesson describe surface routing as something to revisit rather than a one-time decision?

## References
- [Anthropic platform docs: Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Anthropic engineering blog: Writing effective tools for AI agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Anthropic engineering blog: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [explainx.ai: Steering Claude Code - All 7 Instruction Methods Explained (2026)](https://explainx.ai/blog/steering-claude-code-claude-md-skills-hooks-subagents-rules-2026)
- This repository's own `AGENTS.md` and `agent-docs/` (accessed 2026-08)
