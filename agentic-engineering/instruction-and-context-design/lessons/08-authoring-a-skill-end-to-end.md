---
id: instruction-and-context-design/08
subject: instruction-and-context-design
title: "Authoring a Skill End to End: Trigger, Body, and Supporting Files"
slug: authoring-a-skill-end-to-end
status: drafted
mastery:
seniority: senior
source: "Anthropic Claude Docs: Skill authoring best practices (2026); Anthropic engineering blog: Equipping agents for the real world with Agent Skills (2025); Atlan: Agent Skill Best Practices - What Most Guides Skip (2026); Agentman Blog: How Do You Build Your First Agent Skill? A Complete SKILL.md Anatomy Guide (2026); this repository's own agent-docs/learning-workflows.md as a case study (2026)"
durability: durable
prerequisites: [instruction-and-context-design/02, instruction-and-context-design/04, instruction-and-context-design/07]
created: 2026-08-10
updated: 2026-08-10
---

# Authoring a Skill End to End: Trigger, Body, and Supporting Files

## TL;DR
Authoring a skill is four sequential decisions: scope it to one coherent job narrow enough to describe precisely, write a trigger description that states both what it does and exactly when to load it (positively and negatively), structure the body so the most important constraints survive being read in isolation (lesson 06), and split supporting material into separate files only when doing so actually saves context on the common case. Skipping any one of the four produces a skill that either never fires, fires too often, or fires correctly and then gives bad guidance once loaded.

## The idea
Lesson 07 established what a skill is and when the underlying need clears the bar to be worth packaging. This lesson is the "now actually build it" step: given a real, recurring, describable need, how do you turn it into a skill that will hold up under lesson 05's failure modes instead of becoming a case study in one of them? The gap between "I understand what a skill is" and "I can write one that works" is exactly the gap this lesson closes - it's a craft with specific, learnable moves, not a mechanical translation of an idea into a template.

The reason this deserves its own worked walkthrough rather than a bullet list of tips: every decision made while authoring a skill is a trade-off already covered by an earlier lesson in this subject, applied concretely. Scoping trades completeness against describability (lesson 04). Trigger-writing trades sensitivity against precision (lesson 05's over/under-triggering). Body structure trades thoroughness against surviving out-of-order or isolated reads (lesson 06). File-splitting trades a leaner default load against added indirection (lesson 02's cost of structured signal). Authoring a skill well means making each of these four calls deliberately, in order, rather than writing a document and hoping it happens to land well on all four axes at once.

## How it works

### Step 1: Scope the skill to one coherent job
Before writing a single word of the trigger description, decide what this skill is *for*, precisely enough to state in one sentence, and resist the pull to fold in adjacent-but-different needs just because they showed up in the same conversation that motivated the skill. A skill that tries to cover two distinct jobs ends up with a trigger description vague enough to match both, which directly invites lesson 05's over-triggering and ambiguity failures - a vague-enough-to-cover-everything description is often the symptom of scope creep at authoring time, not a triggering bug to fix later.

**Worked example - the running scenario for this lesson:** a team keeps having their agent write database migrations that don't handle backward compatibility correctly (the exact scenario introduced in lesson 07's first worked example). The temptation is to scope a skill broadly: "how to write good database code." Resist it - that's actually several different jobs (migration safety, query performance, schema design review) each with its own trigger vocabulary and its own body. The right scope for *this* need is narrower and more precise: "safely writing schema-changing migrations against a table already receiving production traffic." Narrow enough to describe tightly; broad enough to still be worth packaging (it recurs across every schema change the team makes, per lesson 07's bar).

