---
id: pragmatic-programmer/03
subject: pragmatic-programmer
title: DRY and the Evils of Duplication
slug: dry-duplication
status: drafted
mastery:
seniority: junior
source: The Pragmatic Programmer (20th Anniversary ed., Hunt & Thomas), Chapter 2
prerequisites: [pragmatic-programmer/01]
created: 2026-08-10
updated: 2026-08-10
---

# DRY and the Evils of Duplication

## TL;DR
DRY ("Don't Repeat Yourself") says every piece of knowledge in a system should have a single, authoritative representation. This is not "don't copy-paste code" — it's "don't let the same *fact* about the system exist in two places that can silently drift apart."

## The idea
Copy-pasted code is the visible symptom, but the actual disease DRY targets is **duplicated knowledge**: two or more places in the system that encode the same truth about the business, the data, or the behavior. The danger isn't the extra characters typed — it's that when the truth changes, you now have two (or more) places to remember to update, and you *will* eventually update one and miss the other. That's the moment DRY violations turn from stylistic nitpick into production bug.

The book's running example: a payroll calculation that appears once in the billing module and once, subtly reimplemented, in the reporting module. Someone fixes a tax-rounding bug in billing. Reporting silently keeps producing wrong numbers for months because nobody remembered it had its own copy of the same rule.

## How it works

### DRY is about knowledge, not text
Two lines of identical-looking code are not automatically a DRY violation, and two lines of *different-looking* code can be. The test is: **do these two pieces of code represent the same underlying fact, such that if the fact changes, both must change together?**

- Not a DRY violation: two functions that both happen to contain `x + 1` for unrelated reasons (one computes an array's next index, one computes a retry count). Identical text, unrelated knowledge — changing one has no bearing on the other.
- A DRY violation even without copy-paste: a `MAX_RETRIES = 3` constant in the client's retry loop, and a hardcoded `3` buried in a log message on the server that says "gave up after 3 attempts." Different text, same knowledge — if you bump retries to 5, the log message quietly starts lying.

### The four faces of duplication the book distinguishes
1. **Imposed duplication** — the environment forces it (e.g., a schema defined once in the DB, and again in application code because the ORM needs it). Mitigate with code generation from a single source of truth.
2. **Inadvertent duplication** — developers don't realize two things are the same fact until later (e.g., two "unrelated" validation rules that turn out to both encode "an order must have at least one line item"). Mitigate by naming and centralizing the concept once discovered.
3. **Impatient duplication** — copy-paste because it's faster right now. Mitigate with slightly more upfront design discipline; the interest rate on this debt is high.
4. **Interdeveloper duplication** — two people/teams independently build the same thing because they don't know the other exists. Mitigate with team-wide visibility into what already exists (shared libraries, internal component catalogs, code search).

### Worked example: imposed vs. impatient duplication
A team stores a user's `country_code` in Postgres as a 2-letter ISO code. The frontend needs a list of valid country codes for a dropdown.
- **Impatient duplication** (avoidable): frontend hardcodes an array of 195 country codes in a `.js` file. When the backend adds a new supported country, the frontend silently doesn't offer it, and nobody notices until a support ticket. Fix: expose a `/api/countries` endpoint backed by the single DB-defined list; frontend fetches it.
- **Imposed duplication** (harder to avoid): the DB schema needs a `CHECK` constraint listing valid codes, and the app layer also validates for a fast error message before hitting the DB. Fully removing this duplication may not be practical — but you can generate the app-layer validator from the same source list the DB constraint uses (a single YAML/JSON of country codes, consumed by both a migration script and application code), so there's still one canonical source even though it materializes in two places.

### The single-source-of-truth pattern
The general fix pattern DRY pushes you toward: identify the one true "owner" of a fact, and make every other place *derive from* it (via import, code generation, config, or a shared service) rather than *restate* it. If you can't cleanly designate one owner, that's a signal the concept itself needs to be modeled explicitly (often as its own class, config value, or service) rather than left implicit and scattered.

## Pros
- A change to a business rule requires exactly one edit, eliminating an entire class of "forgot to update the other copy" bugs.
- Makes the codebase's true complexity visible — duplicated logic hides how much surface area a concept actually has.
- Encourages naming things ("this hardcoded `3` is actually `MAX_RETRIES`"), which improves readability as a side effect.

## Cons
- Over-applying DRY to *coincidentally* similar code creates false, brittle couplings — two unrelated features end up sharing a helper function that then must satisfy both, and a change for one breaks the other.
- Chasing DRY across module or service boundaries can introduce tight coupling that's worse than the duplication it removed (a shared library used by both a fast-changing frontend and a stable backend now forces both to move in lockstep).
- Abstracting too early, before a second real occurrence of the same knowledge is confirmed, produces a wrong abstraction that's harder to undo than the original duplication.

## Alternatives
- **WET code ("write everything twice") as a deliberate policy** in fast-moving prototype/exploration phases, with an explicit plan to DRY-up once the abstraction becomes clear — appropriate when the shape of the knowledge is still unknown.
- **Rule of Three** — a pragmatic threshold some teams use: tolerate duplication on the first repeat, but factor it out on the third occurrence, since by then the pattern is proven rather than guessed. Reduces the "false abstraction from premature DRY" failure mode.
- **Cross-cutting duplication tools** (codegen, schema-first API contracts, shared type packages) — solve *imposed* duplication structurally rather than relying on developer discipline.

## When to use it
Whenever you notice the same business rule, magic number, validation, or algorithm expressed in two places — especially across layers (frontend/backend), services, or file boundaries where it's easy to lose track. Prioritize DRY-ing knowledge that changes (tax rates, thresholds, business rules) over knowledge that's structurally frozen.

## When NOT to use it
Don't DRY two pieces of code just because they look similar today if they represent genuinely different concepts that happen to coincide (see the "same text, unrelated knowledge" example above) — that's *accidental* duplication, and merging it manufactures a false coupling. Also hold off on abstracting a single occurrence "in case it repeats" — wait for genuine repetition (see Rule of Three) unless you already know the domain well enough to be confident.

## Key takeaways / mental model
Before merging two similar-looking blocks, ask: "if the business changes this rule tomorrow, do both blocks need to change together?" If yes, DRY it. If no — even if the code looks identical — leave them separate; they're not the same knowledge, they're just currently the same text.

## Self-check questions
1. Explain, in your own words, why DRY is about knowledge and not about lines of text.
2. Give an example from a system you know of "inadvertent duplication" — two rules that turned out to be the same fact, discovered only later.
3. A junior teammate merges two functions into one shared helper because they're currently identical. What question would you ask them to check whether this is a genuine DRY fix or a false abstraction?
4. Why might removing duplication across two microservices owned by different teams sometimes make the overall system *worse*, not better?

## References
- The Pragmatic Programmer, 20th Anniversary Edition (David Thomas & Andrew Hunt), Chapter 2: "A Pragmatic Approach" (DRY section).
