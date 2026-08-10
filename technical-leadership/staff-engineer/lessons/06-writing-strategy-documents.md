---
id: staff-engineer/06
subject: staff-engineer
title: Writing strategy documents that align technical and business direction
slug: writing-strategy-documents
status: drafted
mastery:
seniority: staff
source: Staff Engineer: Leadership Beyond the Management Track (Will Larson), Chapter 4 ("Writing an engineering strategy")
prerequisites: [staff-engineer/03]
created: 2026-08-10
updated: 2026-08-10
---

# Writing strategy documents that align technical and business direction

## TL;DR
Larson defines strategy as the combination of a diagnosis (an honest account of the current situation, including its uncomfortable parts), a set of guiding policies (the actual hard choices and trade-offs made in response), and coherent actions that follow from those policies — most "strategy documents" fail because they skip the diagnosis and jump straight to a wish list of nice-sounding goals with no real trade-offs attached.

## The idea
Ask most engineers to write a "strategy doc" and you'll get a document full of aspirational statements: "we will improve reliability," "we will move faster," "we will reduce technical debt." These aren't strategies — they're wishes. A real strategy has to say what you're *not* going to do, and why, because resources (engineering time, attention, political capital) are always finite, and a document that doesn't force a trade-off hasn't actually decided anything. The test of a real strategy document: could a reasonable, well-informed person disagree with it? If not, it's not a strategy — it's a values statement everyone already agreed with before you wrote it down.

Strategy sits at the intersection of technical and business direction because the hard trade-offs staff-plus engineers are asked to navigate are rarely purely technical — "should we invest six months in a platform rewrite or ship features" is a business question wearing technical clothes, and answering it requires understanding both the technical reality and what the business actually needs over what time horizon.

## How it works

### The three parts: diagnosis, policy, actions
This is Larson's adaptation of Richard Rumelt's strategy kernel, applied to engineering:
1. **Diagnosis** — an honest, specific account of the current situation, written so a reader unfamiliar with the details understands the real state, including the parts that are uncomfortable to admit (a team is understaffed, a system is riskier than leadership believes, a past decision was a mistake). A diagnosis that only says nice things about the status quo isn't a diagnosis — it's a summary written to avoid conflict, and it will produce a strategy with no teeth.
2. **Guiding policy** — the overall approach chosen in response to the diagnosis, stated specifically enough that it rules out real alternatives. "We will prioritize reliability" rules nothing out (everyone already agrees reliability matters). "We will not ship new customer-facing features on the payments service for two quarters while we address its three highest-severity reliability gaps" rules out a specific, real, currently-desired alternative — that's a policy.
3. **Coherent actions** — the concrete, coordinated set of steps that follow from the policy, specific enough to actually execute and check progress against, not just gesture at.

### Worked example — from wish list to real strategy
**Weak version (wish list, not strategy):** "Our engineering strategy is to build a scalable, reliable, high-quality platform that enables the business to move fast. We will invest in testing, monitoring, and developer tooling."

Nobody disagrees with this. It doesn't say what gets deprioritized to fund the investment, doesn't name which system is actually the problem, and can't be used to make a single real decision six months from now.

**Strong version, same underlying situation:**
- *Diagnosis:* "Our checkout service has caused four Sev-1 incidents in the last two quarters, all traced to the same undocumented, untested legacy pricing-rules module that three different teams now depend on without understanding its behavior. Feature velocity on checkout has actually been dropping for two quarters because every change requires manual, fearful verification against this module. Leadership currently believes checkout is stable because incident count per month looks flat — it's flat because engineers have started avoiding changes to the risky area, not because the risk has gone down."
- *Guiding policy:* "For the next two quarters, checkout team capacity is allocated 60% to rewriting and testing the pricing-rules module and 40% to must-ship commitments already made; no new discretionary checkout features will be started in this window, even ones requested by high-priority stakeholders."
- *Coherent actions:* Specific milestones (module behavior fully characterized by tests within week 4; rewrite complete and shadow-deployed by week 10; old module decommissioned by week 14), a named owner, and a mechanism (a standing biweekly review with the two dependent teams) to catch scope creep back into "just one small feature" that would quietly undermine the policy.