### Step 2: Write the trigger description - what it does, and when, stated both ways
The trigger description is the only thing the agent sees before deciding to load the rest (lesson 02's cheap-metadata tier), so it carries the entire weight of avoiding lesson 05's three failure modes. Current practitioner guidance on this (2026) converges on a consistent recipe: state what the skill does, then state when to use it with concrete trigger phrasing that matches how the task will actually be worded - not just the term the author has in their head - and, where a neighboring skill could plausibly compete for the same task, state explicitly what this skill does *not* cover.

**Applying it to the running example:**

Weak version (too narrow, invites under-triggering - the exact failure worked through in lesson 05):
> "Load this when writing a database migration."

This misses every task phrased as "add a column," "drop this index," or "change this constraint" that never uses the word "migration" - the precise under-triggering scenario from lesson 05.

Better version:
> "Use when writing, reviewing, or modifying a schema change (migration, ALTER TABLE, adding/removing/renaming a column, index, or constraint) against a table that already has production data or traffic. Covers backward-compatibility, backfill, and rollout-safety concerns for schema changes. Does not cover query performance tuning or read-path schema design questions for tables with no existing data."

This states what it does (backward-compatibility/backfill/rollout safety for schema changes), states when in vocabulary that matches how the task is likely to be phrased (not just "migration"), and explicitly excludes a plausible neighbor (query performance) to reduce ambiguity/collision risk if a "query performance" skill exists or gets added later.

### Step 3: Structure the body so it survives being the only thing loaded
Once the trigger fires, the body is what the agent actually acts on - and lesson 06's discipline applies directly here: write the body as if this skill might be the only material currently in the agent's effective attention, restating its own applicability rather than assuming the trigger description (which may no longer be in view once the full body loads) already established it. A good body, for this running example, front-loads the single most important constraint, then gives the mechanism, then gives worked examples with concrete before/after states - not because that's an arbitrary template, but because each piece does a specific job:

```
1. Restate scope in one line   -> re-establishes applicability even if
                                   read in isolation (lesson 06)
2. State the non-negotiable    -> the one rule that must never be
   constraint first              violated, placed where position-in-
                                   context favors it (lesson 06)
3. Give the mechanism           -> the actual how: steps, checks, or
                                   a short decision procedure
4. Give 1-2 worked examples     -> concrete before/after, not abstract
   with real before/after        description - agents pattern-match
   states                        against examples more reliably than
                                   against prose rules alone
5. Name the escape hatch        -> what to do when a real case doesn't
                                   fit the common pattern (avoids the
                                   skill giving confidently wrong advice
                                   on its own edge cases)
```

Applied to the running example, the body's first two lines might read:

> "This skill applies to schema changes against tables with existing production data or traffic. **Non-negotiable: never ship a schema change that would block writes or reads on a table already receiving traffic** - specifically, never add a `NOT NULL` column without a default value and a backfill step, and never add a blocking index without an online/concurrent index-creation mechanism where the database supports one."

Then the mechanism section walks through the actual procedure (add the column nullable with a default first, backfill in batches, add the `NOT NULL` constraint in a separate migration once backfill completes), and the worked-examples section shows one full before/after migration pair doing this correctly and one showing the naive, unsafe version it's meant to replace - concrete code, not just a description of the rule, because (per current skill-authoring guidance) agents produce more reliable output when they can pattern-match against an exact example rather than reconstruct one from a prose description alone.

### Step 4: Decide what's inline vs. a supporting file
Not everything belongs in the body. The test is simple and directly tied to lesson 07's progressive-disclosure structure: **does this material help on essentially every task that triggers the skill, or only on some of them?** If every task that triggers the skill needs it, it belongs inline in the body (splitting it out just adds an indirection cost - the agent has to decide to open a second file - for something it needed anyway). If only some tasks need it, it belongs in a separate supporting file that the body references by name, so its cost is only paid on the tasks that actually need that depth.

**Applied to the running example:**
- The non-negotiable constraint and the core mechanism (Step 3, items 1-3) belong inline - virtually every triggering task needs to know the rule and the basic procedure.
- The two compact worked examples belong inline too - they're short, and seeing at least one correct/incorrect pair is close to universally useful for this skill's scope.
- A longer reference covering database-specific syntax differences for online index creation across several database engines does **not** belong inline - most individual tasks only involve one engine, so loading syntax details for every engine on every trigger wastes the tier-2 budget the body is supposed to protect (lesson 02, lesson 07). This belongs in a separate file the body points to by name ("for engine-specific online-index syntax, see the engine syntax reference"), loaded only on the tasks that actually need it.
- A helper script that checks a migration file for the unsafe pattern automatically (rather than relying on the agent to check by reading the rule) is a third kind of supporting material - not prose to load into context at all, but something the body can tell the agent to *run*, whose output (not its own source) is what enters context. This is the deepest tier of progressive disclosure: material the agent never reads directly, only its result.

### A second, shorter worked example to check the pattern generalizes
To confirm this four-step process isn't specific to database migrations, apply it tersely to a different domain: a skill for "converting a third-party API's error response into this team's internal standard error format."
- **Scope:** narrowly, just the conversion/mapping step - not general API-integration guidance, not authentication handling.
- **Trigger:** "Use when handling or transforming an error response from an external API call into this codebase's internal error format. Does not cover retry/backoff policy for failed external calls (see the separate retry-policy guidance) or authentication-failure handling specifically."
- **Body:** restate scope, state the non-negotiable first (e.g., "never surface the third-party API's raw error message or status code directly to internal callers - always map to the internal error taxonomy"), give the mapping mechanism, give one or two worked before/after examples of a real third-party error payload mapped to the internal format.
- **Supporting files:** a full field-by-field mapping table covering every error code a specific third-party API can return belongs in a separate reference file (needed only when a task involves that specific API and that specific code, not on every trigger); the core mapping principle and the one or two most common cases stay inline.

The same four decisions, in the same order, produce a well-scoped, well-triggered, well-structured skill regardless of domain - which is the actual generalizable content of this lesson, not the specific migration or error-mapping content used to illustrate it.

## Pros
- **Produces skills that hold up under real usage**, not just under the one scenario the author had in mind while writing it - because each step directly defends against a specific, named failure mode from earlier lessons rather than relying on general good writing instinct.
- **Makes review tractable.** A reviewer can check a candidate skill against this four-step structure directly ("is the scope one coherent job? does the trigger state both what and when, positively and negatively? does the body front-load the non-negotiable? is the file split justified by per-task variability?") instead of reviewing holistically and hoping to catch problems.
- **Reuses the same process across very different domains** (the migration-safety and error-mapping examples above), so the skill of authoring skills transfers, rather than having to be relearned per topic.

## Cons
- **Real discipline overhead per skill.** Four deliberate decisions, each requiring real thought (not fill-in-the-blank), is slower than writing a skill in one pass and shipping it; for a very low-stakes, easily-corrected need, this process can cost more than the skill itself is worth (echoing lesson 07's "does it clear the bar" question).
- **Step 4's inline-vs-file judgment is genuinely hard to get right on the first attempt** without usage data - it's easy to guess wrong about which material is needed "on essentially every trigger" versus "only sometimes" before the skill has actually been used a few times; expect to revise the split after real usage reveals the guess was off (lesson 09 covers evaluating this after the fact).
- **A well-authored body doesn't guarantee a well-triggered skill** - Steps 3 and 4 can be executed perfectly and the skill can still fail via lesson 05's over/under-triggering or ambiguity modes if Step 2 wasn't done carefully; the four steps are sequential dependencies, not independent safety nets, so a weak trigger undermines a strong body regardless of how well the later steps went.

## Alternatives
- **Write the whole skill as one undifferentiated block of prose, no explicit scope/trigger/body/file separation** - faster to draft, but conflates decisions that trade off against each other differently (scope vs. describability, body structure vs. isolated readability, file-splitting vs. per-task cost), making it much harder to diagnose *which* decision was wrong when the skill underperforms later.
- **Generate a first draft with an LLM from a natural-language description of the need, then edit against this four-step checklist** - a genuinely common and effective 2026 practice (some current skill-authoring workflows explicitly use one model instance to draft a skill and a second, separate instance to test whether it triggers and behaves correctly) - useful for speed, but the four-step structure in this lesson is still what a human reviewer should check the draft against, since an LLM draft can just as easily produce a vague, over-broad trigger as a human can.
- **Skip authoring entirely and rely on always-loaded instructions for this need** - reasonable specifically when lesson 07's bar isn't cleared (the need doesn't really recur, or isn't expensive enough to get wrong); not a real alternative once the bar is cleared, since it reintroduces the always-loaded budget problem lesson 03 exists to avoid.

## When to use it
Apply this four-step process any time a candidate skill has cleared lesson 07's bar (recurs, expensive to get wrong, describable enough to trigger) and is actually being authored - which is the entire practical payoff of everything covered so far in this subject. It's equally applicable whether the skill is being drafted by hand or drafted by an LLM and then reviewed against this structure.

## When NOT to use it
Don't run the full four-step process for a trivial, low-stakes need that only marginally clears lesson 07's bar - a lightweight version (a short trigger, a short body, no file-splitting decision at all because there's no material variable enough to justify it) is proportionate, and forcing every candidate skill through the same heavyweight process regardless of stakes is its own form of wasted ceremony. Also don't use this process to force a need into skill shape when Step 1's scoping repeatedly fails to find one coherent job - that's a signal the need might not actually be skill-shaped at all, and is worth revisiting against lesson 07's three-question bar, or reconsidering as a hook or command instead (lesson 10) if what's actually wanted is deterministic, not model-judged, application.

## Key takeaways / mental model
Authoring a skill is not "write down what I want the agent to know" - it's four separate, sequential engineering decisions, each defending against a specific failure this subject has already named: scope defends against an undescribable, over-broad skill; the trigger defends against lesson 05's over/under-triggering and collision; the body's structure defends against lesson 06's out-of-order and isolated-read risk; and the inline-vs-file split defends against paying for material most triggering tasks never needed. Skipping a step doesn't just weaken that one aspect - it reintroduces the exact failure mode that step exists to prevent.

## Self-check questions
1. You're asked to author a skill from the request "help the agent write better error messages." Walk through Step 1 (scoping) - what's wrong with this request as stated, and what would you ask before writing anything?
2. Take the weak trigger description "Load this when working with dates" (imagine it's for a skill about handling timezone-aware date arithmetic correctly) and rewrite it following Step 2's recipe - what it does, when to use it stated in likely task vocabulary, and what it explicitly does not cover.
3. For the running database-migration skill in this lesson, explain why the "never surface the raw third-party error" non-negotiable (from the second worked example) belongs in the body's first lines rather than in a separate supporting file, using this lesson's own inline-vs-file test from Step 4.
4. A colleague drafts a skill body that reads well from top to bottom but starts with three paragraphs of background before stating its actual constraint. Using lesson 06's "position in context" finding, explain concretely what could go wrong, and how you'd restructure it.
5. Give an example of a piece of supporting material that fails Step 4's test - that is, something an author might be tempted to split into a separate file, but that actually belongs inline because most triggering tasks need it. Justify your answer using the test itself, not just intuition.

## References
- [Anthropic Claude Docs: Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Anthropic engineering blog: Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Atlan: Agent Skill Best Practices - What Most Guides Skip](https://atlan.com/know/ai-agent/ai-agent-skills/agent-skill-best-practices/)
- [Agentman Blog: How Do You Build Your First Agent Skill? A Complete SKILL.md Anatomy Guide](https://agentman.ai/blog/build-your-first-agent-skill-skillmd-anatomy)
- This repository's own `agent-docs/learning-workflows.md` as one inspectable case study of a scoped, triggerable instruction document.
