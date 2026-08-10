---
id: sre/04
subject: sre
title: Error Budgets as a Release-Governance Mechanism
slug: error-budgets
status: drafted
mastery:
seniority: senior
source: Site Reliability Engineering (Beyer, Jones, Petoff, Murphy), Chapter 3
prerequisites: [sre/03]
created: 2026-08-10
updated: 2026-08-10
---

# Error Budgets as a Release-Governance Mechanism

## TL;DR
An error budget is the inverse of an SLO — `100% - SLO` — turned into a spendable quantity of allowed unreliability over a time window. It converts the abstract dev-velocity-vs-stability tension into one concrete, shared number that both product and SRE teams manage against: when the budget is unspent, ship fast; when it's exhausted, slow down and stabilize. This is SRE's central governance mechanism, and it only works if both sides genuinely honor it.

## The idea
`sre/03` established that an SLO is deliberately less than 100% — you're allowed some unreliability. An error budget makes that allowance concrete and manageable: instead of thinking "we're allowed to fail sometimes," you think "we have exactly this much failure available to spend this month, on whatever we choose."

**The core formula:**
```
Error budget = 100% - SLO (as a fraction of the time window)
```

**Worked example.** A service has an SLO of 99.9% availability over a rolling 28-day window (28 days = 40,320 minutes).
```
Allowed downtime = (1 - 0.999) x 40,320 minutes = 40.32 minutes per 28 days
```
That's the team's error budget: roughly 40 minutes of "badness" (failed requests, converted to equivalent downtime) they're allowed to spend over the month, on anything — a risky deploy, a chaotic experiment, an unplanned outage, or a planned maintenance window. The number reframes reliability from an open-ended obligation ("never fail") into a finite resource ("you have 40 minutes — spend it wisely").

Why this matters organizationally: before error budgets, "should we ship this risky release?" was usually answered by whoever had more political capital that week — product wanting velocity, ops wanting a freeze. An error budget makes the answer computable: **if there's budget left, ship; if the budget's exhausted, stop non-essential releases until the SLO is back in compliance.** Both product and SRE agree to this rule *in advance*, before any specific release is being argued about, which is what makes it a governance mechanism rather than just a metric.

## How it works

### Computing spend from real incidents
**Worked example — a full month.** The checkout service above has a 99.9% SLO, giving a 40.32-minute budget for the 28-day window. During the window:
- A botched deploy causes a 12-minute full outage (12 minutes spent).
- A degraded-mode incident causes 30% of requests to fail for 45 minutes: that's `0.30 x 45 = 13.5 minutes` of "equivalent full downtime" spent (partial failures are pro-rated by the fraction of traffic affected, not counted as full outages).
- Total spend: `12 + 13.5 = 25.5 minutes` out of a 40.32-minute budget — **63% of the budget consumed**, 14.82 minutes remaining for the rest of the window.

This pro-rating is important and frequently misunderstood: a 10-minute outage affecting 100% of traffic and a 100-minute incident affecting 10% of traffic spend the *same* amount of budget (10 minutes-equivalent). The budget tracks user-experienced badness, not incident duration alone.

### The policy that makes the budget matter: what happens at zero
The mechanism only has teeth if there's a pre-agreed consequence for exhausting the budget. The book's canonical policy: **when the error budget is exhausted, feature launches and risky releases pause** (freeze non-essential deploys), and engineering effort redirects to reliability work — fixing the root causes that burned the budget — until the SLO is back in compliance for the window. This is agreed upfront, in writing, between product and SRE leadership, specifically so that when the moment arrives, it isn't a fresh negotiation under pressure ("just this once, let it through") — it's already-agreed policy being executed.

**Worked example of the policy in action.** Suppose the checkout service burns through its full 40.32-minute budget by day 10 of the 28-day window (a bad deploy plus a database failover gone wrong). Under the policy: the team stops shipping new checkout features for the remainder of the window (or until the trailing 28-day SLI recovers above 99.9% as old bad days roll out of the window), and the next two sprints' capacity shifts to hardening the deploy pipeline and the failover path — the specific things that burned the budget. Product leadership doesn't get to override this by fiat, because they agreed to the policy before the incident happened.

