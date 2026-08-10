---
id: devops-handbook/01
subject: devops-handbook
title: Applying the Three Ways as an Implementation Model
slug: three-ways-implementation-model
status: drafted
mastery:
seniority: senior
source: The DevOps Handbook (Kim, Humble, Debois, Willis), Part I
prerequisites: [phoenix-project/05, phoenix-project/06, phoenix-project/07]
created: 2026-08-10
updated: 2026-08-10
---

# Applying the Three Ways as an Implementation Model

## TL;DR
The Three Ways (Flow, Feedback, Continual Learning) are principles the Phoenix Project narrative dramatizes; the DevOps Handbook turns them into a concrete implementation program — a specific, ordered set of technical and organizational practices you install, measure, and iterate on, not just a philosophy you agree with.

## The idea
`phoenix-project/05`, `phoenix-project/06`, and `phoenix-project/07` gave you the Three Ways as a narrative lesson: Bill's team discovers, through crisis, that IT work behaves like a flow system, that feedback loops must run in both directions, and that a culture of experimentation compounds improvement over time. That's the "why." This lesson is the "how" — the DevOps Handbook's central claim is that each Way maps onto a specific, learnable set of technical practices, and that adopting them in the right order matters as much as adopting them at all.

The problem the Handbook solves: without an implementation model, "adopt DevOps" is a slogan, not a plan. Teams that try to jump straight to the exciting parts (continuous deployment, chatops, elaborate dashboards) without first fixing the underlying flow of work usually get brittle, hard-to-operate systems faster, not more reliable ones. The Three Ways, translated into a build order, prevent that: you cannot safely accelerate feedback (Second Way) on a system that doesn't have a repeatable, low-variance delivery pipeline (First Way) — you'll just get faster, noisier surprises. And you cannot sustain continual learning (Third Way) if failures don't reliably surface as actionable feedback in the first place.

## How it works

### First Way -> Flow: the technical practices
The First Way says work should move left-to-right (Dev -> Test -> Ops -> Customer) as fast as possible, visibly, without flowing backward. In the Handbook this becomes concrete practice: continuous build/integration/deployment (`devops-handbook/05`, `devops-handbook/06`), architecture that supports independent, low-risk deployment (`devops-handbook/09`), trunk-based development to avoid long-lived branches that hide integration debt (`devops-handbook/07`), and automated testing that fails fast rather than deferring quality checks to a manual QA phase at the end. The measurable target is deployment lead time — how long from a code commit to it running safely in production.

**Worked example.** A team's lead time is 6 weeks: a feature sits in a release branch for 3 weeks waiting for a monthly release train, then 2 weeks in manual QA, then 1 week of change-approval paperwork. Applying First Way practices doesn't mean "work faster" as a slogan — it means specific interventions: trunk-based development removes the branch-merge queue, automated test suites replace the 2-week manual QA phase with a pipeline that runs in under an hour, and pre-approved change categories (`devops-handbook/15`) remove the manual approval wait. Lead time might drop from 6 weeks to 2 days — not through heroics, but through removing the specific queues that were the actual bottleneck (echoing the Theory of Constraints logic from `phoenix-project/03`).

### Second Way -> Feedback: the technical practices
The Second Way says problems discovered downstream (in test, staging, or production) must flow back upstream fast enough that the people who can fix them learn about them while the context is still fresh. This becomes telemetry (`devops-handbook/10`), monitoring and alerting tuned for signal over noise (`devops-handbook/11`), and — critically — routing that feedback to the engineers who wrote the code, not just to an operations team who didn't (`devops-handbook/12`). Feedback that takes weeks to surface (a quarterly production-incident review) is nearly worthless for learning; feedback that surfaces in minutes (a deploy-triggered alert tied to the commit that caused it) closes the loop while the engineer still remembers what they changed and why.

**Worked example.** A team ships a change that increases checkout latency by 400ms. Under weak feedback, this surfaces three weeks later as "sales dipped last month," investigated by an unrelated analytics team with no link back to the change. Under strong Second Way practices, a p99 latency SLI dashboard alerts within 5 minutes of the deploy, tagged with the deploy ID, and pages the on-call engineer who wrote the change — the fix ships within the hour, and the engineer directly learns the causal link between their code and the regression.

### Third Way -> Continual Learning: the technical and cultural practices
The Third Way says the organization should convert every incident, near-miss, and successful experiment into knowledge that spreads beyond the individual or team that discovered it. Concretely: blameless postmortems (`devops-handbook/13`) that produce written, searchable artifacts rather than private lessons-learned; deliberate practice and game days that inject controlled failure to build organizational muscle memory; and platform/enabling teams (`devops-handbook/14`) that turn one team's hard-won fix into a shared capability everyone gets by default.

