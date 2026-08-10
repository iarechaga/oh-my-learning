---
id: legacy-code/02
subject: legacy-code
title: Seams and Enabling Points
slug: seams
status: drafted
mastery:
seniority: senior
source: Working Effectively with Legacy Code (Michael C. Feathers), Chapter 4
prerequisites: [legacy-code/01, design-patterns/01]
created: 2026-08-10
updated: 2026-08-10
---

# Seams and Enabling Points

## TL;DR
A seam is a place in the code where you can change behavior without editing the code at that exact spot — an "enabling point" you can use to substitute a fake/test double for a real dependency (a database, a network call, the system clock) for the purpose of a test, without modifying the code under test itself. Recognizing where seams exist (and don't yet exist) is the single most important skill for making legacy code testable.

## The idea
The change dilemma from `legacy-code/01` needs a resolution mechanism: how do you get a piece of untested code under test *without* rewriting it wholesale first (which itself would be an unverified, risky change)? Feathers' answer is the **seam** — a specific, precise term for any point in a program where you can alter behavior *without editing the source in that exact location*. If a seam exists at the right point, you can redirect a dependency (swap a real database call for a fake one, swap the real system clock for a controllable fake) purely by changing what's plugged in at the seam, leaving the code under test completely untouched.

## How it works

### The three kinds of seams
Feathers names three categories, each corresponding to a different mechanism for substitution:
- **Object seams** — the most common and most useful in object-oriented code: if a class receives its collaborators via a parameter, a constructor argument, or a settable property (rather than constructing/looking them up internally — directly `clean-code/11`'s construction/use separation), you can substitute a different, test-friendly implementation at that point without touching the class's own code. This is the primary seam most of this subject's dependency-breaking techniques (`legacy-code/05`, `legacy-code/11`) exist to *create* where one doesn't currently exist.
- **Link seams** — substitution at the level of how a program is linked/compiled/loaded (e.g., swapping which library or module implementation gets linked in at build time, or intercepting a specific import in a dynamic language). Less commonly used than object seams, but valuable for dependencies (like certain system calls) that are hard to substitute any other way.
- **Preprocessing seams** — substitution via preprocessor directives or conditional compilation in languages that support them (C/C++'s `#ifdef`), swapping in test-specific code paths at compile time. Rare in modern managed languages, but historically important, and worth recognizing when working in codebases that do use this mechanism.

### The enabling point — where the actual substitution decision is made
Every seam has an associated **enabling point**: the specific place in the code (or build configuration, or preprocessor setup) where you actually decide which implementation gets used — a constructor call site, a dependency-injection configuration, a `#define`. Identifying a seam without also identifying its enabling point is incomplete — the seam tells you substitution is *possible*; the enabling point tells you exactly *where* to make that substitution happen for a specific test.

**Worked example.**
```
class OrderProcessor:
    def __init__(self):
        self.payment_gateway = StripeGateway()   # constructed internally — NO seam here
    def process(self, order):
        self.payment_gateway.charge(order.total)
```
As written, `OrderProcessor` has no object seam at the point of `payment_gateway`'s creation — it's hardcoded, constructed internally (echoing `clean-code/11`'s exact anti-pattern). There is no enabling point for a test to substitute a fake gateway; the only "seam" available (if any) would be a much less desirable link/preprocessing-level trick, or actually hitting the real Stripe API in a test, which is exactly the situation `legacy-code/01`'s change dilemma describes.

```
class OrderProcessor:
    def __init__(self, payment_gateway):        # object seam: gateway passed in
        self.payment_gateway = payment_gateway
    def process(self, order):
        self.payment_gateway.charge(order.total)

# enabling point — a test can now substitute a fake here:
processor = OrderProcessor(payment_gateway=FakeGateway())
```
After this small change (a dependency-breaking technique, `legacy-code/05`), `OrderProcessor` has a genuine object seam at its constructor, and the enabling point is exactly that constructor call — a test can now substitute `FakeGateway()` and verify `OrderProcessor`'s behavior without ever touching the real Stripe API, without needing network access, and without the class's own internal logic being modified at all.

### Recognizing existing seams versus needing to create one
A crucial skill this lesson develops: before assuming you need to modify a class to make it testable, look carefully for a seam that *already* exists — sometimes a class already receives its dependencies via a parameter you hadn't noticed, or an existing virtual/overridable method provides an unintended but usable substitution point. Only once you've confirmed no usable seam currently exists should you reach for the dependency-breaking techniques in `legacy-code/05` and `legacy-code/11` to deliberately create one.

### Seams and the broader principle-of-interfaces connection
Recognizing that seams are valuable is, in a real sense, the retroactive, legacy-code-specific justification for `design-patterns/01`'s "program to an interface, not an implementation" and `clean-code/11`'s construction/use separation — code written with those principles in mind, from the start, naturally has object seams everywhere a future test might need one. Legacy code's characteristic lack of seams is, in this light, largely a direct, accumulated consequence of *not* having followed those principles when the code was originally written — this subject's techniques are the remedial fix, applied incrementally and safely, for a gap that earlier, better-informed design would have avoided in the first place.

## Pros
- Seams let you get a specific, targeted piece of code under test without needing to make the entire surrounding system testable first — a surgical, incremental solution to `legacy-code/01`'s change dilemma.
- Recognizing existing seams (rather than assuming none exist) can sometimes let you write a test with zero source changes at all, the lowest-risk possible starting point.
- The seam/enabling-point vocabulary gives a precise, shared way to discuss exactly where and how a substitution for testing purposes will happen, rather than a vague "we need to mock this somehow."

## Cons
- Not every dependency has a convenient, already-existing seam — many legacy codebases have systematically hardcoded, internally-constructed dependencies everywhere, requiring deliberate dependency-breaking work (`legacy-code/05`, `legacy-code/11`) before a seam becomes available at all.
- Link seams and preprocessing seams, while occasionally useful, are more fragile, less portable, and harder to reason about than object seams, and are generally a last resort rather than a first choice.
- Introducing a seam purely for testability (e.g., adding a constructor parameter that production code will always call with the same real implementation) is itself a small production-code change that needs its own care and verification, even though it doesn't change observable behavior.

## Alternatives
- **Testing against the real dependency directly** (a real database, a real payment gateway in a sandboxed test mode) — avoids needing a seam at all, at the cost of slower, less reliable (`clean-code/09`'s F.I.R.S.T. Repeatable/Fast properties), and sometimes unsafe (real API calls with real side effects) tests.
- **Monkey-patching / runtime metaprogramming substitution** (common in dynamic languages) — substitutes behavior at test time without requiring a formal object seam in the production code at all, at the cost of more fragile, implementation-coupled tests that can break in surprising ways if the patched code's internals change.
- **Dependency injection frameworks** — provide object seams systematically and consistently across an entire codebase via configuration, rather than requiring each individual class to be manually retrofitted with a seam one at a time.

## When to use it
Look for an existing seam (and its enabling point) as the very first step whenever you need to test a piece of code that currently depends on something hard to test directly (a database, an external service, global/shared state, the system clock). Only reach for dependency-breaking techniques to *create* a seam once you've confirmed none currently exists.

## When NOT to use it
Don't reach immediately for link seams or preprocessing tricks when a simple object seam (passing a dependency in rather than constructing it internally) would work just as well and is far easier to reason about and maintain. Don't introduce a seam purely for testability without verifying the change itself doesn't alter production behavior — even a "just add a parameter" change needs the same care as any other legacy-code modification.

## Key takeaways / mental model
Before touching any code to make it testable, ask: "is there already a point where I could substitute a fake for this dependency, without editing this exact code?" If yes, that's your seam — find its enabling point and use it. If no, you'll need to deliberately create one, using the techniques in `legacy-code/05` and `legacy-code/11`.

## Self-check questions
1. Using the `OrderProcessor` example, explain precisely why the original version has no usable seam, and what specific change created one.
2. What is the difference between a seam and its enabling point? Why does the book insist on both concepts rather than just one?
3. Describe the three kinds of seams (object, link, preprocessing) and explain why object seams are generally preferred in modern object-oriented code.
4. Find a piece of code in your own experience that lacked a needed seam. What would the minimal change to introduce one have looked like?

## References
- Working Effectively with Legacy Code (Michael C. Feathers), Chapter 4: "The Seam Model".
