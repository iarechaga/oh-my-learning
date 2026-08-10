---
id: code-complete/10
subject: code-complete
title: Controlling Loops and Unusual Control Structures
slug: loops-control-structures
status: drafted
mastery:
seniority: mid
source: Code Complete, 2nd ed. (Steve McConnell), Chapter 16
prerequisites: [code-complete/09]
created: 2026-08-10
updated: 2026-08-10
---

# Controlling Loops and Unusual Control Structures

## TL;DR
Keep loops short enough and simple enough to see the whole thing at once, prefer a single, clearly-marked exit condition over scattered `break`s and early returns buried deep inside, and treat `goto`-like jumps and deeply nested loop-and-conditional combinations as almost always a sign the logic should be restructured or extracted into a named routine instead.

## The idea
Loops are where a small ordering mistake (`code-complete/09`) or an unclear condition compounds the most, because a loop's logic is executed repeatedly and often interacts with mutable state across iterations — an off-by-one, an inverted condition, or an unclear exit point inside a loop is disproportionately costly compared to the same class of mistake in straight-line code, because the bug's effect can be silently wrong across every iteration rather than just one place. This chapter's guidance is about keeping loops simple enough that their entire behavior can be verified by inspection, and about being deliberate with anything that jumps control flow in a non-obvious way (multiple `break`s, early `return`s from deep inside nested loops, `goto`).

## How it works

### Keep loops short enough to see as a whole
McConnality's guidance: a loop should ideally be short enough that you can see its entire body without scrolling, and if a loop body grows too large to hold in view at once, extract the body into a well-named routine called once per iteration — directly applying `code-complete/02`'s cognitive-load argument specifically to loops, where the "held in mind" burden is worse because it must be tracked across repeated executions, not just once.

**Worked example — before (long loop body, hard to hold in view):**
```
for order in orders:
    if order.status == "pending":
        # 30 lines of validation, discount calc, tax calc, persistence, notification...
        ...
```
**After (extracted, loop body trivially small):**
```
for order in orders:
    if order.status == "pending":
        process_pending_order(order)   # the 30 lines now live in one well-named routine
```
The loop itself is now entirely visible at a glance; the substantive logic is still there, just named and extractable to be read (and tested) independently of the iteration mechanics.

### Minimize the number of exit conditions, and make them obvious
A loop with one clear termination condition (a simple `while` condition, or a `for` over a known range) is far easier to verify correct than a loop with several scattered `break` statements buried at different nesting depths, each representing a different, easy-to-miss way the loop could end. If multiple exit conditions are genuinely necessary, keep them near the top of the loop body (not buried deep inside nested conditionals) so a reader scanning the loop's start can see, up front, every way it might terminate — rather than discovering a hidden `break` only by reading the entire body.

**Worked example.** Searching a list for the first item matching two independent criteria, with an early exit:
```
found = None
for item in items:
    if item.is_expired:
        continue          # exit-adjacent control flow, but clearly placed near the top
    if item.matches(criteria):
        found = item
        break              # the one substantive exit, visible without deep nesting
```
Both control-flow deviations (`continue`, `break`) sit near the top of the loop body, immediately visible — contrast with a version where the `break` is nested three `if` levels deep inside 20 lines of unrelated logic, which would force a reader to read the entire body just to discover the loop can end early at all.

### Nested loops: name the levels, and watch the depth
Deeply nested loops (three or more levels) are a strong complexity signal (foreshadowing `code-complete/11`'s complexity-metrics treatment) — each additional nesting level multiplies the number of distinct execution paths a reader must consider. Where nesting is genuinely necessary (e.g., a true 2D/3D grid traversal), use domain-meaningful index names (per `code-complete/08`'s `row`/`col` example) so at least the *purpose* of each level is clear even though the structural complexity remains; where nesting arises from combining several *unrelated* concerns in the same loop, extracting inner loops into their own named routines (as above) is usually the better fix.

