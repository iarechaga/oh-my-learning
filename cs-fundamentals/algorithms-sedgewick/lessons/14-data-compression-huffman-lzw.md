---
id: algorithms-sedgewick/14
subject: algorithms-sedgewick
title: Data compression (Huffman and LZW)
slug: data-compression-huffman-lzw
status: drafted
mastery:
seniority: senior
source: Algorithms (Sedgewick, Wayne), Section 5.5
prerequisites: [algorithms-sedgewick/06, algorithms-sedgewick/13]
created: 2026-08-10
updated: 2026-08-10
---

# Data compression (Huffman and LZW)

## TL;DR
Lossless compression comes in two fundamentally different flavors — **Huffman coding**
exploits *skewed symbol frequency* (some characters appear far more often than others) by
assigning shorter bit codes to common symbols, while **LZW** exploits *repeated
substrings* (patterns, not just individual symbols, recur) by building a dictionary of
seen substrings on the fly — and knowing which kind of redundancy your data has
determines which one actually compresses it well.

## The idea
All lossless compression relies on the same core fact: if a message has any statistical
structure at all (not every bit pattern equally likely), a scheme exploiting that
structure can, on average, represent the message using fewer bits than a naive
fixed-width encoding. The two structures this lesson covers are frequency skew (some
symbols much more common) and substring repetition (some sequences recur), and they call
for genuinely different algorithms — this is the practical payoff of a priority-queue
data structure (`algorithms-sedgewick/06`) and a trie-adjacent symbol table
(`algorithms-sedgewick/13`) applied to a concrete, high-value engineering problem rather
than an abstract exercise.

## How it works

### Fixed-width encoding as the baseline
Standard ASCII uses 8 bits per character regardless of frequency — 'e' costs the same 8
bits as 'z' even though 'e' appears far more often in English text. Compression's first
lever: if some symbols are far more common, giving them shorter codes and rare symbols
longer codes reduces the *average* bits per symbol, even though some symbols now need
more than 8 bits.

### Huffman coding: build the code from the frequency table
Huffman coding is a **greedy, provably optimal** algorithm (among prefix-free codes) for
this exact trade-off, built directly on a priority queue:

1. Count each symbol's frequency in the input.
2. Create a leaf node per symbol, weighted by frequency, and push all leaves onto a
   min-priority queue.
3. Repeatedly pop the two lowest-weight nodes, merge them into a new internal node whose
   weight is their sum, and push the merged node back — exactly the greedy
   two-cheapest-first pattern, using the same priority-queue machinery as
   `algorithms-sedgewick/06`.
4. Repeat until one node remains: the root of the **Huffman trie**. Each leaf's code is
   the sequence of left/right (0/1) edges from root to that leaf.

Worked example: frequencies A=45, B=13, C=12, D=16, E=9, F=5 (total 100, from CLRS's
classic example). Pop two lowest (F=5, E=9), merge into EF=14, push back. Pop two lowest
(C=12, D=16)? No — pop lowest two of {A=45, B=13, D=16, EF=14, C=12}: C=12 and B=13 are
lowest, merge into BC=25. Continue: {A=45, D=16, EF=14, BC=25} — pop D=16, EF=14, merge
into DEF=30. Continue: {A=45, BC=25, DEF=30} — pop BC=25, DEF=30, merge into BCDEF=55.
Finally: {A=45, BCDEF=55} — merge into root=100. Reading root-to-leaf paths gives A a
1-bit code (~45% of symbols cost 1 bit) and F a 4-bit code (~5% of symbols cost 4 bits) —
far better on average than a fixed 3 bits per symbol (needed for 6 distinct symbols).

**Why the codes are unambiguous (prefix-free):** since every symbol is a *leaf* in the
trie, no symbol's code is a prefix of another symbol's code — a decoder reading bits
left to right always knows exactly when one code ends and the next begins, with no
delimiter needed.

### LZW: build the dictionary from the data itself, on the fly
Huffman coding needs to know symbol frequencies upfront (or transmit the frequency table
alongside the compressed data). LZW (Lempel-Ziv-Welch) instead exploits **repeated
substrings** and requires no upfront statistics: it builds a dictionary of substrings
seen so far, incrementally, using the same trie-style structure from
`algorithms-sedgewick/13`.

1. Initialize the dictionary with every single-character string (codes 0-255 for bytes).
2. Scan the input, extending the current matched substring one character at a time as
   long as the extended substring is already in the dictionary.
3. The moment the extended substring is *not* in the dictionary: output the code for the
   longest substring that *was* found, add the (now one-longer) substring to the
   dictionary as a new entry, and restart the match from the last unmatched character.

