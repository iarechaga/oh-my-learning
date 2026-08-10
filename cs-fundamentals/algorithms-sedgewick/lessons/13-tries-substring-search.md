---
id: algorithms-sedgewick/13
subject: algorithms-sedgewick
title: Tries and substring search algorithms
slug: tries-substring-search
status: drafted
mastery:
seniority: mid
source: Algorithms (Sedgewick, Wayne), Sections 5.2-5.3
prerequisites: [algorithms-sedgewick/07, algorithms-sedgewick/09]
created: 2026-08-10
updated: 2026-08-10
---

# Tries and substring search algorithms

## TL;DR
Strings are not just "keys with a comparison operator" — treating a string's individual
characters as first-class lets a **trie** answer prefix queries a hash table or BST
fundamentally cannot, and lets substring-search algorithms (Knuth-Morris-Pratt,
Boyer-Moore, Rabin-Karp) beat brute-force search by exploiting information the naive
character-by-character comparison throws away.

## The idea
`algorithms-sedgewick/07` and `/09` treat keys generically — a BST or hash table works
the same whether keys are integers or strings, because both only ever ask "is this key
equal to / less than that key?" A trie throws that generality away deliberately: it
indexes directly on a string's individual characters, one per level of the tree, which
unlocks operations no comparison-based or hash-based structure can answer efficiently —
"all keys starting with prefix P" being the standout example. Substring search asks a
different question: given one long text and one pattern, find the pattern's occurrences
— and the naive approach (try every starting position, compare character by character)
wastes information every time a mismatch occurs partway through a candidate match.

## How it works

### The trie: one node per character, not per key
A trie (from re**trie**val) is a tree where each edge is labeled with a character, and a
root-to-node path spells out a string prefix. Each node has an array (or symbol table)
of child links, one per possible next character, plus a flag or value marking whether the
path to this node spells a complete key (not just a prefix of some longer key).

Worked example: inserting "SHE", "SHELLS", "SEA" into an empty trie. Root has a child
edge 'S'. That node has a child edge 'H' (from SHE, SHELLS) and a child edge 'E' (from
SEA). Following S->H, add child 'E' (marks end-of-key for "SHE") then continue S->H->E
with child 'L', 'L', 'S' (marks end-of-key for "SHELLS"). Following S->E, add child 'A'
(marks end-of-key for "SEA"). Searching for "SHE": follow S->H->E, land on a node marked
end-of-key — found. Searching for "SH": follow S->H, land on a node *not* marked
end-of-key — "SH" is a prefix of stored keys but not itself a stored key, correctly
reported as absent. Prefix query "keys starting with SH": follow S->H, then explore the
entire subtree rooted there, collecting every marked node — returns "SHE" and "SHELLS"
in one subtree walk, something no hash table can do without scanning every key.

### Why tries beat hash tables and BSTs for string workloads
A hash table's `get` is expected O(1) *regardless of key length only after hashing*, but
computing the hash itself requires reading every character — and a hash table has no
notion of "nearby" keys at all, so prefix queries require a full scan. A BST orders keys
by full-string comparison, which for two similar long strings (e.g. sharing a 50-character
prefix) means every comparison along the search path re-scans that shared prefix
repeatedly. A trie search for a string of length L costs O(L) character examinations
total, *regardless of how many keys are stored or how similar they are to each other* —
each character is examined exactly once, on the way down.

### R-way tries vs. ternary search tries (TSTs)
The child-array-per-node design (an **R-way trie**, R = alphabet size) is fast (O(1) to
find the right child) but wastes space: most nodes only have a handful of actual
children out of R possible slots, especially deep in the tree. A **ternary search trie
(TST)** trades the flat R-way array for a small binary-search-tree-like structure at each
node (left/middle/right children, comparing against one stored character: less-than,
equal-follow-to-next-char, greater-than) — dramatically less space per node, at the cost
of needing O(log R) comparisons instead of O(1) to pick the right child. In practice,
TSTs are the more commonly used structure precisely because real-world tries are sparse.

### Substring search: exploiting information brute force wastes
Given text of length N and pattern of length M, brute-force search tries every one of the
N-M+1 starting positions, comparing up to M characters each — O(NM) worst case (e.g.
searching "AAAAAAAAB" for "AAAB" in a text of A's re-compares most characters at every
shifted position). Smarter algorithms avoid this by remembering *what was already
matched* when a mismatch occurs, instead of discarding that information and restarting
from scratch one position over:

- **Knuth-Morris-Pratt (KMP)**: precompute, for the pattern alone, a "failure function"
  (a deterministic finite-state automaton over the pattern) that says, on a mismatch after
  matching J characters, exactly how far the pattern's own internal structure lets you
  skip — never re-examining a text character already consumed. Guarantees O(N + M) worst
  case, at the cost of O(M) preprocessing and a somewhat intricate automaton construction.
