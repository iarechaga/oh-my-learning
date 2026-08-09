---
id: system-design-interview/01
subject: system-design-interview
title: "A Framework for System Design Interviews"
slug: interview-framework
status: drafted
mastery: 
seniority: mid
source: "System Design Interview – An Insider's Guide, Vol. 1 (Alex Xu), Chapter 1"
prerequisites: []
created: 2026-08-10
updated: 2026-08-10
---

# A Framework for System Design Interviews

## TL;DR
A system design interview is not a test of trivia recall; it is a 45-60 minute
simulation of how you collaborate on an ambiguous, open-ended problem. Run it as a
four-step loop — clarify requirements, estimate scale, sketch a high-level design, then
deep-dive into the hardest parts — and narrate your reasoning the whole way. The
framework matters more than any specific answer, because it is what turns "design
Twitter" from an unsolvable riddle into a tractable, incremental conversation.

## The idea
Unlike a coding interview, a system design interview has no single correct answer and
often no way to "finish." The problem statement is intentionally vague — "design a URL
shortener," "design Twitter" — because the real skill being tested is how you behave
under ambiguity: do you ask clarifying questions before diving in, do you make
trade-offs explicit, do you manage your time, can you go deep on a hard sub-problem
without losing the thread of the whole system?

Candidates fail these interviews for predictable, avoidable reasons that have nothing
to do with system design knowledge:
- They jump straight to a detailed design (e.g., drawing a database schema) before
  agreeing with the interviewer on what is even being built.
- They try to design for a billion users when the interviewer only asked for ten
  thousand, wasting the whole session on unneeded complexity.
- They go silent for five minutes while "thinking," giving the interviewer no signal.
- They pick one component (say, the database) and defend it as the only possible
  choice, rather than naming alternatives and trade-offs.
- They run out of time because they never noticed the clock and spent 30 minutes on
  requirements-gathering for a problem that needed 5.

A framework fixes all of this by turning the interview into a rehearsed shape you fill
in with problem-specific content, freeing your working memory to focus on the actual
design instead of "what do I do next."

## How it works

### Step 0: Treat it as a conversation, not an exam
Before any framework detail: the interviewer is a collaborator, not an adversary. They
often know the "expected" answer and are watching whether you can get there together.
Think out loud constantly — silence is the single biggest signal-killer in this format,
because the interviewer cannot grade what they cannot observe. If you get stuck, say so
and think out loud about what's blocking you; that is still useful signal, whereas
silent thinking looks identical to being lost.

### Step 1: Understand the problem and establish scope (~5 minutes)
Never start designing immediately. Ask clarifying questions to pin down:
- **Which features matter?** "Design Twitter" could mean posting tweets, the news feed,
  search, trends, DMs, notifications — you cannot design all of it in 45 minutes. Ask:
  "Which of these should we focus on?"
- **Scale.** How many users total? How many daily active users (DAU)? Is this a
  greenfield system or an existing one being redesigned? Read-heavy or write-heavy?
- **Non-functional priorities.** Does this system need strong consistency (e.g., a
  payment ledger) or is eventual consistency acceptable (e.g., a like counter)? Is low
  latency critical (e.g., autocomplete) or is throughput what matters (e.g., analytics)?
- **Growth.** Is the product growing 10% a year or is it expected to 100x in 12 months?
  This changes whether you should design for today's scale or engineer in headroom.

Example exchange for "design a news feed system":
> **Candidate:** "Should this support only text posts, or images/video too?"
> **Interviewer:** "Text and images for now."
> **Candidate:** "Can a user's feed include posts from people they don't follow, like
> ads or recommended content, or purely from who they follow?"
> **Interviewer:** "Purely from who they follow, for this exercise."
> **Candidate:** "Roughly how many users, and what's the max follower count for a
> single account — are we talking regular users only, or do we need to handle
> celebrities with tens of millions of followers?"
> **Interviewer:** "300 million DAU, and yes, some accounts have 30 million+
> followers."

That last answer alone determines whether a naive design works (it does not — see
`system-design-interview/11` for why celebrity accounts break simple fan-out).

