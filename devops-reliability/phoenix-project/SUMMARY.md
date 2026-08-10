# The Phoenix Project

A comprehensive per-concept recap of *The Phoenix Project: A Novel about IT, DevOps,
and Helping Your Business Win* by Gene Kim, Kevin Behr, and George Spafford. The
subject turns Parts Unlimited's fictional near-collapse into a durable operating
model: see the system, find the constraint, limit work in process, then build fast
flow, fast feedback, and continual learning across an organization whose Dev, Ops,
and business functions finally point at a shared goal.

Progress note: all 10 lessons are `drafted`; none have been discussed yet, so
mastery is pending across the board and no weak spots are recorded yet. This page
will gain depth (especially on the concepts the learner finds hard) as discussions
happen - the last section below will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom:
the crisis framed as a systems problem first, then flow and constraints, then the
Three Ways, then technical debt, org dynamics, and the strategic payoff.

## Seeing the system

- **[phoenix-project/01] The Parts Unlimited crisis as a systems problem** -
  recurring IT failures are almost always produced by structural conditions (no
  visibility, no shared prioritization, unmanaged dependencies), not individual
  incompetence; fix the system or the same failure recurs with a different name
  attached. ([lesson](lessons/01-parts-unlimited-systems-problem.md))
- **[phoenix-project/02] Work as flow: from projects to value streams** - stop
  managing IT as a pile of disconnected projects and start tracing it as one
  continuous value stream from request to production; lead time is almost always
  dominated by queueing between teams, not active work time.
  ([lesson](lessons/02-work-as-flow-value-streams.md))

## Constraints and flow discipline

- **[phoenix-project/03] Theory of Constraints for IT operations** - total system
  throughput is capped by its single slowest stage; identify, exploit, subordinate
  to, and elevate the constraint, then repeat once a new one appears. At Parts
  Unlimited the constraint is a person, Brent, not a machine.
  ([lesson](lessons/03-theory-of-constraints-it.md))
- **[phoenix-project/04] WIP limits and reducing multitasking damage** - starting
  more concurrent work doesn't add capacity, it subtracts it; capping work in
  process is the concrete mechanism that operationalizes "subordinate everything
  else to the constraint." ([lesson](lessons/04-wip-limits-multitasking.md))

## The Three Ways

- **[phoenix-project/05] The First Way: fast left-to-right flow** - work should
  move from Dev through Ops to the customer as fast and smoothly as possible, and a
  defect should never be allowed to flow downstream where it compounds; small
  batches and "stop the line" are the concrete practices.
  ([lesson](lessons/05-first-way-flow.md))
- **[phoenix-project/06] The Second Way: amplifying feedback loops** - feedback
  must flow right to left just as fast and unfiltered as work flows forward; the
  cost of correcting a mistake grows sharply with how long and how many layers it
  takes to reach the person who can fix it. ([lesson](lessons/06-second-way-feedback.md))
- **[phoenix-project/07] The Third Way: continual learning and experimentation** -
  convert individual, local incident learning into durable, organization-wide
  capability through blameless postmortems and deliberate practice (game days),
  and protect explicit slack to do it. ([lesson](lessons/07-third-way-learning.md))

## Risk and organizational dynamics

- **[phoenix-project/08] Managing technical debt as operational risk** - unpaid
  technical debt compounds like financial debt and shows up as unplanned
  (firefighting) work; prioritize paydown by blast radius and how poorly
  understood a system is, not just by how messy the code looks.
  ([lesson](lessons/08-technical-debt-operational-risk.md))
- **[phoenix-project/09] Changing relationships between Development, Ops, and
  business** - Dev, Ops, and the business are locked into locally rational but
  mutually damaging incentives (ship fast vs. stay stable vs. demand both); the
  fix is shared metrics, structural integration (embedding, shared on-call), and
  giving the business real visibility into IT's constraints.
  ([lesson](lessons/09-dev-ops-business-relationships.md))

## The strategic payoff

- **[phoenix-project/10] Turning IT into a competitive advantage capability** -
  where software materially shapes competitive outcomes, IT delivery and learning
  speed is a strategic capability to invest in, not a cost center to minimize;
  organizational learning velocity (how fast a company can test a hypothesis and
  learn from it) compounds into real competitive advantage.
  ([lesson](lessons/10-it-competitive-advantage.md))

## Focus areas (aggregated weak spots)

None yet - discussions have not started for this subject.
