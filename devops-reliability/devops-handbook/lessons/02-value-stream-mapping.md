---
id: devops-handbook/02
subject: devops-handbook
title: Value Stream Mapping for Software Delivery
slug: value-stream-mapping
status: drafted
mastery:
seniority: senior
source: The DevOps Handbook (Kim, Humble, Debois, Willis), Part II
prerequisites: [devops-handbook/01]
created: 2026-08-10
updated: 2026-08-10
---

# Value Stream Mapping for Software Delivery

## TL;DR
A value stream map lays out every step a change goes through from "code committed" to "value delivered to the customer," recording process time and wait time at each step, so you can see the total lead time and find out where it's actually being lost — usually in the wait time between steps, not the work itself.

## The idea
Teams routinely misdiagnose why delivery is slow. Someone notices deploys feel painful and proposes "let's speed up the deploy" — but the deploy step might be 20 minutes out of a 6-week lead time. Value stream mapping (VSM), borrowed from lean manufacturing, forces you to look at the *whole* pipeline of a change — not just the part that's visible or annoying — and separate two very different quantities at each step: **process time** (how long the work itself takes once someone starts it) and **wait time** (how long the work sits in a queue before anyone starts it). The core lean insight the Handbook imports: in most software delivery pipelines, wait time dwarfs process time, often by 10x or more, and it's invisible unless you deliberately map it.

## How it works

### Building the map
You walk the actual path a real, recent change took — not the idealized process on a wiki — and for each step record: who touched it, how long they spent actively working on it (process time), and how long it sat waiting before that (wait time). You compute **%C/A** ("percent complete and accurate") at each step: the fraction of work arriving at that step that could be used as-is, versus rework/rejected/sent back.

**Worked example.** A team maps a typical feature from commit to production:

```
Step                    Wait time    Process time    %C/A
Code review              4 hrs         1 hr           85%
Merge to release branch  3 days        5 min          100%
QA environment deploy    2 days        30 min         70%  (30% bounced back for defects)
Manual QA testing        5 days        1 day          90%
Change approval board    7 days        15 min         95%
Production deployment    1 day         45 min         98%
--------------------------------------------------------
Total lead time: ~19 days, 2 hours   Total process time: ~2 days
```

Lead time is ~19 days; the actual work being done sums to about 2 days. **Process efficiency** = process time / lead time ≈ 10%. That 10% figure is the headline finding of most real VSM exercises — most of the calendar time isn't work, it's queueing.

### Reading the map: finding the real constraint
The map tells you where to invest next, echoing the Theory of Constraints logic from `phoenix-project/03`: improving a step's process time barely moves total lead time if that step isn't the binding constraint. In the example above, halving manual QA testing's 1-day process time saves half a day out of 19 — barely noticeable. But the 7-day wait for the change approval board and the 5-day wait for manual QA scheduling are the real targets: a pre-approved standard-change category (`devops-handbook/15`) could collapse the 7-day approval wait to zero, and automated test coverage (`devops-handbook/05`) could collapse the 5-day QA wait entirely by removing the human-scheduling bottleneck.

### %C/A as a quality signal, not just a speed signal
The 70% %C/A at the QA-environment-deploy step is itself diagnostic: three out of ten changes bounce back from that step needing rework, meaning work is flowing backward — a First Way violation (`devops-handbook/01`). A low %C/A at any step usually points to a missing quality gate earlier in the pipeline (here: insufficient automated testing before the QA deploy, per `devops-handbook/05`) rather than a problem at the step itself.

### Mapping across organizational boundaries, not just within a team
The Handbook stresses that the most valuable VSM exercises span the whole value stream — from a product idea, through Dev, through Ops, to the customer — not just the engineering-visible slice. A team that only maps its own sprint work will miss waits that happen entirely outside engineering: a security review queue, a legal/compliance sign-off, a hardware-procurement lead time for a new environment. Those cross-team waits are frequently the largest single contributors to lead time precisely because no single team owns or is incentivized to fix them.

## Pros
- Replaces intuition ("deploys feel slow") with a measured breakdown of where time actually goes, preventing wasted investment in the wrong fix.
- Makes wait time visible, which is otherwise invisible because no one is actively watching a queue — they only notice the work they're doing.
- Cross-team maps surface organizational bottlenecks that no single team can see or fix alone, creating a shared artifact to justify structural change.

## Cons
- Requires honest, current data from a real recent change — a map built from an idealized or outdated process description is worse than useless, because it hides the actual bottleneck.
- A one-time map goes stale; lead time bottlenecks shift as you fix them (fixing the approval-board wait might reveal the QA wait as the new binding constraint), so it needs to be a repeated practice, not a one-off exercise.
- Can become a political document — steps owned by other teams (security review, compliance sign-off) may be flagged as the bottleneck, which can create friction if not handled collaboratively.

## Alternatives
- **DORA delivery metrics** (`devops-handbook/16`) — measure the *outcome* (deployment frequency, lead time, MTTR, change failure rate) without mapping every intermediate step; faster to start, but doesn't tell you *where* in the pipeline the time is lost, only that it is.
- **Theory of Constraints "five focusing steps"** (`phoenix-project/03`) — a more general constraint-identification method; VSM is one concrete technique for applying it specifically to a delivery pipeline.
- **Ad hoc retrospectives** — gather qualitative "what felt slow" feedback from the team; faster and cheaper, but subject to recency bias and doesn't produce the quantitative wait/process breakdown a VSM gives you.

## When to use it
Use VSM at the start of a delivery-improvement effort, whenever "delivery feels slow" but no one can point to the specific bottleneck, or when you need a concrete artifact to justify cross-team investment (e.g., "our QA wait, not the deploy step, is costing us 5 days — we need automated test coverage, not a faster deploy script").

## When NOT to use it
Don't reach for a full VSM exercise when the bottleneck is already obvious and agreed (e.g., everyone already knows the nightly manual regression suite is the constraint) — just go fix it. Don't run it as a one-off compliance exercise disconnected from any commitment to act on the findings; a map that produces no follow-through just documents dysfunction without fixing it.

## Key takeaways / mental model
Total lead time = sum of (wait time + process time) across every step, spanning every team the change touches, not just engineering's visible slice. In most pipelines, process time is a small fraction of the total — the real leverage is almost always in collapsing wait time at the true constraint, not in speeding up work that's already fast.

## Self-check questions
1. In the worked example above, why would halving the manual QA testing process time (1 day -> 0.5 days) barely move total lead time, while removing the change-approval-board wait (7 days -> 0) would move it substantially?
2. A team's %C/A drops sharply at a step called "integration testing." What does that suggest is missing earlier in the pipeline, and which later lesson in this subject addresses the fix?
3. Why does the Handbook insist a value stream map should span organizational boundaries (security, legal, procurement) rather than stopping at engineering's edge? What's the risk of a map that stops early?
4. You've fixed the biggest bottleneck a VSM revealed. Why can't you treat the map as "done" — what has to happen next?

## References
- The DevOps Handbook (Kim, Humble, Debois, Willis), Part II: "Where to Start."
- See also: `phoenix-project/02` (work as flow, value streams) and `phoenix-project/03` (Theory of Constraints for IT).
