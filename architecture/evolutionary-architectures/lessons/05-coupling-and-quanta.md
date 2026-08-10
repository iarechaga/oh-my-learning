---
id: evolutionary-architectures/05
subject: evolutionary-architectures
title: "Architectural Coupling and Quanta"
slug: coupling-and-quanta
status: drafted
mastery: 
seniority: senior
source: "Building Evolutionary Architectures, 2nd ed. (Ford, Parsons, Kua, Sadalage), Chapter 5"
prerequisites: [evolutionary-architectures/01, hard-parts/02]
created: 2026-08-10
updated: 2026-08-10
---

# Architectural Coupling and Quanta

## TL;DR
An **architecture quantum** — an independently deployable artifact with high functional
cohesion, high static coupling internally, and its own operational data — is the real
boundary for how far architectural change can safely ripple. Evolutionary architecture
lives or dies on quantum boundaries: components inside the same quantum evolve together
(any change to one may require redeploying/reverifying the others), while components in
different quanta can evolve independently. Getting the quantum boundary wrong is the
single most common reason "modular" or "microservices" systems turn out not to be very
evolvable at all.

## The idea

### Why "independent change" needs a precise unit of measure
`evolutionary-architectures/01` defines evolutionary architecture as guided, incremental
change. But incremental *relative to what*? If changing one microservice secretly
requires redeploying four others in lockstep because of shared runtime state or a shared
database, then the "microservice" boundary on the architecture diagram is fiction — the
*real* unit that must change together is the whole cluster of five, whatever the org
chart or repo layout says. Evolutionary architecture requires knowing your *actual*
independently-changeable boundaries, not the ones drawn on a slide.

