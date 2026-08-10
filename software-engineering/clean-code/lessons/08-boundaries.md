---
id: clean-code/08
subject: clean-code
title: Boundaries and Third-Party Code
slug: boundaries
status: drafted
mastery:
seniority: mid
source: Clean Code (Robert C. Martin), Chapter 8
prerequisites: [clean-code/07]
created: 2026-08-10
updated: 2026-08-10
---

# Boundaries and Third-Party Code

## TL;DR
Wrap third-party libraries and external systems behind an interface you control, sized to what you actually need — not the library's full surface area — so your codebase depends on your own stable abstraction instead of a vendor's evolving API. Write "learning tests" against a new library to both understand it and detect breaking changes in future versions automatically.

## The idea
Every codebase depends on code it doesn't own: a database driver, an HTTP client library, a cloud SDK, an open-source package. These boundaries are a special kind of risk, distinct from ordinary internal coupling (`pragmatic-programmer/04`): the library's maintainers can change its API on their own schedule, for their own reasons, with no obligation to your codebase — and if your code calls that library's specific types and methods directly, scattered across many files, a breaking change (or even just a desired upgrade) becomes a large, unpredictable, scattered refactor.

The chapter's core technique is to treat every third-party dependency the way `pragmatic-programmer/10` treats object structure: don't let external code's shape leak throughout your codebase — wrap it behind a narrow interface *you* define, sized to what your application actually needs, and let only that one wrapping layer know the vendor's specific types exist.

## How it works

### Don't pass boundary interfaces around directly — wrap them
Many libraries expose broad, general-purpose interfaces (a generic `Map`, a full-featured HTTP client with dozens of configuration options) designed for the library's *general* audience, not for your specific use case. Passing that broad interface around your own codebase means every consumer of it has access to far more surface area than they need, and every consumer is coupled to however the library chose to shape that broad interface.

