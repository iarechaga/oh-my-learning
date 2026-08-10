---
id: phoenix-project/03
subject: phoenix-project
title: Theory of Constraints for IT Operations
slug: theory-of-constraints-it
status: drafted
mastery:
seniority: senior
source: The Phoenix Project (Kim, Behr, Spafford), Part 1-2
prerequisites: [phoenix-project/01, phoenix-project/02]
created: 2026-08-10
updated: 2026-08-10
---

# Theory of Constraints for IT Operations

## TL;DR
In any system that moves work through a series of stages, total system throughput is capped by its single slowest stage — the **constraint** (or bottleneck) — no matter how much you improve any other stage. Eliyahu Goldratt's Theory of Constraints (introduced into the novel through the character Erik, and modeled on Goldratt's own book *The Goal*) says: find the constraint, protect and exploit it ruthlessly, subordinate everything else to it, and only then invest in elevating its capacity — and once you do, a new constraint will emerge elsewhere, so the process repeats. In Parts Unlimited, the constraint is a person: Brent, the only engineer who understands enough of the company's systems to safely make most high-risk changes.

## The idea
The Theory of Constraints (ToC) originates in manufacturing: a factory with five sequential machines, each with different processing capacity, can never produce faster than its slowest machine — call it Machine 3, capable of 100 units/hour when Machines 1, 2, 4, and 5 can each do 150+. Speeding up Machine 1, 2, 4, or 5 does *nothing* for total output, because their extra capacity just piles up as unfinished inventory waiting in front of Machine 3. The only way to increase the factory's total throughput is to increase what flows through Machine 3 — either by making Machine 3 itself faster, offloading some of its work elsewhere, or making sure Machine 3 is never sitting idle waiting on something upstream.

Erik's insight, delivered to Bill through a deliberately disorienting series of "go look at the plant floor" exercises, is that IT operations is the same kind of system, and Parts Unlimited's constraint isn't a machine — it's Brent. Nearly every non-trivial change, incident, or deployment at the company eventually routes through Brent, because he is the only person who understands enough of the tangled, undocumented systems to do it safely. Every other engineer, however skilled, is effectively "Machine 1, 2, 4, or 5" — their work piles up waiting for Brent's attention (analogous to inventory piling up in front of Machine 3), and making them individually faster or hiring more of them does not increase the company's actual delivery throughput at all.

This is the lesson's central, transferable idea: **before investing effort anywhere in a system, find the constraint, because effort spent anywhere else is largely wasted.** It reframes "we need more engineers" or "we need a faster CI pipeline" as unproven claims until you've identified where the actual bottleneck sits — improving a non-constraint stage is optimization theater.

## How it works

### The five focusing steps
Goldratt's ToC gives a repeatable procedure, which the book dramatizes through Bill's growing recognition of Brent's role:

1. **Identify the constraint.** Trace the value stream (`phoenix-project/02`) and find the stage where work queues up the most and stays longest — that's the bottleneck. At Parts Unlimited, this is empirically obvious once you look: nearly every escalation, incident, and Phoenix deployment task ends up waiting on Brent specifically, regardless of which team nominally owns the work.
2. **Exploit the constraint.** Make sure the bottleneck resource is never wasted on low-value work or idle time. Concretely: stop routing trivial, answerable-by-anyone questions to Brent; stop letting him get pulled into meetings unrelated to his unique expertise; make sure that when he *is* working, it's on the highest-value item available, not whatever fire is loudest.
3. **Subordinate everything else to the constraint.** Every other team's process should be shaped around not overloading or bypassing the bottleneck. If Brent is the constraint, other engineers should stop starting new work that will eventually need Brent's sign-off until the work already queued for him is cleared — starting more work in a non-constraint stage doesn't help; it just grows the queue in front of the constraint (this is the direct link to `phoenix-project/04`'s WIP limits).
4. **Elevate the constraint.** Only once steps 2 and 3 are exhausted do you invest in adding capacity at the bottleneck itself — for Parts Unlimited, this means deliberately documenting Brent's tribal knowledge, pairing him with other engineers to transfer expertise, and building tooling/runbooks that let more people safely do what only he could do before.
5. **Repeat — don't let inertia become the new constraint.** Once Brent is no longer the sole bottleneck, a new constraint will appear somewhere else in the system (perhaps the QA stage, or the change-approval process) — ToC is a continuous loop, not a one-time fix.

### Why "the constraint is a person" is uncomfortable but common
It's tempting to assume the bottleneck is always a technical stage (a slow CI pipeline, an under-provisioned staging environment). Often it's a person or a narrow group whose knowledge or authority the whole system routes through — exactly Brent's situation, and a pattern common in real organizations as a "bus factor of one" on a critical subsystem, or a single security reviewer who must approve every production change. The management response is the same regardless: protect that person's time from low-value interruptions, and invest specifically in *removing* their uniqueness (documentation, pairing, automation) rather than just asking them to work more hours, which only accelerates burnout without increasing system throughput.

**Worked example.** A 60-engineer platform team discovers that every database schema change — regardless of size — must be manually reviewed by their one remaining DBA, who also handles every production database incident. The team has been trying to speed up delivery by adding more backend engineers who write migrations faster. ToC analysis: the DBA is the constraint; adding backend engineers just grows the queue of migrations waiting for DBA review, exactly like adding capacity to Machine 1 when Machine 3 is the bottleneck. The actual fix: exploit (stop routing trivial, low-risk migrations through full manual DBA review — automate a policy check for the common safe cases), subordinate (pause starting new schema-change work once the DBA's review queue exceeds a threshold), and elevate (train two more engineers to review migrations, cutting the DBA's exclusivity).

