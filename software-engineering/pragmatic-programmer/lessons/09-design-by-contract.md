---
id: pragmatic-programmer/09
subject: pragmatic-programmer
title: Design by Contract and Assertive Programming
slug: design-by-contract
status: drafted
mastery:
seniority: mid
source: The Pragmatic Programmer (20th Anniversary ed., Hunt & Thomas), Chapter 4
prerequisites: [pragmatic-programmer/04]
created: 2026-08-10
updated: 2026-08-10
---

# Design by Contract and Assertive Programming

## TL;DR
Design by Contract makes a function's obligations explicit and checkable: preconditions (what the caller must guarantee), postconditions (what the function guarantees in return), and invariants (what must always hold). Assertive programming applies the same rigor informally, with `assert` statements that crash loudly the instant an assumption is violated — because a program that fails fast and visibly is far easier to fix than one that limps on with corrupted state.

## The idea
Most bugs that are expensive to diagnose share a common shape: something went wrong far upstream of where it was finally *noticed*. A function received a negative number it should never receive, silently produced garbage, and three function calls later some *other* piece of code crashed — the crash site lies, pointing you at innocent code while the guilty code runs clean.

Design by Contract (DbC), a concept from Bertrand Meyer's Eiffel language, treats every function as a formal contract between caller and callee: the caller promises certain things are true before calling (preconditions), and in exchange the function promises certain things will be true when it returns (postconditions) — and some conditions (invariants) must hold true at every stable point regardless. Making these explicit — in a real DbC-supporting language, or via disciplined `assert` statements in languages without native support — converts silent violations into loud, immediate, precisely-located failures.

## How it works

### The three parts of a contract
- **Preconditions**: what must be true of the *inputs* for the function to behave correctly. Example: "withdraw(amount) requires amount > 0 and amount <= current_balance."
- **Postconditions**: what the function *guarantees* is true when it returns, given the preconditions held. Example: "withdraw(amount) ensures new_balance == old_balance - amount, and new_balance >= 0."
- **Invariants**: conditions that must hold true before and after every operation on an object, describing its "always valid" state. Example: for a bank account class, "balance is always >= 0" (assuming no overdraft) is a class invariant, checked after every method that touches balance.

### Whose fault is it? — the point of a contract
A contract's real power is answering "whose bug is this?" instantly. If a precondition is violated, it's the **caller's** bug — they broke their side of the deal, and the callee is not obligated to produce a sensible result (and shouldn't try to guess one). If a postcondition is violated despite valid inputs, it's the **callee's** bug — its implementation is wrong. This eliminates an entire category of debugging ambiguity ("is this my bug or theirs?") by making the boundary of responsibility explicit and mechanically checkable, rather than a matter of after-the-fact argument.

**Worked example.** `sqrt(x)` with precondition `x >= 0` and postcondition `result * result` is approximately `x`, `result >= 0`.
- Caller passes `x = -4`. Precondition violated. This is unambiguously the *caller's* bug — the function is allowed to fail loudly (assert/throw) rather than return `NaN` silently or guess.
- Caller passes `x = 4`, function returns `-2`. Precondition was fine; postcondition failed (`-2 >= 0` is false). This is unambiguously the *implementation's* bug.
- Without contracts, both failures might just manifest later as "some downstream calculation is wrong" with no signal about which side of the `sqrt` call introduced the problem.

### Assertive programming — the practical, language-agnostic version
Few mainstream languages have first-class DbC syntax (Eiffel is the notable exception). The pragmatic substitute: **use `assert` statements liberally to encode the contract you'd otherwise only be hoping is true.**

```
def withdraw(self, amount):
    assert amount > 0, "withdraw amount must be positive"
    assert amount <= self.balance, "insufficient funds"
    old_balance = self.balance
    self.balance -= amount
    assert self.balance == old_balance - amount   # postcondition
    assert self.balance >= 0                        # invariant
    return self.balance
```

