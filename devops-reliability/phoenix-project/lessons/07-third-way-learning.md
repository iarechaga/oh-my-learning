---
id: phoenix-project/07
subject: phoenix-project
title: "The Third Way: Continual Learning and Experimentation"
slug: third-way-learning
status: drafted
mastery:
seniority: staff
source: The Phoenix Project (Kim, Behr, Spafford), Part 2-3
prerequisites: [phoenix-project/05, phoenix-project/06]
created: 2026-08-10
updated: 2026-08-10
---

# The Third Way: Continual Learning and Experimentation

## TL;DR
The **Third Way** is the principle that an organization should deliberately create a culture of ongoing experimentation and learning: taking risks in a controlled way, treating failures as sources of organizational knowledge rather than occasions for blame, and repeatedly reinforcing practices (through repetition and drilling) until they become genuine capability, not just a one-time fix. Where the First Way (`phoenix-project/05`) makes work flow fast and the Second Way (`phoenix-project/06`) makes feedback flow fast, the Third Way is about compounding that fast feedback into permanent, organization-wide improvement instead of relearning the same lessons incident after incident.

## The idea
Fast flow and fast feedback are necessary but not sufficient. An organization can have both and still fail to actually *improve* over time, if each incident's lessons stay local — known only to the engineer who handled it, forgotten within weeks, never turned into a changed process, a new automated check, or a shared piece of institutional knowledge. The Third Way closes this final gap: it's the discipline of converting individual, local learning into organizational, durable capability, through practices like blameless postmortems, deliberate practice (game days, chaos engineering, fire drills), and allocating real time for improvement work rather than treating every hour as committed to feature delivery.

The book dramatizes this through Parts Unlimited's cultural transformation in its final act: incidents stop being treated as occasions to find someone to blame (echoing `phoenix-project/01`) and start being treated as valuable, if expensive, sources of data about where the system is weak. The company begins deliberately scheduling "practice" — rehearsing failure scenarios before they happen for real — rather than only ever encountering them for the first time during an actual crisis. This is the crucial difference between an organization that merely *survives* incidents and one that gets measurably better after each one.

## How it works

### From local fix to organizational capability
When an incident happens and gets fixed, there are at least three different levels at which "learning" can stop, and the Third Way pushes for the deepest one:

1. **Local, tacit fix** — the responding engineer fixes the immediate problem and remembers what they did, but nothing changes elsewhere; if a different engineer hits a similar problem next month, they start from zero.
2. **Documented fix** — the fix and its cause get written up somewhere (a runbook, a wiki page), so the *next* person facing the same specific problem can find the answer faster — real progress, but still reactive.
3. **Systemic capability change** — the underlying condition that made the incident possible gets addressed structurally: a new automated check that would have caught it before production, a new class of test added to the pipeline, a design pattern discouraged organization-wide, or a piece of tooling built so the failure mode becomes structurally impossible rather than merely documented.

**Worked example.** An engineer discovers, during an incident, that a particular database migration pattern (adding a NOT NULL column without a default on a large table) causes a multi-minute table lock that takes down the service. Level 1: they fix this one migration and move on. Level 2: they add a note to the team wiki about this pattern. Level 3: they add an automated linter check to the CI pipeline that flags this exact migration pattern on any pull request, org-wide, before it can ever reach production again — converting one engineer's hard-won incident knowledge into a permanent, self-enforcing organizational capability that protects every future team, including ones who never heard the original story.

### Deliberate practice: rehearsing failure before it's real
A distinguishing Third Way practice is scheduling controlled failure *before* the real thing happens — game days, fire drills, and (at more mature organizations) chaos engineering, where a team deliberately injects a realistic failure into a system (kills a server, throttles a database, simulates a region outage) during a planned window, specifically to find out whether the organization's detection and response actually works, and to build the muscle memory for handling it under low-stakes conditions.

**Worked example.** A payments team runs a quarterly "game day" where they simulate their primary database becoming unavailable during business hours, in a staging environment closely mirroring production, with the on-call engineer treating it exactly like a real incident (following the real runbook, paging the real escalation chain). The first game day reveals the documented failover runbook is two versions out of date and would have made the real outage worse if followed literally; the team fixes the runbook, then re-runs a similar drill next quarter and completes failover in 4 minutes instead of the first attempt's 35. This is the Third Way's compounding effect in action: each drill both surfaces a gap and verifies the previous fix actually worked, building real (not assumed) organizational readiness.

### Repetition and mastery, not one-time fixes
A related, easy-to-miss element of the Third Way: genuine capability requires *repeated* practice, not a single corrective action. Erik's teaching draws an analogy to how the U.S. Navy trains damage-control teams — not through a single lecture on what to do if the ship is hit, but through repeated, realistic drills until the response is close to automatic, because under real crisis conditions, people fall back on trained reflexes, not on documentation they read once. A postmortem action item that says "we added a check" but was never tested under realistic pressure is a level-2 fix wearing level-3 clothing — genuine Third Way maturity means periodically re-verifying that safeguards actually work, not just that they were once built.