### Local efficiency vs. global throughput
A recurring trap ToC exposes: teams and individuals optimizing their *own* local efficiency metrics can actively harm total system throughput. If the QA team is measured on "tests executed per day" and Brent's fixes arrive in QA in unpredictable, uneven bursts (because he's the constraint upstream), QA might batch-process to look efficient on their own metric — but that batching adds delay exactly where the constraint's output needs to move fastest through the rest of the pipeline. ToC's answer: individual stage metrics that aren't explicitly subordinated to the constraint's needs will, left alone, tend to work against total throughput. This is why `phoenix-project/02`'s shift from per-project percent-complete to end-to-end flow metrics matters — local metrics hide exactly this kind of damage.

## Pros
- Gives a concrete, repeatable procedure (five focusing steps) for deciding where improvement effort actually pays off, instead of spreading effort evenly across a system where most of it is wasted.
- Reframes "hire more people" or "buy more tooling" as unproven until you know where the constraint sits — often cheaper fixes (exploit, subordinate) exist before any elevation investment is needed.
- Explains, with a clear causal mechanism, why chronically overloaded key individuals (a "hero" engineer or a sole approver) both feel indispensable and are actively capping the organization's throughput.

## Cons
- Constraints move. A fix that elevates today's bottleneck can simply relocate the problem to a different stage, and organizations that declare victory after step 4 without repeating step 1 will be surprised by the next bottleneck.
- Identifying the *true* constraint requires real value-stream visibility (`phoenix-project/02`); without it, teams often "fix" a visible but non-constraining stage and see no improvement, then wrongly conclude ToC doesn't work.
- Concentrating attention on protecting one person's time (the constraint) can create real interpersonal friction — other stakeholders whose requests get deprioritized to protect the bottleneck resource may perceive this as unfair, requiring real communication and executive backing to sustain.

## Alternatives
- **Uniform efficiency improvement** — try to speed up every stage of the pipeline roughly equally (more engineers everywhere, faster tooling everywhere); intuitive and politically easier to sell than "we're deliberately not investing here," but ToC's core claim is that this wastes most of the investment on non-constraint stages.
- **Pure hiring/headcount growth** — add people broadly to increase capacity; only helps if the new hires reduce load on the actual constraint (or become capable of doing the constraint's work), otherwise it just grows queues in front of the bottleneck faster, per the DBA example above.
- **Agile/Scrum velocity tracking** — measure and try to improve team velocity per sprint; a useful local metric, but like other per-team metrics, it can be blind to a constraint that sits between teams (like Brent, who isn't "on" any one team's sprint) unless explicitly combined with end-to-end flow measurement.

## When to use it
Apply ToC whenever a system's total delivery throughput has stalled despite individual teams or people working hard and looking busy — the giveaway is "everyone is at capacity, but throughput isn't increasing." It's the natural next step after value-stream mapping (`phoenix-project/02`) identifies where work is queueing, and it directly motivates WIP limits (`phoenix-project/04`) as the mechanism for the "subordinate" step.

## When NOT to use it
Don't reach for ToC when a system's throughput problem is genuinely distributed evenly (no single stage dominates the queue) — in that case, broader efficiency work may be appropriate, though this is rarer than it appears; verify with real flow data before assuming it. Also avoid using "protect the constraint" as a permanent excuse not to invest in reducing key-person dependency (step 4, elevate) — treating a person as a permanent bottleneck to be "managed around" rather than a risk to be reduced is a failure to complete the ToC cycle, not a correct application of it.

## Key takeaways / mental model
Find the one stage where work queues up and stays longest — that's the only place where local improvement changes total system output. Protect it from waste, stop other stages from overloading it, then invest in expanding its capacity, and expect a new constraint to appear once you succeed. Effort spent anywhere else is, at best, neutral and, at worst, actively harmful if it grows the queue in front of the real bottleneck.

## Self-check questions
1. A platform team speeds up their CI pipeline by 3x, but end-to-end lead time for shipping a feature doesn't improve at all. Using ToC, what's the most likely explanation, and what would you check next?
2. Explain, in your own words, why "subordinate everything else to the constraint" sometimes means deliberately telling non-bottleneck teams to slow down or stop starting new work.
3. Brent gets promoted and the company hires two senior engineers to replace his unique expertise, fully documented and cross-trained. A year later, throughput has improved but a new bottleneck has emerged in the security review stage. Is this a failure of ToC, or exactly what ToC predicts? Justify your answer.
4. Describe a "local efficiency vs. global throughput" trap from your own experience (or a plausible one) where a team optimizing its own metric plausibly hurt total system throughput.

## References
- The Phoenix Project (Kim, Behr, Spafford), Part 1-2 (Erik's plant-floor lessons and Brent-as-constraint arc).
- Eliyahu Goldratt, The Goal (the source of the Theory of Constraints, referenced directly in the novel).
- See also `phoenix-project/02` (work as flow) and `phoenix-project/04` (WIP limits), which respectively identify and operationalize the constraint.
