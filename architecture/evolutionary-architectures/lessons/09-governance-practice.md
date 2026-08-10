---
id: evolutionary-architectures/09
subject: evolutionary-architectures
title: "Governing and Building an Evolutionary Practice"
slug: governance-practice
status: drafted
mastery: 
seniority: staff
source: "Building Evolutionary Architectures, 2nd ed. (Ford, Parsons, Kua, Sadalage), Chapter 9"
prerequisites: [evolutionary-architectures/02, evolutionary-architectures/07, evolutionary-architectures/08]
created: 2026-08-10
updated: 2026-08-10
---

# Governing and Building an Evolutionary Practice

## TL;DR
Governance in an evolutionary architecture is **fitness-function-driven, not
document-driven**: an architectural decision becomes real and durable when it's encoded
as an automated, enforceable check, not when it's written down in a wiki page or an ADR
that nobody re-reads. Building a sustainable practice around this means establishing
clear ownership of fitness functions, a cadence for evolving them as the system and
business change, and a deliberate balance between governance rigor and team autonomy —
calibrated per quantum, not applied uniformly (the fix for the inappropriate-governance
antipattern from `evolutionary-architectures/08`).

## The idea

### Why document-driven governance fails at scale
Traditional architectural governance works like this: an architecture review board (or
a senior architect) makes a decision, writes it down (a standards document, an ADR, a
wiki page), and expects every team to read it, remember it, and comply with it
indefinitely. This has two structural weaknesses that get worse as an organization
grows:

1. **Enforcement depends entirely on human memory and diligence.** A document doesn't
   fail a build. Compliance decays the moment the person who wrote the standard moves
   teams, the moment a new hire never reads the wiki, the moment deadline pressure makes
   "I'll fix it to match the standard later" feel reasonable (it rarely happens).
