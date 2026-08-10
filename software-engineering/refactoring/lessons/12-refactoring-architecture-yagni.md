---
id: refactoring/12
subject: refactoring
title: "Refactoring, Architecture, and YAGNI"
slug: refactoring-architecture-yagni
status: drafted
mastery:
seniority: senior
source: Refactoring, 2nd ed. (Martin Fowler), Chapter 2 and 5
prerequisites: [refactoring/11, philosophy-of-software-design/02]
created: 2026-08-10
updated: 2026-08-10
---

# Refactoring, Architecture, and YAGNI

## TL;DR
Refactoring and upfront architectural design are complementary, not competing: continuous refactoring reduces (but doesn't eliminate) the need to get every architectural decision right upfront, because a codebase that's genuinely easy to refactor can evolve its architecture as real requirements emerge, rather than needing to have anticipated them all in advance. YAGNI ("You Aren't Gonna Need It") is the discipline that keeps this virtuous cycle honest — build for today's actual, evidenced needs, trusting that refactoring can get you to tomorrow's design once tomorrow's requirements are actually known, rather than guessed at today.

## The idea
This closing lesson connects refactoring's tactical techniques (covered throughout this subject) to the larger strategic question of how architecture and design decisions get made over a project's life. Fowler's own position, echoing and reinforcing `philosophy-of-software-design/02`'s strategic-investment argument: a codebase where refactoring is cheap and reliable (fast tests, small well-factored pieces, low coupling) doesn't need its architecture to be *correct* from day one — because when a real requirement reveals that an earlier architectural choice no longer fits, refactoring (sustained, per `refactoring/11`, at whatever scale the needed change requires) is the mechanism that gets you from "the design that made sense then" to "the design that makes sense now," incrementally and safely, rather than requiring either a risky big-bang rewrite or living forever with an increasingly poor fit.

**YAGNI**, in this context, is the specific discipline that makes trusting this cycle rational rather than reckless: don't build speculative flexibility for requirements you're *guessing* might arrive — build for what's actually needed *now*, and trust that if a genuinely new requirement does arrive, a well-refactored codebase can evolve to meet it *then*, cheaply, because refactoring is cheap. YAGNI without a genuine, practiced ability to refactor cheaply is just recklessness (building nothing for speculative future needs, with no reliable way to adapt when they arrive); refactoring without YAGNI's discipline just produces speculative, premature abstraction (`pragmatic-programmer/05`, `clean-code/12`) that refactoring never actually needed to happen, because it was guessed rather than evidenced.

## How it works

### Refactoring reduces the cost of an architectural decision being "wrong later," not the cost of it being wrong now
A crucial, precise framing: refactoring doesn't make it *free* to change your mind about architecture — a big refactoring (`refactoring/11`) still takes real, sometimes substantial effort, and some architectural decisions (a chosen primary database at real production scale, per `pragmatic-programmer/05`'s reversibility framing) remain genuinely expensive to reverse even with excellent refactoring discipline. What refactoring changes is the *relative* cost: a codebase with strong tests, small well-factored pieces, and low coupling can absorb an architectural correction far more cheaply than a tangled, untested, tightly-coupled one — which is precisely why investing in refactorability (tests, small deep modules, low coupling) is itself a strategic hedge against the near-certainty that *some* early architectural guesses will turn out wrong.

### YAGNI in practice — the concrete discipline
YAGNI doesn't mean "never think ahead" — it means specifically: **don't build the generalized, flexible version of something until a second, genuinely real, evidenced need for that flexibility actually appears** (the Rule of Three, `refactoring/02`, `pragmatic-programmer/03`, is YAGNI's concrete decision procedure). The discipline requires resisting a specific, seductive argument that recurs constantly in real engineering discussions: "we should build this more flexibly now, because we'll probably need that flexibility later, and it'll be harder to add then." YAGNI's counter, backed directly by this subject's refactoring techniques: if the codebase is genuinely well-factored and well-tested, adding that flexibility *later*, once the need is real and its actual shape is known (rather than guessed), is usually not meaningfully harder — and building it now, before the real need is known, risks guessing wrong about its shape, producing exactly the wrong kind of flexibility (echoing `pragmatic-programmer/05`'s abstraction-itis and `philosophy-of-software-design/05`'s speculative-generality cautions).

**Worked example.** A team debates whether to build a payment module supporting multiple payment providers from day one, "in case we need to add a second provider later," even though only one provider is actually in scope right now. YAGNI's answer: build cleanly for the one provider you actually need now, but keep the module well-factored (small, deep, low-coupling — per `philosophy-of-software-design/03`) so that *when* a second provider genuinely becomes a real requirement, extracting a `PaymentProvider` interface (via `refactoring/06`'s Extract Class/Move Function techniques, now informed by two *real*, concrete providers rather than one imagined and one guessed-at) is a well-understood, evidence-based refactoring — not a redesign from scratch, and very likely a cleaner abstraction than what would have been guessed at upfront with only one real example in hand.

