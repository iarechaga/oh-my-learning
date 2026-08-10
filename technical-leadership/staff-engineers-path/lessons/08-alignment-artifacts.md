---
id: staff-engineers-path/08
subject: staff-engineers-path
title: Decision records and alignment artifacts that scale
slug: alignment-artifacts
status: drafted
mastery:
seniority: senior
source: The Staff Engineer's Path (Tanya Reilly), Chapter 5 - "Guiding a project to completion" (writing things down)
prerequisites: [staff-engineers-path/05, staff-engineers-path/07]
created: 2026-08-10
updated: 2026-08-10
---

# Decision records and alignment artifacts that scale

## TL;DR
As the number of people affected by a decision grows, verbal alignment stops scaling — the same decision gets re-litigated in every meeting it wasn't written down for. Lightweight, durable artifacts (decision records, one-pagers, status updates) let a decision made once stay made, and let people who weren't in the room get aligned asynchronously.

## The idea
Alignment achieved in a meeting only covers the people in that meeting, at that moment, with their memory of it intact. Three weeks later, someone who wasn't there — a new hire, someone from another team, even an attendee who's since forgotten the nuance — asks "wait, why did we decide this?" and, without a written record, the answer depends entirely on someone's memory or a willingness to re-explain the whole reasoning from scratch. At small scale (a handful of people, a short project) this is a tolerable amount of friction. At staff scope — decisions affecting multiple teams over months or years — this friction compounds into real cost: repeated re-litigation, drift as different people remember the decision differently, and stalled progress every time someone new needs to be brought up to speed.

Alignment artifacts solve this by making the decision, and the reasoning behind it, durable and self-service. They don't replace conversation — the conversation is still where the decision gets made — but they capture its outcome so the conversation doesn't have to happen again for every new stakeholder.

## How it works

### The core artifact: a decision record
A decision record (sometimes called an Architecture Decision Record, or ADR) captures one specific, bounded decision:
- **Context** — what problem prompted this decision, and what constraints were in play.
- **Decision** — what was actually decided, stated unambiguously.
- **Alternatives considered** — what else was on the table, and why it wasn't chosen (this is often the most valuable part — it preempts "but why didn't we just do X" months later).
- **Consequences** — what this decision commits you to, including known downsides accepted knowingly rather than discovered later.
- **Status** — proposed / accepted / superseded (decisions get revisited; a stale, unmarked ADR that contradicts current reality is worse than no ADR).

**Worked example.** A team debates whether to use synchronous REST calls or an async event queue for a new integration. The meeting reaches a decision: async, because the caller doesn't need an immediate response and this decouples the two services' deploy schedules. Without a decision record, two months later a new engineer proposes "why don't we just call it synchronously, it'd be simpler" — and the team either re-has the entire debate, or someone senior has to personally remember and re-explain the reasoning. With a short decision record (even five sentences: context, decision, two alternatives considered with one line each on why they lost, expected consequence), the new engineer reads it in two minutes, either finds their concern already addressed or raises a genuinely new point the original record didn't anticipate — either way, real time is saved and the original reasoning isn't lost.

### Status updates as an alignment artifact
For an ongoing project (especially one being driven per `staff-engineers-path/07`), a short, regularly-cadenced status update — what's done, what's next, what's blocked, what changed since last time — serves a similar function at the project level: it lets stakeholders stay aligned without needing a meeting, and it creates a visible trail of "did this project actually progress" that protects against silent stalling. A good status update takes minutes to skim and answers "do I need to do anything" for each reader.

### Calibrating artifact weight to the decision's cost
Not every decision needs a formal ADR — writing one for a decision that's cheap to reverse and affects only your own team is often not worth the overhead. The right question: *what does it cost if this decision gets re-litigated or misremembered later, versus the cost of writing it down now?* High-cost-to-reverse, multi-team decisions justify a full decision record; small, local, reversible ones are fine as a quick chat-message summary, or no artifact at all.

## Pros
- Lets alignment happen asynchronously and scale past the people physically in the original meeting, which is essential once a decision affects more people than could realistically attend one conversation.
- Preserves the *reasoning*, not just the outcome — the "alternatives considered" section is often what prevents the same debate from recurring.
- Creates institutional memory that survives individual turnover; a team can lose the person who made a decision and still understand why it was made.

## Cons
- Writing genuinely useful artifacts (concise, honest about trade-offs, not just a rubber-stamp summary) takes real effort and is easy to do badly — a bloated or vague decision record is nearly as useless as none at all.
- Artifacts go stale; an ADR marked "accepted" for a decision that was later reversed, with no status update, actively misleads anyone who finds it later — someone has to own keeping the record current.
- Over-formalizing every small decision creates process overhead that slows teams down without adding proportional value; calibrating "which decisions deserve an artifact" is itself a judgment call that's easy to get wrong in either direction.

## Alternatives
- **Meeting notes distributed by email/chat** — lighter-weight, faster to produce, but typically capture *what happened* rather than *why*, and are usually not maintained/updated afterward, so they decay into an inaccurate record faster than a purpose-built decision record.
- **A living wiki page per system/decision area** — continuously edited rather than point-in-time, avoiding the "stale ADR" problem, but loses the historical trail of *why* a past decision was made once it's edited over, unless the wiki tooling preserves history well.
- **Tribal knowledge / verbal culture** — no artifacts at all, relying on people remembering and re-explaining as needed; works only at very small scale or very low team turnover, and is the default failure mode this lesson is a response to.

## When to use it
Write a durable alignment artifact whenever a decision is expensive to reverse, affects more people than were in the room when it was made, or is likely to be questioned again later by someone without the original context (new hires, other teams, future-you in six months).

## When NOT to use it
Skip the formal artifact for small, cheap, easily-reversible, single-team decisions — a decision record for "we're naming this variable `retryCount`" is pure overhead. Also don't let writing the artifact become a substitute for actually having the conversation and reaching real alignment first; a beautifully written decision record documenting a decision nobody actually agreed to just documents the disagreement more precisely. Finally, never leave a superseded decision record marked "accepted" — an out-of-date artifact that looks current is more dangerous than no artifact, because it actively misleads readers who trust it.

## Key takeaways / mental model
Alignment achieved verbally covers only the room it happened in; alignment written down (context, decision, alternatives considered, consequences, status) scales to everyone who reads it later, including people who weren't there. Weight the artifact to the decision's cost of being re-litigated or forgotten, and keep it current — a stale record is worse than none.

## Self-check questions
1. Recall a decision at your work that got re-litigated more than once. Would a short decision record (context, decision, alternatives considered) have prevented that, and what would it have said?
2. Why is the "alternatives considered" section often the most valuable part of a decision record, more than the decision itself?
3. Give an example of a decision that's NOT worth writing a formal record for, and explain what makes it different from one that is.
4. What goes wrong when a decision record is written but never updated after the decision is later reversed? How would you prevent that in practice?

## References
- The Staff Engineer's Path (Tanya Reilly), Chapter 5: "Guiding a project to completion" (writing things down / status updates).
