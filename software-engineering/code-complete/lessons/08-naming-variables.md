---
id: code-complete/08
subject: code-complete
title: Naming Variables Well
slug: naming-variables
status: drafted
mastery:
seniority: junior
source: Code Complete, 2nd ed. (Steve McConnell), Chapter 11
prerequisites: [clean-code/02, code-complete/07]
created: 2026-08-10
updated: 2026-08-10
---

# Naming Variables Well

## TL;DR
Beyond `clean-code/02`'s general "reveal intent" naming principles, this chapter gives specific, checkable conventions for particular kinds of variables — booleans that read as true/false questions, loop variables with more meaning than a bare `i` once the loop body grows, status/flag variables named for their actual states rather than generically, and a consistent, documented convention for optional naming elements (prefixes, abbreviations) so the *whole team* names things the same way.

## The idea
`clean-code/02` established the general theory of good naming: reveal intent, avoid disinformation, match length to scope. This chapter, from a different book emphasizing checklist-style practical conventions, narrows in on **specific variable categories that have their own naming failure modes** — booleans, loop counters, status codes — and on the meta-point that a team-wide naming *convention*, consistently applied, is itself valuable independent of whether any single name is individually "clever" or not.

## How it works

### Boolean variables should read as a true/false question
A boolean named `status` or `flag` tells the reader nothing about what `true` versus `false` actually *means* without reading the assignment or usage. Name booleans so that reading the name alone answers a yes/no question: `isValid`, `hasPermission`, `canRetry`, `wasSuccessful`. This is stronger than just "use a good name" — it's a specific structural pattern (a verb/state prefix: `is`/`has`/`can`/`was`) that reliably produces self-documenting booleans across an entire codebase, rather than relying on ad hoc judgment each time.

**Worked example — before:**
```
if order.status:
    ship(order)
```
Does `status` being truthy mean "paid," "validated," "ready to ship," or something else entirely? The reader can't tell without finding where `status` is set. **After:**
```
if order.is_ready_to_ship:
    ship(order)
```
Now the condition is self-explanatory at the call site with zero additional lookup.

### Loop variables: `i`, `j`, `k` are fine only while the loop stays trivial
`clean-code/02` already established that name length should match scope — a loop counter in a three-line loop can reasonably stay `i`. This chapter sharpens the specific failure mode: **as soon as a loop body grows, gains nested loops, or the index carries actual domain meaning, `i`/`j`/`k` stop being adequate**, because the scope that originally justified brevity no longer holds.

**Worked example.** A single-level, three-line loop: `for i in range(len(items)): total += items[i].price` — `i` is fine; its entire meaning is visible in three lines. Now consider a nested loop over a 2D grid where an outer bug once swapped `i` and `j`: `for i in range(rows): for j in range(cols): grid[j][i] = ...` — silently transposing the grid. Naming the indices for what they actually represent (`for row in range(rows): for col in range(cols): grid[row][col] = ...`) makes a transposition bug like this visually obvious at the point it's written, because `grid[col][row]` reads as suspicious in a way `grid[j][i]` doesn't.

### Status variables: name for the specific states, not a generic label
A variable literally named `status` or `flag` used to hold one of several meaningful states (`PENDING`, `SHIPPED`, `CANCELLED`) should ideally be typed as an enum with those exact named values, and even the variable holding it should be named for what it represents (`orderStatus`, not just `status`, especially once more than one kind of "status" exists in the same scope — an order status and a payment status are easy to confuse if both are just called `status` nearby).

