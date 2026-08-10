---
id: refactoring/08
subject: refactoring
title: Simplifying Conditional Logic
slug: simplifying-conditionals
status: drafted
mastery:
seniority: mid
source: Refactoring, 2nd ed. (Martin Fowler), Chapter 10
prerequisites: [refactoring/05, code-complete/09]
created: 2026-08-10
updated: 2026-08-10
---

# Simplifying Conditional Logic

## TL;DR
Decompose Conditional extracts a condition and its branches into named functions, making a complex `if` read like prose. Replace Nested Conditional with Guard Clauses flattens disqualifying checks into early returns (echoing `code-complete/09`). Replace Conditional with Polymorphism is the most structural of the three, converting a repeated type-switch into a class hierarchy — the mechanical fix for the smell `clean-code/06` and `clean-code/12` both flag.

## The idea
`code-complete/09` already covered ordering and structuring conditionals well; this lesson gives the specific, mechanical, named refactoring techniques for getting *existing*, already-tangled conditional logic into that better shape safely, step by step, rather than rewriting it from scratch.

## How it works

### Decompose Conditional — name the condition and each branch
Extract the boolean condition itself, and each branch's logic, into separate, well-named functions (a direct application of Extract Function, `refactoring/05`, to the specific case of `if`/`else` structures).

**Worked example.**
```
# Before
if not (date < SUMMER_START || date > SUMMER_END):
    charge = quantity * summer_rate + summer_service_charge
else:
    charge = quantity * regular_rate + regular_service_charge

# After
if is_summer(date):
    charge = summer_charge(quantity)
else:
    charge = regular_charge(quantity)
```
The confusing negated compound condition (`not (date < X || date > Y)`) and the arithmetic in each branch are now named, self-explanatory functions — a reader no longer has to mentally evaluate the boolean logic or the arithmetic to understand what the code is *doing*; the names tell them directly, and the details are available on demand by opening the named function if genuinely needed.

### Replace Nested Conditional with Guard Clauses — flatten disqualifying checks
When a function has one "normal" path buried deep inside several nested `if`s checking for disqualifying special cases, invert the structure: check each disqualifying condition first, with an early `return`, so the "normal" logic is left unindented and undisturbed at the end — directly the technique `code-complete/09` recommended, now given as its own named, mechanical refactoring.

**Worked example.**
```
# Before — the "normal" calculation buried three levels deep
def get_pay_amount(employee):
    result = 0
    if not employee.is_dead:
        if not employee.is_separated:
            if employee.is_retired:
                result = deadAmount()
            else:
                result = normalPayAmount(employee)
        else:
            result = separatedAmount()
    else:
        result = deadAmount()
    return result

# After — guard clauses handle each disqualifying case, normal logic is flat and clear
def get_pay_amount(employee):
    if employee.is_dead: return dead_amount()
    if employee.is_separated: return separated_amount()
    if employee.is_retired: return retired_amount()
    return normal_pay_amount(employee)
```
Every disqualifying condition is now a single, flat, immediately-visible line — echoing `code-complete/10`'s "make exit conditions obvious, near the top" guidance — and the genuinely normal case (the last line) is completely unindented, with none of the original nesting's nested-nested-nested nature obscuring it.

