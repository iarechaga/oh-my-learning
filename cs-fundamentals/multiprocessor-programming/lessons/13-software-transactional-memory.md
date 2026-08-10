---
id: multiprocessor-programming/13
subject: multiprocessor-programming
title: Software transactional memory and composable synchronization
slug: software-transactional-memory
status: drafted
mastery:
seniority: senior
source: The Art of Multiprocessor Programming (Herlihy & Shavit), Chapter 18
prerequisites: [multiprocessor-programming/10, multiprocessor-programming/08]
created: 2026-08-10
updated: 2026-08-10
---

# Software transactional memory and composable synchronization

## TL;DR
Software transactional memory (STM) lets you write concurrent code as a block that
appears to execute atomically — read and write shared state freely inside it — while the
runtime tracks accesses, detects conflicts with other concurrent transactions, and
automatically aborts and retries on conflict. Its headline advantage over hand-written
locks is **composability**: two independently-written transactional operations can be
combined into one larger atomic operation just by nesting them, something locks
famously cannot do safely without global coordination.

## The idea
`multiprocessor-programming/02` introduced locks, and every lesson since has shown ways
to make locking faster (`multiprocessor-programming/04`), or to avoid it altogether via
lock-free CAS-based algorithms (`multiprocessor-programming/10`,
`multiprocessor-programming/11`). But hand-crafting a lock-free algorithm for every new
data structure is genuinely hard (`multiprocessor-programming/08`'s universal
construction exists precisely because this is hard), and even ordinary lock-based code
has a well-known composability failure: if you have two independently correct,
lock-protected operations (say, `withdraw(accountA)` and `deposit(accountB)`, each
correctly locking its own account), there's no *general*, safe way to combine them into
a single atomic "transfer" operation without either introducing new deadlock risk
(acquiring both locks in a consistent global order requires every piece of code
everywhere to agree on that order) or exposing an intermediate, inconsistent state to
other threads. STM is a different strategy for the same underlying goal (correct
concurrent access to shared state) that sidesteps this composability problem by making
the *unit of synchronization* an explicit, nestable transaction, borrowing an idea
directly from database systems.

## How it works

### The transactional API, conceptually
A transaction is a block of code the programmer marks as atomic:

```
atomic {
    x = read(accountA.balance)
    write(accountA.balance, x - 100)
    y = read(accountB.balance)
    write(accountB.balance, y + 100)
}
```

The runtime's job: make this block **appear** to execute as one indivisible step from
every other thread's perspective — either the whole block's effects become visible
atomically, or (if a conflict is detected) none of them do, and the block is transparently
retried. The programmer never explicitly acquires a lock; they simply declare "this
region needs to happen atomically" and the runtime figures out how.

### Optimistic execution and conflict detection
Most STM implementations execute a transaction **optimistically**: run the block's
reads and writes against a private, per-transaction log (a **read set** recording which
locations were read and what value was observed, and a **write set** recording pending
writes not yet made globally visible) rather than directly against shared memory. At
**commit time**, the runtime validates: for every location in the read set, is the value
still what was observed when read (i.e., did any other committed transaction change it in
the meantime)? If validation succeeds, the write set is applied atomically (often via a
single CAS or a short critical section internal to the STM runtime itself); if validation
fails, the transaction **aborts** — all its tentative reads/writes are discarded, and it
automatically retries from the beginning, typically with backoff
(`multiprocessor-programming/04`'s contention-management idea, reused here).

**Worked example: detecting a conflict.** Two threads concurrently run the transfer
transaction above, both starting from `accountA.balance = 500`, `accountB.balance = 200`.
1. Thread 1 begins: reads `accountA.balance = 500` into its read set, computes
   `500 - 100 = 400`, stages `write(accountA.balance, 400)` in its write set (not yet
   visible to anyone).
2. Thread 2 begins concurrently, and — through some other transaction entirely — commits
   a change to `accountA.balance`, say a deposit bringing it to 600, fully visible to
   other threads now.
3. Thread 1 continues and reaches commit time: it validates its read set, re-checking
   `accountA.balance` — but it's now 600, not the 500 Thread 1 originally read. Validation
   fails.
4. Thread 1's transaction **aborts**: all its staged writes are discarded, and it retries
   from the start, this time correctly reading `accountA.balance = 600` and computing
   `600 - 100 = 500`.

No lock was ever held across this interaction; the conflict was detected and resolved
entirely through read-set validation at commit time. This is directly analogous to
`multiprocessor-programming/06`'s optimistic-locking linked list (traverse freely,
validate before committing) but generalized to arbitrary blocks of code touching
arbitrary shared locations, not just a specific data structure's pointers.

### Composability: the headline advantage
Because the unit of atomicity is an explicit `atomic { ... }` block rather than a
specific lock instance, two independently-written transactional operations compose for
free: wrapping two existing `atomic` blocks inside one larger `atomic` block (nesting)
makes the combination itself atomic, with no new deadlock risk and no need for the two
pieces of code to have been written with any awareness of each other's internal locking
strategy.

**Worked example: composing transfer with a logging operation.** Suppose you already
have `atomic { transfer(A, B, 100) }` and, separately, `atomic { appendLog(entry) }`, each
independently correct. With locks, safely combining "transfer AND log it atomically
together" would require either a new shared lock spanning both (invasive — you'd have to
modify both pieces of code to know about a shared lock) or accepting a window where the
transfer is visible but the log entry isn't yet (or vice versa). With STM, you simply
write `atomic { transfer(A, B, 100); appendLog(entry); }` — nesting the two existing
transactional blocks inside a new one — and the runtime guarantees the combination is
atomic, with no changes needed to either original piece of code. This is the concrete,
practical payoff of composability, and it's a genuine capability gap locks cannot close
in general.

