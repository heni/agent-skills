# Project layout and bibliography tooling

Contents: [File layout](#file-layout) · [Why one file per section](#why-one-file-per-section)
· [Long documents](#long-documents-theses-and-books) · [Where entries come from](#where-bib-entries-come-from)
· [The BibTeX objection](#the-bibtex-objection-and-what-it-actually-means) ·
[Engine choice](#engine-bibtex-or-biber) · [Keys](#citation-keys) ·
[Normalising an imported entry](#normalising-an-imported-entry) ·
[The loop](#the-working-loop)

## File layout

```
paper/
├── main.tex              preamble, macros include, \input lines -- no content
├── macros.tex            every notation-bearing symbol
├── refs.bib              bibliography, one entry per source
├── sections/
│   ├── 00-abstract.tex
│   ├── 01-introduction.tex
│   ├── …
│   └── 06-final-remarks.tex
├── figures/
└── scripts/              numerical checks of the lemmas, one file per lemma
```

`assets/skeleton/` in this skill is exactly this, ready to copy. `main.tex`
contains no prose. If you find yourself editing text in `main.tex`, the layout
has already broken.

## Why one file per section

- **Reordering is a two-line edit.** Moving §4 before §3 means swapping two
  `\input` lines, not cutting several hundred lines of source and hoping the
  braces balanced.
- **Compile one section while drafting.** `\includeonly{sections/04-proofs}`
  with `\include`, or comment out the other `\input`s, turns a twenty-second
  build into a two-second one. On a long proof this changes how you work.
- **Diffs stay readable.** A rewritten introduction shows up as a change to one
  file; git blame stays meaningful; a coauthor editing §5 never conflicts with
  you editing §2.
- **Selective rewriting is safe.** A style pass over the introduction cannot
  accidentally touch a theorem statement three hundred lines away.
- **The audit reports real locations.** `scripts/audit.py` follows `\input` and
  `\include`, so every flag comes back as `04-proofs.tex:87`, not as a line
  number in a two-thousand-line monolith.

`\input` splices the file in place. `\include` starts a new page and enables
`\includeonly`, at the cost of the page break — right for chapters, wrong for
sections. Use `\input` for a paper, `\include` for a thesis.

## Long documents (theses and books)

```
thesis/
├── main.tex
├── chapters/
│   ├── 01-introduction/
│   │   ├── chapter.tex        \input{...} lines for the sections
│   │   └── sections/
│   └── 02-…/
└── refs.bib
```

One directory per chapter, `\include{chapters/01-introduction/chapter}` in
`main.tex`, and inside each chapter the same `\input` discipline one level down.
With `biblatex` you can give each chapter its own reference list by wrapping it
in `\begin{refsection}…\end{refsection}` and calling `\printbibliography[
heading=subbibliography]`; with plain BibTeX this needs `bibunits` or
`chapterbib` and is more trouble than it is worth — prefer one bibliography at
the end unless the house style demands otherwise.

## Where `.bib` entries come from

**Rule: never type a bibliography entry by hand, and never accept one that a
language model produced from memory.** Every entry is exported from a record
that actually exists:

| source | what it gives | how |
|---|---|---|
| **MathSciNet** | the canonical math record, MR number, reviewed | "Citation → BibTeX"; requires a subscription |
| **zbMATH Open** | same role, free | entry page → BibTeX button, `Zbl` number |
| **arXiv** | preprints, `eprint`/`archivePrefix` | abstract page → "Export BibTeX Citation" |
| **Crossref / DOI** | anything with a DOI | `curl -LH "Accept: text/bibliography; style=bibtex" https://doi.org/10.xxxx/yyy`, or a `doi2bib` service |
| **publisher page** | volume, issue, pages | last resort; formatting varies |
| **Google Scholar** | fast, but sloppy | acceptable only as a lookup step before fetching the real record |

For a paper you already have as a PDF, `pdftotext` the first page and search the
DOI, or use the arXiv id printed in the margin. For a book, the ISBN.

Practical consequence, and the reason this matters more than tidiness: an entry
you fetched is an entry that exists. An entry you typed from memory may not be.
Bibliographies are copied between papers without checking, so a fabricated
reference propagates and outlives the paper that introduced it.

`scripts/bibcheck.py` flags every entry with no DOI, arXiv id, MR number or URL
— those are precisely the ones neither you nor a referee can verify.

## The BibTeX objection, and what it actually means

Igor Pak advises against using BibTeX unless you know exactly what you are
doing, and he is right about the symptom: MathSciNet exports are bloated with
fields nobody wants, and the same author appears as `Paul Erd\H{o}s` in one
entry and `Erdös, P.` in another, so the reader cannot tell it is one person.

The objection is to *unedited imports*, not to the tool. Hand-maintaining a
`\begin{thebibliography}` block is worse: it breaks alphabetisation, makes keys
inconsistent, and removes the DOI that would let anyone check the entry. The
resolution is a two-step discipline: **import from an authoritative record, then
normalise**. `bibcheck.py` automates the detection half of the second step —
it reports the same-person-several-spellings case explicitly.

## Engine: BibTeX or Biber

- **`bibtex` + `amsalpha`/`amsplain`** — the default for a math journal. Keys
  come out as `[Kra96]`, `[SY09]`, `[A+13]`, which tell the reader the author
  and year at the point of citation. Most AMS and Elsevier templates assume it.
- **`biblatex` + `biber`** — better Unicode handling, `refsection` for
  per-chapter lists, `\autocite`, and a real query language for the `.bib`. Use
  it for theses and for anything you control end to end.
- **Venue templates override both.** IEEE wants `IEEEtran.bst` and numeric
  citations; LNCS wants `splncs04.bst`. Do not fight the template.

Whichever you use, commit the generated `.bbl` alongside the source when
submitting to arXiv — arXiv does not run BibTeX for you.

## Citation keys

Pick one convention and convert everything to it:

- **alphanumeric** `Kra96`, `SY09`, `Tra15a`, `A+13` for five or more authors,
  `Con17+` for unpublished — matches `amsalpha` output and reads well in a long
  paper;
- **author-year** `krantz1996` — fine, and what most reference managers emit.

Do not mix. `bibcheck.py` reports the distribution and complains when both
appear. Never let a key encode something that can change (a section number, a
draft ordinal).

## Normalising an imported entry

After importing, before committing:

1. **Strip the bloat** — `abstract`, `keywords`, `file`, `annote`, and the
   reference-manager private fields. They inflate the file and leak your local
   paths.
2. **One spelling per person**, across every entry. Pick the form the person
   uses themselves.
3. **Brace the capitals that must survive**: `title = {Fast {LLM} inference on
   {GPUs}}`. BibTeX lowercases unbraced words in many styles.
4. **En-dashes in page ranges**: `pages = {12--34}`, never `12-34`.
5. **Abbreviate journal names consistently** — either all abbreviated
   (`Amer. Math. Monthly`) or all full, not a mixture.
6. **Keep `doi` and `eprint`.** They are the provenance; strip them and the
   entry becomes uncheckable. Add `archivePrefix = {arXiv}` next to `eprint`.
7. **Unpublished work**: `@misc` with `eprint`, or `howpublished` plus the URL
   and an access date. Not a bare title.

## The working loop

```bash
latexmk -pdf main.tex                        # build
python3 scripts/audit.py main.tex --bib refs.bib
python3 scripts/bibcheck.py refs.bib
```

`audit.py` checks the `.tex` side of the bibliography — `\cite` keys with no
entry, entries never cited, entries missing author/title/year. `bibcheck.py`
checks the `.bib` itself — provenance, duplicates by DOI/arXiv id/title, name
spellings, key convention, title casing, page ranges, bloat.

Neither proves an entry is real. Provenance fields make it *checkable*; only
opening the record proves it. Run the verification pass described in
`evidence.md` before submission, and report to the author which entries were
confirmed, which were corrected, and which could not be found.
