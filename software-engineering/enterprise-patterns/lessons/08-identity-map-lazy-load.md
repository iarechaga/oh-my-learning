---
id: enterprise-patterns/08
subject: enterprise-patterns
title: Identity Map and Lazy Load
slug: identity-map-lazy-load
status: drafted
mastery:
seniority: senior
source: Patterns of Enterprise Application Architecture (Martin Fowler), Chapter 11
prerequisites: [enterprise-patterns/07]
created: 2026-08-10
updated: 2026-08-10
---

# Identity Map and Lazy Load

## TL;DR
Identity Map ensures each database row is loaded into exactly one, shared in-memory object per business transaction — asking for the same row twice returns the *same* object instance, not two independent copies — preventing update conflicts and wasted queries. Lazy Load defers loading a related object's data until it's actually accessed, avoiding the cost of loading a large object graph when only a small part of it is actually needed.

## The idea
Both patterns address efficiency and correctness problems that emerge specifically once you're loading and navigating a real object graph (as Data Mapper, `enterprise-patterns/06`, and a rich Domain Model, `enterprise-patterns/02`, both do) — problems that don't arise the same way in simpler patterns like Table Module, which don't build individually-instantiated, richly-linked object graphs in the first place.

## How it works

### Identity Map — one row, one object, per transaction
Without an Identity Map, loading the same customer row twice within one business transaction (once via a direct lookup, once via navigating from an `Order`'s `customer` reference) would naively create two *separate* `Customer` object instances, each independently representing the same underlying row — a direct instance of `refactoring/07`'s value-versus-reference-semantics concern: if code modifies one instance (say, applying a discount) and the *other* instance later gets saved, unaware of the first instance's change, the first change is silently lost, overwritten by the second instance's stale data.

**Worked example — the bug Identity Map prevents.**
```
# Without Identity Map:
customer_a = customer_mapper.find(42)     # loads a NEW Customer instance
customer_a.apply_discount()                # modifies customer_a only

order = order_mapper.find(101)
customer_b = order.customer                 # a SEPARATE, independently-loaded Customer instance for the SAME row 42!
customer_b.credit_limit = 5000              # modifies customer_b, unaware customer_a exists

uow.commit()   # which change wins? customer_a's discount, or customer_b's credit limit change?
               # depends on save order — a genuine, silent data-consistency bug
```
**With an Identity Map:**
```
class IdentityMap:
    def __init__(self): self._map = {}
    def get(self, cls, id): return self._map.get((cls, id))
    def add(self, obj, id): self._map[(obj.__class__, id)] = obj

class CustomerMapper:
    def find(self, id, identity_map):
        existing = identity_map.get(Customer, id)
        if existing: return existing               # SAME instance returned, not a new one
        row = db.query("SELECT * FROM customers WHERE id = ?", id)
        customer = Customer(row["name"], row["credit_limit"], row["is_vip"])
        identity_map.add(customer, id)
        return customer
```
Now `customer_a` and `customer_b` (loaded via `order.customer`, assuming the Mapper checks the Identity Map before creating a new instance) are the *same* object — a discount applied via one reference is immediately visible via the other, because there's genuinely only one `Customer` object in memory for row 42, eliminating the silent-overwrite bug entirely, by construction rather than by careful discipline.

### Lazy Load — defer loading until actually needed
A rich object graph (a `Customer` with `orders`, each `Order` with `line_items`, each `line_item` with a `Product`) can be expensive to load fully and eagerly every time you just need the `Customer`'s name — Lazy Load defers fetching a related object's data until the code actually accesses it, avoiding wasted queries for data that turns out never to be used in a given code path.

**Worked example.**
```
class Customer:
    def __init__(self, id, name, mapper):
        self.id, self.name = id, name
        self._mapper = mapper
        self._orders = None            # NOT loaded yet
    @property
    def orders(self):
        if self._orders is None:                       # loaded on FIRST access, not at construction
            self._orders = self._mapper.find_orders_for(self.id)
        return self._orders

customer = customer_mapper.find(42)     # only customer's own fields queried so far
print(customer.name)                     # no orders query triggered
print(customer.orders)                   # NOW the orders query runs, on first actual access
```
If a given code path only ever needs `customer.name` and never touches `customer.orders`, Lazy Load means the (potentially expensive) orders query never runs at all — a direct efficiency win, especially valuable for object graphs with many, potentially deep relationships where eagerly loading everything "just in case" would be wasteful for the common case that only needs a small part of the graph.

### The N+1 query problem — Lazy Load's most notorious failure mode
Lazy Load's convenience has a well-known, costly trap: if code iterates over a list of objects and accesses a lazy-loaded relationship on *each one* inside the loop, you get one query to load the list, plus one *additional* query per item to lazy-load each item's relationship — the infamous "N+1 queries" problem.

**Worked example of the trap.**
```
customers = customer_mapper.find_all()    # 1 query, loads 100 customers
for customer in customers:
    print(customer.orders)                  # triggers 1 query PER customer — 100 additional queries!
# total: 101 queries, where a single well-designed JOIN query could have done it in 1
```
This is precisely why understanding Lazy Load's mechanics matters practically, even when using an ORM that provides it automatically — recognizing the N+1 pattern, and knowing to reach for **eager loading** (explicitly requesting related data upfront, via a JOIN or a batch query) specifically for code paths that *will* need the related data for every item in a collection, is essential, evidence-based tuning (echoing `code-complete/14`'s measure-first discipline) rather than something to leave entirely to Lazy Load's default, convenient-but-sometimes-costly behavior.

