---
id: pragmatic-programmer/12
subject: pragmatic-programmer
title: Transforming Programming and Error Handling
slug: transforming-programming
status: drafted
mastery:
seniority: mid
source: The Pragmatic Programmer (20th Anniversary ed., Hunt & Thomas), Chapter 7
prerequisites: [pragmatic-programmer/09]
created: 2026-08-10
updated: 2026-08-10
---

# Transforming Programming and Error Handling

## TL;DR
Think of a program as a pipeline of transformations — each function turns one representation of data into another, closer-to-the-goal representation — rather than as a pile of stateful procedures. Handle errors at the transformation boundary where they occur, deliberately deciding whether to crash, retry, or produce a well-defined "no result," instead of letting exceptions propagate wherever the language's default happens to take them.

## The idea
The book proposes a mental model shift: instead of picturing a program as "a sequence of steps that mutate state," picture it as **`f(g(h(input))) = output`** — a chain of transformations, where each stage takes a well-defined input shape and produces a well-defined output shape, ideally without hidden side effects. This isn't a purity mandate (real programs have I/O and side effects) — it's a lens for *design*: at each step, ask "what shape of data comes in, what shape goes out, and is this transformation doing one clear thing?"

Error handling falls naturally out of this lens: every transformation stage has to decide what happens when it *can't* produce a valid output for a given input. The book argues this decision should be made deliberately, at the point of the transformation, rather than left to whatever the language's default exception-propagation behavior happens to do — because a silently propagating exception, by the time it's caught (if it's caught at all), has lost the context needed to handle it meaningfully.

## How it works

