---
id: instruction-and-context-design/05
subject: instruction-and-context-design
title: "Failure Modes of Deferred Loading: Over-Triggering, Under-Triggering, and Silent Gaps"
slug: failure-modes-of-deferred-loading
status: drafted
mastery:
seniority: senior
source: "Anthropic engineering blog: Equipping agents for the real world with Agent Skills (2025); Anthropic Claude Docs: Skill authoring best practices (2026); SkillResolve-Bench: Measuring and Resolving Same-Capability Ambiguity in Agent Skill Retrieval, arXiv:2606.10388 (2026); FORTIS: Benchmarking Over-Privilege in Agent Skills, arXiv:2605.09163 (2026); Atlan: Agent Skill Best Practices - What Most Guides Skip (2026)"
durability: durable
prerequisites: [instruction-and-context-design/04]
created: 2026-08-10
updated: 2026-08-10
---

# Failure Modes of Deferred Loading: Over-Triggering, Under-Triggering, and Silent Gaps

## TL;DR
Deferred loading (lesson 04) only works if the agent loads the right resource at the right moment, and that judgment call fails in three distinct, recognizable ways: **over-triggering** (loads when it shouldn't, wasting context and diluting attention), **under-triggering** (fails to load when it should, leaving the agent to improvise without material it needed), and **ambiguity/collision** (two resources' trigger conditions overlap, so the agent loads the wrong one with full confidence). Each has a different root cause, a different symptom to watch for, and a different fix - conflating them leads to fixing the wrong thing.

## The idea
Lesson 03 established the always-loaded/on-demand split, and lesson 04 covered how a trigger description makes an agent decide, at run time, whether a given on-demand resource is relevant to the current task. That decision is a judgment call made by a model reading a short natural-language description and comparing it, in the moment, to whatever the current task looks like. Judgment calls are not deterministic function calls - they fail, and they fail in patterned ways worth naming individually rather than lumping together as "the trigger didn't work."

Why this matters enough for its own lesson: the three failure modes look similar from the outside (something about how a skill or a doc got loaded went wrong) but point to opposite fixes. A system suffering from over-triggering needs its descriptions narrowed and its scope tightened. A system suffering from under-triggering needs the opposite: descriptions broadened, more explicit trigger phrases added, gaps in coverage closed. Applying the under-triggering fix to an over-triggering problem (or vice versa) makes things worse, not better - which is exactly why naming the failure precisely, before reaching for a fix, is the actual skill being taught here.

## How it works

### Failure mode 1: Over-triggering
**What it is:** the agent loads an on-demand resource for a task that didn't actually need it. The description was written broadly enough, or worded ambiguously enough, that it matches tasks outside its real scope.

**Why it's a failure, not just harmless caution:** the entire economic case for deferred loading (lesson 03) is that most resources should stay out of context most of the time, because context is a scarce, degrading resource - more tokens in context does not mean more capability, and irrelevant material competes for the model's attention with material that actually matters to the current task. A resource that fires too often defeats its own purpose: it behaves like an always-loaded resource that happens to be implemented as an on-demand one, except worse, because its author assumed it would only show up when relevant and wrote it accordingly (narrower framing, fewer caveats about "this might not apply"). When it shows up anyway, it can actively mislead - the agent treats a loaded resource as evidence of relevance ("this got loaded, so it must apply here") and skews its plan toward instructions that don't actually fit the task.

**Worked scenario:** a repository defines two on-demand documents - one for "reviewing pull requests" and one for "writing commit messages" - and the "reviewing pull requests" description reads: *"Load this whenever inspecting or discussing recent code changes."* An agent asked to summarize what changed in the last commit for a status update (not a review, not a merge decision) matches "inspecting... recent code changes" and loads the full PR-review document - a multi-page checklist covering security review, test coverage thresholds, and approval criteria. None of it applies to writing a two-sentence summary. The agent now has to actively work out which parts of a loaded, seemingly-authoritative document to ignore, burns context budget it didn't need to spend, and risks folding review-checklist language into a status update where it doesn't belong. The fix is not "add more nuance to the review document" - the document was fine. The fix is narrowing the trigger: *"Load this before approving, requesting changes on, or leaving a formal review comment on a pull request"* - specific enough to exclude casual inspection.

### Failure mode 2: Under-triggering
**What it is:** the agent needed an on-demand resource, the resource existed, but nothing about the current task matched its description closely enough to load it. The agent proceeds without it and improvises - sometimes reasonably, often wrong in a way that looks confident.

