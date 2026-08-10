# A Philosophy of Software Design - Subject Summary

A comprehensive recap of *A Philosophy of Software Design*, 2nd ed. (John Ousterhout),
concept by concept.

**Progress note:** all 11 lessons are `drafted`; none have been discussed yet, so
mastery is pending across the board and no weak spots are recorded. This summary will
gain depth (especially on the concepts you find hard) as discussions happen - the
"Focus areas" section at the bottom will fill in from discussion records. Several
lessons deliberately contrast with Clean Code (e.g. function-length guidance) - worth
holding both in tension rather than picking a "winner."

See the progress table in [README.md](README.md). Reading order is top to bottom: the
nature of complexity first, then the module/interface techniques, then comments,
naming, and design tensions.

## The nature of complexity

- **[philosophy-of-software-design/01] Complexity is the enemy: symptoms and causes** -
  complexity = anything structural that makes a system harder to understand and
  modify. Three symptoms (change amplification, cognitive load, unknown unknowns), two
  causes (dependencies, obscurity). ([lesson](lessons/01-complexity-is-the-enemy.md))
- **[philosophy-of-software-design/02] Working code is not enough (strategic vs
  tactical)** - strategic design investment pays back within months, not years;
  "tactical tornadoes" look individually fast but are collectively expensive.
  ([lesson](lessons/02-strategic-vs-tactical.md))

## Module and interface design

- **[philosophy-of-software-design/03] Modules should be deep** - a module's value is
  functionality-to-interface ratio; deliberately contrasts Clean Code's function-length
  guidance - splitting can shallow a module, not just shorten it.
  ([lesson](lessons/03-deep-modules.md))
- **[philosophy-of-software-design/04] Information hiding and leakage** - leakage is
  when one design decision is reflected in more than one module's interface, even with
  no exposed fields; temporal decomposition is a common cause.
  ([lesson](lessons/04-information-hiding.md))
- **[philosophy-of-software-design/05] General-purpose modules are deeper** - design
  around the actual underlying functionality, not one caller's specific framing - but
  stop short of speculative, imagined-future generality.
  ([lesson](lessons/05-general-purpose-modules.md))
- **[philosophy-of-software-design/06] Pulling complexity downward** - unavoidable
  complexity is usually better absorbed once by an implementer than handled repeatedly
  by every caller; scrutinize every required config parameter.
  ([lesson](lessons/06-pulling-complexity-downward.md))
- **[philosophy-of-software-design/07] Different layer, different abstraction** -
  pass-through methods and trivial decorators are a specific, checkable smell: a layer
  should represent a genuinely different abstraction, not just relay calls.
  ([lesson](lessons/07-different-layer-different-abstraction.md))
- **[philosophy-of-software-design/08] Define errors (and special cases) out of
  existence** - before handling an error well, ask whether redefining the operation's
  semantics (idempotency, clamping) removes the special case entirely.
  ([lesson](lessons/08-define-errors-out-of-existence.md))

## Comments, naming, and synthesis

- **[philosophy-of-software-design/09] Comments describe things the code cannot** -
  comments capture exactly what information hiding deliberately hides; a more
  comment-friendly stance than Clean Code, distinguishing interface vs. implementation
  comments. ([lesson](lessons/09-comments.md))
- **[philosophy-of-software-design/10] Choosing names and consistency** - struggling to
  name something well is diagnostic of a design problem, not just a vocabulary gap;
  codebase-wide consistency is nearly as valuable as any single name's cleverness.
  ([lesson](lessons/10-naming-consistency.md))
- **[philosophy-of-software-design/11] Design tensions and when principles conflict** -
  nearly every principle in this subject has situations where it conflicts with
  another; the skill is recognizing the tension and judging the trade-off explicitly.
  ([lesson](lessons/11-design-tensions.md))

## Focus areas (aggregated weak spots)

None yet - discussions have not started for this subject.
