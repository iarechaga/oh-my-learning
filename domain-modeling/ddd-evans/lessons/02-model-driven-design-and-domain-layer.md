---
id: ddd-evans/02
subject: ddd-evans
title: Model-driven design and the domain layer
slug: model-driven-design-and-domain-layer
status: drafted
mastery:
seniority: mid
source: Domain-Driven Design (Eric Evans), Part I-II, Chapters 3-4
prerequisites: [ddd-evans/01]
created: 2026-08-10
updated: 2026-08-10
---

# Model-driven design and the domain layer

## TL;DR
Model-driven design means the model produced by knowledge crunching (`ddd-evans/01`) is not a separate artifact from the code — the code's object structure *is* the model, kept alive and correct by a tight, continuous binding between the two. That binding lives in a dedicated domain layer, isolated from UI, persistence, and application plumbing, so domain logic never gets diluted or scattered.

## The idea
A common failure mode: a team draws careful UML diagrams during analysis, then writes code that only loosely resembles those diagrams, because the diagrams were never load-bearing — they were just documentation, produced once and abandoned. Over time the code drifts arbitrarily far from the model, and the "model" becomes a historical artifact nobody trusts.

Evans's alternative is model-driven design: there must be one model, and the implementation must be a literal, disciplined translation of it — not "inspired by" it. If a rule exists in the model ("an order cannot ship before payment is captured"), that rule must exist as an explicit, findable piece of code, not as an implicit consequence of scattered conditionals across five files. If the code can't cleanly express a piece of the model, that's not a coding problem to route around — it's a signal the model itself is wrong or incomplete, and it needs to change, which sends you back to more knowledge crunching.

To make that discipline possible, the domain logic needs a home of its own: the **domain layer** (sometimes called the model layer). This is the subset of the codebase whose sole job is expressing business concepts, business state, and business rules — no SQL, no HTTP handling, no view rendering, no framework glue. Everything else in the system exists to support the domain layer, not the other way around.

## How it works

### The domain layer's isolation
Picture a typical layered application (elaborated in `ddd-evans/03`): presentation, application, domain, infrastructure. The domain layer sits in the middle, and the rule is directional: domain code never depends on presentation or infrastructure code — those layers depend on the domain layer (or talk to it through abstractions the domain layer defines, like a repository interface — see `ddd-evans/10`).

**Concrete smell without a domain layer** — business logic embedded directly in a web controller:
```
def submit_order(request):
    order = db.query("SELECT * FROM orders WHERE id = ?", request.order_id)
    if order['status'] != 'draft':
        return error("cannot submit")
    if sum(item['price'] * item['qty'] for item in order['items']) < 10:
        return error("order too small")
    db.execute("UPDATE orders SET status = 'submitted' WHERE id = ?", request.order_id)
    send_confirmation_email(order['customer_email'])
    return success()
```
The business rules ("must be draft," "minimum order value is 10") live entangled with HTTP handling and raw SQL. There is no `Order` object — just a dictionary pulled from a row. Nobody can unit-test "can an order be submitted" without spinning up a database and a fake HTTP request. And if the same rule needs to apply from a batch job or an admin tool, it has to be copy-pasted or awkwardly extracted after the fact.

**With a domain layer:**
```
class Order:
    def submit(self):
        if self.status != OrderStatus.DRAFT:
            raise InvalidOrderStateError("Order must be draft to submit")
        if self.total() < Money(10, "USD"):
            raise OrderTooSmallError()
        self.status = OrderStatus.SUBMITTED
        self.record_event(OrderSubmitted(self.id))
```
Now `Order.submit()` is a self-contained expression of a business rule, testable with plain objects and no infrastructure, reusable from any entry point (web, batch, CLI, another service), and readable by a domain expert (with a little translation of syntax) as a direct statement of the rule they described in conversation. This is model-driven design: the shape of the code (`Order`, `submit()`, `OrderStatus.DRAFT`) is a direct translation of the shared vocabulary from `ddd-evans/01`, not an incidental byproduct of how the database happens to be structured.

