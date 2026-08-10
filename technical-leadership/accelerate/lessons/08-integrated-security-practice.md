---
id: accelerate/08
subject: accelerate
title: Security as an integrated delivery practice
slug: integrated-security-practice
status: drafted
mastery:
seniority: staff
source: Accelerate (Forsgren, Humble, Kim), Chapter 6 "Integrating Infosec into the Delivery Lifecycle"
prerequisites: [accelerate/05, accelerate/06, accelerate/07]
created: 2026-08-10
updated: 2026-08-10
---

# Security as an integrated delivery practice

## TL;DR
The research found that involving information security throughout the software delivery lifecycle — rather than as a separate gate at the end — is associated with *both* better delivery performance and better security outcomes. Treating security as a late-stage checkpoint doesn't just slow delivery; the data suggests it produces worse security too, because it's disconnected from the design decisions where security actually gets built in or left out.

## The idea
The traditional model places infosec review as a gate near the end of the pipeline — a security team reviews a nearly-finished feature or a release candidate, finds problems, and sends it back. This model has an intuitive appeal (a dedicated specialist checks the work before it ships) but the research identifies two compounding problems with it: it creates exactly the kind of cross-team, late-stage handoff bottleneck that inflates lead time (`accelerate/03`) the same way disconnected QA does (`accelerate/07`), and, more surprisingly, it doesn't actually produce better security outcomes, because by the time a late-stage review happens, the architectural and design decisions that determine most security properties are already locked in and expensive to change.

The alternative the book's data supports is **integrating security into the delivery lifecycle** the same way testing was integrated in `accelerate/07`: security expertise embedded early (threat modeling during design, security-relevant code review by developers themselves, automated security testing in the CI pipeline) rather than concentrated in a single late gate. This is sometimes labeled "DevSecOps," but the book is precise about the mechanism, not just the buzzword: it's about *when* and *by whom* security work happens, mirroring the same developer-ownership and shift-left logic as test automation.

## How it works

### The core practices the research measured
- **Security review happens as part of the normal development process**, not as a separate release gate — ideally during design/architecture discussions, not after code is written.
- **Developers can perform basic security testing themselves** (e.g., automated static analysis, dependency vulnerability scanning) as part of their normal workflow, without waiting on a separate security team for routine checks.
- **The security team acts as a consultant and enabler** (providing tools, training, and guidance developers can self-serve) rather than as a bottleneck gate that must personally review every change.
- **Security requirements and controls are considered during the design phase**, before implementation, rather than being an afterthought discovered in a late review.

### Worked example — the cost of a late security gate
A team builds a new feature over six weeks. In week six, the security team performs its scheduled review and finds that the feature's data model doesn't adequately isolate tenant data in a multi-tenant system — a design-level issue, not a small code fix. Because it's a design issue discovered after implementation, fixing it properly requires reworking the data model, not just patching a function, adding another 3-4 weeks. If a security-minded reviewer (or the security team itself, briefly) had been part of the initial design discussion in week one, the tenant-isolation requirement would have shaped the schema from the start, at near-zero marginal cost. This illustrates the chapter's core argument: the cost of addressing a security concern grows the later in the lifecycle it's discovered, exactly like the cost curve for correctness bugs that motivates fast test feedback (`accelerate/07`) — except security issues are often more architectural, so the cost curve is even steeper.

### Worked example — self-service security testing
Instead of every pull request waiting in a queue for a security team to manually review it for common issues (SQL injection patterns, outdated dependencies with known CVEs, hardcoded secrets), the security team builds and maintains automated scanners that run in the same CI pipeline as the test suite (`accelerate/07`) — static analysis, dependency vulnerability scanning, secret detection — and gives developers fast, actionable feedback directly in their pull request, the same way a failing unit test would. The security team's time is then freed to focus on the harder, judgment-requiring work (threat modeling for genuinely novel features, responding to real incidents) instead of being a bottleneck for routine, mechanically-detectable issues. This mirrors the shift from QA-owned to developer-owned testing in `accelerate/07` almost exactly — the security team moves from gatekeeper to platform/enabler.

