# A Philosophy of Software Design

The complexity-management layer of the software-engineering track: a compact,
opinionated theory of design centered on one enemy - complexity - and the techniques
that fight it: deep modules, information hiding, pulling complexity downward, and
designing interfaces that are simpler than their implementations. It often argues the
*opposite* of Clean Code on specifics (e.g. function length), which makes it a valuable
counterpoint to hold in tension.

**Source book:** *A Philosophy of Software Design* (2nd edition) - John Ousterhout
(Yaknyam Press, 2021).

**How to use this subject:** read a lesson on your own, then ask to *discuss
`philosophy-of-software-design/<NN>`* (e.g. *"discuss `philosophy-of-software-design/03`"*).
Ordered by dependency: the nature of complexity first, then the module/interface
techniques, then comments, naming, and design tensions.

**Seniority baseline:** senior (lessons range mid->senior).

## Concepts

| ID  | Concept | Seniority | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | --------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | Complexity is the enemy: symptoms and causes | mid | drafted | — | — | [lesson](lessons/01-complexity-is-the-enemy.md) | — |
| 02  | Working code is not enough (strategic vs tactical) | senior | drafted | — | — | [lesson](lessons/02-strategic-vs-tactical.md) | — |
| 03  | Modules should be deep | senior | drafted | — | — | [lesson](lessons/03-deep-modules.md) | — |
| 04  | Information hiding and leakage | senior | drafted | — | — | [lesson](lessons/04-information-hiding.md) | — |
| 05  | General-purpose modules are deeper | senior | drafted | — | — | [lesson](lessons/05-general-purpose-modules.md) | — |
| 06  | Pulling complexity downward | senior | drafted | — | — | [lesson](lessons/06-pulling-complexity-downward.md) | — |
| 07  | Different layer, different abstraction | senior | drafted | — | — | [lesson](lessons/07-different-layer-different-abstraction.md) | — |
| 08  | Define errors (and special cases) out of existence | senior | drafted | — | — | [lesson](lessons/08-define-errors-out-of-existence.md) | — |
| 09  | Comments describe things the code cannot | mid | drafted | — | — | [lesson](lessons/09-comments.md) | — |
| 10  | Choosing names and consistency | mid | drafted | — | — | [lesson](lessons/10-naming-consistency.md) | — |
| 11  | Design tensions and when principles conflict | senior | drafted | — | — | [lesson](lessons/11-design-tensions.md) | — |

**Status:** `drafted` (lesson written) · `discussed` (at least one discussion held).
**Mastery:** `solid` · `partial` · `shaky` · `not-yet` - set from the most recent
discussion's verdict; empty until first discussed.
**Cross-subject prerequisites** (e.g. `clean-code/03`) are listed per lesson in its front
matter and named in prose; several lessons deliberately contrast with Clean Code.
