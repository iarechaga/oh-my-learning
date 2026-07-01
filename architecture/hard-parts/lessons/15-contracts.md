---
id: hard-parts/15
subject: hard-parts
title: "Contracts: Strict vs Loose"
slug: contracts
status: drafted
mastery:
seniority: senior
source: Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 13
prerequisites: [hard-parts/03]
created: 2026-06-30
updated: 2026-06-30
---

# Contracts: Strict vs Loose

## TL;DR
A contract is how two software parts agree to communicate: signatures, schemas, field names, formats, and behavior. The main architectural choice is coupling level. Strict contracts maximize certainty and tooling; loose contracts maximize evolvability and autonomy. A practical default is loose at service boundaries and strict where correctness or performance dominates.

## The idea
Every interface encodes assumptions. Assumptions create coupling. Coupling sets change cost.

So contracts are architecture decisions, not just syntax files.

Sysops Squad framing:
- Ticket Producer emits ticket lifecycle events.
- Survey consumes close events.
- Dispatch and Billing consume the same stream for different needs.

If one producer field change breaks many consumers, the boundary is too strict.

Think in a spectrum:
1. Strict: exact shared schema, strong validation, tight coordination.
2. Loose: minimal required agreement, tolerant readers, independent evolution.

Neither side is universally correct. Match strictness to domain risk, regulation, latency needs, and change frequency.

## How it works

### Strict contracts
Strict contracts define exact, shared, versioned schemas with required fields.

Examples:
- gRPC/protobuf with required semantics.
- SOAP/WSDL.
- Shared serialized objects.
- Strongly typed RPC stubs.

How strict works:
1. One canonical schema exists.
2. Producer and consumer compile or validate against it.
3. Missing required fields fail early.
4. Drift is often caught before deploy.

Why teams choose strict:
- High certainty.
- Excellent tooling and code generation.
- Strong compile-time feedback.
- Often efficient binary serialization.

Costs:
- Changes ripple across consumers.
- Versioning burden grows quickly.
- Cross-team coordination can slow delivery.

Strict fits boundaries where failure cost is high and change cadence is controlled.

### Loose contracts
Loose contracts define a stable required subset and tolerate additive changes.

Examples:
- JSON name-value payloads with tolerant readers.
- REST with required-subset parsing.
- Hypermedia APIs.
- GraphQL field selection.

How loose works:
1. Producer can add optional fields without forcing consumers to change.
2. Consumer ignores fields it does not use.
3. Consumer validates only required business data.
4. Producer and consumer evolve mostly independently.

Benefits:
- High decoupling.
- Fast independent releases.
- Lower coordination overhead.

Costs:
- Less compile-time certainty.
- More runtime and CI responsibility.
- Need contract tests for confidence.

Loose contracts are usually better at dynamic service boundaries.

### Stamp coupling
Stamp coupling means passing a large structure when a consumer needs only a small part.

Smell example:
- Survey only needs `ticketId`, `customerId`, `closedAt`.
- Producer sends full `TicketAggregate` with many unrelated fields.

Why this hurts:
1. Unused fields create accidental coupling.
2. Irrelevant field changes can still break consumers.
3. Payload and parsing overhead increase.

Nuance: stamp coupling can be useful in choreographed sagas.

If workflow state must travel with events, a larger payload can be deliberate context propagation, enabling local decisions without a central orchestrator. So stamp coupling is usually a boundary smell, but sometimes a choreography tool. See lesson 13.

### Consumer-driven contracts (CDC)
CDC lets consumers publish the fields and behavior they require. Providers verify those contracts in CI.

Flow:
1. Consumer writes contract tests.
2. Consumer publishes contract artifacts.
3. Provider build pulls contracts.
4. Provider runs verification tests.
5. Build fails on breaking changes.

CDC keeps loose contracts safer by catching breakage early.

CDC plus fitness functions is a strong pair:
- CDC checks real consumer expectations.
- Fitness functions enforce long-term compatibility policy.

### Contract coupling spectrum (ASCII)
```text
Strict certainty                                                Loose evolvability
|-------------------------------------------------------------------------|
protobuf/gRPC required fields
        SOAP/WSDL
               typed REST DTO with strict validation
                          JSON tolerant reader with required subset
                                      GraphQL client-selected fields
                                                REST hypermedia controls
```

### Worked example 1: Sysops Squad strict vs loose ticket contracts
Goal: show what breaks (and what does not) for add, remove, and rename changes.

#### 1) Strict protobuf contract
Initial contract v1:
```proto
message TicketClosed {
  string ticket_id = 1;
  string customer_id = 2;
  int64 closed_at_epoch_ms = 3;
}
```

Survey consumer steps:
1. Parse with generated stubs.
2. Read `ticket_id`, `customer_id`, `closed_at_epoch_ms`.
3. Trigger survey creation.

Change A: producer adds field.
```proto
message TicketClosed {
  string ticket_id = 1;
  string customer_id = 2;
  int64 closed_at_epoch_ms = 3;
  string resolution_code = 4;
}
```

Result:
1. Older consumer ignores field 4.
2. Existing behavior keeps working.
3. Additive change is normally safe.

Change B: producer renames/removes required semantic field.
```proto
message TicketClosed {
  string ticket_id = 1;
  string client_id = 2; // renamed from customer_id
  int64 closed_at_epoch_ms = 3;
}
```

Result:
1. Consumer still expects `customer_id` semantic.
2. Mapping or validation fails.
3. Teams must coordinate migration or versioning.

