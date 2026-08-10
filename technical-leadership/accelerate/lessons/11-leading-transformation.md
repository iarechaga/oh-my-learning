---
id: accelerate/11
subject: accelerate
title: Leading transformation using capability-based interventions
slug: leading-transformation
status: drafted
mastery:
seniority: staff
source: Accelerate (Forsgren, Humble, Kim), Chapter 9 "Leaders and Managers" and Chapter 10 "Conclusion"
prerequisites: [accelerate/05, accelerate/06, accelerate/07, accelerate/08, accelerate/09, accelerate/10]
created: 2026-08-10
updated: 2026-08-10
---

# Leading transformation using capability-based interventions

## TL;DR
The book explicitly rejects maturity-model transformation (a fixed sequence of stages every organization progresses through toward one end state) in favor of a **capability model**: a checklist of roughly two dozen independent, context-specific capabilities (technical, process, cultural — the ones covered across `accelerate/05` through `accelerate/10`) that an organization can invest in based on its own constraints and current bottleneck, in any order, continuously, with no "done" state.

## The idea
Traditional transformation programs (and traditional process-maturity frameworks like CMMI) tend to assume a universal path: every organization moves through the same stages, in the same order, toward the same defined end state, usually assessed by an external audit. This is appealing to executives because it's legible — you can point to "we are at stage 3 of 5" — but the book argues it's the wrong model for two reasons the research surfaces directly: (1) organizations vary enormously in which capability is their actual bottleneck, so a fixed universal sequence wastes effort on capabilities that aren't the constraint for a given org; and (2) there is no final "mature" state to reach — the four key metrics keep improving with continued capability investment, and elite performers keep investing, they don't graduate and stop.

The alternative the book proposes: treat each of the roughly 24 capabilities identified across the research (spanning continuous delivery, architecture, culture, product management, and support for learning) as an *independent lever*, measure where your organization currently stands on each, identify which one is your actual bottleneck given your specific context, invest there, remeasure, and repeat — a continuous, iterative loop rather than a linear program with an end date.

## How it works

### The capability model vs. the maturity model
| | Maturity model | Capability model |
| --- | --- | --- |
| Structure | Fixed stages, universal order | ~24 independent capabilities, any order |
| Assessment | External audit against a defined rubric | Self-assessment against your own current bottleneck |
| End state | A defined "mature" level to reach | None — continuous improvement, ongoing investment |
| Context sensitivity | Low — same path prescribed for every org | High — invest based on your specific constraint |

### Worked example — why order matters, and why it's context-specific, not universal
An organization with a tightly coupled legacy architecture (`accelerate/06`) that tries to adopt trunk-based development and aggressive deployment frequency (`accelerate/05`) before addressing coupling will find every attempted small, independent deployment still requires coordinating with three other teams — the practice doesn't take hold because the architectural prerequisite isn't there yet. For this organization, architecture is the bottleneck capability, and it should be invested in first, even though "continuous delivery practices" might be a fine starting point for a different organization that already has loosely coupled systems but weak test automation instead. A universal maturity-model sequence (e.g., "stage 1: adopt CI; stage 2: adopt CD; stage 3: adopt microservices") would prescribe the same order to both organizations, wasting the first organization's early effort on practices that can't succeed without the architectural work happening first.

### Leadership's specific role: transformational, not transactional
The book's data (Chapter 9) also measured leadership behavior directly, using a validated instrument distinguishing **transformational leadership** (vision, inspirational communication, intellectual stimulation, supportive leadership, personal recognition) from purely **transactional leadership** (management by exception, reward contingent on specific measurable output). Transformational leadership behaviors were found to be an *amplifier* — they don't directly move the four key metrics themselves, but they strengthen the effect of the technical and process capability investments, essentially setting the conditions (psychological safety, shared vision, genuine support) under which teams actually adopt and sustain the capability investments rather than complying superficially and reverting once attention moves elsewhere.

**Worked example — amplification, not substitution:** Two organizations invest in identical technical capabilities (CI/CD tooling, architecture refactoring). Organization A's leadership communicates a clear vision for why (tied to customer and business outcomes, not just "corporate mandate"), personally removes organizational obstacles teams report, and treats early setbacks as learning opportunities (generative culture, `accelerate/09`). Organization B's leadership mandates the same tooling adoption via a top-down deadline with no explanation beyond compliance, and treats early setbacks as evidence the team isn't trying hard enough. The book's model predicts Organization A converts the technical investment into real, durable capability improvement more reliably than Organization B — same technical investment, different leadership amplification, different actual outcome.

