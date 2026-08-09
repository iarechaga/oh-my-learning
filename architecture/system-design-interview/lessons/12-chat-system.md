---
id: system-design-interview/12
subject: system-design-interview
title: "Design a Chat System"
slug: chat-system
status: drafted
mastery: 
seniority: senior
source: "System Design Interview – An Insider's Guide, Vol. 1 (Alex Xu), Chapter 12"
prerequisites: [system-design-interview/01, system-design-interview/02, system-design-interview/03, system-design-interview/07]
created: 2026-08-10
updated: 2026-08-10
---

# Design a Chat System

## TL;DR
A chat system (like WhatsApp or Slack) must maintain a persistent connection to every
online client (since chat is push, not poll), track online presence, guarantee message
delivery and ordering even across a user's multiple devices, and store message history
durably. The interview deep dive centers on three tightly linked hard parts: how
clients maintain a real-time connection (WebSockets, not HTTP polling), how the
service guarantees message delivery and ordering, and how message storage is modeled
for fast retrieval of a conversation's history.

## The idea
Unlike a typical request/response web system, chat is fundamentally push-based: when
User A sends a message to User B, the system must proactively deliver it to User B's
device(s), not wait for User B to ask "any new messages?" This single fact — the server
must be able to initiate communication to the client — drives most of the design's
distinguishing decisions, from connection protocol to how you track who's online and
where to route a given message.

## How it works

### Step 1: Clarify requirements
- **Scope.** 1-on-1 messaging (Assume: primary focus; group chat as an extension —
  scoping this explicitly avoids trying to design both with equal depth in limited
  time).
- **Message types.** Text, with the design extensible to media later. (Assume: text
  only for the core design.)
- **Delivery guarantee.** At-least-once with client-side dedup, not exactly-once (same
  realistic framing as `system-design-interview/10`).
- **Presence.** Online/offline/last-seen status. (Assume: yes, a common expectation.)
- **Scale.** Assume 50 million DAU, each sending ~40 messages/day.

### Step 2: Back-of-the-envelope
`50,000,000 × 40 / 100,000 seconds/day = 20,000 messages/sec average`, ~40,000/sec at
peak. Each message ~100 bytes of text plus ~50 bytes metadata (sender, recipient,
timestamp, message ID) ≈ 150 bytes. Daily storage: `50M × 40 × 150 bytes = 300 GB/day`
— over a year, ~110 TB, meaningful but not exotic; needs a horizontally scalable store
but not an unusual one. Concurrent connections: if 50M DAU means roughly 10-15 million
concurrently online at peak (a reasonable assumption for a global product with
staggered time zones), the system needs to hold that many persistent connections open
simultaneously — this is the number that shapes the connection-layer design, not the
message-rate number.

### Step 3: High-level design
```
[Client A] <--WebSocket--> [Chat Server 1] --+
                                              |
[Client B] <--WebSocket--> [Chat Server 2] --+--> [Message Queue / direct routing]
                                              |
                                    [Message Store]  [Presence Store]
                                              |
                                    [Push notification, if recipient offline]
```

- Clients hold a **persistent WebSocket connection** to a chat server (not HTTP
  polling — see Step 4 for why).
- A **connection/session registry** (often in a fast shared store like Redis) maps
  `user_id → which chat server instance holds their live connection`, since with many
  chat server instances behind a load balancer, the server handling a given send isn't
  necessarily the one holding the recipient's connection.
- **Message Store**: durable storage for message history.
- If the recipient is offline, fall back to a push notification
  (`system-design-interview/10`) instead of (or alongside) queuing for delivery on
  reconnect.

### Step 4: Deep dive — connection protocol (why WebSockets)
Plain HTTP is request/response: the client must initiate every exchange. Two ways to
approximate push-like behavior over it: **polling** (client repeatedly asks "anything
new?" every few seconds — wastes requests and adds latency up to the polling interval)
and **long polling** (client asks, server holds the request open until there's
something to send or a timeout, then the client immediately re-asks — better than
polling but still has per-request overhead and doesn't gracefully support the server
pushing multiple things quickly).

**WebSockets** upgrade an HTTP connection into a persistent, full-duplex TCP connection:
either side can send data at any time without a new request. This is the standard
choice for real-time chat because it minimizes latency (no polling interval) and
overhead (no repeated HTTP headers per message) once established, at the cost of the
chat servers needing to hold open, stateful connections for every online user rather
than being purely stateless request handlers.

**Why this changes the load-balancing story:** recall from `system-design-interview/03`
that a load balancer normally works well with stateless app servers, where any instance
can handle any request. With WebSockets, a specific client is *stuck* to whichever chat
server instance accepted its connection for the lifetime of that connection — this is
why the connection/session registry (mapping user → server) is a load-bearing
component: when User A sends a message to User B, A's chat server must look up which
*other* server instance holds B's live connection and route the message there (often
via an internal pub/sub or the message queue), rather than assuming both users share a
server.

