---
id: clean-architecture/07
subject: clean-architecture
title: "Business Rules: Entities and Use Cases"
slug: business-rules
status: drafted
mastery:
seniority: senior
source: Clean Architecture (Robert C. Martin), Chapters 20-21
prerequisites: [clean-architecture/04]
created: 2026-08-10
updated: 2026-08-10
---

# Business Rules: Entities and Use Cases

## TL;DR
Martin distinguishes two kinds of business rules that deserve different homes in an architecture: **Entities** encapsulate the most general, critical business rules that would exist and matter even if the specific application didn't (a `Loan`'s interest-calculation rule matters to the business regardless of which app enforces it); **Use Cases** encapsulate application-specific rules — the particular way *this* application orchestrates entities to accomplish a specific task. Neither should know anything about databases, UI, or frameworks.

## The idea
Before this lesson's architecture (`clean-architecture/08`'s dependency rule) can be meaningfully applied, you need to know what actually belongs at the "center" of that architecture — the parts everything else should depend on, never the reverse. Martin's answer: the business rules, split into two distinct concentric layers based on how general and application-independent each rule is.

## How it works

### Entities — the most critical, most general business rules
An Entity, in this book's specific sense (distinct from, though related to, a "database entity" or an ORM model class), is an object encapsulating **the most critical business rules operating on the most critical business data** — rules that would be true and valuable to the business even if this specific application, or even the specific *concept* of "an app," didn't exist. Martin's own touchstone example: a bank's "a loan's interest is calculated by compounding daily at the current rate, applied to the outstanding principal" rule is a rule about *loans*, as a business concept — it existed in some form before any specific loan-management software was built, and it would remain a true, relevant business rule even if this particular application were replaced by an entirely different one, or by a human clerk with a calculator.

**The test for "is this an Entity-level rule."** Ask: "does this rule exist because of *this specific application's* particular way of doing things, or does it exist because of what the business fundamentally *is*, independent of any specific software?" A `Loan`'s interest calculation passes this test (it's a rule about loans, period). A rule like "when a loan application is submitted through the mobile app, send a push notification to the loan officer's app-specific dashboard" fails this test — it's specific to *this* application's particular user-facing workflow, not a fundamental fact about what loans or lending are.

### Use Cases — application-specific orchestration
A Use Case describes and constrains **how a specific application uses and orchestrates Entities to accomplish an automated task** — the rules that are true specifically *because of how this particular application works*, not fundamental truths about the business domain independent of any application. "When a user submits a loan application through our system, validate their credit score is above our specific threshold, create a `Loan` entity, and notify the assigned loan officer" is a Use Case — it describes *this application's* specific process, which could plausibly be different in a different application serving the same underlying business (a different bank might use a different credit-score threshold, or a different notification mechanism, without changing what a `Loan`'s interest calculation fundamentally is).

**Worked example distinguishing the two.**
```
class Loan:                                          # Entity — general business rule
    def __init__(self, principal, rate):
        self.principal, self.rate = principal, rate
    def calculate_interest(self, days):
        return self.principal * (1 + self.rate / 365) ** days - self.principal

class SubmitLoanApplicationUseCase:                   # Use Case — THIS application's specific orchestration
    def __init__(self, credit_check_service, loan_repository, notifier):
        self.credit_check_service = credit_check_service
        self.loan_repository = loan_repository
        self.notifier = notifier
    def execute(self, application):
        if self.credit_check_service.score(application.applicant) < 650:   # THIS app's specific threshold
            raise ApplicationRejected("credit score too low")
        loan = Loan(application.amount, current_market_rate())
        self.loan_repository.save(loan)
        self.notifier.notify_loan_officer(loan)                             # THIS app's specific workflow
        return loan
```
`Loan.calculate_interest` would remain true and meaningful in almost any lending context. `SubmitLoanApplicationUseCase`'s specific credit-score threshold, specific notification behavior, and specific orchestration sequence are all decisions *this particular application* made, which a different application serving the same business could reasonably make differently — that's precisely what distinguishes a Use Case from an Entity.

