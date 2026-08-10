---
id: clean-code/10
subject: clean-code
title: "Classes: Cohesion and SRP in the Small"
slug: classes
status: drafted
mastery:
seniority: mid
source: Clean Code (Robert C. Martin), Chapter 10
prerequisites: [clean-code/03, clean-code/06]
created: 2026-08-10
updated: 2026-08-10
---

# Classes: Cohesion and SRP in the Small

## TL;DR
A class should be small — measured not in lines but in *responsibilities* — and every one of its fields and methods should be tightly related to a single purpose (high cohesion). A class name that can't be stated in about 25 words without "and" or "or" is a strong signal it's doing more than one job.

## The idea
`clean-code/03` applied "do one thing" to functions; this chapter applies the same discipline one level up, to classes. The failure mode is structurally identical: a class that accumulates unrelated responsibilities (a `UserManager` that handles authentication, sends emails, formats reports, and logs analytics) forces every reader to load all of those unrelated concerns into their head just to understand any one of them, and forces every change to any single concern to be made cautiously, since the class's other, unrelated responsibilities might accidentally be affected by a change that shouldn't touch them at all.

**Cohesion** is the specific lens the chapter uses to detect this: a class is highly cohesive when its methods and fields work together closely, and most methods use most of the fields. A class is poorly cohesive when it can be cleanly split into groups of methods/fields that never interact with each other — a strong sign that what looks like one class is actually two or more, arbitrarily bundled.

## How it works

### The "class name that needs 'and'" test
A quick, practical smell test: try to describe the class in about 25 words. If the description naturally needs "and" ("handles user authentication *and* sends welcome emails *and* generates activity reports"), that's usually more than one responsibility, and the class should probably be split along those "and" boundaries.

**Worked example — before (low cohesion, multiple responsibilities):**
```
class UserManager:
    def authenticate(self, username, password): ...
    def hash_password(self, password): ...
    def send_welcome_email(self, user): ...
    def render_activity_report(self, user): ...
    def log_login_event(self, user): ...
```
Notice that `authenticate`/`hash_password` share fields/concerns (credentials), `send_welcome_email` shares nothing with them, `render_activity_report` shares nothing with either, and `log_login_event` is again a separate concern. Measuring cohesion concretely: if you drew a table of which methods use which fields, you'd see distinct, non-overlapping clusters — a strong structural signal, not just a naming feeling, that this is several classes wearing one name.

**After (split by cohesion):**
```
class Authenticator:
    def authenticate(self, username, password): ...
    def hash_password(self, password): ...

class WelcomeEmailSender:
    def send(self, user): ...

class ActivityReportRenderer:
    def render(self, user): ...

class LoginEventLogger:
    def log(self, user): ...
```
Each class now has one describable job, and — critically — each can be changed, tested, and understood in isolation. A bug in report rendering can't accidentally be introduced while touching authentication logic, because they're no longer in the same class sharing the same file, the same instance state, and the same "blast radius."

### Small classes, plural, beat one large class
The natural objection to splitting classes: "now I have five small classes instead of one big one — isn't that *more* to keep track of?" The book's counter: the *total* complexity of the system doesn't change by splitting a class — the same methods and fields exist either way — but the complexity a reader has to hold *at any one time* drops sharply, because they can now focus on one small, cohesive class fully, rather than one large class only partially (holding the rest as noise they have to filter out mentally).

### The Single Responsibility Principle, restated at the class level
This chapter is the concrete, tactical companion to SRP (formalized further in `software-engineering/clean-architecture`'s SOLID treatment): **a class should have one reason to change.** "Reason to change" is the operative phrase — it's not about how many methods a class has, it's about how many independent *forces* (a business rule changing, a data format changing, a reporting requirement changing) could each independently require modifying this class. `UserManager` above had at least four independent reasons to change (an auth policy change, an email template change, a report format change, a logging format change) bundled into one class — meaning a change driven by any one of those four unrelated forces required touching (and re-testing, and re-reviewing) the same file.

### Organizing for change — encapsulation still matters within small classes
Splitting into small, cohesive classes doesn't mean abandoning encapsulation (`clean-code/06`) — each small class should still hide its own internal state behind a minimal, well-named public interface, exposing only what its collaborators genuinely need. Small-and-cohesive and well-encapsulated are complementary properties, not substitutes for each other.

## Pros
- High cohesion makes each class's purpose immediately graspable and independently testable, changeable, and reviewable.
- Splitting by responsibility isolates the blast radius of a change to exactly the class whose "reason to change" actually fired, echoing `pragmatic-programmer/04`'s orthogonality at the class-design level.
- The "describe in 25 words without 'and'" test is a cheap, fast, repeatable smell check that doesn't require deep structural analysis to apply.

## Cons
- Splitting aggressively can produce a proliferation of very small classes that, without clear naming and organization, becomes its own kind of navigational overhead ("where's the logic that actually does X?").
- Determining the "right" responsibility boundaries requires real domain judgment; splitting along the wrong seams can produce classes that are small but still tangled by hidden coupling between them.
- Retrofitting cohesion onto an existing large, low-cohesion class is a genuine refactoring effort (see `software-engineering/refactoring`), not a quick fix, especially if many callers already depend on its current, bundled interface.

## Alternatives
- **God classes / large multi-purpose classes as a deliberate short-term choice** — sometimes reasonable in genuinely small, short-lived scripts or prototypes (`pragmatic-programmer/06`) where the long-term maintenance cost this chapter warns about never materializes.
- **Package/module-level cohesion instead of class-level** — in some languages/paradigms, cohesion is organized at the module or package level rather than strictly per-class, achieving a similar goal (grouping what changes together, separating what doesn't) with a different unit of organization.
- **Functional decomposition without classes at all** — in languages/styles that favor functions and data (see `clean-code/06`'s data-structure style) over classes, the same cohesion principle applies to *modules of functions* rather than to classes specifically.

## When to use it
Apply the cohesion lens whenever a class's method list starts requiring "and" to describe, or when you notice distinct groups of methods that never touch the same fields. Especially watch for it in classes named with vague, catch-all nouns (`Manager`, `Handler`, `Utils`, `Helper`) — these names are a strong prior indicator of low cohesion, because they don't commit to describing one specific responsibility.

## When NOT to use it
Don't split a class purely to reduce its line count if its methods and fields are genuinely tightly related (high cohesion) — a longer but cohesive class is preferable to several small classes with hidden coupling between them. Don't over-invest in splitting truly short-lived, throwaway code where the long-term readability payoff never gets realized.

## Key takeaways / mental model
For any class, ask: "how many independent business/technical forces could each, on their own, require me to change this class?" If the honest answer is more than one, find the seam between those forces and split along it — the goal isn't fewer lines per class, it's fewer unrelated reasons to touch the same file.

## Self-check questions
1. Find a class in code you've worked on named `Manager`, `Handler`, or `Utils`. List its methods and group them by which fields they actually use — is it one cohesive class or several bundled together?
2. Explain why splitting one large class into five small ones doesn't increase the system's total complexity, only redistributes what a reader has to hold at once.
3. What does "one reason to change" mean concretely, and how is it different from "does one thing" as applied to functions in `clean-code/03`?
4. Give an example of splitting a class along the *wrong* seam, producing small classes that are still tangled by hidden coupling.

## References
- Clean Code: A Handbook of Agile Software Craftsmanship (Robert C. Martin), Chapter 10: "Classes".
- See also: `software-engineering/clean-architecture` for the formal Single Responsibility Principle and the rest of SOLID.
