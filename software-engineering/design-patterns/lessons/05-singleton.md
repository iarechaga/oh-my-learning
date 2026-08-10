---
id: design-patterns/05
subject: design-patterns
title: "Creational: Singleton (and Its Problems)"
slug: singleton
status: drafted
mastery:
seniority: junior
source: Design Patterns (Gamma, Helm, Johnson, Vlissides), Chapter 3
prerequisites: [design-patterns/03]
created: 2026-08-10
updated: 2026-08-10
---

# Creational: Singleton (and Its Problems)

## TL;DR
Singleton ensures a class has exactly one instance, globally accessible. It's the most widely known pattern in the catalog and also the most widely misused — it's frequently a disguised global variable, which reintroduces hidden coupling (`pragmatic-programmer/04`) and makes unit testing genuinely difficult, so modern practice generally prefers dependency injection of a single, explicitly-constructed instance over a Singleton that enforces its own uniqueness internally.

## The idea
Some things in a system genuinely should have exactly one instance — a single configuration object, a single connection pool, a single logging registry. Singleton solves this by having the class itself enforce and guard its own single-instance invariant, typically via a private constructor and a static `getInstance()` method that creates the instance on first call and returns the same one thereafter.

The reason this pattern earns a specifically skeptical treatment (unlike the other creational patterns, whose main risk is over-application) is that its most common real-world use isn't "there must genuinely be exactly one" — it's "I want easy global access to something from anywhere in the codebase," which is a different, much more dangerous motivation, because it reintroduces exactly the hidden global-state coupling that `pragmatic-programmer/04`'s orthogonality and `clean-code/11`'s construction/use separation both argue against.

## How it works

### The mechanics
```
class ConfigManager:
    _instance = None
    def __init__(self):
        if ConfigManager._instance is not None:
            raise RuntimeError("use get_instance()")
        self.settings = load_settings()
    @staticmethod
    def get_instance():
        if ConfigManager._instance is None:
            ConfigManager._instance = ConfigManager()
        return ConfigManager._instance
```
Any code, anywhere, can call `ConfigManager.get_instance()` and reach the same shared object, with no need to have it passed in explicitly.

### Why that "anywhere, no need to pass it in" convenience is actually the problem
Recall `clean-code/11`'s central argument: a class that constructs its own dependency internally, rather than receiving it, becomes hard to test in isolation and hides a real dependency from its own signature. `Singleton.get_instance()` calls scattered throughout a codebase are exactly this failure mode, just dressed up as a "pattern": any class calling `ConfigManager.get_instance()` internally has an invisible, untestable dependency on global state — you cannot substitute a fake `ConfigManager` for a unit test without either modifying the global singleton state directly (fragile, and unsafe under parallel test execution) or resorting to invasive monkey-patching.

**Worked example — the testing problem, concretely.** A `PaymentService` that internally calls `ConfigManager.get_instance().tax_rate` cannot be unit-tested with a different tax rate without either mutating the real global `ConfigManager` singleton before the test (which then risks leaking that mutated state into *other*, unrelated tests run in the same process — a violation of `clean-code/09`'s Independent F.I.R.S.T. property) or reaching for test-framework-specific monkey-patching tricks that are themselves fragile and implementation-coupled. Contrast with dependency injection (`clean-code/11`): `PaymentService(config: Config)` receiving its config explicitly can trivially be tested with any fake `Config` instance, with zero shared global state and zero risk of test pollution.

### The correct fix: keep "exactly one instance" as a fact, drop the global-access mechanism
The pattern's genuinely useful half — "there should be exactly one instance of this in the running application" — is entirely separable from its problematic half — "and any code, anywhere, can reach it via a global static call." Modern practice generally keeps the first half and discards the second: construct exactly one instance at the application's composition root (`clean-code/11`) and inject that single instance wherever it's needed, via constructor parameters, rather than via a static `getInstance()` call scattered through the codebase.
```
# composition root — constructed exactly once, exactly like a Singleton's invariant
config = Config(load_settings())

# every consumer receives it explicitly — testable, no hidden global dependency
payment_service = PaymentService(config)
notification_service = NotificationService(config)
```
This achieves the pattern's stated *intent* (exactly one instance) without its problematic *mechanism* (global, hidden access) — the single instance still exists exactly once, but every consumer's dependency on it is visible in its own constructor signature and trivially fakeable in tests.

### Singleton and concurrency
A subtler, additional problem: naive Singleton implementations (like the example above) are not thread-safe — two threads calling `get_instance()` simultaneously, both seeing `_instance is None`, can both proceed to construct a new instance, silently violating the pattern's core "exactly one" guarantee (a race condition, directly connecting to `pragmatic-programmer/11`'s temporal-coupling and shared-mutable-state concerns). Fixing this correctly requires careful locking around the lazy-initialization check, or eager initialization at module/class-load time instead of lazy first-call initialization — another reason the pattern is trickier to get fully right than its simple textbook form suggests.

