---
id: evolutionary-architectures/08
subject: evolutionary-architectures
title: "Evolutionary Architecture Pitfalls and Antipatterns"
slug: pitfalls-antipatterns
status: drafted
mastery: 
seniority: staff
source: "Building Evolutionary Architectures, 2nd ed. (Ford, Parsons, Kua, Sadalage), Chapter 8"
prerequisites: [evolutionary-architectures/02, evolutionary-architectures/05, evolutionary-architectures/07]
created: 2026-08-10
updated: 2026-08-10
---

# Evolutionary Architecture Pitfalls and Antipatterns

## TL;DR
The book names recurring, specific failure modes teams hit when trying to build or
sustain evolutionary architecture: the **last 10% trap** (generic solutions get
disproportionately hard to finish), **inappropriate governance** (one-size-fits-all
standards applied across heterogeneous quanta), **resume-driven development** (adopting
tech for career capital rather than fit), **vendor lock-in as evolvability debt**, and
**treating fitness functions as a one-time setup** rather than a living practice. Each
one undermines evolvability in a different way, and each is common enough to be worth
recognizing by name before you're in the middle of it.

## The idea

### Why name antipatterns instead of just listing best practices?
Best-practice lists tell you what to do; antipatterns tell you what a *specific failure
looks like from the inside*, which is far more useful for recognition in the moment.
Most teams that fall into these traps aren't ignorant of best practices — they can recite
"keep services decoupled" or "automate your checks" — they fall in anyway because the
antipattern has a specific, seductive shape that best-practice advice doesn't warn you
about. Naming the shape is what lets you catch yourself (or a teammate, or a
tech-lead-level decision) mid-pattern instead of only recognizing it in a postmortem.

## How it works

