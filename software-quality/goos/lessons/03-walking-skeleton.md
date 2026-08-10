---
id: goos/03
subject: goos
title: Walking Skeleton and Deployment Pipeline
slug: walking-skeleton
status: drafted
mastery:
seniority: senior
source: Growing Object-Oriented Software, Guided by Tests (Freeman & Pryce), Part II/Chapter 4
prerequisites: [goos/02]
created: 2026-08-10
updated: 2026-08-10
---

# Walking Skeleton and Deployment Pipeline

## TL;DR
A walking skeleton is the smallest possible implementation of a system that connects all its major architectural pieces (UI, domain, persistence, external integrations) and can be built, tested, and deployed through the real pipeline — before it does anything useful. Build it first, deploy it to a production-like environment on day one, and grow real behavior into it afterward, so that "can we build and ship this system at all" is answered immediately rather than assumed.

## The idea
Freeman & Pryce open Part II of the book with an observation many teams learn the hard way: the mechanics of getting *any* code from a developer's machine into a running, deployed system — build scripts, packaging, configuration, environment setup, the actual deployment mechanism, monitoring hooks — is itself a substantial, risky, and often underestimated piece of engineering. If a team defers this work until "we have something worth deploying," they end up doing deployment engineering under time pressure, late in the project, on top of an already-complex codebase, precisely when they can least afford new surprises.

The walking skeleton is the answer: build an end-to-end path through the system's architecture that does almost nothing functionally interesting, but genuinely exercises every piece of infrastructure the real system will need — and get it through the real build-test-deploy pipeline immediately. This is `goos/02`'s vertical-slicing idea applied at the very first, most minimal possible slice, with an explicit focus on the deployment mechanics rather than just the application layers.

The name is deliberate: a skeleton has the shape of the whole body, with none of the muscle — it can stand and walk, but it can't do useful work yet. The walking skeleton for the auction sniper isn't "the domain model for bidding" — it's something like "a process that starts up, connects to a (possibly fake) auction server, prints something to a log or a trivial UI, and is deployable via the actual CI/CD pipeline the team will use for the rest of the project."

## How it works

### What belongs in a walking skeleton
A walking skeleton needs to include, in some minimal but real form, every category of infrastructure the finished system will depend on:
- **Build and packaging** — the real build tool, producing the real artifact format (a jar, a container image, whatever production will actually run).
- **Automated tests wired into the build** — even if there's only one trivial test, the CI step that runs tests and fails the build on a red test must exist from day one.
- **Deployment mechanism** — the actual scripts or pipeline (not a developer manually copying files) that gets the artifact into a production-like environment.
- **The real external integration points, even if stubbed** — for the sniper, this means actually connecting to the auction house's real (or realistic test) messaging protocol, not a hand-rolled placeholder that has nothing to do with the real protocol's quirks.
- **A minimal but real UI or entry point** — enough to observe that the system is doing *something*, e.g., printing the auction status.

**Worked example.** The sniper's walking skeleton, per the book: a single process that (1) is built via the same build tool the team will use throughout, (2) connects over the auction house's actual XMPP-based messaging protocol to a test auction server, (3) joins one named auction, (4) logs each event it receives (price change, auction closed) to a simple console UI, and (5) is deployed via a real deployment script into a staging environment — with zero bidding logic. This sounds almost trivially small, and it is — but building it surfaces real, specific risks immediately: does the team actually understand the auction protocol's message formats? Does the CI server have network access to reach a test auction instance? Does the deployment script actually work outside a developer's own machine? Each of those questions, if left unanswered until later, could each individually derail a sprint; the walking skeleton answers all of them in the first days.

### Why "deploy it for real" is non-negotiable
A tempting shortcut is to build the skeleton's application code but skip the "actually deploy it through the real pipeline" part, planning to "set up deployment properly later." Freeman & Pryce argue this defeats the purpose: the deployment pipeline is exactly the kind of infrastructure that tends to hide the nastiest, most time-consuming surprises (credentials, network policies, environment differences, missing dependencies on the target machine) — and those surprises don't get smaller by waiting. Deploying the (nearly useless) skeleton for real, from day one, means the team discovers and fixes those problems while the stakes are low, and then every subsequent slice rides an already-proven pipeline instead of accumulating deployment risk silently in the background.

