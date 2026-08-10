---
id: seeking-sre/02
subject: seeking-sre
title: Defining Reliability Ownership Between Product and Platform Teams
slug: reliability-ownership-models
status: drafted
mastery:
seniority: staff
source: Seeking SRE (David Blank-Edelman, ed.), essay on the boundary between platform and product reliability responsibilities
prerequisites: [seeking-sre/01]
created: 2026-08-10
updated: 2026-08-10
---

# Defining Reliability Ownership Between Product and Platform Teams

## TL;DR
"Reliability is everyone's job" is true but useless without a concrete, written boundary specifying which failures a product team owns, which a platform team owns, and who owns the failures that fall in between (the majority of real incidents) — that boundary needs to be negotiated explicitly and revisited, not left to whoever happens to answer the page first.

## The idea
Once an organization has chosen an adoption model (`seeking-sre/01`), a second and harder question follows: for any given incident, whose job is it to fix it? In a small company this resolves itself informally — there's one team, one Slack channel, everyone just jumps in. That informality stops scaling somewhere between 50 and 150 engineers, when a platform team (owning shared infrastructure: Kubernetes clusters, the CI/CD pipeline, the message broker) and multiple product teams (owning services built on that infrastructure) start pointing at each other during incidents. "It's a platform problem" versus "it's how you're using the platform" is an argument that, unresolved, gets litigated live during every outage, adding minutes or hours to time-to-resolution precisely when speed matters most.

The book's framing: ownership needs to be defined along the *failure's origin*, not along organizational convenience, and the definition needs to live somewhere durable (a written RACI-style doc or service catalog entry) that both sides agree to before the next incident, not during it.

## How it works

### Three ownership zones
**Zone 1 - clearly product-owned.** Bugs in application logic, bad deploys, misconfigured feature flags, capacity the product team under-provisioned for a known traffic pattern. The product team owns detection (their own SLOs, `sre/03`), response, and the postmortem.

**Zone 2 - clearly platform-owned.** A shared database cluster running out of connections because of a platform-level configuration cap, a CI/CD pipeline outage blocking all deploys, a shared load balancer misconfiguration. The platform team owns detection, response, and the postmortem, and typically owes affected product teams a status update.

**Zone 3 - the contested middle.** This is where most real incidents actually live: a product team's traffic pattern change (a new feature causing a 5x spike in a particular query type) that exposes a previously-fine platform limitation (a connection pool sized for the old traffic pattern). Is this a platform capacity failure, or a product team failing to communicate a launch? Both framings are defensible, which is exactly why it needs to be decided *before* the incident, via a written interface contract, not argued live.

### Worked example: the interface contract
A concrete artifact that resolves Zone 3 disputes in advance: a one-page "platform interface contract" per shared service, answering:
- What SLO does the platform commit to for this shared resource (e.g., "the message broker commits to p99 publish latency under 50ms at up to 10,000 msgs/sec")?
- What is the product team's responsibility before using it at scale (e.g., "traffic increases of more than 2x within 30 days must be flagged to platform via the capacity-request form")?
- If a Zone 3 incident happens despite both sides honoring the contract (the platform met its committed SLO, the product team gave the required notice, and it still broke), ownership defaults to platform, because the contract's job is precisely to make that the rare, well-defined case rather than the norm.
This turns "who owns this" from a live argument into a contract lookup: did the product team give 30 days' notice for a 2x traffic increase? If yes and it still broke, it's platform's postmortem to write; if no, it's product's.

### Worked example: a real Zone 3 incident, resolved two ways
A checkout service (product team) starts issuing 3x more database writes after a new "save for later" feature ships, and the shared Postgres cluster (platform team) starts throttling connections org-wide, causing a partial outage for four unrelated teams sharing that cluster.
- *Without a contract*: the incident channel fills with platform saying "why didn't you tell us," product saying "we didn't think it'd be a big deal," and the postmortem stalls on assigning blame instead of fixing anything, delaying the actual fix (connection pooling changes) by days.
- *With a contract*: the capacity-request log shows no notice was filed for the new feature. Ownership is unambiguous — the product team's postmortem, with a documented action item to add a pre-launch capacity-check to their release checklist; platform's only action item is to make the "no proactive notice" case fail faster (a circuit breaker) rather than degrade for everyone.

