---
id: staff-engineers-path/05
subject: staff-engineers-path
title: Defining and communicating technical direction
slug: technical-direction
status: drafted
mastery:
seniority: staff
source: The Staff Engineer's Path (Tanya Reilly), Chapter 3 - "Creating a technical vision"
prerequisites: [staff-engineers-path/02, staff-engineers-path/03, staff-engineers-path/04]
created: 2026-08-10
updated: 2026-08-10
---

# Defining and communicating technical direction

## TL;DR
Technical direction is a written, shareable answer to "where are we headed and why" for a system or domain — distinct from a vision (aspirational, longer-term, less concrete) and a strategy (the specific plan to get there). Writing it down and circulating it for real feedback is what turns one engineer's opinion into an organization's shared, actionable plan.

## The idea
Without an explicit technical direction, teams default to making locally-optimal decisions that drift apart over time — two teams independently "solve" the same problem differently, a new hire has no way to know which of five competing patterns is the one to follow, and six months of quiet disagreement surfaces all at once during a contentious design review. A staff engineer's job is often to make the implicit direction explicit: to write down what "good" looks like for a domain, in enough detail that other engineers can use it to make their own decisions consistently, without staff-level oversight on every single choice.

Reilly distinguishes three related but different artifacts:
- **Vision** — where we want to be in 3-5 years; aspirational, doesn't need to specify *how*.
- **Direction** — the nearer-term technical stance: what patterns, technologies, and principles to converge on now, and why, so that day-to-day decisions naturally move toward the vision.
- **Strategy** — the specific plan (with sequencing, ownership, milestones) for how a particular initiative gets from here to there.

This lesson focuses on direction: the connective tissue between an aspirational vision and an executable plan, and the artifact staff engineers write most often.

## How it works

### The shape of a technical direction document
A useful direction doc typically covers:
1. **Current state** — an honest description of where things stand today, including the parts that are messy; a direction doc that pretends the current state is fine has no reason to exist.
2. **Where we're headed and why** — the target state, tied explicitly back to business/strategic context (`staff-engineers-path/03`) so readers understand *why* this direction, not just *what* it is.
3. **Principles, not just point decisions** — general rules ("new services default to async messaging over synchronous calls for cross-team communication unless latency requirements make that impossible") that let other engineers extrapolate to situations the document didn't explicitly cover. A list of specific approved technologies goes stale; principles age better.
4. **What this does NOT cover / open questions** — scoping honestly, and naming unresolved tensions rather than hiding them, builds more trust than a document that claims false completeness.
5. **How to get involved / give feedback** — direction documents are stronger when co-owned; naming a review process signals this isn't a decree.

**Worked example — before and after.** A staff engineer notices five teams have five different approaches to service-to-service authentication, some insecure. A weak, direction-less intervention: quietly telling each team lead "you should use mTLS" in separate conversations — slow, inconsistent, and easily forgotten. A direction document instead states: *current state* (five inconsistent auth patterns, two audited as non-compliant); *direction* (all internal service-to-service calls converge on mTLS via the shared service mesh within two quarters); *principle* ("no new service ships without mesh-managed auth; exceptions require a documented waiver from the security team"); *open question* ("legacy batch jobs that can't run in the mesh yet — proposal: allow a time-boxed exception, revisit in Q3"). This is reviewable, arguable, and — once agreed — becomes the shared reference that makes every future related decision faster, because teams don't need to re-litigate the question each time.

### Getting real feedback, not rubber-stamp approval
A direction document circulated only to people who will agree is a wasted exercise — it doesn't test the direction, it just performs consensus. Deliberately seek out the engineers most likely to disagree or to be most affected by constraints the document doesn't yet know about (the team running the legacy batch jobs in the example above), and treat their pushback as information rather than an obstacle to route around. A direction that survives contact with its skeptics is far more likely to actually hold up when teams start executing against it.

### Direction is a living artifact, not a one-time announcement
A direction document that's written once and never revisited becomes exactly the kind of stale, ignored policy that erodes trust in future direction-setting. Staff engineers typically build in an explicit revisit cadence (e.g., "we'll reassess this direction in two quarters, or sooner if a stated assumption breaks") and update it when reality diverges from the plan — this echoes the "state your bets' assumptions explicitly" discipline from `staff-engineers-path/03`.

## Pros
- Converts many one-off, inconsistent local decisions into a shared, reusable reference — new engineers and other teams can self-serve decisions instead of needing a staff engineer's direct involvement each time.
- Written artifacts scale in a way conversations don't: a document can be linked, referenced in a design review, and enforced consistently, whereas verbal guidance decays and varies by who heard it.
- Forces the author to make their reasoning explicit and defensible, which surfaces weak assumptions before they get baked into a dozen teams' code.

## Cons
- Writing a genuinely good direction document is slow and easy to underestimate — gathering real cross-team feedback, in particular, takes calendar time that's hard to compress.
- A direction document with no organizational authority behind it (no sponsor, no enforcement mechanism) risks becoming "yet another doc nobody follows," which is worse than not writing it, since it signals that direction-setting doesn't matter.
- Overly detailed, point-decision-heavy documents go stale fast and become a maintenance burden; overly abstract, principle-only documents leave too much ambiguity to actually guide day-to-day decisions — calibrating the right level of detail is a real skill, not a solved problem.

## Alternatives
- **Architecture Decision Records (ADRs) per decision** — smaller-grained, point-in-time records of individual decisions rather than a holistic direction; useful as building blocks, but don't by themselves convey an overarching "why" the way a direction document does — see `staff-engineers-path/08` for these as an alignment artifact.
- **Tech radar (adopt/trial/assess/hold)** — a lighter-weight, technology-inventory-style artifact popularized by ThoughtWorks; communicates *what's allowed* without necessarily explaining the underlying principles or business context a full direction document provides.
- **Verbal/informal direction-setting via influence and 1:1s** — works at small scale (a handful of teams, an org where the staff engineer already has deep personal relationships) but doesn't scale past that, and leaves no artifact for anyone who wasn't in the room.

## When to use it
Write an explicit technical direction when you observe teams solving the same class of problem inconsistently, when a domain is about to scale past what implicit tribal knowledge can hold together, or when you're about to ask multiple teams to make coordinated investment (like the mTLS migration) and need a shared artifact to rally around.

## When NOT to use it
Don't write a heavyweight direction document for a decision that affects only your own team, or for a fast-moving area where the "right" direction is likely to change within weeks — a lighter ADR or a conversation is more appropriate. Also avoid writing direction in a vacuum without gathering feedback from the teams it constrains; a direction imposed rather than negotiated tends to be quietly ignored.

## Key takeaways / mental model
Direction is the layer between vision (aspirational) and strategy (executable plan): state the current state honestly, the target state and why, principles that generalize beyond specific decisions, and open questions you haven't resolved — then actively seek disagreement before calling it done, and revisit it on a cadence rather than treating it as permanent.

## Self-check questions
1. Find (or imagine) a case where multiple teams solved the same problem in inconsistent ways. Draft the "current state" and "principle" sections of a direction document that would unify them.
2. Why are principles more durable than a list of approved specific technologies in a direction document? Give an example of a principle that would survive a technology migration a point-decision list wouldn't.
3. Explain why circulating a direction document only to people likely to agree undermines its purpose, even if it gets approved faster that way.
4. What's the difference between a technical vision, a technical direction, and a strategy? Give an example of each for the same underlying problem.

## References
- The Staff Engineer's Path (Tanya Reilly), Chapter 3: "Creating a technical vision".
