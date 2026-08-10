---
id: philosophy-of-software-design/03
subject: philosophy-of-software-design
title: Modules Should Be Deep
slug: deep-modules
status: drafted
mastery:
seniority: senior
source: A Philosophy of Software Design, 2nd ed. (John Ousterhout), Chapter 4
prerequisites: [philosophy-of-software-design/01, clean-code/03]
created: 2026-08-10
updated: 2026-08-10
---

# Modules Should Be Deep

## TL;DR
A module's value is the ratio of its functionality to its interface: a "deep" module provides substantial functionality behind a small, simple interface (high value); a "shallow" module has an interface that's nearly as complicated as its own implementation (low value, since it barely reduces the cognitive load of using it). Ousterhout's most provocative, deliberately anti-Clean-Code claim follows directly from this: bigger functions/modules are often *better*, specifically because splitting a function can shallow it.

## The idea
This is the chapter where the subject's README's promised "productive counterpoint to Clean Code" becomes most concrete and most contentious. `clean-code/03` argued functions should be small because smaller units are individually easier to understand. Ousterhout's depth framework agrees that *interfaces* should be simple, but explicitly disputes that smaller modules automatically produce simpler interfaces — and argues that reflexively decomposing a module into many small pieces can make the *overall system* harder to understand, even though each individual piece looks simpler in isolation, because the total interface complexity (summed and multiplied across all the newly-created seams between pieces) can exceed what one, larger, well-designed module's single interface would have required.

**The depth metric, precisely:** a module's interface consists of everything a user of that module must know to use it (its API signature, but also any behavioral assumptions, side effects, or ordering requirements it doesn't fully encapsulate). A module is "deep" when its interface is *much* simpler than its implementation — the interface hides a lot of complexity, delivering a lot of value per unit of interface complexity a caller must learn. A module is "shallow" when its interface is roughly as complex as (or nearly indistinguishable in complexity from) its implementation — it doesn't hide much, so it doesn't earn back much value for the cost of it existing as a separate module at all.

## How it works

### The canonical deep-module example: Unix file I/O
The book's own touchstone example: the Unix `open`/`read`/`write`/`close` interface is famously simple — five or six basic calls — while the implementation underneath (disk scheduling, caching, buffering, file-system-specific storage layouts, permissions, concurrent access) is enormously complex. Nearly every application programmer who has ever called `open()` has never needed to know any of that implementation complexity — the interface is a small, stable "window" onto an enormous amount of hidden functionality, which is precisely what makes it a deep module and precisely why it's remained essentially unchanged and universally usable for decades.

### The shallow-module counter-example, and its cost
```
class DataValidator:
    def check_not_null(self, value): return value is not None
    def check_is_string(self, value): return isinstance(value, str)
    def check_length(self, value, max_len): return len(value) <= max_len
```
Each individual method here is trivially simple to read (`clean-code/03` would approve of the small size), but each method's interface is *not meaningfully simpler* than its one-line implementation — a caller has to learn and orchestrate three separate calls, each barely hiding anything, to do what could have been one call: `validate(value, max_length=50)` doing all three checks internally and returning one clear result. This module is shallow: it has three tiny interfaces, and the sum of the cognitive cost of learning and correctly sequencing all three actually *exceeds* what one deeper, appropriately-larger `validate()` method would have cost a caller to learn and use.

### The specific, deliberate disagreement with Clean Code's function-size guidance
Ousterhout explicitly argues that `clean-code/03`'s aggressive "keep functions to 4-6 lines" instinct, applied uncritically, tends to produce shallow modules: splitting a cohesive piece of logic into many tiny functions doesn't reduce the *total* complexity a reader must eventually understand to grasp the whole — it just redistributes that complexity across more interfaces (more names to learn, more call boundaries to trace across), and each additional interface boundary has its own, non-zero cognitive cost (echoing `code-complete/02`'s "how much must you hold in mind" framing, but pointing it at a different conclusion than Clean Code's).

**Worked example — the same logic, contrasted for depth.** A "before" split into many tiny, shallow steps:
```
def validate_order(order):
    check_has_items(order)
    check_items_positive_price(order)
    check_customer_exists(order)
    check_customer_not_banned(order)
    check_shipping_address_valid(order)
```
Versus a single, deeper `validate_order` that internally does the same checks but exposes one simple call and one simple result to callers, with the individual checks as genuinely private, non-separately-callable internal logic rather than a public sequence a caller must learn to invoke *in order* (note: several of these checks have a real, easy-to-get-wrong dependency, e.g. you shouldn't check shipping address validity for a customer who doesn't exist yet — an implicit ordering constraint the "many tiny public functions" version pushes onto every caller to get right, rather than encapsulating). Ousterhout's point isn't "never split functions" — it's that splitting should be evaluated by whether it actually produces a *simpler interface for the resulting pieces*, not merely a *shorter* one.

