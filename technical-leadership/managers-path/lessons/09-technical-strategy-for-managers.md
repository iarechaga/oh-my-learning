---
id: managers-path/09
subject: managers-path
title: Technical strategy for engineering managers and directors
slug: technical-strategy-for-managers
status: drafted
mastery:
seniority: staff
source: The Manager's Path (Camille Fournier), Chapter 8 - Executive Leadership and Chapter 9 - Culture
prerequisites: [managers-path/03]
created: 2026-08-10
updated: 2026-08-10
---

# Technical strategy for engineering managers and directors

## TL;DR
Managers don't stop being technical - they shift from personally solving technical problems to setting technical *direction*: deciding what the team should invest in, when to pay down debt versus ship features, and how to keep architectural decisions coherent across a team or org, using judgment and organizational leverage rather than hands-on coding.

## The idea
A common misconception is that becoming a manager means becoming "non-technical." Fournier pushes back hard on this: staying technically credible - understanding the systems well enough to ask good questions, sanity-check estimates, and make defensible calls on debt versus features - remains essential, but the *mode* of technical involvement changes. A manager's technical judgment now expresses itself through decisions about priorities, staffing, and architecture direction, not through personally writing the code that implements those decisions. This is a different and, for many, harder skill than deep hands-on technical work: it requires forming a confident opinion on a technical trade-off without necessarily being the person closest to the code, and defending that opinion to stakeholders who care about business outcomes, not implementation elegance.

The strategic core of this lesson is the recurring tension between feature velocity and technical health (debt, scalability, maintainability). Every team faces pressure to ship features now; technical debt's cost is real but deferred and invisible until it isn't. A manager who never pushes back accumulates debt that eventually stalls the team; a manager who only ever prioritizes technical health never ships anything the business needs. Navigating this trade-off deliberately, rather than by default in either direction, is a core piece of a manager's technical leadership.

## How it works

### Stay technical enough to ask the right questions, not to write the code
Fournier's practical advice is to maintain enough hands-on technical engagement - reading code in reviews, understanding system architecture diagrams, occasionally pairing - to keep real technical credibility with the team and to sanity-check what you're told, without trying to remain the team's top individual technical contributor (the trap named in `managers-path/03`). Concrete example: when an engineer estimates a project at three weeks, a technically engaged manager can ask "what makes this harder than the similar migration we did last quarter?" - a question that surfaces hidden assumptions - without needing to personally re-derive the estimate from scratch.

### Make debt-versus-features trade-offs explicit, not implicit
A manager's job includes actively deciding, and making visible to stakeholders, how much of the team's capacity goes to new features versus paying down technical debt or investing in scalability - rather than letting it default to 100% features because that's what's most visible to product stakeholders. A concrete technique: maintain a running, prioritized list of technical debt items with an honest cost/risk estimate for each (what does this slow down, what does it risk if unaddressed), and periodically negotiate a portion of capacity - not a fixed rule like "20% of every sprint," which Fournier notes often gets quietly eroded under deadline pressure, but a deliberate, revisited allocation the manager actively defends.

### Translate technical trade-offs into business language for stakeholders
Product and business stakeholders don't need to understand the technical detail of why a migration is risky; they need to understand the business consequence ("if we don't do this now, the next three features in this area will each take 1.5x longer, and we'll have a real outage risk during peak traffic"). A manager who can't make this translation either loses the negotiation for technical investment (stakeholders discount vague technical concerns) or wins it by fiat without stakeholder buy-in, which erodes trust for the next negotiation.

### Keep architectural coherence as the team and system grow
As more engineers touch a system, without deliberate coordination, architecture tends to drift - inconsistent patterns, duplicated logic, contradictory conventions accumulating from different people's independent decisions. A manager's technical strategy work includes making sure some mechanism exists to keep decisions coherent - a tech lead role (`managers-path/02`), a lightweight architecture review process, documented conventions - appropriate to the team's size, rather than either micromanaging every technical decision personally or letting the system drift with no coordination at all.

## Pros
- Preserves the manager's technical credibility and judgment, which is essential for making defensible calls on staffing, priorities, and architecture that the team will actually trust.
- Makes technical investment (debt paydown, scalability work) visible and negotiated rather than silently sacrificed to feature pressure by default.
- Scales technical leadership beyond what any one person could personally implement, by setting direction that a whole team executes coherently.

## Cons
- Requires continued technical investment of time (reading code, staying current) that competes directly with the people-management workload that also demands real time.
- Negotiating capacity for technical health is a recurring political effort, not a one-time win - it has to be re-defended in every planning cycle against feature pressure.
- Risk of drifting too far from hands-on reality if technical engagement lapses, leading to decisions that sound reasonable in the abstract but miss real implementation constraints.

## Alternatives
- **Dedicated architect role** - a technical (not people-management) role explicitly responsible for cross-team architectural coherence, freeing managers to focus more on people while the architect owns technical strategy; works well at larger scale, adds a coordination seam between the architect and the managers who staff the work.
- **Bottom-up technical governance (guilds/RFCs)** - technical direction emerges from a broader group of senior engineers via a documented proposal process, rather than being set top-down by managers; distributes technical judgment more widely but can be slower to reach decisions.
- **Pure feature-prioritization by product, with debt handled reactively** - let product own all prioritization and treat technical debt only when it becomes an acute blocker; simpler in the short term but tends to accumulate debt that eventually forces a costly, disruptive rewrite.

## When to use it
Continuously, at any point a manager has technical authority over what a team builds - especially at planning/prioritization time, when architecture decisions are being made, and when negotiating capacity between features and technical health.

## When NOT to use it
Don't personally re-derive or approve every technical decision the team makes - that's over-involvement that undermines the tech lead and senior engineers' own judgment (see `managers-path/02`) and doesn't scale as the team or org grows. And don't treat "staying technical" as license to keep doing hands-on implementation work at the expense of the people-management responsibilities that are now the primary job (see `managers-path/03`).

## Key takeaways / mental model
A manager's technical leverage comes from setting direction and defending technical investment in language stakeholders understand, not from personally writing the best code - stay technical enough to ask sharp questions and make defensible calls, and treat the features-versus-debt trade-off as a decision to make explicitly, not a default to fall into.

## Self-check questions
1. Why does Fournier argue that a manager giving up hands-on coding should not mean giving up technical judgment? What's the difference between the two?
2. Your team has accumulated real technical debt, but product is pushing hard for the next feature. Describe how you'd frame the trade-off to a non-technical stakeholder.
3. What's the risk of a manager who tries to stay the team's top individual technical contributor even after becoming a manager? Connect this back to `managers-path/03`.
4. Describe one mechanism (besides personally reviewing every decision) a manager could use to keep architectural coherence as a team scales from 5 to 15 engineers.

## References
- The Manager's Path (Camille Fournier), Chapter 8: "Executive Leadership" and Chapter 9: "Culture".
