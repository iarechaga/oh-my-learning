---
id: code-complete/07
subject: code-complete
title: Using Variables and Data Effectively
slug: variables-and-data
status: drafted
mastery:
seniority: junior
source: Code Complete, 2nd ed. (Steve McConnell), Chapters 10-11
prerequisites: [code-complete/02]
created: 2026-08-10
updated: 2026-08-10
---

# Using Variables and Data Effectively

## TL;DR
Minimize a variable's scope and lifetime, initialize it as close as possible to first use, give each variable exactly one clear purpose, and prefer the most restrictive data representation that still fits the problem — every one of these reduces the mental bookkeeping (`code-complete/02`) a reader has to do to track what a variable currently holds and why.

## The idea
Variables are the most granular unit of state in a program, and every one of them is a small ongoing cognitive burden: as long as a variable is in scope, a reader has to track what it currently contains, whether that's still valid, and whether anything nearby might have changed it. This chapter's collection of guidance is unified by one goal — **minimize how long and how widely a variable's current value has to be tracked**, because every extra line of scope, every reused-for-a-different-purpose variable, and every "declared here but not initialized until forty lines later" pattern multiplies the reader's bookkeeping burden for no corresponding benefit.

## How it works

### Minimize scope and span
- **Scope**: the region of code where a variable is visible/accessible at all. Declare variables in the narrowest scope that actually needs them — a loop variable used only inside the loop body shouldn't be declared at function-top level "just in case," because that widens the region a reader must consider when asking "could this have been changed here?"
- **Span**: the number of lines between a variable's uses. A long span (declared on line 5, next used on line 80) forces a reader who reaches line 80 to scroll back and re-establish what the variable currently holds — directly the same problem `clean-code/05` raised about vertical distance in formatting, here applied specifically to variable lifetime.

**Worked example.** A function that computes several unrelated intermediate values, all declared at the top:
```
def process():
    total = 0
    user_count = 0
    error_log = []
    # ... 60 lines of unrelated setup and other logic ...
    for user in users:
        total += user.balance
    return total
```
`user_count` and `error_log` are declared but their actual first use is far away (or, worse, never — dead variables, a smell in their own right). Minimizing scope and span means declaring `total = 0` immediately before the loop that uses it, and not declaring `user_count`/`error_log` at all unless and until they're genuinely needed — reducing the live "things to track" set at every point in the function to only what's actually relevant right there.

### Initialize each variable close to its first use, not at the top out of habit
A common inherited habit (partly from older languages requiring declarations up front) is declaring and initializing all variables at the top of a function regardless of when they're actually used. This chapter argues against that habit specifically: initializing right before first use keeps the *declaration* and the *reason it exists* visually adjacent, so a reader encountering the initialization already has the context for why, without needing to separately recall a declaration seen much earlier.

