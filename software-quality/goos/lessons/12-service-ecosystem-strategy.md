---
id: goos/12
subject: goos
title: Test Strategy Across a Service Ecosystem
slug: service-ecosystem-strategy
status: drafted
mastery:
seniority: staff
source: Growing Object-Oriented Software, Guided by Tests (Freeman & Pryce), Part III/Chapter 10
prerequisites: [goos/06, goos/08, goos/11]
created: 2026-08-10
updated: 2026-08-10
---

# Test Strategy Across a Service Ecosystem

## TL;DR
GOOS's techniques were demonstrated on one system (the auction sniper) talking to one external dependency, but the same principles — fast feedback, thin end-to-end slices, ports and adapters at every boundary, disciplined interaction testing — scale to a whole ecosystem of collaborating services, where the hardest problem shifts from "test one system well" to "decide, deliberately, what each of many test suites is and isn't responsible for verifying," so that confidence is built cheaply and reliably across the whole system without any one team's suite having to (impossibly) simulate the entire ecosystem.

## The idea
Everything in this subject so far has one system as its unit of concern: the sniper, its internal objects, and one external boundary (the auction house). Real organizations rarely stop there — the sniper might itself be one service among many (a bidding service, a notification service, a user-account service, a billing service), each owned by a different team, each independently deployed, each with its own test suite. At this scale, a new, higher-order question appears that none of the earlier lessons directly answer: given that no single team can practically write end-to-end tests that exercise the *entire* multi-service ecosystem for every change (too slow, too fragile, too tightly coupling every team's release schedule to every other team's), what should each team's test suite actually cover — and what confidence, if any, substitutes for full end-to-end coverage across the whole ecosystem?

This is a genuinely staff-level concern: it's not about how to test one component well (which the rest of this subject covers thoroughly) but about how the *testing strategy itself* has to be designed and negotiated across team and system boundaries — a second-order decision about how confidence is distributed and composed across an organization, not just a technical decision about one codebase.

## How it works

### The test pyramid, extended across service boundaries
Within one service, GOOS's approach naturally produces a shape sometimes called the "test pyramid": many fast unit tests (`goos/01`, `goos/05`, `goos/07`) at the base, fewer, slower tests at the port/adapter boundary (`goos/06`, `goos/08`), and a small number of full acceptance tests (`goos/04`) at the top. Extending this idea across an ecosystem means recognizing that "the top of the pyramid" — genuinely full, end-to-end, cross-service tests — must stay *very* small in number, for the same reasons a single service's acceptance-test layer stays small: they're slow, fragile (now failing not just from your own bugs but from any other team's environment issues), and expensive to maintain across independently-evolving services. Most confidence at ecosystem scale has to come from somewhere other than exhaustive cross-service end-to-end testing.

