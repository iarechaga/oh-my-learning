---
id: enterprise-patterns/02
subject: enterprise-patterns
title: "Domain Logic: Transaction Script vs Domain Model"
slug: domain-logic-patterns
status: drafted
mastery:
seniority: senior
source: Patterns of Enterprise Application Architecture (Martin Fowler), Chapter 9
prerequisites: [enterprise-patterns/01, clean-code/06]
created: 2026-08-10
updated: 2026-08-10
---

# Domain Logic: Transaction Script vs Domain Model

## TL;DR
Transaction Script organizes business logic as one procedure per business transaction, each handling everything that transaction needs, directly and sequentially — simple, but scales poorly as logic and duplication grow. Domain Model organizes the same business logic as a network of objects, each with both data and behavior, capturing rules as methods on the objects they concern — more powerful for complex logic, at a real complexity and learning-curve cost that isn't justified for simple applications.

## The idea
This is the single most consequential decision the Domain layer (`enterprise-patterns/01`) faces, and Fowler frames it explicitly as a trade-off, not a "correct answer" — directly connecting to `clean-code/06`'s object-versus-data-structure duality, but applied here specifically to how an *entire application's* business logic should be organized, rather than to a single class.

## How it works

### Transaction Script — one procedure per transaction
Each business transaction (place an order, calculate a bill, approve a claim) is implemented as a single procedure that does everything that transaction requires, directly and in sequence: read input, validate, apply business rules, update the database, return a result. There's no elaborate object model — data is largely represented in simple structures (rows, DTOs), and behavior lives in the procedures, not distributed across a rich network of domain objects.

