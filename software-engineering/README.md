# Software Engineering

The software-engineering **domain** of this learning repository. It groups the
book-subjects that teach how to write maintainable, evolvable software - the craft and
discipline of code itself, as distinct from the system-level design covered in the
[architecture](../architecture/README.md) domain.

Concept IDs are subject-scoped (e.g. `clean-code/03`, `refactoring/07`), so this
`software-engineering/` folder organizes files on disk without changing how you refer to
a concept.

## Subjects

| Subject | What it is | Lessons | Index |
| --- | --- | --- | --- |
| **The Pragmatic Programmer** | *The Pragmatic Programmer*, 20th Anniversary ed. (Hunt & Thomas) - the pragmatic philosophy and everyday habits of effective developers: DRY, orthogonality, tracer bullets, decoupling, and pragmatic tooling. | 15 | [pragmatic-programmer/README.md](pragmatic-programmer/README.md) |
| **Code Complete** | *Code Complete*, 2nd ed. (McConnell) - construction-level craftsmanship: defensive programming, variables and routines, class design, and taming complexity in the small. | 14 | [code-complete/README.md](code-complete/README.md) |
| **Clean Architecture** | *Clean Architecture* (Martin) - SOLID, component principles, and the dependency rule that keeps business rules independent of frameworks, UI, and databases. | 13 | [clean-architecture/README.md](clean-architecture/README.md) |
| **Clean Code** | *Clean Code* (Martin) - writing readable code in the small: naming, functions, comments, formatting, error handling, and code smells. | 12 | [clean-code/README.md](clean-code/README.md) |
| **Refactoring** | *Refactoring*, 2nd ed. (Fowler) - improving the design of existing code safely: code smells and a catalog of named refactorings backed by tests. | 12 | [refactoring/README.md](refactoring/README.md) |
| **A Philosophy of Software Design** | *A Philosophy of Software Design* (Ousterhout) - complexity as the enemy, deep modules, information hiding, and designing for the long term. | 11 | [philosophy-of-software-design/README.md](philosophy-of-software-design/README.md) |
| **Working Effectively with Legacy Code** | *Working Effectively with Legacy Code* (Feathers) - getting untested code under test: seams, dependency-breaking techniques, and characterization tests. | 12 | [legacy-code/README.md](legacy-code/README.md) |
| **Enterprise Application Patterns** | *Patterns of Enterprise Application Architecture* (Fowler) - the enterprise pattern catalog: domain logic, data source and mapping (ORM), concurrency, sessions, and distribution patterns. | 14 | [enterprise-patterns/README.md](enterprise-patterns/README.md) |
| **Design Patterns** | *Design Patterns* (Gamma, Helm, Johnson, Vlissides - the "Gang of Four") - the classic 23 object-oriented patterns grouped as creational, structural, and behavioral. | 11 | [design-patterns/README.md](design-patterns/README.md) |

A sensible path: start with the philosophy and everyday craft (The Pragmatic Programmer,
Clean Code, Code Complete), learn to see and name design forces (Design Patterns, A
Philosophy of Software Design), then apply them to change existing systems safely
(Refactoring, Working Effectively with Legacy Code) and structure larger applications
(Clean Architecture, Patterns of Enterprise Application Architecture).

See each subject's `README.md` for its concept index and progress, and the root
[SUMMARY.md](../SUMMARY.md) for the cross-domain overview.