### Reconciling, not just contrasting, with Clean Code
The subject's own framing (a deliberate counterpoint "to hold in tension") is more useful than treating this as "Ousterhout is right, Martin is wrong." A genuinely well-designed small function (per `clean-code/03`'s own best examples) usually *is* deep relative to its size — a well-named, single-purpose helper with a simple, narrow interface hiding a small but real piece of logic. The disagreement is sharpest at the margin: Clean Code's rule of thumb pushes toward splitting whenever a function exceeds a small line count, and Ousterhout's depth criterion pushes toward splitting only when the split actually produces a simpler *interface*, not just a shorter *body* — the two heuristics agree in the common case and diverge specifically when further splitting would create several new, still-not-very-simple interfaces (the `DataValidator` example above) rather than hiding real complexity behind a cleanly narrower one.

## Pros
- The depth metric gives a specific, checkable test ("interface simple relative to implementation?") that goes beyond mere line-count heuristics for evaluating whether decomposition actually helped.
- Correctly identifies that splitting can sometimes *increase* total system complexity by multiplying shallow interfaces, a failure mode line-count-only heuristics can miss entirely.
- The Unix I/O example gives a concrete, widely-recognized touchstone for what "deep" genuinely looks like at its best, useful as a calibration reference.

## Cons
- "Is this interface simple relative to its implementation" is a genuinely harder, more judgment-dependent question to answer quickly than "count the lines," which is part of why Clean Code's simpler heuristic remains popular despite this critique.
- Taken too far, "prefer deep modules" can be used to justify avoiding decomposition that would genuinely have helped (e.g., truly separating two unrelated concerns bundled in one large function, which is a cohesion problem `clean-code/10` correctly flags, not a depth problem).
- The depth framework doesn't, on its own, tell you *how* to design a genuinely deep interface for a new problem — it's a good evaluative test for a candidate design, but a weaker generative tool for producing one from scratch.

## Alternatives
- **Clean Code's line-count-driven decomposition** (`clean-code/03`) — simpler to apply mechanically, and usually correct in the common case, at the risk of occasionally shallowing a module that would have been better left more consolidated.
- **Cohesion-based splitting criteria** (`clean-code/10`, `code-complete/04`) — a complementary, not competing, lens: cohesion asks "do these things belong together," depth asks "is the resulting interface worth its complexity" — a genuinely low-cohesion large function should still usually be split, regardless of the depth question, because it's bundling unrelated concerns, not because of its size.
- **Interface Segregation Principle** (see `software-engineering/clean-architecture`) — a related SOLID principle arguing interfaces should be no larger than clients actually need, complementary to depth's "is the interface simple relative to what it hides" question.

## When to use it
Apply the depth test specifically when deciding whether to split an already-cohesive piece of logic into smaller pieces: ask whether the split produces genuinely simpler individual interfaces, or just shorter individual bodies with the same total interface complexity spread across more names and call sites.

## When NOT to use it
Don't use "prefer deep modules" as a justification to avoid splitting a module that's genuinely low-cohesion (bundling multiple unrelated responsibilities per `clean-code/10`) — that's a different problem the depth criterion doesn't excuse. Don't apply the depth test to modules whose interface is already appropriately narrow and whose current size reflects genuine, singular purpose rather than bundled unrelated concerns.

## Key takeaways / mental model
Before splitting a module, ask: "does this split produce pieces whose *interfaces* are each meaningfully simpler than the whole's interface was, or does it just make each piece's *body* shorter while leaving me with several new interfaces to learn instead of one?" Depth, not brevity, is the actual goal.

## Self-check questions
1. Using the `DataValidator` example, explain specifically why splitting validation into three public methods makes the module shallower rather than deeper.
2. Why does Ousterhout use Unix file I/O as the canonical example of a deep module? What specifically makes its interface-to-implementation ratio so favorable?
3. Describe a case from your own code where splitting a function actually made the overall design harder to understand, not easier. What would Ousterhout's depth test have flagged?
4. How does the depth criterion relate to, but differ from, the cohesion criterion in `clean-code/10`? Give an example where a module could be highly cohesive but still shallow.

## References
- A Philosophy of Software Design, 2nd ed. (John Ousterhout), Chapter 4: "Modules Should Be Deep".
- See also: `clean-code/03` (Functions: Small, One Thing, One Level) for the deliberately contrasting view this lesson engages with directly.