### The feedback loop between model and implementation
Model-driven design is bidirectional, not "design once, implement once." If, while implementing `submit()`, a developer realizes the rule is actually "an order must be draft *and* have a valid shipping address," that discovery should flow back into the model — and back into the language used with domain experts — not just get silently patched into the code as an implementation detail nobody else knows about. The code is a *sensitive instrument* for testing the model: bugs, awkward implementations, and contorted logic are often symptoms of a model that's subtly wrong, not just implementation mistakes to code around.

### Worked example: a payroll system's domain layer
A payroll domain layer might contain `Employee`, `PaySchedule`, `Timesheet`, `Paycheck`, `TaxWithholding` — each with behavior, not just data (`Timesheet.totalHours()`, `Paycheck.calculateNetPay()`). None of these classes know about the database table structure, the PDF-generation library used to print pay stubs, or the REST endpoint that triggers payroll runs. Those concerns live in outer layers (`ddd-evans/03`) and depend inward on the domain layer's objects and interfaces, never the reverse. A `PayrollRunController` in the application layer orchestrates: fetch employees via a repository (`ddd-evans/10`), call domain methods, persist results — but it contains no payroll *rules* itself, only sequencing.

## Pros
- Business rules live in one findable, testable place instead of being smeared across controllers, SQL, and view templates.
- The code becomes a genuine communication tool with domain experts, not just a black box that happens to produce correct output.
- Domain logic is reusable across every delivery mechanism (web, batch, CLI, message queue) because it has no dependency on any of them.
- Bugs and awkward code become useful signals about model correctness rather than just things to patch around.

## Cons
- Requires real discipline to maintain the isolation — it's always tempting to "just quickly" call the database from inside a domain method under deadline pressure, and that erosion compounds.
- Adds indirection (interfaces, layers) that feels like overhead on a small or short-lived project where the domain genuinely is trivial.
- Teams unfamiliar with the practice often build an anemic domain layer by habit — classes with fields and getters/setters but no real behavior — which keeps the *shape* of a domain layer while losing its actual value; this is one of the most common DDD anti-patterns in practice.

## Alternatives
- **Transaction script** — organize logic as a set of procedures, one per use case, operating directly on data structures; simpler to reason about for genuinely simple CRUD systems, but doesn't scale as business rules multiply and start needing to be shared or reused across scripts.
- **Active Record** — domain objects that also know how to persist themselves (common in frameworks like Rails or Django); convenient for simple cases but tends to blur the domain/infrastructure boundary this lesson insists on, since the object now depends on the persistence mechanism.
- **Anemic domain model** — an explicitly discouraged, but common, middle ground: domain classes exist but hold no behavior, with all logic living in separate "service" classes that manipulate them like data bags; this looks superficially similar to a real domain layer but loses most of its benefits (see `ddd-evans/06` for where behavior legitimately belongs in a service versus where it's really just an anemic model in disguise).

## When to use it
Use model-driven design and an isolated domain layer whenever the domain has real, evolving business rules worth protecting from erosion — most line-of-business systems, anything with meaningful state machines, calculations, or policies that stakeholders care about getting right.

## When NOT to use it
Skip the ceremony for systems that are genuinely thin wrappers over storage with no real business rules (a simple content-management form, a proxy service), or in early-stage prototypes where the domain itself is still unknown and premature structure would just have to be thrown away — start simpler and introduce the domain layer once the rules stabilize enough to be worth protecting.

## Key takeaways / mental model
The domain layer is the one place in the system where you're allowed to write code that reads as "here is a true statement about the business" with no infrastructure noise attached — everything else in the architecture exists to get data into and out of that layer without contaminating it.

## Self-check questions
1. Take the `submit_order` procedural example above and identify every business rule hidden inside it. Which of those would a domain expert actually recognize as "a rule," versus which are accidental implementation details?
2. What's the practical difference between an anemic domain model and a real one, if both have classes named `Order`, `Customer`, etc.?
3. Why does the book treat awkward or buggy implementation code as a signal about the *model*, not just about the code?
4. Describe a project where a domain layer would be overkill, and explain what you'd do instead.

## References
- Domain-Driven Design: Tackling Complexity in the Heart of Software (Eric Evans), Chapter 3: "Binding Model and Implementation" and Chapter 4: "Isolating the Domain".
