---
id: refactoring/05
subject: refactoring
title: Composing Methods (Extract/Inline)
slug: composing-methods
status: drafted
mastery:
seniority: junior
source: Refactoring, 2nd ed. (Martin Fowler), Chapter 6
prerequisites: [refactoring/03, clean-code/03]
created: 2026-08-10
updated: 2026-08-10
---

# Composing Methods (Extract/Inline)

## TL;DR
Extract Function and Inline Function are the most fundamental, most frequently-used refactorings in the entire catalog — pulling a piece of logic out into its own named function, or collapsing a function back into its call site when its name no longer earns its keep. Both are small, mechanical, easily reversible, and together they're the primary tool for reshaping a function's structure without changing what it does.

## The idea
This lesson operationalizes `clean-code/03`'s "functions should be small and do one thing" into the two concrete, named, step-by-step mechanical techniques that actually get you there safely. Extract Function is refactoring's single most common move — the specific, disciplined procedure for turning "this chunk of code deserves its own name" into reality without breaking anything along the way. Inline Function is its precise inverse, used when a function's indirection no longer earns its keep (echoing `philosophy-of-software-design/07`'s pass-through-layer caution).

## How it works

### Extract Function — the mechanical procedure
1. Identify a coherent fragment of code within a larger function that could be given a clear, descriptive name.
2. Check what local variables the fragment reads and writes — these become the extracted function's parameters (for reads) and return value(s) (for writes).
3. Create the new function, named for *what* the fragment does (not *how*), with the identified parameters and return value.
4. Replace the original fragment with a call to the new function.
5. Run tests immediately (per `refactoring/03`'s safety-net discipline) to confirm behavior is unchanged.

**Worked example.**
```
# Before
def print_invoice(order):
    print(f"Invoice for {order.customer_name}")
    subtotal = sum(item.price * item.qty for item in order.items)
    tax = subtotal * order.tax_rate
    total = subtotal + tax
    print(f"Total: {total}")

# After — the total-calculation fragment extracted, named for what it computes
def print_invoice(order):
    print(f"Invoice for {order.customer_name}")
    total = calculate_total(order)
    print(f"Total: {total}")

def calculate_total(order):
    subtotal = sum(item.price * item.qty for item in order.items)
    tax = subtotal * order.tax_rate
    return subtotal + tax
```
`calculate_total` now has an honest, complete name (echoing `code-complete/05`'s naming standard), is independently testable, and is potentially reusable by other code that also needs an order's total — none of which was true while the logic sat inline inside `print_invoice`.

### Handling variables that complicate extraction
The mechanical procedure gets more involved when the fragment being extracted reassigns a variable that's used *after* the extracted block, or when it depends on several local variables computed just before it. Fowler's specific guidance: if a fragment only *reads* several locals, pass them as parameters; if it produces exactly one value used afterward, return that value; if it reassigns *multiple* variables that are each used afterward, that's a signal the fragment might not have as clean a single responsibility as it first appeared, and reconsidering the extraction's boundaries (rather than forcing an awkward multi-value return) is often the better fix.

### Inline Function — the precise inverse, and when it's the right call
Inline Function collapses a function call back into its body at the call site(s), removing the function definition. This is the correct move specifically when a function's *indirection* costs more than it delivers — directly the `philosophy-of-software-design/07` pass-through-layer smell, or a case where a function's body is now so simple and self-explanatory that the extra hop to a separately-named function adds a lookup cost for the reader without adding real clarity.

**Worked example.**
```
# Before — the indirection doesn't earn its keep
def get_rating(driver):
    return more_than_five_late_deliveries(driver) ? 2 : 1

def more_than_five_late_deliveries(driver):
    return driver.late_deliveries > 5

# After — inlined, since the extracted function added a lookup with no real clarity gain
def get_rating(driver):
    return 2 if driver.late_deliveries > 5 else 1
```
This isn't a universal rule against small helper functions (`clean-code/03` still generally favors them) — it's a judgment call, per `philosophy-of-software-design/03`'s depth criterion, about whether *this specific* extracted function's interface is actually simpler than just reading its one-line body directly at the call site. When it isn't, inlining is the more honest structure.

### Extract Function and Inline Function as complementary tools for exploration
A practical, less obvious use of this lesson's techniques together: when you're not yet sure how a piece of logic should be decomposed, it's often faster and safer to extract *speculatively*, look at the result, and either keep it, adjust its boundaries, or inline it back if it didn't turn out to be the right seam — rather than trying to design the "correct" decomposition perfectly in your head before touching any code. Because both operations are small, mechanical, and quickly reversible (especially with editor/IDE refactoring-tool support), this back-and-forth exploration is cheap and low-risk, exactly the kind of small, safe step `refactoring/01` describes.

## Pros
- Extract Function is the single highest-leverage, most frequently applicable refactoring — mastering it well pays off across almost every other refactoring scenario.
- Both operations are small, mechanical, and easily verified against tests, making them very low-risk individually even in code you don't yet fully understand.
- Together, they support fast, safe, exploratory restructuring — extract to try a decomposition, inline to undo it if it didn't help.

## Cons
- Over-applying Extract Function without attention to the resulting interface's depth (`philosophy-of-software-design/03`) can produce many small, shallow functions rather than genuinely improved structure.
- Handling fragments with multiple reassigned variables correctly requires more careful thought than the simple, single-return-value case, and can tempt a rushed, awkward extraction if not done carefully.
- Frequent extract/inline cycles, if not accompanied by immediate test runs (per `refactoring/03`), can accumulate several unverified changes before a bug is caught, undermining the safety the small-steps discipline is supposed to provide.

## Alternatives
- **IDE-automated extract/inline refactoring tools** — mechanize the procedure (correctly identifying parameters, return values, and updating call sites) far more reliably than doing it by hand, reducing the risk of a manual transcription error during the extraction itself.
- **Extract Class** (`refactoring/07`) — a coarser-grained alternative when the fragment being pulled out represents not just a function's worth of logic but a whole additional responsibility deserving its own class, not just its own method.
- **Leaving the code as-is** — appropriate when a function, while large, is already at one clear level of abstraction and further extraction would only shallow it (`philosophy-of-software-design/03`) rather than genuinely clarify it.

## When to use it
Use Extract Function whenever you can name a coherent fragment of a larger function clearly and concretely — that ability to name it well is itself a strong signal the extraction is worthwhile. Use Inline Function when a function's interface no longer earns its keep relative to just reading its (now simple) body directly.

## When NOT to use it
Don't extract a fragment purely to shorten a function's line count if the resulting function's interface isn't genuinely simpler than reading the fragment in place — that's exactly the shallow-module risk `philosophy-of-software-design/03` warns against. Don't inline a function whose name currently *does* meaningfully clarify intent, even if its body happens to be short — depth, not brevity, is the deciding factor in both directions.

## Self-check questions
1. Walk through extracting a function from a piece of your own code, following the five-step mechanical procedure, and note what became a parameter versus a return value.
2. Describe a case where a fragment reassigning multiple variables made extraction awkward, and how you resolved it (or would resolve it).
3. Give an example of a function you'd inline rather than keep separate, and explain using the depth criterion why inlining is the better call there.
4. Why are Extract Function and Inline Function useful as a pair for exploratory restructuring, not just as one-way fixes?

## References
- Refactoring: Improving the Design of Existing Code, 2nd ed. (Martin Fowler), Chapter 6: "A First Set of Refactorings" (Extract Function, Inline Function sections).
