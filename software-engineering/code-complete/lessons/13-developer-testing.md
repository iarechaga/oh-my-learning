---
id: code-complete/13
subject: code-complete
title: Developer Testing
slug: developer-testing
status: drafted
mastery:
seniority: mid
source: Code Complete, 2nd ed. (Steve McConnell), Chapter 22
prerequisites: [pragmatic-programmer/13, clean-code/09]
created: 2026-08-10
updated: 2026-08-10
---

# Developer Testing

## TL;DR
The developer who wrote a piece of code is uniquely positioned (and responsible) to test it structurally — deliberately targeting boundary conditions, error paths, and each independent execution path (informed by `code-complete/11`'s complexity metric) — rather than only exercising the "obvious" happy-path cases a casual test would cover. Structural, coverage-aware testing by the author complements, but doesn't replace, independent QA and review.

## The idea
`pragmatic-programmer/13` established ruthless testing as a mindset, and `clean-code/09` gave the mechanics of what a clean test looks like. This chapter's specific contribution is about **coverage strategy**: given that you, the developer, know your own code's actual structure (every branch, every boundary, every error path), you're positioned to test it far more systematically than someone testing it purely from the outside, based only on the specification. Developer testing means deliberately using that structural knowledge to target the specific cases most likely to hide bugs — not just the cases that happen to occur to you first.

## How it works

### Boundary condition testing — the highest-value target
Empirically, bugs cluster disproportionately at **boundaries**: the first/last element of a collection, zero, the maximum allowed value, an empty input, the transition point of a conditional. McConnell's specific, practical checklist for boundary testing includes: the minimum and maximum valid values, one below the minimum and one above the maximum (to confirm the boundary is enforced, not just handled correctly *inside* it), zero, empty collections, single-element collections (a common special case distinct from both "empty" and "many"), and the first and last iterations of a loop specifically.

**Worked example.** Testing a function `get_page(items, page_number, page_size)` that paginates a list:
- Boundary cases to deliberately test, beyond an "obvious" middle-page happy-path case: `page_number = 0` or negative (invalid boundary — does it reject cleanly or misbehave?), the *last* valid page (does it return a correctly short, non-full final page?), an empty `items` list, a single-item `items` list, `page_size = 1`, and a `page_number` past the last valid page (does it return empty, or error, or something worse like an index-out-of-range crash?).
Testing only "page 2 of a 50-item list with page_size 10" (the obvious middle-case scenario) would miss every one of these boundary-clustered bugs, despite that happy-path test passing cleanly and potentially giving false confidence.

### Structural (white-box) coverage, informed by cyclomatic complexity
Because the developer knows the code's actual branching structure, they can specifically aim for coverage the specification alone wouldn't reveal is needed: **branch coverage** (has every `if`/`else` branch been exercised by some test?) and, more rigorously, **path coverage**, informed directly by `code-complete/11`'s cyclomatic complexity number — a routine with cyclomatic complexity 5 has (at minimum) 5 linearly independent paths, and a genuinely thorough developer test suite for that routine should have at least 5 test cases collectively exercising each one, a concrete, checkable target that a purely specification-driven (black-box) test approach has no way to derive, since it doesn't have visibility into the code's actual internal branching at all.

**Worked example.** Recall the `classify_order` routine from `code-complete/11` with cyclomatic complexity 5 (four decision points: `total > 1000`, `is_vip or rush` compound condition, `items_count == 0`, plus the implicit base path). A specification-only ("black-box") tester might test "a large VIP order" and "a normal order" — two cases, covering perhaps 2 of the 5 paths. A developer, seeing the actual code, knows to also test: a large *non*-VIP, non-rush order (exercises the `total > 1000` true / compound-condition false path), a rush order under the $1000 threshold (exercises the compound condition differently), and an empty order (exercises the `items_count == 0` path) — collectively exercising all 5 independent paths, something only possible because the developer can see the actual structure driving those paths.

### Test the error paths as deliberately as the success paths
Error-handling code (`clean-code/07`, `pragmatic-programmer/12`) is written to handle rare, unhappy circumstances — which is exactly why it's disproportionately likely to be under-tested and to itself contain bugs: it's exercised far less often in ad hoc manual testing than the happy path, so latent bugs in error-handling logic can persist unnoticed for a long time, right up until the rare failure condition actually occurs in production — at which point the error-handling code that was supposed to gracefully manage the failure might itself crash or behave incorrectly, compounding the original problem. Developer testing should deliberately construct the conditions needed to trigger each error path (a malformed input, a simulated network failure, a full disk) rather than leaving error paths to accidental, incidental coverage.

### Retest after every fix, and add a permanent regression test
Directly echoing `pragmatic-programmer/13`'s "every bug is a missing test" — once a bug is found (by any means), the developer testing discipline is: write a test that reproduces it first, confirm it fails, then fix, then confirm it passes, and keep that specific test in the suite permanently, so this exact class of regression can never silently reappear after a future, unrelated change.

## Pros
- Structural knowledge lets a developer target boundary and path coverage a black-box approach has no visibility to derive, catching a class of bugs specification-driven testing alone would miss.
- Deliberately testing error paths (rather than leaving them to incidental coverage) catches bugs in exactly the code most likely to matter during a real production incident.
- Using cyclomatic complexity as a concrete coverage target turns "did I test this thoroughly enough" into a checkable, quantified question rather than a vague feeling.

## Cons
- Because the developer wrote the code, they share the same blind spots that produced any bugs in the first place — developer testing alone cannot substitute for independent review (`code-complete/12`) or QA, which brings a genuinely different perspective.
- Exhaustive boundary and path coverage for every routine is a real time investment that must be weighed against a routine's actual risk/consequence — applying it uniformly everywhere, regardless of stakes, is disproportionate.
- Chasing 100% branch/path coverage as a number can produce tests that technically exercise every line without meaningfully verifying correct *behavior* (a coverage-gaming failure mode related to `pragmatic-programmer/13`'s point about mutation testing revealing weak assertions).

## Alternatives
- **Pure black-box (specification-based) testing** — tests derived solely from the spec/requirements, without looking at the implementation; catches different bugs (misunderstood requirements) than structural testing does, and is complementary rather than a substitute — see `software-quality/goos`, `software-quality/unit-testing` for deeper treatment.
- **Property-based testing** (`pragmatic-programmer/13`) — generates many inputs automatically to find edge cases, complementary to deliberately hand-targeted boundary tests, and sometimes finds boundary-adjacent cases a human wouldn't have thought to test manually.
- **Mutation testing** — measures whether existing tests would actually catch introduced bugs, directly addressing the "100% coverage but weak assertions" failure mode this lesson's structural-coverage approach can otherwise fall into.

## When to use it
Apply boundary-focused and structural-coverage-informed testing to any routine with real consequences if wrong, especially ones with several branches or a nontrivial cyclomatic complexity score. Deliberately construct and test error-path conditions for any code with meaningful error handling, rather than relying on incidental coverage.

## When NOT to use it
Don't chase exhaustive path coverage on trivial, low-complexity, low-consequence routines where the investment clearly exceeds the risk. Don't treat developer-written tests as sufficient on their own for anything genuinely high-stakes — pair them with independent review (`code-complete/12`) and, where warranted, independent QA, since shared blind spots are a real limitation of self-testing alone.

## Key takeaways / mental model
Use your own knowledge of the code's actual structure as an advantage: target the boundaries (min, max, zero, empty, one-past-the-end), aim for a number of test cases at least matching the routine's cyclomatic complexity, and deliberately trigger error paths rather than leaving them to chance. But remember that self-testing shares your own blind spots — pair it with review, not as a substitute for it.

## Self-check questions
1. Take a routine you've written and list its boundary conditions using McConnell's checklist (min, max, one-below, one-above, zero, empty, single-element). Which of these did your original tests actually cover?
2. Compute a routine's cyclomatic complexity and check how many of its independent paths your existing tests actually exercise.
3. Why are error-handling paths disproportionately likely to harbor undetected bugs, and what specific practice addresses that?
4. Why can't developer testing alone substitute for independent code review, even if the developer tests thoroughly?

## References
- Code Complete, 2nd ed. (Steve McConnell), Chapter 22: "Developer Testing".
- See also: `pragmatic-programmer/13` (Pragmatic Testing) and `code-complete/11` (cyclomatic complexity) for directly connected concepts.
