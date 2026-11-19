# Structure: what each part of the paper is for

Contents: [Reading orders](#reading-orders) · [Title](#title) · [Abstract](#abstract) ·
[Introduction](#introduction) · [Preliminaries](#preliminaries) ·
[Theorem statements](#stating-a-theorem) · [Proofs](#writing-a-proof) ·
[Numerical sections](#numerical-and-experimental-sections) ·
[Final remarks](#final-remarks) · [Acknowledgements and references](#acknowledgements)
· [Venue variations](#venue-variations)

## Reading orders

Design for the fact that almost nobody reads front to back. Real readers do one of:
title only; title + abstract; abstract + main theorem, then stop; introduction
only; straight to the main theorem, then backwards for definitions; the proof of
one lemma, found by search. The structure below serves all of these at once. The
practical consequences: the main theorem must be findable in seconds, statements
must be self-contained, and every section must be enterable from the outside.

## Title

The first approximation to the contents, not a slogan. Match the title's shape to
what was actually done:

- full result → "Every X is Y"
- partial result → "On Y for X", "New examples of Y"
- new proof of a known result → "A short proof that every X is Y"
- refutation → "Not every X is Y"
- incremental note → "A remark on Y"
- survey → "Y: a survey" (say so explicitly; readers need the genre)

Avoid vague generics ("On some problems in ..."), avoid symbols in the title where
words will do (they break indexing and citation tools), avoid noun stacks
("distributed consensus network protocol convergence rate problem"). If the paper
introduces a class of objects, naming it in the title gives readers something to
remember and repeat.

Check the title for ambiguity by reading it as a stranger would: "Optimal Font
Caching" can be caching of optimal fonts. Reorder or add a word.

## Abstract

The easiest section, and the one most often overinflated. It is a dry summary of
results, close in spirit to a MathSciNet entry.

- State the key result first; mention the existence of the others briefly.
- Give the setting in one clause, not a paragraph of motivation.
- No proofs, no notation the reader has not met, no "in this paper we will".
- Citations only if genuinely more precise than a paraphrase (e.g. disproving a
  specific conjecture); many venues forbid them outright.
- Length ≈ 0.3–0.5 lines per page of paper. Ten lines for a ten-page note is too
  much.
- It must not claim more than the theorems prove. Cross-check the abstract against
  the claim ledger line by line; this is the most common referee complaint.

Shape that works: *setting in one sentence → the question → the main theorem in
words → the sharpest secondary result → what the method also gives.*

## Introduction

The hardest section, and for most readers the only one. Write a rough version
first so you know what the paper is, then rewrite it completely once the body
exists — the paper always ends up different from the plan.

**Opening.** The first sentence is the best sentence in the paper. Do not open
with "Let $G=(V,E)$ be a graph." and do not open with "An X is a Y" ("An important
method for internal sorting is quicksort" → "Quicksort is an important method for
internal sorting, because ..."). Open with the object, the question, or the
tension. One or two paragraphs of genuine, non-generic motivation are permitted
here and nowhere else; use them.

**Body of the introduction.** Set up the problem, then state the main results.
Aim for the first theorem on page 1, page 2 at the worst. If the main theorem is
too technical to state early, state an easy nontrivial corollary instead and
forward-reference the general version — that corollary is what readers will
remember and repeat to other people.

**History.** Only the history that bears directly on the main result. Do not
attempt to credit everyone here; that belongs in final remarks. The compact form
that works:

> [A] asked whether XYZ and proved the weak form. [B] showed that the strong form
> fails. We refine the argument of [B] to show that XYZ fails as well, and we
> conjecture that the weak form is best possible.

**Contributions.** If the venue expects an explicit list, keep it to three or four
items, each a claim the body defends, each mapped to a section. Do not pad it with
"we conduct extensive experiments". If the venue does not expect one, prose is
better than a bulleted list.

**Last paragraph.** Outline the paper's organization in your own words, one
sentence per section, with what the reader gets from each — not "Section 3
contains the proofs."

**Foreword.** If the introduction still runs past four pages, split off a short
untitled first subsection for the big picture, motivating examples, and connections
to other fields. Keep it under a page.

## Paragraphs: context, content, conclusion

Sections are not the smallest unit that needs designing. Mensh & Kording (*Ten
simple rules for structuring papers*, PLoS Comput. Biol. 13(9), 2017) give the
template that works at every scale, and it is worth applying literally:

> **context** — what the reader needs in order to care about what follows;
> **content** — the substance, one idea;
> **conclusion** — what it means, and the hook into the next unit.

At paragraph scale this is three to six sentences: the first sentence says which
idea this paragraph is about, the middle carries it, the last says what follows
from it. At section scale it is the opening paragraph, the body, and the
transition. At paper scale it is the introduction, the results, and the
discussion.

Two consequences worth stating separately:

- **One central contribution per paper.** A paper defending two unrelated claims
  is remembered for neither. If the second claim is good, it is a second paper;
  if it is not, it is a remark in §7.
- **The last sentence of a paragraph is the one that is remembered.** Put the
  load there, not in a summarising clause you were tempted to add afterwards.

The failure this template prevents is the paragraph that opens mid-argument,
carries three ideas, and ends on the weakest one — which is what unedited
drafting produces by default.

## Preliminaries

Only what is used. A preliminaries section that recites a standard course is a
signal of padding. Each definition should be reachable from the index of notation,
and each should be stated twice — formally, and in one informal clause — when the
object is not standard.

Order definitions so that proofs can follow the same order later. Put the
assumption list (A1), (A2), ... here, each with one sentence on what it buys and
whether it is known to be necessary.

## Stating a theorem

- **Self-contained.** The statement must survive being read alone, out of context.
  If it needs hypotheses, name them or restate them.
- Never begin a statement with a symbol.
- The sentence before a theorem environment is a complete sentence and should
  motivate, not announce. Bad: "We now have the following". Good: "The same
  argument gives a bound that does not depend on the dimension." then the theorem.
- Capitalize named results: Theorem 1, Lemma 2.3, Algorithm 4.
- Number displayed formulas only when referenced, plus the few that are important
  enough that a reader may want to cite them.
- If a theorem is long, factor it: put the technical core in a proposition and
  state the clean consequence as the theorem.

## Writing a proof

Structure every nontrivial proof as **sketch, then detail**:

> *Proof.* The argument has three steps. (i) We show the iterates stay in a
> compact set. (ii) On that set the map is a contraction in the metric $d$. (iii)
> A fixed-point argument then gives the claim, and step (ii) gives the rate.
>
> *Step (i).* ...

The sketch is not decoration; it is what lets a reader verify the architecture
without reading every line, and what lets them find the step they doubt.

Rules inside a proof:

- Tie the formulas together with running commentary. A bare chain of displays is
  homework, not exposition. The prose between displays should say *why* the next
  line follows, not restate it.
- Prefer a direct argument to contradiction when both are available; contradiction
  proofs hide where the hypotheses are used and are harder to reuse.
- Say what is being proved and by what strategy before doing it: "We prove the
  second inequality by contradiction." "It suffices to bound the first term."
- Signpost long proofs: "The lemma is half proved." "It remains to handle the case
  $k=0$."
- State where each hypothesis is used. A hypothesis never used is either a defect
  or a chance to strengthen the theorem — check which.
- Do not use `⇒`, `∀`, `∃`, `∴` as prose abbreviations outside logic papers; write
  the words.
- End with the standard box; keep a space before it.
- If the proof is long, close with a one-sentence recap of what was established,
  in the notation of the statement.

## Numerical and experimental sections

- Organize by the question answered, not by the chronology of what was run.
- State the setup so it is reproducible: dimensions, distributions, seeds,
  solver/tolerance, hardware if timings matter. What "reproducible" costs in
  practice, and how to keep a campaign's settings from drifting between tables,
  is in `experiments.md` — read it before the production runs, not after.
- Every figure and table needs a sentence in the text saying what to look at and
  what it shows. Figures small and numerous beats large and few. Plot choice,
  colour, sizing and caption contents are in `figures.md`.
- Every measured number carries an uncertainty and an $n$, every comparison
  claim carries an exact $p$-value and an effect size, and bold in a table means
  "not distinguishable from the best", with the rule stated in the caption. The
  details are in `numerics.md`; do not write this section without reading it.
- Report the negative results and the regimes where the method loses. Boundaries
  are what make the positive claims credible.
- Never present numerical evidence in language reserved for proof ("we show",
  "it follows"). Use "the experiments indicate", "consistent with".

## Final remarks

Treat this section as endnotes, not as a dumping ground. Untitled numbered
subsections, one to three paragraphs each, ordered by decreasing importance. It is
the right home for:

- extended history and full credit to related work, one paper at a time with what
  each contributed — never "see [2–19] for related work";
- what the method does not do, and why — this is the designated home for the
  paper's defensive material, and collecting it here is what lets the body read
  as a positive argument (`prose.md`, "Defensive density");
- open problems: yours first, then other people's;
- speculative connections you do not want to lose.

Insert forward pointers from the body ("for more on this, see §7.3") as you write,
so the reader can defer.

## Acknowledgements

Short, unnumbered, before the references. Name people individually for
conversations; single out specific contributions with what they were ("who pointed
out the counterexample in §5"); then institutions and funding. Ask permission
before attributing an unpublished idea or conjecture to someone.

Do not add author names, affiliations, or funding lines that were not supplied.
Getting an affiliation wrong is worse than leaving it blank.

## References

The citation grammar — what "see [X]" means as opposed to "[X] proved" — matters
and is covered in `evidence.md`. Formatting rules:

- Pick one style and enforce it: consistent name spelling (one form per person),
  abbreviated first names, no journal series bloat.
- Alphanumeric keys (`[Kra96]`, `[SY09]`, `[A+13]` for five or more authors) help
  the reader more than numbers in a long paper; numeric is fine in short notes and
  is often mandated by the venue.
- Cite a specific location for any result quoted from a work longer than a few
  pages, and prefer *section* numbers over page numbers (`[A, §3.1]`) — page
  numbers differ between arXiv and journal versions.
- Include arXiv ids for unpublished work; make links clickable.
- Entries are exported from an authoritative record and then normalised, never
  hand-written; see `bibliography.md` for the sources and the tooling.
- Where citations go: the most relevant in the introduction, the precise ones at
  the point of use when a result is used as a lemma, the full context in final
  remarks. Avoid citation clumps in the middle of a proof; they break the argument.

## Venue variations

- **Math journals** — as above; final remarks carry the history and open problems.
- **CS theory / ML conferences** — the introduction absorbs the related work that a
  math paper would defer, contributions are usually an explicit list, and a
  "Conclusion" replaces "Final remarks" and is expected to be short. Proofs often
  move to an appendix; the body then needs a proof sketch that is genuinely
  self-standing.
- **IEEE control/signal journals** — Roman-numeral sections, "Notation" as its own
  early subsection, assumptions numbered and referenced throughout, a simulation
  section that is expected rather than optional, and a short conclusion. Lemma
  numbering is usually flat within the paper.
- **Extended abstract / short note** — one result, one proof, no preliminaries
  section; put definitions inline at first use.

## Fitting a hard page limit

What the limit counts differs by venue, and getting it wrong costs a page in
either direction. IEEE letters and many control conferences (L-CSS, CDC) count
the bibliography inside the limit and allow an appendix past it; the large
machine-learning conferences do the reverse, excluding references and appendix
from the count in the same PDF; physics letters (PRL) and some general-science
journals are limited by words or by a typeset-length estimate, where a page
count is not the binding quantity at all. Read the call, then apply two rules.

**Measure at the boundary, not by a landmark.** "The references start on page 6"
is not the same as "the references end on page 6": an entry can start on the
last allowed page and spill onto the next, which is a violation the landmark
check passes. Measure what is actually at the seam:

```bash
pdftotext -f 6 -l 6 main.pdf - | tail -2     # must end with the last counted line
pdftotext -f 7 -l 7 main.pdf - | head -2     # must begin the excluded material
```

`scripts/pagegate.py main.pdf --limit 6` performs exactly this and exits
non-zero when the limit is exceeded, so it can sit in a Makefile. Tell it what
the venue excludes: `--after APPENDIX` where the bibliography is counted,
`--after REFERENCES,APPENDIX` where it is not.

Re-run it after every build; a two-line insertion anywhere in the body moves the
seam. Under a word limit the same discipline applies to a different quantity:
count with `texcount` or the publisher's own estimator, not by eye.

**A length pass is a claim pass.** Cutting words changes what sentences assert —
a dropped qualifier is the cheapest way to publish something false. After
trimming, re-read each touched sentence against the table or figure it
summarises. Cut in this order: roadmap paragraphs that announce what the next
section will do, prose that restates a display, duplicated setup between
sections, and an aside whose absence no reader would notice. Do not buy space by
deleting a hypothesis, an uncertainty, or the scope of a claim.
