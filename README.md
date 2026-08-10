# Oh My Learning - Lessons + Socratic Discussion

[![Sponsor](https://img.shields.io/badge/Sponsor-%E2%9D%A4-db61a2?logo=githubsponsors&logoColor=white)](https://github.com/sponsors/iarechaga)

If this learning library is useful to you, consider [sponsoring its
upkeep](https://github.com/sponsors/iarechaga). Thank you!

An AI coding agent writes a deep, self-contained **lesson** for each concept; you read
it on your own; then you ask the agent to **discuss** it with you. The discussion is
Socratic - questions instead of lectures - and finds the gaps in your understanding
before you find them in an interview or a production incident.

**609 lessons, 45 subjects, 8 domains**, from architecture and distributed systems to
DDD, testing, DevOps/SRE, and technical leadership. This is not a code project - there
is nothing to build or run. The "program" is the loop of *read, then get grilled on it
until you actually understand it.*

> Driven by an AI agent. Lesson authoring, discussions, and progress tracking are all
> performed by an AI coding agent (such as [OpenCode](https://opencode.ai) or Claude
> Code) that reads [`AGENTS.md`](AGENTS.md). Without an agent you can still read the
> lessons as standalone notes, but the interactive part needs one.

---

## Cómo empezar (2 minutos)

1. **Fork o clona el repo**, y ábrelo con un agente de código que lea `AGENTS.md`
   (OpenCode, Claude Code, o similar).
2. **Dile que quieres empezar a aprender.** El agente te pone en tu propia rama, no en
   `main` (`main` es la biblioteca compartida; tu aprendizaje es personal - tu progreso,
   tus notas). No necesitas ejecutar comandos de git: en tu primera sesión el agente
   crea y cambia a una rama `learn/<tu-nombre>` por ti.
3. **El agente te conoce primero.** Te pregunta tu nombre, tu nivel de seniority
   (te ayuda a estimarlo si no lo tienes claro) y qué quieres aprender y por qué. Con
   eso, te propone un **track de estudio ordenado**: una lista concreta de conceptos, en
   el orden correcto, con el motivo de cada uno - no una lección al azar.
4. **Lee una lección** y pídele al agente que la discuta contigo: *"discute
   `system-design/03`"*. Una pregunta cada vez, pistas en vez de respuestas, al menos un
   escenario aplicado, y un veredicto de dominio (`solid` / `partial` / `shaky` /
   `not-yet`) al final.
5. **El agente lleva tu progreso por ti**, en `PROGRESS.md` en la raíz de tu rama: qué
   sigue (*Next up*), dónde flojeas (*Focus areas*), y estadísticas por dominio y
   seniority. Pregúntale en cualquier momento *"¿qué sigo?"*, *"¿cómo voy?"* o *"quiero
   más foco en bases de datos"* - te responde al momento, sin tener que repasar el repo
   entero, y ajusta el track si se lo pides.

No necesitas los libros originales: cada lección enseña el concepto desde cero, con
ejemplos trabajados, trade-offs y preguntas de autoevaluación. El libro citado es solo
un "profundiza más" opcional.

---

## Dominios de un vistazo

| Dominio | De qué trata | Subjects | Lecciones |
| --- | --- | --- | --- |
| **[Architecture](architecture/README.md)** | Diseño de sistemas escalables, mantenibles y distribuidos - de la teoría (DDIA) a la práctica (System Design, microservicios, arquitecturas evolutivas). | 10 | 152 |
| **[Software Engineering](software-engineering/README.md)** | Escribir código mantenible y evolutivo: pragmatismo, Clean Code/Architecture, refactoring, patrones. | 9 | 114 |
| **[Technical Leadership](technical-leadership/README.md)** | Crecer más allá de programar: liderazgo IC staff-plus, management, delivery science, toma de decisiones. | 7 | 89 |
| **[CS Fundamentals](cs-fundamentals/README.md)** | Algoritmos, estructuras de datos y concurrencia - la base formal. | 5 | 74 |
| **[DevOps, Cloud & Reliability](devops-reliability/README.md)** | Operar software en producción: flujo, feedback, y SRE (SLOs, error budgets, incidentes). | 4 | 54 |
| **[Domain Modeling](domain-modeling/README.md)** | Modelar complejidad de negocio con Domain-Driven Design. | 4 | 54 |
| **[Data Engineering & Databases](data-engineering/README.md)** | Elegir, diseñar y entender sistemas de almacenamiento. | 3 | 35 |
| **[Software Quality](software-quality/README.md)** | Testing y fiabilidad a través de mejor diseño de tests. | 3 | 37 |

**-> [Mira las 609 lecciones: CATALOG.md](CATALOG.md)** - el catálogo completo,
dominio -> subject -> lección, con seniority y enlace directo a cada una. Se genera
programáticamente desde el front matter de las lecciones (ver
[scripts/generate_catalog.py](scripts/generate_catalog.py)), así que nunca se
desincroniza a mano.

---

## Otras formas de leer

Además de leer el Markdown directamente en GitHub o en tu editor, hay una web estática
local con navegación, badges de seniority y estado de lectura:

```bash
pip3 install -r website/requirements.txt
python3 website/build.py
python3 website/serve.py
```

Abre `http://localhost:8000`. Se reconstruye a partir de los mismos ficheros de
lección; ver [`agent-docs/website.md`](agent-docs/website.md) para el detalle.

---

## Para quien quiere contribuir o entender los internals

El modelo del repositorio en corto: los **subjects** (un libro cada uno) se agrupan por
**domain**; cada subject tiene una lección por concepto, identificada por un ID estable
`<subject>/<NN>` (p.ej. `ddia/07`). Cada lección lleva `status` (`drafted` ->
`discussed`), `mastery` (`solid`/`partial`/`shaky`/`not-yet`, personal y por rama) y
`seniority` (`junior`/`mid`/`senior`/`staff`/`principal`, qué puesto ancla el concepto -
ver [SENIORITY.md](SENIORITY.md)).

- **El modelo completo del repositorio**, con el árbol de carpetas y las reglas de IDs,
  está en [`CONTRIBUTING.md`](CONTRIBUTING.md#repository-model-in-one-screen).
- **Cómo contribuir** (nueva lección, subject o domain; o pedirlo por Issues) está en
  [`CONTRIBUTING.md`](CONTRIBUTING.md).
- **El contrato del agente** - la plantilla de lección, el protocolo de discusión
  socrática, el sistema de progreso (`PROGRESS.md`), y todas las reglas de
  verificación - vive en [`AGENTS.md`](AGENTS.md) y su detalle en `agent-docs/`.

---

## License & attribution

The lessons in this repository are **original explanations written from first
principles**. Each lesson cites the source book it draws its concepts from, but the
prose, structure, worked examples, and diagrams are the author's own - the books are a
source and an optional "go deeper", never reproduced here.

This work is licensed under the **Creative Commons Attribution-ShareAlike 4.0
International License** ([CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/));
the full text is in [`LICENSE`](LICENSE). In short: you may share and adapt the material,
even commercially, as long as you **give appropriate credit** and **license your
derivatives under the same terms**.

Cited book titles and author names are referenced for attribution only and remain the
property of their respective rights holders; they are not covered by this license.
