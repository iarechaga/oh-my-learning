---
id: staff-engineers-path/09
subject: staff-engineers-path
title: Raising quality bars with reviews and technical standards
slug: raising-quality-bars
status: drafted
mastery:
seniority: staff
source: The Staff Engineer's Path (Tanya Reilly), Chapter 6 - "Good Influence" (raising the bar)
prerequisites: [staff-engineers-path/04, staff-engineers-path/05]
created: 2026-08-10
updated: 2026-08-10
---

# Raising quality bars with reviews and technical standards

## TL;DR
A staff engineer raises an organization's quality bar not by personally catching every mistake in every review, but by turning their judgment into reusable standards — checklists, review templates, worked examples of "good" — so the bar holds even when they're not in the room.

## The idea
An individual senior engineer improves quality locally: they write good code, catch bugs in the reviews they personally do, model good practices for whoever's watching. That's real, but it's bounded by their personal bandwidth and only reaches the reviews they attend and the people who happen to be nearby. A staff engineer aiming to raise the organizational quality bar has to solve a scaling problem: how does "the judgment I'd apply if I reviewed this myself" get applied to the hundreds of reviews they'll never see?

The answer is to externalize judgment into artifacts other people can use without you: a design-review checklist that encodes the questions you'd ask, a documented quality bar that says explicitly what "production-ready" means for this org, worked examples of both a strong and a weak version of a common artifact (a design doc, a postmortem) that let people calibrate by comparison rather than by guessing what you'd think.

## How it works

### From personal judgment to a checklist
**Worked example.** A staff engineer reviewing design docs keeps noticing the same gaps: docs that don't address rollback/failure scenarios, docs that don't name who's on the hook operationally, docs that skip alternatives considered. Reviewing each doc personally catches these gaps, but only for the docs she happens to review. She converts this into a design-review checklist: "Does this doc describe what happens when the primary approach fails? Does it name an operational owner post-launch? Does it list at least one alternative and why it was rejected?" Published and required for all design reviews in her org, this checklist now enforces roughly the same bar she'd apply personally, on every design doc, including the ones she'll never personally see — because any reviewer, not just her, can now check for these things.

### Setting the bar through examples, not just rules
Checklists are necessary but not sufficient — some quality judgments are hard to fully reduce to a checklist ("is this abstraction actually the right one?"). A complementary technique: curate and circulate real worked examples of strong and weak versions of a common artifact, annotated with *why* one is stronger. This calibrates reviewers' taste, not just their rule-following, and tends to generalize better to novel situations a checklist didn't anticipate.

### Review as a leverage point, not just a gate
Code review, design review, and architecture review are naturally high-leverage moments to raise the bar, because they're already a checkpoint every piece of work passes through — you don't need to invent a new process, you improve the standard applied at a process that already exists. A staff engineer often invests specifically in making *reviews themselves* better: templates that prompt reviewers to check the right things, calibration sessions where multiple reviewers discuss a borderline case together to converge on a shared standard, or simply reviewing junior reviewers' reviews to mentor their reviewing skill (directly overlapping with `staff-engineers-path/11`).

### The trade-off: standards vs. autonomy and speed
Every added standard is friction: a longer checklist means slower reviews, and a rigid bar applied uniformly can be wrong for a genuinely low-stakes piece of work (a quick internal script doesn't need the same rigor as a customer-facing payments change). Good quality-bar-setting is proportionate — it typically scales requirements to the stakes of what's being reviewed, rather than applying one bar everywhere, and it's revisited periodically so it doesn't calcify into bureaucracy that outlives its usefulness.

## Pros
- Scales one person's judgment across every review in the org, not just the ones they personally attend.
- Makes quality expectations explicit and consistent, reducing the "different reviewers enforce different standards" problem that frustrates engineers and produces inconsistent code/design quality.
- Doubles as a teaching tool — a good checklist or worked example set teaches newer engineers *why* the bar is where it is, not just *that* it exists.

## Cons
- A checklist is a floor, not a ceiling; teams can start "checking the boxes" without engaging with the underlying judgment the checklist was trying to encode, producing compliance without real quality.
- Standards that aren't revisited become outdated or overly bureaucratic, adding friction without adding value — someone has to own maintaining them.
- Setting a bar too high for the actual stakes involved slows everything down uniformly and breeds resentment, especially if applied without judgment to low-stakes work.

## Alternatives
- **Personal review of everything important** — the staff engineer stays the bottleneck reviewer for high-stakes work; ensures consistently high judgment on what they do review, but doesn't scale and creates a single point of failure/delay.
- **Automated tooling/linting for objective standards** — offloads mechanically-checkable quality bars (style, common bug patterns, security scanning) to tooling rather than human review; frees human review time for the judgment calls tooling can't make, and is a natural complement to, not a replacement for, checklist-based review standards.
- **Pure cultural osmosis** — rely on newer engineers absorbing quality norms by working alongside experienced ones over time, with no written standard; works slowly and inconsistently, especially as teams grow past the point where everyone works closely with the same senior people.

## When to use it
Invest in explicit quality bars and review standards when you notice the same category of gap recurring across multiple reviews/docs/designs — a repeated pattern is a signal the judgment is generalizable and worth externalizing — and especially as an org scales past the size where informal, in-person mentorship alone can carry the bar.

## When NOT to use it
Don't build heavyweight standards for a one-off situation that's unlikely to recur, and don't apply a uniform, high bar to genuinely low-stakes work — that's the standards equivalent of over-engineering. Also resist writing a checklist as a substitute for actually doing a few reviews yourself first; a checklist written from theory rather than from real, observed recurring gaps tends to miss what actually matters.

## Key takeaways / mental model
Your personal judgment doesn't scale past the reviews you personally attend; a checklist, a documented quality bar, and worked examples of strong-vs-weak do. Build them from real, recurring patterns you've observed, scale their rigor to the stakes of what's being reviewed, and revisit them so they don't calcify into bureaucracy that's disconnected from the judgment they were meant to encode.

## Self-check questions
1. Think of a mistake or gap you've seen recur across multiple reviews (code, design, or otherwise). Draft a two-to-three-item checklist that would catch it consistently, even applied by someone other than you.
2. Why is a checklist alone insufficient to raise a quality bar, and what does pairing it with worked examples add?
3. Describe a situation where applying your org's "highest" quality bar uniformly to a low-stakes piece of work would be the wrong call. What should scale the bar up or down?
4. How would you know a quality standard has calcified into bureaucracy rather than still encoding useful judgment? What would you do about it?

## References
- The Staff Engineer's Path (Tanya Reilly), Chapter 6: "Good Influence" (raising the bar).