2. **It doesn't scale with organizational size or quantum count.** A review board can
   plausibly track compliance across five teams by attending their design reviews. It
   cannot plausibly do so across two hundred teams and a thousand quanta — the review
   board becomes either a bottleneck (every change waits for board approval) or a
   rubber stamp (approval happens without real verification, because there's no time to
   verify two hundred teams' worth of changes manually).

### The alternative: governance as an enforced, automated contract
Fitness-function-driven governance flips the mechanism: a governance decision isn't
"real" in an actionable sense until it's expressed as a fitness function that runs
automatically and has a consequence when violated (per the anatomy in
`evolutionary-architectures/02`). The ADR or document still matters — it captures the
*why*, which a machine-checkable rule alone can't convey to a future engineer trying to
understand intent — but the *enforcement* lives in the pipeline, not in anyone's memory.

This reframes what an architecture/governance team's job actually is: not "write
standards and hope," but "identify what needs protecting, encode it as a fitness
function, and make sure that fitness function keeps running and keeps being true" — a
fundamentally more scalable job, because the governance team's leverage compounds
(one well-placed fitness function protects every future change automatically) instead
of requiring linear effort (reviewing every change by hand, forever).

## How it works

### Building the practice: who owns fitness functions, and how they evolve

**Ownership**: the book's guidance, and common practice among organizations that do this
well, is to place fitness-function ownership close to the quantum it protects, not
centralized in a single architecture team, *except* for genuinely cross-cutting
concerns:
- **Quantum-local fitness functions** (a specific service's internal dependency rules,
  its own performance budget) are owned by the team that owns that quantum — they
  understand the context best and bear the consequences of both under- and
  over-protecting it.
- **Cross-cutting fitness functions** (security scanning, a company-wide data-residency
  rule, a compliance requirement that applies to every quantum) are owned centrally, by
  a platform or architecture team, because they represent a genuinely uniform constraint
  that isn't a matter of per-team judgment — this is the legitimate case for uniform
  governance, distinguished from the inappropriate-governance antipattern precisely by
  being deliberately, explicitly scoped to things that really are universal, rather than
  applied broadly by default.

The distinction matters enormously in practice: getting it backwards — centralizing
quantum-local decisions, or leaving genuinely cross-cutting concerns to individual team
discretion — recreates exactly the inappropriate-governance failure mode from
`evolutionary-architectures/08`, just via an ownership-model mistake instead of a
technology mandate.

**Evolution cadence**: fitness functions need scheduled review, not just initial
creation, directly addressing the "one-time setup" antipattern:
- A **regular cadence** (e.g., quarterly) to review whether existing thresholds still
  make sense given the system's current scale and the business's current risk profile —
  a performance budget set when the system handled 100 req/s needs re-evaluation at
  10,000 req/s, and a security policy calibrated for last year's threat landscape needs
  re-evaluation against this year's.
- A **trigger-based review** whenever an incident occurs that a fitness function should
  have caught but didn't — treating gaps in fitness-function coverage as postmortem
  action items, the same way a functional bug triggers a new regression test.
- An explicit **retirement process** for fitness functions protecting characteristics
  that no longer matter (a migration that finished, a deprecated feature) — removing
  stale checks deliberately, rather than letting them silently accumulate as noise that
  erodes trust in the whole suite (recall from `evolutionary-architectures/02` that a
  fitness function nobody trusts gets routed around, which then risks discrediting even
  the fitness functions that are still meaningful).

### Balancing governance rigor and team autonomy
This is the central organizational trade-off of the whole subject, and it's genuinely
staff/principal-level judgment, not a formula:

- **Too much centralized rigor** — every characteristic governed by centrally-mandated,
  uniformly-applied fitness functions — recreates the inappropriate-governance
  antipattern: teams lose the ability to make context-appropriate trade-offs for their
  own quantum, innovation slows, and teams start treating governance as an obstacle to
  route around rather than a genuine safeguard (which, per the trust dynamic above, is a
  self-reinforcing failure — once teams start routing around governance, it stops
  protecting anything, which then justifies routing around it further).
- **Too little rigor / pure team autonomy** — every team decides everything, with no
  shared, enforced cross-cutting constraints — reintroduces exactly the risks fitness
  functions exist to prevent: security regressions, compliance violations, and
  uncoordinated technology sprawl (a milder, unintentional version of resume-driven
  development, `evolutionary-architectures/08`, multiplied across every team making
  independent, ungoverned choices).

**The resolution the book points toward**: govern the *few things that are genuinely
cross-cutting and non-negotiable* (security baselines, compliance, data residency, a
small set of company-wide reliability guarantees) centrally and rigorously, via fitness
functions with real teeth — and leave everything else (technology choice within
guardrails, internal architecture, quantum-local performance targets) to team autonomy,
verified by fitness functions the *team itself* owns and calibrates. This isn't a fixed
ratio — it's a judgment call that should itself be revisited as the organization's risk
profile and maturity change, and it's exactly the kind of ambiguous, no-clean-answer,
cross-team trade-off that marks this as staff-level (and often principal-level, when the
scope is company-wide) work rather than a mechanical checklist.

### Worked example: designing governance for a specific cross-cutting concern
A company handles customer PII across forty microservices owned by twelve different
teams. A new data-residency law requires EU customer data to stay in EU infrastructure.
Designing the governance response:

1. **Classify the concern**: this is unambiguously cross-cutting — every team handling
   EU customer data is subject to the same legal requirement, with no legitimate
   per-team variation (unlike, say, choice of internal caching library). It belongs in
   the "centrally governed, rigorously enforced" bucket, not team autonomy.
2. **Encode as a fitness function, not a memo**: rather than an email to all
   engineering saying "please make sure EU data stays in the EU," build an automated
   check — e.g., static analysis flagging outbound network calls or database
   connections from any service handling PII to non-EU-tagged infrastructure, wired into
   every affected team's pipeline (`evolutionary-architectures/04`), plus a continual
   production check (per `evolutionary-architectures/03`'s triggered/continual
   distinction) since misconfigured infrastructure could violate this with no code
   change at all.
3. **Assign ownership**: the platform/compliance team owns the fitness function's
   definition and threshold (because the requirement is legal, not a matter of
   engineering taste), but each of the twelve teams is responsible for their own
   service passing it — ownership of the *check* is central, responsibility for
   *passing* it is distributed, which keeps the governance team from becoming a
   bottleneck reviewing forty services by hand.
4. **Set a review trigger**: any change to data-residency law, or any incident
   involving data residency, triggers a mandatory review of this fitness function's
   scope and implementation — it doesn't sit untouched indefinitely once written.

This example threads together fitness functions (`/02`), their categories (`/03`),
pipelines (`/04`), and the antipatterns to avoid (`/08`) into a single governance
decision — which is the point: governance, done well, isn't a separate practice bolted
on top of everything else in this subject, it's the organizational discipline of
applying all of it consistently, at the right scope, on a living cadence.

## Pros
- Scales enforcement without scaling headcount linearly — a well-placed fitness function
  protects every future change automatically, unlike a review board's per-change effort.
- Converts governance disputes into concrete, falsifiable arguments about thresholds and
  scope ("this check is too strict for our quantum's context") rather than vague
  compliance-versus-autonomy politics.
- Distributed ownership with centrally-governed exceptions keeps teams engaged and
  accountable for their own quanta's fitness functions rather than treating governance
  as something imposed from outside.
- Explicit review cadences prevent the "fitness functions as one-time setup" antipattern
  from `evolutionary-architectures/08`.

## Cons
- Deciding what's genuinely cross-cutting versus quantum-local is itself a hard,
  ongoing judgment call with real organizational stakes — get it wrong in either
  direction and you recreate a named antipattern.
- Building and maintaining the governance fitness functions (especially cross-cutting
  ones spanning many teams' pipelines) is significant platform-engineering investment,
  not a policy decision alone.
- Distributed ownership can lead to inconsistent quality of quantum-local fitness
  functions across teams with different skill levels or priorities, without some
  minimum central support or template.
- Requires sustained organizational commitment to the review cadence — it's easy for
  quarterly reviews to quietly stop happening once the original champions move on,
  silently reintroducing the staleness problem this whole practice was designed to avoid.

## Alternatives
- **Centralized architecture review board (document-driven)** — the traditional model
  this lesson positions itself against. Differs by relying on human review and memory for
  enforcement; can still work at small scale (a handful of teams) where a board can
  plausibly track everything, but doesn't scale.
- **Fully decentralized, no cross-cutting governance at all** — trust every team
  completely. Differs by accepting the risk of uncoordinated technology sprawl and
  missed cross-cutting requirements (security, compliance) in exchange for maximum
  velocity and autonomy; can be reasonable for a small, early-stage company with low
  regulatory exposure, but doesn't hold as the company and its risk surface grow.
- **Compliance-as-a-gate at release time only** — check cross-cutting requirements
  (like security scans) only right before a major release, rather than continuously.
  Differs from fitness-function-driven governance by trading continuous, incremental
  verification for a big, late gate — reintroducing the large-batch, late-feedback
  problems that `evolutionary-architectures/04` argues against.

## When to use it
- Any organization past the size where a review board or a handful of senior engineers
  can plausibly track every team's compliance with architectural standards by hand —
  typically once there are more than a few independently-deployable quanta and teams.
- Whenever a genuinely cross-cutting, non-negotiable requirement (security, compliance,
  a company-wide reliability commitment) needs to be guaranteed across many teams
  without creating a manual review bottleneck.

## When NOT to use it
- A small organization with a handful of teams and low regulatory/compliance exposure
  may not need formal, fitness-function-driven governance infrastructure yet — the
  overhead of building and maintaining it can exceed the coordination problem it solves
  at that scale; informal review and direct communication may suffice until the
  organization grows past that point.
- Don't build cross-cutting, centrally-enforced fitness functions for concerns that are
  actually quantum-local judgment calls dressed up as universal standards — that's the
  inappropriate-governance antipattern in a new outfit; genuinely test whether a concern
  is universal before centralizing it.

## Key takeaways / mental model
Governance done well is the organizational-scale expression of everything else in this
subject: it takes the idea that architectural intent should be enforced by automated,
objective fitness functions (`/02`) rather than hoped-for compliance, and applies it
deliberately at the right scope — centrally and rigorously for the few things that are
genuinely universal, and locally with team ownership for everything else — on a living
cadence that keeps the checks meaningful as the system and business change. The
recurring theme across this whole subject is the same at every scale, from a single
dependency rule to company-wide compliance: architectural intent that isn't enforced by
something automated and continuously re-verified is not actually guiding anything — it's
just a hope written down somewhere.

## Self-check questions
1. Why does document-driven governance (standards documents, ADRs alone) fail to scale
   as an organization grows, even if the standards themselves are good ones?
2. Walk through how you'd decide whether a given architectural concern belongs in the
   "centrally governed" bucket or the "team-owned, quantum-local" bucket. What test
   would you apply?
3. In the data-residency worked example, why is ownership of the fitness function's
   *definition* centralized while responsibility for *passing* it is distributed? What
   would go wrong with the opposite split?
4. What's the risk of a governance review cadence that quietly stops happening after
   the original champions move to other work?
5. A new VP argues for "one strict standard, applied to every team, for everything,
   permanently" as the safest governance model. Using the concepts from this subject,
   what would you push back on, and why?

## References
- *Building Evolutionary Architectures*, 2nd ed. (Ford, Parsons, Kua, Sadalage,
  O'Reilly 2022), Chapter 9: Building Evolutionary Architectures (governance and putting
  the practice together)
- `evolutionary-architectures/02` (fitness functions), `/07` (retrofitting), `/08`
  (pitfalls and antipatterns) — governance is the organizational discipline that ties
  these together at scale.
