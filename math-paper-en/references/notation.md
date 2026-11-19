# Notation: symbols, macros, typesetting

Contents: [The two invariants](#the-two-invariants) · [The notation table](#the-notation-table)
· [Choosing letters](#choosing-letters) · [Confusable glyphs](#confusable-glyphs) ·
[Macro discipline](#macro-discipline) · [Symbols in sentences](#symbols-in-sentences) ·
[Displays](#displays) · [Subscript hygiene](#subscript-hygiene) ·
[Fixing a collision](#fixing-a-collision-late)

## The two invariants — and their scope

Uniqueness of meaning is a property of **free** terms. A bound (dummy) variable
lives inside its binder — the index of a $\sum$, the variable of an $\int$, the
$x$ of $\max_{x\in X}$ or of $\{x : P(x)\}$, the variable of a quantifier or a
$\mapsto$ — and reusing it elsewhere costs the reader nothing. The $i$ of
$\sum_{i=1}^{n}$ in §2 and the $i$ of $\sum_{i\in I}$ in §5 are different
variables, and nobody has ever been confused by that. Renaming the second one is
wasted effort.

**One symbol, one meaning — for every free symbol, across the whole paper.**
Not per section. A "in this section $h$ denotes a function" disclaimer is not a
fix; it is an admission. The cost of renaming is thirty minutes of your time;
the cost of not renaming is a fraction of your readers, who will stop rather
than page back.

**One meaning, one symbol** — same scope. Do not write $A_j$, $1\le j\le n$ in
one place and $A_k$, $1\le k\le n$ in another without a reason; that said, for
dummy indices this is a consistency preference, not an invariant. Fix index
conventions early ($i$ ranges to $m$, $j$ to $n$) and keep them because it makes
the paper easier to skim, not because ambiguity threatens.

Three things do go wrong, in decreasing order of severity:

1. **Free collision.** Two meanings on one free letter: $h$ the bandwidth and
   $h(t)$ the trajectory. Rename one.
2. **Shadowing.** A dummy variable reusing a letter that is free and in scope:
   $n$ is the dimension, and you write $\sum_{n=1}^{K}$. Legal, unreadable.
   Rename the dummy.
3. **A dummy escaping its binder.** The prose refers to $i$ after the sum that
   bound it has ended, or a statement quantifies over an index it never
   introduced. Usually a sign that the statement is not self-contained.

`scripts/audit.py` implements this distinction. It detects binders
($\sum,\prod,\int$ and friends, $\lim,\max,\min,\sup,\inf$, quantifiers,
set-builders, $\mapsto$, family subscripts $(\cdot)_{i\in I}$, differentials
$\,dx$, and prose binders such as "for all $i$"), excludes bound occurrences
from the collision check, and reports shadowing separately. Scope is
over-approximated to the enclosing formula, which is generous but errs toward
silence rather than noise.

## The notation table

Maintain it from the first line of drafting, in `sections/notation.tex` or as a
comment block in `macros.tex`:

| symbol | macro | meaning | type / domain | first use |
|---|---|---|---|---|
| $\mathcal{G}$ | `\Gr` | communication graph | undirected, $n$ vertices | §2.1 |
| $L$ | `\Lap` | graph Laplacian of $\Gr$ | $\mathbb{R}^{n\times n}$, PSD | (2.3) |
| $\lambda_2$ | `\lamtwo` | algebraic connectivity | $\ge 0$ | (2.4) |

Whether or not the table ships with the paper (it should, for anything over ~15
pages, as a "Notation" subsection), it is the artifact that keeps the invariants
true. Every new symbol goes in the table before it goes in the text.

## Choosing letters

Mnemonic families make a paper readable without the reader learning anything:

- functions: $f, g, \varphi, \psi, \zeta, \eta, \rho$ (letters with descenders)
- constants: $a, b, c, C, c_0$; keep a single convention for "constant that may
  change from line to line" and say so once
- variables: $x, y, z, u, v$
- integers and indices: $i, j, k, \ell, m, n$
- sets uppercase, elements lowercase; families script or calligraphic
- matrices uppercase Roman, vectors lowercase (state the convention; do not mix
  bold and arrow decorations)
- probability: $\mathbb{P}, \mathbb{E}$, random objects uppercase, realizations
  lowercase

Do not use a symbol's conventional meaning for something else: $\varepsilon$ small,
$\delta$ small, $\Sigma$ covariance or sum, $\nabla$ gradient, $\|\cdot\|$ a norm.
If your field owns a symbol, borrowing it costs the reader more than a new letter
does.

Terms of art may not be varied. If you define "nice graph", write "the graph is
nice", never "the niceness of the graph implies". Keep the defined form and use it
unchanged; readers pattern-match on exact strings.

## Confusable glyphs

Avoid or replace:

| Avoid | Reason | Use |
|---|---|---|
| `l` | reads as 1 | `\ell` |
| `\epsilon` | reads as `\in` | `\varepsilon` |
| `\emptyset` | reads as a computer zero | `\varnothing` |
| $\iota, \kappa, \upsilon, \omicron, \Xi$ | look like Latin letters or like noise | Latin letters |
| Fraktur $\mathfrak{G}$ vs $\mathfrak{S}$, $\mathfrak{F}$ vs $\mathfrak{T}$ | indistinguishable on a board | other alphabet, unless the field requires Fraktur |
| `*` for multiplication | programming notation | juxtaposition or `\times` |
| `p[r]` | programming notation | $p_r$ |

Reusing one letter in several fonts ($P$, $\mathcal{P}$, $\mathbb{P}$, $\mathbf{p}$)
is legitimate and often good — provided the fonts stay visually distinct and each
carries a stable role. Decide the roles once and record them in the table.

Hyphen, en-dash, minus and em-dash are four different characters: `-` in
compounds, `--` in ranges (lines 10--18), `-` inside math mode for minus, `---`
(sparingly) in prose.

## Macro discipline

Define a macro for every notation-bearing symbol, in `macros.tex`:

```latex
\newcommand{\Lap}{L}                 % graph Laplacian
\newcommand{\lamtwo}{\lambda_{2}}    % algebraic connectivity
\newcommand{\Rn}{\mathbb{R}^{n}}
\DeclareMathOperator*{\argmin}{arg\,min}
```

Payoffs: renaming a symbol paper-wide is a one-line edit; you can test whether a
letter is free by commenting out its macro and seeing whether the file still
compiles; and a reviewer can read the macro list as a notation index. Do not use
macros to hide structure (`\newcommand{\mainineq}{...}` for a whole display makes
the source unreadable).

Two families of macros are worth having globally: short aliases for Greek letters
you use constantly, and semantic operators via `\DeclareMathOperator` (never
`\text{tr}` inline, never $sin$ in italics).

## Symbols in sentences

1. **Never start a sentence with a symbol.** "The polynomial $x^n - a$ has $n$
   distinct roots", not "$x^n-a$ has ...".
2. **Never let two formulas touch.** Put a word between them.
   Bad: "Consider $S_q$, $q<p$." Good: "Consider $S_q$, where $q<p$."
3. **The blah test.** Replace every non-trivial formula by "blah" and read the
   paragraph aloud. If it no longer parses as English, the prose is leaning on the
   displays. Many readers skim formulas on first pass; the sentences must survive.
4. **Define before use**, or immediately after, and at least informally.
5. **Small numbers**: spell out as adjectives ("two passes"), keep as numerals as
   names ("Method 2", "the leftmost 2 in the sequence").
6. **Punctuate displays as parts of the sentence.** No colon before a display that
   completes the sentence grammatically:

   > We shall be especially interested in the nonincreasing vectors
   > $$A_n = \{(a_1,\dots,a_n)\in\mathbb{N}^n : a_1\ge\cdots\ge a_n\}.\qquad(1)$$

   A display ending a sentence takes a period.

## Displays

- Display a formula when it is referenced later, when it is the point of the
  paragraph, or when it does not fit comfortably inline. Otherwise inline it.
- Do not number every display; number the referenced and the important ones.
- Break long displays at logical points, before the relation symbol in a display
  (after it, in inline math).
- LaTeX spacing is not always right. `\Phi(2a+c)\Phi(c-2a)` reads as one strange
  operator; `\Phi(2a+c)\,\Phi(c-2a)` reads as a product. Look at the output.
- Prefer the slash form `(1+x)/y` to a stacked fraction inside exponents and
  subscripts, where stacked fractions shrink to illegibility.
- Never display a false equation; a reader's eye lands on displays and takes them
  as gospel. Put it inline and mark it: "the identity $\dots$ is *false* here".
- Ellipses: `x_1, \dots, x_n` at comma level, `x_1 + \cdots + x_n` at operator
  level. Commas before and after the dots in a list.
- Nested parentheses: keep them parentheses (brackets and braces carry meaning);
  better still, name the inner expression and remove the nesting.

## Subscript hygiene

The single most common source of unreadable mathematics is subscripts breeding.

- Do not index a set's elements unless you need the indices. "Let $X$ be a finite
  set" then talk about $x, y \in X$; a subset then needs no $x_{i_1},\dots$.
- Never subscript a subscript, and never subscript a superscript. If you have
  written $n^{\alpha_k}_j$, restructure the objects, not the typography.
- Name and conquer: `v = c + u(c_i - c_j + 1)` becomes `v = c + ku` with
  `k = c_i - c_j + 1` if $k$ is manipulated repeatedly.
- Keep relations in a consistent direction: after "$p=(p_1,\dots,p_n)$ and $i<j$",
  write $p_i < p_j$, not $p_j > p_i$.

## Fixing a collision late

When `audit.py` reports a collision, or you notice one:

1. Decide which occurrence keeps the letter — usually the one that appears most
   often, or the one whose meaning is conventional for that letter.
2. Choose a replacement from the free-letter set (compile-test by commenting out
   the candidate's macro if it has one).
3. If the losing symbol has a macro, the change is one line. If not, add a macro
   first, replace occurrences mechanically, then edit the definition.
4. Re-read every sentence that mentions the renamed object: prose often encodes
   the old letter ("the map $h$" becomes "the bandwidth $h$" — the noun changes
   too).
5. Re-run the audit; check the notation table.

A rewrite pass must never touch, character for character: math mode, `verbatim`,
`\texttt`, identifiers and paths, `\label`/`\ref`/`\cite` keys, or numbers and
units inside `siunitx`. If a style edit changes any of those, it is a bug.
