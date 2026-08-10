---
id: evolutionary-architectures/07
subject: evolutionary-architectures
title: "Building Evolvable Architectures (Retrofitting)"
slug: building-evolvable-architectures
status: drafted
mastery: 
seniority: staff
source: "Building Evolutionary Architectures, 2nd ed. (Ford, Parsons, Kua, Sadalage), Chapter 7"
prerequisites: [evolutionary-architectures/02, evolutionary-architectures/05, evolutionary-architectures/06]
created: 2026-08-10
updated: 2026-08-10
---

# Building Evolvable Architectures (Retrofitting)

## TL;DR
Almost no real system was designed for evolvability from day one — retrofitting it onto
an existing system means finding its *actual* coupling points and quanta (which are
usually messier than any diagram claims), then incrementally strangling in fitness
functions and decoupling, prioritized by which characteristics are genuinely at risk
right now, not by an idealized rewrite plan. This is staff-level work because it
requires reading a system's true structure from evidence, making cross-team trade-off
calls under incomplete information, and sequencing years of incremental change without a
green-field reset.

## The idea

### The retrofitting problem is different from the green-field problem
Everything in lessons 01-06 is easiest to reason about for a system being designed from
scratch: you choose quantum boundaries deliberately, you design the schema with
expand/contract as the default mode of change, you build fitness functions in from day
one. Almost no working engineer spends most of their career on green-field systems.
Most spend it on systems that are already years old, already coupled in ways nobody
fully documented, already carrying assumptions baked into thousands of call sites — and
the business still needs it to keep evolving, because the business itself hasn't stopped
changing just because the codebase is old.

Retrofitting evolvability is fundamentally an exercise in *archaeology followed by
incrementalism*: you can't redesign the whole system at once (too risky, too slow, and
the business won't stand still while you do it), so you have to (1) figure out what's
actually there, underneath the diagrams and stated intentions, and (2) make it
incrementally more evolvable through the same guided, small-step process the rest of
this subject describes — applied to the *architecture itself* as the thing being
evolved.

## How it works

### Step 1: find the real coupling points and quanta, not the documented ones
Architecture diagrams, wikis, and even the org chart routinely describe an aspirational
system, not the actual one. The retrofitting starting point is evidence-based discovery:

- **Trace actual database access**, not documented ownership — query logs, ORM
  configuration, direct SQL grep across every service's codebase. It's common to
  discover three "owning" teams' services all directly querying a table that only one
  team believes it owns.
- **Trace actual call graphs**, not the intended service boundaries — distributed
  tracing data (if it exists) or, failing that, manually walking the code's outbound
  HTTP/RPC clients. This reveals synchronous dependencies that make services one
  quantum in practice (`evolutionary-architectures/05`) even though they're described as
  independent.
- **Trace deploy history correlation** — which services, in practice, tend to get
  deployed together or break together? If deploying service A reliably requires a
  same-day deploy of service B "just to be safe," that's strong empirical evidence
  they're one quantum regardless of what anyone claims.
