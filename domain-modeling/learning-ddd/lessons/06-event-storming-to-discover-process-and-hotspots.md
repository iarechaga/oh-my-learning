---
id: learning-ddd/06
subject: learning-ddd
title: Event storming to discover process and hotspots
slug: event-storming-to-discover-process-and-hotspots
status: drafted
mastery:
seniority: mid
source: Learning Domain-Driven Design (Vlad Khononov), Part I, Chapter 4 (continued) - "Event Storming"
prerequisites: [learning-ddd/05]
created: 2026-08-10
updated: 2026-08-10
---

# Event storming to discover process and hotspots

## TL;DR
Event storming is a workshop technique where domain experts and engineers collaboratively map a business process as a timeline of orange sticky notes, each one a **domain event** ("Order Placed," "Payment Declined," "Shipment Dispatched") written in past tense. Building the timeline together - and layering in commands, actors, systems, and explicitly flagged "hotspots" (disagreements or unknowns) - surfaces the real process, the real vocabulary (`learning-ddd/05`), and the real bounded-context boundaries (`learning-ddd/03`) far faster and more accurately than interviews or up-front documentation.

## The idea
Traditional requirements gathering (interviews, written specs, BPMN diagrams drawn by a single analyst) has a structural weakness: one person interprets what several domain experts say and produces one artifact, and every domain expert who wasn't in the room, or whose nuance got lost in translation, only finds out something was wrong once the software is built. Event storming inverts this: put every relevant domain expert, plus engineers, in the same room (or virtual board), and build the model together, in real time, using a notation simple enough that non-technical participants can actively contribute rather than passively review.

The core unit is the **domain event** - something that happened in the business, always named as a past-tense fact ("Invoice Generated," not "Generate Invoice"; "Appointment Cancelled," not "Cancel Appointment"). Events are placed on a long timeline (physically, a wall covered in orange sticky notes) in the order they occur. This single constraint - everything is a fact that already happened, in chronological order - forces precision: vague statements like "we handle the appointment somehow" get pressured into specific, sequenced facts ("Appointment Requested" -> "Provider Assigned" -> "Appointment Confirmed" -> possibly "Appointment Cancelled" or "Appointment Completed").

## How it works

### The core notation (color-coded sticky notes)
- **Orange - Domain Events**: past-tense facts, the backbone of the timeline. E.g., "Order Placed," "Refund Approved."
- **Blue - Commands**: the intent or action that triggers an event, usually issued by an actor. E.g., the command "Place Order" leads to the event "Order Placed."
- **Yellow (small) - Actors**: who or what issues a command - a customer, a support agent, an external system, a scheduled job.
- **Pink - External Systems**: third-party or upstream systems the process depends on (a payment gateway, a carrier API).
- **Purple - Policies**: automated reactions - "whenever X event happens, automatically trigger Y command" (e.g., "whenever Payment Declined, automatically send Payment Retry Reminder"). Policies are where a lot of hidden business logic and automation lives, and they're easy to miss without this explicit notation.
- **Green - Read Models / Views**: information a user or system needs to see in order to issue a command correctly (e.g., a support agent needs to see "Order Status" before deciding to issue "Approve Refund").
- **Red - Hotspots**: explicitly flagged disagreements, unknowns, or "we're not sure" moments. This is one of event storming's most valuable outputs - a visible, undeniable record of exactly where the team's shared understanding breaks down, rather than that disagreement staying hidden until it becomes a production bug.

### Step by step, worked example - e-commerce order fulfillment
1. **Chaotic exploration**: participants write down every domain event they can think of related to "what happens when a customer orders something," without worrying about order or completeness yet: "Order Placed," "Payment Charged," "Inventory Reserved," "Shipment Dispatched," "Delivery Confirmed," "Refund Requested," "Item Backordered."
2. **Enforce timeline order**: the group arranges these chronologically, discovering gaps and branches as they do: does "Inventory Reserved" happen before or after "Payment Charged"? A warehouse-ops domain expert clarifies: "we reserve inventory *before* charging, otherwise we'd charge customers for things we don't have" - a business rule the engineers hadn't known, now made explicit and placed correctly on the timeline.
3. **Add commands and actors**: "Order Placed" is triggered by the command "Place Order," issued by the actor "Customer" (via the checkout UI). "Payment Charged" is triggered by the command "Charge Payment," issued not by the customer directly but by an internal Policy: "whenever Order Placed AND Inventory Reserved, automatically Charge Payment."
4. **Surface a hotspot**: while discussing "Item Backordered," a customer-support domain expert says "when that happens we email the customer," while a warehouse-ops domain expert says "no, we auto-cancel that line item after 48 hours if it's still backordered." Neither knew the other's process existed. This gets flagged red - a genuine, previously invisible process gap - and resolved in the workshop rather than being discovered later as conflicting production behavior.
5. **Draw bounded-context boundaries on top of the timeline**: once the full process is visible, the group looks for natural seams - clusters of events, commands, and vocabulary that hang together and speak a consistent language, versus places where the vocabulary or ownership visibly shifts. In this example: everything from "Place Order" through "Inventory Reserved" clusters around order/checkout vocabulary (a Checkout/Ordering context); "Payment Charged" and related events cluster around a Payments context; "Shipment Dispatched" through "Delivery Confirmed" cluster around a Fulfillment context. This is exactly how event storming feeds `learning-ddd/03`'s bounded-context design - the boundaries emerge from where the *language and process* naturally cluster, not from a pre-existing org chart or database schema.

