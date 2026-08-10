---
id: clean-architecture/11
subject: clean-architecture
title: The Database and the Web Are Details
slug: details-database-web
status: drafted
mastery:
seniority: senior
source: Clean Architecture (Robert C. Martin), Chapters 25-26
prerequisites: [clean-architecture/08]
created: 2026-08-10
updated: 2026-08-10
---

# The Database and the Web Are Details

## TL;DR
Martin makes a deliberately provocative claim: the choice of database, and the choice of whether your system is delivered over the web, over a desktop GUI, or as a CLI, are both *details* — implementation decisions that should be deferred, kept swappable, and never allowed to shape your business rules' fundamental structure. A relational database is a data-storage *mechanism*, not a "model" your business logic should be built around; the web is a *delivery* mechanism, not the essence of what your application does.

## The idea
This lesson applies the Dependency Rule (`clean-architecture/08`) to the two technical decisions most engineers reflexively treat as foundational, architecture-defining choices made at the very start of a project — and argues both should instead be treated as late-bindable details, exactly like any other volatile dependency. This isn't a claim that databases or delivery mechanisms don't matter; it's a claim about *where* the decision to use a specific one should sit in the dependency graph, and how late it can reasonably be deferred.

## How it works

### The database is a detail — data structure vs. storage mechanism
Martin's specific argument: a relational table, a document in a NoSQL store, and an in-memory object graph are all just different **ways of storing** data — none of them is the actual *data model* your business cares about. The actual data model — what a `Loan`, a `Customer`, an `Order` fundamentally *is*, what fields and relationships and rules genuinely matter — should be expressed entirely in Entity classes (`clean-architecture/07`), independent of whether those Entities eventually get persisted as SQL rows, document-store JSON blobs, or flat files.

**The specific failure mode this warns against.** A common, subtle architectural mistake: letting an ORM's table-mapped model classes *become* the application's actual domain model — Entities that inherit from an ORM base class, carry database-specific annotations, and mirror the exact shape of database tables (including denormalization artifacts, foreign-key columns, and other storage-specific concerns that have nothing to do with the actual business concept). This conflates "how the data is stored" with "what the data fundamentally is," and it means the business logic is now, silently, coupled to a specific database technology's specific modeling conventions — exactly the coupling `clean-architecture/08`'s dependency rule exists to prevent, even though the code might still nominally be organized into "layers."

