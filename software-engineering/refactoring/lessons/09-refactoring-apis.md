---
id: refactoring/09
subject: refactoring
title: Refactoring APIs and Parameters
slug: refactoring-apis
status: drafted
mastery:
seniority: mid
source: Refactoring, 2nd ed. (Martin Fowler), Chapter 11
prerequisites: [refactoring/05, clean-code/03]
created: 2026-08-10
updated: 2026-08-10
---

# Refactoring APIs and Parameters

## TL;DR
Change Function Declaration renames or reshapes a function's signature safely, using a temporary transitional period (keeping the old signature as a thin wrapper) rather than a single risky global rename. Introduce Parameter Object groups a repeated cluster of parameters (Data Clumps, `refactoring/04`) into one named type. Remove Flag Argument eliminates the specific anti-pattern `clean-code/03` names, splitting one flag-controlled function into two honestly-named ones.

## The idea
A function's signature is one of its most consequential design decisions — it's the part every caller directly depends on, so changing it, once the function has real callers, needs a specific, safe migration path rather than a single all-at-once edit that risks breaking every call site simultaneously if something's missed. This lesson's techniques are all, in different ways, about changing a signature *safely*, in a way that's verifiable and reversible at each step.

## How it works

### Change Function Declaration — migrate a signature without a risky big-bang edit
For a small, low-risk change (renaming a rarely-called private function, adding an optional parameter with a safe default), a direct, immediate edit plus a full test run is fine. For a larger, riskier change (a widely-called function, a parameter reordering that could silently produce wrong behavior if a caller passes arguments positionally in the old order), Fowler recommends a **migration via an intermediate step**: create the new signature as a genuinely new function, have the old function's body simply delegate to the new one, migrate callers one at a time (or in batches, verified via tests at each step), and only remove the old signature once every caller has migrated.

**Worked example.**
```
# Step 1: old function delegates to a new one with the desired signature
def calculate_total(order):              # old signature, kept temporarily
    return calculate_order_total(order, include_tax=True)

def calculate_order_total(order, include_tax):   # new signature
    subtotal = sum(item.price * item.qty for item in order.items)
    return subtotal * (1 + order.tax_rate) if include_tax else subtotal

# Step 2 (over time, across several small commits): migrate each caller
# from calculate_total(order) to calculate_order_total(order, include_tax=True)

# Step 3 (once no callers remain on the old signature): delete calculate_total entirely
```
Each step is individually small and verifiable, and at every point in the migration, both the old and new signatures work correctly — there's no moment where callers are broken while the migration is in progress, which is precisely the safety property a single, all-at-once rename/reshape cannot offer for a widely-used function.

### Introduce Parameter Object — group a recurring cluster
When several parameters consistently travel together across multiple function signatures (Data Clumps, per `refactoring/04` and `refactoring/07`), Introduce Parameter Object groups them into one named type, which can then also absorb any related behavior that operates on that cluster (a mechanical instance of Extract Class, `refactoring/06`, specifically triggered by a repeated parameter grouping).