### One variable, one purpose
Reusing a variable for two unrelated purposes at different points in a function (a classic pattern: `temp` used first to hold a user's name, then later reused to hold a computed total) forces a reader to track *which* meaning is currently active at any given line — an entirely avoidable, self-inflicted version of the cognitive-load problem, since introducing a second, distinctly-named variable costs nothing but immediately removes the ambiguity.

**Worked example — before (reused variable, ambiguous):**
```
temp = user.name.upper()
send_greeting(temp)
temp = calculate_total(order)  # same variable, now means something totally different
apply_discount(temp)
```
**After:**
```
greeting_name = user.name.upper()
send_greeting(greeting_name)
order_total = calculate_total(order)
apply_discount(order_total)
```
No functional difference, but a reader scanning the "after" version never has to ask "wait, what does this variable actually hold at this specific line" — each name's meaning is fixed for its entire (now separately scoped) lifetime.

### Prefer the most restrictive representation that fits
Choose the narrowest, most specific data type/representation that still captures the real domain constraint, rather than a broader, more permissive one "just in case." A `Percentage` value object constrained to 0-100 at construction communicates and enforces more than a bare `float` that could theoretically hold `-500` or `1e300`; an `enum` with exactly the valid statuses communicates and enforces more than a bare `string` that could theoretically hold any text. This connects directly to `code-complete/06`'s "validate once, trust the type thereafter" idea — a restrictive type is, in effect, validation baked permanently into the data's shape, rather than a check that has to be repeated at every use site.

### Avoid magic numbers and literals — name them
A bare `86400` in code communicates nothing about why that specific number matters; naming it `SECONDS_PER_DAY` (echoing `pragmatic-programmer/10`'s configuration-decoupling instinct, applied here to compile-time constants rather than runtime config) both documents intent and centralizes the value so a later correction (accounting for leap seconds, say) happens in exactly one place rather than requiring a search for every bare `86400` scattered through the codebase.

## Pros
- Minimizing scope and span directly reduces the "what does this currently hold" tracking burden a reader carries while reading any given line.
- One-purpose variables eliminate an entirely avoidable category of ambiguity and copy-paste-style bugs (accidentally relying on a stale value left over from the variable's earlier "meaning").
- Restrictive types/representations enforce domain constraints structurally, reducing how much validation logic needs to be repeated at every use site.

## Cons
- Minimizing scope aggressively can, in some cases, require slightly more verbose code (re-declaring similar-but-distinct variables in nested scopes rather than one shared outer declaration) — usually a worthwhile trade, but a real, non-zero cost.
- Introducing restrictive custom types for every value (a dedicated `Percentage` type instead of a bare `float`) adds real definitional overhead that isn't always proportionate for a value used in exactly one place, once, with no risk of misuse.
- Named constants for genuinely "obvious in context" literals (e.g., `0` as an initial counter value) can sometimes add more noise than clarity if applied indiscriminately to every literal in the codebase.

## Alternatives
- **Functional programming's preference for immutability over mutable variables entirely** — sidesteps much of this chapter's concern (tracking what a mutable variable "currently" holds) by making most values immutable once created, so there's no "currently holds" question to track at all — a stronger, different-paradigm answer to the same underlying cognitive-load problem.
- **Static analysis / linters flagging unused, over-scoped, or reused variables** — mechanically catch a meaningful subset of this chapter's concerns (unused variables, overly broad scope) without relying purely on manual discipline.
- **Const-by-default language features** (e.g., requiring `final`/`const`/`let` vs. `var` distinctions) — some modern languages bake "minimize mutability and reduce ambiguity about what a variable currently holds" directly into the language's default idioms, reducing reliance on this chapter's guidance as a purely manual discipline.

## When to use it
Apply scope/span minimization and one-variable-one-purpose discipline to every variable you write, by default — it's essentially free and has no real downside for typical application code. Reach for restrictive custom types specifically for values with genuine domain constraints that are used in more than one place or that cross a trust boundary (`code-complete/06`).

## When NOT to use it
Don't introduce a dedicated named type or constant for a truly one-off, self-evident literal used exactly once in an obvious context — that's ceremony without payoff. In performance-critical, tightly-scoped hot loops, weigh any representation choice against measured performance impact rather than applying "most restrictive representation" as an absolute rule regardless of cost.

## Key takeaways / mental model
For every variable, ask: "how narrow can I make its scope, how short can I make the distance between its declaration and its use, and does it hold exactly one clear meaning for its entire life?" Each "yes" directly shrinks what a reader has to track to understand any given line of code.

## Self-check questions
1. Find a variable in your own code with a long span (declared far from its uses) or reused for two different purposes. Rewrite it applying this lesson's guidance.
2. Why does declaring all variables at the top of a function (an old habit in some languages/styles) work against this chapter's goals, even when it "looks tidy"?
3. Give an example of a magic number or literal in code you've seen, and explain what naming it would communicate that the bare value didn't.
4. Describe a case where introducing a restrictive custom type (instead of a primitive) would have prevented a real bug you've encountered.

## References
- Code Complete, 2nd ed. (Steve McConnell), Chapter 10: "General Issues in Using Variables" and Chapter 11: "The Power of Variable Names" (data-representation portions).