**The fix, applying the Dependency Rule concretely.** Entities remain plain objects with no database awareness at all; a separate `Repository`/`Gateway` interface (owned by the Use Cases circle, per `clean-architecture/08`'s exact mechanism) defines what persistence operations the business logic actually needs (`save`, `findById`, `findOverdueLoans`); a concrete implementation in the outermost circle translates between Entities and whatever the actual database's specific storage format requires. Swapping from Postgres to MongoDB, under this structure, means rewriting *one* implementation of that interface — the Entities and Use Cases never change, never even need to be recompiled.

### The web is a detail — delivery mechanism vs. business purpose
The parallel argument for delivery mechanisms: whether your application is accessed via a web browser, a native mobile app, a CLI, or a batch job is a decision about **how users or other systems interact with your business logic** — it is not, and should not become, part of what that business logic fundamentally *is*. A Use Case (`clean-architecture/07`) like `SubmitLoanApplicationUseCase` should be expressible and fully testable without any HTTP request, response object, or web framework involved at all — it should be equally invokable from a web controller, a CLI command, or an automated test, because its actual logic has nothing to do with HTTP specifically.

**The specific failure mode this warns against.** Business logic methods that accept a framework's `Request` object directly as a parameter, or that construct a framework-specific `Response` object as their return value, have silently coupled the business logic to one specific delivery mechanism — adding a CLI interface to the same application later would require either duplicating the logic or awkwardly faking a web request object just to invoke it, neither of which should be necessary if the Dependency Rule had been consistently applied.

**Worked example.**
```
# Coupled to the web framework — a violation
def submit_loan_application_endpoint(request):   # framework's Request object, directly
    score = credit_service.score(request.POST["applicant_id"])
    if score < 650:
        return HttpResponse(status=400, body="rejected")   # framework's Response object, directly
    ...

# Decoupled — the Use Case knows nothing about HTTP
class SubmitLoanApplicationUseCase:
    def execute(self, application_data: dict) -> LoanResult:   # plain data in, plain data out
        score = self.credit_service.score(application_data["applicant_id"])
        if score < 650:
            return LoanResult(accepted=False, reason="credit score too low")
        ...

# a THIN web controller (Interface Adapters circle) translates HTTP <-> the Use Case's plain interface
def submit_loan_application_endpoint(request):
    result = SubmitLoanApplicationUseCase().execute({"applicant_id": request.POST["applicant_id"]})
    return HttpResponse(status=200 if result.accepted else 400, body=result.reason)
```
The decoupled version's `SubmitLoanApplicationUseCase` can be tested with plain Python dicts and no web framework running at all, and could be invoked identically from a CLI command or a scheduled job with zero changes to the Use Case itself — exactly the flexibility `clean-architecture/01`'s "architecture keeps options open" framing promises, made concrete for the two most commonly over-coupled technical decisions in real systems.

### Why these two decisions specifically get treated as foundational, and why that's the mistake
Martin's diagnosis for why teams so often violate this principle for exactly these two decisions: choosing a database and choosing a delivery framework are typically among the *very first* decisions made on a new project, often before the business logic itself is well understood — and because they're made first, and because the chosen framework/database's own tooling and conventions are visible and convenient from day one, it's easy to let the business logic's structure passively follow whatever shape the framework or ORM encourages, rather than deliberately keeping the business logic independent from the start. The fix isn't to delay *choosing* a database or framework (you still need something to build against) — it's to choose one while deliberately keeping the business logic's structure independent of that specific choice, via the interfaces this lesson (and `clean-architecture/08`) describe.

## Pros
- Keeps the actual, valuable business logic swappable and testable independent of which specific database or delivery mechanism is currently in use.
- Prevents an ORM's or web framework's specific conventions from silently becoming the shape of the business's actual domain model.
- Makes adding a second delivery mechanism (a CLI alongside an existing web app, or an API alongside a UI) a matter of writing a new, thin adapter — not duplicating or awkwardly retrofitting business logic.

## Cons
- Maintaining this separation requires real, ongoing discipline against the path of least resistance most frameworks and ORMs make convenient by default (inheriting from a base model class, accepting a framework's request object directly).
- The translation/mapping code needed at the boundary (converting between framework-specific objects and plain data, or between Entities and ORM models) is a genuine, ongoing cost that can feel like unnecessary duplication for very simple CRUD-style applications.
- For genuinely small, short-lived, single-delivery-mechanism applications with no credible plan to ever swap database or framework, this separation's cost may exceed its benefit, echoing `clean-architecture/09`'s cost/benefit boundary-drawing test.

## Alternatives
- **Active Record pattern** (see `software-engineering/enterprise-patterns`) — deliberately merges the data model and persistence logic into one class, the opposite of this lesson's separation; a reasonable, lighter-weight choice specifically for simpler applications where the full separation's cost isn't justified.
- **Framework-first development** (e.g., building directly and heavily on a specific full-stack framework's conventions) — trades architectural independence for development speed and framework-provided tooling, often a reasonable choice for smaller applications or rapid prototypes (`pragmatic-programmer/06`).
- **A separate "anti-corruption layer"** (see `domain-modeling/implementing-ddd`) — a related, DDD-flavored technique for keeping a domain model clean from an external system's (or legacy system's) specific conventions, conceptually similar to this lesson's database/web boundary but framed around integration with other bounded contexts specifically.

## When to use it
Apply this separation for any system with meaningful, enduring business logic where a credible chance exists of needing to swap the database, add a second delivery mechanism, or migrate frameworks over the system's life — or simply whenever you want business logic to be genuinely, fully unit-testable without spinning up a database or web server.

## When NOT to use it
Don't impose the full separation on a genuinely small, throwaway, or single-purpose CRUD application with no credible future need to swap its database or delivery mechanism — Active Record or framework-first development may be the more proportionate choice there, per `clean-architecture/09`'s cost/benefit framing.

## Key takeaways / mental model
Ask, of any business-logic code: "does this know, even implicitly, that it's talking to a specific database or a specific web framework?" If yes, that's exactly the coupling this lesson argues against — push that knowledge outward, to the Interface Adapters and Frameworks circles, and let the business logic stay expressible in plain, boring data structures and plain function calls.

## Self-check questions
1. Using the loan-application example, explain precisely what coupling the "before" version has to the web framework, and what changes to remove it in the "after" version.
2. Describe a case where an ORM's conventions silently shaped a domain model's structure in code you've seen, and what the resulting coupling cost was (or would be) if the database needed to change.
3. Why does Martin argue this separation's cost isn't always justified, and what specific factors would lead you to skip it for a given project?
4. Explain why choosing a database or framework early in a project, without deliberately maintaining this separation, tends to produce architecture that "passively follows" the framework's shape, according to this lesson's diagnosis.

## References
- Clean Architecture: A Craftsman's Guide to Software Structure and Design (Robert C. Martin), Chapter 25: "Layers and Boundaries" and Chapter 26: "The Missing Chapter" (database and web details).