### `goto` and similarly unstructured jumps — nearly always avoidable, occasionally still useful
McConnell, notably less dogmatic here than some contemporaries, doesn't declare `goto` categorically forbidden — he acknowledges a few narrow, genuinely useful cases (some error-cleanup patterns in languages lacking exceptions, or breaking out of deeply nested loops in languages without a labeled-break construct) where a disciplined, clearly-commented `goto` can be clearer than the convoluted workaround needed to avoid it entirely. But the default, strong recommendation remains: structured control flow (loops with clear conditions, named routines, labeled breaks where the language supports them) should be your near-universal first choice, and an unstructured jump should be a rare, deliberate, well-justified exception you can defend specifically — not a habitual shortcut.

### Loop and a half, and other named idioms
The chapter also catalogs specific recurring loop shapes worth recognizing by name rather than reinventing awkwardly each time — e.g., the "loop and a half" pattern for a loop whose exit condition can only be evaluated partway through the body (read a line, check if it's the sentinel, otherwise process it) — recognizing these named shapes helps you reach for a known-good structure instead of contorting a `while` condition to awkwardly front-load logic that naturally belongs mid-body.

## Pros
- Loops small enough to see as a whole, with obvious exit conditions, are dramatically easier to verify correct by inspection — directly reducing the risk of iteration-repeated bugs.
- Extracting large loop bodies into named routines makes the extracted logic independently testable, separate from the iteration mechanics.
- Recognizing named loop idioms (loop-and-a-half, etc.) avoids awkward, ad hoc reinventions of well-understood shapes.

## Cons
- Extracting every nontrivial loop body into a separate routine adds a layer of indirection (a reader must now also open the extracted routine to see the full behavior) — proportionate for genuinely large bodies, unnecessary ceremony for already-small ones.
- Minimizing exit conditions can occasionally force awkward, less-natural code compared to a well-placed, well-commented early exit deep in a loop — a rare but real case where the "rule" and genuine clarity diverge.
- Some legitimate performance optimizations (loop unrolling, combined multi-purpose loops for cache locality) intentionally trade off some of this chapter's readability guidance for measured speed gains, and McConnell doesn't treat readability as an absolute trump card in every performance-critical context.

## Alternatives
- **Functional-style iteration (map/filter/reduce) instead of explicit loops** — often eliminates entire classes of loop-control-flow concerns (off-by-one errors, unclear exit conditions) by expressing the intent declaratively rather than imperatively, at some cost in explicitness for genuinely complex, multi-condition iteration logic.
- **Generators/iterators encapsulating traversal logic** — push the complexity of "how do I traverse this" into a reusable, separately-testable construct, leaving the calling loop trivially simple regardless of how complex the underlying traversal actually is.
- **Recursive formulations** — for some problems (tree traversal, certain divide-and-conquer algorithms), a recursive structure is clearer than an equivalent iterative loop with manual stack management, at the cost of stack-depth and, in some languages, performance considerations.

## When to use it
Apply "keep the loop body small enough to see at once" and "minimize and surface exit conditions" to every loop, as a default habit. Extract loop bodies into named routines once they exceed roughly what fits on one screen, or once they mix concerns that would each deserve their own name.

## When NOT to use it
Don't extract trivially small loop bodies into separate routines just for the sake of following this guidance — that adds indirection without a corresponding clarity benefit. Don't avoid a well-justified, well-commented `goto` or early-exit pattern in the rare case (some error-cleanup code, deeply nested-loop breaks) where the structured alternative would genuinely be more convoluted, not less.

## Key takeaways / mental model
Ask of any loop: "can I see its entire behavior, including every way it can end, without scrolling or digging through nested conditionals?" If not, that's the signal to extract the body into a named routine or to consolidate and surface the exit conditions near the top.

## Self-check questions
1. Find a loop in your own code with a `break` or early `return` buried deep inside nested conditionals. Rewrite it so every exit condition is visible near the top of the loop body.
2. Explain why bugs inside loops tend to be more costly than equivalent bugs in straight-line code.
3. Describe a legitimate, narrow case (per McConnell's more permissive stance) where a `goto` or similar unstructured jump might genuinely be clearer than the structured alternative.
4. Give an example of a "loop and a half" situation from your own experience, and describe how you handled the awkward mid-body exit condition.

## References
- Code Complete, 2nd ed. (Steve McConnell), Chapter 16: "Controlling Loops".
