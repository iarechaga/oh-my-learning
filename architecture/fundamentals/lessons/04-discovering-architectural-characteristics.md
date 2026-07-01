---
id: fundamentals/04
subject: fundamentals
title: Discovering Architectural Characteristics
slug: discovering-architectural-characteristics
status: drafted
mastery:
seniority: senior
source: Fundamentals of Software Architecture (Richards & Ford, O'Reilly 2nd ed. 2025), Chapter 5
prerequisites: [fundamentals/03]
created: 2026-06-30
updated: 2026-06-30
---

# Discovering Architectural Characteristics

## TL;DR
Architects do not invent quality attributes; they discover them. By translating business goals, domain constraints, stakeholder concerns, and implicit requirements, architects uncover the core qualities that must drive system design. This translation prevents teams from building technically beautiful systems that fail to meet business needs.

## The idea
Business stakeholders do not speak the language of quality attributes. They don't ask for "99.9% availability" or "elastic deployment models." Instead, they explain their problems and goals in business terms: "We lose thousands of dollars every time the system crashes during our morning peak," or "We need to launch new features faster than our competitors."

If architects design systems based purely on what stakeholders say directly, they will miss the most critical design drivers. The discovery process is the translation mechanism that bridges the gap between business concerns and architectural characteristics.

## How it works
An architect discovers characteristics through a structured translation pipeline:

```
Business Statement                  Technical Translation
==================                  =====================
"We are losing customers   =======> Priority: Performance
due to slow checkout"               Metrics: Sub-second response time

"Our team must expand      =======> Priority: Maintainability, Testability
by fifty developers"                Metrics: Component separation, low coupling
```

This translation requires examining four primary sources of requirements.

### 1. Translating Business Goals
Every corporate initiative has a direct technical counterpart. You must learn to ask: "What does this goal imply for the system's structure?"
- **Corporate Goal: Merge with a competitor.** Implications: Interoperability and portability become critical. The systems must be able to exchange data easily.
- **Corporate Goal: Reduce operating costs.** Implications: Feasibility, efficiency, and resource utilization dominate. The system might need to use serverless models to scale down to zero when idle.

### 2. Analyzing Domain Constraints
The industry you operate in dictates several characteristics by default. You cannot ignore these, even if stakeholders do not mention them:
- **Healthcare Applications**: Privacy, security, and compliance (such as HIPAA) are non-negotiable.
- **Financial Applications**: Transactional safety, auditability, and data consistency are the absolute priorities.

### 3. Mapping Stakeholders
Different people in the organization care about different aspects of the system. You must interview diverse groups to get a complete picture:
- **The CEO/CFO**: Cares about cost, time to market, and competitive advantage.
- **The Security Officer**: Cares about encryption, compliance, and threat mitigation.
- **The Support Team**: Cares about observability, debuggability, and maintainability.

### 4. Uncovering Implicit Requirements
These are the qualities that are never explicitly written down because stakeholders assume they are standard. Users assume that their passwords are encrypted. They expect the page to load quickly on their phones. They assume their personal data is kept private.

You must bring these implicit expectations to light and define concrete metrics for them.

### Worked Example: The European Expansion at Sysops Squad
Suppose the leadership team at Sysops Squad announces a new goal: "We are expanding our ticket system to Europe next quarter. We also want to allow local European partners to integrate their custom reporting tools directly with our data."

An architect translates this announcement into specific quality attributes:
- **"Expanding to Europe"**: This triggers a major **Compliance** requirement. The system must adhere to GDPR rules, meaning personal data must be stored within EU boundaries (data residency) and users must have the right to be forgotten. It also introduces a **Performance** concern due to network latency across continents.
- **"Allow local partners to integrate custom tools"**: This triggers an **Interoperability** and **Security** requirement. The architect cannot allow external partners to run raw SQL queries on the production database, as this creates tight coupling and security risks. Instead, they must design a secure, versioned API layer.

By translating the business announcement, the architect uncovers GDPR compliance, global performance, interoperability, and security as the core drivers for the next phase of development.

## Pros
- Directs architectural efforts toward solving actual business problems.
- Eliminates guesswork by grounding technical designs in documented business needs.
- Helps justify the cost of technical refactoring or architectural changes to business leaders.

## Cons
- Requires significant time spent in meetings, workshops, and interviews instead of writing code.
- Conflicting stakeholder demands can be difficult to resolve and require strong negotiation skills.
- If the business strategy is vague or constantly shifting, the discovered characteristics can quickly become obsolete.

## Alternatives
- **The "standard architecture" approach**: Applying the exact same quality attributes to every project in the company. It's fast to start but leads to massive over-engineering for simple tools and under-engineering for critical systems.
- **Developer-led discovery**: Letting developers choose priorities based on what they find interesting (e.g., trying out a new event-driven framework). This satisfies developers but frequently fails to meet compliance or budget constraints.

## When to use it
- At the start of a new product or major system redesign.
- During strategic pivots, corporate acquisitions, or entries into new markets.
- When an existing system suffers from frequent production incidents or slow delivery times.

## When NOT to use it
- Very small, well-defined projects with stable and simple requirements.
- Tactical bug-fix phases or minor feature updates where the architectural direction is already set.

## Key takeaways / mental model
Stakeholders speak in business outcomes; architects translate those outcomes into quality attributes. Never accept "we want everything" as a requirements list. Dig deeper to find the real business drivers and domain constraints that dictate the 3 to 5 characteristics that truly matter.

## Self-check questions
1. Why is a business goal like "expand to global markets" a major architectural driver?
2. What is an example of an implicit requirement that stakeholders are unlikely to mention but is critical?
3. How should an architect handle two stakeholders with directly conflicting goals (e.g., speed to market vs maximum security)?

## References
- Fundamentals of Software Architecture (Richards & Ford, O'Reilly 2nd ed. 2025), Chapter 5
