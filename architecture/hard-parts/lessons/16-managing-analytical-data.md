---
id: hard-parts/16
subject: hard-parts
title: Managing Analytical Data
slug: managing-analytical-data
status: drafted
mastery:
source: Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 14
prerequisites: [hard-parts/08, ddia/05, ddia/16]
created: 2026-06-30
updated: 2026-06-30
---

# Managing Analytical Data

## TL;DR
Operational data (OLTP) runs day-to-day business transactions, while analytical data (OLAP) helps humans and models make decisions. Architecture for analytical data evolved from centralized data warehouses to raw-data lakes, and then toward data mesh, which decentralizes ownership to domains. The key trade-off is not technology first, but ownership and operating model first.

## The idea
Most teams first learn data architecture through operational systems: create a ticket, assign it, close it, bill it. That is OLTP data, and in this repository you already covered it in lesson 08.

Analytical data has a different mission. It answers questions like:
1. Which incident categories are growing faster than staffing?
2. Which customers churn after low survey scores?
3. Which team-level patterns predict SLA breaches?

Those are not single-row transactional questions. They are broad, historical, cross-domain questions.

This difference matters because OLTP and OLAP optimize for opposite constraints:
1. OLTP optimizes for correctness and low-latency writes under concurrency.
2. OLAP optimizes for large scans, aggregations, and trend analysis.
3. OLTP models the present state needed to run workflows.
4. OLAP models historical and derived state needed to guide decisions.

If you force one architecture to satisfy both perfectly, you usually get a bad compromise for both. That is why analytical-data architecture became its own discipline.

The chapter-level arc in Hard Parts is a progression:
1. Data Warehouse: centralize structured analytics with schema-on-write.
2. Data Lake: centralize raw data with schema-on-read.
3. Data Mesh: decentralize analytical ownership to domains while sharing a platform and governance model.

The deeper lesson is that each stage solves one bottleneck and reveals the next. Warehouse solves fragmented BI, lake solves schema rigidity and cost, mesh solves organizational scaling and ownership mismatch.

## How it works
Start from first principles: analytical systems need three capabilities at once.
1. Ingest data from many operational sources.
2. Shape it into forms useful for analysis, reporting, and ML.
3. Make it discoverable and trustworthy for downstream consumers.

The three architecture styles differ mainly in where transformation happens, who owns semantics, and who carries operational burden.

### 1) Data Warehouse

#### How it works
A data warehouse is a central analytical store where data is transformed before it is loaded for most queries. This is commonly called schema-on-write.

Typical flow:
1. Extract data from operational systems (ticketing, surveys, billing, CRM).
2. Transform and clean it through ETL pipelines.
3. Load modeled tables into one central warehouse.
4. Expose SQL and BI tools to analysts and reporting teams.

Modeling pattern:
1. Build dimensional models, often a star schema.
2. Keep fact tables for measurable events (tickets opened, invoices paid).
3. Keep dimension tables for context (customer, team, priority, time).
4. Join facts to dimensions for fast aggregates and dashboards.

Connection to DDIA lesson 05:
Warehouse engines often use column-oriented storage for analytical scans. That design is a strong fit for OLAP queries reading a few columns across many rows, but not ideal for high-write OLTP workloads.

Worked mini example (star schema):
1. Fact table `fact_ticket_resolution` stores `ticket_id`, `opened_time_id`, `closed_time_id`, `customer_id`, `team_id`, `resolution_minutes`.
2. Dimension `dim_customer` stores customer tier and region.
3. Dimension `dim_time` stores date hierarchies.
4. BI query computes median resolution time by tier and month in seconds, because the data is already cleaned and conformed.

#### Pros
1. Fast, predictable SQL for structured analytical questions.
2. One central source for BI definitions and executive reporting.
3. Strong data quality gates before data reaches business users.
4. Mature ecosystem for dashboards, cubes, lineage, and access control.