*Worked example:* User A is connected to Chat Server 1; User B is connected to Chat
Server 2. A sends a message to B. Server 1 receives it, looks up B's connection
location in the registry (`user_B → server_2`), and forwards the message internally to
Server 2 (e.g., via a lightweight internal pub/sub channel), which then pushes it down
B's live WebSocket connection. If the registry instead said B was offline, Server 1
would persist the message and trigger a push notification instead.

### Step 5: Deep dive — message ordering and delivery guarantees
Two related but distinct hard problems:

**Ordering.** Messages within a single conversation must appear in a consistent order
to both participants, even if they're sent close together and processed by different
server instances. A common technique: assign each message a unique, roughly
time-ordered ID at creation (a Snowflake-style ID, `system-design-interview/07`, or a
per-conversation monotonic sequence number) and always render messages sorted by that
ID rather than by arrival order at the client, which can vary due to network jitter.

*Worked example:* User A sends "Hi" then immediately "How are you?" in quick
succession. Due to network conditions, User B's client receives "How are you?" first.
Because each message carries a monotonically increasing sequence ID (assigned at the
server when the message is accepted, not at the client), B's client sorts by that ID
before rendering — "Hi" (lower ID) still displays first, correcting the out-of-order
network delivery.

**Delivery guarantee (at-least-once + dedup).** A message might be delivered twice if,
e.g., a client reconnects and the server isn't sure whether the last message was
acknowledged, so it resends to be safe. Each message carries a client-generated unique
ID (so retries of "the same send" are recognizable); the receiving client (or server)
deduplicates on that ID before displaying/storing it again — the same idempotency
pattern used in `system-design-interview/10`'s notification system.

**Message states (sent/delivered/read).** A common product requirement (the familiar
single/double/blue checkmark pattern) needs explicit acknowledgment messages flowing
back from recipient to sender: the recipient's client sends a "delivered" ack once the
message reaches it, and a "read" ack once the user views it, each updating the
message's state in the store and notifying the sender's client if it's currently
connected.

### Step 6: Deep dive — storing message history
Messages are typically stored keyed by conversation (so "fetch the last 50 messages in
this conversation" is a fast, single-partition range query), not keyed globally by
sender or recipient alone.

*Worked example schema:* a table/partition keyed by `conversation_id`, with rows
ordered by `message_id` (the time-sortable ID from Step 5) — this makes "give me the
most recent N messages in conversation C" an efficient range scan on one partition,
rather than an expensive scatter-gather across the whole dataset. This access pattern
(fetch by conversation, ordered by time) is exactly the kind of case-by-key,
range-within-key workload that a wide-column/NoSQL store (or a well-indexed relational
table partitioned by conversation) handles well, in contrast to the pure key-value
`get`/`put` access pattern of `system-design-interview/06`.

**Group chat as an extension:** a group conversation is modeled the same way (messages
keyed by `conversation_id`, now with N participants instead of 2), but delivery fans
out to N connected clients instead of 1 — conceptually closer to the fan-out problem in
`system-design-interview/11`, though at a vastly smaller scale per event (a group has
dozens to low-hundreds of members, not millions of followers), so the celebrity-account
hybrid trick generally isn't needed here.

### Step 7: Deep dive — presence (online/offline/last-seen)
Presence is inherently approximate and eventually consistent — there's no way to know
with certainty that someone is "truly" online at this exact instant, only that their
client recently sent a heartbeat. A common approach: each connected client sends a
periodic heartbeat; the server (or a presence service backed by a fast store with TTL
expiry) marks a user offline if no heartbeat is received within a timeout window (e.g.,
30 seconds). On disconnect (graceful or timeout), presence changes are published to
that user's contacts who are themselves online (again, a small-scale fan-out, similar
in shape to message delivery).

