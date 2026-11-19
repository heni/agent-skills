---
name: math-paper-en
description: Write, restructure, translate, polish, or audit research papers in mathematics and mathematical engineering in English LaTeX — theorem/proof papers, journal and conference submissions, arXiv preprints, extended abstracts. Use this skill whenever the user asks to draft or rewrite a paper, an abstract, an introduction, a theorem statement or a proof in English; to translate a Russian draft into English; to make prose read like a working mathematician wrote it rather than a language model; to check notation for collisions; to verify that citations and named terms are real and used correctly; or to run a pre-submission audit. Use it equally for the measurement side of such a paper: reporting error bars and confidence intervals, choosing how many seeds, trials or instances to run, describing an experimental setup so it can be rebuilt, comparing methods fairly, tables and figures of results, making a run reproducible, and fitting a hard page limit or word limit. Use it even when the request sounds small ("fix my abstract", "reword this lemma", "does this sound AI-written?", "my error bars are undefined", "how many seeds do I need?") — the same notation, evidence, and prose rules apply to fragments.
---

# Writing a mathematical paper in English

The goal is a paper that a referee reads without friction and a specialist trusts:
every symbol means one thing, every claim has visible support, every citation is
real, and the English sounds like a mathematician wrote it in one sitting after
thinking hard — not like a template being filled in.

Five properties are being optimized simultaneously. They pull against each other,
so the order below matters.

1. **Correct and complete.** No claim without support; no proof step that skips
   what the reader cannot reconstruct. Completeness beats elegance.
2. **Conventional structure.** A reader should be able to find the main theorem in
   under a minute and read the paper in any of the four or five orders that real
   readers actually use.
3. **Natural flow.** Prose carries the argument between the displays; the reader is
   told where they are going and why.
4. **Not machine-flavored.** No LLM vocabulary, no uniform sentence rhythm, no
   bullet-list thinking, no throat-clearing.
5. **Disciplined symbols, terms and references.** One meaning per symbol, no
   invented terminology, no invented or decorative citations.

## Non-negotiables

- **Never invent a reference.** No author, title, venue, year, theorem number, or
  arXiv id goes into the file unless it was verified against a real record in this
  session, or supplied by the user. If a reference is needed and unverified, write
  `\todo{REF: <what is needed>}` and tell the user. A plausible-looking fake
  citation is the single most damaging thing this skill can produce.
- **Never invent terminology.** Every technical term is either standard in the
  field (and traceable to a source), or introduced by an explicit definition in
  this paper. No new name for an existing object.
- **Never state a result the user has not established.** If a gap is found while
  writing, surface it; do not paper over it with "it can be shown that".
- **Never fake naturalness by tampering.** No homoglyphs, zero-width characters,
  deliberate typos, or invisible Unicode. These corrupt LaTeX, are trivially
  detectable, and are dishonest. Naturalness comes from writing well.
- **Disclose by provenance, not by tool presence.** Prose and formatting under
  an author who owns the science is instrumental; experiments, data cleaning,
  algorithm choice and proof steps are contributory and get declared. Venue
  policy wins on compliance; when in doubt, disclose. See `disclosure.md`.
- **Detection is not the target; quality is.** Detectors are unreliable in both
  directions and no rule set guarantees a score. Say so plainly if the user asks
  for a guarantee. What the rules below do deliver is prose without the tells that
  make a reader (or a tool) suspect a machine.

## Workflow

Do not skip to prose. Steps 1–4 are cheap and prevent the expensive failures.
Step 6 applies only to papers that report measurements, and a paper with none —
or with numbers that exist only to verify a proof — skips it along with the
numerical half of step 10.

### 1. Fix the target

Establish, from the conversation or by asking once: the venue and its style
(journal vs. conference vs. arXiv-only), the length budget, the audience's
background, and — critically — **what is actually proved** versus what is
conjectured, checked numerically, or borrowed. Do not proceed on a vague answer to
the last one.

### 2. Build the claim ledger

Before any prose, write a scratch ledger (not part of the paper) listing every
claim the paper will make:

