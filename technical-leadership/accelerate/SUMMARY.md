# Accelerate - Subject Summary

A comprehensive recap of *Accelerate: The Science of Lean Software and DevOps* (Forsgren,
Humble, Kim), concept by concept.

**Progress note:** all 12 lessons are `drafted`; none have been discussed yet, so mastery
is pending across the board and no weak spots are recorded. This file will gain depth
(especially on the concepts the learner finds hard) as discussions happen - the
"Focus areas" section at the bottom will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom: the
evidence model and the four key metrics first, then the technical and cultural capability
drivers, then how to measure productivity honestly and lead a transformation that lasts.

## Evidence model and the four key metrics

- **[accelerate/01] Why software delivery performance is a strategic capability** - speed
  and stability move together, not against each other; six years of validated research
  shows high delivery performance predicts higher profitability, market share, and
  productivity. ([lesson](lessons/01-delivery-performance-as-capability.md))
- **[accelerate/02] The DORA model and validated research approach** - how the research
  used validated psychometric scales and structural equation modeling to test causal
  direction, not just correlation, across multiple replicated survey years.
  ([lesson](lessons/02-dora-model-and-research.md))
- **[accelerate/03] Deployment frequency and lead time for changes** - the two throughput
  metrics, both proxies for batch size; small batches are the mechanism behind faster,
  safer delivery. ([lesson](lessons/03-deployment-frequency-and-lead-time.md))
- **[accelerate/04] Change failure rate and time to restore service** - the two stability
  metrics that prevent throughput from being gamed; elite performers score well on all
  four metrics at once, refuting the speed-vs-stability trade-off.
  ([lesson](lessons/04-change-failure-and-restore-time.md))

## Technical and cultural capability drivers

- **[accelerate/05] Continuous delivery foundations and small-batch flow** - keeping the
  codebase always release-ready via automated testing, trunk-based development, and
  deployment automation is the strongest single predictor of the four key metrics.
  ([lesson](lessons/05-continuous-delivery-foundations.md))
- **[accelerate/06] Architecture for flow: loosely coupled teams and systems** - the
  architectural property that matters is independent deployability, not a specific style
  like microservices; ties directly to Conway's Law and team boundaries.
  ([lesson](lessons/06-architecture-for-flow.md))
- **[accelerate/07] Test automation and build quality as throughput constraints** -
  developer-owned, fast, trusted tests (not raw coverage percentage) are what let teams
  ship on a green build with no manual regression gate.
  ([lesson](lessons/07-test-automation-and-build-quality.md))
- **[accelerate/08] Security as an integrated delivery practice** - shifting security left
  (design-time threat modeling, self-service automated scanning) improves both lead time
  and security outcomes versus a late centralized review gate.
  ([lesson](lessons/08-integrated-security-practice.md))
- **[accelerate/09] Lean management and generative culture** - Westrum's generative
  culture and lean practices (WIP limits, lightweight peer review over heavyweight change
  boards) independently predict performance, on top of technical practices.
  ([lesson](lessons/09-lean-management-and-culture.md))

## Measurement, transformation, and sustaining performance

- **[accelerate/10] Measuring productivity without vanity metrics** - lines of code,
  commits, hours, and velocity are gameable activity metrics; measure outcomes (the four
  key metrics) plus deployment pain and burnout as leading indicators instead.
  ([lesson](lessons/10-measuring-productivity.md))
- **[accelerate/11] Leading transformation using capability-based interventions** - reject
  universal maturity-model staircases in favor of diagnosing your own bottleneck among
  ~24 independent capabilities; transformational leadership amplifies technical
  investment. ([lesson](lessons/11-leading-transformation.md))
- **[accelerate/12] Sustaining high performance and preventing local optimization** -
  elite performance erodes without continued investment; watch for burnout and for teams
  improving local metrics at the system's expense.
  ([lesson](lessons/12-sustaining-high-performance.md))

## Focus areas (aggregated weak spots)

None yet - discussions have not started for this subject.