**Worked example — before (library's `Map` leaks everywhere):**
```
def build_sensor_config() -> dict:
    config = {}
    config["threshold"] = 10
    config["unit"] = "celsius"
    return config

# elsewhere, far from where config was built:
config["threshhold"]  # typo silently returns None instead of a clear error
```
**After (narrow, purpose-built wrapper):**
```
class SensorConfig:
    def __init__(self, threshold: float, unit: str):
        self.threshold = threshold
        self.unit = unit

def build_sensor_config() -> SensorConfig:
    return SensorConfig(threshold=10, unit="celsius")

# elsewhere:
config.threshhold  # AttributeError, immediately and loudly, at the actual typo site
```
The wrapper converts a silent, general-purpose-`dict` typo bug into an immediate, loud failure (echoing `pragmatic-programmer/09`'s fail-fast principle) and, more importantly, gives you one place to control exactly what "sensor config" means in your domain, independent of whether the underlying storage is a `dict`, a database row, or a config file — none of your calling code needs to know or care.

### Learning tests — a two-for-one technique
When adopting a new third-party library, instead of reading documentation and immediately writing production code against it, write small, throwaway-style tests that exercise the library's API directly, checking that it behaves the way you *expect* it to. This has two distinct payoffs:
1. **Learning payoff**: writing a test forces precise, checkable understanding — "I believe calling `parse()` on malformed input raises `ParseError`, not returns `None`" is either confirmed or refuted immediately, rather than assumed from a skim of the docs.
2. **Regression-detection payoff**: keep these tests in your suite permanently. When you upgrade the library's version later, running the learning tests immediately tells you whether the library's *actual behavior* — not just its API signatures — has changed in a way that would break your assumptions, often long before that change would otherwise surface as a confusing production bug in your own, much larger integration.

**Worked example.** Adopting a new JSON schema validation library, write learning tests like:
```
def test_validator_rejects_missing_required_field():
    result = validator.validate({"name": "Alice"}, schema=USER_SCHEMA)
    assert result.is_valid is False
    assert "email" in result.errors  # confirms exact error shape, not just pass/fail

def test_validator_accepts_extra_unknown_fields_by_default():
    result = validator.validate({"name": "Alice", "email": "a@b.com", "extra": 1}, schema=USER_SCHEMA)
    assert result.is_valid is True  # confirms the library's default "additionalProperties" behavior
```
If a future version of the library changes its default handling of unknown fields (a common source of subtle breaking changes in validation libraries specifically), the second learning test fails immediately on upgrade, with a clear, specific message — rather than the change silently altering validation behavior somewhere deep in production months later.

### Boundaries with code that doesn't exist yet
The same wrapping discipline applies to code you're waiting on — a not-yet-built module, an API another team hasn't finished, a service still being designed. Define the interface *you* need first, write your code against that interface, and provide a temporary fake/stub implementation behind it — this both unblocks your own work and, once the real thing is ready, requires changing only the one implementation behind your interface, not every caller.

## Pros
- Wrapping third-party dependencies isolates the entire codebase from a vendor's API churn to a single, small, well-known point of contact.
- Learning tests convert "we assume the library does X" into a checked, automatically-re-verified fact, catching silent behavioral regressions on upgrade.
- Narrow, purpose-built wrapper types replace general-purpose library types (dicts, generic collections) with domain-appropriate, typo-safe, self-documenting ones.

## Cons
- Writing a wrapper for every third-party dependency is real, ongoing effort — over-applied to trivial, stable, rarely-changing dependencies, it's ceremony without corresponding payoff.
- Learning tests add to the test suite's maintenance surface, and need to be revisited (not just ignored) when they fail on a legitimate library upgrade, not silently deleted.
- A poorly-designed wrapper interface, sized wrong (too broad, mirroring the library too closely; or too narrow, missing something you'll need soon) undermines the whole benefit.

## Alternatives
- **Direct, unwrapped use of stable, foundational libraries** (a language's standard library, a decades-stable core dependency) — pragmatic when the dependency's API is extremely unlikely to break or change in ways that matter, making the wrapping overhead not worth it.
- **Adapter pattern** (see `software-engineering/design-patterns`) — the formal design-pattern name for exactly this wrapping technique, when you need to conform an external interface to one your own code already expects.
- **Vendored/forked dependencies** — for especially critical, hard-to-wrap dependencies, some teams vendor (copy into their own repo) or fork a library to fully control its evolution, trading the maintenance burden of a wrapper for the (larger) maintenance burden of owning a fork.

## When to use it
Wrap any third-party dependency whose API surface is broader than what you need, that you expect to evolve/version over the project's lifetime, or that's central enough that a breaking change would be costly if scattered across many call sites. Write learning tests when adopting any new library whose behavior (not just API shape) matters to correctness.

## When NOT to use it
Don't wrap a trivial, extremely stable dependency (e.g., a language's own standard-library string functions) purely for the sake of following this pattern — the abstraction has a real cost and no corresponding benefit there. Don't let learning tests substitute for your own integration tests against your actual usage — they test the library's behavior in isolation, not your code's correctness using it.

## Key takeaways / mental model
Ask, for every third-party dependency: "if this library's API changed tomorrow, how many places in my code would need to change?" If the honest answer is "more than one, and they're scattered," that's a boundary worth wrapping behind an interface sized to what you actually use — not the library's full surface.

## Self-check questions
1. Find a place in code you've written where a third-party type (a library's response object, a generic collection) is passed around directly. Sketch a narrow wrapper type that would isolate the rest of your code from it.
2. Explain the two distinct payoffs of a learning test, using a concrete example.
3. Why does wrapping a boundary help even for "just reading data" from a library, not only for calls with side effects?
4. Describe a situation where wrapping a dependency would be overkill, and explain why.

## References
- Clean Code: A Handbook of Agile Software Craftsmanship (Robert C. Martin), Chapter 8: "Boundaries".