**Worked example.**
```
def process_order(order_data):
    # everything for this transaction lives here, sequentially
    validate_order_data(order_data)
    customer = db.get_customer(order_data["customer_id"])
    if customer.credit_limit < order_data["total"]:
        raise CreditLimitExceeded()
    discount = 0.1 if customer.is_vip else 0
    final_total = order_data["total"] * (1 - discount)
    db.insert_order(customer.id, final_total)
    return final_total
```
This is simple, easy to trace end-to-end (a single reader can follow the entire transaction top-to-bottom without jumping between many classes), and easy to add a *new* transaction to (just write a new procedure) — but as the number of transactions grows, logic that genuinely belongs to a shared concept (like "is this customer eligible for a discount") tends to get duplicated across many separate procedures, each independently re-implementing similar logic slightly differently (echoing `pragmatic-programmer/03`'s DRY concern, now at the whole-application scale).

### Domain Model — a network of objects with data and behavior
Business logic is instead distributed across a network of domain objects (an `Order`, a `Customer`, a `Product`), each responsible for the rules and calculations that genuinely concern it — directly `clean-code/06`'s object style, applied at the scale of a whole application's business logic.

**Worked example.**
```
class Customer:
    def __init__(self, credit_limit, is_vip):
        self.credit_limit, self.is_vip = credit_limit, is_vip
    def discount_rate(self):
        return 0.1 if self.is_vip else 0
    def can_afford(self, amount):
        return self.credit_limit >= amount

class Order:
    def __init__(self, customer, total):
        self.customer, self.total = customer, total
    def final_total(self):
        return self.total * (1 - self.customer.discount_rate())
    def place(self):
        if not self.customer.can_afford(self.final_total()):
            raise CreditLimitExceeded()
        return self.final_total()
```
Now `discount_rate()` lives in exactly one place (on `Customer`, the object it genuinely concerns) and is automatically reused by *every* transaction that needs to know a customer's discount — no duplication, and a future change to discount policy touches one method, not every transaction procedure that happened to inline similar logic.

### The trade-off, precisely
- **Transaction Script wins** for genuinely simple domains, where business logic doesn't have much shared structure across transactions, and where the team's familiarity with OO domain modeling is limited — it's easier to learn, easier to trace end-to-end, and has less structural overhead for logic that's inherently simple and largely independent per transaction.
- **Domain Model wins** as logic complexity grows — specifically when the *same* underlying rules and calculations are genuinely shared across many different transactions, when business rules have rich, non-obvious interactions worth capturing in a rich object model, and when the team has the OO design skill to build and maintain that model well. The cost: a genuine learning curve, more upfront design effort, and — a specific technical cost this subject devotes several later lessons to — the need for careful, deliberate work to map the resulting rich object graph onto a relational database (`enterprise-patterns/06`, `enterprise-patterns/09`-`10`), since a rich, deeply-linked object model doesn't map onto flat, table-shaped storage as directly as Transaction Script's simpler data structures do.

### A pragmatic middle ground exists — and it's usually where real systems land
Fowler is explicit that most real systems don't sit purely at one extreme — a system might use simple Transaction Script-style procedures for genuinely simple transactions while using a richer Domain Model for a specific, genuinely complex sub-area (say, pricing rules with many interacting discount/promotion combinations) — applying the more expensive pattern specifically where its power is actually needed, echoing this whole subject's repeated theme of proportionality (`code-complete/01`'s doghouse-vs-skyscraper scaling, applied here to domain logic organization specifically).

## Pros
- Transaction Script is fast to write, easy to understand end-to-end, and has a low learning curve — well-suited to genuinely simple applications or genuinely simple individual transactions.
- Domain Model eliminates cross-transaction duplication of shared business rules and provides a natural home for rich, interacting business logic that Transaction Script would otherwise scatter and repeat.
- Recognizing that both can coexist within one system lets a team apply each pattern proportionately, rather than forcing an all-or-nothing choice across an entire application.

## Cons
- Transaction Script accumulates duplicated logic as the number of transactions grows and shared rules multiply, producing exactly the change-amplification problem (`philosophy-of-software-design/01`) DRY exists to prevent.
- Domain Model has a real upfront cost — more classes, more design decisions, a genuine learning curve for engineers unfamiliar with rich OO domain modeling — and, notoriously, requires solving the object-relational mapping problem this subject's later lessons address in depth.
- Choosing Domain Model for a domain that turns out to be simpler than expected produces unnecessary structural overhead; choosing Transaction Script for a domain that turns out to be more complex than expected produces accumulating duplication that eventually demands a costly migration to a richer model.

## Alternatives
- **Table Module** (`enterprise-patterns/03`) — a distinct middle-ground pattern, organizing logic around a database table (not an individual record) rather than committing fully to either Transaction Script's per-transaction procedures or Domain Model's per-object behavior.
- **Domain-Driven Design's richer tactical patterns** (see `domain-modeling/ddd-evans`, `domain-modeling/implementing-ddd`) — a more elaborate, more thoroughly developed evolution of the Domain Model idea, adding Aggregates, domain events, and bounded contexts for genuinely complex domains beyond what this book's more basic Domain Model pattern alone addresses.
- **Rules engines** — for domains with an especially large number of interacting, frequently-changing business rules, externalizing rule logic into a dedicated rules-engine configuration rather than either Transaction Script code or a hand-built Domain Model, trading code-level flexibility for a different kind of maintainability.

## When to use it
Use Transaction Script for genuinely simple applications, or for individual transactions within a larger system that don't share significant logic with other transactions. Use Domain Model once shared, non-trivial business rules recur across multiple transactions, or once the domain's inherent complexity (many interacting rules and states) justifies the investment.

## When NOT to use it
Don't commit to a full Domain Model for a domain that's genuinely simple and unlikely to grow much more complex — the mapping and design overhead isn't justified there. Don't stick with Transaction Script once duplication has grown substantial and shared business rules keep getting reimplemented slightly differently across transactions — that's the signal to migrate the shared logic (at least) into a Domain Model.

## Key takeaways / mental model
Ask, for your domain: "do multiple transactions genuinely share the same underlying business rules and calculations, and is that sharing likely to grow?" If yes, and if the team has (or can build) the OO design skill, Domain Model's investment pays off. If the domain is simple, or each transaction is largely independent, Transaction Script's simplicity is the better, more proportionate choice.

## Self-check questions
1. Using the order-processing example, explain precisely what duplication risk Transaction Script has that Domain Model resolves, and where that duplication would show up as the system grows.
2. Describe a real or hypothetical domain where a pragmatic middle ground (Transaction Script for most transactions, Domain Model for one complex sub-area) would be the right choice, and explain why.
3. What specific new technical problem does choosing Domain Model introduce that Transaction Script mostly avoids? (Hint: see this subject's later lessons.)
4. Give an example of a system that started with Transaction Script and later needed to migrate toward Domain Model as complexity grew. What would that migration look like, at a high level?

## References
- Patterns of Enterprise Application Architecture (Martin Fowler), Chapter 9: "Domain Logic Patterns" (Transaction Script and Domain Model sections).
