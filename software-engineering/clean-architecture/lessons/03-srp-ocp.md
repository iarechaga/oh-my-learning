---
id: clean-architecture/03
subject: clean-architecture
title: SRP and OCP
slug: srp-ocp
status: drafted
mastery:
seniority: mid
source: Clean Architecture (Robert C. Martin), Chapters 7-8
prerequisites: [clean-code/10, clean-architecture/02]
created: 2026-08-10
updated: 2026-08-10
---

# SRP and OCP

## TL;DR
The Single Responsibility Principle, precisely defined here, is not "a module should do one thing" — it's "a module should be responsible to one, and only one, actor" (a single group of stakeholders who could request a change for the same underlying reason). The Open/Closed Principle says a well-designed component should be extensible (open) without requiring modification of its existing, working code (closed) — achieved specifically through the dependency-inversion mechanism `clean-architecture/02` explained.

## The idea
These are the first two of the five SOLID principles, and Martin's treatment sharpens both beyond their common, looser interpretations. **SRP** is frequently mis-taught as "a class should do one thing" — Martin's actual, more precise formulation (echoing but sharpening `clean-code/10`'s cohesion argument): **a module should have responsibility to one, and only one, actor** — where "actor" means a single group of people (a business role, a stakeholder, a department) who would ask for changes to that module for the *same underlying business reason*. **OCP** asks: can you add new behavior to a system by *adding* new code, rather than *modifying* existing, already-working, already-tested code? A well-architected system should make this the common case, not the exception.

## How it works

### SRP, precisely: one actor, not "one thing"
Martin's own famous example: an `Employee` class with three methods — `calculatePay()` (requested and owned by the finance/accounting actor), `reportHours()` (requested and owned by HR), and `save()` (requested and owned by the database administration actor/team). Each method individually "does one thing" in the naive sense, but the *class as a whole* has three genuinely distinct reasons to change, corresponding to three different, independent groups of stakeholders — exactly `refactoring/04`'s "Divergent Change" smell, but now with Martin's sharper diagnostic: **not "does this class do multiple things" but "could two different groups of people, for two entirely unrelated business reasons, each independently request a change to this same file?"** If yes, that's an SRP violation, regardless of how cohesive the individual methods look in isolation.

**Why this distinction matters practically.** Two changes requested by two different actors, landing in the same file, risk **merge conflicts and accidental coupling between unrelated concerns** — a change the finance actor requests to `calculatePay()` might be reviewed, tested, and deployed by people who have no context on HR's `reportHours()` logic sitting in the same file, and a mistake introduced while touching one method can accidentally affect the other simply by being in the same compiled/deployed unit. Splitting by actor (a `PayCalculator`, an `HoursReporter`, an `EmployeeRepository`, each owned conceptually by its respective actor) means each actor's changes are isolated to their own class, eliminating this specific risk.

### OCP, precisely: extend without modifying
The often-quoted "open for extension, closed for modification" is easy to state but easy to misunderstand as a vague aspiration. Martin's concrete mechanism for actually achieving it: **use interfaces (enabled by OO's disciplined polymorphism, `clean-architecture/02`) so that adding a new behavior means adding a new class implementing an existing interface — never editing the classes that already work.**

**Worked example.**
```
# A reporting system where each report format was hardcoded via conditionals — violates OCP
def generate_report(data, format):
    if format == "pdf":
        return generate_pdf(data)
    elif format == "csv":
        return generate_csv(data)
    # adding "xml" support means MODIFYING this existing, working function

# Redesigned to satisfy OCP via an interface and polymorphism
class ReportFormatter:
    def format(self, data): raise NotImplementedError

class PdfFormatter(ReportFormatter):
    def format(self, data): ...

class CsvFormatter(ReportFormatter):
    def format(self, data): ...

def generate_report(data, formatter: ReportFormatter):
    return formatter.format(data)

# adding XML support: a NEW class, zero changes to generate_report or any existing formatter
class XmlFormatter(ReportFormatter):
    def format(self, data): ...
```
This is directly `refactoring/08`'s Replace Conditional with Polymorphism, now framed explicitly as satisfying OCP: `generate_report` is genuinely closed (its own code never needs to change again for a new format) while the system as a whole remains open (new formats are added freely) — the exact combination the principle's name describes.

