---
id: legacy-code/09
subject: legacy-code
title: I Can't Run a Method in a Test Harness
slug: method-into-harness
status: drafted
mastery:
seniority: senior
source: Working Effectively with Legacy Code (Michael C. Feathers), Chapter 9
prerequisites: [legacy-code/08]
created: 2026-08-10
updated: 2026-08-10
---

# I Can't Run a Method in a Test Harness

## TL;DR
Even once a class can be constructed in a test (`legacy-code/08`), a *specific method* on it can still resist testing for its own, narrower set of reasons — it's private and inaccessible, it depends on protected state only set up through a complex sequence of other calls, or it reads/writes a resource (a file, a static field) the test can't control. Extract Method (to isolate the untestable part) and Expose Method (carefully, and only when justified) are the two primary responses.

## The idea
`legacy-code/08` addressed construction-level obstacles; this lesson addresses obstacles specific to a single *method* once the class itself is already constructible. A method can be perfectly reasonable to call, but still resist being exercised meaningfully in a test for reasons distinct from anything about the class's constructor — visibility restrictions, complex setup preconditions, or hidden resource dependencies internal to that one method's body.

## How it works

### Obstacle 1: the method is private, and you don't want to (or can't) make it public
Private methods encode a legitimate design decision (`clean-code/06`'s encapsulation, `philosophy-of-software-design/04`'s information hiding) — they're private because they're implementation details the class's own public interface doesn't want to expose. But sometimes a specific piece of logic buried inside a private method genuinely needs its own focused test, distinct from testing it only indirectly through whatever public method happens to call it.

**The disciplined response — extract, don't just expose.** Rather than reflexively making the private method public (which leaks the implementation detail to every caller, not just the test — a real design cost, echoing `philosophy-of-software-design/04`'s leakage concept), first ask whether the private logic is complex enough to deserve its own genuinely separate concept. If yes, **Extract Class** (`refactoring/06`) to give that logic its own small, focused class with a naturally public interface — the extraction is justified by the logic's genuine complexity and testability need, not merely by the desire to bypass a visibility modifier. If the logic is simple enough that testing it only indirectly, through the containing class's public interface, is genuinely adequate, leave it private and test it that way — not every private method needs its own isolated test.

### Obstacle 2: the method depends on complex internal state set up through many other calls
A method might be public and simple to call syntactically, but only produce meaningful, correct behavior after a specific, complex sequence of other calls has already configured the object's internal state correctly — making it hard to set up a test in a reasonable number of lines without essentially reimplementing that whole setup sequence.

