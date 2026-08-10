---
id: philosophy-of-software-design/10
subject: philosophy-of-software-design
title: Choosing Names and Consistency
slug: naming-consistency
status: drafted
mastery:
seniority: mid
source: A Philosophy of Software Design, 2nd ed. (John Ousterhout), Chapter 14
prerequisites: [clean-code/02, code-complete/08]
created: 2026-08-10
updated: 2026-08-10
---

# Choosing Names and Consistency

## TL;DR
A vague name doesn't just fail to help — it actively hides the fact that you don't yet have a precise idea of what the thing actually is, and picking a genuinely precise name often exposes a design problem that a vague name would have let you paper over. Consistency (the same name always meaning the same thing, everywhere, and different things always getting different names) is, on its own, nearly as valuable as any individual name's cleverness.

## The idea
`clean-code/02` and `code-complete/08` already covered naming in depth from their respective books' angles. Ousterhout's distinct contribution is a sharper claim about *why* naming difficulty matters: **struggling to find a good name for something is diagnostic, not just annoying.** If you genuinely can't come up with a crisp, honest name for a variable, function, or class, that's frequently a signal that the *thing itself* doesn't have a sufficiently clear, single purpose yet — the naming difficulty is downstream of a design problem, not an independent, purely-verbal one.

## How it works

### Vague names as a symptom, not just a style problem
A name like `data`, `temp`, `helper`, `manager`, or `info` isn't merely unhelpful to a reader (as `clean-code/02` establishes) — Ousterhout pushes further: the difficulty of finding a *better* name for the same thing is itself useful information. If every specific, honest name you try to give a variable or class feels either too narrow (doesn't cover everything it actually holds/does) or too vague (covers everything but says nothing), that's frequently because the variable or class genuinely *is* doing too many unrelated things (echoing `clean-code/10`'s cohesion argument) — and no name, however cleverly chosen, can make a genuinely incoherent responsibility set sound coherent. The fix in that case isn't a better name — it's redesigning the thing so a clean, honest name becomes possible.