### Why OCP matters architecturally, not just at the class level
Martin extends OCP beyond individual classes to entire architectural layers: a well-architected system should let you add a significant new feature by adding new components, with **zero or minimal changes to existing, deployed components** — this is the direct motivation for the dependency rule (`clean-architecture/08`) covered later in this subject, which structures an entire system so that high-level business policy is "closed" against changes originating from low-level details (a new database, a new UI framework), because those details depend on the policy's interfaces, never the reverse.

## Pros
- SRP's "one actor" framing gives a precise, checkable diagnostic for a smell that's otherwise easy to rationalize away ("but each method really does just one small thing") — asking "which stakeholder group requests changes here" cuts through that rationalization directly.
- OCP, achieved via polymorphism, converts a whole category of feature additions from risky edits to existing, tested code into safe, additive changes — directly reducing the regression risk `refactoring/03`'s safety-net concerns are all about.
- Both principles, applied together, reduce the blast radius of any single change — SRP by ensuring one change request maps to one isolated module, OCP by ensuring most new behavior doesn't require touching existing modules at all.

## Cons
- SRP's "one actor" test, while precise, requires organizational knowledge (who actually requests changes, and why) that isn't always obvious just from reading code — applying it well requires understanding the business/organizational context, not just the code's structure.
- OCP, pursued aggressively for every possible future extension point, produces exactly the speculative-generality problem `clean-code/12` and `pragmatic-programmer/05` warn against — not every conditional needs to become a polymorphic hierarchy preemptively, only ones with genuine, evidenced extension needs (echoing the Rule of Three).
- Both principles can be over-applied to trivial, low-stakes, rarely-changing code, adding structural ceremony disproportionate to any real, evidenced need for that flexibility.

## Alternatives
- **Cohesion-based splitting** (`clean-code/10`) — a related but less precise predecessor to SRP's actor-based test; useful as a first-pass heuristic, but Martin's actor framing catches violations cohesion alone might miss (e.g., three methods that all "feel" related but actually serve unrelated stakeholders).
- **YAGNI-driven conditional logic left in place** — accepting a simple, un-polymorphic conditional (OCP violation, technically) for a genuinely small, rarely-changing, low-stakes set of cases, deferring the OCP-satisfying refactor until real evidence of growth appears (Rule of Three, `refactoring/02`).
- **Feature flags** — a different mechanism for adding new behavior without disturbing "closed" existing logic, achieving some of OCP's goal at the level of runtime configuration rather than compile-time polymorphism.

## When to use it
Apply SRP's actor test whenever a class or module's methods seem individually reasonable but might actually serve genuinely distinct, unrelated stakeholder groups. Apply OCP via polymorphism whenever a conditional dispatching on type/format/mode is expected to grow with new cases over time (informed by real evidence, not speculation).

## When NOT to use it
Don't split a class by actor if, in your specific organizational context, the "different actors" are actually the same small team making coordinated, related decisions — the risk SRP protects against (independent, uncoordinated changes colliding) doesn't apply if the changes are, in practice, always coordinated anyway. Don't build a full polymorphic hierarchy for OCP's sake around a conditional that has never actually needed a new case and shows no real sign of needing one soon.

## Key takeaways / mental model
For SRP, ask: "which distinct group of stakeholders, for which distinct business reason, would ask for a change to this specific module?" More than one answer is a violation. For OCP, ask: "if a genuinely new case/format/type appears, can I add it without editing any existing, already-working code?" If not, and new cases are a real, expected pattern, that's the signal to introduce polymorphism.

## Self-check questions
1. Using the `Employee` example, explain precisely why three individually-reasonable-looking methods violate SRP, using the actor test rather than a vague "does too much" complaint.
2. Rewrite a type-based conditional from your own code (or the report-formatter example) to satisfy OCP via polymorphism, and explain what future change becomes additive rather than a modification.
3. Describe a case where applying OCP preemptively, without real evidence of a growing set of cases, would be over-engineering. What would you do instead, per YAGNI?
4. Why does Martin extend OCP beyond the class level to entire architectural layers? What's the connection to the dependency rule covered later in this subject?

## References
- Clean Architecture: A Craftsman's Guide to Software Structure and Design (Robert C. Martin), Chapter 7: "SRP: The Single Responsibility Principle" and Chapter 8: "OCP: The Open-Closed Principle".
