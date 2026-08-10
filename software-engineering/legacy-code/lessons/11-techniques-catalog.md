---
id: legacy-code/11
subject: legacy-code
title: Dependency-Breaking Techniques Catalog
slug: techniques-catalog
status: drafted
mastery:
seniority: senior
source: Working Effectively with Legacy Code (Michael C. Feathers), Chapter 25
prerequisites: [legacy-code/05, legacy-code/08]
created: 2026-08-10
updated: 2026-08-10
---

# Dependency-Breaking Techniques Catalog

## TL;DR
Beyond the core techniques already covered (Parameterize Constructor, Extract Interface, Subclass and Override), Feathers catalogs a fuller toolkit for specific, recurring dependency shapes: Extract and Override Call/Getter/Factory Method (isolate one problematic call inside a larger method), Replace Global Reference with Getter, and Introduce Static Setter (for breaking singleton/static dependencies specifically). Recognizing which specific dependency *shape* you're facing is what determines which named technique applies.

## The idea
`legacy-code/05` and `legacy-code/08` introduced the most common, broadly-applicable dependency-breaking techniques. This lesson rounds out the catalog with several more specific, narrower techniques, each shaped for a particular recurring situation Feathers observed repeatedly across real legacy codebases. The organizing principle throughout the whole catalog remains the same: identify the *precise shape* of the dependency blocking you, then reach for the technique built specifically for that shape, rather than a generic, one-size-fits-all fix.

## How it works

### Extract and Override Call — isolate one problematic call inside a larger method
When a method is otherwise fine to test, but contains one specific call to something untestable (a static method, a hard-to-construct object, a real I/O operation) buried in its middle, extract just that one call into its own small, overridable method, then use a test-specific subclass to override only that narrow seam — without touching or restructuring anything else in the original method.

**Worked example.**
```
# Before — one problematic call buried inside an otherwise-fine method
class PriceCalculator:
    def calculate(self, item):
        base = item.base_price
        tax_rate = TaxService.get_current_rate()   # static call, hard to control in a test
        return base * (1 + tax_rate)

# After — the problematic call extracted into its own overridable method
class PriceCalculator:
    def calculate(self, item):
        base = item.base_price
        tax_rate = self._get_tax_rate()             # now a seam
        return base * (1 + tax_rate)
    def _get_tax_rate(self):
        return TaxService.get_current_rate()

class TestablePriceCalculator(PriceCalculator):
    def _get_tax_rate(self):
        return 0.10   # fixed, controllable value for the test
```
This is a narrower, more surgical variant of `legacy-code/05`'s Subclass and Override — the extraction is scoped to exactly the one problematic call, leaving the rest of `calculate`'s logic completely untouched, minimizing the size and risk of the change needed to unblock a specific test.

### Extract and Override Factory Method / Getter — the same idea, for object creation
A close variant: when the problematic dependency is created via `new SomeClass(...)` (or equivalent) buried inside a method, extract that specific construction into its own overridable factory method, rather than the call being extracted in the general case above.
```
class ReportBuilder:
    def build(self, data):
        formatter = PdfFormatter()    # construction buried inline
        return formatter.format(data)

class ReportBuilder:
    def build(self, data):
        formatter = self._create_formatter()    # now a seam
        return formatter.format(data)
    def _create_formatter(self):
        return PdfFormatter()
```
The naming distinction (Extract and Override *Call* for a method invocation, *Factory Method* for object construction, *Getter* for retrieving a value/reference) helps communicate precisely what kind of seam is being introduced, even though the underlying mechanical technique (extract into an overridable method, override in a test subclass) is essentially the same pattern applied to slightly different situations.