**Worked example.** One team discovers that a particular database connection-pool misconfiguration caused a cascading outage. Under weak Third Way practice, that team fixes their own instance and moves on — the same misconfiguration causes an outage in a different team's service six months later. Under strong Third Way practice, the postmortem produces a documented failure mode, the platform team adds a default connection-pool guardrail to the shared service template, and no team can trivially reintroduce that failure again.

### Why order matters: sequencing the Three Ways as an implementation program
The Handbook is explicit that these Ways build on each other, not that they're three independent checklists to pursue in parallel. Attempting Second Way telemetry and alerting on a system with First Way flow problems (slow, manual, high-variance deploys) produces noisy, low-trust alerts because you can't distinguish "real regression" from "this always breaks a bit during our messy monthly release." Attempting Third Way blameless learning culture without First/Second Way technical practices in place produces well-intentioned postmortems whose recommended fixes ("deploy more carefully") have no concrete mechanism to become real, because there's no pipeline or telemetry to encode the fix into.

## Pros
- Converts an inspiring but abstract philosophy into a concrete, ordered, measurable adoption plan.
- The build order (Flow -> Feedback -> Learning) prevents common failure modes of skipping straight to advanced practices on a shaky foundation.
- Gives every subsequent lesson in this subject a place in a larger structure, rather than being a disconnected list of "DevOps practices."

## Cons
- The neat three-phase framing can be read too literally as strictly sequential; in practice, real organizations run all three Ways concurrently at different maturity levels across different teams, and the model doesn't give sharp guidance for that messier reality.
- Doesn't by itself resolve organizational and incentive problems (a team punished for reporting incidents will not produce honest Second/Third Way feedback no matter how good the tooling is) — the technical practices are necessary but not sufficient.
- Risk of "Three Ways theater": adopting the vocabulary (dashboards labeled "feedback," retro docs labeled "blameless") without the substance underneath actually changing.

## Alternatives
- **Google's SRE model** (see `sre/*`) — arrives at similar practices (SLOs, error budgets, blameless postmortems) from a reliability-engineering angle rather than a flow/lean angle; heavier emphasis on quantified risk tolerance (error budgets) as the release-governance mechanism.
- **Straight Agile/Scrum adoption without the technical practices layer** — addresses planning cadence and team process but, without CI/CD, telemetry, and trunk-based development, tends to produce "fast planning, slow delivery" — sprints that plan well but still ship on a slow, brittle pipeline.
- **Big-bang platform rewrite** — attempts to buy the First Way's flow benefits through a new architecture in one large project rather than incremental practice adoption; higher risk, and skips the learning that incremental practice adoption produces along the way.

## When to use it
Use the Three Ways as your organizing map whenever you're planning a DevOps transformation roadmap, deciding what to invest in next, or diagnosing why a transformation stalled — check which Way is actually the bottleneck before investing further in a Way that's already working.

## When NOT to use it
Don't invoke it as a rhetorical banner without committing to the underlying technical practices — leadership declaring "we're a Three Ways organization" while deployment lead time and postmortem quality stay unchanged is exactly the theater this model is meant to prevent. Also don't force strict sequential adoption on teams already further along (a team with strong telemetry doesn't need to "wait" for some notional First Way completion milestone before improving feedback further).

## Key takeaways / mental model
Ask, for any team or org: which Way is the actual constraint right now — is work not flowing (First), do problems take too long to surface (Second), or does the org fail to learn from what does surface (Third)? Invest there first; investing in a later Way while an earlier one is broken mostly produces noise, not improvement.

## Self-check questions
1. A team has excellent monitoring dashboards but a 6-week manual release process. Using the Three Ways sequencing logic, explain why their telemetry investment is producing less value than it could.
2. Give a concrete example (not from this lesson) of "Three Ways theater" — practices that use the vocabulary without the substance — for each of the three Ways.
3. Why does the Handbook argue you cannot sustain Third Way learning culture without First and Second Way technical practices already in place? What specifically breaks?
4. How does this lesson's technical-practices framing differ from `phoenix-project/05`-`07`'s narrative framing of the same Three Ways? What does each version teach that the other doesn't?

## References
- The DevOps Handbook (Kim, Humble, Debois, Willis), Part I: "The Three Ways."
- See also: `phoenix-project/05`, `phoenix-project/06`, `phoenix-project/07` for the narrative introduction to the same ideas.