Write the agreed scope down (verbally or on the whiteboard) as a short list of
in-scope and explicitly out-of-scope features. This anchors the rest of the interview
and gives you something to point back to if you start drifting into unnecessary detail.

### Step 2: Propose a high-level design and get buy-in (~10 minutes)
Sketch the main components and how data flows between them: clients, load balancer(s),
API/application servers, cache, database(s), and any async pieces (queues, background
workers). Keep it at the box-and-arrow level first — do not pick a specific database
product yet.

```
[Client] --> [Load Balancer] --> [API Servers] --> [Cache] --> [Database]
                                        |
                                        v
                                  [Message Queue] --> [Workers] --> [Object Storage]
```

Walk the interviewer through a couple of concrete request paths using this diagram
("when a user posts a tweet, the request hits the load balancer, gets routed to an API
server, which writes to the database and pushes an event onto the queue for fan-out
workers to process..."). This does two things: it validates the design does what it's
supposed to, and it gives the interviewer a natural point to redirect you ("actually,
let's focus more on the read path").

For back-of-the-envelope math to size these components (QPS, storage, bandwidth), see
`system-design-interview/02`.

### Step 3: Design deep dive (~15-20 minutes)
This is where the interview is actually won or lost. Pick — or let the interviewer
point you to — the one or two hardest parts of the system and go deep:
- What is the data model, and why?
- Where are the bottlenecks (a single database node, a hot cache key, a single queue
  consumer)?
- How do you handle failure (a server crashes mid-request, a network partition splits
  the cluster, a downstream service times out)?
- What are the specific trade-offs of the choice you made, and what would you do
  differently under different constraints?

For "design a news feed system," the deep dive is almost always fan-out-on-write vs.
fan-out-on-read and how to handle celebrity accounts (a hybrid approach). For "design a
rate limiter," it's which algorithm to use and how to make it work correctly across
multiple servers. Depth beats breadth here: a thorough treatment of one hard problem is
worth more than a shallow tour of five easy ones.

### Step 4: Wrap up (~5 minutes)
If time remains, the interviewer may ask you to:
- Identify bottlenecks and single points of failure in what you drew, and how you'd
  remove them (replication, redundancy, sharding).
- Discuss operational concerns: metrics, monitoring, alerting, how you'd roll out a
  change safely.
- Reflect on trade-offs you made and how the design would change under a different
  constraint ("what if this needed to support 10x the write volume?").
- Mention what you did not have time to cover, briefly, so the interviewer knows you
  are aware of the gap rather than ignorant of it.

### Time budget as a first-class tool
A common failure mode is spending 25 minutes on requirements and high-level design and
then rushing (or never reaching) the deep dive, which is where most of the signal
lives. A workable default split for a 45-minute interview:

| Step | Time | Failure if you overspend | Failure if you underspend |
| --- | --- | --- | --- |
| 1. Requirements | ~5 min | Never get to design the thing | Design the wrong thing |
| 2. High-level design | ~10 min | No time for depth | Interviewer can't follow your later reasoning |
| 3. Deep dive | ~15-20 min | (this is where you want the time) | Interview reads as shallow |
| 4. Wrap-up | ~5 min | — | Missed chance to show awareness of trade-offs |

Explicitly checking in on time ("I want to make sure we get to the deep dive — should
we move on from requirements?") is itself a positive signal: it shows you manage scope
like you would on a real project with a deadline.

### Worked mini-example: applying the framework to "design a parking garage"
Even a smaller, less distributed-systems-flavored prompt benefits from the same shape:
1. **Clarify:** How many levels/spots? Multiple vehicle types (car, motorcycle, bus)?
   Multiple entrances? Automated payment or a human attendant? (Suppose: 5 levels, 3
   spot types, automated entry/exit, single garage — not a multi-location chain.)
2. **High-level design:** A `ParkingGarage` composed of `Level`s, each composed of
   `Spot`s; an `EntrancePanel` that issues tickets; an `ExitPanel` that computes fees.
3. **Deep dive:** Concurrency — two cars approaching the last compatible spot at once.
   Spot-assignment strategy — nearest-available vs. pre-reserved. Fee calculation with
   different rates per vehicle type and time-of-day.
4. **Wrap-up:** What changes if this becomes a multi-garage chain with a shared
   reservation system across locations?

The same four steps apply whether the system is "Twitter" or "a parking garage" —
which is exactly why the framework, not the specific answer, is the transferable skill.

## Pros
- **Converts an unbounded problem into a bounded one.** Scoping in Step 1 stops you
  from trying to design everything.
- **Produces a natural time budget**, preventing the single most common interview
  failure (running out of time before the deep dive).
- **Gives the interviewer repeated chances to redirect you**, which reduces the risk of
  spending 20 minutes on a part of the system they don't care about.
- **Transfers to real work.** The same shape — clarify scope, sketch the design,
  identify and solve the hard part, review trade-offs — is how real design docs and
  design-review meetings are run.

## Cons
- **Can feel mechanical** if followed rigidly without adapting to the interviewer's
  signals; a framework is a scaffold, not a script to recite.
- **Requirements-gathering can be overdone.** Some candidates ask so many clarifying
  questions that they eat into design time without the questions actually changing the
  design. Ask questions that would change your architecture, not questions for their
  own sake.
- **Does not by itself supply system design knowledge.** The framework organizes your
  time and communication; you still need to know what a load balancer, cache, or
  message queue does and when to reach for one (see `system-design/*` and the
  remaining lessons in this subject).

## Alternatives
- **Diving straight into a "textbook" architecture** (e.g., always proposing
  microservices + Kafka + Redis regardless of scale) — faster to start, but signals
  you're pattern-matching rather than reasoning about this problem's actual
  constraints, and it usually breaks down when the interviewer asks "why?"
- **A pure bottom-up approach** (start from the data model and build up) — useful when
  the interviewer explicitly wants a data-modeling-heavy session, but it tends to lose
  the big picture and eats time before you've validated scope with the interviewer.
- **A pure top-down "whiteboard everything first" approach** (draw the full final
  architecture before discussing any of it) — can look impressive but doesn't leave
  room for the interviewer's input, and if your first assumption about scope was wrong,
  you've wasted the whiteboard.

The four-step framework in this lesson is essentially a structured middle ground: scope
first (avoids wasted work), then top-down sketch (keeps the big picture and invites
feedback), then bottom-up depth on the hardest part (where signal actually lives).

## When to use it
Use this framework for any open-ended "design X" interview prompt, and more broadly for
any real-world situation where you must scope and communicate a system design under
time pressure: a design review, a technical proposal document, an incident postmortem
where you need to propose a fix. The core discipline — clarify scope, sketch before
detailing, budget your time, go deep on the hard part — generalizes well beyond
interviews.

## When NOT to use it
Do not force the full four-step ritual onto a question that isn't actually open-ended.
If an interviewer asks a narrow, well-defined question ("how would you implement a
sliding-window rate limiter in Redis?"), extensive requirements-gathering about DAU and
growth projections is wasted motion — recognize the question's actual scope and answer
at the right altitude. Similarly, in a whiteboard/take-home format with no live
interviewer to redirect you, you cannot rely on Step 1's back-and-forth to validate
scope — state your assumptions explicitly instead and move on.

## Key takeaways / mental model
Think of the interview as a funnel: wide at the top (clarify what's even being built),
narrowing through a high-level sketch (agree on the shape), narrowing further into a
deep dive (prove you can solve the hardest part), and a final check for gaps. Time
spent widening the funnel too much at the top starves the bottom, where the real signal
is. The framework's job is to keep you moving down the funnel instead of getting stuck
at one level.

## Self-check questions
1. Why is asking "how many daily active users?" a better clarifying question than "what
   programming language should I use?" in the first five minutes of the interview?
2. You've spent 20 minutes gathering requirements for "design a URL shortener" and
   haven't drawn anything yet. What should you do, and why?
3. An interviewer says nothing while you talk for two straight minutes about a database
   choice without asking any questions back. What does that likely mean about whether
   you're using this framework well?
4. For "design a chat system," which step of the framework would surface that message
   ordering and delivery guarantees are the hard part, rather than, say, the choice of
   programming language for the server?
5. How would you adapt this framework for a take-home design document with no live
   interviewer to redirect you?

## References
- *System Design Interview – An Insider's Guide, Vol. 1* (Alex Xu), Chapter 1