**Worked example.**
```
# Before — the same three-value cluster in multiple signatures
def readings_within_range(readings, min_temp, max_temp): ...
def readings_outside_range(readings, min_temp, max_temp): ...

# After — the cluster becomes its own type
class TemperatureRange:
    def __init__(self, min_temp, max_temp): self.min_temp, self.max_temp = min_temp, max_temp
    def contains(self, temp): return self.min_temp <= temp <= self.max_temp

def readings_within_range(readings, range: TemperatureRange): ...
```
Beyond the immediate signature simplification, `TemperatureRange` can now also grow its own genuinely useful behavior (`contains`, and later perhaps `overlaps_with`, `midpoint`) — behavior that had nowhere natural to live when `min_temp`/`max_temp` were just two loose, separately-passed primitives (echoing `refactoring/07`'s Replace Primitive with Object logic, here triggered specifically by the parameter-clumping pattern).

### Remove Flag Argument — split, don't branch internally
Directly the fix for `clean-code/03`'s named flag-argument anti-pattern: a boolean (or enum-like) parameter that selects between two genuinely different behaviors should become two separately, honestly-named functions instead, each doing one specific thing.

**Worked example.**
```
# Before — a flag argument hiding two distinct behaviors
def book_concert(customer, is_premium):
    if is_premium:
        return premium_booking_flow(customer)
    return standard_booking_flow(customer)

# After — two honestly-named functions, callers state their intent directly
def book_premium_concert(customer):
    return premium_booking_flow(customer)

def book_standard_concert(customer):
    return standard_booking_flow(customer)
```
Every call site now states plainly which behavior it wants (`book_premium_concert(customer)`) rather than requiring a reader to know that `True` means "premium" at this specific call site — directly removing the ambiguity `clean-code/03` originally flagged, via this lesson's specific, named mechanical technique for doing so safely.

## Pros
- The migration-via-intermediate-step technique lets even large, widely-called function signatures change safely, without a risky single global edit.
- Introduce Parameter Object simplifies signatures and frequently unlocks a genuinely useful new type with its own behavior, as a natural side effect.
- Remove Flag Argument eliminates an entire category of ambiguous call sites, making intent explicit at every point of use.

## Cons
- The intermediate-step migration technique adds temporary duplication (old and new signatures coexisting) and requires discipline to actually finish (removing the old signature) rather than letting both linger indefinitely.
- Introducing a Parameter Object for a cluster that doesn't actually repeat meaningfully (a one-off pairing of two unrelated values that happen to be passed together once) is disproportionate structural overhead.
- Removing a flag argument by splitting into two functions can, if the two behaviors share substantial common logic, require care to avoid duplicating that shared logic — often addressed by having both new functions call a shared, private helper.

## Alternatives
- **Direct signature editing with a full-codebase find-and-replace**, skipping the intermediate-step migration — acceptable for small, low-risk, low-caller-count functions, but risky for anything widely called, per this lesson's own guidance.
- **Keyword/named arguments as an alternative to Introduce Parameter Object** — in languages with strong named-argument support, sometimes sufficient to clarify a signature without the overhead of a whole new type, when the parameters don't warrant their own behavior.
- **Builder pattern** (`design-patterns/04`) — a different, more general technique for managing many optional parameters, appropriate when a function/constructor has more configuration surface than a single Parameter Object cleanly captures.

## When to use it
Use the migration-via-intermediate-step approach whenever changing a widely-called function's signature. Use Introduce Parameter Object once a genuine, recurring cluster of parameters is identified (Rule of Three). Use Remove Flag Argument whenever you find a boolean or enum-like parameter selecting between two genuinely distinct behaviors, rather than a genuine configuration option.

## When NOT to use it
Don't bother with a full migration-via-intermediate-step for a private, rarely-called function with few, easily-verified call sites — a direct edit plus tests is simpler and sufficient there. Don't Introduce Parameter Object for a parameter grouping that's occurred only once. Don't split every boolean parameter into two functions — a genuine configuration toggle (not a hidden behavior fork) is fine to leave as a single parameter.

## Key takeaways / mental model
Before changing a function's signature, ask "how many callers does this have, and how risky would a mistake in updating them all at once be?" — scale your migration approach (direct edit vs. intermediate-step) to that answer. And whenever you see a boolean parameter, ask "does True/False actually mean two different behaviors, or one genuine configuration knob?" — the former should be two functions, not a flag.

## Self-check questions
1. Walk through migrating a function's signature using the intermediate-step technique, and explain why it's safer than a single, all-at-once edit for a widely-called function.
2. Identify a Data Clump from your own code (parameters that always travel together) and apply Introduce Parameter Object to it, noting what new behavior the resulting type could naturally absorb.
3. Find a flag argument in code you've seen and split it into two honestly-named functions, following Remove Flag Argument.
4. Describe a case where a flag argument is actually fine to leave as-is, because it represents a genuine configuration option rather than a hidden behavior fork.

## References
- Refactoring: Improving the Design of Existing Code, 2nd ed. (Martin Fowler), Chapter 11: "Refactoring APIs".