### Renegotiating boundaries as teams mature
Ownership zones are not static. A product team that consistently causes Zone 3 incidents through undisciplined capacity planning is a signal to either invest in that team's operational maturity (see `seeking-sre/03`) or shrink Zone 3 by giving platform more automated guardrails (rate limits, quota systems) so fewer decisions require human judgment at all. Conversely, a platform team that's become a bottleneck for every Zone 3 dispute is a signal to push more ownership (and better self-service tooling) toward product teams.

## Pros
- Converts a recurring, morale-damaging live argument ("whose fault is this") into a contract lookup, cutting time-to-resolution on ambiguous incidents.
- Makes postmortems more productive because the "who investigates and who fixes" question is settled before the retro starts.
- Surfaces a concrete, actionable signal (repeated Zone 3 incidents from one team) for where to invest next — either team maturity or platform guardrails.

## Cons
- Writing and maintaining interface contracts for every shared service is real, ongoing work that's easy to let go stale as platform capabilities change.
- A contract can be used defensively ("not my problem, check the doc") in ways that undermine the collaborative spirit the practice is meant to protect, if leadership treats the contract as blame-assignment rather than a coordination tool.
- Contracts add friction to genuinely simple, no-time-to-negotiate startup-stage collaboration; introducing them too early can feel bureaucratic before the org actually has recurring Zone 3 disputes to justify them.

## Alternatives
- **Fully embedded platform expertise (no separate platform team)** — if every product team has enough infrastructure expertise in-house, the platform/product boundary dissolves rather than needing negotiation; works only at very small scale or with unusually infra-savvy product engineers.
- **Central incident command with post-hoc ownership assignment** — instead of pre-negotiated contracts, a neutral incident commander (see `sre/09` mechanics, adapted at staff level here) assigns ownership after the fact based on root cause; lower upfront investment but repeats the live-argument risk this lesson is trying to avoid, unless the incident commander has real authority to make the call stick.
- **Self-service platform with hard technical guardrails instead of social contracts** — replace the written contract with enforced quotas, rate limits, and automated capacity alerts so Zone 3 shrinks structurally; more engineering investment upfront but removes the need for social negotiation almost entirely once built.

## When to use it
Write explicit ownership contracts once you have more than a couple of product teams sharing platform infrastructure, or as soon as you observe a live "whose incident is this" argument happening more than once. Revisit contracts whenever platform capabilities change materially or a product team's traffic pattern shifts.

## When NOT to use it
Skip formal contracts at very small scale where one team effectively owns everything, or where the platform surface is thin enough (a single shared database with one consumer) that ambiguity can't really arise. Don't let contract-writing become a substitute for actually fixing recurring Zone 3 root causes — a contract that correctly assigns blame every month for the same recurring failure is a sign you need a guardrail, not another negotiation.

## Key takeaways / mental model
Picture three zones on a line between "clearly product" and "clearly platform," with a contested middle. The fix isn't eliminating the middle zone (you can't) — it's writing down, in advance, what each side owes the other (committed SLOs, required notice) so that most Zone 3 incidents resolve by contract lookup instead of live argument, and the residual disputes become clear signals for where to invest next.

## Self-check questions
1. A checkout service's traffic pattern change exposes a shared database's connection limit, causing a partial outage for unrelated teams. Using the interface-contract framework, walk through how you'd determine whether this is Zone 2 (platform) or Zone 1/3 (product), and what evidence you'd check.
2. Why does the lesson argue that ownership zones need to be defined "along the failure's origin, not organizational convenience"? Give an example of a convenience-based assignment that would go wrong.
3. A platform team is described as a chronic bottleneck for every ambiguous incident. What does the lesson suggest as the structural fix, short of eliminating the platform team's role entirely?
4. Explain the difference between a "no contract" and a "with contract" resolution of the same Zone 3 incident, and why the presence of a contract changes what the postmortem can focus on.

## References
- Seeking SRE (David Blank-Edelman, ed.), essay on the boundary between platform and product reliability responsibilities.
- See also `sre/03` (SLOs) and `sre/04` (error budgets) for the mechanics that platform-side commitments in an interface contract are typically built from.