**The response — a test-specific factory or builder method.** Rather than duplicating the complex setup sequence in every test, extract it into a single, reusable, well-named test helper (echoing `design-patterns/04`'s Builder pattern, applied here specifically to test setup) that constructs an object already in the specific state needed, in one call — `create_order_ready_for_shipping()` rather than five lines of setup repeated across every test that needs an order in that state.

### Obstacle 3: the method reads or writes a resource the test can't control
A method that reads a static/global field, writes to a real file, or depends on some other resource outside the test's direct control resists testing for the same underlying reason `legacy-code/04`'s separation problem describes, now specifically localized to one method rather than a whole class's construction.

**The response — apply `legacy-code/05`'s dependency-breaking techniques, scoped to just this method's specific resource dependency**, most commonly Parameterize Constructor (if the resource can be injected at the class level) or, for a narrower, method-specific fix, extracting the resource access into its own small, overridable method that a test-specific subclass (echoing `legacy-code/05`'s Subclass and Override) can substitute.

**Worked example — combining Extract Method with a testing seam.**
```
# Before — a private method with a hard-to-test resource dependency, buried inside a public one
class InventoryManager:
    def restock(self, item, quantity):
        current_time = datetime.now()                # untestable, non-repeatable
        self._log_restock(item, quantity, current_time)
        self._update_count(item, quantity)

    def _log_restock(self, item, quantity, timestamp):
        with open("/var/log/restock.log", "a") as f:   # real file I/O, buried in a private method
            f.write(f"{timestamp}: restocked {quantity} of {item}")

# After — the resource-dependent logic is isolated into its own overridable method
class InventoryManager:
    def restock(self, item, quantity):
        self._log_restock(item, quantity, self._current_time())
        self._update_count(item, quantity)

    def _current_time(self):
        return datetime.now()

    def _log_restock(self, item, quantity, timestamp):
        with open(self._log_path(), "a") as f:
            f.write(f"{timestamp}: restocked {quantity} of {item}")

    def _log_path(self):
        return "/var/log/restock.log"

# test — a subclass overrides just the resource-touching seams
class TestableInventoryManager(InventoryManager):
    def _current_time(self): return datetime(2026, 1, 1)
    def _log_path(self): return "/tmp/test-restock.log"
```
The resource dependencies (`datetime.now()`, the hardcoded file path) are extracted into their own small, overridable methods — a targeted application of `legacy-code/05`'s Subclass and Override, specifically scoped to the resource dependencies rather than requiring a broader class redesign — leaving `restock`'s core logic (`_update_count`, the overall sequencing) genuinely testable without touching a real file or depending on the real current time.

## Pros
- Distinguishing between "extract the logic" and "just expose the private method" preserves genuine encapsulation while still enabling focused testing where it's actually warranted.
- Test-specific factory/builder helpers eliminate repetitive, error-prone setup duplication across many tests needing the same complex initial state.
- Method-scoped resource-dependency extraction (as in the worked example) is a smaller, less invasive fix than a whole-class redesign, appropriate when the problem is genuinely localized to one method.

## Cons
- Deciding whether private logic is "complex enough to deserve extraction" versus "simple enough to test only indirectly" requires judgment, and erring toward extracting everything can produce excessive, low-value class fragmentation.
- Test-specific factory/builder helpers need their own maintenance as the class's setup requirements evolve, and can silently drift out of sync with real production initialization sequences if not kept in check.
- Method-scoped Subclass-and-Override fixes, like the class-level version (`legacy-code/05`), are best treated as an incremental bridge rather than a permanent solution if the resource-dependency problem turns out to be pervasive across many methods.

## Alternatives
- **Reflection-based testing frameworks** (invoking private methods directly via language reflection APIs, bypassing visibility restrictions entirely) — avoids any production-code change, at the cost of tests tightly coupled to private implementation details that can break on any internal refactor, exactly the fragility `refactoring/03` warns against for tests.
- **Testing only through the public interface, accepting indirect coverage of private logic** — the simplest, least invasive option, appropriate when private logic genuinely isn't complex enough to warrant its own isolated test.
- **A full class-level dependency-injection redesign** (`legacy-code/08`) — resolves method-level resource dependencies as a side effect of a more thorough class-level fix, appropriate once several methods on the same class share the same underlying resource-dependency problem.

## When to use it
Extract private logic into its own class specifically when it's complex enough to warrant independent, focused testing — not merely to bypass a visibility modifier. Use test-specific factory/builder helpers whenever multiple tests need the same complex setup sequence. Extract resource dependencies into overridable seams when a specific method's (not the whole class's) resource access is what's blocking a test.

## When NOT to use it
Don't make a private method public purely to test it directly if testing it indirectly through the class's actual public interface already provides adequate coverage — that's leaking an implementation detail (`philosophy-of-software-design/04`) for no real testing benefit. Don't duplicate complex setup logic across many individual tests when a single, shared test helper would be clearer and easier to maintain.

## Key takeaways / mental model
When a specific method resists testing, ask: "is this a visibility problem, a setup-complexity problem, or a resource-dependency problem?" Each has its own matched fix — extract the logic (if it's genuinely complex) rather than just exposing it, build a shared test helper for complex setup, or extract just the resource-touching parts into overridable seams.

## Self-check questions
1. Using the `InventoryManager` example, explain exactly which two resource dependencies were isolated, and why isolating them (rather than the whole class) was the proportionate fix.
2. Describe a situation where making a private method public would be the wrong fix, and what extracting it into its own class would look like instead.
3. Why does the book recommend a shared test-specific factory/builder for complex setup, rather than duplicating the setup in each test?
4. Give an example from your own experience of a method that resisted testing for one of this lesson's three obstacles, and identify which one it was.

## References
- Working Effectively with Legacy Code (Michael C. Feathers), Chapter 9: "I Can't Get This Class into a Test Harness" (method-level obstacles section).