### The walking skeleton is maintained, not thrown away
Unlike a disposable prototype, the walking skeleton is not thrown away once it has "proven the architecture" — it *becomes* the first real slice of the production system (as in `goos/02`'s "join and lose" example), and every subsequent feature is grown into it. This is why Freeman & Pryce insist on real tools and real deployment mechanisms from the start, rather than throwaway shortcuts: shortcuts taken "just for the skeleton" tend to either get left in place (becoming permanent technical debt) or need to be redone properly later (wasting the effort spent building them).

### Distinguishing the walking skeleton from a spike or proof-of-concept
A spike (mentioned in `goos/01`) is explicitly disposable — its purpose is learning, and the code is thrown away once the lesson is learned. A walking skeleton is the opposite: it is production code from the first commit, built with the same care, tests, and review the rest of the system will get, specifically because it will never be replaced, only grown. Confusing the two — treating the skeleton as throwaway, or treating a spike as if it needs production-grade rigor — wastes effort in both directions.

## Pros
- Surfaces deployment and infrastructure risk in the first days of a project, when it's cheap to fix, instead of late, when it's expensive and time-pressured.
- Gives the team (and stakeholders) a real, running, deployed system to observe and build confidence in from the very start, even though it does almost nothing yet.
- Every subsequent feature is added to an already-proven pipeline, so deployment stops being a recurring source of surprise as the project grows.

## Cons
- Building a walking skeleton takes real upfront effort that produces something functionally almost useless, which can be a hard sell to stakeholders expecting visible feature progress immediately.
- If the team gets the architecture badly wrong at the skeleton stage, that mistake is now baked into "production code from day one" rather than isolated in a disposable prototype — so getting the broad architectural shape roughly right still matters.
- Requires access to real (or realistic) external systems and deployment targets from the very start of the project, which isn't always available (e.g., a third-party partner system that isn't ready yet) — in that case, the skeleton has to stub that one piece, accepting the risk stays hidden there a bit longer.

## Alternatives
- **Prototype-then-discard** — build a throwaway proof-of-concept to learn the architecture, then start "real" development from scratch. Learns similar lessons about integration risk but doesn't keep the code or the proven pipeline, so the deployment risk resurfaces when "real" development starts.
- **Defer deployment setup** — build application functionality first, treating deployment as a separate, later concern. The most common alternative in practice; this is precisely the pattern this lesson argues against, because it concentrates deployment risk at the worst possible time.
- **Infrastructure-as-code-first approach** — some teams invest heavily in deployment automation and environment provisioning before writing any application code at all, going further than a walking skeleton by fully productionizing infrastructure before any behavior exists; more thorough but slower to produce any observable system behavior.

## When to use it
Build a walking skeleton at the start of any project with real uncertainty about deployment targets, external integrations, or the team's familiarity with the tech stack — which is most new projects. It's especially valuable when multiple architectural layers (UI, domain, external protocol, persistence) are all unproven simultaneously.

## When NOT to use it
If you're adding a new project to an organization with a mature, well-understood deployment platform and the new system reuses proven patterns end-to-end, a full walking-skeleton exercise may be overkill — you can reasonably start with a thin real feature slice (`goos/02`) without treating deployment itself as a major unknown, since it demonstrably isn't one here.

## Key takeaways / mental model
Ask, on day one of a new system: "if I had to ship something — anything — to production right now, what would stop me?" Build exactly enough to remove every one of those blockers, deploy that through the real pipeline, and only then start adding real behavior. The skeleton proves you *can* ship before you spend weeks building something worth shipping.

## Self-check questions
1. A teammate proposes building the sniper's bidding algorithm first, fully tested in isolation, and "worrying about deployment once it's ready to demo." What specific risks does this ordering leave undiscovered, and when would they likely surface?
2. Explain the difference between a walking skeleton and a throwaway spike, and why that difference changes how much care you put into the skeleton's code quality.
3. Your team's walking skeleton for a new service can't reach a required third-party partner API yet because that partner isn't ready. What would you stub, and what residual risk does that stub leave unaddressed?

## References
- Growing Object-Oriented Software, Guided by Tests (Freeman & Pryce), Part II, Chapter 4: "A Walking Skeleton" and Chapter 5: "Maintaining the Walking Skeleton."