### Programming as transformation
Break a task into named stages, each a pure(ish) transformation with a clear input and output type:
```
raw_csv_bytes -> parse_rows -> validate_rows -> normalize_fields -> persist_records
     (bytes)      (list[Row])   (list[ValidRow])  (list[Record])      (int count)
```
Each arrow is a transformation with a clear contract (see Lesson 09's Design by Contract): `parse_rows` promises to turn well-formed CSV bytes into a list of `Row`, and its precondition is roughly "bytes are valid UTF-8 text," while `validate_rows` promises to turn `Row`s into `ValidRow`s or explicitly signal which rows failed validation and why.

This decomposition makes it obvious, stage by stage, *where* errors can occur and *what kind* of error each stage can produce — malformed bytes at parsing, a business-rule violation at validation, a duplicate-key conflict at persistence — rather than one big function where "something went wrong" could mean any of a dozen unrelated things.

### Deciding how each stage should fail
For each transformation stage, the book pushes you to explicitly choose among a few deliberate error strategies, rather than defaulting to "let the exception bubble up":
1. **Crash immediately (fail fast)** — appropriate when the failure represents a broken *assumption* (see Lesson 09's assertions) that makes continuing meaningless or dangerous — e.g., a config file that's supposed to exist but doesn't.
2. **Return a well-defined "no result"** (a `null`, an `Optional`/`Maybe`, a tagged `Result` type, an empty list) — appropriate when "no valid output" is itself a legitimate, expected outcome the caller should handle explicitly — e.g., `find_user_by_email` returning `None` for an email that simply isn't registered.
3. **Retry, with a bound** — appropriate for failures expected to be transient (a network timeout, a momentarily locked resource) — but always with a maximum attempt count/backoff, never an unbounded retry loop.
4. **Propagate a typed, specific exception/error** — appropriate when the *caller*, not this stage, is in a better position to decide what to do, but only when the error carries enough specific context (what failed, with what input, why) for that caller to actually act on it meaningfully.

**Worked example.** In the CSV pipeline above:
- `parse_rows` on malformed bytes: **crash/typed exception** — malformed input at this stage usually means an upstream contract was violated (someone promised CSV and didn't deliver), and continuing would just push garbage further down the pipeline.
- `validate_rows` on a row missing a required field: **well-defined "no result," collected, not a crash** — return a `list[ValidRow]` alongside a separate `list[ValidationError]` describing exactly which rows failed and why, so the caller can report all errors to a user in one pass rather than crashing on the first bad row and hiding the rest.
- `persist_records` on a transient DB connection blip: **retry with a bound** (e.g., 3 attempts, exponential backoff) — because this failure class is expected to be transient, and a bounded retry meaningfully improves success rate without risking an infinite hang.

### Why "just let it throw" is usually the wrong default
Letting every error propagate as a generic, unhandled exception discards the single most valuable thing you have at the moment of failure: **you're standing exactly where the problem occurred, with full context about what was being attempted.** By the time a generic exception is caught several layers up (if it's caught at all), that context is gone — the catch block only knows "something threw," not which specific transformation failed on which specific input and why. Deciding the error strategy *at* the transformation, while that context is still available, produces far more actionable error messages and far more correct recovery behavior.

## Pros
- Decomposing into named transformations makes it obvious where and how each stage can fail, replacing vague "something broke" debugging with a precise, stage-by-stage error surface.
- Deliberate per-stage error strategy (crash / no-result / retry / propagate) produces error handling that matches the actual failure semantics, instead of one-size-fits-all exception bubbling.
- Collecting validation errors (rather than crashing on the first one) produces dramatically better user-facing feedback for anything processing multiple records/inputs.

## Cons
- Explicitly choosing an error strategy per stage is more upfront design work than reflexively `try/catch`-wrapping a whole function and moving on.
- Overusing "no result" values (nulls, empty collections) instead of surfacing genuine errors can silently hide real problems as if they were normal, absent-but-fine outcomes.
- Retry-with-backoff logic, done carelessly, can itself cause cascading load problems (e.g., synchronized retry storms across many clients) if not designed with jitter and circuit breakers in mind.

## Alternatives
- **Result/Either types (functional error handling)** — make the "success or specific failure" outcome part of the function's return type itself (`Result<ValidRow, ValidationError>`), forcing callers to handle both cases at compile time rather than relying on documentation or convention.
- **Global exception handlers / centralized error middleware** — catch broadly at a system boundary (e.g., an HTTP framework's top-level error handler) for *presentation* concerns (turning any uncaught error into a generic 500 response), while still handling business-meaningful errors deliberately at the point they occur — the two approaches are complementary, not exclusive.
- **Circuit breakers** (see `architecture/system-design` and `building-microservices`) — a more sophisticated retry-adjacent pattern for distributed calls, which stops retrying a downstream dependency altogether once it's clearly unhealthy, rather than retrying indefinitely and adding load to a struggling system.

## When to use it
Use the transformation lens when designing any multi-step data-processing pipeline, to force explicit thinking about each stage's input/output contract and failure modes. Decide error strategy deliberately, per stage, especially in code that processes external or user-supplied input, where multiple distinct failure classes are likely.

## When NOT to use it
Don't force a rigid transformation-pipeline shape onto genuinely stateful, interactive logic (a UI event handler, a long-lived stateful connection) where "input in, output out" isn't a natural fit — the lens is most valuable for data-processing-shaped code, not everything.

## Key takeaways / mental model
Ask of every function: "what's the input shape, what's the output shape, and what happens when I can't produce a valid output?" Answer the third question deliberately and specifically for each stage — crash, no-result, retry-bounded, or propagate-with-context — rather than letting a language default decide it for you.

## Self-check questions
1. Decompose a task you've recently worked on into a chain of named transformations with explicit input/output shapes.
2. For each of the four error strategies (crash, no-result, retry, propagate), give a real example from your own code where that strategy was the right (or wrong) choice.
3. Why does collecting all validation errors in one pass usually beat crashing on the first invalid record?
4. Explain why letting an error propagate as a generic exception "loses context," using a specific example.

## References
- The Pragmatic Programmer, 20th Anniversary Edition (David Thomas & Andrew Hunt), Chapter 7: "While You Are Coding" (Transforming Programming section).