### Antipattern 1: The last 10% trap
**Shape**: a team builds a generic, reusable solution — a platform, a shared library, an
internal framework meant to serve many future use cases — and the first 90% goes
smoothly: common cases are handled cleanly, the abstraction feels elegant. Then the last
10% (edge cases, the specific needs of the *next* consumer who doesn't fit the mold)
turns out to cost disproportionately more effort than the first 90% did, often more than
a purpose-built solution would have cost from scratch.

**Why it happens**: generic solutions are, by construction, built around the
*commonalities* across use cases. The last 10% is precisely the *differences* — and
differences don't compose or reuse the way commonalities do. Each new edge case often
requires bending the abstraction in a way that partially invalidates the simplicity that
made the first 90% cheap, and the cost compounds as more edge cases arrive.

**Worked example**: a platform team builds a generic "notification service" meant to
handle email, SMS, and push notifications for every product team in the company. The
first three consumers (simple transactional emails) integrate easily. The fourth
consumer needs region-specific SMS compliance rules (opt-out language varies by
jurisdiction); the fifth needs push notifications with rich media and platform-specific
payload quirks; the sixth needs guaranteed delivery ordering for a specific workflow.
Each of these "10%" requirements forces either a special case bolted onto the generic
service (eroding its simplicity) or a painful negotiation about what the platform will
and won't support — and the platform team, having sold the service as "the one
notification solution," is now the bottleneck for every edge case across the company.

**Connection to evolvability**: this directly undermines the last-responsible-moment
principle from `evolutionary-architectures/01` — building broad reusability *before* you
know the actual range of future needs is exactly the speculative-generality trap that
evolutionary architecture is supposed to replace with "build the capacity to change
cheaply, then build the specific thing when you actually need it."

### Antipattern 2: Inappropriate governance
**Shape**: architectural standards (a specific framework version, a specific logging
library, a specific code-style rule, a mandated deployment process) are applied
uniformly across every team and every quantum, regardless of whether that quantum's
context makes the standard appropriate.

**Why it happens**: uniform governance is organizationally easier to *communicate and
audit* than context-sensitive governance — "everyone uses Java 17 and this logging
library" is a one-line policy; "each team chooses what fits their quantum's needs,
subject to X constraints" requires actual judgment to enforce. Centralized architecture
or platform teams gravitate toward the simpler-to-audit uniform policy, especially at
scale, even when it's the wrong fit for a meaningful fraction of the org.

**Why it undermines evolvability**: recall from `evolutionary-architectures/05` that
different quanta can and should evolve independently, on their own timelines, according
to their own needs — that's the whole point of quantum boundaries. Inappropriate,
uniform governance re-couples quanta *organizationally* even after they've been
decoupled *technically*: a quantum that would benefit from adopting a new data store, or
skipping a company-wide framework migration because it doesn't apply to its workload,
can't, because governance treats "different" as "wrong" rather than asking whether the
difference is justified by the quantum's actual context.

**Worked example**: a company mandates that every service must use its central ORM and
relational database, "for consistency." A specific service handling real-time
leaderboard data would be far better served by an in-memory store with different
consistency guarantees — but governance blocks it, not because anyone evaluated the
trade-off for this specific quantum, but because the policy doesn't distinguish "this
quantum's needs are genuinely different" from "this team just wants to use something
new." The fix (covered further in `evolutionary-architectures/09`) is governance that
operates via fitness functions scoped and calibrated per quantum, not a single global
rule — appropriate governance asks "does this choice violate a characteristic we
actually care about for *this* quantum," not "does this choice match everyone else's."

### Antipattern 3: Resume-driven development
**Shape**: technology choices (a new framework, a trendy data store, a fashionable
architectural style) are driven by what looks good on an engineer's résumé or is
personally interesting to learn, rather than by fit for the problem and the system's
actual evolvability needs.

**Why it happens**: it's a genuine, understandable incentive — engineers' career growth
often does depend on breadth of technology exposure, and there's real tension between
individual career incentives and system-level architectural fitness. It's rarely
malicious; it's usually a rationalized version of "this new tool is actually better"
that's subtly inflated by the chooser's personal interest in learning it.

**Why it undermines evolvability**: every technology choice becomes part of the system's
future coupling and maintenance burden. A trendy but poorly-supported or poorly-understood
technology, adopted for excitement rather than fit, tends to accumulate exactly the kind
of undocumented, tribal-knowledge-dependent coupling that makes later change expensive —
the opposite of evolvability. It also frequently correlates with vendor lock-in
(Antipattern 4) when the trendy choice is a specific vendor's proprietary offering.

**How to recognize it in the moment**: ask "would we choose this if it weren't
personally interesting to the person proposing it?" and "what's the actual fitness
function this choice improves, versus how exciting it is to work with?" — a healthy
technology choice can usually name the specific characteristic it protects or improves;
a resume-driven one usually can't, beyond generic appeals to "modern" or "better."

### Antipattern 4: Vendor lock-in as evolvability debt
**Shape**: adopting a vendor's proprietary features, APIs, or data formats deeply enough
that switching away (or even upgrading independently of the vendor's roadmap) becomes
prohibitively expensive — not immediately visible as a problem, because lock-in
accumulates gradually, one convenient proprietary feature at a time.

**Why it happens**: vendor-specific features are often genuinely useful and save real
engineering time in the short term — the antipattern isn't "ever use a vendor feature,"
it's failing to recognize that each one is *architectural debt specifically against
evolvability*, taken on without being weighed as such.

**Why it undermines evolvability**: it's a direct violation of "guided, incremental
change across multiple dimensions" — a system locked into a specific vendor can no
longer evolve along whatever dimension that vendor doesn't support or chooses to
deprioritize. This is functionally identical to the shared-database coupling problem
from `evolutionary-architectures/06`, just at the vendor boundary instead of the
service boundary: your evolvability is capped by someone else's roadmap and pricing
decisions, and you often don't discover the true cost until you try to leave and find
migration effort measured in years, not weeks.

**Worked example**: a team adopts a cloud vendor's proprietary serverless orchestration
service because it ships a feature faster than the vendor-neutral alternative would
have. Eighteen months later, the vendor deprecates a key API the team depends on with six
months' notice, or the vendor's pricing model changes unfavorably at the company's now-
larger scale, or a security/compliance requirement mandates multi-cloud — and the team
discovers the "fast" original choice now requires a multi-quarter migration to unwind,
because the lock-in accumulated silently, one convenient feature at a time, with no
fitness function ever tracking "how much of our system now depends on vendor-specific
behavior we couldn't replace quickly."

### Antipattern 5: Fitness functions as a one-time setup
**Shape**: a team invests real effort building fitness functions early in a project —
the dependency-direction check, the performance budget, the security scan — and then
never revisits them as the system, the team, and the business context change.

**Why it happens**: writing fitness functions once, at project kickoff or during an
initial evolvability push, feels like "done" work — it's checked off a list, the CI
pipeline is green, and there's no obvious trigger reminding anyone to revisit thresholds
or coverage as the system evolves.

**Why it undermines evolvability**: it directly contradicts the definition of
evolutionary architecture from `evolutionary-architectures/01` — fitness functions are
supposed to *guide continuous* change, not be verified once and forgotten. Thresholds
calibrated for a system at one scale become meaningless (too strict or too lax) as the
system grows; new characteristics that matter now (a new compliance requirement, a
newly-critical performance path) go unprotected because nobody added a fitness function
for them after the initial push; old fitness functions protecting characteristics that
no longer matter keep consuming CI time and attention for no benefit — this is the exact
"stale temporal check" problem flagged in `evolutionary-architectures/03`, generalized
to the whole suite, not just individually temporal checks.

**The fix, previewed** (developed fully in `evolutionary-architectures/09`): fitness
functions need an *owner* and a *review cadence*, the same way a codebase needs ongoing
maintenance, not a one-time build. Treating them as living artifacts — added, removed,
and re-tuned as the system and its risks change — is what keeps "guided" actually guided
over the system's whole lifetime, not just at launch.

## Pros
- Naming these patterns gives teams a shared, specific vocabulary to recognize and push
  back on them mid-decision, rather than only in postmortems.
- Each antipattern has a distinct root cause and a distinct fix, which makes them
  individually actionable rather than a vague "be more disciplined" exhortation.
- Several of them (governance, fitness-function staleness) connect directly to the
  governance practice covered in `evolutionary-architectures/09`, giving a clear next
  step once recognized.

## Cons
- Naming antipatterns can tip into blame ("that's resume-driven development!") rather
  than constructive redirection if used carelessly in team dynamics — the point is
  recognition, not accusation.
- Some tension between antipatterns and legitimate trade-offs is genuinely hard to
  adjudicate in the moment — e.g., distinguishing "healthy exploration of a new
  technology" from "resume-driven development" requires judgment, not a bright line.
- Awareness of the antipatterns doesn't automatically prevent them under real
  organizational pressure (deadlines, incentive structures) — naming the trap doesn't
  remove the forces that lead teams into it.

## Alternatives
- **Generic "best practices" checklists without named failure modes** — differs by being
  prescriptive rather than diagnostic; useful for onboarding but less useful for
  in-the-moment recognition of a specific trap already being walked into.
- **Post-incident-only learning** — only formalize a "pitfall" after the organization has
  been burned by it directly. Differs by being reactive rather than anticipatory; the
  antipatterns in this lesson let a team recognize a trap *before* paying its cost, based
  on the accumulated experience of other organizations documented in the book.

## When to use it
- As a checklist to review architectural and technology decisions against, especially
  ones with long-term platform, governance, or vendor implications.
- When diagnosing why a previously evolvable system has become hard to change — these
  five patterns are a strong first set of hypotheses to check.

## When NOT to use it
- Don't use antipattern-naming as a blanket veto on generic platforms, governance
  standards, new technology adoption, or vendor services — each of those is sometimes the
  right call. The antipattern is the *unexamined, undiscussed* version of the choice, not
  the choice itself.

## Key takeaways / mental model
Each antipattern is a specific way that "guided, incremental change" quietly stops being
guided: the last 10% trap guides you toward premature generality; inappropriate
governance guides every quantum toward the same answer regardless of fit; resume-driven
development guides technology choices by excitement instead of characteristics; vendor
lock-in quietly hands the guidance to someone else's roadmap; and treating fitness
functions as one-time setup lets the guide go stale while everyone assumes it's still
watching. Recognizing the *shape* of each trap is what lets you catch it while the cost
is still small.

## Self-check questions
1. Explain the last 10% trap in your own words and connect it to the
   last-responsible-moment principle from `evolutionary-architectures/01`.
2. Why does inappropriate governance undermine the benefit of well-drawn quantum
   boundaries, even when the quanta themselves are technically well decoupled?
3. What distinguishes healthy adoption of new technology from resume-driven development?
   Is there a clean line, or is it a judgment call — and if so, what question would you
   ask to make the judgment call explicit?
4. Why is vendor lock-in described as "evolvability debt" specifically, rather than just
   "risk" in general?
5. Why does a green CI pipeline with passing fitness functions not guarantee the fitness
   functions are still doing their job?

## References
- *Building Evolutionary Architectures*, 2nd ed. (Ford, Parsons, Kua, Sadalage,
  O'Reilly 2022), Chapter 8: Putting It Into Practice (antipatterns and pitfalls)
- `evolutionary-architectures/01` (core definition), `/05` (coupling and quanta), `/09`
  (governance) — each antipattern here is a specific way one of those concepts breaks.
