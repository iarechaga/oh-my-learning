# Fast-Moving Domain Policy

Load this file before authoring, reviewing, or maintaining any lesson in
`agentic-engineering/` - today the only domain this applies to - or before deciding
whether a new domain needs the same treatment. It defines how a domain copes with a
subject matter that has no settled literature and changes faster than the repo's
normal maintenance rhythm, without weakening the stability guarantees the rest of the
repository relies on.

This is a domain-scoped policy, not a repo-wide one. The other eight domains draw from
settled literature and need none of this.

---

## Why this exists

Every other domain anchors each subject to one canonical, stable book. `agentic-engineering`
cannot: there is no consolidated book on working with LLM agents, and the field moves on
a timescale of months (new products, revised protocol specs, new orchestration
patterns), not years. Refusing to teach it until it "settles" is not an option the
maintainer chose - the instability is accepted as a fact of the field, not a reason to
wait. What needs deliberate design is how the domain coexists with that instability
without silently rotting or destabilizing the rest of the repo.

## Durable vs. perishable

Every concept in this domain is one or the other. The distinction is about **what the
claim depends on**, not how deep or advanced it is:

- **Durable** - true regardless of which specific product, API, or framework exists
  today. Architecture, mechanisms, trade-offs, and failure modes: *why* context
  poisoning happens, *why* an agent can't reliably separate instruction from data,
  *why* parallel tool calls cut latency, *why* a trigger description can over-fire.
  These are cross-vendor patterns that would still be true if every product named in
  an example lesson disappeared tomorrow.
- **Perishable** - tied to a specific product, benchmark, price, spec version, or file
  format that will change. Not lesser content - often the most immediately useful - but
  content whose *correctness has an expiration date* by construction.

**Where each lives:**

- Eight subjects in this domain are durable end to end. Named products may appear
  inside any of their lessons as **boxed-off, swappable examples** - never as the
  concept's title or defining identity. If a lesson cannot be explained without naming
  a specific product still existing or working the way it does today, that lesson
  belongs in the ninth subject, not here. This is a hard authoring rule, not a
  suggestion.
- One subject, `agentic-engineering/landscape-snapshot`, is perishable by design: a
  dated survey of the concrete products/frameworks/protocols/benchmarks/pricing/file
  formats that exemplify the durable subjects' concepts. Every durable subject's
  `README.md` points to the specific `landscape-snapshot` lesson that carries its
  current examples, so a durable lesson never has to choose between staying accurate
  and staying useful.

This isolates the maintenance burden: eight subjects need correction only when an
architectural claim turns out to be wrong (rare), and one subject needs scheduled,
routine refreshing (expected, indefinitely).

## Front matter: `durability` and `next_review`

Two fields, used only in `agentic-engineering/` lessons (absent elsewhere; YAML front
matter with extra keys is harmless to the site generator and catalog script, which
only read the fields they know about - no schema change to the other 609 lessons, and
no MAJOR-triggering "restructuring the front-matter schema" under
[release-policy.md](release-policy.md)):

```yaml
durability: durable | perishable
next_review: YYYY-MM     # required when durability: perishable; omit for durable
```

- `durability: durable` - the default for eight of the nine subjects. No forced review
  cadence; corrected opportunistically like any other lesson in the repository, under
  the normal PATCH rules.
- `durability: perishable` - used in `landscape-snapshot` (and lesson `07` of that
  subject is the one exception, tagged `durable`, since "how to track what changed" is
  itself durable methodology despite living in the perishable subject).
- `next_review` is set **when the lesson is authored**, not before - a scaffolded
  concept with no lesson body yet has nothing to review. Set it to the lesson's
  `created` date plus one quarter.

## Making staleness visible without rereading

Each subject's `README.md` concept table is the source of truth for this, not the
lesson bodies:

- The eight durable subjects state once, in prose above their table, that every
  concept is durable - no per-row noise.