Strict takeaway: additive fields are often safe; required semantic rename or removal is breaking.

#### 2) Loose JSON tolerant-reader contract
Initial payload v1:
```json
{
  "eventType": "TicketClosed",
  "ticketId": "T-90210",
  "customerId": "C-771",
  "closedAt": "2026-06-30T10:15:00Z"
}
```

Survey consumer rules:
1. Require `ticketId`, `customerId`, `closedAt`.
2. Ignore unknown keys.
3. Reject only if required subset is missing or invalid.

Change A: producer adds fields.
```json
{
  "eventType": "TicketClosed",
  "ticketId": "T-90210",
  "customerId": "C-771",
  "closedAt": "2026-06-30T10:15:00Z",
  "resolutionCode": "HW_REPLACED",
  "region": "ES-NORTH"
}
```

Result:
1. Consumer reads required subset.
2. Extra keys are ignored.
3. No break.

Change B: producer renames `customerId` to `clientId` without alias.
```json
{
  "eventType": "TicketClosed",
  "ticketId": "T-90210",
  "clientId": "C-771",
  "closedAt": "2026-06-30T10:15:00Z"
}
```

Result:
1. Required `customerId` is missing.
2. Consumer rejects event at runtime.
3. CDC should catch this before release.

Loose takeaway: additive change is cheap; semantic rename or removal is still breaking, but detected by tests/runtime instead of compilation.

### Worked example 2: CDC test published by Survey consumer
Goal: show a concrete safety net for loose contracts.

Survey publishes expectations:
1. Producer emits `TicketClosed` events.
2. Payload includes `ticketId`, `customerId`, `closedAt`.
3. Types are string, string, ISO-8601 datetime string.
4. Extra keys are allowed.

Pseudo CDC artifact:
```text
Contract: SurveyConsumer expects TicketClosed
Given provider has a closed ticket T-90210 for customer C-771
When provider emits TicketClosed
Then payload contains ticketId, customerId, closedAt
And closedAt matches ISO-8601 format
And unknown keys do not fail consumer parsing
```

Provider CI steps:
1. Pull consumer contracts.
2. Start provider in test mode.
3. Run verification.
4. Fail build on missing key, wrong type, or behavior drift.

Rename replay (`customerId` -> `clientId`):
1. Provider compiles locally.
2. CDC verification runs.
3. Test fails on missing `customerId`.
4. Pipeline blocks release.

## Pros
- Makes coupling explicit and discussable.
- Strict contracts provide certainty, validation, and tooling.
- Loose contracts improve autonomy and independent evolution.
- Tolerant readers make additive changes low risk.
- CDC plus fitness functions recover early feedback.

## Cons
- Strict contracts can force synchronized releases.
- Shared schemas add governance and coordination overhead.
- Loose contracts shift many failures to CI/runtime.
- CDC adds toolchain and test maintenance cost.
- Stamp coupling can quietly inflate accidental dependencies.

## Alternatives
- **Shared database integration** - avoids API drift but creates strong data ownership coupling.
- **Canonical schema everywhere** - increases consistency but slows adaptation.
- **Anti-corruption layers** - isolate internal models at mapping cost.
- **Central orchestration contracts** - clearer flow but tighter orchestrator dependency.

## When to use it
Prefer loose contracts at service boundaries with frequent change and independent deployments.

Use strict contracts where correctness, compliance, or latency is more important than flexibility:
1. Internal high-throughput RPC paths.
2. Financial or regulated interfaces.
3. Safety-critical integrations.

Use CDC whenever loose contracts carry critical business behavior.

Use stamp coupling intentionally: avoid it as default interface style, but allow it for choreographed saga state when context truly must travel with the event.

## When NOT to use it
Do not default to strict contracts on every boundary in fast-moving organizations; coordination cost can dominate.

Do not adopt loose contracts without guardrails for important consumers; without CDC and policy checks, breakage appears late.

Do not pass full domain objects when consumers need only a few fields, unless workflow context is deliberately propagated in choreography.

Do not assume GraphQL or hypermedia eliminates coupling; they change its form.

## Key takeaways / mental model
Think of contracts as a coupling dial.

1. Turn toward strict for certainty and performance.
2. Turn toward loose for evolvability and autonomy.
3. Add matching guardrails: versioning discipline on strict side, tolerant readers plus CDC plus fitness functions on loose side.

Keep stamp-coupling nuance in mind:
- Usually an interface smell.
- Sometimes a valid choreography state carrier.

Practical default for many distributed systems:
1. Loose at service boundaries.
2. Strict in tightly controlled or regulated zones.
3. CDC as the safety bridge.

## Self-check questions
1. What is a software contract, and how does it create coupling?
2. Why should strict vs loose be treated as a spectrum?
3. In the Sysops Squad examples, which changes are additive-safe under strict protobuf and loose JSON?
4. Why does renaming `customerId` to `clientId` break both models?
5. What is stamp coupling, and why is it usually a boundary smell?
6. When is stamp coupling deliberately useful in choreography?
7. How does CDC detect provider breakage before production?
8. How do fitness functions complement CDC?
9. Give one boundary where strict contracts are better and explain why.
10. Give one boundary where loose contracts are better and list guardrails.

## References
- Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 13
- [03-dynamic-coupling.md](03-dynamic-coupling.md)
- [13-distributed-workflows-orchestration-choreography.md](13-distributed-workflows-orchestration-choreography.md)
- [12-api-design-communication.md](../../system-design/lessons/12-api-design-communication.md)