### Consumer-driven contracts: verifying a boundary without a live partner
The key technique that fills the gap left by minimizing full end-to-end tests is a natural extension of `goos/06`'s ports-and-adapters idea: each service defines, and tests against, a **contract** describing exactly what it expects from (or promises to) a collaborating service — independent of whether that collaborating service is actually running. A **consumer-driven contract** is written by the consuming team (e.g., the bidding service, which needs specific fields from the notification service's API) and verified two ways: the consumer tests against a fake/stub that honors the contract (fast, no live dependency, exactly like `goos/06`'s adapter-boundary testing within one service), and the *provider* team runs the same contract as a test against their real implementation, catching any accidental breaking change before it ships — without either team needing the other's system running live during normal development.

**Worked example.** The bidding service depends on a notification service to send "you won" messages. Instead of the bidding team's test suite spinning up a real notification service for every test run (slow, and coupling the bidding team's CI to the notification team's deploy state), the bidding team maintains a contract: "notification service must accept `POST /notify {userId, auctionId, outcome}` and respond 202." Bidding-team tests run against a stub that honors this contract. The notification team, separately, runs the same contract against their real service in their own CI pipeline — if they ever change the endpoint in a way that breaks the contract, their own build fails immediately, at the source of the change, rather than surfacing later as a mysterious integration failure discovered by the bidding team in a shared staging environment.

### Where a small number of genuine end-to-end tests still earn their place
Consumer-driven contracts verify that each pairwise boundary honors its agreed shape, but they can't catch every category of problem — particularly emergent behavior that only shows up when several real services interact under realistic conditions (timing issues, cascading failures, genuinely surprising interactions between three or more services that no single pairwise contract anticipated). A small number of true end-to-end tests, run less frequently than each service's own fast suite (e.g., nightly against a shared staging environment, rather than on every commit), still earns its place for exactly this residual risk — deliberately kept few, because their cost (speed, fragility, cross-team coordination to keep the shared environment stable) scales badly, unlike the fast, cheap, plentiful unit and contract tests underneath them.

### Deciding what's "your" boundary vs. "their" boundary
A recurring, genuinely hard judgment call at this scale: when a cross-service interaction breaks, whose test suite should have caught it? Freeman & Pryce's underlying philosophy (ports and adapters, `goos/06`) suggests the answer: each service's *own* port/adapter boundary is exactly where that service's responsibility for the interaction ends — a service is responsible for correctly implementing its side of a contract and for its own adapter correctly translating to/from that contract, but not for verifying another team's implementation beyond that agreed contract. This mirrors, at organizational scale, the same discipline `goos/10` teaches at the object scale: define the boundary of responsibility precisely, test rigorously up to that boundary, and trust (verified via contract, not blind faith) rather than re-verify beyond it.

## Pros
- Distributes testing effort sustainably across many independently-evolving teams, avoiding the organizational bottleneck of a single, slow, fragile suite of full-ecosystem end-to-end tests that everyone depends on and nobody can move fast against.
- Consumer-driven contracts catch breaking changes at their source (the provider's own CI), often before the change is even merged, rather than as a late-discovered integration failure affecting a different team.
- Extends this entire subject's core discipline (fast feedback, boundary isolation, evidence over speculation) up to organizational scale rather than requiring a fundamentally different philosophy once multiple teams and services are involved.

## Cons
- Consumer-driven contract testing requires real cross-team process discipline (agreeing on contract ownership, keeping contracts current, running provider-side verification consistently) that's genuinely harder to sustain than a single team's internal testing practice, because it depends on coordination the team doesn't fully control.
- Contracts can drift out of sync with reality if either side stops maintaining them carefully, silently reintroducing the exact integration risk they were meant to eliminate — the discipline has to be actively sustained, not set up once and forgotten.
- Even a well-designed contract-testing strategy can't fully replace the residual value of occasional real end-to-end tests for genuinely emergent, multi-service interaction problems — deciding how few is "enough" is a judgment call with real risk on both sides (too many is slow and fragile; too few misses real cross-service bugs).

## Alternatives
- **Shared, persistent full-integration environment as the primary safety net** — maintain one always-on environment with all real services running, and run substantial end-to-end suites against it regularly. Catches genuine cross-service issues directly, but at real cost: slow, expensive to keep stable, and creates organizational coupling (one team's broken deploy blocks everyone's tests) that this lesson's approach is specifically designed to avoid.
- **Trust and monitoring instead of pre-deployment contract verification** — skip consumer-driven contracts, deploy independently, and rely on production monitoring/alerting to catch integration breakages after the fact (sometimes paired with feature flags and canary releases to limit blast radius). Faster in the common case, and a legitimate complement to contract testing rather than a full substitute, but shifts some risk discovery from before deployment to after.
- **A single, monolithic service instead of many collaborating ones** — sidesteps the cross-service testing problem entirely by not having cross-service boundaries in the first place. A legitimate architectural alternative for organizations where the coordination cost of many services outweighs their benefits, though it trades away independent deployability and team autonomy.

## When to use it
Adopt a deliberate, contract-based cross-service test strategy once a system has genuinely split into multiple independently-deployed services owned by different teams — the point at which no single team can reasonably own comprehensive end-to-end confidence across the whole ecosystem by themselves.

## When NOT to use it
Don't introduce consumer-driven contracts or elaborate cross-service test strategy for a single monolithic service, or for a small number of services all owned and deployed by one team that can reasonably coordinate informally — the organizational overhead this lesson describes is specifically a response to independent ownership and independent deployment; it's not needed where those conditions don't hold.

## Key takeaways / mental model
At ecosystem scale, ask not "how do I test the whole system end-to-end" (increasingly impossible as services multiply) but "what does each service owe the services around it, and how is that promise verified cheaply, on every change, without requiring everyone's system to be running at once?" Consumer-driven contracts answer that question at each pairwise boundary; a small, deliberately limited number of real end-to-end tests catch what contracts structurally can't; and each service's own internal test suite (everything covered earlier in this subject) remains the foundation underneath both.

## Self-check questions
1. Explain why full end-to-end tests across an entire service ecosystem don't simply scale up the acceptance-testing approach from `goos/04` — what specifically breaks down as the number of independently-deployed services grows?
2. Using the bidding/notification example, describe what happens (and where the failure is caught) if the notification team changes their API's response code from 202 to 200, under a consumer-driven-contract strategy versus under a strategy relying only on a shared staging environment.
3. A staff engineer is asked "whose fault is it" when a cross-service interaction breaks in production despite both services' own test suites being green. Using this lesson's framing of contract-testing versus residual end-to-end risk, what two different explanations should they consider before assigning blame?
4. Describe a situation where introducing consumer-driven contract testing between two services would be premature organizational overhead, and explain what would need to change for it to become worthwhile.

## References
- Growing Object-Oriented Software, Guided by Tests (Freeman & Pryce), Part III (the book's closing discussion of sustaining growth and the principles' applicability beyond a single system).
- Related industry practice: Consumer-Driven Contracts (Ian Robinson) and tools such as Pact, which formalize the contract-testing technique this lesson describes as a natural extension of `goos/06`'s ports-and-adapters boundary discipline.