- `landscape-snapshot/README.md` carries two extra table columns beyond the repo's
  standard format: **Durability** and **Next review**. Any row with a `Next review`
  date in the past is stale - full stop. That is the whole check: read one table, not
  seven lessons.

## Maintenance cadence

- **Durable subjects (all but `landscape-snapshot`):** no forced cadence. Fixed like
  any other lesson, when a correction is needed.
- **`landscape-snapshot`:** reviewed **quarterly**, mandatory. A review is one of two
  outcomes per lesson:
  1. **Still accurate** - bump `next_review` by one quarter and `updated`; no content
     rewrite. This is meant to be a cheap pass most of the time.
  2. **Changed** - rewrite the affected part; normal PATCH (or MINOR, if the landscape
     genuinely gained a new category of thing, not just a new entrant in an existing
     one).
- **Trigger so this doesn't get forgotten:** [release-policy.md](release-policy.md)'s
  release-cutting workflow includes a step to scan `landscape-snapshot/README.md` for
  rows past their `next_review` date and flag them to the human before finalizing any
  release - piggybacking on a step that already exists rather than adding new tooling.

## What this implies for versioning

No new SemVer category is needed. A `landscape-snapshot` refresh is a normal PATCH (or
MINOR, per the existing rules in [release-policy.md](release-policy.md)) - the concept
ID never changes, only the body content, so it never touches the ID/structure-stability
promise the `1.0.0` release made.

What *is* different is **cadence and volume, not semantics**: this domain will produce
PATCH-sized changelog entries indefinitely, on a quarterly rhythm, while the other
eight domains receive them rarely and then go quiet. That asymmetry is expected, not a
sign of drift. To keep it from cluttering `CHANGELOG.md` for a reader who doesn't care
about this domain, group each refresh under one recognizable, skippable bullet:

```
### Fixed
- Landscape refresh: agentic-engineering, Q3 2026 - updated coding-agent-products-today,
  model-capability-tiers-and-pricing-today.
```

## Workflow V - Currency review

Trigger: the human asks whether this domain (or a subject/lesson in it) is still
current - e.g. *"check whether `agentic-engineering` still holds up"*, *"is
`landscape-snapshot` out of date?"*, *"audit the agentic-engineering domain"*,
*"find out if there's anything new in the field this domain should cover"* - in any
language the human happens to be using; the trigger is the intent, not the exact
wording. This is a different action from the quarterly
`landscape-snapshot` maintenance cadence above (which is a scheduled push); this is a
learner- or maintainer-triggered pull, on demand, and it always ends in an explicit
verdict, never a hedge.

**Scope, cheapest check first:**

1. **Triage from front matter alone - no web research yet.** Read every lesson's
   `durability`/`next_review` in the requested scope (whole domain, one subject, or one
   lesson). Any `perishable` lesson with `next_review` in the past is automatically
   in scope for full verification. `durable` lessons are only verified if the human
   asked for a full audit, or if gap detection (below) surfaces something that might
   invalidate one.
2. **Deep-verify `landscape-snapshot` in full** whenever the domain or that subject is
   in scope - it is cheap (7 lessons) and is precisely the subject this workflow exists
   to check.
3. **Spot-check the eight durable subjects lightly** when a full-domain audit is
   requested: the question for a durable lesson is *"has anything happened that
   invalidates the concept," not "is every boxed example still current"* - boxed
   examples are expected to age and are not what durability claims to protect.

**Verification - real sources, not recall.** For every lesson in scope, re-derive its
specific factual claims (named products, protocol/benchmark status, prices, file
formats, or - for durable lessons - the architectural claim itself) and check each one
against a live web search or fetch. This is exactly the domain where the agent's own
training data is guaranteed to be stale - never assess currency from memory. Cite what
you checked, the same way lesson `source:` fields do.

**Verdict - exactly one of three per lesson, stated explicitly, no softer alternative:**

- **Current** - the lesson's claims still hold (durable lessons: the concept is
  architecturally unchanged; perishable lessons: the named products/numbers/status
  still match, or differ only in inconsequential ways - e.g. a price moved 10%, a
  version number ticked up with no capability change).
