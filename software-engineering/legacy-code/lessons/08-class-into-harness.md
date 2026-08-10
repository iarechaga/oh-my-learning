---
id: legacy-code/08
subject: legacy-code
title: I Can't Get This Class into a Test Harness
slug: class-into-harness
status: drafted
mastery:
seniority: senior
source: Working Effectively with Legacy Code (Michael C. Feathers), Chapter 9
prerequisites: [legacy-code/05]
created: 2026-08-10
updated: 2026-08-10
---

# I Can't Get This Class into a Test Harness

## TL;DR
Four specific, recurring reasons make a class impossible to construct directly in a test — untestable constructor side effects, constructor parameters that are themselves hard to construct, undesirable side effects from construction (real I/O, real network calls), and required global/singleton state — each with its own specific, named technique from this subject's toolkit rather than a single generic fix.

## The idea
This lesson names the single most common concrete complaint developers voice about legacy code — "I literally cannot even *construct* an instance of this class in a test" — and breaks it into the four specific, distinguishable reasons Feathers observes recurring across real codebases. Naming the specific reason is what determines which of `legacy-code/05`'s toolkit techniques (or others already covered) is the right fix, rather than flailing at a generic "make it testable" goal.

## How it works

### Reason 1: the constructor itself does too much
A constructor that does real work beyond simple field assignment — opening a database connection, reading a config file, starting a background thread — makes construction itself expensive, slow, or side-effect-laden, exactly the kind of cost `clean-code/09`'s F.I.R.S.T. properties (Fast, Repeatable) warn against for tests.

**Fix**: extract the problematic work out of the constructor into a separate method (an explicit `initialize()` or `connect()` call, invoked by production code right after construction, but skippable in a test) — this is a variant of `refactoring/05`'s Extract Function applied specifically to constructor bodies, and directly resolves the construction-cost problem without needing a deeper redesign.

### Reason 2: constructor parameters are themselves hard to construct
Sometimes the class itself is fine, but one of its required constructor parameters is a large, complex, hard-to-build object (which might, recursively, have its own construction problems) — making it hard to even *call* the constructor in a test, independent of anything the class under test itself does.

**Fix**: Extract Interface (`legacy-code/05`) for that parameter's type, so a test can pass a minimal fake implementing just the needed interface, rather than needing to construct the real, complex concrete object at all.

### Reason 3: construction has undesirable side effects
Even if the constructor itself is simple, it might *require* an argument that, when used, triggers a real, undesired side effect (a real payment gateway client that, merely by being constructed with real credentials, might attempt an authentication handshake against a live server) — this is a **separation** problem, exactly in `legacy-code/04`'s sense.

**Fix**: Parameterize Constructor (`legacy-code/05`) to accept a fake/test-double implementation instead of the real, side-effect-triggering one.

### Reason 4: the class depends on hard-to-control global or singleton state
If a class reaches out, internally, to a global variable, a static singleton (`design-patterns/05`'s specific testability critique), or ambient shared state, you can't isolate a single instance's behavior in a test without also controlling that global state — and worse, tests can silently interfere with each other if they share and mutate the same global state (violating `clean-code/09`'s Independent F.I.R.S.T. property).

