# Computer Science Fundamentals

This domain covers the core computer science layer behind effective software work:
algorithm analysis, data structures, algorithm design paradigms, and concurrency
correctness. It combines both theory-heavy references and implementation-oriented texts
so you can move from first principles to practical engineering judgment.

Concept IDs are subject-scoped (e.g. `clrs/07`), so this `cs-fundamentals/` folder organizes files on disk without changing how you refer to a concept.

## Subjects

| Subject | What it is | Lessons | Index |
| --- | --- | --- | --- |
| **CLRS** | *Introduction to Algorithms* (Cormen, Leiserson, Rivest, Stein) - the comprehensive algorithms reference across analysis, data structures, graph algorithms, flow, and complexity. | 20 | [clrs/README.md](clrs/README.md) |
| **Algorithms (Sedgewick and Wayne)** | *Algorithms* (Sedgewick, Wayne) - practical, implementation-focused treatment of core algorithms and data structures. | 14 | [algorithms-sedgewick/README.md](algorithms-sedgewick/README.md) |
| **Algorithm Design** | *Algorithm Design* (Kleinberg, Tardos) - design techniques and proof patterns: greedy, divide and conquer, dynamic programming, flow, and NP-completeness. | 12 | [algorithm-design/README.md](algorithm-design/README.md) |
| **Java Concurrency in Practice** | *Java Concurrency in Practice* (Goetz et al.) - the definitive JVM guide to thread safety, memory model semantics, and concurrent component design. | 15 | [java-concurrency/README.md](java-concurrency/README.md) |
| **The Art of Multiprocessor Programming** | *The Art of Multiprocessor Programming* (Herlihy, Shavit) - deep concurrent algorithm theory and lock-free or wait-free data structures. | 13 | [multiprocessor-programming/README.md](multiprocessor-programming/README.md) |

A sensible path is algorithms first (CLRS, Sedgewick/Wayne, then Kleinberg/Tardos),
followed by concurrency (Goetz, then Herlihy/Shavit) once sequential reasoning is solid.

See each subject's `README.md` for its concept index and progress, and the root
[SUMMARY.md](../SUMMARY.md) for the cross-domain overview.