### Why this connects back to the four key metrics
Integrated security removes a cross-team, late-stage handoff from the pipeline (the same lead-time mechanism from `accelerate/03` and `accelerate/07`), and because it catches issues earlier and cheaper, it also tends to reduce the change failure rate (`accelerate/04`) associated with security incidents specifically — a late-discovered security flaw that ships is a change failure with especially high cost (data breach, compliance violation) compared to an ordinary bug.

## Pros
- Removes a late-stage, high-friction cross-team gate from the delivery pipeline, directly improving lead time the same way integrated testing does.
- Catches security issues while they're still cheap to fix (at design time) rather than after implementation, when fixes are architecturally expensive.
- Frees the security team's specialist time for genuinely hard problems instead of routine, automatable checks, which is also a better use of scarce security expertise.

## Cons
- Requires developers to gain baseline security literacy (common vulnerability classes, secure defaults) that they may not currently have — a real training investment, not just a process change.
- Security teams may resist shifting from a gatekeeper role to an enablement role, especially if organizational incentives (audit requirements, compliance sign-off structures) are built around a formal, centralized approval step.
- Self-service automated scanning tools (SAST, dependency scanners) produce false positives that, if not tuned, can create noise developers learn to ignore — echoing the same flaky-test trust problem from `accelerate/07`, now applied to security tooling.

## Alternatives
- **Centralized late-stage security review (traditional model)** — the status quo this chapter argues against; provides a clear, auditable single checkpoint, which some compliance regimes are built around, but the research associates it with worse lead time and no better (often worse) security outcomes.
- **Bug bounty / external penetration testing programs** — valuable as an additional, periodic outside-in check, but operates on a much longer cycle than integrated per-change security and doesn't replace the need for security-aware design at build time.
- **Security champions model** — a hybrid where each team designates a developer with extra security training as a local point of contact, bridging the central security team and day-to-day development; complements rather than replaces the automated self-service tooling this lesson describes.

## When to use it
Integrate security practices into the pipeline (design-time threat modeling, self-service automated scanning in CI, developer security training) for any system that currently routes security review through a late, centralized gate and is trying to improve lead time or reduce security-related change failures.

## When NOT to use it
Don't fully remove centralized security expertise from novel, high-risk designs (e.g., a new authentication system, a new cross-border data flow) — self-service automated scanning catches known, mechanical issue classes well, but genuinely novel threat modeling still benefits from a security specialist's judgment; the goal is to route the *routine* work to automation and self-service, not to eliminate specialist involvement in genuinely hard cases. In heavily regulated contexts with a hard compliance requirement for a specific formal sign-off step, that step may need to remain even as you add earlier, integrated security work around it — the two are not mutually exclusive.

## Key takeaways / mental model
Security has the same cost-of-late-discovery curve as correctness bugs, but steeper, because security issues are more often architectural. The fix is the same shift-left logic as `accelerate/07`: move security work as early as possible (design-time threat modeling) and make routine checks self-service and automated (CI-integrated scanning), reserving scarce specialist time for genuinely hard, novel judgment calls.

## Self-check questions
1. Using the multi-tenant data isolation worked example, explain why discovering a security design flaw in week six costs more to fix than discovering it in week one. What general principle does this illustrate?
2. Compare the shift described in this lesson (security team: gatekeeper -> enabler) to the shift in `accelerate/07` (QA: separate reviewer -> developer-owned tests). What's structurally the same about both changes?
3. A security team lead worries that self-service scanning tools will let developers ship insecure code without oversight. What would you say to address that concern, using this lesson's distinction between routine and novel security work?
4. Name one context where a centralized, formal security sign-off gate should probably still remain even after adopting this lesson's practices, and explain why.

## References
- Accelerate: The Science of Lean Software and DevOps (Forsgren, Humble, Kim), Chapter 6: "Integrating Infosec into the Delivery Lifecycle".
