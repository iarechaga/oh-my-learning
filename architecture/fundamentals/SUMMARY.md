# Fundamentals of Software Architecture - Subject Summary

A comprehensive recap of *Fundamentals of Software Architecture*, concept by concept.
This subject is the consolidation layer of the architecture track: it gives names to
architecture work, explains quality attributes and modularity, surveys the major
architecture styles, and closes with the practical skills architects need to govern,
communicate, and evolve decisions.

**Source book:** *Fundamentals of Software Architecture: An Engineering Approach* -
Mark Richards and Neal Ford (O'Reilly, 2nd ed., 2025).

**Progress note:** all 22 lessons are `drafted`; none discussed yet, so mastery is
pending and no weak spots are recorded. See the table in [README.md](README.md).
Reading order is top to bottom (dependency-ordered).

## Foundations: thinking, characteristics, and modularity

- **[01] Architectural thinking** - the shift from local design detail to broad system
  trade-offs, business alignment, architecture-vs-design boundaries, and the need to
  reason from context rather than copy patterns. ([lesson](lessons/01-architectural-thinking.md))
- **[02] The role of the software architect** - technical direction, mentoring,
  governance, communication, and the balance between staying hands-on and maintaining
  breadth across many technologies. ([lesson](lessons/02-role-of-the-software-architect.md))
- **[03] Architectural characteristics** - quality attributes as first-class design
  drivers: operational, structural, and cross-cutting characteristics such as
  scalability, reliability, performance, maintainability, testability, security, and
  deployability. ([lesson](lessons/03-architectural-characteristics.md))
- **[04] Discovering architectural characteristics** - how to derive characteristics
  from stakeholder concerns, business goals, domain constraints, explicit requirements,
  and implicit risks. ([lesson](lessons/04-discovering-architectural-characteristics.md))
- **[05] Measuring and governing characteristics** - turning characteristics into
  metrics, fitness functions, CI/CD checks, review practices, and guardrails that stop
  architecture from drifting. ([lesson](lessons/05-measuring-governing-characteristics.md))
- **[06] Modularity fundamentals** - cohesion, coupling, encapsulation, afferent and
  efferent coupling, instability, connascence, and why boundaries are the raw material
  of architecture. ([lesson](lessons/06-modularity-fundamentals.md))
- **[07] Component-based thinking** - identifying, sizing, naming, and partitioning
  logical components before deciding whether anything should become a service.
  ([lesson](lessons/07-component-based-thinking.md))
- **[08] Architecture quanta** - independently governable and deployable architecture
  units, plus the static and dynamic coupling that prove whether a unit is truly
  independent. ([lesson](lessons/08-architecture-quanta.md))

## Topology: monolithic and distributed choices

- **[09] Monolithic vs distributed architecture** - the fundamental topology decision:
  monoliths are simpler, faster, and easier to reason about, while distributed systems
  buy independent scale, deployment, and fault boundaries at high operational cost.
  ([lesson](lessons/09-monolithic-vs-distributed-architecture.md))
- **[10] The fallacies of distributed computing** - the false assumptions architects
  make about networks, latency, bandwidth, security, topology, administration,
  transport cost, and homogeneity. ([lesson](lessons/10-fallacies-of-distributed-computing.md))

## Architecture styles

- **[11] Layered architecture** - horizontal technical layers, closed and open layers,
  dependency direction, isolation, and the architecture sinkhole anti-pattern.
  ([lesson](lessons/11-layered-architecture.md))
- **[12] Modular monolith** - domain modules inside one deployable unit, with explicit
  APIs, logical data separation, fast in-memory communication, and a clean extraction
  path toward services if scale demands it. ([lesson](lessons/12-modular-monolith.md))
- **[13] Pipeline architecture** - pipe-and-filter structures for staged transformations,
  batch processing, compiler-like flows, ingestion pipelines, and ETL-style work.
  ([lesson](lessons/13-pipeline-architecture.md))
- **[14] Microkernel architecture** - a minimal core plus plug-ins, extension contracts,
  registries, and the fit for products that need controlled customization.
  ([lesson](lessons/14-microkernel-architecture.md))
- **[15] Service-based architecture** - coarse-grained services and shared databases as
  a pragmatic middle ground between monoliths and fine-grained microservices.
  ([lesson](lessons/15-service-based-architecture.md))
- **[16] Event-driven architecture** - producers, channels, consumers, broker vs
  mediator topologies, asynchronous decoupling, dead-letter handling, and governance
  risks around event contracts. ([lesson](lessons/16-event-driven-architecture.md))
- **[17] Space-based architecture** - replicated in-memory processing units and
  virtualized middleware that remove the database from the hot path for extreme
  concurrency and elasticity. ([lesson](lessons/17-space-based-architecture.md))
- **[18] SOA and microservices** - the contrast between enterprise integration through
  SOA and application-level autonomy through microservices, including governance,
  data ownership, operational cost, and team fit. ([lesson](lessons/18-soa-and-microservices.md))
- **[19] Choosing an architecture style** - a selection framework that matches
  characteristics, constraints, team topology, risk, cost, and evolution paths to
  suitable styles or hybrids. ([lesson](lessons/19-choosing-an-architecture-style.md))

## Decisions, risk, communication, and leadership

- **[20] Architecture decisions and ADRs** - how to record decisions, context,
  alternatives, consequences, and point-in-time rationale so teams do not repeat old
  debates or lose why a choice was made. ([lesson](lessons/20-architecture-decisions-and-adrs.md))
- **[21] Architecture risk and communication** - risk storming, likelihood-impact
  matrices, C4-style diagrams, presentations, and translating technical risk into
  business impact. ([lesson](lessons/21-architecture-risk-and-communication.md))
- **[22] Architect leadership and career** - leading by influence, negotiating trade-offs,
  architecture laws, intersections with operations/data/platform/AI, and growing from
  deep specialist to broad technical leader. ([lesson](lessons/22-architect-leadership-and-career.md))

## Focus areas

None yet - no discussions have been held. After each discussion, the recorded weak
spots and misconceptions will be aggregated here, with extra detail on concepts rated
`shaky` or `not-yet`.