### Rolling windows and budget "regeneration"
Because the SLI is computed over a *rolling* window (e.g., 28 days), old bad days eventually roll off, and the budget replenishes without any manual reset. **Worked example.** If day 1 of the window had a 20-minute outage, that 20 minutes is part of the 28-day sum. Once day 1 rolls out of the rolling window (i.e., you're now looking at days 2-29), that 20 minutes drops out of the calculation automatically, freeing up budget — assuming no new incidents replace it. This is a deliberate design choice: it means a bad week doesn't permanently damn a service to a frozen state; it recovers on its own as time passes, provided no new spend occurs, giving teams a natural incentive to *stop* burning budget rather than an indefinite penalty.

### Spending the budget deliberately, not just by accident
A subtle but important point: an error budget isn't just a hedge against accidental outages — it's meant to be *spent on purpose* too. Deliberately risky but valuable activities compete for the same budget: a canary rollout of a major rewrite, a chaos-engineering exercise that deliberately injects failures to validate resilience, or an infrastructure migration. **Worked example.** A team planning a risky database migration might deliberately budget 15 of their 40.32 minutes for the migration window, leaving 25 minutes of margin for unplanned incidents during the rest of the month — an explicit, negotiated trade-off rather than an ad hoc risk taken and hoped for the best.

### Error budgets as the neutral arbiter between dev and SRE
This is the mechanism's real organizational payoff. Without it, "is this release too risky to ship" is a subjective argument between people with opposed incentives. With it, both sides can look at the same dashboard and agree on the answer, because the rule was fixed before anyone had a stake in a specific release. The book explicitly frames the error budget as removing the need for SRE to act as an unpopular gatekeeper saying "no" case by case — the *policy* says no, not a person, which is both fairer and much less politically costly to sustain over time.

## Pros
- Converts a political, incentive-misaligned negotiation ("can we ship this?") into an objective, pre-agreed computation both sides trust.
- Naturally self-heals via the rolling window — a bad month doesn't permanently freeze the team, it recovers as old incidents age out.
- Makes reliability investment prioritization concrete: when budget is tight, the next sprint's priority (harden, don't add features) is obvious rather than debated.

## Cons
- Only works if leadership actually honors the "freeze releases at zero budget" policy under real business pressure — a budget that gets overridden "just this once" for an important launch stops functioning as governance and becomes theater.
- Pro-rating partial outages (fraction of traffic affected x duration) requires accurate traffic-segmentation data; a service without good per-request success/failure telemetry can't compute spend precisely.
- Can create a perverse incentive to game the SLI's definition (e.g., narrowing what counts as a "valid" request) to avoid burning budget, rather than actually improving reliability — the SLI must be defended from this kind of gaming (see `sre/02`).

## Alternatives
- **Uptime-percentage dashboards with no spend/consequence tied to them** — informative but toothless; nothing changes when the number is bad, so it doesn't function as governance, only as reporting.
- **Change-freeze windows set by calendar (e.g., no releases during the holiday season)** — a coarser, static risk-management tool; doesn't respond to actual reliability performance the way an error budget does, and can freeze releases even when the service has been perfectly healthy.
- **Ad hoc release approval by a change advisory board** — a human-gatekeeper model; more flexible case by case, but reintroduces the political/subjective dynamic error budgets are specifically designed to remove, and doesn't scale well with release frequency.

## When to use it
Adopt error budgets once you have a trustworthy SLI and a negotiated SLO (`sre/02`, `sre/03`) and — critically — once leadership is willing to commit, in writing and in advance, to honoring the freeze policy when the budget hits zero. The mechanism's value is almost entirely in that advance commitment; without it, you have a metric, not a governance tool.

## When NOT to use it
Don't introduce an error budget as pure theater if there's no organizational appetite to actually pause releases when it's exhausted — a budget nobody enforces trains teams to ignore it, which is worse than not having one (it looks like governance while providing none). Also skip it for services too new or too low-stakes to have a meaningful SLO yet; there's nothing to budget against.

## Key takeaways / mental model
Error budget = "how much unreliability are we allowed to spend, and who gets to decide how to spend it." The formula (`100% - SLO`, applied to the window) is the easy part; the hard part — and the actual value — is the advance, honored agreement about what happens when it hits zero. Treat the budget like a real, finite currency: track spend precisely (pro-rated by impact), let it regenerate via the rolling window, and never let it be overridden case by case without changing the underlying policy for everyone.

## Self-check questions
1. A 99.95% SLO service has a 30-day rolling window. Compute the error budget in minutes, then compute how much budget is spent by an incident affecting 25% of traffic for 2 hours.
2. Explain why "we blew the budget, but this release is really important, let's ship anyway" undermines the entire error-budget mechanism, even if the release itself turns out fine.
3. Describe a scenario where a team should deliberately pre-allocate part of its error budget to a planned activity (not an accidental incident), and explain why that's a legitimate use of the budget rather than a workaround.
4. Why does a rolling window (vs. a fixed calendar month that resets to full budget on the 1st) change the incentives for a team that just had a very bad week?

## References
- Site Reliability Engineering: How Google Runs Production Systems (Beyer, Jones, Petoff, Murphy), Chapter 3 ("Embracing Risk").
- See also: `sre/03` (SLOs, the source of the budget), `sre/12` (release engineering, which consumes budget status to gate rollouts), and `devops-reliability/seeking-sre` (forthcoming) for how error-budget policy evolves across an organization over time.
