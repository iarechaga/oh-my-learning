---
id: clean-code/03
subject: clean-code
title: "Functions: Small, One Thing, One Level"
slug: functions
status: drafted
mastery:
seniority: junior
source: Clean Code (Robert C. Martin), Chapter 3
prerequisites: [clean-code/02]
created: 2026-08-10
updated: 2026-08-10
---

# Functions: Small, One Thing, One Level

## TL;DR
Functions should be small, do exactly one thing, and operate at a single level of abstraction — mixing "what to do" with "how to do it" in the same function is what makes functions hard to read, hard to test, and hard to safely change. Few, well-named arguments and no hidden side effects round out the discipline.

## The idea
A function is the smallest unit of "what does this code do" a reader has to understand at a time. If a function is small and does one clearly-nameable thing, a reader can understand it in isolation, trust its name, and move on without holding its internals in their head while reading the calling code. If a function is large and mixes several unrelated concerns, the reader is forced to load and track all of them simultaneously just to understand any one part — the exact cognitive overload this chapter is designed to prevent.

## How it works

### Small — really small
The book's guidance is aggressive by most engineers' initial instinct: functions should rarely exceed 20 lines, and functions of 4-6 lines are common in well-factored code. This isn't arbitrary — it's a direct consequence of "do one thing": a function that genuinely does only one thing, at one level of detail, is usually short simply because there isn't much to say about one thing.

**Worked example — before (does several things at once):**
```
def process_order(order):
    # validate
    if not order.items:
        raise ValueError("empty order")
    if order.total < 0:
        raise ValueError("negative total")
    # calculate discount
    discount = 0
    if order.customer.is_vip:
        discount = order.total * 0.1
    elif order.total > 100:
        discount = order.total * 0.05
    # persist
    order.total -= discount
    db.save(order)
    # notify
    email.send(order.customer.email, "Order confirmed", render_template(order))
```
This function does four unrelated things (validate, calculate discount, persist, notify), each at a different level of detail. **After:**
```
def process_order(order):
    validate_order(order)
    apply_discount(order)
    save_order(order)
    notify_customer(order)
```
Now `process_order` reads like a table of contents — one level of abstraction (the "what," delegated), with each "how" pushed down into its own named, independently readable and testable function.

### Do one thing
The test the book offers for "does this function do one thing": can you extract another function from it with a name that isn't just a restatement of part of the original name? If yes, it was doing more than one thing. Applied to the "before" example above: `process_order` clearly had four extractable sub-functions with genuinely distinct names (`validate_order`, `apply_discount`, `save_order`, `notify_customer`) — proof it wasn't doing "one thing," it was doing four things sequentially.

### One level of abstraction per function
Mixing high-level intent ("apply the discount") with low-level detail ("multiply total by 0.1") in the same function forces a reader to context-switch abstraction levels mid-read — jarring and error-prone, because it's easy to lose track of which level you're reading at. The **Stepdown Rule**: code should read top-to-bottom like a narrative, where each function is followed by the functions at the next level of detail it calls — `process_order` (top level) is immediately followed in the file by `validate_order`, `apply_discount`, etc. (next level down), which are themselves followed by whatever they call, and so on. A reader can stop reading at whatever depth answers their current question, without needing to jump around the file.

### Function arguments: fewer is better
The book's preference ordering, from best to worst: **zero arguments** (niladic) > **one argument** (monadic) > **two arguments** (dyadic) > **three arguments** (triadic) > more than three (avoid, wrap in an object instead). Each additional argument multiplies the number of cases a reader has to consider and the number of combinations tests must cover. A function with a boolean flag argument (`render(view, true)`) is a specific anti-pattern the book calls out: it's a signal the function actually does two different things depending on the flag, and should probably be two differently-named functions instead (`renderForPrint(view)` and `renderForScreen(view)`), which is more honest about the fact that two genuinely different behaviors exist.