**Fix**: this is the hardest case in the list, and often requires the most invasive change — converting the global/singleton access into an injected dependency (echoing `design-patterns/05`'s recommended remedy directly), which may itself require first applying Reason 1-3's techniques to the global object's own construction before it can be cleanly injected.

**Worked example — combining several of these in one realistic case.**
```
# A class combining constructor side effects (Reason 1), a real dependency
# with side effects (Reason 3), and reliance on a singleton (Reason 4):
class ReportService:
    def __init__(self, db_config):
        self.connection = Database.connect(db_config)     # Reason 1: real work in constructor
        self.logger = GlobalLogger.get_instance()          # Reason 4: singleton dependency
        self.email_client = SmtpClient(real_smtp_server)   # Reason 3: real side-effect-triggering construction

# Untangling it, one reason at a time:
class ReportService:
    def __init__(self, connection, logger, email_client):   # Reason 1 fixed: no construction-time work
        self.connection = connection                          # Reason 3 fixed: injected, can be a fake
        self.logger = logger                                  # Reason 4 fixed: injected instead of a global lookup
        self.email_client = email_client

# production code now explicitly assembles the real dependencies at the composition root (clean-code/11):
service = ReportService(
    connection=Database.connect(real_config),
    logger=GlobalLogger.get_instance(),   # still a singleton internally, but now injected, not reached-for
    email_client=SmtpClient(real_smtp_server),
)

# a test can now construct ReportService trivially, with fakes for everything:
test_service = ReportService(connection=FakeConnection(), logger=FakeLogger(), email_client=FakeEmailClient())
```
Each of the three original problems is addressed by the specific technique matched to its specific cause — this worked example shows that real legacy classes often combine multiple reasons simultaneously, and untangling them one at a time, rather than looking for one silver-bullet fix, is the realistic path forward.

## Pros
- Naming the specific reason a class resists testing (rather than a vague "it's just hard to test") points directly at the matched, proportionate fix from this subject's toolkit.
- Most of the four reasons have well-established, low-risk, incremental fixes (extract initialization, extract interface, parameterize constructor) that don't require a full redesign.
- Working through real, combined cases (as in the worked example) builds the practical skill of untangling several simultaneous obstacles methodically, rather than being overwhelmed by their combination.

## Cons
- The global/singleton dependency case (Reason 4) is often the most invasive and highest-effort to fix properly, and sometimes requires touching code far beyond the class currently being tested.
- Fixing all four reasons in a single class, as in the worked example, is itself a nontrivial, multi-step change that needs the same careful, test-verified sequencing as any other legacy-code modification (`refactoring/01`, `legacy-code/07`).
- Some codebases have global/singleton dependencies so pervasive that fixing even one class fully can reveal a much larger, systemic dependency-breaking effort is actually needed — a scope-creep risk worth recognizing early.

## Alternatives
- **Monkey-patching / dependency substitution at the test-framework level**, bypassing the need to fix construction issues in production code at all — a faster, more fragile alternative, particularly relevant for singleton/global-state problems (Reason 4) where a full injection redesign isn't immediately feasible.
- **Integration testing against real dependencies in a controlled test environment** — sidesteps needing to solve construction-testability problems at all, at the cost of slower, less isolated tests.
- **A full dependency-injection framework adoption** — resolves all four reasons systematically and consistently across an entire codebase, at a much higher upfront adoption cost than fixing one class's specific, immediate testability problem.

## When to use it
Diagnose which of the four specific reasons (constructor side effects, hard-to-construct parameters, side-effect-triggering construction, global/singleton dependencies) is blocking a specific class's testability, and apply the matched technique — rather than attempting a generic, undirected "make this testable" effort.

## When NOT to use it
Don't attempt to fix a global/singleton dependency problem (Reason 4) as your very first step if the class also has simpler, more immediately fixable problems (constructor side effects, hard-to-construct parameters) — resolve the easier reasons first, since doing so may simplify or even partially resolve the harder one as a side effect (as the worked example demonstrates).

## Self-check questions
1. Using the `ReportService` example, identify which specific technique fixed each of the three combined problems, and explain why each technique matched its specific cause.
2. Describe a class from your own experience that resisted testing for one of these four specific reasons. Which reason was it, and what would the matched fix look like?
3. Why is the global/singleton dependency case (Reason 4) typically the hardest to fix, compared to the other three?
4. In what order would you tackle multiple simultaneous testability problems in one class, and why does that order matter?

## References
- Working Effectively with Legacy Code (Michael C. Feathers), Chapter 9: "I Can't Get This Class into a Test Harness".