### Consistent naming conventions and abbreviations — a team-level concern
McConnell stresses that individual naming quality matters less, in aggregate, than whether the *whole team* follows the same conventions consistently: if one part of the codebase abbreviates "customer" as `cust` and another spells it out fully, or if one module capitalizes constants and another doesn't, readers must learn and hold multiple naming dialects simultaneously — a direct, unnecessary addition to cognitive load (`code-complete/02`) that has nothing to do with any individual name's quality and everything to do with cross-codebase consistency. Where abbreviations are used at all, the chapter recommends a single, documented, applied-everywhere convention (e.g., always `num` for "number of," never sometimes `num` and sometimes `cnt` for the same concept) — directly echoing `pragmatic-programmer/03`'s "one word per concept" DRY-of-vocabulary principle, now applied specifically to abbreviation style.

### Avoid names that differ in ways easy to misread
Extending `clean-code/02`'s disinformation warning with a specific, checkable list of visually confusable pairs to actively avoid: names differing only in a hard-to-notice character (`l` vs. `1` in some fonts, or two similarly-spelled variables like `clientData` and `clientDate`), or names that are close synonyms used inconsistently for genuinely different things (`input`/`inValue` used interchangeably for what are actually two different parameters). These are specifically dangerous because they pass a casual visual scan without triggering a "wait, what does this mean" pause — the exact opposite of what a good name should do.

## Pros
- Boolean-as-question naming (`is`/`has`/`can` prefixes) is a cheap, mechanical convention that reliably eliminates an entire category of ambiguous conditionals.
- Naming loop variables for their domain meaning once a loop grows past trivial size catches structural bugs (like index transposition) that generic names hide.
- Team-wide consistent conventions reduce cross-codebase cognitive load independent of any single name's individual quality.

## Cons
- Overly verbose boolean/status names, applied rigidly even in genuinely trivial, obvious contexts, can add noise disproportionate to the ambiguity risk.
- Enforcing a team-wide naming convention takes ongoing discipline (via review or linting) and tends to drift without active maintenance, especially across a growing team.
- Renaming a widely-used status/flag variable or converting it from a loose type to an enum, once adopted broadly, can be a nontrivial refactor to retrofit onto existing code.

## Alternatives
- **Linters/static analysis enforcing naming conventions** (e.g., requiring boolean variables to start with `is`/`has`) — mechanizes part of this chapter's guidance, catching violations automatically rather than relying purely on review-time human judgment.
- **Strong typing over naming conventions for status values** — instead of relying on a well-named string/int for status, use a proper enum or sum type so the compiler (not just the name) enforces which states are valid, reducing reliance on naming discipline alone to convey the same information.
- **Domain-specific naming glossaries** (see `domain-modeling/ddd-evans`'s ubiquitous language) — go further than a generic team convention by tying naming specifically to the business's own established vocabulary, for domains where that vocabulary is rich and precise.

## When to use it
Apply boolean-as-question naming to every boolean variable, always. Rename loop variables for domain meaning the moment a loop stops being trivially small or gains nesting. Establish and document (in a style guide or linter config) a single team-wide convention for abbreviations and naming style, especially once a team grows past a size where informal, unwritten consistency naturally holds.

## When NOT to use it
Don't over-apply verbose boolean naming to a truly obvious, extremely local boolean whose meaning is unambiguous from one line of immediate context. Don't retrofit every existing `status`/`flag` variable in a large legacy codebase in one disruptive pass — prioritize the ones causing genuine confusion or bugs, and apply the convention going forward for new code (echoing the incremental spirit of `software-engineering/legacy-code`).

## Self-check questions
1. Find a boolean variable in your own code that doesn't read as a clear true/false question. Rename it using the `is`/`has`/`can` convention.
2. Explain, using the grid-transposition example, why naming loop indices for domain meaning can catch a structural bug that `i`/`j` naming hides.
3. Why does McConnell emphasize team-wide naming *consistency* as being as important as individual name quality?
4. Give an example of two similarly-named or similarly-spelled variables from real code that could plausibly be confused for each other, and propose better names.

## References
- Code Complete, 2nd ed. (Steve McConnell), Chapter 11: "The Power of Variable Names".
- See also: `clean-code/02` (Meaningful Names) for the general theory this chapter's specific conventions build on.
