# math-paper-en

A skill for writing, restructuring, translating, polishing and auditing research
papers in mathematics and mathematical engineering in English LaTeX.

## What is in here

```
math-paper-en/
├── SKILL.md                    workflow: ledger -> notation -> literature ->
│                               files -> statements -> prose -> audit
├── references/
│   ├── structure.md            title, abstract, introduction, statements,
│   │                           proofs, numerics, final remarks, references;
│   │                           venue variations (math / CS / IEEE / short note)
│   ├── notation.md             one symbol one meaning; letter conventions,
│   │                           confusable glyphs, macro discipline, displays,
│   │                           subscript hygiene, fixing a collision late
│   ├── prose.md                sentence craft, rhythm, tense and voice;
│   │                           LLM tells (vocabulary tiers, throat-clearing,
│   │                           triads, uniformity); Russian-interference table
│   ├── evidence.md             claim ledger, citation verification and citation
│   │                           grammar, terminology, novelty claims, numerical
│   │                           verification protocol for proofs
│   ├── bibliography.md         project layout, one file per section, chapter
│   │                           splitting, where .bib entries come from, the
│   │                           BibTeX objection, bibtex vs biber, keys,
│   │                           normalising an imported entry
│   ├── numerics.md             uncertainty intervals (SD/SE/CI/range), digits,
│   │                           hypothesis tests and exact p-values, multiple
│   │                           comparisons (Demsar), what bold means in a
│   │                           table, error bars, rate fits, verification vs
│   │                           measurement
│   ├── experiments.md          the oracle check, reporting the rig, one setting
│   │                           per paper, resolution before claims, swept
│   │                           knobs, fixed-budget comparisons, setup
│   │                           reproducibility, what stays in the notebook
│   ├── figures.md              plot choice, ink, colour, sizing and formats,
│   │                           captions, tables vs figures, reproducible
│   │                           figure scripts
│   ├── lifecycle.md            reproducibility artefact, submission and
│   │                           anonymisation, responding to reviewers,
│   │                           after acceptance
│   ├── disclosure.md           what AI assistance must be declared, the
│   │                           provenance rule, venue policies, wording
│   └── checklist.md            pre-submission checklist + self-refereeing pass
├── scripts/
│   ├── audit.py                mechanical audit of a .tex tree
│   ├── bibcheck.py             lint of the .bib itself
│   ├── statcheck.py            lint of the statistical reporting
│   └── pagegate.py             hard page limit, measured at the page seam
└── assets/skeleton/            multi-file LaTeX project to copy for a new paper
    ├── Makefile                make / make check / make draft SECTION=...
    ├── main.tex                preamble + \input lines only
    ├── macros.tex              one macro per notation-bearing symbol
    ├── refs.bib
    └── sections/00..07*.tex
```

## `dev/`

`dev/skill-evals.json` is **trial and unvalidated**: prompts that exercise the
skill's own rules during its development. Never run. The directory is not read
at runtime and can be deleted. The quality gate for a manuscript is
`references/checklist.md`.

## Installing

Copy the folder into your skills directory:

```bash
cp -R math-paper-en ~/.claude/skills/          # global
cp -R math-paper-en .claude/skills/            # project-level
```

Or open the packaged `.skill` file and press **Save skill**.

Adopting it in a paper that already exists — its own Makefile, no `.bib`, a
mature manuscript that flags a wall on the first audit — is covered in
`SKILL.md`, step 5b. The scripts run against what you have; nothing needs
restructuring.

## Running the audit alone

The audit script has no dependencies beyond the Python standard library:

```bash
python3 scripts/audit.py path/to/main.tex --bib path/to/refs.bib
python3 scripts/audit.py main.tex --json report.json    # machine-readable
python3 scripts/audit.py main.tex --no-follow           # ignore \input
python3 scripts/bibcheck.py path/to/refs.bib
python3 scripts/statcheck.py path/to/main.tex
python3 scripts/pagegate.py path/to/main.pdf --limit 6   # 0 met, 1 exceeded, 2 not checked
```

