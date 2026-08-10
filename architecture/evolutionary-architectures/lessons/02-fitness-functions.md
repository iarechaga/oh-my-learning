---
id: evolutionary-architectures/02
subject: evolutionary-architectures
title: "Fitness Functions"
slug: fitness-functions
status: drafted
mastery: 
seniority: senior
source: "Building Evolutionary Architectures, 2nd ed. (Ford, Parsons, Kua, Sadalage), Chapter 2"
prerequisites: [evolutionary-architectures/01, fundamentals/03]
created: 2026-08-10
updated: 2026-08-10
---

# Fitness Functions

## TL;DR
An **architectural fitness function** is any mechanism that provides an objective,
automatable integrity check for one or more architectural characteristics. It's the
concrete implementation of "guided" in the definition of evolutionary architecture: a
test, script, or monitor that verifies a characteristic (e.g., "no cyclic dependencies,"
"p99 latency < 200ms," "no critical CVEs in dependencies") still holds, and fails loudly
when it doesn't.

## The idea

### The problem: architectural intent decays silently
Unit tests protect *functional* behavior — if you break a feature, a test usually turns
red. But most codebases have no equivalent protection for *architectural* behavior. You
can have 100% passing unit tests and still have silently:
- introduced a circular dependency between two modules that were supposed to stay
  decoupled,
- let response time creep from 80ms to 400ms over six months of small, individually
  "fine" changes,
- allowed a service to start calling another service's database directly, bypassing its
  API,
- shipped a dependency with a known critical vulnerability.

Nobody *decided* to do these things. They accumulated because there was no automated
signal telling anyone it was happening — architectural decisions, once made, are
usually written down in a document or a diagram and then never checked again. The
document doesn't fail a build. Reality drifts from intent, and by the time someone
notices (usually during an incident, or when a "simple" feature turns out to require a
six-week refactor because coupling has metastasized), it's expensive to fix.

### The idea: borrow "fitness function" from genetic algorithms
In a genetic algorithm, a **fitness function** scores each candidate solution in a
population against the goal you're optimizing for; solutions that score well survive
into the next generation, solutions that score poorly are discarded. The book borrows
this vocabulary deliberately: an *architectural* fitness function does the same job for
architecture decisions. Each change to the system is a "candidate," and the fitness
function is the automated judge that decides whether that candidate preserves the
characteristics you care about.

The key properties a good fitness function needs, mirroring the analogy:
- **Objective** — a pass/fail (or numeric threshold) that doesn't depend on human
  judgment at evaluation time. "Feels maintainable" is not a fitness function; "cyclomatic
  complexity per method ≤ 10" is.
- **Automatable** — it should run without a human manually re-deriving the answer each
  time. Even fitness functions that require a human step (e.g., a security review) should
  be *triggered* and *tracked* automatically, with the manual part as small as possible.
- **Tied to a specific architectural characteristic** — a fitness function without a
  named characteristic it's protecting is just a vague quality gate. Always be able to
  answer "what is this checking, and why do we care?"

### It's a superset of tests, not a rename of tests
It's tempting to think "fitness function = fancy word for test," but the book is
explicit that fitness functions are a **broader category** that includes:
- Unit/integration tests that assert structural properties (e.g., ArchUnit-style rules
  in Java, dependency-cruiser rules in JS).
- Monitors that run continuously in production (e.g., an APM alert on p99 latency).
- Manual processes with a defined cadence and owner (e.g., a quarterly architecture
  review, a security audit) — less automatable but still fitness functions if they
  gate a decision objectively.
- Chaos-engineering experiments (does the system survive a dependency failing?).
- Metrics dashboards paired with an explicit threshold and an escalation policy.

The unifying idea isn't "it's a unit test"; it's "it's *any* mechanism that objectively
verifies an architectural characteristic, and it runs often enough to catch drift before
it's expensive to fix."

## How it works

### Anatomy of a fitness function
Every fitness function has:
1. **A characteristic it protects** (from the multi-dimensional list: performance,
   security, modularity, scalability, data integrity, deployability...).
2. **A verification mechanism** (a script, a test assertion, a monitoring rule, a
   scheduled review).