The book (and `hard-parts/02`, which this lesson builds directly on and does not
duplicate in full — read it first if you haven't) names this real boundary the
**architecture quantum**: an independently deployable artifact with (1) high functional
cohesion, (2) high static coupling *inside* the boundary, and (3) synchronous dynamic
coupling for the runtime interactions that define it. Two components belong to the same
quantum if they cannot be deployed, verified, or rolled back independently of each
other — regardless of whether they live in separate repos, separate containers, or are
labeled "separate services."

### Static vs. dynamic coupling, quickly recapped for this lesson's purpose
(Full treatment in `hard-parts/02` and `hard-parts/03` — this is the minimum needed
here.)
- **Static coupling** — compile-time/build-time dependencies: shared libraries, shared
  database schemas, shared contracts. This determines what must be *deployed* together.
- **Dynamic coupling** — runtime communication patterns: synchronous vs. asynchronous
  calls, how failures and latency propagate. This determines what must *behave*
  correctly together at runtime, even if deployed separately.

A quantum boundary is drawn where *both* kinds of coupling become loose enough to allow
independent change. High static coupling (a shared database, a shared internal library
whose interface changes force recompilation everywhere) forces lockstep deployment.
Tightly synchronous dynamic coupling (service A calls service B and blocks, with no
tolerance for B being briefly unavailable or slightly incompatible) forces lockstep
*operational* behavior even when the code deploys independently.

### Why quantum boundaries determine evolvability
Evolution — trying something new, verifying it with a fitness function, keeping it if it
works — is cheap and low-risk *within* a well-isolated quantum, and expensive and
high-risk *across* quantum boundaries. Changing something inside one quantum has a
contained blast radius: you deploy it, its own fitness functions verify it, done.
Changing something that spans quanta (a shared database schema used by three services,
a synchronous call chain that assumes a specific response shape everywhere) requires
coordinating the change across every affected quantum simultaneously — exactly the
big-batch, high-risk, hard-to-verify-incrementally change that evolutionary architecture
is trying to avoid.

This is why identifying your real quanta (not your aspirational ones) is a prerequisite
step for evolutionary-architecture work, not a nice-to-have: if you don't know where
your actual boundaries are, you can't know which changes are safe to make
incrementally and which ones secretly require a coordinated, larger effort — and you'll
be repeatedly surprised by "small" changes that turn into multi-team fire drills.

## How it works

### Worked example 1: the "microservices" that are actually one quantum
A team has three services: `OrderService`, `InventoryService`, and `PaymentService`,
each in its own repo, each with its own CI pipeline, each deployed to its own container.
On paper: three quanta. In practice:

- All three read and write to the same shared PostgreSQL database, with `OrderService`
  directly querying tables that `InventoryService` also writes to (high static coupling
  via shared schema).
- `OrderService` calls `InventoryService` synchronously and blocks on the response, with
  no timeout or fallback — if `InventoryService`'s response shape changes even slightly,
  `OrderService` breaks immediately (tight synchronous dynamic coupling).

Given the quantum definition, these three "services" are actually **one architecture
quantum**. Deploying a schema change to the `inventory` table requires verifying
`OrderService` still works against it — you can't safely change `InventoryService`'s
data model without also considering `OrderService`'s and `PaymentService`'s assumptions
about it. The team's mental model ("three independently deployable services") is wrong
in the way that matters: evolving one "service" independently is not actually safe, no
matter how the repos are split. Any fitness function claiming to protect "OrderService
can deploy independently" would be false — and worse, nobody would notice until an
attempted independent deploy breaks production.

### Worked example 2: shrinking the quantum by removing coupling
Take the same three services and change two things:
1. Give each service its own database (or at minimum, its own schema/tables that only
   it writes to), replicating any data another service needs via an event stream instead
   of direct queries — this removes the static coupling via shared schema (see
   `evolutionary-architectures/06` for the data-ownership piece of this).
2. Change `OrderService -> InventoryService` from a blocking synchronous call to an
   asynchronous, eventually-consistent flow (`OrderService` publishes an
   "order placed" event; `InventoryService` reserves stock asynchronously and publishes
   back) — this loosens the dynamic coupling from "must respond correctly, synchronously,
   right now" to "must eventually process the event correctly."

After these changes, the three services approach being genuinely separate quanta:
`InventoryService` can change its internal data model, redeploy, and roll back without
coordinating a simultaneous deploy of `OrderService`, as long as it honors its event
contract. This is the practical work of "shrinking the quantum" — deliberately removing
static and dynamic coupling until the deployable boundary matches the boundary you
actually want to be able to evolve independently.

Note the trade-off, made explicit rather than hand-waved: the async version accepts
eventual consistency and added operational complexity (event schemas, retries, ordering)
in exchange for independent evolvability. That's a genuine cost, not a free win — see
"Cons" below and the broader trade-off framing in `hard-parts/02` and `hard-parts/03`.

### Worked example 3: quantum boundaries and fitness function scope
Quantum boundaries directly determine what scope a fitness function needs, connecting
this lesson back to `evolutionary-architectures/02` and `/03`:
- **Within a quantum**: atomic fitness functions (dependency-direction rules,
  unit-level performance budgets) are usually sufficient — the blast radius of a
  violation is contained to the quantum.
- **Across quanta**: you need holistic fitness functions (per
  `evolutionary-architectures/03`) — e.g., a contract test verifying `OrderService`'s
  assumptions about the event shape `InventoryService` publishes stay compatible, run
  continuously since either side could change independently. A holistic fitness function
  is, in a sense, exactly the tool for verifying that a cross-quantum boundary is being
  respected — that the *coupling that remains* (an event contract, an API contract)
  hasn't silently tightened back into an implicit, unverified dependency.

### Common failure mode: quantum mismatch hiding in "just one more query"
The most frequent way teams accidentally merge two intended quanta back into one is
gradual: a developer under deadline pressure adds "just one more" direct database query
across a service boundary, or "just one more" synchronous call because it's faster to
build than the properly decoupled async version. Individually, each of these seems
harmless. Collectively, they re-couple services that were deliberately designed to be
separate quanta, and nobody notices until an attempted independent deploy breaks in
production. This is exactly the class of slow, silent drift that atomic fitness
functions (a dependency-direction check that flags cross-service database access, for
instance) exist to catch — connecting this lesson concretely back to
`evolutionary-architectures/02`.

## Pros
- Gives a precise, testable definition of "independently deployable," replacing vague
  claims like "we're microservices" with a checkable boundary.
- Explains *why* certain "small" changes turn into large coordinated efforts (they cross
  a real quantum boundary even if they look small on a diagram).
- Directly informs what scope of fitness function you need where (atomic inside a
  quantum, holistic across quanta).

## Cons
- Correctly identifying real quantum boundaries in an existing system takes real
  investigative effort — static and dynamic coupling aren't always visible from the
  architecture diagram; you often have to trace actual database access and call graphs.
- Shrinking a quantum (decoupling shared data, moving from sync to async) has genuine
  costs: eventual consistency, more operational complexity, more moving parts to
  monitor — not a pure win, and not always worth it for a given pair of components.
- Quantum boundaries can shift over time as coupling is added or removed; treating them
  as a one-time analysis rather than something to re-verify (with fitness functions) lets
  drift creep back in.

## Alternatives
- **Bounded contexts (DDD)** — a domain-modeling boundary based on shared language and
  business meaning. Differs by being a *conceptual/modeling* boundary, not necessarily a
  *deployment* boundary; a bounded context and an architecture quantum often align but
  aren't guaranteed to (you can have one bounded context split across quanta, or one
  quantum spanning parts of two bounded contexts, though both are usually signs worth
  investigating).