- **Outdated** - specific facts have measurably changed (a new tier, a renamed or
  merged product, a superseded benchmark, a spec revision) such that a reader would be
  misled, but the lesson's structure and durable teaching are still sound - it needs an
  edit, not a rewrite.
- **Obsolete** - the concept itself no longer applies as described (a protocol fully
  deprecated and replaced, an execution model that no longer exists, a durable claim
  that turned out to be wrong) - it needs a rewrite, not a patch.
- **Unable to determine** - only when the above three genuinely cannot be assigned
  (no reliable current source found, or sources conflict badly enough that neither
  side can be trusted). State this explicitly, name what you searched for, and why it
  didn't resolve - never default to "current" because verification was inconclusive.

**Gap detection - separate from verifying what exists.** Independently research what
has emerged in the field (new products, protocols, benchmarks, or genuinely new
capability categories) that no existing lesson covers. For each finding, propose where
it belongs: a new `landscape-snapshot` entry (a new instance of an existing durable
concept), a new lesson in an existing durable subject (a genuinely new *durable*
concept, not just a new product), or - rarely - a new subject, if nothing existing
fits. Proposals only; this workflow never mass-authors on its own, same as Workflow A.

**Report - the actionable output:**

- A per-lesson verdict table (ID, verdict, one-line reason, what was checked).
- An ordered action list grouped by verdict: Obsolete (rewrite) first, Outdated
  (edit) next, Unable to determine (needs a human or a deeper follow-up) after that,
  Current (no action) last.
- Gap-detection proposals, each with a suggested location and a one-line reason.
- **`next_review` updates** - bump to `created`/today plus one quarter *only* for
  lessons verdicted Current. Leave `next_review` untouched (still overdue and visibly
  stale) for Outdated, Obsolete, and Unable-to-determine lessons until someone actually
  fixes the content - never launder staleness by bumping the date without fixing what's
  wrong.

This workflow **reports and updates `next_review`; it does not rewrite lesson bodies**
unless the human then asks for that as a follow-up (an ordinary authoring/edit pass
under the usual PATCH/MINOR rules).

**Future extension, noted but not implemented:** the other eight domains age too, just
on a different timescale (a book's ideas rarely invalidate, but a citation, a tool
mentioned in passing, or an industry statistic can still go stale). A lighter version
of this workflow - verdict-based, source-checked, but without the durability/
`next_review` machinery those domains don't have - could generalize here eventually.
Not built now; flagged so it isn't rediscovered as if novel.

## A known gap this does not fix

`PROGRESS.md`'s `mastery` field (see [progress-tracking.md](progress-tracking.md)) has
no way to express "this was `solid` when discussed, but the underlying content has
since gone stale." A learner who mastered `landscape-snapshot/05` a year ago has no
signal telling them to re-verify it, even though `next_review` on the lesson itself
says it should be revisited. This is a real, currently-unfilled gap between this
domain's freshness model and the progress-tracking system - noted here deliberately so
it isn't rediscovered by surprise. The natural fix (Workflow P surfacing "marked
`solid`, but `next_review` has passed" alongside the normal Focus areas) is not
implemented as part of this policy; it is future work if this domain's use in practice
shows it is needed.

## Non-negotiables

- Never let a durable lesson's title, definition, or "How it works" section depend on
  a specific product still existing. If it can't be written without naming one, it
  belongs in `landscape-snapshot`.
- Never author a `landscape-snapshot` lesson without setting `durability: perishable`
  and a `next_review` date (except lesson `07`, which is durable).
- Never skip a quarterly `landscape-snapshot` review because "nothing seemed to
  change" - confirm it explicitly (bump `next_review`) rather than letting the date
  quietly lapse.
- Never treat a `landscape-snapshot` rewrite as requiring anything beyond a normal
  PATCH/MINOR release - this policy does not introduce new version semantics.