Notice the strong version names an uncomfortable truth (leadership's flat-incident-count read is wrong), states a real trade-off that will disappoint some stakeholders (no new features for two quarters), and gives concrete, checkable actions. That's what makes it strategy rather than aspiration.

### Writing for the actual audience
A strategy document has two different audiences with different needs: engineers who will execute it need enough technical specificity to act, and business/executive stakeholders need to understand the trade-off and its business rationale without wading through implementation detail. Larson's practical answer is a short executive-readable diagnosis and policy up front, with technical action detail available but not forced on every reader — burying the real trade-off under implementation detail is a common way strategy documents fail to actually align business and technical direction, because the business reader never gets to the part that affects them.

### Circulating for real feedback, not rubber-stamping
A strategy that never leaves your own head isn't a strategy that can align anyone — it needs to be reviewed by the people whose work it will constrain, before being finalized. Circulating a draft to the affected teams' leads and honestly incorporating pushback (as opposed to circulating a fait accompli and expecting sign-off) is what makes the eventual policy something people follow because they believe it, not just something they were told.

## Pros
- Forces genuinely hard trade-off decisions into the open, where they can be debated and defended, instead of leaving them implicit and re-litigated every sprint.
- Gives a durable, written reference that outlasts any single meeting or conversation — new team members and stakeholders joining later can read the diagnosis and understand why the current approach exists.
- Directly demonstrates staff-plus judgment (see `staff-engineer/01`) in a form promotion committees and executives can actually evaluate.

## Cons
- Writing a real diagnosis requires naming uncomfortable truths, which takes real political courage and can create friction with whoever owns the status quo being critiqued.
- A strategy document with a real policy will disappoint someone by design (it rules out an alternative they wanted) — this is a feature, not a bug, but it's genuinely uncomfortable to be the author of that disappointment.
- Poorly-timed strategy work (written for a problem nobody with authority currently cares about) can be technically excellent and organizationally ignored.

## Alternatives
- **OKRs / goal-setting frameworks alone** — useful for tracking measurable progress but, without an accompanying diagnosis and policy, tend to produce the same wish-list problem (goals nobody disagrees with) rather than forcing trade-offs.
- **Roadmaps without a stated policy** — a prioritized list of projects communicates *what* will happen but, without the diagnosis-and-policy reasoning behind it, doesn't explain *why*, which makes the roadmap brittle the moment circumstances change and nobody remembers the reasoning that produced it.
- **Verbal/informal alignment (no written document)** — faster for small, single-team decisions, but doesn't scale past the room it happened in and leaves no durable record for people who join later or weren't in the room — a real cost for anything crossing more than one or two teams.

## When to use it
Write a real strategy document when a decision needs to bind multiple teams' priorities over a meaningful time horizon (a quarter or more), when there's a genuine, currently-unresolved disagreement about direction, or when you (per `staff-engineer/03`) have identified a cross-team problem serious enough to need explicit, defensible trade-offs rather than ad hoc handling.

## When NOT to use it
Don't write a formal strategy document for decisions that are genuinely reversible, low-stakes, or scoped to a single team's day-to-day work — the overhead of a full diagnosis-policy-actions document isn't justified, and a quick design doc or even a Slack thread is the right-sized tool instead.

## Key takeaways / mental model
Before calling anything a "strategy," apply the disagreement test: could a smart, well-informed person reasonably push back on this? If every sentence is something everyone already agreed with, you've written a values statement, not a strategy — go back and find the diagnosis's uncomfortable truth and the policy's real trade-off.

## Self-check questions
1. Take a "strategy" document or plan you've seen (or written) recently. Apply the disagreement test: does it contain a real trade-off someone could reasonably object to, or is it a wish list? Rewrite one sentence of it into something that passes the test.
2. In the worked checkout example, what specifically makes the diagnosis uncomfortable, and why does Larson argue that discomfort is necessary rather than something to soften?
3. Explain why a guiding policy that "rules nothing out" isn't actually a policy. Give your own example of a weak, non-ruling-out policy statement and a strong, trade-off-forcing rewrite.
4. Why does a strategy document need a different level of detail for its executive audience versus its engineering audience? What goes wrong if you write only for one of the two?

## References
- Staff Engineer: Leadership Beyond the Management Track (Will Larson), Chapter 4: "Writing an engineering strategy" (drawing on Richard Rumelt's "Good Strategy/Bad Strategy" kernel of diagnosis, guiding policy, and coherent action).