### Worked example - healthcare scheduling hotspot
During an event-storming session for appointment scheduling, the timeline includes "Appointment Requested" -> "Provider Assigned" -> "Appointment Confirmed." A front-desk domain expert flags a hotspot: "what happens if two staff members assign different providers to the same slot at the same time?" No one in the room has a confident answer - this is a genuine, previously-unaddressed race condition in the real-world process, not just a code bug. Surfacing it here, as a red sticky note, means the team can design for it (e.g., an explicit "Provider Assignment Conflict Detected" event and a policy for resolving it) before writing any code, rather than discovering the race condition in production when two patients show up for the same slot.

### Worked example - SaaS billing, discovering a policy
A billing event-storming session reveals a purple Policy note nobody had written down anywhere: "whenever a Subscription's Trial Period Ends AND no Payment Method has been added, automatically issue Downgrade to Free Tier." This policy existed in institutional knowledge (a support lead remembered it from a decision made eighteen months prior) but had never been written down, and a recent engineer had implemented trial expiration slightly differently (silently locking the account instead of downgrading it) without knowing the intended behavior. The workshop catches and corrects this drift.

## Pros
- Surfaces hidden business logic, undocumented policies, and cross-team disagreements far faster than sequential interviews or a single analyst's written spec - the "red hotspot" mechanism makes disagreement visible and resolvable in the room, rather than staying hidden until it becomes a bug.
- Produces a shared, chronologically accurate model of the actual process, owned collectively by the room rather than filtered through one person's interpretation.
- Feeds directly and concretely into `learning-ddd/05` (the vocabulary used on the sticky notes becomes the ubiquitous language) and `learning-ddd/03` (event/vocabulary clusters reveal bounded-context boundaries).
- Non-technical participants can meaningfully contribute (the notation is simple enough not to require software background), producing buy-in and shared ownership of the resulting model that a written spec rarely achieves.

## Cons
- Requires getting the right domain experts and engineers physically or virtually in the same room for a sustained session (often half a day to several days for a large process) - real scheduling cost.
- Facilitation skill matters a great deal; a poorly facilitated session can devolve into unstructured discussion without producing a usable timeline, or let a dominant participant's view suppress quieter but important disagreements.
- The output (a wall of sticky notes, or a digital board) needs deliberate follow-up work to translate into lasting artifacts (a written ubiquitous language glossary, a context map) - without that follow-up, the insights fade once the workshop ends.
- Not a substitute for the deeper tactical modeling that comes after (`learning-ddd/07`, `learning-ddd/08`) - it discovers the process and vocabulary, but doesn't by itself decide aggregate boundaries or persistence strategy.

## Alternatives
- **Sequential one-on-one interviews with domain experts** - lower scheduling burden (no need to get everyone in a room at once), but loses the cross-checking effect where one expert's statement visibly contradicts another's in real time; disagreements surface much later, if at all.
- **Business Process Model and Notation (BPMN)** - a more formal, complete process-modeling notation, often produced by a business analyst after the fact; more rigorous for compliance/audit purposes but far less effective as a *discovery* tool since it's typically authored by one person rather than built collaboratively.
- **User story mapping** - focuses on user-facing feature flow and priority rather than domain events and cross-team process; complements event storming (which is deeper on backend/process logic) rather than replacing it.
- **Domain Storytelling** - a related, narrative-driven collaborative modeling technique (pictographic rather than sticky-note-based) covered in some DDD literature as an alternative discovery workshop format with a similar collaborative-discovery goal.

## When to use it
Use event storming at the start of modeling a new bounded context or a complex process, especially in or around core subdomains (`learning-ddd/02`) where getting the process and vocabulary right has the highest payoff, and whenever multiple teams or departments have overlapping but not-yet-reconciled understanding of a process.

## When NOT to use it
Skip it for genuinely simple, well-understood, low-stakes processes (a generic subdomain like "send a password reset email") where the process is already completely clear and workshop overhead wouldn't surface anything new. Also avoid running it without securing real domain-expert time and facilitation - a workshop with only engineers guessing at business rules reproduces exactly the "translated by one person" weakness this technique exists to avoid.

## Key takeaways / mental model
Build the process as a strict, past-tense, chronological sequence of facts, out loud, with the actual domain experts in the room - and treat every "wait, that's not how I thought it worked" moment as gold, not friction: flag it red, resolve it there, and let the resulting event/command/policy vocabulary become the seed of both the ubiquitous language (`learning-ddd/05`) and the bounded-context map (`learning-ddd/03`).

## Self-check questions
1. Why must event-storming notes be phrased strictly in past tense ("Order Placed") rather than present tense or as commands ("Place Order")? What discipline does that enforce?
2. Describe how a red "hotspot" sticky note in an event-storming session is a *better* outcome than a session where no disagreements surface. What would the absence of any hotspots actually suggest?
3. Walk through how the events and vocabulary clusters from an event-storming session for a process you know would suggest bounded-context boundaries (`learning-ddd/03`).
4. What is a "Policy" sticky note (purple) modeling, and why is it often where undocumented business rules hide?

## References
- Learning Domain-Driven Design (Vlad Khononov), Part I, Chapter 4: "Communicating with Domain Experts" / Event Storming.
- Introducing EventStorming (Alberto Brandolini) - the technique's originating source.