It follows `\input`/`\include`, strips math mode, verbatim and markup, and
reports: LLM-marker vocabulary by tier with line numbers, throat-clearing and
model-reflex phrasing, proof gap-fillers ("it can be shown", "clearly"),
sentence-length statistics (sd, coefficient of variation, band share, runs),
em-dash and transition density, sentences opening with a symbol, adjacent
formulas, colons before displays, free-symbol usage and collisions with bound
(dummy) variables detected and excluded, dummy-shadowing, confusable glyphs, duplicate/undefined/unused labels, `\cite` keys
missing from the `.bib`, uncited and incomplete `.bib` entries, and leftover
`\todo` markers.

`bibcheck.py` lints the `.bib` itself: entries with no DOI, arXiv id, MR number
or URL (nobody can verify those), duplicates by key, DOI, arXiv id or title, one
person spelled several ways across entries, mixed citation-key conventions,
capitals BibTeX will lowercase, hyphenated page ranges, reference-manager bloat,
and field hygiene.

With no `.bib` — a hand-written `thebibliography`, common in IEEE-style
submissions — `audit.py` validates `\cite` keys against the `\bibitem` keys in
the source instead, so citation integrity is still checked; only entry-level
provenance is lost.

`pagegate.py` checks a hard page limit where it actually binds — the last allowed
page must *end* with the last bibliography entry, not merely start it. It exits 0
when the limit is met, 1 when it is exceeded, and 2 when the check could not be
performed (poppler missing, PDF unreadable), so a build gate can treat "could not
verify" as failure rather than as a pass.

In the skeleton, `make check` runs the three text linters and needs no build;
`make pages LIMIT=6` builds the PDF and measures the seam, and `make check-all
LIMIT=6` does both.

`statcheck.py` lints the statistical reporting: numbers with no uncertainty, a
`\pm` whose meaning is never defined, `1.96\sigma` used where a confidence
interval for a mean was meant, thresholded `p < 0.05` instead of an exact value,
"significant" with no test or interval nearby, tests with no multiple-comparison
correction, bolded table entries with no rule in the caption, columns with mixed
decimal places, and undefined error bars.

Every flag is advisory. A flagged word may be a term of art, and an exact
combinatorial value legitimately carries no error bar; the scripts exclude math
mode but know nothing about your field, so a flagged term of art stays.
Provenance fields make an entry
checkable; only opening the record proves it.

## Disclosure

The skill is built for writing papers with a language model in the loop. Every
major venue now requires that such assistance be disclosed and forbids listing a
model as an author. `references/disclosure.md` covers what to disclose and where;
the de-AI prose rules exist because model-flavoured writing is bad writing, not
as a way of hiding anything.

## Sources

The structural and stylistic rules are distilled from the standard guides —
Halmos, *How to Write Mathematics*; Knuth, Larrabee & Roberts, *Mathematical
Writing* (the 27 points of §1); Krantz, *A Primer of Mathematical Writing*;
Higham, *Handbook of Writing for the Mathematical Sciences*; Gillman, *Writing
Mathematics Well*; Pak, *How to Write a Clear Math Paper: Some 21st Century
Tips*; Poonen's practical suggestions; Tao's advice on writing — together with
the data-driven LLM marker vocabulary of Kobak, González-Márquez, Horvát &
Lause, *Delving into LLM-assisted writing in biomedical publications through
excess vocabulary*, Science Advances 11 (2025), eadt3813, and the de-AI prose
conventions circulating in the open Claude-skill ecosystem.

The reporting and lifecycle rules come from Demšar, *Statistical Comparisons of
Classifiers over Multiple Data Sets*, JMLR 7 (2006); Wasserstein & Lazar, *The
ASA's Statement on p-Values*, The American Statistician 70 (2016); Mensh &
Kording, *Ten simple rules for structuring papers*, PLoS Comput. Biol. 13(9)
(2017); Rougier, Droettboom & Bourne, *Ten Simple Rules for Better Figures*,
PLoS Comput. Biol. 10(9) (2014); Tufte, *The Visual Display of Quantitative
Information*; and the machine-learning reproducibility checklists (Pineau et
al.'s NeurIPS code-submission process, Gundersen's reproducibility factors).

The de-AI rules are good-writing rules, not detection evasion. No rule set
guarantees a detector score, detectors have high error rates in both
directions, and the skill explicitly forbids tampering (homoglyphs, invisible
characters, deliberate typos).
