---
id: clean-code/02
subject: clean-code
title: Meaningful Names
slug: meaningful-names
status: drafted
mastery:
seniority: junior
source: Clean Code (Robert C. Martin), Chapter 2
prerequisites: [clean-code/01]
created: 2026-08-10
updated: 2026-08-10
---

# Meaningful Names

## TL;DR
A name should tell the reader why it exists, what it does, and how it's used — without needing a comment to fill the gap. Naming is cheap to fix and expensive to leave wrong, because a misleading or vague name actively misdirects every future reader's mental model of the code.

## The idea
Names are the most frequent form of communication in code — more frequent than comments, more frequent than documentation, because every variable, function, class, and parameter is a naming decision, and there are far more of those in any program than there are comments or docs. A vague name (`data`, `temp`, `flag`, `process()`) forces every reader to go read the implementation just to find out what it actually means — paying the reading cost (see `clean-code/01`) that a better name would have avoided entirely. A misleading name is worse: it actively lies, sending the reader's mental model in the wrong direction, and the bug that results from a reader trusting a wrong name can be far more expensive than the bug that results from having no name-based information at all.

## How it works

### Use intention-revealing names
A name should answer, without needing to open the implementation: why does this exist, what does it do, how is it used?

**Worked example — before:**
```
int d; // elapsed time in days
```
The comment is doing the job the name should be doing. **After:**
```
int elapsedTimeInDays;
```
Now the comment is unnecessary — the name itself carries the information, and unlike a comment, the name cannot silently drift out of sync with the code the way a comment can (see `clean-code/04` on comments) because the name *is* what the reader and every caller actually interacts with.

### Avoid disinformation
Don't use names that carry an established meaning that contradicts what the thing actually is. A variable named `accountList` that's actually a `Set`, not a `List`, misleads any reader who (reasonably) assumes list semantics (ordering, duplicates allowed) and writes code that silently breaks those assumptions. Similarly, avoid names that differ only in ways easy to miss visually (`XYZControllerForEfficientHandlingOfStrings` vs. `XYZControllerForEfficientStorageOfStrings`) — a reader skimming code will not reliably catch a difference buried in the middle of a long, similar-looking name.

### Make meaningful distinctions — don't pad names to satisfy a compiler
Names like `a1`, `a2`, ... `aN`, or `ProductInfo` vs. `ProductData` (where "Info" and "Data" carry no actual distinguishing meaning), are **noise words** — they satisfy uniqueness requirements without adding information, and worse, they imply a distinction exists when it doesn't, prompting a reader to hunt for a difference that isn't there.

### Use pronounceable, searchable names
`genymdhms` (generation date, year, month, day, hour, minute, second) is unpronounceable and forces every conversation about it into spelling it out letter by letter. Single-letter names and magic numbers are also **unsearchable** — searching a codebase for `7` to find where a timeout constant is used returns useless noise, while searching for `MAX_RETRY_ATTEMPTS` returns exactly the relevant occurrences. As a rule of thumb from the book: **the length of a name should correspond to the size of its scope** — a loop counter `i` in a five-line loop is fine (its entire meaning is visible in the tiny scope it lives in), but a class-level field or anything visible across a large scope needs a name descriptive enough to stand on its own far from its declaration.

### Avoid encodings (Hungarian notation, member prefixes) that modern tooling makes obsolete
Older conventions encoded type or scope into the name itself (`strName`, `m_balance`, `IShape` for interfaces) because editors couldn't reliably show that information otherwise. Modern IDEs show type information, member-vs-local status, and interface implementations directly and reliably — encoding that same information redundantly into the name adds visual noise and, worse, becomes actively wrong (disinformation) the moment a type changes and the encoded prefix isn't updated to match.

### Class names are nouns, method names are verbs
A class should be named with a noun or noun phrase describing what it *is* (`Customer`, `WikiPage`, `AccountParser`) — a class named with a verb (`Manager`, `Processor`, `Handler` used as the *entire* name with no noun) tends to signal a class with no clear single responsibility, foreshadowing `clean-code/10`'s cohesion discussion. A method should be named with a verb or verb phrase describing what it *does* (`postPayment`, `deletePage`, `save`) — a method named as a noun (`accountBalance()` when it actually mutates state) misleads the reader about whether calling it is safe/idempotent.

