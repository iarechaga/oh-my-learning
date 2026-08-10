---
id: philosophy-of-software-design/06
subject: philosophy-of-software-design
title: Pulling Complexity Downward
slug: pulling-complexity-downward
status: drafted
mastery:
seniority: senior
source: A Philosophy of Software Design, 2nd ed. (John Ousterhout), Chapter 8
prerequisites: [philosophy-of-software-design/03]
created: 2026-08-10
updated: 2026-08-10
---

# Pulling Complexity Downward

## TL;DR
When a piece of complexity must exist somewhere, it's usually better handled once, inside a lower-level module that can absorb it fully, than pushed up to be handled repeatedly by every one of that module's callers. Ousterhout frames this as a deliberate, sometimes counterintuitive trade-off: a module's *implementer* absorbing a bit more complexity to spare *many* callers from each having to handle it themselves is almost always a net win, because the cost is paid once and the benefit is multiplied by every caller.

## The idea
Some complexity is genuinely unavoidable — it reflects a real requirement or a real messiness in the underlying problem (echoing `code-complete/02`'s essential complexity). The question this chapter asks isn't "how do we eliminate this complexity" (sometimes you can't) but **"who should be responsible for handling it — the one module that could absorb it once, or the many callers who would otherwise each have to handle it themselves, redundantly?"**

The chapter's default answer, stated as a general design bias rather than an absolute rule: push complexity **downward and inward**, toward the implementer of a lower-level module, and away from the many callers who would otherwise each need to deal with it. A small amount of extra complexity in one place, paid once by someone who deeply understands that module, is a better trade than the same complexity multiplied across every caller, most of whom don't (and shouldn't need to) understand it as deeply.

## How it works

### The default configuration problem — a canonical example
A module requiring configuration has a choice: require every caller to explicitly supply every configuration value (pushing the complexity of "what are sensible values" up to every caller), or provide sensible defaults internally so most callers can ignore configuration entirely, while still allowing callers with genuinely unusual needs to override specific values.

**Worked example.**
```
# Complexity pushed UP to every caller — most callers don't actually care about these details
def create_http_client(timeout_ms, max_retries, retry_backoff_ms, connection_pool_size):
    ...

# Complexity pulled DOWN into the module, absorbed once by its implementer
def create_http_client(timeout_ms=5000, max_retries=3, retry_backoff_ms=200, connection_pool_size=10):
    ...
```
The second version required its implementer to think carefully, once, about what sensible defaults actually are for typical usage (a real, nontrivial design task — someone has to have genuine expertise to pick good defaults) — but every caller who doesn't have an unusual need can now simply call `create_http_client()` with zero arguments, entirely unburdened by configuration complexity that would otherwise have been pushed onto every one of them redundantly.

### Handling special cases internally, rather than exposing them to every caller
A closely related application: if a module's underlying operation has a special case (an edge condition, an unusual input shape), handling that special case *inside* the module — so it presents one clean, uniform behavior to callers — is usually better than requiring every caller to detect and separately handle the special case themselves.

**Worked example.** A text-editor's "delete selection" operation has a special case: if the selection is empty (cursor with no actual selection), the "delete" should be a no-op rather than an error. Pushing this complexity up would mean every single call site that might delete a selection needs its own `if selection.is_empty(): return` guard before calling delete. Pulling it down means the `delete_selection()` method itself checks for the empty case internally and simply does nothing in that case — every caller can call `delete_selection()` unconditionally, with the special case fully absorbed exactly once, inside the one module that owns the operation.

### Where NOT to pull complexity down — the exception that proves the rule
The chapter is careful to note this is a bias, not an absolute: pulling complexity down is the right move specifically when the module implementer can genuinely absorb it well (has the context and expertise to make good decisions on behalf of callers) and when doing so doesn't hide something callers genuinely need visibility into to make their own correct decisions. If a caller genuinely needs fine-grained control over a specific behavior (say, a caller with an unusually strict latency requirement that really does need to configure `timeout_ms` precisely), the module should still expose that as an *override*, not force every caller through a one-size-fits-all default that can't be adjusted — the "pull complexity down" bias is about *sensible defaults absorbing the common case*, not about *removing configurability entirely* for callers who genuinely need it.

### Configuration parameters as a symptom worth scrutinizing
A related, sharper point: every configuration parameter a module exposes is, in a sense, complexity the implementer chose *not* to absorb, pushed instead onto every caller who must now understand and correctly set that parameter. This doesn't mean configuration parameters are always wrong — sometimes callers genuinely differ enough that no single default serves everyone — but it does mean each parameter deserves scrutiny: "could I make a sensible decision here myself, on behalf of most callers, rather than asking every one of them to decide?" A module with a dozen required parameters, most of which have an obviously-usually-correct value, has generally failed to pull enough complexity downward.

## Pros
- Concentrates the cost of handling real, unavoidable complexity in one place (the module's implementation), paid once by someone with the most context, rather than redundantly by every caller.
- Produces simpler, easier-to-use call sites for the common case, directly supporting `philosophy-of-software-design/03`'s deep-module goal.
- Sensible defaults with override capability preserve flexibility for genuinely unusual callers without burdening the typical ones.

## Cons
- Requires the module's implementer to have genuine expertise to make good decisions on behalf of many callers — a poorly-chosen default absorbed "downward" can be worse than transparent, caller-supplied configuration if the implementer's assumptions don't actually hold broadly.
- Can obscure genuinely important information from callers who *do* need visibility into a decision to make their own correct choices — pulling complexity down too aggressively risks hiding something that shouldn't have been hidden.
- Absorbing more complexity into a lower-level module can make that module itself larger and more intricate internally, a real cost that's easy to underweight since it's paid by fewer people (the module's own maintainers) than the benefit it produces (spread across many callers).

## Alternatives
- **Fully explicit, caller-driven configuration with no defaults** — maximizes caller control and transparency, at the cost of pushing complexity onto every caller, appropriate specifically when callers genuinely differ enough that no sensible default exists.
- **Convention over configuration** (a related, framework-level design philosophy, common in frameworks like Ruby on Rails) — a stronger, more systemic version of pulling complexity down, where an entire framework's defaults absorb decisions so thoroughly that configuration is rarely needed at all.
- **Progressive disclosure of complexity** — expose a simple default path for common cases while making advanced configuration available but clearly separated (e.g., an "advanced options" section), a middle-ground technique achieving both simplicity for common callers and full control for unusual ones.

## When to use it
Pull complexity downward whenever a module's implementer can make a genuinely good decision on behalf of most callers, especially for configuration defaults and internal handling of predictable special cases. Scrutinize every required parameter and every "callers must handle this special case themselves" pattern as an opportunity to check whether the complexity could instead be absorbed once, internally.

## When NOT to use it
Don't pull complexity down when doing so would hide a decision that genuinely varies enough across callers that no single default serves the majority well, or when it would hide information a caller genuinely needs to make their own correct decision. Don't over-invest in absorbing complexity for a module with very few, very similar callers where the "many callers" multiplier this chapter relies on doesn't actually apply.

## Key takeaways / mental model
For every piece of unavoidable complexity in a module, ask: "should I absorb this once, here, or should I push it up to be handled repeatedly by every caller?" Default toward absorbing it yourself when you can make a genuinely good decision on callers' behalf — but keep an explicit override available for the callers who genuinely need one.

## Self-check questions
1. Using the HTTP client example, explain what complexity was pulled downward and who benefits from that choice, and at what cost to the implementer.
2. Describe a special case in your own code that's currently handled by every caller separately, and sketch how pulling it down into the module itself would look.
3. Why is a long list of required configuration parameters a symptom worth scrutinizing under this chapter's framework?
4. Give an example of a case where pulling complexity down would be the WRONG choice, because callers genuinely need visibility into or control over the decision.

## References
- A Philosophy of Software Design, 2nd ed. (John Ousterhout), Chapter 8: "Pull Complexity Downwards".
