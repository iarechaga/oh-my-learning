---
id: devops-handbook/06
subject: devops-handbook
title: Continuous Delivery and Deployment Pipeline Design
slug: continuous-delivery-pipelines
status: drafted
mastery:
seniority: senior
source: The DevOps Handbook (Kim, Humble, Debois, Willis), Part III
prerequisites: [devops-handbook/05]
created: 2026-08-10
updated: 2026-08-10
---

# Continuous Delivery and Deployment Pipeline Design

## TL;DR
Continuous delivery extends CI's automated pipeline all the way to "always deployable" — every trunk commit that passes the pipeline produces a release-candidate artifact that could be deployed to production at any time; continuous deployment goes one step further and actually deploys every passing change automatically, without a human "go" decision.

## The idea
CI (`devops-handbook/05`) answers "is this change safe to merge." Continuous delivery (CD) answers the next, harder question: "is this change safe to run in production, right now, with real users." The gap between those two questions is usually where organizations lose the most time — a change can pass every unit and integration test and still take weeks to actually reach production because of manual staging deploys, manual sign-offs, and scheduled release windows. CD's answer is to automate that entire remaining path into a single, repeatable pipeline, so "ready to ship" and "shipped" become nearly the same moment, and the decision to actually release becomes a business choice (continuous delivery) or is removed entirely (continuous deployment) rather than a logistical ordeal.

## How it works

### Pipeline stages: a concrete example
A mature deployment pipeline typically looks like a series of automated gates, each stricter and slower than the last, each one a chance to catch a different class of problem before it reaches real users:

```
Commit --> [CI: build, unit tests, lint]           (~5 min)
       --> [Integration tests, security scan]       (~10 min)
       --> [Deploy to staging, run smoke tests]      (~5 min)
       --> [Automated acceptance / E2E tests]        (~15 min)
       --> [Canary deploy: 5% of production traffic] (~30 min observation)
       --> [Full production rollout]
```

Each stage either passes automatically (advancing the change) or fails automatically (halting it and alerting the owning engineer) — no stage requires a human to manually click "looks good" under normal operation. The canary stage is the key risk-reduction mechanism: rather than deploying to 100% of traffic at once, the change goes to a small slice first, its error rate and latency are compared against the rest of the fleet automatically, and only if it looks healthy does the rollout proceed — this is what makes deploying dozens of times a day *safer*, not riskier, than deploying monthly, because each individual deploy's blast radius is small and automatically monitored.

### Continuous delivery vs. continuous deployment — the actual difference
This distinction is frequently blurred in casual usage but matters:
- **Continuous delivery**: every change that passes the pipeline is *deployable* — a human (or a scheduled process) makes the explicit business decision of when to actually release it, but that decision is now "press the button" rather than "coordinate a multi-week release process." The pipeline has done all the *technical* validation; only a *business* decision remains.
- **Continuous deployment**: there is no separate human decision — every change that passes the pipeline deploys to production automatically, immediately. This requires higher confidence in the pipeline's ability to catch problems, because there's no human checkpoint left to catch what automation missed.

Most organizations that describe themselves as "doing continuous deployment" are actually doing continuous delivery with a very fast, largely-rubber-stamp human approval — which is a legitimate and common maturity level, not a failure to reach the "real" goal.

### Decoupling deployment from release: feature flags
A key technique that makes frequent deployment compatible with controlled feature rollout is separating "the code is running in production" from "the feature is visible to users." A new checkout flow can be deployed to 100% of production servers behind a feature flag that's initially off, then enabled for 1% of users, then 10%, then 100% — entirely independent of the deployment pipeline's cadence. This lets teams deploy continuously (fast feedback per `devops-handbook/01`) while still controlling the pace of user-facing change deliberately (a business/product decision, not an engineering one).

### Rollback and forward-fix as pipeline citizens
A well-designed pipeline treats "roll back" as a first-class, automated, tested path — not a manual emergency procedure improvised under pressure. Concretely: the pipeline can redeploy the last known-good artifact within the same automated flow used for forward deploys, and this path is exercised regularly enough (via game days or routine practice) that it's trusted, not merely theoretical.