- **Boyer-Moore**: scan the pattern **right to left** against the text, and on a
  mismatch, use a precomputed "bad character" rule — jump the pattern forward based on
  where (or whether) the mismatched text character appears elsewhere in the pattern,
  potentially skipping multiple text positions in one step. Often sub-linear in practice
  (doesn't examine every text character), though worst case is O(NM) without the
  additional "good suffix" rule.
- **Rabin-Karp**: hash the pattern once, then compute a **rolling hash** of every
  length-M substring of the text incrementally (each new window's hash is derived from
  the previous one in O(1), not recomputed from scratch) and compare hash values first,
  only doing a full character comparison on a hash match (to rule out false positives
  from hash collisions). Simple to implement correctly and generalizes cleanly to
  multi-pattern search, at the cost of relying on hash quality for its average-case
  guarantee.

Worked example (Rabin-Karp intuition): searching for "234" in text "12342". Hash("234")
computed once. Rolling hash of "123" -> (subtract "1"'s contribution, shift, add "2") ->
rolling hash of "234" in O(1), which matches the pattern's hash — verify with a direct
character comparison to confirm (not a collision) — match found at position 1.

## Pros
- Tries answer prefix and "all keys starting with X" queries natively, in time
  proportional to the prefix length plus the number of matches — categorically faster
  than any comparison-based or hash-based alternative for this query type.
- Trie search cost depends only on the searched string's length, not on how many keys
  are stored or how similar keys are to each other, unlike BST comparisons on long
  shared-prefix strings.
- KMP and Boyer-Moore substring search give worst-case or practical sub-linear
  guarantees respectively, a real asymptotic improvement over brute force's O(NM) for
  large texts (log parsing, DNA sequence search, plagiarism detection).

## Cons
- R-way tries can waste substantial space (an array of R child pointers per node, mostly
  null) when the alphabet is large (e.g. full Unicode) or keys are sparse; TSTs mitigate
  this but add O(log R) overhead per character.
- KMP's failure-function construction and Boyer-Moore's bad-character/good-suffix rules
  are meaningfully more intricate to implement correctly than brute-force search — real
  complexity cost for the asymptotic/practical improvement.
- Tries (and substring search generally) are specialized to sequence data (strings, or
  more generally sequences with an ordered alphabet); they don't generalize to arbitrary
  comparable keys the way a BST does.

## Alternatives
- **Hash tables** (`algorithms-sedgewick/09`) — better when only exact-match lookup is
  needed and prefix queries are never required; simpler and often faster for pure
  membership/lookup workloads.
- **Brute-force substring search** — simplest to implement correctly, and often fine in
  practice for short patterns or infrequent searches where the O(NM) worst case is never
  actually approached by real input data.
- **Suffix trees/arrays** (not covered in depth here) — needed when many different
  pattern searches will be run against the *same* fixed text repeatedly (e.g. genome
  search tools), amortizing a larger upfront preprocessing cost across many queries.

## When to use it
Use a trie (TST in practice, for space efficiency) when prefix queries, autocomplete, or
"longest prefix match" (e.g. IP routing tables) are core requirements. Use KMP when a
worst-case linear guarantee matters (untrusted or adversarial input); use Boyer-Moore
when average-case speed on large texts matters more than worst-case guarantees; use
Rabin-Karp when searching for multiple patterns simultaneously or implementing
plagiarism/duplicate-detection style search.

## When NOT to use it
Don't reach for a trie when only exact-match lookup is needed and keys aren't
particularly similar to each other — a hash table is simpler and has lower constant
factors. Don't hand-roll KMP or Boyer-Moore for a one-off, non-performance-critical
substring search — most languages' built-in string search is already well-optimized, and
brute force is easier to get right for infrequent, small-scale use.

## Key takeaways / mental model
A trie indexes on individual characters rather than treating strings as opaque
comparable keys, which is what makes prefix queries and "longest matching prefix" cheap
in a way no comparison-based or hash-based structure can match; TSTs trade the R-way
trie's O(1)-per-character speed for much better space efficiency via a small
binary-search structure per node. Substring search algorithms beat brute force's O(NM)
by remembering information a naive restart-from-scratch approach throws away on every
mismatch — KMP via a precomputed pattern automaton, Boyer-Moore via right-to-left
scanning with skip rules, Rabin-Karp via incremental rolling hashes.

## Self-check questions
1. Walk through why a trie search for a string of length L costs O(L) regardless of how
   many keys are stored, while a BST search on long, similar strings can cost far more
   than O(L) comparisons.
2. Explain the specific space/time trade-off between an R-way trie and a ternary search
   trie, and why TSTs are more commonly used in practice.
3. Using the "AAAAAAAAB" text / "AAAB" pattern example, explain concretely why
   brute-force search is O(NM) here while KMP avoids re-examining already-consumed text
   characters.
4. Why does Rabin-Karp need to verify a hash match with a full character comparison
   before declaring a match, and what could go wrong if it skipped that verification?

## References
- Algorithms, 4th Edition (Robert Sedgewick, Kevin Wayne), Sections 5.2 ("Tries") and 5.3
  ("Substring Search").