- **Interview the people who get paged** — on-call engineers and support staff often
  know the *real* coupling ("oh yeah, if you touch that table you have to tell the
  billing team or their nightly job breaks") long before it's written down anywhere,
  because they've lived the incidents.

This step routinely surfaces uncomfortable findings: quanta are bigger than believed,
"independent" services share a database, a single legacy component is a hidden hub that
half the system quietly depends on. That's expected — the whole point of retrofitting is
that the starting map is wrong, and you need the real one before you can safely change
anything.

### Step 2: prioritize which characteristics get fitness functions first
You cannot retrofit fitness functions for every architectural characteristic at once —
that's a multi-year, all-consuming project with no incremental payoff along the way, and
it will lose to the next urgent feature request. The retrofit has to be prioritized
based on **actual, evidenced risk**, not a generic best-practices checklist:

- What has actually broken, or nearly broken, in the last 6-12 months? Incident
  postmortems are a goldmine — if performance regressions caused two outages this
  quarter, a performance-budget fitness function is a higher-priority retrofit than a
  cyclomatic-complexity check nobody has been burned by.
- What characteristic is a known, current business risk? A payments system facing new
  compliance requirements needs a security/audit fitness function before it needs a
  code-style fitness function, even if the code-style violations are more numerous.
  This is the same principle `fundamentals/03` covers for choosing which characteristics
  matter for a given system — retrofitting doesn't get to skip prioritization just
  because the system already exists.
- What's the cheapest fitness function that would have caught the most expensive past
  incident? This reframes the fuzzy question "what should we protect?" into a concrete,
  defensible, backward-looking ROI calculation stakeholders can actually evaluate and
  fund.

### Step 3: incremental, strangler-fig-style decoupling
Once you know the real quanta and have prioritized which characteristics to protect
first, the actual mechanical work of retrofitting looks like a strangler-fig migration:
build the new, better-decoupled path alongside the old one, incrementally route traffic
or responsibility to the new path, and only remove the old path once the new one is
fully verified — the same expand/contract discipline from `evolutionary-architectures/06`
generalized from "schema change" to "architecture change" in general.

**Worked example**: a legacy monolith has `OrderService` code directly querying the
`inventory` table owned (nominally) by a separate `InventoryService` team — discovered
in Step 1 via query-log tracing. Rather than a risky big-bang cutover:

1. Stand up a proper API on `InventoryService` for the specific queries `OrderService`
   currently runs directly against the table.
2. Add a fitness function flagging any *new* direct database access from `OrderService`
   to the `inventory` schema, freezing the wound so it stops getting worse while the fix
   is in progress (this is a fitness function whose job is explicitly to prevent
   backsliding during a migration — an example of the "temporal" category from
   `evolutionary-architectures/03`).
3. Incrementally migrate each existing direct-query call site in `OrderService` to use
   the new API instead, one call site (or one feature) at a time, verifying behavior
   after each migration — small, reviewable, revertible steps, exactly per
   `evolutionary-architectures/04`'s incremental-deployment principle.
4. Once every call site is migrated (verified via the same kind of tracing used in Step
   1 — confirm zero remaining direct queries), revoke `OrderService`'s database
   credentials for the `inventory` schema entirely. This is the "contract" step: it's
   only safe once verified, and it's what actually locks in the improvement — without
   it, nothing stops a future developer from reintroducing a direct query under
   deadline pressure.
5. Only *now* do `OrderService` and `InventoryService` approach being separate quanta in
   the sense of `evolutionary-architectures/05` — this took five deliberate,
   individually-safe steps, not one architectural decision.

### Why this is staff-level, not senior-level, work
The individual mechanics (write a fitness function, do an incremental migration) are
senior-level skills covered in earlier lessons. What makes retrofitting a whole existing
architecture staff-level work is the judgment layered on top:
- **Cross-team negotiation** — the "real" coupling discovered in Step 1 usually spans
  team boundaries nobody wants to admit are entangled; getting agreement to fix it (and
  funding to do so) is an organizational problem, not just a technical one.
- **Sequencing decisions with no clean answer** — which of five discovered coupling
  problems gets fixed first, when fixing any one of them takes months and the business
  wants feature work too? This requires weighing risk, cost, and organizational appetite
  simultaneously, usually under incomplete information about all five problems' true
  severity.
- **Working without the safety net of a green-field reset** — every step must keep the
  system running and correct in production throughout a months-or-years-long process;
  there's no "pause the business while we redesign this."

## Pros
- Makes evolvability achievable for the vast majority of real systems, which are
  brownfield, not green-field.
- Evidence-based discovery (Step 1) frequently surfaces risks the organization didn't
  know it had, independent of the evolvability project's original goal.
- Prioritizing by actual incident history (Step 2) produces defensible, fundable work
  instead of a vague "let's improve architecture" initiative that's easy to deprioritize.
- Strangler-fig-style incrementalism (Step 3) keeps the system shippable and the
  business unblocked throughout a long migration.

## Cons
- Discovery work (Step 1) is genuinely time-consuming and can surface more problems than
  the organization has appetite to fix, creating its own prioritization and morale
  challenge.
- Retrofitting is slower and messier than doing it right the first time — there's no way
  to fully avoid the cost of the original coupling, only to pay it down incrementally.
- Requires sustained organizational buy-in over a long timeline; a change in leadership
  priorities partway through can leave a system in an awkward, half-migrated state
  (some call sites migrated, some not) that's arguably worse than the original
  consistent-but-coupled state if the migration stalls indefinitely.
- Cross-team coupling discoveries can create political friction ("your team has been
  secretly depending on our internal table for two years") that needs careful handling,
  separate from the technical fix.

## Alternatives
- **Full rewrite** — discard the existing system and build a new one with evolvability
  designed in from the start. Differs by trading a long, uncertain, high-risk project
  (rewrites notoriously underestimate the hidden behavior/edge cases baked into the old
  system) for a clean design; occasionally justified when the existing system's
  technology or fundamental model is genuinely unsalvageable, but the book (and most
  practitioner experience) treats incremental retrofitting as the safer default.
- **Do nothing until it's a crisis** — defer evolvability work indefinitely, treating
  the aging architecture as acceptable until a specific failure forces action. Differs by
  accepting compounding risk and cost in exchange for near-term feature velocity;
  rational only in the very short term, and the cost of eventual forced action is
  usually far higher than incremental retrofitting would have been.
- **Freeze and wrap (anti-corruption layer only)** — instead of decoupling the legacy
  system internally, wrap it behind a stable interface and prevent any new system from
  depending on its internals directly, without fixing the internal coupling itself.
  Differs by containing the *blast radius* of the legacy coupling on new work without
  actually resolving it; a reasonable interim step or even permanent solution for a
  system nearing end-of-life, but doesn't make the legacy system itself more evolvable.

## When to use it
- Any existing system where the business needs continued evolution but the architecture
  has accumulated coupling that makes change expensive and risky — i.e., most systems
  more than a couple of years old.
- Before undertaking a larger modernization or decomposition effort, as the essential
  discovery phase that prevents the effort from being planned against a fictional
  diagram of the current state.

## When NOT to use it
- A system genuinely near end-of-life, being actively replaced or sunset on a known
  timeline, may not be worth this investment — a "freeze and wrap" or "do nothing"
  approach can be the rational choice if the system won't exist much longer anyway.
- A system with low change velocity and no near-term evolution needs (see
  `evolutionary-architectures/01`'s "when not to use" case) doesn't need this investment
  either — retrofitting evolvability only pays off if you're actually going to need to
  evolve the thing.

## Key takeaways / mental model
Retrofitting evolvability is archaeology, then triage, then strangler-fig surgery: first
find out what's really coupled (not what the diagram says), then prioritize fixes by
actual evidenced risk (not a generic checklist), then decouple incrementally with the
same expand/contract discipline used for data, verified and locked in with fitness
functions at each step. The staff-level skill isn't any single technique here — it's
sequencing a multi-month-or-year, cross-team effort so the system stays correct and
shippable throughout, under real organizational constraints and incomplete information.

## Self-check questions
1. Why can't architecture diagrams or documentation be trusted as the starting point for
   a retrofit? What evidence would you gather instead, and how?
2. Walk through how you would prioritize which of five discovered coupling problems to
   fix first in a real system, given limited engineering time.
3. Explain the strangler-fig migration in the worked example, step by step, and identify
   which step is the riskiest and why.
4. Why is "do nothing until it's a crisis" a rational-sounding but usually costly choice?
5. What makes retrofitting work staff-level rather than senior-level, given that the
   individual techniques involved (fitness functions, incremental migration) are
   themselves senior-level skills?

## References
- *Building Evolutionary Architectures*, 2nd ed. (Ford, Parsons, Kua, Sadalage,
  O'Reilly 2022), Chapter 7: Evolutionary Architecture Topologies (and the retrofitting
  guidance threaded through the book's case studies)
- `evolutionary-architectures/05` (coupling and quanta) and `/06` (evolutionary data) —
  the discovery and migration techniques this lesson generalizes to whole-architecture
  retrofits.