Worked example: compressing "ABABABA" with an initial dictionary of {A:0, B:1}. Start
matching: "A" is in dict. Extend to "AB" — not in dict yet — output code for "A" (0), add
"AB" as new entry (code 2), restart matched substring at "B". "B" in dict. Extend to
"BA" — not in dict — output code for "B" (1), add "BA" (code 3), restart at "A". "A" in
dict. Extend to "AB" — *now* in dict (added in step 1)! Extend further to "ABA" — not in
dict — output code for "AB" (2), add "ABA" (code 4), restart at "A" (last character).
"A" in dict, end of input, output code for "A" (0). Result: codes [0, 1, 2, 0] represent
"ABABABA" (7 characters) in 4 codes — and critically, the dictionary was built with *no
upfront pass over the data* and needs no separate transmission, since the decoder
rebuilds the identical dictionary as it decodes, in lockstep.

### Why the two are complementary, not competing
Huffman coding compresses well when frequency is skewed but substrings don't repeat much
(e.g. a single long English sentence with typical letter frequencies but few repeated
multi-word phrases). LZW compresses well when substrings repeat, even if individual
character frequencies are close to uniform (e.g. source code with repeated keywords and
variable names, or genomic data with repeated motifs). Real-world compressors often
combine both ideas in sequence: DEFLATE (used in gzip, PNG, zip) runs an LZ77-family
substring-matching pass *followed by* Huffman coding on the resulting output — each
exploiting the redundancy the other doesn't target.

## Pros
- Huffman coding is provably optimal among prefix-free codes for a known, fixed symbol
  frequency distribution — no cleverer fixed-code scheme can do better on average.
- LZW requires no upfront statistics pass and no separately transmitted frequency
  table or dictionary — the decoder reconstructs the dictionary identically as it reads,
  which makes it well suited to streaming data.
- Both build directly on data structures already covered (priority queue, trie-style
  incremental symbol table), reinforcing that these aren't just abstract exercises but
  load-bearing components of real compression tools.

## Cons
- Huffman coding needs the frequency table upfront (or a pass over the data to compute
  it), and that table itself must be transmitted or agreed upon, adding overhead for
  small inputs.
- Huffman coding does *not* exploit substring repetition at all — text with highly
  repeated phrases but roughly uniform character frequency compresses poorly under pure
  Huffman coding.
- LZW's dictionary grows unboundedly with input size unless capped, and once capped,
  compression quality can degrade or require a dictionary-reset strategy; it also
  provides no optimality guarantee the way Huffman coding does for its target
  redundancy type.

## Alternatives
- **Run-length encoding** — simpler still, exploits only *consecutive repeated* symbols
  (not general substring repetition or frequency skew); effective for data like
  simple bitmap images with long runs of the same pixel value, ineffective otherwise.
- **Arithmetic coding** — like Huffman coding but not restricted to whole-bit-per-symbol
  codes, so it can approach the theoretical entropy limit more closely than Huffman
  coding when symbol probabilities aren't powers of two; more complex to implement.
- **DEFLATE (LZ77 + Huffman)** — the practical combination used by gzip/zip/PNG,
  layering substring-repetition compression and frequency-skew compression to capture
  both redundancy types in one format.

## When to use it
Use Huffman coding when symbol frequencies are known (or cheaply computable) and skewed,
and substring repetition isn't the dominant redundancy — or as a final compression stage
after a substring-matching pass. Use LZW when data has repeated substrings and no
upfront frequency analysis is desirable (streaming, unknown-distribution data) — it was
historically the core of GIF and Unix `compress`.

## When NOT to use it
Don't use pure Huffman coding on data whose redundancy is mostly repeated substrings
(source code, structured logs) — it will compress far worse than an
LZ-family approach because it never looks beyond single-symbol frequency. Don't use LZW
(or any general-purpose compressor) on data that's already compressed or is
high-entropy/random (encrypted data, already-compressed media) — there's no exploitable
redundancy left, and the compressor's own overhead can make output slightly larger than
the input.

## Key takeaways / mental model
Lossless compression exploits statistical structure, and there are two structurally
different kinds worth telling apart: **frequency skew** (Huffman coding, via a greedy
priority-queue-built trie giving common symbols shorter codes) and **substring
repetition** (LZW, via an on-the-fly dictionary built identically by encoder and
decoder, needing no upfront statistics). Real compressors like DEFLATE combine both,
because real data usually has both kinds of redundancy simultaneously — the
practical lesson is choosing (or combining) compression strategies to match the
redundancy actually present in the data, not defaulting to one algorithm universally.

## Self-check questions
1. Walk through building the Huffman trie for a small frequency table of your choosing
   and explain why every symbol ending up as a leaf (not an internal node) is what makes
   the resulting code prefix-free and unambiguous to decode.
2. Using the "ABABABA" example, explain concretely how the LZW decoder reconstructs the
   same dictionary as the encoder without ever receiving it explicitly.
3. Give a concrete example of data where Huffman coding would compress well but LZW
   would not, and vice versa.
4. Why does compressing already-compressed or encrypted data typically fail to shrink
   it further, and what does that imply about applying compression as a blanket default
   in a data pipeline?

## References
- Algorithms, 4th Edition (Robert Sedgewick, Kevin Wayne), Section 5.5 ("Data
  Compression").