```
C1  main theorem, statement          status: proved        evidence: §4, Thm 4.1
C2  sharpness of the rate            status: numeric only  evidence: fig. 3
C3  Assumption A2 is not removable   status: counterexample §5
C4  method reduces to [Smith] when.. status: cited         evidence: [Smi14, Thm 2]
```

Every sentence in the finished paper that asserts something must trace to a ledger
row. Claims with status `numeric only` are stated as numerical evidence, never as
theorems. This ledger is also the map for the abstract and the contribution list.

### 3. Build the notation table

Also before prose. One row per symbol: symbol, meaning, type/domain, first use.
Enforce two invariants across the whole paper, not per-section — but only for
**free** symbols:

- one symbol, one meaning (no `h` as both a function and a bandwidth);
- one meaning, one symbol (no `A_j` here and `A_k` there without a reason).

Bound (dummy) variables — summation and integration indices, quantified
variables, set-builder variables — are local to their binder and may be reused
freely; the `i` of two different sums is two different variables. What must not
happen is a dummy shadowing a free symbol in scope (`n` the dimension, then
`\sum_{n=1}^{K}`), or a dummy referred to in prose after its binder has ended.

Renaming later is cheap in a macro-based file and expensive in prose. See
`references/notation.md` for the letter conventions, the LaTeX macro discipline
that makes renaming a one-line edit, and the confusable-glyph list.

### 4. Check the literature before claiming novelty

Anything of the form "we are the first", "this has not been studied", "unlike
existing work" requires a search pass first: how large is the relevant body of
work, which are the anchor papers, what exactly do they prove, and how far is the
present result from theirs. Rediscovering a known theorem is bad; transporting a
theorem between areas with a qualitatively new consequence is fine — but say which
one it is. Record the outcome in the ledger. Details in `references/evidence.md`.

### 5. Lay out the files

Never keep the whole paper in one `main.tex`. Use the skeleton in
`assets/skeleton/`: `main.tex` holds only preamble, macros include, and
`\input{sections/...}` lines; each section is its own file; all notation macros
live in `macros.tex`; the bibliography is a `.bib` built by the tooling, never
a hand-written `thebibliography` block. This makes reordering, notation changes,
selective rewriting and single-section compiles safe, and it makes every audit
flag point at a real location. Copy the skeleton rather than inventing a layout.
For the chapter-level variant, engine choice, and where `.bib` entries come
from, read `references/bibliography.md`.

### 5b. Adopting this in a project that already exists

Most of the time the paper is already written, under its own build, in a
repository with its own conventions. Do not restructure it to adopt the skill —
the scripts are meant to run against what you have, and the friction is
predictable:

- **No `.bib`.** A hand-written `thebibliography` is common in IEEE-style
  submissions. Run `audit.py` without `--bib`: it then validates `\cite` keys
  against the `\bibitem` keys in the tex, so citation integrity, duplicate keys
  and uncited entries are still checked. What a missing `.bib` costs is
  entry-level provenance — whether each record carries a DOI, an arXiv id or an
  MR number, and whether two entries are the same paper — which is what
  `bibcheck.py` exists for; with no file to read it exits non-zero, meaning not
  applicable rather than failing.
- **Your own Makefile.** Wire the targets in rather than copying the skeleton's.
  Point `SKILL` at the installed skill with an absolute path, since the
  manuscript is often a submodule or a sibling repository:

  ```make
  SKILL = $(HOME)/.claude/skills/math-paper-en
  LIMIT = 6
  check:                     # text only; no build, so it runs on a broken draft
  	python3 $(SKILL)/scripts/audit.py main.tex
  	python3 $(SKILL)/scripts/statcheck.py main.tex
  pages: main.pdf            # the seam can only be measured on a built PDF
  	python3 $(SKILL)/scripts/pagegate.py main.pdf --limit $(LIMIT)
  ```

- **Measure the artifact you submit.** Projects often keep a stand-in class or a
  preview build for speed. A page gate run against the preview measures a
  different layout than the one the venue sees; point it at the real PDF.