## Pros
- Guarantees a genuine single-instance invariant when one is truly required (e.g., a hardware resource that can only have one owner).
- Provides convenient, no-plumbing-required access from anywhere in the codebase — the exact property that's also its biggest risk.
- The underlying "exactly one instance, constructed once" *intent* is legitimate and common; the pattern correctly identifies a real recurring need, even though its typical implementation mechanism is now considered problematic.

## Cons
- Global, hidden access reintroduces the orthogonality and testability problems `pragmatic-programmer/04` and `clean-code/11` specifically argue against.
- Naive implementations are not thread-safe without careful additional locking, and getting that locking right is a genuine source of subtle bugs.
- Once adopted, Singletons tend to accumulate more and more responsibilities over time (since they're so easy to reach from anywhere), becoming a magnet for exactly the low-cohesion, many-unrelated-responsibilities problem `clean-code/10` warns about.

## Alternatives
- **Dependency injection of a single, explicitly-constructed instance** (shown above) — achieves the same "exactly one instance" guarantee without global access; the generally preferred modern approach.
- **Module-level state** (in languages where modules are natively singletons, e.g., Python modules) — sometimes a simpler, more idiomatic way to get single-instance behavior for genuinely simple cases, though it shares some of Singleton's global-access testing concerns.
- **A DI container's "singleton scope"** — many dependency-injection frameworks explicitly support registering a dependency as "singleton-scoped" (constructed once, reused for every injection), giving you the pattern's benefit through the container's explicit configuration rather than through the class's own self-enforced mechanism.

## When to use it
Reserve genuine Singleton-style self-enforced uniqueness for cases with a real, structural reason only one instance can correctly exist (a hardware driver, a license manager enforcing a single active session) — and even then, prefer exposing it through dependency injection rather than a globally-called static method wherever possible.

## When NOT to use it
Don't reach for Singleton merely for the convenience of global access to something (a logger, a config object, a cache) that could just as easily be constructed once and passed down through dependency injection — that convenience is exactly the anti-pattern this lesson warns against, and it costs you testability and hidden coupling.

## Key takeaways / mental model
Separate the pattern's *intent* ("exactly one instance should exist") from its *mechanism* ("and it's globally, statically accessible from anywhere"). The intent is often legitimate; the mechanism is usually a testability and coupling liability better replaced by constructing one instance at your composition root and injecting it explicitly.

## Self-check questions
1. Explain, using the `PaymentService`/`ConfigManager` example, exactly why a class that internally calls a Singleton's `get_instance()` is hard to unit test.
2. Describe the thread-safety problem with a naive lazy-initialized Singleton, and name at least one way to fix it.
3. Give an example of a Singleton in code you've seen that accumulated unrelated responsibilities over time. How does that connect to `clean-code/10`'s cohesion argument?
4. Rewrite a Singleton-based dependency from your own code (or a hypothetical one) as a dependency-injected, composition-root-constructed instance instead.

## References
- Design Patterns: Elements of Reusable Object-Oriented Software (Gamma, Helm, Johnson, Vlissides), Chapter 3: "Creational Patterns" (Singleton section).
- See also: `clean-code/11` (Systems and Separating Construction from Use) for the dependency-injection alternative this lesson recommends.
