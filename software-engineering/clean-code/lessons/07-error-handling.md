---
id: clean-code/07
subject: clean-code
title: Error Handling Without Clutter
slug: error-handling
status: drafted
mastery:
seniority: mid
source: Clean Code (Robert C. Martin), Chapter 7
prerequisites: [pragmatic-programmer/12]
created: 2026-08-10
updated: 2026-08-10
---

# Error Handling Without Clutter

## TL;DR
Separate error-handling logic from the main logic path so both are readable on their own; prefer exceptions with real, specific context over returning error codes the caller might silently ignore; and never return or pass `null`, since it pushes a null-check burden onto every single caller, most of whom will eventually forget.

## The idea
Error handling is necessary, but the naive way most code handles it — interleaving `if (error) { ... }` checks throughout the "happy path" logic — makes it nearly impossible to read either concern clearly: the reader can't easily see what the function does when things go right, because that logic is scattered between error checks, and can't easily audit what happens when things go wrong, because those checks are scattered between normal logic. This chapter (building directly on `pragmatic-programmer/12`'s "decide an error strategy deliberately" theme) is about the *mechanics* of keeping these two concerns visually and structurally separate.

## How it works

### Use exceptions, not error codes, for the caller-facing contract
Returning an error code (`-1`, `null`, a status enum) forces every single caller to remember to check it — and, crucially, forgetting to check is silent: the code compiles, runs, and the bug lies dormant until the unchecked error condition actually occurs in production. An exception, by contrast, propagates automatically and *cannot* be silently ignored by an unaware caller — if nobody catches it, the program crashes loudly (echoing `pragmatic-programmer/09`'s "fail fast, fail loud"), which is a far better failure mode than silently continuing with an unchecked error state.

**Worked example — before (error code, silently ignorable):**
```
status = device.shutdown()
if status == DEVICE_SUSPENDED:
    log.info("suspended")
# caller forgets to check other status codes -> bug lies dormant
```
**After (exception, cannot be silently ignored):**
```
try:
    device.shutdown()
except DeviceSuspendedException:
    log.info("suspended")
except DeviceShutdownError as e:
    log.error(f"shutdown failed: {e}")
    raise
```

### Write the try-catch-finally block first, then fill in the happy path
A practical technique the book recommends: when writing a function that might fail, write the `try`/`catch`/`finally` skeleton *before* writing the logic inside the `try` block. This forces you to think about the failure boundary and cleanup semantics upfront, as a first-class design question, rather than retrofitting error handling after the happy-path logic is already written and error paths feel like an afterthought bolted on.

### Provide context with exceptions — a generic message is nearly useless
An exception without enough context (`raise Exception("failed")`) forces whoever's debugging it later to reconstruct, from scratch, what operation was being attempted, with what inputs, and why it failed — exactly the context that was available and cheap to capture at the moment of failure (echoing `pragmatic-programmer/12`'s "you're standing exactly where the problem occurred" argument). A good exception message states the operation attempted, the relevant input/state, and the reason: `raise PaymentDeclinedError(f"charge of {amount} {currency} declined by processor: {reason_code}")` is immediately actionable; `raise Exception("payment failed")` is not.

### Define exceptions by the caller's needs, not by the underlying library
When wrapping a third-party API or library call, don't let its specific exception types leak directly into your calling code — wrap them in your own exception types defined around how *your* callers will actually want to react. This decouples your codebase from a specific vendor's exception hierarchy (echoing `pragmatic-programmer/04`'s orthogonality) and lets you consolidate many different low-level failure types into fewer, more meaningfully-actionable categories for your own callers.

**Worked example.** A payment gateway SDK throws `GatewayTimeoutException`, `GatewayAuthError`, `GatewayRateLimitException`, and a dozen other specific types. Instead of letting all of these leak into application code (forcing every caller to know the vendor's entire exception taxonomy), wrap the SDK call and translate:
```
try:
    gateway_sdk.charge(amount)
except (GatewayTimeoutException, GatewayRateLimitException):
    raise RetryablePaymentError("temporary gateway issue, safe to retry")
except GatewayAuthError:
    raise PaymentConfigurationError("gateway credentials invalid, not retryable")
```
Now application code only needs to know about two meaningfully-different categories (`RetryablePaymentError` vs. `PaymentConfigurationError`), not the vendor's dozen-deep exception hierarchy — and if the vendor's SDK changes its exception types in a future version, only this one wrapping point needs updating.

### Don't return null, and don't pass null
Returning `null` from a function (e.g., `findUser(id)` returning `null` when not found) forces every caller to remember to null-check — and forgetting is one of the single most common sources of runtime crashes across virtually every mainstream language. The book's preferred alternatives: throw a specific exception (`UserNotFoundException`) when "not found" is genuinely an error in this context, or return a well-defined empty/special-case object (an empty list, an `Optional`/`Maybe` type, or a documented "null object" implementing the same interface with harmless no-op behavior) when "not found" is a legitimate, expected outcome the caller should handle explicitly rather than crash on. Passing `null` as an argument is treated even more harshly — it forces every function to defensively null-check every parameter, and a missed check produces a `NullPointerException`/`AttributeError` far from wherever the actual `null` originated, exactly the "lost context" failure this whole chapter is trying to prevent.

## Pros
- Separating error handling from main logic makes both independently readable and auditable.
- Exceptions with real context turn "something failed somewhere" into an immediately actionable diagnosis.
- Eliminating null returns and null arguments removes one of the most common categories of runtime crash entirely, by construction.

## Cons
- Designing a thoughtful, caller-oriented exception hierarchy (rather than just re-throwing whatever a library throws) takes real upfront design effort.
- Exceptions used for control flow in non-exceptional, frequent cases (rather than genuine errors) can hurt performance and readability — exceptions are best reserved for genuinely exceptional conditions, not routine branching.
- `Optional`/`Maybe`-style "no null" alternatives add syntactic overhead in languages without strong native support for them, and can be awkwardly retrofitted onto an existing null-heavy codebase.

## Alternatives
- **Result/Either types** (see `pragmatic-programmer/12`) — make success-or-specific-failure part of the return type itself, forcing callers to handle both cases at compile time; a stronger, more explicit alternative to exceptions in languages that support them well.
- **Error codes with mandatory-checking tooling** (e.g., linters that flag unchecked return values) — recover some of exceptions' "can't be silently ignored" safety without the runtime cost/complexity of exceptions, viable in languages/ecosystems with strong static analysis support.
- **Panics / unrecoverable crashes for programmer errors, distinct from recoverable errors** (Go's `panic`/`recover` split, or `pragmatic-programmer/09`'s assertions) — a language-level distinction between "this represents a bug, crash loudly" and "this is an expected, recoverable failure, handle it," which some ecosystems bake directly into the type system or language mechanics rather than leaving it to convention.

## When to use it
Use exceptions with rich context for genuinely exceptional, non-routine failures, especially ones crossing a boundary (a third-party call, an I/O operation) where you don't yet know what the caller will need to do. Wrap third-party exceptions into your own vocabulary whenever integrating an external library your callers shouldn't need to know the internals of.

## When NOT to use it
Don't use exceptions for routine, expected, high-frequency conditions where a normal return value (or a `Result`/`Optional` type) is clearer and cheaper — e.g., "item not found in a lookup that's expected to sometimes miss" is often better modeled as a `None`/`Optional` than an exception, since it's not exceptional, it's a normal outcome. Never return or accept `null` as a substitute for a properly-modeled "no result" case.

## Key takeaways / mental model
Ask, for every function that can fail: "if this fails, does the caller need to be forced to handle it (exception), or is this a normal, expected outcome they should check for explicitly (a return value / Optional)?" Whichever you choose, make sure the failure carries enough context that whoever encounters it later can act on it without having to reconstruct what you already knew at the moment it happened.

## Self-check questions
1. Rewrite a function you've seen that returns an error code into one that uses a specific, well-named exception instead. What does the caller's code look like before and after?
2. Why does wrapping a third-party library's exceptions in your own exception types matter, beyond just "cleaner code"?
3. Give an example of a `null` return that caused (or could cause) a real crash, and describe the alternative that would have prevented it.
4. When is throwing an exception the wrong choice, and a plain return value the right one? Give a concrete example.

## References
- Clean Code: A Handbook of Agile Software Craftsmanship (Robert C. Martin), Chapter 7: "Error Handling".
- See also: `pragmatic-programmer/12` (Transforming Programming and Error Handling) for the broader per-stage error-strategy framing this chapter's mechanics support.