### The role of a dedicated transformation/DevOps team
The book also addresses a common organizational choice: should transformation be led by a separate, dedicated "DevOps team" or platform team, or be the responsibility of every existing team? The data-informed recommendation is nuanced — a dedicated team *can* help (building shared tooling, spreading expertise, running experiments) but only if it operates as an internal platform/enabling function that other teams can pull from voluntarily, not as a new centralized gatekeeper that other teams must go through — the latter risks recreating exactly the coordination bottleneck architecture-for-flow (`accelerate/06`) is meant to eliminate, just relocated to a new team.

## Pros
- Context-sensitive: directs investment at each organization's actual bottleneck rather than a generic universal sequence, avoiding wasted effort on capabilities that aren't currently constraining.
- Continuous framing (no "done" state) matches the reality that elite performers keep investing rather than plateauing, setting the right expectation with leadership from the start.
- The transformational-leadership finding gives leaders a concrete, evidence-backed behavioral target (vision, support, recognition, intellectual stimulation) rather than just "sponsor the initiative."

## Cons
- Lack of a fixed universal roadmap is less legible to executives who want a simple "we are at stage X" status to report upward — the capability model requires more nuanced, ongoing communication instead of a single number.
- Self-assessing which capability is your actual bottleneck requires real organizational honesty and diagnostic skill; a team in denial about its actual weak point (e.g., blaming tooling when the real issue is culture, `accelerate/09`) can mis-prioritize investment even within this more flexible model.
- Without a defined end state, transformation efforts risk losing momentum or executive attention over time ("when will we be done?" has no clean answer), requiring sustained leadership commitment (`accelerate/12` covers this risk in more depth) rather than a one-time push.

## Alternatives
- **CMMI (Capability Maturity Model Integration) and similar staged maturity models** — the traditional alternative; provides external legibility and audit-ability, valuable in contexts (e.g., certain government contracting) that specifically require a certified maturity level, but the book's data argues against it as the right internal improvement model due to its universal-sequence assumption.
- **Big-bang transformation programs (time-boxed, externally consultant-led)** — a common alternative structure (e.g., an 18-month "digital transformation initiative" with a defined end date); risks the same problems the capability model is designed to avoid — treating transformation as a project with an end state rather than a continuous capability, and applying a somewhat generic playbook regardless of the organization's specific bottleneck.
- **Grassroots/bottom-up-only change (no leadership involvement)** — relies on individual teams or engineers adopting good practices without executive sponsorship; the book's transformational-leadership finding argues this under-performs a model where leadership actively amplifies and sustains the effort, particularly for capabilities (like architecture, `accelerate/06`) that require cross-team coordination no single team can unilaterally fix.

## When to use it
Use the capability model to structure any organizational improvement effort spanning the technical, process, and cultural practices in this subject — start by diagnosing your organization's actual current bottleneck (via the four key metrics, deployment pain, and Westrum culture assessment) rather than adopting a generic industry "transformation roadmap."

## When NOT to use it
Don't use the capability model's flexibility as an excuse to avoid making any prioritization decision at all ("we're investing a little in everything") — the model still requires identifying your actual bottleneck and concentrating investment there; diffuse, unfocused effort across all 24 capabilities simultaneously dilutes impact compared to a genuinely bottleneck-focused approach. If your organization has a hard external requirement for a specific certified maturity level (some regulatory or contracting contexts), you may need to satisfy that framework's requirements in parallel with, not instead of, the capability-model-driven internal improvement work.

## Key takeaways / mental model
There is no universal transformation staircase — there is a bottleneck, specific to your organization, among roughly two dozen independent capabilities, and the job of transformation leadership is to correctly diagnose that bottleneck, invest in it, remeasure, and repeat, indefinitely. Leadership's own behavior (transformational, not just transactional) is not a side detail — it's an amplifier that determines whether technical and process investment actually converts into durable capability, or reverts once the initial push loses momentum.

## Self-check questions
1. Explain, using the tightly-coupled-architecture worked example, why a universal "adopt CI, then CD, then microservices" sequence can fail for one organization while succeeding for another with different starting conditions.
2. Distinguish transformational from transactional leadership as the chapter defines them. Why does the research position transformational leadership as an *amplifier* of technical investment rather than a direct driver of the four key metrics itself?
3. A CTO wants a fixed 12-month roadmap with defined maturity stages to report to the board. What tension does this create with the capability model, and how would you propose reporting progress differently while still giving the board something legible?
4. Explain the risk of a dedicated "DevOps team" becoming a new bottleneck, using the architecture-for-flow concept from `accelerate/06`. What structural choice avoids this risk?

## References
- Accelerate: The Science of Lean Software and DevOps (Forsgren, Humble, Kim), Chapter 9: "Leaders and Managers", Chapter 10: "Conclusion".