**Why it's the more dangerous failure of the two:** over-triggering is self-announcing - a reader can usually tell that irrelevant material got pulled in, because it visibly doesn't fit. Under-triggering is silent. The agent doesn't know what it doesn't have; it just answers the question in front of it using whatever's already in context plus its general training, and nothing in the output flags "I was missing a document that would have changed this answer." This is precisely why Anthropic's own internal skill-quality work (per its 2026 documentation on maintaining 300+ internal skills) instruments trigger *rate*, not just trigger *correctness* - a skill that never fires cannot be evaluated for whether it fires well, and low-frequency firing is itself the signal something is wrong, independent of whether any single miss was ever traced back to a bad answer.

**Worked scenario:** a codebase has an on-demand document covering the house style for database migrations - specifically, that every migration adding a `NOT NULL` column must ship with a backfill step and a default value, because the schema is large enough that a blocking `ALTER TABLE` would cause an outage. Its description reads: *"Load this when writing a database migration."* An agent is asked to *"add a `status` column to the orders table"* - a request that never uses the word "migration" at all, even though writing one is exactly what the task requires. The description's trigger term doesn't match the task's actual vocabulary. The agent writes a plain `ALTER TABLE orders ADD COLUMN status VARCHAR NOT NULL` with no backfill, no default, no awareness that this pattern is disallowed - not because it disagrees with the house rule, but because it never saw the rule. The output looks completely reasonable on its own terms; the gap only surfaces later, in review, or worse, in production. The fix is broadening the description to match how the request is actually likely to be phrased: *"Load this when writing a database migration, or when a task involves adding/changing/removing a column, index, or constraint on an existing table - even if the word 'migration' isn't used."*

### Failure mode 3: Ambiguity / collision
**What it is:** two (or more) on-demand resources have descriptions that both plausibly match the current task, and the agent picks one - confidently, and not necessarily the more appropriate one - instead of loading both or asking.

**Why it's distinct from the first two:** over-triggering and under-triggering are about a single resource's threshold being miscalibrated (too loose or too tight). Ambiguity is a *relative* problem between two resources that, individually, might each have a perfectly reasonable description - the failure only exists because they overlap with each other. This is why fixing ambiguity usually means editing both descriptions together, in contrast to over/under-triggering fixes, which are usually local to one resource. 2026 research on this specific problem (SkillResolve-Bench, arXiv:2606.10388) frames it as "same-capability ambiguity": when a growing library of on-demand resources accumulates several entries that address similar-sounding needs, retrieval accuracy measurably degrades, because the model has to disambiguate between candidates that all score as plausibly relevant rather than choosing the one clearly-correct match.