### One word per concept, consistently
Pick one word for one abstract concept and stick to it across the entire codebase: don't use `fetch`, `retrieve`, and `get` interchangeably for the same kind of operation on different classes — that inconsistency forces the reader to learn and remember an arbitrary per-class vocabulary instead of one consistent one. Conversely, don't reuse the same word for genuinely different concepts (overloading `add` for both "insert into a collection" and "sum two numbers" on unrelated classes) — that's the disinformation problem again, in the opposite direction.

**Worked example — a naming pass on a real function signature:**
```
// Before
def proc(l):
    r = []
    for x in l:
        if x[4] == 1:
            r.append(x)
    return r

// After
def select_active_users(users):
    active_users = []
    for user in users:
        if user.is_active:
            active_users.append(user)
    return active_users
```
The "before" version requires reading and mentally decoding what `l`, `x[4] == 1`, and `r` mean — probably by cross-referencing wherever `proc` is called and wherever the list elements are constructed. The "after" version needs no cross-referencing at all; the intent is legible on its own, entirely from names.

## Pros
- Good names eliminate an entire category of "go read the implementation to understand this" friction, directly reducing the reading cost from `clean-code/01`.
- Consistent, searchable, pronounceable names make code reviewable in conversation and greppable across a large codebase.
- Naming is one of the cheapest clean-code investments — renaming is usually a safe, mechanical, low-risk change (especially with IDE rename-refactoring tools), unlike restructuring logic.

## Cons
- Finding a genuinely good name takes real thought and sometimes several attempts — it's easy to underinvest in naming under time pressure precisely because it looks like a small, low-stakes decision.
- Consistency requires team-wide discipline (a shared vocabulary) that erodes without active maintenance, especially across a large team or a long-lived codebase with turnover.
- Overly long, maximally descriptive names in narrow, short-lived scopes can hurt readability by cluttering lines — the "match name length to scope" rule needs judgment, not a fixed character-count rule.

## Alternatives
- **Domain-driven naming (ubiquitous language)** — go further than generic "good naming" by deliberately mining and using the exact vocabulary domain experts use, so code and business conversation share the same terms — a deeper, more structured version of this lesson's principles; see `domain-modeling/ddd-evans`.
- **Type-driven self-documentation** — in strongly-typed languages, let precise types (`Meters` instead of `float`, `UserId` instead of `int`) carry some of the meaning a name would otherwise have to, reducing reliance on naming discipline alone.
- **Comments as a naming substitute** — explicitly discouraged by the book (see `clean-code/04`): a comment explaining what a poorly-named thing means is strictly worse than naming it well in the first place, since the comment can silently drift out of sync while the name cannot.

## When to use it
Apply careful naming to everything with a scope wider than a few lines — function names, class names, parameters, and any variable that outlives a tiny, immediately-visible block. Revisit a name the moment you notice yourself wanting to explain it in a comment or in conversation — that's the signal the name itself isn't carrying enough meaning.

## When NOT to use it
Don't over-engineer names for genuinely trivial, tiny-scope variables (a loop index in a three-line loop, a lambda parameter used once) — matching name length to scope means brevity is correct there, not a compromise.

## Key takeaways / mental model
Before finalizing any name, ask: "if someone saw only this name, with zero other context, would they correctly guess what it is, what it does, and how to use it?" If the honest answer requires "well, you'd also need to know that..." — that's exactly the information the name is currently failing to carry, and exactly what a comment would otherwise have to compensate for.

## Self-check questions
1. Take a poorly-named variable or function from code you've written and rewrite its name using this lesson's criteria. What information does the new name carry that the old one didn't?
2. Explain why Hungarian-notation-style type prefixes (`strName`) are now considered harmful rather than helpful, given modern tooling.
3. Why is `accountList` disinformation if the underlying collection is actually a `Set`? What concrete bug could that mismatch cause?
4. Give an example of a name from your own code with a scope-length mismatch (either too short for its scope, or too long for how small its scope is).

## References
- Clean Code: A Handbook of Agile Software Craftsmanship (Robert C. Martin), Chapter 2: "Meaningful Names".