### Step 8: Wrap-up — scaling and failure handling
- **Chat server scaling**: add more instances behind the load balancer; the
  connection/session registry is what makes this horizontally scalable despite
  connection stickiness.
- **Chat server failure**: when a chat server instance dies, every client connected to
  it loses its connection and must reconnect (typically with client-side automatic
  reconnect + exponential backoff), landing on a different instance; the registry entry
  for those users must be cleared/updated so senders don't route to a dead server.
- **Message queue as a buffer**: using a message queue for inter-server message routing
  (rather than direct server-to-server calls) adds resilience if a target server is
  briefly unreachable — the message waits in the queue rather than being dropped.

## Pros
- WebSockets give low-latency, low-overhead real-time delivery, which is the core
  product requirement chat can't compromise on.
- Time-sortable message IDs solve both ordering and (paired with the
  conversation-keyed storage model) fast history retrieval in one mechanism.
- The registry + internal routing pattern lets chat servers scale horizontally despite
  connections being inherently stateful/sticky.

## Cons
- Persistent connections are more operationally expensive per-user than stateless HTTP
  request handling — each chat server instance has a hard ceiling on concurrent
  connections it can hold, which must be capacity-planned explicitly (unlike stateless
  servers, where connection count isn't the binding resource).
- Presence is fundamentally approximate — there's an inherent lag between a user
  actually going offline and the system reflecting that.
- Client reconnect storms (e.g., after a chat server or network blip affecting many
  users at once) need careful backoff/jitter to avoid overwhelming the system exactly
  when it's recovering.

## Alternatives
- **Long polling instead of WebSockets** — simpler to support behind some restrictive
  corporate proxies/firewalls that block WebSocket upgrades, but higher latency and
  more per-message overhead; sometimes kept as a fallback for clients where WebSockets
  fail to connect.
- **Server-Sent Events (SSE)** — a simpler, HTTP-based push mechanism, but one-way
  (server-to-client only), so it doesn't cover the client-to-server send path;
  workable if send and receive use genuinely different transports, but adds complexity
  relative to WebSockets' single bidirectional channel.
- **A third-party chat/messaging platform** (e.g., a managed pub/sub or chat API
  provider) — for many products, building this from scratch isn't justified; use a
  managed service unless real-time messaging is a core product differentiator.

## When to use it
Any product with real-time, bidirectional user-to-user communication: messaging apps,
customer support chat, in-app collaboration features, multiplayer game state sync (with
different framing but similar connection-layer needs).

## When NOT to use it
Don't reach for a persistent-connection architecture for features that are really
just "occasional updates," where the delay of polling or push notifications is
acceptable (e.g., a "your report is ready" notification doesn't need a chat-grade
WebSocket infrastructure — the notification system in `system-design-interview/10` is
a better fit). The operational cost of holding millions of persistent connections open
is only worth paying when true low-latency bidirectional communication is a hard
product requirement.

## Key takeaways / mental model
The whole design flows from one fact: chat requires the server to push, so the
transport must support that (WebSockets), and once connections are stateful and
sticky, every other component (routing, presence, scaling) exists to answer "given
that a specific server holds a specific user's live connection, how do we still treat
the fleet as one logical system?" The registry mapping user → server is the answer to
that question, and it shows up, in different clothes, as the load-bearing component in
every deep-dive sub-area: message routing, presence propagation, and reconnect
handling all depend on it being accurate.

## Self-check questions
1. Why does a WebSocket-based chat server break the usual assumption (from
   `system-design-interview/03`) that any load-balanced instance can handle any
   request, and what component fixes this?
2. Walk through why a message can arrive at the recipient's client out of order over
   the network, and explain how time-sortable message IDs let the client correct for
   it without needing perfectly ordered delivery.
3. Why is "at-least-once plus client-side dedup" a more realistic target than
   exactly-once delivery for this system, and what specific mechanism achieves the
   dedup?
4. Why is storing messages keyed by `conversation_id` (rather than by sender or a
   global message table) the right choice for the dominant access pattern of a chat
   app?
5. A user's chat server instance crashes. Walk through what happens to (a) their own
   client, and (b) messages that other users try to send them, in the seconds after
   the crash and before they reconnect.

## References
- *System Design Interview – An Insider's Guide, Vol. 1* (Alex Xu), Chapter 12