- **A mature manuscript flags a wall.** Running the audit for the first time on
  a finished paper produces hundreds of advisory lines, most of them terms of
  art. Triage once by class rather than by line: fix the mechanical classes
  (dangling labels, undefined symbols, unbraced capitals), decide the vocabulary
  ones in one pass, then keep the count from rising. A ratchet works where a
  clean sweep does not.
- **Project-local linters keep working.** The scripts here know nothing about
  your repository's own rules; run both, and let the project's rule file stay
  authoritative for anything they disagree on.
- **Small-caps headings.** `pdftotext` renders IEEE small caps with spaces
  ("A PPENDIX"), which `pagegate.py` normalises. If your class renders section
  headings some other way, pass `--after` the string that actually appears.

### 6. Fix the experimental setup before the production runs *(papers with measurements)*

If the paper reports measurements, the runs that produce them are part of the
writing, and the expensive failures happen here rather than in the prose. Before
the first production sweep, walk `references/experiments.md`: check that no
quantity the method consumes is one only the simulator knows; check that the
modelled steady state is the one the paper talks about; fix one setting —
protocol, nuisance levels, sample size — for every table in the paper; and size
the runs so the interval is narrower than the smallest difference you will
claim. Record the whole parameter set with each run, not just the seed.

The rule of thumb: every question a referee could ask about the setup should be
answerable from the experiment's own log. Re-running a campaign because a
parameter drifted mid-way, or because 120 trials could not resolve the effect,
costs more than the entire prose pass.

### 7. Draft the mathematics, statement first

For each result, in this order:

1. **Statement.** Self-contained: it must not depend on assumptions living in the
   surrounding text. Name the hypotheses (A1), (A2), ... and refer to them.
2. **Proof sketch.** A numbered list of the steps, each one sentence, so the reader
   sees the architecture before the details. Two to six steps.
3. **Full proof**, following exactly the sketch's step order and numbering.

Do not write theory ahead of its practical consequence: get one checkable
consequence out of the theoretical premise first, then grow the theory toward it.

**Verify every intermediate claim numerically.** Each lemma, each inequality, each
constant gets its own separate numerical check on random or adversarial instances
before it enters the file. Verification numbers report the *worst case*, not a
mean with an interval — one counterexample refutes a lemma. Measured numbers in
an experimental section follow the opposite discipline; see
`references/numerics.md`. A proof whose Lemma 3 fails at `n=7` is not a proof.
Record what was checked and how in a comment near the statement (`% checked:
1e4 random instances, n<=200, max violation 3e-14`), so the reviewer of your own
draft can rerun it.

### 8. Write the surrounding prose

Section-by-section jobs, and what belongs in each, are in
`references/structure.md`. Read that file before writing the abstract or the
introduction — those two are where most drafts fail.

Order that works: rough introduction first (to find out what the paper is), then
the body, then the introduction rewritten from scratch, then the abstract, then
final remarks.

### 9. Prose pass

Read `references/prose.md` and apply it. Its two halves: what makes mathematical
English flow (rhythm, transitions, "blah test", tense, `we`), and what makes text
smell of a language model (vocabulary, uniform sentence length, bullet thinking,
throat-clearing, symmetric triads, em-dash habit). Edit only what needs editing —
a passage that is already natural gets worse when rewritten.

### 10. Audit and self-referee

Run the scripts first. They clear the mechanical findings, so that whoever reads
the draft next — the author after a week, a coauthor, a review loop — spends
attention on what only judgement catches.

Run the mechanical audit:

```bash
python3 scripts/audit.py path/to/main.tex --bib path/to/refs.bib
python3 scripts/bibcheck.py path/to/refs.bib
python3 scripts/statcheck.py path/to/main.tex     # if the paper has numbers
```