### Replace Global Reference with Getter — a stepping stone toward breaking global dependencies
For the specific, especially thorny problem of a class reaching directly for a global variable or static field (`legacy-code/08`'s Reason 4), an intermediate, lower-risk step before a full dependency-injection redesign: wrap the global access in an instance method (a getter), so the class's *own* code now goes through one seam, even though that seam still, for now, reaches for the same global underneath.
```
# Step 1 — wrap the global access, changing nothing observable yet
class OrderService:
    def process(self, order):
        logger = self._get_logger()    # seam introduced, still reaches the global for now
        logger.log(f"processing {order.id}")
    def _get_logger(self):
        return GlobalLogger.instance()

# Step 2 (a separate, later step) — a test subclass can now override just the seam
class TestableOrderService(OrderService):
    def _get_logger(self):
        return FakeLogger()
```
This is deliberately incremental: Step 1 alone doesn't fully solve the global-dependency problem (production code still reaches for the same global underneath), but it's a small, safe, immediately-verifiable change that creates the seam needed for Step 2 to work — exactly the small-steps discipline `refactoring/01` and `legacy-code/07` both establish, applied here specifically to the hardest dependency-breaking case.

### Introduce Static Setter — a pragmatic, temporary tool for singleton-heavy code
For a singleton (`design-patterns/05`) that's deeply embedded and not yet ready for a full injection redesign, a static setter method lets a test *temporarily replace* the singleton's single instance for the duration of a test, then restore it afterward — an explicitly pragmatic, somewhat blunt tool Feathers presents as a bridge, not a permanent solution, given the shared-global-state risks it still carries (tests must carefully restore the original singleton afterward, or risk polluting subsequent tests — violating `clean-code/09`'s Independent property if done carelessly).

## Pros
- Extract and Override Call/Factory Method/Getter provide narrow, low-risk, highly targeted fixes for a single problematic dependency, without requiring a broader class redesign.
- Replace Global Reference with Getter provides a genuinely incremental, low-risk path toward eventually eliminating a global dependency, rather than requiring the full fix in one risky step.
- Naming each technique precisely for its specific situation (a call vs. a factory vs. a getter vs. a global) helps communicate exactly what kind of change is being made, aiding review and shared understanding.

## Cons
- Extract-and-Override techniques, applied repeatedly across many methods needing similar seams, can accumulate a proliferation of small overridable methods that, left unconsolidated, become their own minor source of clutter.
- Introduce Static Setter carries real shared-mutable-state risk if a test forgets to restore the original singleton afterward — a subtle, hard-to-diagnose source of test pollution if not handled with strict discipline (e.g., in a guaranteed teardown step).
- Replace Global Reference with Getter, if never followed up with an actual injection fix, can linger indefinitely as a half-measure — the global dependency isn't actually eliminated, just given one additional, mostly-cosmetic layer of indirection.

## Alternatives
- **A full dependency-injection redesign from the start** — resolves the underlying problem more completely than any of this lesson's narrower, incremental techniques, at a correspondingly higher upfront cost and risk for a single, urgent fix.
- **Test-framework-native mocking of static/global methods** (available in some languages/frameworks via bytecode manipulation or similar mechanisms) — sidesteps needing Extract and Override entirely, at the cost of more "magic," less portable, and sometimes slower test setup.
- **Accepting integration-level testing for globally-dependent code**, rather than isolating it at the unit level at all — a pragmatic concession for code where the global dependency is deeply pervasive and not worth the effort to isolate for unit testing specifically.

## When to use it
Use Extract and Override Call/Factory Method/Getter whenever a single, specific dependency buried inside an otherwise-fine method is the only thing blocking a test. Use Replace Global Reference with Getter as a first, incremental step toward eventually eliminating a global dependency. Use Introduce Static Setter as a pragmatic, carefully-guarded bridge for singleton-heavy code not yet ready for a full redesign.

## When NOT to use it
Don't rely on Introduce Static Setter without strict, guaranteed teardown discipline restoring the original singleton after every test — the shared-state pollution risk is real and can produce confusing, intermittent test failures elsewhere in the suite. Don't leave Replace Global Reference with Getter as a permanent "fix" if the global dependency is causing ongoing, recurring testing friction — treat it as a stepping stone toward the fuller fix, not the destination.

## Key takeaways / mental model
When a single, specific dependency (a call, a constructed object, a global reference) is blocking a test inside an otherwise-fine method or class, reach for the narrowest technique that isolates exactly that dependency — extract-and-override for a call or construction, a getter wrapper as a first step for globals, and a carefully-guarded static setter only as a temporary bridge for deeply-embedded singletons.

## Self-check questions
1. Using the `PriceCalculator` example, explain why extracting just the one problematic call is a narrower, lower-risk fix than a full class redesign.
2. Walk through the two-step Replace Global Reference with Getter technique, and explain why Step 1 alone doesn't fully solve the global-dependency problem.
3. What specific discipline is required to safely use Introduce Static Setter, and what happens if that discipline is skipped?
4. Given a method with three different problematic dependencies (a call, a global, and a hard-to-construct parameter), describe which techniques from this lesson and `legacy-code/05`/`legacy-code/08` you'd apply to each, and in what order.

## References
- Working Effectively with Legacy Code (Michael C. Feathers), Chapter 25: "Dependency-Breaking Techniques".