### Allocating explicit time and slack for learning
The Third Way requires organizational slack — time genuinely set aside for improvement work, postmortem follow-through, and drills — rather than treating 100% of capacity as committed to feature delivery. This directly echoes `phoenix-project/04`'s WIP-limit logic: an organization running at full utilization with zero slack has no capacity left to run a game day, write up a thorough postmortem, or build the automated check that would prevent a recurrence — the learning work competes with delivery work for the same constrained capacity, and without an explicit allocation, delivery pressure will always win in the moment, even though skipping the learning work guarantees the same incidents recur.

**Worked example.** Two teams both have serious incidents in the same month. Team A immediately returns 100% of capacity to the next feature deadline once the incident is resolved; six weeks later, a near-identical incident recurs, because nobody had time to build the systemic fix. Team B allocates 20% of the following two sprints specifically to postmortem follow-through — building the automated check, updating the runbook, running a verification drill — and does not experience a recurrence of that failure class for the rest of the year. The total engineering hours invested are comparable; the difference is that Team B treated learning as a first-class allocation, not a hoped-for side effect of goodwill.

## Pros
- Converts expensive incidents into durable, compounding organizational capability instead of one-off local fixes that leave the same systemic weakness in place for the next person to rediscover.
- Deliberate practice (game days, drills) finds gaps in detection, runbooks, and response *before* they're discovered during a real, high-stakes incident.
- Builds genuine organizational confidence and resilience over time, measurably reducing the frequency and severity of recurring failure classes.

## Cons
- Requires real, protected time investment that competes directly with feature delivery, and is one of the first things cut under deadline pressure — exactly the trap Parts Unlimited starts in.
- Deliberate failure injection (game days, chaos engineering) carries real operational risk if not carefully scoped and requires organizational maturity (strong Second Way feedback, good rollback capability) to run safely.
- Learning only compounds if it's actually captured and enforced systemically (level 3, not level 1 or 2) — an organization that documents lessons but never builds structural safeguards, or never re-verifies them, gets the appearance of a learning culture without its actual protective effect.

## Alternatives
- **Reactive-only incident response** — fix each incident as it happens and move on, with no deliberate practice or systemic follow-through; cheaper in the short term, but guarantees recurring failure classes, exactly Parts Unlimited's starting state.
- **Formal training programs without real-system drills** — invest in classroom-style training or documentation without realistic, hands-on rehearsal; builds some knowledge but misses the "trained reflex under pressure" benefit that realistic drills provide, per the Navy damage-control analogy.
- **External audits/reviews as the primary learning mechanism** — rely on periodic outside assessment (security audits, compliance reviews) to surface systemic gaps, rather than continuous internal practice; useful as a complement, but typically far less frequent and less tailored to the organization's actual failure modes than internally-run game days and blameless postmortems.

## When to use it
Invest in Third Way practices once fast flow (`phoenix-project/05`) and fast feedback (`phoenix-project/06`) are reasonably established — the Third Way's compounding value depends on already having a functioning feedback loop to learn from. It's essential for any system where failure classes tend to recur, where the cost of an incident is high enough to justify deliberate rehearsal, or where key-person dependency (`phoenix-project/03`) means institutional knowledge needs to be actively spread rather than left with one person.

## When NOT to use it
Don't over-invest in elaborate deliberate-practice programs (frequent, large-scale game days) for low-stakes systems where the cost of an occasional real incident is genuinely lower than the cost of regular rehearsal — proportionality matters. Also avoid running failure-injection drills before the organization has the Second Way feedback maturity (`phoenix-project/06`) and rollback capability to handle a drill that goes wrong safely; practicing failure in a system that can't yet detect or recover from failure reliably just creates real incidents with extra steps.

## Key takeaways / mental model
After every incident, ask: did we fix the instance, or did we fix the class? And separately: have we actually verified, under realistic conditions, that the fix works — or do we just believe it does because nobody's tested it since? An organization that consistently pushes learning to level 3 (systemic, verified capability) and protects real time to do so gets measurably safer over time; one that stops at level 1 or 2 relearns the same lessons indefinitely.

## Self-check questions
1. Using the database-migration worked example, explain the practical difference between a level-2 fix (documented) and a level-3 fix (systemic, automated) in terms of what happens when a *different* engineer, unaware of the original incident, makes a similar mistake.
2. Why does the Third Way depend on the Second Way already being reasonably mature? What goes wrong if an organization tries deliberate failure-injection drills before it has fast, reliable feedback loops?
3. A team's postmortems consistently produce well-written action items, but six months later the same failure classes keep recurring. Using the "capacity and slack" worked example, what's the most likely explanation, and what would you check?
4. Design a lightweight game-day exercise for a system you're familiar with (or a plausible hypothetical one). What specific failure would you inject, what would you want to learn, and what would count as a good versus a concerning result?

## References
- The Phoenix Project (Kim, Behr, Spafford), Part 2-3 (Erik's Three Ways framework and the book's cultural-transformation arc).
- See also `phoenix-project/05` (First Way) and `phoenix-project/06` (Second Way), which the Third Way builds on, and `devops-handbook/12` and `devops-handbook/13` (incident feedback loops and blameless postmortems), which operationalize this concept into concrete practice.