### Refactoring as the mechanism that makes incremental architecture viable at all
`architecture/evolutionary-architectures` (a related subject in the architecture domain) treats "evolvable architecture" as a first-class goal, achieved partly through fitness functions and incremental change management at the system level. This subject's contribution is the code-level mechanism that makes that evolution *actually possible* in practice: an architecture is only genuinely evolvable if the code implementing it can be safely restructured as the architecture evolves — which is exactly what a disciplined refactoring practice, sustained over time (`refactoring/02`'s opportunistic habit, `refactoring/11`'s big-refactoring techniques when needed), provides. Evolutionary architecture at the system level and continuous refactoring at the code level are, in this sense, the same underlying philosophy applied at two different scales.

## Pros
- Strong refactoring discipline reduces the *relative* cost of architectural decisions turning out wrong, making it rational to defer some decisions until real evidence exists rather than guessing upfront.
- YAGNI, backed by genuine refactoring capability, avoids the compounding cost of speculative, wrong-shaped abstractions built on guesses rather than evidence.
- Connects code-level refactoring discipline directly to system-level evolutionary architecture, showing they're the same underlying strategy at different scales rather than unrelated concerns.

## Cons
- YAGNI requires genuine trust that refactoring will actually be cheap when the real need arrives — trust that's only warranted if the codebase's tests and factoring are actually kept healthy in the meantime; YAGNI in a codebase with a weak safety net is a much riskier bet.
- Some architectural decisions are genuinely expensive to reverse even with excellent refactoring discipline (data migrations at scale, cross-team API contracts) — YAGNI's "just refactor later" answer doesn't apply equally well to every kind of decision, and misjudging which category a decision falls into is a real risk.
- The discipline to consistently defer speculative flexibility, resisting the seductive "we'll probably need this" argument, takes real organizational and individual restraint that's easy to abandon under pressure from stakeholders who find "build it flexibly now" intuitively appealing.

## Alternatives
- **Big design up front, minimizing reliance on later refactoring** — appropriate specifically for contexts where requirements are genuinely stable and well-understood, or where the cost of a wrong architectural guess is severe enough that upfront rigor is worth its cost (echoing `code-complete/01`'s doghouse-vs-skyscraper scaling) — the direct alternative to this lesson's incremental-with-refactoring approach.
- **Spike-and-stabilize** — deliberately build a quick, non-refactored exploratory version first (`pragmatic-programmer/06`) specifically to learn the real shape of a requirement, then refactor (or rebuild) properly once that shape is known — a hybrid that front-loads learning before committing to either upfront design or pure incremental evolution.
- **Formal architecture governance with fitness functions** (see `architecture/evolutionary-architectures`) — a more structured, system-level complement to this lesson's code-level discipline, adding automated checks that architectural qualities are preserved as the system evolves incrementally.

## When to use it
Trust YAGNI and defer speculative flexibility whenever your codebase's refactoring safety net (tests, factoring quality) is genuinely strong enough that a later correction, informed by real evidence, would be cheap. Invest deliberately in refactorability itself (tests, small deep modules, low coupling) specifically because it's what makes deferring architectural decisions a rational bet rather than a reckless one.

## When NOT to use it
Don't apply YAGNI to decisions that are genuinely expensive to reverse even with strong refactoring discipline (data model choices at real scale, external-facing contracts with many independent consumers) — these deserve more upfront care precisely because refactoring's usual cost-reduction doesn't apply as fully to them. Don't rely on "we can refactor later" as a justification for skipping test coverage now — that specific combination (weak safety net plus deferred decisions) is the reckless version of YAGNI this lesson explicitly warns against.

## Key takeaways / mental model
Ask, before building speculative flexibility: "if I skip this now and the need turns out to be real later, will my codebase's tests and factoring make that refactoring cheap?" If yes, defer it — YAGNI is a rational bet, not laziness. If the honest answer is no (weak tests, tangled coupling), fix that first, because deferring architectural decisions without a genuine ability to refactor later isn't discipline, it's just risk.

## Self-check questions
1. Using the payment-provider example, explain why building a `PaymentProvider` interface only once a second real provider exists tends to produce a better abstraction than guessing at one upfront.
2. Why does the lesson argue refactoring reduces the *relative*, not the *absolute*, cost of an architectural decision being wrong? Give an example of a decision where even strong refactoring discipline wouldn't fully offset the cost of guessing wrong.
3. Describe the specific combination of circumstances (safety net + deferred decision) that makes YAGNI reckless rather than disciplined, according to this lesson.
4. How does this lesson connect code-level refactoring practice to system-level evolutionary architecture (see `architecture/evolutionary-architectures`)? Are they the same idea at different scales, or genuinely different concerns?

## References
- Refactoring: Improving the Design of Existing Code, 2nd ed. (Martin Fowler), Chapter 2: "Principles in Refactoring" and Chapter 5 (Big Refactorings, architectural implications).
- See also: `philosophy-of-software-design/02` (Working Code Is Not Enough) and `architecture/evolutionary-architectures` for the strategic and system-level counterparts to this lesson's argument.
