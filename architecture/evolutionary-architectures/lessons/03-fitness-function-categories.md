---
id: evolutionary-architectures/03
subject: evolutionary-architectures
title: "Categories of Fitness Functions"
slug: fitness-function-categories
status: drafted
mastery: 
seniority: senior
source: "Building Evolutionary Architectures, 2nd ed. (Ford, Parsons, Kua, Sadalage), Chapter 3"
prerequisites: [evolutionary-architectures/02]
created: 2026-08-10
updated: 2026-08-10
---

# Categories of Fitness Functions

## TL;DR
Fitness functions are classified along several independent dimensions —
**atomic vs. holistic**, **triggered vs. continual**, **static vs. dynamic**, plus
**domain-specific** and **temporal** variants. A single real-world fitness function is
usually a point in this multi-dimensional space, not just one type. The categories
matter because they tell you what a check *can't* catch: an atomic check can pass while
a holistic regression sneaks through, and a triggered check can pass while a dynamic,
runtime-only failure sneaks through.

## The idea

### Why categorize at all?
It's tempting to treat "we have fitness functions" as a binary — either the team has
some CI checks or it doesn't. But not all fitness functions catch the same class of
problem, and teams that only build one *kind* of fitness function (typically: fast,
atomic, triggered, static ones — because those are the easiest to write) develop a false
sense of security. They pass every build and still ship systems that degrade in ways
none of their checks were built to see. The categorization exists to make the *coverage
gaps* visible, so you can deliberately decide which gaps you're accepting versus which
ones you're closing.

## How it works

### Dimension 1: Atomic vs. Holistic
- **Atomic** fitness functions verify one architectural characteristic in isolation,
  usually scoped to one part of the codebase. Example: "class `OrderService` must not
  import from package `billing.internal`." Fast, cheap, easy to reason about, easy to
  pinpoint the cause of a failure.
- **Holistic** fitness functions verify how multiple characteristics or components
  interact — they can pass every individual atomic check and still fail the holistic
  one. Example: an end-to-end test that exercises the checkout flow across five
  microservices and asserts the whole flow completes under 2 seconds *and* that no
  service made more than one call to any other service (catching an accidental N+1
  fan-out that no single service's atomic latency check would reveal, because each
  individual call is fast — it's the aggregate interaction that's slow).

Why holistic checks matter: modern systems fail at the seams, not usually within a
single well-tested module. A service mesh where every service independently meets its
own SLA can still produce an end-to-end user experience that's unacceptably slow,
because latencies compound across the call chain, retries multiply load, and a
circuit-breaker in one service can cascade failures to five others. No atomic check,
run in isolation, can see that — you need a fitness function whose scope spans the
interaction.

### Dimension 2: Triggered vs. Continual
- **Triggered** fitness functions run in response to a specific event: a commit, a pull
  request, a deploy, a scheduled cron job. Example: the dependency-direction check from
  `evolutionary-architectures/02`, which runs on every CI build.
- **Continual** fitness functions run constantly, monitoring the system in a steady
  state rather than reacting to a discrete event. Example: a production APM alert that
  continuously watches p99 latency and pages on-call if it crosses a threshold for more
  than five minutes, independent of any deploy happening.

Why the distinction matters: some regressions have nothing to do with a code change.
Recall the CVE-scanner example from `evolutionary-architectures/02` — the codebase
didn't change, but a newly disclosed vulnerability made a previously "fit" dependency
unfit. A purely triggered fitness function (only running on commits) would never catch
this, because there's no commit to trigger it. You need something continual (a
scheduled nightly scan, or a subscription to a vulnerability feed) to close that gap.
Similarly, infrastructure can degrade with zero code changes — a certificate expiring,
a disk filling up, a downstream vendor's API getting slower — and only a continual
fitness function watches for that.

### Dimension 3: Static vs. Dynamic
- **Static** fitness functions have a fixed pass/fail criterion that doesn't change
  based on context: "cyclomatic complexity ≤ 10," "zero critical CVEs."
- **Dynamic** fitness functions have a criterion that adapts based on context — time of
  day, business cycle, current load, or other systems' state. Example: an e-commerce
  site's fitness function for "maximum acceptable checkout latency" might tighten during
  a Black Friday sale (when the business cares intensely about conversion-rate-killing
  slowness) and loosen during a 3am low-traffic window (where absolute latency matters
  less than resource cost). Another example: an autoscaling-aware fitness function that
  asserts "CPU utilization stays under 80%" only makes sense relative to the current
  number of provisioned instances — the threshold's *meaning* is dynamic even if the
  number 80% is static.

Why it matters: a purely static threshold, picked once, can become wrong as the system's
context changes — either too strict (constant false alarms as legitimate variation in
normal operation trips it) or too lax (it was calibrated for last year's traffic and no
longer protects anything). Dynamic fitness functions cost more to design and reason
about, but they avoid both failure modes for characteristics whose "acceptable" range
genuinely depends on context.

### Dimension 4: Domain-specific
Some fitness functions encode rules unique to your business domain, not generic
architecture hygiene. Example: a healthcare system's fitness function asserting "no
patient-identifiable field ever appears in a log line" (a HIPAA-driven concern specific
to that domain) or a financial system's "double-entry ledger fitness function" that
verifies every transaction's debits and credits sum to zero across the whole system.
These require domain knowledge to write — a generic architecture tool won't hand them to
you — but they're often the highest-value fitness functions a team can build, because
they encode the actual business-critical invariant, not a generic best practice.

### Dimension 5: Temporal
A fitness function scoped to only be true (or only be checked) during a specific window
of time. Example: during a database migration, a temporary fitness function might assert
"the old and new schema stay in sync" — a check that's only meaningful for the duration
of the migration and should be deliberately deleted once the migration completes (an
example of managing fitness-function lifecycle, not just adding them — a stale temporal
check left in the pipeline after its purpose has passed is itself a form of drift).