### Both layers must remain independent of databases, UI, and frameworks
Critically, both Entities and Use Cases should be expressible in plain, framework-free code — a `Loan` entity should not know it's ever going to be persisted to a specific database, and a `SubmitLoanApplicationUseCase` should not know whether it's being invoked from a web request, a CLI command, or a scheduled batch job. Both depend only on interfaces (`credit_check_service`, `loan_repository`, `notifier` above are all abstractions, per `clean-architecture/04`'s DIP) — this is what makes the entire business-rule layer testable without a database or network connection, and swappable to a different delivery mechanism (web, CLI, a different UI) without touching a single business rule.

### Why the two-layer split matters, not just a single "business logic" layer
Keeping Entities and Use Cases as two distinct concepts (even though both are "business logic" in a loose sense) matters because they have genuinely different *reasons to change* — directly connecting to `clean-architecture/03`'s SRP/CCP framing: a change to the fundamental interest-calculation rule (an Entity change) is driven by a different actor and a different business reason than a change to this specific application's credit-score threshold or notification workflow (a Use Case change). Collapsing both into one undifferentiated "business logic" module risks exactly the divergent-change problem SRP is designed to prevent.

## Pros
- The Entity/Use Case distinction gives a precise, checkable test ("would this rule exist independent of this specific app?") for deciding where a given piece of business logic belongs.
- Keeping both layers framework-independent makes the core business logic testable in isolation, without needing a database, network, or UI framework running at all.
- Separating the two layers by their different reasons to change avoids conflating genuinely distinct business/technical actors in one undifferentiated module.

## Cons
- The distinction between "general business rule" and "application-specific rule" isn't always crisp in practice — some rules genuinely sit in a gray area, and reasonable engineers can disagree about where a specific rule belongs.
- Keeping Entities and Use Cases fully framework-independent requires real discipline (resisting the convenience of, say, an ORM's base class or a web framework's request object leaking into a Use Case) that's easy to erode under delivery pressure.
- For genuinely small applications with little enduring, application-independent business logic, the full Entity/Use Case split can feel like unnecessary structural ceremony relative to the actual complexity being managed.

## Alternatives
- **A single, undifferentiated "domain" or "service" layer** — simpler to start with, appropriate for smaller applications, at the cost of not distinguishing genuinely different reasons to change once the codebase grows.
- **Domain-Driven Design's Aggregates and Application Services** (see `domain-modeling/ddd-evans`, `domain-modeling/implementing-ddd`) — a closely related, often more elaborate framework for the same underlying distinction, with additional concepts (aggregates, domain events, bounded contexts) for more complex domains.
- **Transaction Script pattern** (see `software-engineering/enterprise-patterns`) — a simpler, more procedural alternative for genuinely simple business logic, where the full Entity/Use Case distinction's overhead isn't justified by the domain's actual complexity.

## When to use it
Apply the Entity/Use Case distinction for any system with genuine, enduring business rules that matter independent of the specific application, especially when you expect the application's specific delivery mechanism (web, mobile, API) or specific orchestration details to change or multiply over time.

## When NOT to use it
Don't force the full two-layer split onto a genuinely simple application whose "business logic" is thin, has no enduring rules independent of the specific app, and shows no sign of needing that independence — a simpler, single-layer domain/service structure may be entirely adequate there.

## Key takeaways / mental model
For any piece of business logic, ask: "would this rule still make sense and matter if this specific application were swapped out for a different one serving the same underlying business?" If yes, it's Entity-level. If it's specifically about how *this* application orchestrates things, it's Use-Case-level. Either way, keep both free of any dependency on databases, UI, or frameworks.

## Self-check questions
1. Using the loan example, explain precisely why `calculate_interest` belongs on the Entity while the credit-score threshold belongs in the Use Case.
2. Describe a business rule from your own domain that sits in a genuine gray area between Entity and Use Case. How would you decide where it belongs?
3. Why must both Entities and Use Cases remain independent of databases, UI, and frameworks? What test could you use to verify this independence in your own code?
4. Explain, using `clean-architecture/03`'s SRP/CCP framing, why collapsing Entities and Use Cases into one undifferentiated layer risks a divergent-change problem.

## References
- Clean Architecture: A Craftsman's Guide to Software Structure and Design (Robert C. Martin), Chapter 20: "Business Rules" and Chapter 21: "Screaming Architecture" (Entities and Use Cases sections).