### Read-only vs. read-write transactions, and the retry cost
Read-only transactions can often commit cheaply (no writes to apply, sometimes no
validation needed at all depending on the STM implementation's guarantees) — an important
practical performance characteristic given how often real workloads are read-dominated
(the same observation that motivated `multiprocessor-programming/06`'s lazy
synchronization for lists). The main performance risk with STM is **wasted work under
high contention**: a long transaction that conflicts and aborts near its end has to redo
all of its work from scratch, which can be far more wasteful than a short critical
section under a traditional lock that simply makes other threads wait rather than
discarding completed work — this is STM's central performance trade-off versus locking.

### Progress guarantees of STM
Plain optimistic STM as described gives something close to obstruction-freedom
(`multiprocessor-programming/07`): a transaction completes if it can run without
conflicting writes from others long enough to validate and commit, but under sustained
contention, transactions can repeatedly abort and retry indefinitely (a livelock risk,
just like obstruction-free algorithms in general) unless a contention-management policy
(prioritizing older transactions, randomized backoff, or bounding retries before falling
back to locking) is layered on top — the same mitigation pattern
`multiprocessor-programming/07` described for obstruction-free algorithms generally.
Some STM designs achieve stronger (lock-free or even wait-free) guarantees at the cost of
more complex implementations.

## Pros
- Composability: independently-written atomic blocks combine safely by nesting, closing
  a real, well-known gap in lock-based code that has no general safe solution.
- Removes an entire class of lock-ordering bugs (deadlock from inconsistent lock-
  acquisition order) — there are no explicit locks for the programmer to order
  inconsistently in the first place.
- Lets the programmer write what *looks like* simple sequential code (no manual lock
  acquire/release, no hand-designed CAS-retry loop) while the runtime handles the
  concurrency machinery — a real reduction in the cognitive load of correct concurrent
  programming.

## Cons
- Performance under high contention can be worse than well-tuned locks: aborted
  transactions discard completed work entirely, unlike a blocked thread waiting on a lock
  (which loses only time, not completed computation).
- I/O and other externally-visible side effects (printing, network calls, writes to
  non-transactional memory) inside a transaction are deeply problematic — if the
  transaction aborts and retries, an already-executed side effect (like a sent network
  request) cannot be "undone" the way an in-memory write can be discarded; real STM
  systems require careful discipline (or explicit unsafe escape hatches) around this.
- Implementation complexity is substantial (efficient read/write-set tracking,
  validation, contention management) — mature STM runtimes are non-trivial systems in
  their own right, and STM has seen less mainstream production adoption than lock-free
  data structures or plain locks, partly due to these overheads and partly due to the
  I/O problem above.

## Alternatives
- **Universal constructions** (`multiprocessor-programming/08`) — another generic
  technique for making arbitrary code concurrent, built on consensus and explicit
  operation-list replay rather than optimistic execution with rollback; STM is generally
  more practical for expressing "run this block of arbitrary code atomically" while
  universal constructions are framed around turning a specific sequential *object*
  concurrent.
- **Fine-grained hand-written locking or lock-free algorithms**
  (`multiprocessor-programming/06`, `multiprocessor-programming/11`) — better raw
  performance for a specific, well-understood data structure, at the cost of losing
  composability and requiring bespoke design/proof effort per structure.

## When to use it
Reach for STM (where a mature runtime/language support exists — e.g. Clojure's `ref`s and
STM, Haskell's STM monad) when you need to compose multiple independently-developed
atomic operations into larger atomic operations, and your transactions are short,
memory-only (no I/O inside), and contention is low-to-moderate. It shines specifically in
codebases where lock-ordering discipline across many independently-written modules would
otherwise be a recurring source of deadlock bugs.

## When NOT to use it
Don't use STM for transactions containing I/O or other non-undoable side effects — the
abort-and-retry model fundamentally assumes all effects are revocable, which I/O
generally is not. Don't reach for STM under sustained high contention with long
transactions — the wasted-work-on-abort cost can make it perform substantially worse
than a well-designed lock or a hand-crafted lock-free structure
(`multiprocessor-programming/11`) for that specific workload. Don't use it in languages/
runtimes without solid, well-tested STM support — a hand-rolled STM implementation is a
serious undertaking, not something to build ad hoc for a single project.

## Key takeaways / mental model
STM replaces "acquire specific locks in a specific order" with "declare this block
atomic and let the runtime detect conflicts optimistically, aborting and retrying on
collision" — the same optimistic-traversal-then-validate pattern seen in
`multiprocessor-programming/06`'s lists, generalized to arbitrary code. Its unique,
genuine advantage is composability: atomic blocks nest safely, closing a gap locks cannot
close in general. Its cost is wasted work on abort and fundamental incompatibility with
irrevocable side effects like I/O — which is why STM is a specialized tool for
memory-only, composable atomicity, not a universal replacement for locks or lock-free
algorithms.

## Self-check questions
1. Walk through the transfer-transaction worked example and explain exactly what causes
   Thread 1's transaction to abort, and why discarding and retrying is the correct
   response rather than proceeding with stale data.
2. Explain, with a concrete example, why locks cannot safely compose two independently-
   written lock-protected operations into one atomic operation in general, while STM's
   `atomic` blocks can.
3. Why is performing a network call or other I/O inside an `atomic` block dangerous under
   STM's abort-and-retry model?
4. Given a system with short, memory-only operations that are frequently composed in new
   combinations by different teams, versus a system with one performance-critical,
   heavily-contended queue — which situation favors STM, and which favors a hand-crafted
   lock-free structure? Justify both.

## References
- The Art of Multiprocessor Programming (Herlihy & Shavit), Chapter 18: "Transactional
  Memory."