### Worked example: classifying one fitness function along multiple dimensions
Take the checkout-flow example from the "Atomic vs. Holistic" section: an end-to-end
test asserting the multi-service checkout flow completes under 2 seconds and involves no
more than one call between any two services.

- **Atomic vs. Holistic**: holistic (spans multiple services and their interaction).
- **Triggered vs. Continual**: as described, triggered (runs on merge to the release
  branch) — but a team might reasonably *also* run a continual version of the same idea
  in production via distributed tracing + an SLO alert, making the "same" underlying
  characteristic protected by both a triggered and a continual fitness function. This is
  common and often desirable: triggered catches it before deploy (cheap to fix), continual
  catches it if it slips through anyway (expensive but still better than nobody noticing).
- **Static vs. Dynamic**: as specified (flat 2-second threshold), it's static. A more
  sophisticated version — tightening the threshold during peak sale traffic — would make
  it dynamic.
- **Domain-specific**: not really — "checkout shouldn't be slow due to fan-out" is a
  generic distributed-systems concern, not unique to this business (contrast with the
  double-entry ledger example, which is deeply domain-specific).
- **Temporal**: no, it's meant to be permanent, not tied to a specific window.

This shows the real point of the taxonomy: it's not a checklist to "cover every box"
mechanically, it's a set of questions to ask about *every* fitness function you write —
"does this need to be holistic, not just atomic? Does this need a continual variant, not
just a triggered one? Does the threshold need to flex with context?" — so that coverage
gaps are a deliberate choice, not an accident of only knowing how to write the easy kind.

### Why holistic and continual checks are systematically under-built
Both are harder to write than atomic/triggered checks:
- Holistic checks require cross-team coordination (whose test is this, who owns fixing
  a failure that spans five teams' services?) and are more brittle/flaky by nature
  (more moving parts = more sources of nondeterminism).
- Continual checks require production monitoring infrastructure, alerting pipelines,
  and on-call ownership — organizational investment beyond "add a CI step."

Teams under delivery pressure gravitate to what's cheap: atomic, triggered, static
checks. That's a reasonable starting point, but it leaves exactly the failure modes that
matter most at scale — cross-cutting regressions and non-deploy-triggered decay —
uncovered. Recognizing this bias is the practical payoff of learning the taxonomy: know
which corner of the space your current fitness-function suite lives in, and treat the
uncovered corners as known risk, not invisible risk.

## Pros
- Makes coverage gaps explicit and discussable instead of an unknown unknown.
- Guides prioritization: which category of fitness function would catch the failure
  modes that actually hurt this system?
- Prevents false confidence from "we have fitness functions" when in practice only the
  cheapest category has been built.

## Cons
- More categories to reason about adds conceptual overhead versus "just write tests."
- Holistic and continual fitness functions are genuinely expensive to build and
  maintain — categorizing the gap doesn't make closing it cheap.
- Over-applying the taxonomy (trying to hit every category for every characteristic) is
  wasted effort; not every characteristic needs a dynamic or domain-specific variant.

## Alternatives
- **Single-category checklist (just "do we have CI tests?")** — simpler to communicate
  but hides the specific failure modes (cross-cutting, non-deploy-triggered, context-
  sensitive) that a one-dimensional view can't see.
- **Risk-based ad hoc prioritization without a taxonomy** — pick fitness functions purely
  by "what bit us last time," skipping formal categorization. Can work for a mature team
  with strong incident-review discipline, but tends to under-invest in categories the
  team hasn't been burned by yet (e.g., no continual checks until a non-deploy-triggered
  incident happens once, painfully).

## When to use it
- When designing or auditing a fitness-function suite for an important system: walk
  through each dimension explicitly and ask which of your current checks are missing
  from each category, and whether that gap is acceptable.
- When a production incident wasn't caught by any existing fitness function — classify
  what *kind* of check would have caught it (usually reveals a missing holistic or
  continual check) before writing the fix.

## When NOT to use it
- Don't force every fitness function into every category "for completeness" — a simple,
  cheap atomic/triggered/static check is often exactly the right tool, and adding
  unnecessary holistic/dynamic variants is waste.
- Don't use the taxonomy as a gate that blocks shipping a useful atomic check just
  because you haven't also built the holistic one yet — partial coverage that ships
  today beats comprehensive coverage that ships never.

## Key takeaways / mental model
Picture fitness functions living on three independent axes: scope (atomic <-> holistic),
cadence (triggered <-> continual), and rigidity (static <-> dynamic), plus two special
tags (domain-specific, temporal). Most teams' fitness-function suites cluster in one
corner of this space (atomic, triggered, static) because that corner is cheapest to
build — which is fine as a start, but leaves cross-cutting and non-deploy-triggered
regressions systematically uncaught. Auditing your fitness functions means asking, for
each important characteristic: which corner of this space are we actually covering, and
is that the corner where our real risk lives?

## Self-check questions
1. Give an example of a regression that a well-built atomic fitness function would miss
   but a holistic one would catch, and explain why.
2. Why can a fitness function fail even though no commit triggered it? Which category
   distinction explains this?
3. Design a dynamic fitness function for a system you know — what makes its threshold
   context-dependent rather than fixed?
4. Why do teams systematically under-invest in holistic and continual fitness functions
   even when they know about them?
5. Classify a fitness function from `evolutionary-architectures/02` (the CVE scanner or
   the performance budget) along all five dimensions from this lesson.

## References
- *Building Evolutionary Architectures*, 2nd ed. (Ford, Parsons, Kua, Sadalage,
  O'Reilly 2022), Chapter 3: Categorizing Fitness Functions