#### Cons
1. Tight coupling to source schemas; upstream changes frequently break ETL.
2. ETL becomes heavy and brittle as source count and change velocity grow.
3. Central warehouse team turns into a delivery bottleneck.
4. Schema rigidity slows exploratory analysis and novel questions.
5. Poor fit for raw, unstructured, or ML feature engineering data.

### 2) Data Lake

#### How it works
A data lake stores raw data, usually on cheap object storage, and applies structure later when data is consumed. This is schema-on-read.

Typical flow:
1. Land raw extracts, logs, events, and files in object storage.
2. Preserve original fidelity with minimal upfront modeling.
3. Let downstream users apply transformations when needed.
4. Use engines for batch SQL, notebooks, and ML processing over lake data.

Practical effect:
1. Ingestion gets easier because you avoid modeling everything upfront.
2. Consumption gets harder because many teams must create their own transforms.
3. Data quality and meaning move from centralized ETL to distributed consumers.

Worked mini example (raw fidelity):
1. Survey platform changes question schema from `score_1_to_5` to `nps_0_to_10`.
2. Lake ingestion still stores both raw versions without breaking.
3. Data scientist builds a harmonization transform for churn model training.
4. Another analyst builds a separate transform for monthly support KPI reporting.

#### Pros
1. Flexible ingestion for structured, semi-structured, and unstructured data.
2. Lower storage cost for large historical datasets.
3. Preserves raw data for future use cases not yet known.
4. Strong fit for data science and ML experimentation.

#### Cons
1. High risk of a data swamp without governance, quality, and metadata discipline.
2. Hard discoverability: users struggle to find trustworthy datasets.
3. Semantic consistency degrades when each team transforms independently.
4. Still centralized in ownership, often with lingering source coupling.
5. Heavy downstream transformation burden shifts complexity to consumers.

### 3) Data Mesh

#### How it works
Data mesh reframes analytical architecture around organizational scaling. Instead of one central team owning all analytical pipelines, each business domain owns and serves its analytical data as products.

The four explicit principles are:
1. Domain ownership of analytical data.
2. Data as a product.
3. Self-serve data platform.
4. Federated computational governance.

What each principle means in practice:
1. Domain ownership: the team that understands ticketing semantics owns ticket analytics outputs.
2. Data as a product: datasets have product qualities (discoverable, documented, reliable, versioned, support expectations).
3. Self-serve platform: shared tooling handles storage, catalog, lineage, access control, and serving patterns so domains do not reinvent infrastructure.
4. Federated computational governance: global standards are enforced through automation and policy-as-code, while domains keep local autonomy.

#### Data Product Quantum (DPQ)
A Data Product Quantum (DPQ) is the analytical counterpart attached to an operational quantum and owned by the same domain team.

Think of it as a paired unit:
1. Operational quantum: runs business workflows (OLTP APIs, transactions, domain state).
2. DPQ: publishes analytical outputs from that domain with explicit contracts for consumers.

Why this pairing matters:
1. The same team that defines operational meaning defines analytical meaning.
2. Semantic drift between app logic and analytics contracts is reduced.
3. Ownership and accountability are clear when quality issues appear.

Connection to DDIA lesson 16:
DDIA discusses unbundling monolithic data concerns into dataflow-oriented systems. DPQ fits that trajectory: domains emit well-defined data products into a broader dataflow ecosystem rather than forcing all semantics through one central schema team.

Worked mini example (DPQ attachment):
1. Ticketing domain operational quantum owns `CreateTicket`, `AssignTicket`, `CloseTicket` workflows.
2. Its DPQ publishes `tickets_product_v1` with events and curated tables such as `ticket_lifecycle_daily` and `ticket_sla_breach_facts`.
3. Consumers (Finance, Support Ops, ML) subscribe through platform interfaces.
4. Ticketing team maintains product SLOs, schema contracts, and quality tests.

