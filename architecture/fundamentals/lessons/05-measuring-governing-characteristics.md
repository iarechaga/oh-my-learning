---
id: fundamentals/05
subject: fundamentals
title: Measuring and Governing Characteristics
slug: measuring-governing-characteristics
status: drafted
mastery:
source: Fundamentals of Software Architecture (Richards & Ford, O'Reilly 2nd ed. 2025), Chapter 6
prerequisites: [fundamentals/03, fundamentals/04]
created: 2026-06-30
updated: 2026-06-30
---

# Measuring and Governing Characteristics

## TL;DR
An architectural characteristic is useless if you cannot measure and govern it. Architects use automated metrics and fitness functions in the build pipeline to protect system qualities from decaying over time as the codebase evolves. This approach moves governance from passive documentation to active, automated enforcement.

## The idea
Software architectures naturally decay. As teams add features under tight deadlines, they introduce shortcuts that degrade performance, break module boundaries, and compromise security. This organic decay is known as architectural drift or software entropy.

To prevent this drift, we must move away from subjective opinions. Saying "the code feels clean" or "we should try to keep latency low" is not enough. We must define objective, repeatable measurements and build automated guardrails that prevent structural regression.

## How it works
Architects govern characteristics by combining metric collection with automated fitness functions.

### 1. Defining Clear Metrics
You must identify concrete metrics for each prioritized quality:
- **Operational Metrics**: Latency (such as p95 or p99 response times), error rates, CPU and memory saturation, and availability percentages.
- **Structural Metrics**: Cyclomatic complexity (measures code path branching), component coupling (inbound and outbound dependencies), test coverage, and code churn.

### 2. Architecture Fitness Functions
An architecture fitness function is an automated mechanism that provides an objective integrity assessment of some architectural characteristic. It is the ultimate tool for continuous governance.

```
Developer Commit -> [ Run Unit Tests ] -> [ Run Fitness Functions ] -> [ Deploy ]
                                                       |
                             * ArchUnit / Dependency-Cruiser checks
                             * Security vulnerability scan
                             * Latency / Performance budget check
```

Fitness functions are integrated directly into the CI/CD pipeline and can take several forms:
- **Automated**: Runs on every pull request to check coupling, dependencies, and lint rules.
- **Temporal**: Runs on a schedule, such as an automated script that checks if security certificates are within thirty days of expiration.
- **Continuous**: Monitors production behavior, alert-logging if latency budgets are exceeded.

### Worked Example: Governing Modularity and Performance at Sysops Squad
Suppose the architect at Sysops Squad needs to govern modularity and performance across multiple teams.

#### Scenario A: Preventing Circular Dependencies
- **The Problem**: Developers are writing SQL queries directly inside controller files, bypass-linking the repository layer and creating circular imports.
- **The Fitness Function**: The architect configures a dependency linter (like dependency-cruiser) in the build pipeline. They write a rule asserting that files in the `/controllers/` directory must never import from the `/db/` database package directly.
- **The Result**: If a developer tries to commit code that violates this boundary, the build immediately fails, and the pull request cannot be merged.

#### Scenario B: Protecting Performance Budgets
- **The Problem**: New API releases are getting slower due to bulky payloads and unoptimized database joins.
- **The Fitness Function**: The architect sets up an automated performance gate. In the staging environment, the pipeline runs a lightweight benchmark simulation that fires fifty requests per second. The fitness function asserts that the p95 latency must stay under 200 milliseconds.
- **The Result**: If a change pushes the latency to 210 milliseconds, the test fails, and the deploy is halted automatically.

## Pros
- Direct, rapid feedback to developers when they violate structural rules.
- Objective, transparent standards that eliminate arguments during code reviews.
- High scalability, allowing a small architecture team to protect system qualities across dozens of microservices.

## Cons
- Writing and maintaining fitness functions requires engineering time and effort.
- Overly restrictive rules can slow down delivery times and frustrate product teams.
- Abstract characteristics (like usability or team feasibility) are incredibly hard to measure automatically.

## Alternatives
- **Manual Architecture Reviews**: Relying on an architecture review board to manually inspect code and diagrams. This is slow, creates an organizational bottleneck, and rarely catches deep structural issues.
- **Trust-based development (no governance)**: Relying entirely on developer discipline and memory to follow style guides. This works well for small, cohesive teams but fails inevitably as the organization grows.

## When to use it
- In distributed architectures where independent teams can easily introduce drift.
- For critical characteristics that have high operational or financial penalties if violated.
- When migrating a monolith to microservices to ensure newly drawn boundaries are respected.

## When NOT to use it
- Small, single-user utility scripts or short-lived prototypes where long-term maintainability does not matter.
- Simple CRUD tools with low traffic and no complex security or operational needs.

## Key takeaways / mental model
Code rot is inevitable unless you actively prevent it. Move from subjective rules in wiki pages to objective, automated fitness functions in your build pipeline. Protect your architecture's integrity automatically on every single commit.

## Self-check questions
1. What is an architecture fitness function, and how does it differ from a standard unit test?
2. How can an architect govern structural coupling without manually inspecting imports?
3. Why do manual architecture reviews fail to prevent long-term architectural drift?

## References
- Fundamentals of Software Architecture (Richards & Ford, O'Reilly 2nd ed. 2025), Chapter 6