3. **A trigger** (when does it run — every commit? every deploy? nightly? on a schedule
   independent of deploys?).
4. **A pass/fail or threshold criterion** (this is what makes it *objective* rather than
   a discussion).
5. **A consequence when it fails** (block the build, page someone, flag for review — a
   fitness function with no consequence is just a metric nobody acts on).

### Worked example 1: dependency-direction check (structural/modularity)
Suppose you have a modular monolith with a `domain` layer that must never depend on the
`infrastructure` layer (to keep business logic testable and swappable). A fitness
function using a tool like ArchUnit (Java) or `dependency-cruiser` (JS/TS):

```
rule: no-domain-to-infra-dependency
  given: classes residing in package "..domain.."
  should: never depend on classes residing in package "..infrastructure.."
```

- Characteristic protected: modularity / layering.
- Mechanism: static analysis of import/dependency graph.
- Trigger: every CI build, on every pull request.
- Criterion: zero violations.
- Consequence: build fails, PR cannot merge.

This catches the very common failure mode where a developer, under deadline pressure,
adds a "quick" direct call from a domain class to a database client living in
`infrastructure`, because it's the fastest way to get a feature working today. Without
the fitness function, this passes code review only if the reviewer happens to notice —
and reviewers miss things under the same time pressure. With it, the build simply won't
let the violation merge.

### Worked example 2: performance budget as a CI gate
A team commits to "the checkout API must respond in under 300ms at p95 under a load of
500 req/s." As a fitness function:

- Mechanism: a load test (e.g., k6 or Gatling script) that runs against a staging
  deployment as part of the pipeline, asserting `p95 < 300ms` at the specified load.
- Trigger: on every merge to the release branch (not necessarily every commit — load
  tests are expensive, so triggering less frequently than a unit test is a legitimate
  design choice, discussed further in `evolutionary-architectures/03`).
- Criterion: p95 latency measurement compared to a hard threshold; also worth tracking
  the trend (is it 250ms and rising, or 250ms stable?) rather than only pass/fail.
- Consequence: pipeline stops before production deploy; team is notified with the
  measured value and the trend.

This converts "we should keep checkout fast" — a value everyone nods at in a planning
meeting and nobody enforces — into a hard, continuously re-verified gate. It also
catches the classic death-by-a-thousand-cuts failure: no single commit added enough
latency to matter, but ten commits over a month each added 5-10ms, and the aggregate
crossed the threshold. A one-time performance review at project kickoff would never
catch this; a continuously re-run fitness function does, by construction.

### Worked example 3: a security-scan gate
- Mechanism: a dependency vulnerability scanner (e.g., Snyk, Dependabot alerts,
  `npm audit`) run as a pipeline step.