#### Pros
1. Scales with organization by distributing ownership across domains.
2. Aligns analytical semantics with domain expertise.
3. Removes central-team throughput bottlenecks.
4. Fits microservices and architectural-quantum thinking from earlier lessons.
5. Encourages durable data contracts and product-level accountability.

#### Cons
1. Organizational complexity rises; this is not only a tooling change.
2. Requires significant investment in a robust self-serve platform.
3. Needs governance maturity and interoperable standards to avoid fragmentation.
4. Upfront transition cost is high for centralized orgs.
5. Requires cultural shift: domains must own consumer-facing data quality.

### Trade-off table: Warehouse vs Lake vs Mesh

| Dimension | Data Warehouse | Data Lake | Data Mesh |
| --- | --- | --- | --- |
| Primary ownership | Central data/BI team | Central platform or data engineering team | Domain teams, with platform support |
| Source coupling | High through ETL mappings to source schemas | Medium to high, often deferred but still present | Lower at org level, contracts owned per domain |
| Flexibility | Lower, schema-on-write | Higher for ingestion, variable for consumption | High if standards and platform are strong |
| Governance posture | Strong central control | Often weak unless intentionally built | Federated computational governance |
| Organizational scalability | Bottlenecks as org grows | Better ingestion scale, still central semantics pressure | Designed for large multi-domain scale |
| Best-fit context | Stable structured BI, clear metrics | Raw data retention, experimentation, ML exploration | Many domains, high change rate, ownership-driven analytics |

### Worked example: Sysops Squad analytics evolution
Sysops Squad runs ticketing, post-incident surveys, and billing. Leadership wants weekly reliability and customer-health insights.

#### Phase A: Central data warehouse approach
How it works:
1. ETL pulls `tickets`, `survey_responses`, and `billing_invoices` into one warehouse nightly.
2. Central analytics team models star schemas and dashboard marts.
3. Executives query one BI layer for shared KPIs.

What goes well:
1. KPI definitions are centralized and consistent.
2. SQL dashboards are fast for structured management reporting.

What breaks as scale grows:
1. Ticketing schema changes twice a month, repeatedly breaking ETL jobs.
2. Analytics queue length grows because one central team owns all modeling requests.
3. Data science team struggles to use raw survey text and event payloads in the rigid warehouse model.

#### Phase B: Data mesh with domain data products
How it works:
1. Ticketing domain team owns operational services and a ticketing DPQ.
2. Ticketing DPQ publishes a `tickets` data product with clear contracts and quality checks.
3. Survey domain publishes its own survey product, including curated aggregates and optional raw access tiers.
4. Billing domain publishes billing-product datasets.
5. Consumers subscribe to products via self-serve platform APIs, catalog, and access policies.

Concrete consumer flow:
1. Support Operations subscribes to ticketing `ticket_age_distribution_daily` and survey `nps_by_queue_daily`.
2. Finance subscribes to billing `invoice_collection_latency` and ticketing `support_effort_cost_facts`.
3. ML team subscribes to versioned training views from ticketing and survey products.

Why this resolves prior bottlenecks:
1. Domain teams publish semantics they already understand deeply.
2. Central team no longer mediates every transformation request.
3. Platform team focuses on reusable infrastructure, not domain semantics.
4. Governance remains consistent through automated global standards.

Historical note:
One of the authors of Hard Parts is Zhamak Dehghani, originator of the data mesh concept, which explains why ownership and socio-technical design are emphasized strongly in this chapter.

## Pros
1. Gives a clear mental map for selecting analytical architecture by context.
2. Makes ownership trade-offs explicit instead of hiding them behind tooling.
3. Supports both BI and ML needs when patterns are chosen deliberately.
4. Encourages stronger alignment between domain meaning and analytical outputs.
5. Reduces surprise coupling by treating analytical contracts as first-class architecture.

## Cons
1. Easy to treat as a technology migration when it is largely an operating-model migration.
2. Transition periods can temporarily increase complexity and duplicated pipelines.
3. Governance mistakes can produce either chaos (too loose) or bottlenecks (too strict).
4. Teams may underestimate the product discipline required for shared analytical datasets.
5. Without platform investment, decentralization can devolve into incompatible silos.