- **Team/ownership boundaries (Conway's Law)** — draw the boundary around who owns what
  organizationally. Differs by being a social/organizational lens rather than a technical
  coupling lens; ideally these align with quantum boundaries (a team should own a
  quantum, not half of two), but org charts and technical coupling frequently drift apart
  in real companies.
- **Repo/deployment-artifact count as a proxy** — assume "N repos/containers = N
  independent units." Differs (and is the mistake this lesson warns against) by
  measuring surface structure instead of actual static/dynamic coupling; a cheap first
  guess, but unreliable without verifying coupling directly.

## When to use it
- Before deciding how to decompose a system, or before evaluating whether an existing
  decomposition is real or aspirational.
- When diagnosing why "independent" services keep requiring coordinated releases —
  quantum analysis usually reveals the specific coupling causing it.
- As the scoping input for deciding which fitness functions need to be atomic versus
  holistic (per `evolutionary-architectures/03`).

## When NOT to use it
- Don't chase minimal quanta (maximal decoupling) as a goal in itself — some coupling is
  cheaper to keep than to remove, especially for components that genuinely change
  together for good domain reasons (see the "last 10% trap" and inappropriate governance
  antipatterns in `evolutionary-architectures/08` for what over-applying decomposition
  can cost).
- For a small system with one team and low change velocity, formal quantum analysis is
  likely overkill — the coordination cost quantum boundaries are meant to solve doesn't
  exist yet at that scale.

## Key takeaways / mental model
The architecture quantum is the *actual* unit of independent evolution — not the repo
count, not the container count, not the org chart, but the real boundary set by static
coupling (what must deploy together) and dynamic coupling (what must behave correctly
together at runtime). Evolutionary architecture's promise of cheap, incremental,
guided change is only true *within* a quantum; crossing a quantum boundary re-introduces
the big-batch, high-coordination-cost change the whole approach is trying to escape.
Before claiming a system is evolvable, trace its real quanta — you may find they're
bigger (or drawn in different places) than the architecture diagram suggests.

## Self-check questions
1. Define an architecture quantum in your own words, including all three defining
   properties.
2. Why can three services in three separate repos and containers still be one quantum?
   Give the specific coupling that would cause this.
3. What did the team in worked example 2 trade away in exchange for shrinking the
   quantum (moving from sync calls + shared DB to async events + separate data)?
4. Why does quantum boundary analysis directly determine whether a fitness function
   needs to be atomic or holistic?
5. Describe a "just one more query" scenario from your own experience (or a plausible
   one) that silently re-merged two intended quanta, and what fitness function would
   have caught it.

## References
- *Building Evolutionary Architectures*, 2nd ed. (Ford, Parsons, Kua, Sadalage,
  O'Reilly 2022), Chapter 5: Evolvable Architectural Structures
- `hard-parts/02` (The Architecture Quantum and Static Coupling) — the primary,
  fuller treatment of static coupling and connascence this lesson builds on.
- `hard-parts/03` (Dynamic Coupling) — the runtime-communication half of the coupling
  picture referenced here.