**Worked example.** A canary deploy shows a 3x increase in p99 latency on the 5% traffic slice within 4 minutes of rollout. An automated rollback trigger (not a human paged at 2am) reverts that slice to the previous artifact immediately, and the responsible engineer is notified with the specific metrics that triggered the rollback and a link to the diff — turning what would have been a customer-visible incident into an automatically contained, 4-minute blip.

## Pros
- Shrinks the gap between "code is ready" and "code is running for users" from weeks to minutes, directly improving deployment lead time (a core DORA metric, `devops-handbook/16`).
- Canary and progressive rollout mechanisms make frequent deployment *safer* than infrequent deployment, contrary to the common intuition that faster shipping means riskier shipping.
- Automated rollback removes a major source of incident-response panic by making "revert" a routine, tested, fast pipeline action rather than an improvised emergency procedure.

## Cons
- Requires significant upfront and ongoing investment: fast, reliable automated tests (`devops-handbook/05`), production-representative staging environments, canary infrastructure, and automated health-check comparison logic.
- Continuous deployment specifically requires very high confidence in automated testing and monitoring, because there's no human checkpoint left — organizations that adopt it before their pipeline is trustworthy will ship more bugs faster, not fewer.
- Some contexts (certain regulated industries, safety-critical or hardware-coupled systems) have real, non-negotiable manual review requirements that limit how far toward full automation the pipeline can go.

## Alternatives
- **Scheduled release trains with manual QA gates** — the direct alternative this practice replaces; lower upfront tooling investment, but reintroduces the large-batch and slow-feedback problems from `devops-handbook/02` and `devops-handbook/03`.
- **Blue-green deployment** — an alternative (or complementary) progressive-rollout mechanism to canarying: maintain two full production environments and switch traffic between them atomically; simpler mental model than a gradual canary ramp, but doesn't give the same fine-grained "how much traffic is affected" control during the transition.
- **Manual staged rollout by a release manager** — a human decides and executes each rollout percentage step; more human judgment in the loop, useful when automated health signals aren't yet trustworthy, but slower and doesn't scale with deployment frequency.

## When to use it
Invest in a full CD pipeline once CI (`devops-handbook/05`) is solid and trusted, and once deployment frequency or lead time is a genuine business constraint — the investment pays back fastest for teams shipping frequently to a large user base where blast-radius control matters.

## When NOT to use it
Don't build automated canary/progressive-rollout infrastructure before the underlying test suite (`devops-handbook/05`) is fast and trustworthy — automating a shaky quality gate just automates shipping bad changes faster. Don't push toward full continuous deployment (removing the human decision entirely) in contexts with genuine regulatory sign-off requirements or where automated health signals aren't yet reliable enough to be trusted without a human check.

## Key takeaways / mental model
Think of the pipeline as a series of increasingly strict, increasingly expensive gates, each one automatically catching a different class of problem, with blast radius shrinking at each stage (unit test failure affects no one; a bad canary affects 5% of traffic for minutes). The goal isn't "no human ever decides anything" — it's "the pipeline handles everything a human doesn't need to add unique judgment to," freeing humans for the decisions that actually require them. Continuous delivery also turns "when do we release" from an engineering-logistics question into a pure business-timing question — often the biggest organizational unlock, independent of whether you ever flip on full continuous deployment.

## Self-check questions
1. Explain the precise difference between continuous delivery and continuous deployment. Why might a mature organization deliberately choose to stay at continuous delivery rather than push to full continuous deployment?
2. Using the canary-deploy worked example, explain why deploying to 5% of traffic first and monitoring automatically is safer than deploying to 100% with a slower, more thorough pre-deploy manual review.
3. How do feature flags decouple "deployment cadence" from "release cadence," and why does that decoupling matter for balancing engineering speed against product/business control?
4. A team wants to adopt continuous deployment but their automated test suite has a known 10% flaky-failure rate. What should they fix first, and why would skipping that step make continuous deployment dangerous rather than merely inconvenient?

## References
- The DevOps Handbook (Kim, Humble, Debois, Willis), Part III: "The First Way: Technical Practices of Flow."
- See also: `devops-handbook/05` (continuous integration, the pipeline's first stage) and `devops-handbook/16` (deployment frequency and lead time as measured outcomes of this practice).