**Worked example — flag argument smell:**
```
# Before: flag argument hides two behaviors behind one name
def create_file(name, is_temporary):
    if is_temporary:
        path = f"/tmp/{name}"
    else:
        path = f"/data/{name}"
    open(path, "w").close()

# After: two honestly-named functions
def create_temp_file(name):
    open(f"/tmp/{name}", "w").close()

def create_permanent_file(name):
    open(f"/data/{name}", "w").close()
```

### No hidden side effects
A function's name is a promise about what it does; a function that does something the name doesn't advertise (a `checkPassword()` that, on success, also silently initializes a user session as a side effect) violates that promise, and the surprise is exactly where bugs and misuse hide. If a function must have a side effect, its name should say so (`checkPasswordAndInitSession()`) — verbose, but honest, which the book explicitly prefers over short-but-misleading.

### Command-Query Separation
A function should either *do* something (a command, which may change state, and typically returns nothing meaningful) or *answer* something (a query, which returns a value and changes nothing) — not both. `setAndCheckAttribute(name, value)` conflates the two, producing ambiguous call sites like `if (setAttribute("username", "alice"))` that read as a question but are actually also performing a mutating command — genuinely unclear to a reader whether this is safe to call speculatively or not.

## Pros
- Small, single-purpose functions are independently readable, independently testable, and independently reusable.
- The Stepdown Rule turns a file into a top-to-bottom narrative a reader can stop reading at whatever depth answers their question.
- Fewer arguments and no hidden side effects reduce the combinatorial cases a reader (and a test suite) must consider.

## Cons
- Aggressively decomposing into many tiny functions can, if done carelessly, scatter related logic across many files/methods, making it harder to see the whole picture — this is the "jumping around" complaint sometimes leveled at extremely fragmented code.
- Extracting functions has a real naming cost (see `clean-code/02`) — every new function needs a genuinely good name, and a poorly-named extracted function is worse than the inline code it replaced.
- Very small functions can add a (usually negligible, but occasionally real in hot paths) call-overhead cost in some languages/runtimes.

## Alternatives
- **Comments to delineate sections within one large function** instead of extracting sub-functions — the book explicitly treats this as an inferior substitute (see `clean-code/04`): a comment marking "// --- validation ---" inside a large function is evidence that section should be its own function, not a permanent way to organize it.
- **Larger, coarser-grained functions with clear internal structure** — sometimes reasonable for performance-critical code where function-call overhead or inlining behavior genuinely matters, at the cost of the readability benefits above.
- **Object-oriented decomposition (splitting behavior across small classes/methods)** rather than pure functional decomposition — addresses the same "do one thing" goal at the class level (see `clean-code/10`), complementary to function-level decomposition rather than a true alternative to it.

## When to use it
Apply aggressively to any function you find yourself struggling to name clearly, or that mixes levels of detail — if you can't summarize what a function does in one clean sentence without using "and," it's doing more than one thing. Extract sub-functions whenever a natural, well-named boundary presents itself.

## When NOT to use it
Don't force decomposition onto a function that's already small, cohesive, and clearly named just to satisfy a line-count target — decomposition should track natural conceptual boundaries, not an arbitrary metric. In genuinely hot, performance-critical paths, weigh the readability benefit of extraction against measured call-overhead costs rather than applying the rule unconditionally.

## Key takeaways / mental model
Read a function and ask: "can I describe what this does in one short sentence with no 'and'?" If not, it's doing more than one thing — find the natural seam and extract it, give the extracted piece an honest name, and check whether the result reads top-to-bottom like a narrative (the Stepdown Rule).

## Self-check questions
1. Take a function from your own code that does more than one thing and decompose it, naming each extracted piece.
2. Explain what's wrong with a boolean flag argument, using a concrete example, and show the two-function alternative.
3. What is Command-Query Separation, and why does violating it produce ambiguous call sites?
4. Why does the book prefer a verbose-but-honest function name over a short-but-misleading one?

## References
- Clean Code: A Handbook of Agile Software Craftsmanship (Robert C. Martin), Chapter 3: "Functions".