It reports free-symbol collisions and dummy-shadowing (bound variables are
detected and excluded), undefined/unused labels, `\cite` keys missing from the
`.bib`, sentences opening with a symbol, adjacent formulas with no words between
them, LLM-marker vocabulary with line numbers, sentence-length uniformity,
em-dash density, and transition-word density. `bibcheck.py` covers the `.bib`
itself: entries with no DOI/arXiv id/MR number (unverifiable by anyone),
duplicates by DOI or title, one person spelled several ways, mixed key
conventions, unbraced capitals, hyphenated page ranges, reference-manager
bloat. `statcheck.py` covers the statistical reporting: numbers with no
uncertainty, a `\pm` whose meaning is never defined, `1.96\sigma` passed off as
a confidence interval for a mean, thresholded `p < 0.05` instead of an exact
value, "significant" with no test nearby, bolded table entries with no rule in
the caption, columns with mixed decimal places, undefined error bars. All three
scripts flag; they do not fix, and not every flag is a defect — a flagged word
may be a term of art, and an exact combinatorial value legitimately has no
error bar.

Then the human-level pass in `references/checklist.md`, which covers what no
script can check: does the abstract match the theorems, is every hypothesis used,
is the first sentence the best sentence.

### 11. Ship it

A numerical paper is not finished when the PDF compiles. `references/lifecycle.md`
covers what goes with it: the reproducibility artefact (method, data, seeds,
compute budget, and a `README` mapping every table and figure to the command
that produces it), anonymisation for double-blind review, arXiv mechanics, and
the structure of a response to reviewers. `references/disclosure.md` covers the
AI-assistance declaration.

## Reference map

| File | Read it when |
|---|---|
| `references/structure.md` | writing or reordering any section; title, abstract, intro, final remarks |
| `references/notation.md` | choosing symbols, macros, fonts; fixing a collision; typesetting displays |
| `references/prose.md` | writing or polishing any English sentence; de-LLM pass; translation from Russian |
| `references/evidence.md` | citations, novelty claims, terminology, numerical verification protocol |
| `references/bibliography.md` | project file layout, chapter splitting, where `.bib` entries come from, BibTeX vs Biber, key conventions |
| `references/numerics.md` | reporting measured numbers: which interval, exact p-values, multiple comparisons, what bold means in a table, error bars, rate fits |
| `references/experiments.md` | before running anything the paper will report: oracle check, rig reporting, one setting per paper, resolution, swept knobs, fixed-budget comparisons, reproducibility of the setup |
| `references/figures.md` | drawing any figure or table: plot choice, colour, sizing, formats, captions |
| `references/lifecycle.md` | the reproducibility artefact, submission and anonymisation, responding to reviewers |
| `references/disclosure.md` | before submitting: what AI assistance must be declared, and how to word it |
| `references/checklist.md` | pre-submission; final read-through; self-refereeing |
| `assets/skeleton/` | starting a new paper |
| `scripts/audit.py` | after any substantial edit, and before submission |
| `scripts/bibcheck.py` | whenever the `.bib` changes, and before submission |
| `scripts/statcheck.py` | whenever the paper reports measured numbers |
| `scripts/pagegate.py` | venues with a hard page limit, after every build |

## Fast paths

Not every request is a whole paper. Match the effort to the task, but never drop
the non-negotiables.

- **"Polish this paragraph" / "does this sound AI-written?"** → `prose.md` only.
  Report what you changed and why, in a short list. Do not restructure the
  mathematics uninvited.
- **"Write the abstract"** → ledger (step 2, abbreviated) + `structure.md`
  abstract section. An abstract asserting more than the theorems do is a defect,
  not a style choice.
- **"Translate my Russian draft"** → `prose.md` has a Russian-interference section
  (article use, "Let us consider", `which`/`that`, calques like "the given",
  "sufficiently many", tense drift). Translate meaning, then re-run the prose pass
  on the English as if it were a first draft.
- **"Check my notation"** → `audit.py` + `notation.md`; return a table of
  collisions with proposed renamings, not a rewritten paper.
- **"We need to cut a page"** → `structure.md` (Fitting a hard page limit) +
  `pagegate.py`. Cut roadmap prose and restatements of displays first, never a
  hypothesis or a scope qualifier, and re-check every touched claim afterwards.
- **"Referee my draft"** → `checklist.md` in reviewer mode; deliver findings as a
  separate document, not as edits inside the author's text.

## Communicating with the user

Report gaps, unverifiable citations, and claims that outrun their evidence
explicitly and early — before delivering polished prose built on them. A beautiful
paragraph defending an unproved claim wastes more of the author's time than a
blunt question does.
