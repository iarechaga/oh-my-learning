---
id: system-design-interview/10
subject: system-design-interview
title: "Design a Notification System"
slug: notification-system
status: drafted
mastery: 
seniority: mid
source: "System Design Interview – An Insider's Guide, Vol. 1 (Alex Xu), Chapter 10"
prerequisites: [system-design-interview/01, system-design-interview/02, system-design-interview/03]
created: 2026-08-10
updated: 2026-08-10
---

# Design a Notification System

## TL;DR
A notification system sends messages to users across multiple channels — push
notifications (iOS/Android), SMS, and email — triggered either by another internal
service ("order shipped") or a scheduled job ("weekly digest"). The interview deep dive
is about decoupling triggering from delivery with a message queue, handling each
channel's very different third-party integration and failure modes, and preventing
duplicate or overwhelming notifications to the same user.

## The idea
Notifications look simple ("send a message to a user") but are a genuine distributed
systems problem once you account for scale, multiple heterogeneous channels each with
its own third-party provider and failure characteristics, retry/idempotency
requirements (a user should not get the same notification 5 times because a retry
fired), and the need to not block the triggering service's own request path while a
slow third-party API is called.

## How it works

### Step 1: Clarify requirements
- **Channels.** Push notification, SMS, email. (Assume: all three, each user can be
  reached on channels they've opted into.)
- **Triggers.** Both event-driven (a service publishes "order shipped") and scheduled
  (a nightly digest job). (Assume: both.)
- **Guarantees.** Should delivery be guaranteed exactly-once, at-least-once, or
  best-effort? (Assume: at-least-once with dedup on the client/consumer side —
  exactly-once across third-party providers you don't control is not realistically
  achievable, and is a good point to say explicitly in the interview.)
- **Scale.** Assume 10 million notifications/day across all channels combined, with
  bursty spikes (e.g., a breaking-news push to all users at once).

### Step 2: Back-of-the-envelope
`10,000,000 / 100,000 seconds/day ≈ 100 notifications/sec average`. But notification
systems are unusually bursty — a single triggering event (e.g., "notify all 5 million
subscribed users about a live event") can require sending 5 million notifications in a
short window, dwarfing the daily average by orders of magnitude. This burst
characteristic — not the daily average — is what actually sizes the system, and is
worth calling out explicitly: average QPS massively understates the real peak
requirement for a fan-out-style trigger, unlike more evenly-distributed traffic.

### Step 3: High-level design
```
[Triggering Service] --> [Notification API] --> [Message Queue] --> [Workers per channel]
      (or Cron job)                                                        |
                                                                    +-------+-------+
                                                                    v       v       v
                                                                [Push]   [SMS]  [Email]
                                                                  |        |       |
                                                             [APNs/FCM] [Twilio] [SendGrid]
```

The **triggering service never calls a third-party provider directly.** It publishes an
event ("notify user 123: order shipped") to the notification API, which validates it,
enriches it (look up the user's preferred channels, contact info, template), and places
it on a message queue. This decoupling means:
- The triggering service's request returns immediately — it doesn't wait on a
  potentially slow third-party API call (Apple's push service, an SMS gateway), which
  keeps the triggering service's own latency and reliability independent of
  notification delivery.
- If a channel's third-party provider is degraded or down, notifications for that
  channel simply queue up rather than causing failures or retries to cascade back into
  the triggering service.
- Each channel gets its own worker pool, so a slow SMS provider doesn't block push
  notification delivery — matching the "decouple with a queue" pattern from
  `system-design-interview/03`.

### Step 4: Deep dive — per-channel differences
Each channel has meaningfully different constraints, and a good design surfaces them
rather than treating "send notification" as one uniform operation:

| Channel | Provider example | Key constraint |
| --- | --- | --- |
| Push | APNs (iOS), FCM (Android) | Needs a device token per device; tokens expire/rotate and must be refreshed; provider has its own rate limits and payload size limits. |
| SMS | Twilio, similar gateways | Costs real money per message — volume matters for budgeting; strict regional/carrier regulations (e.g., opt-out compliance). |
| Email | SendGrid, SES | Highest payload flexibility (HTML, attachments); deliverability depends on sender reputation — bulk sending needs careful rate control to avoid being flagged as spam. |

*Worked example — device token churn:* a push notification worker attempts to deliver
to a device token that's since expired (the user reinstalled the app, getting a new
token). APNs/FCM returns an error indicating the token is invalid. The worker must
recognize this specific error and mark the stored token as invalid (or remove it) so
future notifications don't keep retrying against a dead token — without this cleanup
step, the system silently wastes calls and, at scale, accumulates a growing set of
permanently-failing deliveries.

### Step 5: Deep dive — idempotency and de-duplication
At-least-once delivery (Step 1's chosen guarantee) means a retry (e.g., a worker
crashes after sending but before acknowledging the queue message, so the message is
redelivered) can cause the same notification to be sent twice. Fix with an idempotency
key: generate a unique ID per logical notification (e.g., `hash(user_id, event_type,
event_id)`), and before sending, check (and atomically set) that ID in a
short-lived deduplication store (e.g., Redis with a TTL matching the retry window).

*Worked example:* a worker picks up "notify user 123: order 456 shipped" (idempotency
key `abc123`), successfully sends the push notification, but crashes before
acknowledging the queue message. The message queue redelivers it to another worker.
That worker checks the dedup store, finds `abc123` already marked as sent within the
TTL window, and skips sending — the user gets exactly one notification despite the
retry.

### Step 6: Deep dive — respecting user preferences and rate limits
- **Opt-in/opt-out and channel preferences** must be checked before sending — a user
  who disabled SMS notifications must never receive one, both as a product requirement
  and, for SMS specifically, a legal one in many jurisdictions (e.g., TCPA in the US).
- **Per-user notification rate limiting.** A user shouldn't receive 50 notifications in
  a minute because of a bug or a burst of unrelated triggering events; apply a rate
  limit per user per channel (conceptually the same mechanism as
  `system-design-interview/04`, keyed by user ID + channel instead of API endpoint),
  and consider batching/digesting ("3 new comments" instead of 3 separate
  notifications) when volume is high for a single user in a short window.
- **Retry with backoff, not immediate hammering.** A failed send (transient provider
  error) should retry with exponential backoff, not immediately — repeatedly hammering
  a struggling third-party provider makes things worse for everyone using it.

### Step 7: Deep dive — templates and third-party abstraction
A notification template system (subject/body templates per notification type, with
variable substitution) separates *what* to say from *how* to send it, letting product
teams add new notification types without touching delivery code. A thin abstraction
layer per channel (a common interface like `send(user, message)` with a channel-specific
implementation underneath) makes it possible to swap or add providers (e.g., moving
from Twilio to a different SMS gateway) without changing the triggering or queueing
logic.

### Step 8: Wrap-up — monitoring and reliability
Track delivery success/failure rates per channel and per provider — a spike in push
notification failures is an early signal of an APNs/FCM outage or a bulk expired-token
problem. A dead-letter queue for messages that fail repeatedly (after retry limits are
exhausted) prevents them from blocking the main queue indefinitely while still
preserving them for investigation, rather than silently dropping them.

## Pros
- Decoupling triggering from delivery via a queue keeps the triggering service fast and
  insulated from third-party provider slowness/outages.
- Per-channel worker pools and abstraction let each channel scale and evolve
  independently.
- Idempotency keys give correctness (no user-visible duplicates) despite at-least-once
  delivery semantics, which is the realistic guarantee achievable with third-party
  providers you don't control.

## Cons
- At-least-once (not exactly-once) delivery means the dedup layer is load-bearing — if
  it's buggy or its TTL window is too short relative to real-world retry delays,
  duplicates can slip through.
- Each channel's third-party integration is a genuine ongoing maintenance burden
  (token rotation, provider API changes, deliverability tuning).
- Burst traffic (a mass notification event) requires the queue and worker pool to
  absorb spikes far above the daily average — under-provisioning for bursts is a common
  and costly mistake.

## Alternatives
- **Synchronous, direct sending from the triggering service** — simpler for a very
  low-volume system, but couples the triggering service's reliability/latency to every
  third-party provider's, and doesn't scale to bursty fan-out.
- **A single generic "send" queue for all channels** instead of per-channel queues —
  simpler to operate initially, but a slow/degraded channel then head-of-line-blocks
  unrelated channels' messages; per-channel queues avoid this at the cost of more
  infrastructure to manage.
- **Third-party notification platforms** (e.g., a unified provider that handles
  push/SMS/email under one API) — reduces the amount of custom integration code, at the
  cost of another vendor dependency and less control over routing/retry logic.

## When to use it
Any product needing to reach users outside the app itself: transactional notifications
(order updates, security alerts), marketing/engagement notifications, and scheduled
digests. Essentially any system with more than a trivial, single-channel, low-volume
notification need.

## When NOT to use it
A product sending a handful of transactional emails (e.g., password resets) doesn't
need a queue-and-worker-pool architecture — calling the email provider's API directly
from the triggering request is simpler and appropriate at that scale. Build the fuller
architecture only once volume, channel count, or burstiness genuinely demand it.

## Key takeaways / mental model
Picture the triggering event and the actual delivery as two separate concerns joined
only by a queue: the trigger just needs to say "this happened," and the notification
system is entirely responsible for turning that into a delivered message across
whichever channels the user prefers, with retries, dedup, and rate limiting handled on
its own side. The queue is what lets these two concerns fail, scale, and retry
independently — without it, every triggering service inherits the reliability
characteristics of every third-party notification provider it touches.

## Self-check questions
1. Why does decoupling the triggering service from actual delivery via a message queue
   matter more for notifications than it might for, say, a simple CRUD write?
2. Walk through a concrete scenario where at-least-once delivery would produce a
   duplicate notification, and explain how the idempotency-key mechanism prevents the
   user from seeing it.
3. Why do push, SMS, and email each warrant their own worker pool rather than one
   shared "send notification" worker pool?
4. A breaking-news event needs to notify 5 million users within a few minutes. Why does
   this scenario invalidate using the *daily average* QPS as your capacity planning
   number?
5. What's the difference between rate-limiting a user's *incoming* notifications
   (Step 6) and rate-limiting *outgoing* requests to a third-party provider like
   Twilio, and why might a system need both?

## References
- *System Design Interview – An Insider's Guide, Vol. 1* (Alex Xu), Chapter 10
