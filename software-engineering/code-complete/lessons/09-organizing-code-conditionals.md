---
id: code-complete/09
subject: code-complete
title: Organizing Straight-Line Code and Conditionals
slug: organizing-code-conditionals
status: drafted
mastery:
seniority: junior
source: Code Complete, 2nd ed. (Steve McConnell), Chapters 14-15
prerequisites: [code-complete/07]
created: 2026-08-10
updated: 2026-08-10
---

# Organizing Straight-Line Code and Conditionals

## TL;DR
Order statements so dependent operations read top-to-bottom in the order they actually happen, keep dependent statements physically close together, and structure `if`/`else` chains so the normal case comes first and each branch is easy to scan — small, mechanical ordering choices that compound into a much easier-to-follow routine.

## The idea
Even within a single, already-well-named, appropriately-sized routine (`code-complete/05`), the *order* in which statements appear and the *structure* of conditional branches still meaningfully affect how easily a reader can follow what happens and when. This chapter is about the fine-grained, sentence-level organization within a routine — the equivalent, one level down, of what `clean-code/05` covers at the file/vertical-formatting level.

## How it works

### Order statements to reflect true dependencies, and group dependent statements together
If statement B depends on statement A's result, A should appear immediately before B, not scattered elsewhere in the routine with unrelated code interleaved between them — directly echoing `code-complete/07`'s "minimize span" guidance, now applied to statement ordering generally rather than just variable declarations specifically. Conversely, if two statements have *no* dependency on each other, their relative order genuinely doesn't matter functionally — but the chapter recommends still choosing an order that reads naturally (e.g., matching the order a domain expert would describe the steps in), since an arbitrary, unmotivated order still costs the reader a moment of "why is this here, in this position" friction even when it's not incorrect.

**Worked example — before (dependent statements scattered):**
```
tax_rate = get_tax_rate(order.region)
discount = calculate_discount(order)
subtotal = sum(item.price for item in order.items)
total = (subtotal - discount) * (1 + tax_rate)
```
Here, `discount` and `tax_rate` are computed before `subtotal`, even though `total`'s actual dependency order is subtotal-then-discount-then-tax. **After (ordered to match actual dependency flow):**
```
subtotal = sum(item.price for item in order.items)
discount = calculate_discount(order)
tax_rate = get_tax_rate(order.region)
total = (subtotal - discount) * (1 + tax_rate)
```
Functionally identical, but a reader following the final `total` computation top-down now sees each input computed in the order it conceptually feeds into the result, rather than needing to jump around mentally to reconstruct the actual data flow.

### Structure `if`/`else` chains for readability
- **Put the normal/common case first.** A reader scanning an `if`/`else` chain naturally expects the first branch to represent the typical path; burying the common case in an `else` after several unusual special-case checks forces extra scanning effort to find "what usually happens here."
- **Keep the positive form when reasonable** (`if is_valid` rather than `if not is_invalid`) — double negatives (`if not is_invalid`) require an extra mental inversion step every time a reader encounters them, a small but entirely avoidable tax.
- **Make sure both branches are actually necessary and clear** — an `if` branch with an empty or near-trivial body, and all the substantive logic in the `else`, usually reads better inverted (put the substantive logic in the `if`, invert the condition) so the reader doesn't have to read past an uninteresting branch first to find the real logic.

**Worked example — before:**
```
if not user.is_banned:
    if user.has_verified_email:
        allow_login(user)
    else:
        show_verification_prompt(user)
else:
    show_banned_message(user)
```
The banned check (likely the rarer case) is checked first and nested awkwardly around the more common verified/unverified logic. **After:**
```
if user.is_banned:
    show_banned_message(user)
elif user.has_verified_email:
    allow_login(user)
else:
    show_verification_prompt(user)
```
Flattened from nested `if`/`else` into a single `if`/`elif`/`else` chain, and reordered so the reader encounters the more decisive, rarer disqualifying case first, then the two common outcomes as parallel, equally-weighted branches — easier to scan than nested conditionals with an inverted, double-negative-flavored outer check.

