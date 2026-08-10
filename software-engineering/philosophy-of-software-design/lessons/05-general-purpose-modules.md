---
id: philosophy-of-software-design/05
subject: philosophy-of-software-design
title: General-Purpose Modules Are Deeper
slug: general-purpose-modules
status: drafted
mastery:
seniority: senior
source: A Philosophy of Software Design, 2nd ed. (John Ousterhout), Chapter 6
prerequisites: [philosophy-of-software-design/03]
created: 2026-08-10
updated: 2026-08-10
---

# General-Purpose Modules Are Deeper

## TL;DR
A somewhat-general-purpose module — one whose interface is defined by the underlying functionality rather than by the exact needs of its current single caller — tends to be deeper (simpler interface relative to what it does) and more reusable than a module built to match one specific use case exactly. Ousterhout's specific guidance: lean slightly general, but stop well short of speculative, imagined-future-need generality.

## The idea
When building a module for a specific, immediate need, there's a natural pull toward making its interface match that need exactly — a function called `getUserEmailForWelcomeMessage()` that does precisely and only what the welcome-message feature currently requires. This chapter argues that pull, followed too literally, tends to produce shallow modules (`philosophy-of-software-design/03`): the interface ends up encoding incidental facts about the *current caller's specific situation* rather than the underlying, more stable functionality — which means every *new* caller with a slightly different need either can't reuse the module at all, or has to bend their situation awkwardly to fit an interface that was never designed with them in mind.