- Trigger: every build, plus a scheduled nightly scan (because new CVEs are published
  against dependencies you didn't change — the threat model changes even when your code
  doesn't).
- Criterion: zero dependencies with a "critical" severity vulnerability (a threshold —
  "zero critical" rather than "zero of any severity," which would be unworkable in
  practice given how noisy low-severity findings are).
- Consequence: build fails on critical findings; lower-severity findings are logged and
  tracked but don't block, to avoid the team habitually overriding an over-strict gate
  (a real failure mode — see "governance as a living practice" in
  `evolutionary-architectures/08` and `/09`).

This is a good example of a fitness function whose trigger is deliberately *not* purely
commit-driven: the codebase can be unchanged and still go from "fit" to "unfit" because
the outside world (the CVE database) changed. Fitness functions must account for that —
purely triggered, commit-based checks miss this class of regression entirely (this
distinction is developed fully in `evolutionary-architectures/03`).

### Why "objective" matters more than it sounds
A common mistake is writing a fitness function around a subjective judgment disguised as
a metric — e.g., "code readability score" from an opaque linter heuristic that nobody
trusts and everybody routes around. If engineers don't believe the fitness function is
measuring something real, they'll treat a failure as noise to suppress rather than a
signal to act on, and the fitness function becomes theater. The discipline of choosing
fitness functions is as much about picking things worth automating and that the team
will *respect* as it is about the automation itself.

## Pros
- Converts tacit architectural knowledge (in an architect's head, or a stale wiki page)
  into an explicit, continuously verified contract.
- Catches slow architectural drift ("boiling frog" regressions) that no single code
  review would flag.
- Gives architects a way to delegate enforcement of a decision instead of manually
  policing every PR forever.
- Makes architecture decisions falsifiable and debatable in concrete terms ("this
  threshold is wrong" is a productive conversation; "this feels off" is not).

## Cons
- Writing and maintaining good fitness functions is real engineering work, easy to
  underinvest in under delivery pressure.
- A badly chosen threshold (too strict or too lax) either creates constant false-alarm
  fatigue or provides false confidence.
- Overhead: expensive fitness functions (load tests, chaos experiments) can slow down
  pipelines if not triggered thoughtfully (see `evolutionary-architectures/03` on
  triggered vs. continual).
- Risk of "fitness function theater" — writing them once at project kickoff and never
  revisiting them as the architecture and requirements change (a named antipattern; see
  `evolutionary-architectures/08`).

## Alternatives
- **Architecture Decision Records (ADRs) alone** — document the decision and rationale,
  but rely on humans to remember and enforce it. Differs by having no automated
  enforcement; useful as a *complement* to fitness functions (the ADR explains *why*,
  the fitness function enforces *that*), not a substitute.
- **Periodic manual architecture review** — a senior architect or review board inspects
  the codebase on a cadence (quarterly, at major releases). Differs by having much lower
  frequency and higher latency between drift occurring and being caught; still a valid
  fitness function *if* it's scheduled, objective, and has consequences — just a weaker
  one than continuous automated checks.
- **Pure code review discipline** — rely on reviewers to catch architectural violations
  by eye on every PR. Differs by depending entirely on human attention and consistency,
  which degrades under time pressure, team turnover, and codebase growth; doesn't scale
  the way an automated check does.

## When to use it
- Any characteristic you've identified as important enough to protect (from
  `fundamentals/03`'s prioritized characteristics list) should get at least one fitness
  function — that's the whole point of prioritizing characteristics in the first place.
- Especially valuable for characteristics that degrade silently and gradually
  (coupling, performance, security posture) rather than ones that break loudly and
  immediately (a fitness function for "does the app crash on startup" is redundant with
  the fact that you'd notice immediately).

## When NOT to use it
- Don't build a fitness function for a characteristic nobody has actually prioritized —
  it's wasted engineering effort and adds noise/maintenance burden without protecting
  anything that matters to this system.
- Don't automate a check whose criterion can't be made genuinely objective — a fuzzy
  fitness function that requires human interpretation every time it "fails" isn't
  saving anyone judgment time; it's just adding a step.
- Avoid retrofitting fitness functions onto characteristics that are already so far
  degraded that the "check" would fail on every single build with no realistic near-term
  fix — that just trains the team to ignore failures. Fix the worst violations first,
  then add the gate (see `evolutionary-architectures/07` on prioritizing retrofits).

## Key takeaways / mental model
A fitness function is a unit test for your architecture, generalized: it doesn't have to
be a unit test, but it has to be objective, automatable (even if the automation just
triggers a scheduled human step), tied to a named characteristic, and consequential when
it fails. If "guided" is what separates evolutionary architecture from undirected
change, fitness functions are the literal implementation of "guided." When you catch
yourself saying "we should really keep an eye on X," ask: could this be a fitness
function instead of a hope?

## Self-check questions
1. What three properties make something a fitness function rather than just a metric or
   a test?
2. Why is "code readability score" from a fuzzy linter a weaker fitness function
   candidate than "p95 latency under 300ms," even though both produce a number?
3. Design a fitness function (characteristic, mechanism, trigger, criterion,
   consequence) for a characteristic from your own current project.
4. Why can a fitness function fail even when no code has changed? Give a concrete
   example.
5. What's the risk of writing fitness functions once at project kickoff and never
   revisiting them?

## References
- *Building Evolutionary Architectures*, 2nd ed. (Ford, Parsons, Kua, Sadalage,
  O'Reilly 2022), Chapter 2: Fitness Functions
- `fundamentals/03` (architectural characteristics) — fitness functions are how you
  protect the characteristics prioritized there.