**Worked scenario:** a system has two on-demand documents: one titled "formatting API error responses" with the description *"Load when an endpoint needs to return an error to a client,"* and another titled "handling internal service failures" with the description *"Load when a service encounters a failure it needs to respond to."* A task asks the agent to make an internal payment-processing endpoint return a structured error when a downstream call fails. Both descriptions plausibly match - "an endpoint... return an error" and "a service encounters a failure" both describe this task accurately, because the task genuinely sits at the boundary the two documents were meant to divide. The agent loads one (say, whichever scores marginally higher in whatever internal relevance signal it's using) and follows its formatting rules, missing the other document's requirement that internal-failure errors must be logged with a correlation ID before being returned. Nothing failed loudly - the agent followed a real, applicable document correctly. The fix is to make the two descriptions mutually exclusive by adding the boundary explicitly to both: the client-facing one gains *"...for errors returned directly to an external client"* and the internal one gains *"...for failures in service-to-service calls, before they are translated into a client-facing response"* - and, where the two genuinely need to compose (as in this scenario), a cross-reference stating that both apply together for this exact case.

### A comparison table for fast triage
```
Symptom                                  Likely failure mode      Where to look first
---------------------------------------  -----------------------  -----------------------------
Output contains material that doesn't    Over-triggering           Narrow the trigger description
fit the actual task; context feels                                 of the resource that loaded
bloated with irrelevant instructions

Output looks confident but violates a    Under-triggering          Broaden the trigger description;
rule/constraint that exists in an                                  check whether the task's actual
on-demand doc that never loaded                                    wording matches it

Output correctly follows one resource    Ambiguity / collision     Compare the two (or more)
but silently misses a requirement                                  resources' descriptions for
from a different, equally-applicable                                overlap; make boundaries
resource                                                            explicit in both
```

## Pros
Naming these three failure modes precisely - rather than treating "the trigger was wrong" as one undifferentiated bucket - gives a fast, reliable diagnostic: identify the symptom, map it to the mode, apply the mode-specific fix, instead of guessing at a rewrite and hoping it helps.

## Cons
- **Diagnosis still requires evidence you often don't have.** Under-triggering in particular is silent by construction - you frequently only find out it happened after a bad output is traced back to a missing resource, and by then the cost has already been paid.
- **Fixing one mode can induce another.** Broadening a description to fix under-triggering is the single most common way to accidentally create over-triggering for a different task; narrowing to fix over-triggering is the most common way to reintroduce under-triggering. The three modes trade off against each other, not independently.
- **Ambiguity fixes require touching multiple resources at once**, which is more disruptive than a local edit and easy to defer because it's nobody's individual resource's fault.

## Alternatives
- **Always-load everything relevant-looking ("when in doubt, load it")** - eliminates under-triggering by construction but reintroduces the exact context-cost problem deferred loading exists to solve (lesson 03); not a real alternative so much as reverting to the always-loaded default.
- **Ask the user/task-issuer to disambiguate explicitly** - genuinely effective for ambiguity/collision specifically (the agent surfaces "this could mean X or Y, which do you want?" instead of silently guessing), but doesn't scale to fully autonomous pipelines with no one to ask, and does nothing for under-triggering, where the agent doesn't know there's anything to ask about.
- **Automated trigger-rate monitoring** (instrumenting how often each on-demand resource actually loads, in production, over real tasks) - doesn't fix any individual failure but turns invisible under-triggering into a visible, measurable signal (a resource that never fires is a candidate for a broadened description or a redundant resource worth removing), which is why current practitioner guidance treats it as a required companion to writing trigger descriptions, not an optional extra.

## When to use it
Apply this triage whenever an agent's output is wrong or off in a way that traces back to "did it use the right supplementary material," which is most of the debugging surface in any system with more than a handful of on-demand resources (skills, reference docs, dispatched instruction files). It's also the right lens during design review of a *new* on-demand resource, before it ships: ask deliberately whether its description could over-fire, whether its trigger vocabulary matches how the task will actually be phrased, and whether it overlaps with anything that already exists.

## When NOT to use it
Don't reach for this framework on a system with only one or two on-demand resources and no ambiguity between them - the failure surface these three modes describe only becomes material once a library of triggerable resources exists that could plausibly compete or gap against each other. For a single skill in an otherwise empty library, the only real question is "does this description match the task," which is lesson 04's territory, not this one's.

## Key takeaways / mental model
Picture deferred loading as a set of motion-sensor lights, one per on-demand resource. Over-triggering is a sensor so sensitive it floods the room every time anyone walks past in the hallway. Under-triggering is a sensor so dim it stays dark even when someone's standing right under it. Ambiguity is two sensors covering overlapping floor space, so when someone stands in the overlap, only one light comes on and it might be the wrong one to actually see by. Three different sensor problems, three different fixes - and none of them is "install more lights" or "remove all the sensors."

## Self-check questions
1. An agent handling customer support tickets has an on-demand "refund policy" document with the description "Load when a customer asks for a refund." A customer writes "this product broke after two days, what are my options" - never using the word "refund" - and the agent responds without ever loading the refund policy, offering a solution that isn't actually one of the company's supported options. Which failure mode is this, and how would you fix the description?
2. A team notices their "security review" on-demand document loads on almost every single code-related task, including trivial documentation typo fixes. Is this over-triggering or under-triggering, and what's the first thing you'd check in the description?
3. Two on-demand documents exist: one for "writing SQL queries" and one for "writing analytics dashboards." A task asks the agent to "add a new chart showing weekly signups" - which requires both writing a SQL query and building a chart. Is this an ambiguity/collision case, an under-triggering case, or something else? What would the ideal outcome look like, and how would you get there?
4. Why does the lesson claim that fixing under-triggering (broadening a description) is "the single most common way to accidentally create over-triggering for a different task"? Construct a concrete example where broadening one resource's description to catch a missed case causes it to now over-fire on an unrelated task.
5. You're told that a particular skill "almost never fires" in production telemetry. Before concluding this is under-triggering that needs a broader description, what other explanation should you rule out first?

## References
- [Anthropic engineering blog: Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Anthropic Claude Docs: Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [SkillResolve-Bench: Measuring and Resolving Same-Capability Ambiguity in Agent Skill Retrieval (arXiv:2606.10388)](https://arxiv.org/pdf/2606.10388)
- [FORTIS: Benchmarking Over-Privilege in Agent Skills (arXiv:2605.09163)](https://arxiv.org/pdf/2605.09163)
- [Atlan: Agent Skill Best Practices - What Most Guides Skip](https://atlan.com/know/ai-agent/ai-agent-skills/agent-skill-best-practices/)