**Worked example.** Struggling to name a class that handles user authentication, sends analytics events, and formats email templates — every candidate name (`UserStuff`, `AccountHelper`, `UserManager`) feels unsatisfying because none of them is actually true to what the class does; they're all vague precisely *because* the class's actual responsibility is incoherent (echoing `clean-code/10`'s low-cohesion diagnosis directly). The naming struggle is the symptom; the fix is splitting the class by responsibility (as `clean-code/10` recommends) — at which point each resulting piece (`Authenticator`, `AnalyticsTracker`, `EmailTemplateRenderer`) names itself easily and precisely, because each one now genuinely has one clear job.

### Consistency as a value nearly independent of any individual name's quality
Directly echoing `code-complete/08`'s team-wide consistency argument, but stated more sharply: Ousterhout argues that a *consistent*, if slightly less clever, naming convention beats an *inconsistent* set of individually excellent names, because consistency lets a reader build reliable expectations that transfer across the whole codebase — once a reader learns that this codebase always calls "the number of items" `count` (never `num`, `n`, or `total` interchangeably for the same concept), they can *predict* the name of a new, unfamiliar variable holding that same concept before even looking it up, which is a genuinely different and more valuable kind of understanding than any single well-chosen name provides in isolation.

**Two specific consistency disciplines:**
1. **The same name should always mean the same thing.** If `count` means "number of items" in one class, it shouldn't mean "number of retries" in another, nearby class — even though both are legitimately "a count of something," reusing the exact same bare name for two different specific concepts creates exactly the kind of disinformation `clean-code/02` warns against, now framed as a *consistency* violation specifically.
2. **Different things should always have different names.** If two genuinely different concepts (a database connection's timeout and an HTTP request's timeout) are both just called `timeout` in nearby, easily-confused contexts, a reader loses the ability to tell them apart at a glance — the fix isn't necessarily complex naming, just *differentiated* naming (`db_timeout_ms` and `http_timeout_ms`) so the two concepts remain visually and semantically distinct wherever they appear near each other.

### Names should reflect the abstraction, not the implementation
Extending `philosophy-of-software-design/04`'s information-hiding argument directly into naming: a name that leaks implementation detail (`user_list` for something that's actually backed by a `Set`, or `redis_cache` for a cache whose backing store is an implementation detail that shouldn't be exposed to callers) commits the reader to an implementation fact the interface was supposed to hide — precisely the failure mode `clean-code/02`'s disinformation warning and `philosophy-of-software-design/04`'s leakage diagnostic both flag, but specifically located in the *name itself* as the leak's vehicle, rather than in a method signature or duplicated constant.

## Pros
- Treating naming difficulty as diagnostic gives you an early, cheap signal of design problems (low cohesion, unclear responsibility) before they've caused any other visible harm.
- Codebase-wide consistency lets readers build transferable, predictive expectations, compounding in value as a codebase grows, independent of any single name's individual cleverness.
- Naming for abstraction rather than implementation prevents names from becoming a secondary channel through which information hiding quietly leaks.

## Cons
- Not every naming struggle indicates a genuine design flaw — sometimes a concept is legitimately hard to name well because natural language itself lacks a crisp term for it, even though the underlying design is sound.
- Enforcing consistency across a large, long-lived, multi-contributor codebase requires ongoing vigilance (review, linting, a documented glossary) that's easy to let slip without active maintenance.
- Prioritizing consistency over an individually better-fitting name in a specific case can occasionally produce a slightly awkward name that a reader unfamiliar with the codebase's conventions might not immediately parse as clearly as a from-scratch, context-free name would.

## Alternatives
- **Domain-driven ubiquitous language** (see `domain-modeling/ddd-evans`) — a more structured, deliberately-curated approach to achieving the same consistency goal, grounded specifically in how domain experts talk about the business, rather than purely an engineering-driven convention.
- **Automated naming-convention linting** — mechanically enforces some consistency rules (casing, prefixes/suffixes for booleans per `code-complete/08`) without relying purely on individual developer vigilance or code review to catch drift.
- **A living, actively-maintained project glossary** — an explicit document listing key terms and their precise, agreed meanings, reducing reliance on tacit, distributed knowledge of "what we call this thing" across a growing team.

## When to use it
Treat any prolonged struggle to name something well as a prompt to re-examine the thing's actual design, not just a wordsmithing problem to push through. Apply consistency checks (same name/same meaning, different things/different names) deliberately during code review, especially for concepts that recur across many files or modules.

## When NOT to use it
Don't assume every hard-to-name concept indicates a design flaw — some genuinely coherent, well-designed concepts are just intrinsically hard to name crisply in natural language; use judgment, not a mechanical rule, to distinguish this from a genuine cohesion problem. Don't sacrifice a genuinely much clearer, context-appropriate name purely to match an established but weaker convention if the mismatch is severe enough to actively mislead.

## Key takeaways / mental model
When you're struggling to name something well, don't just push through with a mediocre name — pause and ask whether the difficulty is telling you something about the thing's design, not just about your vocabulary. And treat consistency (same name, same meaning; different things, different names) as valuable in its own right, not merely as a matter of taste.

## Self-check questions
1. Describe a time you struggled to name something and, in hindsight, the struggle was actually revealing a design problem (a class or function doing too much). What was the eventual fix?
2. Give an example from your own code of the same bare name meaning two different things in two different, easily-confused contexts. How would you differentiate them?
3. Why does the book argue codebase-wide consistency can be nearly as valuable as any single name's individual quality?
4. Give an example of a name that leaks implementation detail it shouldn't, and propose a replacement that names the abstraction instead.

## References
- A Philosophy of Software Design, 2nd ed. (John Ousterhout), Chapter 14: "Choosing Names".
- See also: `clean-code/02` (Meaningful Names) and `code-complete/08` (Naming Variables Well) for the complementary naming treatments this chapter builds on.
