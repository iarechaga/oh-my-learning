# Software Quality

Testing and reliability are about creating fast feedback loops that let you change code
with confidence. This domain focuses on writing tests that catch meaningful failures,
stay readable, and resist churn as the design evolves. The goal is not more tests, but
more trustworthy systems through better test design and strategy.

Concept IDs are subject-scoped (e.g. `goos/07`), so this `software-quality/` folder organizes files on disk without changing how you refer to a concept.

## Subjects

| Subject | What it is | Lessons | Index |
| --- | --- | --- | --- |
| **GOOS** | *Growing Object-Oriented Software, Guided by Tests* (Freeman & Pryce) - outside-in TDD, walking skeletons, mock objects, and design-through-tests at system level. | 12 | [goos/README.md](goos/README.md) |
| **Unit Testing** | *Unit Testing: Principles, Practices, and Patterns* (Khorikov) - valuable vs brittle tests, four pillars, doubles, and practical test strategy. | 13 | [unit-testing/README.md](unit-testing/README.md) |
| **xUnit Test Patterns** | *xUnit Test Patterns: Refactoring Test Code* (Meszaros) - the canonical catalog of test smells, test patterns, and test-code refactorings. | 12 | [xunit-test-patterns/README.md](xunit-test-patterns/README.md) |

A sensible path: start with Unit Testing for core quality criteria, use GOOS to learn
design-through-tests across slices, then use xUnit Test Patterns as your long-term
maintenance and smell-reference guide.

See each subject's `README.md` for its concept index and progress, and the root
[SUMMARY.md](../SUMMARY.md) for the cross-domain overview.