### Replace Conditional with Polymorphism — the structural fix for repeated type-switches
When the *same* type-based (or mode-based) conditional logic repeats across several methods (echoing `clean-code/12`'s "repeated conditional type-checking suggests missing polymorphism" smell), replace it with a class hierarchy: one subclass per type/mode, each overriding a shared method, so adding a new type/mode means adding one new subclass rather than adding a new branch to *every* repeated conditional.

**Worked example.**
```
# Before — the same bird-type switch repeated in multiple methods
def plumage(bird):
    if bird.type == "EuropeanSwallow": return "average"
    elif bird.type == "AfricanSwallow": return "tired" if bird.num_coconuts > 2 else "average"
    elif bird.type == "NorwegianBlueParrot": return "beautiful" if not bird.is_nailed else "scorched"

def air_speed_velocity(bird):
    if bird.type == "EuropeanSwallow": return 35
    elif bird.type == "AfricanSwallow": return 40 - 2 * bird.num_coconuts
    elif bird.type == "NorwegianBlueParrot": return 0 if bird.is_nailed else 10

# After — one class per type, each owning both behaviors
class EuropeanSwallow:
    def plumage(self): return "average"
    def air_speed_velocity(self): return 35

class AfricanSwallow:
    def __init__(self, num_coconuts): self.num_coconuts = num_coconuts
    def plumage(self): return "tired" if self.num_coconuts > 2 else "average"
    def air_speed_velocity(self): return 40 - 2 * self.num_coconuts
```
Adding a fourth bird type under the "before" version means editing every existing conditional function (change amplification, `philosophy-of-software-design/01`); under the "after" version, it means adding one new class, touching neither existing class — directly recovering the object-style "easy to add types" trade-off `clean-code/06` names, at the cost of the corresponding "harder to add new shared operations" trade-off that same lesson also names (unless paired with Visitor, `design-patterns/11`, if operations genuinely need to grow instead of types).

## Pros
- Decompose Conditional makes complex boolean logic and branch arithmetic self-documenting through naming, without needing a single line of explanatory comment.
- Guard clauses flatten nesting and surface every disqualifying condition near the top, directly reducing the reader's tracking burden (`code-complete/02`, `code-complete/11`).
- Replace Conditional with Polymorphism eliminates change amplification for a specific, common, and otherwise persistent smell (repeated type-switches), converting many scattered edits into one new, localized class.

## Cons
- Decompose Conditional, applied to an already-simple, clearly-readable condition, adds unnecessary indirection for no real clarity gain.
- Guard clauses assume an early-exit structure is actually appropriate for the function's control flow — for functions where all conditions genuinely need to converge into one final combined result (not a clean early-return shape), forcing guard clauses can be awkward.
- Replace Conditional with Polymorphism only pays off when the *same* type-switch genuinely repeats across multiple methods — applied to a single, one-off conditional with no repetition, it's disproportionate structural overhead for the actual problem.

## Alternatives
- **Table-driven dispatch (a lookup dictionary mapping type to behavior)**, instead of full polymorphism — a lighter-weight alternative to Replace Conditional with Polymorphism when the per-type behavior is simple enough not to need a full class, and when a new "type" is really just a new dictionary entry rather than a class warranting its own identity and additional behavior.
- **Pattern matching / sum types** (in languages with strong native support) — achieve much of polymorphism's "compiler-enforced exhaustiveness, easy to add cases" benefit with a different mechanism and often less boilerplate than a full class hierarchy.
- **Strategy pattern** (`design-patterns/09`) — a closely related structural fix, more appropriate when the varying behavior is a single, swappable algorithm assigned at runtime rather than a fixed set of named "types."

## When to use it
Apply Decompose Conditional whenever a condition or branch's logic isn't immediately readable at a glance. Apply guard clauses whenever a function's "normal" logic is nested inside several layers of disqualifying special-case checks. Apply Replace Conditional with Polymorphism specifically once the same type-based conditional structure genuinely repeats across multiple methods/functions, not for a single isolated instance.

## When NOT to use it
Don't decompose an already-simple, clearly-named condition purely for the sake of following this technique. Don't force guard clauses onto logic that genuinely needs all conditions evaluated together for one combined result. Don't reach for full polymorphism for a one-off conditional that doesn't actually repeat — a table-driven dispatch or even the plain conditional itself may be simpler and entirely adequate.

## Key takeaways / mental model
For a confusing condition or branch: name it (Decompose Conditional). For deeply nested disqualifying checks: flatten them to the top (guard clauses). For the same type-based switch appearing again and again across your codebase: replace it with one class per type (polymorphism) — but only once the repetition is real, not anticipated.

## Self-check questions
1. Apply Decompose Conditional to a confusing `if` condition from your own code, and explain what became easier to read.
2. Rewrite a deeply-nested conditional function using guard clauses, and identify which condition should be checked first and why.
3. Using the bird example, explain precisely what change-amplification cost the polymorphic version eliminates compared to the repeated-conditional version.
4. Describe a case where a table-driven dispatch would be a better, lighter-weight choice than full Replace Conditional with Polymorphism.

## References
- Refactoring: Improving the Design of Existing Code, 2nd ed. (Martin Fowler), Chapter 10: "Simplifying Conditional Logic".