**Somewhat general-purpose**: design the interface around what the underlying functionality actually *is*, at a level of generality that serves the current need cleanly while also naturally covering nearby, easily-foreseeable variations — without trying to anticipate every conceivable future need (which risks `pragmatic-programmer/05`'s "abstraction-itis").

## How it works

### The specific-vs-general trade-off, made concrete
**Worked example — before (interface shaped by one specific caller's exact need):**
```
def get_user_email_for_welcome_message(user_id):
    user = db.get_user(user_id)
    if user.email_verified:
        return user.email
    return None
```
This function's name and behavior are entirely tied to one specific caller's specific purpose (the welcome-message feature). A second feature that also needs "a verified user's email, for a different notification" cannot reuse this function without either duplicating nearly-identical logic (echoing `pragmatic-programmer/03`'s DRY concern) or awkwardly repurposing a function whose name and framing don't match its new use.

**After (somewhat general-purpose, matching the actual underlying functionality):**
```
def get_verified_email(user_id):
    user = db.get_user(user_id)
    return user.email if user.email_verified else None
```
The renamed, reframed function now matches what it actually *does* ("get a verified email"), independent of any particular caller's specific downstream purpose — both the welcome-message feature and any future notification feature can call it directly, with no bending required, because the interface was designed around the underlying functionality rather than around one caller's framing of it.

### Where to stop — avoiding speculative generality
The chapter is explicit that "somewhat general-purpose" has a ceiling: don't add configuration options, parameters, or flexibility for needs that are only imagined, not actually present or clearly foreseeable — this is exactly `pragmatic-programmer/05`'s reversibility caution and `clean-code/12`'s speculative-generality smell, restated here specifically in the context of interface design for reusable modules. A module built to handle every conceivable future variation, with a dozen optional parameters covering cases nobody has actually asked for yet, is *not* what this chapter recommends — that's over-generalization, and it produces its own kind of shallow, hard-to-use interface (too many options to reason about, most of which are dead weight for the actual, current callers).

**Worked example of over-generalization to avoid.** Building `get_verified_email` further into `get_user_field(user_id, field_name, require_verified=False, fallback=None, transform_fn=None)` — anticipating hypothetical future needs ("what if someone wants an unverified phone number with a custom transform") that nobody has actually asked for — produces an interface that's *more* complex to learn and use correctly than the simple, "somewhat general" version, for zero present benefit. This is over-shooting the actual sweet spot the chapter is arguing for.

### The test: does generality follow from the functionality, or from imagined future callers?
A practical way to tell the difference: ask whether the more general interface is more general because it accurately reflects **what the underlying operation fundamentally is** (get a verified email — a real, stable, nameable operation independent of any specific caller), versus because it's trying to **pre-anticipate hypothetical future callers' hypothetical needs** (a field-and-transform-function generic accessor, built speculatively). The former tends to genuinely deepen a module; the latter tends to just add unused surface area.

### Reusability as a byproduct, not the primary goal
A subtle but important framing point: the chapter doesn't argue you should design for reuse as an explicit, primary goal (which tends to produce exactly the speculative over-generalization above) — it argues that designing an interface around the *actual underlying functionality*, thought through carefully, tends to *produce* reusability as a natural side effect, because a well-conceived, accurately-named operation is simply more likely to match a future need than one shaped narrowly around today's single specific caller's incidental framing.

## Pros
- Modules designed around underlying functionality rather than one caller's specific framing tend to be reusable without modification by future, related callers.
- Avoids the shallow-module trap of an interface too narrowly tied to one caller's incidental context (`philosophy-of-software-design/03`).
- The "functionality-driven, not speculation-driven" test gives a concrete way to distinguish healthy generality from harmful over-engineering.

## Cons
- Judging the right level of generality requires real design experience and domain knowledge — get it wrong in either direction (too narrow, or speculatively too broad) and you pay a real cost either way.
- A "somewhat general" interface, designed without a second real caller yet in hand, is still a bet on what generality will actually be useful — sometimes wrong, requiring rework once a genuinely different second use case appears.
- This principle can be in tension with delivering the current feature as fast as possible (echoing `philosophy-of-software-design/02`'s tactical-vs-strategic trade-off) — thinking through the "actual underlying functionality" properly takes more upfront time than just matching the immediate need literally.

## Alternatives
- **Rule of Three** (echoing `pragmatic-programmer/03`) — defer generalizing at all until a genuine third occurrence of a similar need appears, avoiding any generality bet until it's empirically justified rather than designed in advance.
- **YAGNI ("You Aren't Gonna Need It")** — a stronger, more skeptical stance than even "somewhat general," pushing toward the narrowest interface that satisfies the current need, revising only once a second need genuinely materializes.
- **Domain-driven naming and modeling** (see `domain-modeling/ddd-evans`) — a complementary, more structured way to arrive at "what is the underlying functionality actually called and shaped like," grounded in how domain experts themselves talk about the concept, rather than purely a design intuition.

## When to use it
Apply "design around the actual underlying functionality" when building any module you reasonably expect a second, related caller to eventually need — take the small extra time to name and frame the interface around what the operation fundamentally *is*, not around your current caller's specific incidental context.

## When NOT to use it
Don't add configuration/flexibility for needs that are only imagined, not observed or clearly foreseeable — that's the over-generalization failure mode this chapter explicitly warns against, not the "somewhat general" sweet spot it recommends. For genuinely one-off, unlikely-to-be-reused code, matching the immediate need exactly is simpler and entirely appropriate.

## Key takeaways / mental model
When naming and shaping a new module's interface, ask: "what is this operation actually, fundamentally doing, independent of my current caller's specific situation?" Design to that answer — not to an imagined future caller's imagined future needs, and not merely to your current caller's incidental framing.

## Self-check questions
1. Using the `get_verified_email` example, explain specifically what made the "before" version shallow and tied to one caller, and what the "after" version changed.
2. Give an example of over-generalization from real code you've seen — a module built with speculative flexibility nobody has actually used. What would the "somewhat general" version have looked like instead?
3. Why does the chapter argue reusability should be a byproduct of good functionality-driven design, rather than a primary, explicit design goal?
4. Describe a case where the Rule of Three (deferring generalization until a real third use case appears) would be a safer choice than trying to design "somewhat general" upfront.

## References
- A Philosophy of Software Design, 2nd ed. (John Ousterhout), Chapter 6: "General-Purpose Modules Are Deeper".