## Pros
- Identity Map eliminates an entire class of silent data-consistency bugs caused by multiple, independently-loaded, inconsistently-updated copies of the same underlying row.
- Lazy Load avoids the cost of eagerly loading large object graphs when only a small part is actually needed for a given code path.
- Both patterns are typically provided automatically by mature ORMs, meaning most developers benefit from them without hand-implementing either — but understanding both explains real, common ORM behaviors and failure modes (like N+1 queries) that are otherwise mysterious.

## Cons
- Identity Map requires careful scoping (typically to one business transaction/request) — sharing an Identity Map across unrelated transactions risks stale data or unexpected object sharing across logically-unrelated operations.
- Lazy Load's convenience directly enables the N+1 query problem, one of the most common and costly performance anti-patterns in real-world ORM-based applications, if not actively watched for.
- Both patterns add real conceptual overhead (an extra map to reason about, deferred-loading semantics that can surprise a developer unfamiliar with them) relative to naive, always-eager, always-fresh-instance loading.

## Alternatives
- **No Identity Map, accepting the risk of duplicate object instances** — simpler, but reintroduces the exact silent-overwrite bug this pattern prevents; rarely a deliberate choice in modern practice, since most ORMs provide Identity Map by default.
- **Eager loading by default, everywhere** — avoids the N+1 problem entirely by always loading full object graphs upfront, at the cost of wasting effort loading data that many code paths never actually use — the opposite trade-off from Lazy Load, appropriate specifically when you know in advance that related data is almost always needed.
- **Explicit, deliberate query design (batch-loading, DataLoader-style patterns)** — a more controlled middle ground, explicitly batching related-object loads for a known collection rather than relying on Lazy Load's implicit, per-item default behavior.

## When to use it
Use Identity Map (typically via your ORM's default session/context behavior) for any system loading and navigating an object graph within a transaction — it's rarely something to deliberately opt out of. Use Lazy Load for relationships that are only occasionally needed, and switch to eager loading specifically for code paths that iterate over a collection and access the same relationship on every item.

## When NOT to use it
Don't rely on Lazy Load's default behavior inside a loop over many objects without checking for the N+1 pattern — that's the single most common, costly mistake this pattern enables. Don't share an Identity Map across unrelated business transactions, which risks unexpected object sharing and stale-data bugs across logically independent operations.

## Key takeaways / mental model
Identity Map: "does loading the same row twice give me the same object, or two independently-drifting copies?" It should always be the same object, within one transaction's scope. Lazy Load: "am I about to access this relationship inside a loop over many items?" If yes, check for N+1 and consider eager loading instead of relying on the default lazy behavior.

## Self-check questions
1. Using the `customer_a`/`customer_b` example, explain precisely how the silent-overwrite bug occurs without an Identity Map, and how the Identity Map prevents it.
2. Walk through the N+1 query example and calculate exactly how many queries run, then explain how eager loading would reduce that count.
3. Why must an Identity Map be scoped to one business transaction rather than shared globally across the whole application's lifetime?
4. Identify a place in code you've worked with where Lazy Load's default behavior either caused (or could have caused) an N+1 query problem, and describe how you'd detect and fix it.

## References
- Patterns of Enterprise Application Architecture (Martin Fowler), Chapter 11: "Object-Relational Behavioral Patterns" (Identity Map and Lazy Load sections).