If any assertion fails, the program crashes *immediately, at the exact line where the assumption broke* — not three calls later in unrelated code. This is the "fail fast, fail loud" principle in concrete form: a crashed program with a precise stack trace pointing at the exact violated assumption is dramatically cheaper to fix than a program that silently continues with corrupted state and fails somewhere unrelated, much later.

### A crucial rule: never rely on assertions having side effects, and never disable them silently in production without a plan
Two disciplines the book stresses:
1. **Assertions should be side-effect-free checks, not load-bearing logic.** `assert queue.pop() is not None` is dangerous — if assertions are stripped in production builds (common in many languages/runtimes for performance), you've silently deleted a `pop()` call the program depends on. Keep the check and the action separate.
2. **Don't use assertions as a substitute for real error handling of expected conditions.** A user submitting an invalid form isn't a broken contract — it's an expected, recoverable input that needs proper validation and a user-facing error message, not a crash. Assertions are for conditions that *should be impossible if the code is correct* — genuine bugs, not expected bad input from the outside world.

## Pros
- Converts silent, far-from-the-cause bugs into loud, precisely-located failures at the moment the real assumption breaks.
- Makes responsibility for a bug ("caller's fault" vs. "callee's fault") mechanically clear instead of debatable.
- Documents a function's real behavioral guarantees in a checkable, always-up-to-date way — contracts can't silently drift out of sync with the code the way a comment can, because they're actually executed.

## Cons
- Assertions add runtime overhead, which matters in hot paths (though usually negligible relative to the debugging time saved).
- Overusing assertions for expected, recoverable conditions (bad user input, expected network failures) produces crashes where graceful error handling was the right call.
- Contracts on complex objects (deep invariants across large object graphs) can become expensive or genuinely hard to express precisely, limiting how far the discipline scales without real DbC language support.

## Alternatives
- **Type systems (especially strong/static typing)** — enforce a subset of what preconditions/postconditions would check (argument shapes, nullability) at compile time, for free, without runtime cost — but can't express richer behavioral contracts ("amount must be <= balance") that depend on runtime values.
- **Exception-based validation** — throw a typed, catchable exception for invalid input instead of asserting, appropriate specifically for *expected* failure conditions (see the "don't assert on bad user input" caution above) rather than internal-consistency bugs.
- **Property-based testing** (Lesson 13) — instead of checking contracts at runtime in production, generate many random inputs at test time and check the same pre/postcondition-style properties hold, catching violations before shipping rather than in the field.

## When to use it
Use assertions liberally for conditions that represent "if this is false, my code has a bug" — internal invariants, function preconditions on values already validated elsewhere, postconditions on your own logic. Use them especially at trust boundaries between components you don't fully control (a third-party library's return value, a config value loaded from disk) where a wrong assumption would otherwise propagate silently.

## When NOT to use it
Don't assert on conditions that represent expected, recoverable real-world input — use proper validation and error handling there instead, reserving crashes for genuine internal-logic bugs. Don't rely on an assertion's side effects, since assertions may be compiled/stripped out entirely in some production configurations.

## Key takeaways / mental model
Ask of every function: "what do I need to be true for this to work, and what do I promise is true when it's done?" Then make both checkable — formally via DbC syntax where the language supports it, or informally via `assert` everywhere else — so a broken assumption crashes loudly at its source instead of corrupting state silently and surfacing as a mystery three calls downstream.

## Self-check questions
1. Explain, using the `sqrt` example's structure, how contracts make it mechanically clear whose bug a given failure is.
2. Why is it dangerous to write `assert x = compute_and_cache(y)` if the assertion has the side effect of populating a cache the rest of the program depends on?
3. Give an example of a condition that should be handled with a normal error/exception rather than an assertion, and explain why asserting on it would be wrong.
4. Describe a bug you've encountered where the failure surfaced far from its actual cause. Where would a precondition or postcondition assertion have caught it earlier?

## References
- The Pragmatic Programmer, 20th Anniversary Edition (David Thomas & Andrew Hunt), Chapter 4: "Pragmatic Paranoia" (Design by Contract and Assertive Programming sections).
- Bertrand Meyer, "Object-Oriented Software Construction" (origin of Design by Contract in Eiffel).