### Case/switch statements: order for the most common case, and always handle "else"
For a switch/case-style dispatch across several possibilities, put the most frequently-hit case first for readability (and, in some languages/older compilers, for a minor performance benefit, though that's secondary to the readability point) and always include an explicit default/else branch — even if it's just an assertion that "this should be unreachable" — so a reader (and the runtime) can trust that every possible input is deliberately accounted for, rather than silently falling through with no handling at all if a new, unanticipated case is introduced later.

### Boolean expression clarity
Complex boolean conditions (`if (a and b) or (not c and d)`) benefit from being decomposed into a named intermediate variable when the expression itself isn't immediately parseable at a glance: `should_notify = (is_active and has_opted_in) or (is_admin and not is_muted)`, then `if should_notify:` — this both names the *meaning* of the condition (echoing `clean-code/02`'s naming discipline, applied to boolean logic specifically) and avoids the reader needing to mentally evaluate raw boolean algebra to understand what circumstance the branch actually covers.

## Pros
- Ordering statements to match true dependencies and keeping related statements close together directly reduces the mental reconstruction effort of following a routine's actual logic flow.
- Common-case-first, positive-form conditionals reduce the number of double-negatives and buried-common-paths a reader has to untangle.
- Named boolean intermediate variables make complex conditions self-documenting rather than requiring live boolean-algebra evaluation by the reader.

## Cons
- "Order for the most common case" requires actually knowing which case is common — guessing wrong provides no benefit and can occasionally mislead a reader about the code's real-world usage pattern.
- Restructuring existing nested conditionals into a flatter, reordered form is a real (if usually low-risk) refactoring effort, and can introduce subtle behavioral differences if branch conditions aren't logically equivalent after reordering (worth double-checking with tests, per `pragmatic-programmer/13`).
- Named intermediate boolean variables, applied to already-simple conditions, add an unnecessary extra line and indirection with no real clarity benefit.

## Alternatives
- **Guard clauses (early returns) instead of nested if/else** — a related, often-preferred structural alternative for handling several disqualifying conditions in sequence: `if user.is_banned: return show_banned_message(user)` followed by the main logic unindented, rather than deeply nested `if`/`else` — reduces nesting depth directly (see `code-complete/11`).
- **Polymorphic dispatch instead of a large switch/case** (see `clean-code/06`, `clean-code/12`'s repeated-conditionals smell) — for cases where the same type-based switch recurs across multiple functions, replacing it with polymorphism eliminates the ordering/completeness concerns of a switch statement entirely, at the cost of the object/data-structure trade-off discussed in `clean-code/06`.
- **Declarative/table-driven logic** — for dispatch logic driven by a large number of cases with a regular structure, a lookup table (mapping input to result/handler) can be clearer and more maintainable than an equivalently large `if`/`elif` or `switch` chain.

## When to use it
Apply dependency-ordering and common-case-first structuring to every routine with more than a couple of sequential steps or more than a two-way branch. Extract named boolean variables whenever a condition requires more than a quick glance to parse.

## When NOT to use it
Don't reorder genuinely independent statements purely to chase a "natural" narrative order if doing so has any risk of subtly changing behavior (e.g., statements with hidden side-effect ordering dependencies you haven't fully verified) — confirm independence first (echoing `pragmatic-programmer/11`'s temporal-coupling caution). Don't extract a named boolean variable for a condition that's already trivially readable as written.

## Key takeaways / mental model
Read your own routine as if seeing it for the first time and ask: "does the order of these statements match the order I'd naturally explain them in, and does the first branch I encounter in each conditional represent what usually happens?" If not, reordering costs little and pays off every time someone else reads it.

## Self-check questions
1. Find a routine in your own code where statement order doesn't match the natural dependency/narrative order. Reorder it and explain what's easier to follow afterward.
2. Using the login example, explain why nested `if`/`else` with a negated outer condition is harder to scan than a flattened `if`/`elif`/`else` chain.
3. When would extracting a named boolean variable from a complex condition NOT be worth doing?
4. Why does a switch/case statement benefit from an explicit default/else branch even when every "current" case seems to be covered?

## References
- Code Complete, 2nd ed. (Steve McConnell), Chapter 14: "Organizing Straight-Line Code" and Chapter 15: "Using Conditionals".