## Alternatives
- **Keep a centralized warehouse with stronger domain partnership** - useful when organization size is moderate and metric definitions are stable.
- **Lakehouse-style central platform** - blends warehouse and lake capabilities in one central model; can reduce some friction but does not automatically solve ownership bottlenecks.
- **Hybrid model (mesh-incremental)** - start with central core datasets, then move high-change domains to domain-owned data products first.
- **Operational read models only** - for some teams, lightweight reporting projections from operational systems are enough and full analytical-platform investment is unnecessary.

## When to use it
Use this conceptual framework when your organization needs to decide not only how to store analytical data, but who should own and evolve it.

Use warehouse-first when:
1. Reporting is mostly structured and stable.
2. Centralized BI governance is acceptable.
3. Source schema volatility is manageable.

Use lake-first when:
1. You need low-cost raw retention across many formats.
2. Data science and exploratory workloads dominate.
3. You can invest in metadata, catalog, and quality controls early.

Use mesh-first (or mesh evolution path) when:
1. Domain count is high and central data team is a bottleneck.
2. Business semantics change rapidly per domain.
3. Platform and governance capabilities can be funded and staffed.

## When NOT to use it
Do not push into data mesh just because it is fashionable.

Avoid mesh if:
1. Domain boundaries are unclear or unstable.
2. Teams are not ready to own data products end to end.
3. Self-serve platform capability is weak or nonexistent.

Do not over-engineer lakes if:
1. You do not have a realistic plan for catalog, lineage, and quality signals.
2. Most users only need stable KPI dashboards.

Do not force a rigid warehouse-only model if:
1. Raw and unstructured data are central to product strategy.
2. Central ETL change queues are already blocking critical decisions.

## Key takeaways / mental model
Use a two-axis mental model.

Axis 1 is data-shaping strategy:
1. Schema-on-write (warehouse).
2. Schema-on-read (lake).
3. Contracted product outputs per domain (mesh DPQs).

Axis 2 is ownership strategy:
1. Central semantics and delivery.
2. Central storage but distributed consumption transforms.
3. Federated domain ownership with shared platform and automated governance.

If OLTP is about running the business now, OLAP is about steering the business next.
If lesson 08 taught you to decompose operational data by domain ownership, this lesson extends that logic to analytics through the Data Product Quantum attached to each operational quantum.

In short:
1. Warehouse optimizes for consistent structured BI.
2. Lake optimizes for flexible raw-data capture and exploration.
3. Mesh optimizes for organizational scale and domain-aligned analytical ownership.

## Self-check questions
1. What is the practical difference between operational (OLTP) and analytical (OLAP) data in terms of goals, workloads, and modeling?
2. Why does schema-on-write in a warehouse improve query speed but increase coupling to upstream schema changes?
3. How does column-oriented storage from DDIA lesson 05 relate to warehouse performance characteristics?
4. In a data lake, what conditions cause a useful lake to degrade into a data swamp?
5. State the four principles of data mesh exactly, and explain one implementation implication for each.
6. Define Data Product Quantum (DPQ) and explain how it attaches to an operational quantum.
7. Why is data mesh primarily a socio-technical and ownership shift, not just a storage-engine decision?
8. In the Sysops Squad example, what bottleneck appears in the warehouse phase and how does the ticketing data product reduce it?
9. Compare warehouse, lake, and mesh across governance and organizational scalability.
10. What signals would tell you to choose a hybrid migration path instead of a full immediate mesh transition?

## References
- Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 14
- [08-decomposing-operational-data.md](08-decomposing-operational-data.md)
- [05-oltp-olap-column-storage.md](../../ddia/lessons/05-oltp-olap-column-storage.md)
- [16-future-of-data-systems.md](../../ddia/lessons/16-future-of-data-systems.md)
