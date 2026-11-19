# Pre-submission checklist

Run `scripts/audit.py` first — it covers the mechanical items. This file is what
no script can check. Work through it in order; each block is cheap and catches a
different class of defect.

## A. Correctness and completeness

- [ ] For every quantity the method consumes: who knows it, and from where? A
      value only the simulator has is an oracle, and an experiment claiming
      practicality may not use one (`experiments.md`).
- [ ] Every assertive sentence traces to a claim-ledger row, with matching status
      language (proved / cited / numerically checked / conjectured).
- [ ] Sentences added while fixing something are in the ledger too: a
      justification attached to a repair is a claim and needs its own source
      (`evidence.md`).
- [ ] Every hypothesis (A1), (A2), ... is used somewhere. If one is not, either
      drop it and strengthen the theorem, or say why it is kept.
- [ ] Every lemma and every explicit constant was checked numerically, with the
      check recorded in a comment.
- [ ] Each proof follows the order announced in its sketch, and each step of the
      sketch appears.
- [ ] Degenerate cases are handled or explicitly excluded: $n=1$, empty set,
      equality, zero denominators, ties.
- [ ] No "it can be shown", "clearly", "obviously", "a standard argument" covering
      a step you have not actually done.
- [ ] Constants: is each one uniform in the parameters it must be uniform in? Say
      so in the statement.
- [ ] Every theorem statement is self-contained when read alone.

## B. Structure

- [ ] The main theorem is findable within one minute of opening the paper.
- [ ] The abstract claims exactly what the theorems prove — no more, no fewer.
- [ ] The first sentence is the best sentence, and it is not "An X is a Y" and not
      "Let $G=(V,E)$ be ...".
- [ ] The introduction states the main result (or a clean corollary) by page 2.
- [ ] The last paragraph of the introduction maps sections to content in your own
      words.
- [ ] Section lengths follow content, not a template.
- [ ] Forward references (`see §6.2`) exist wherever the body defers a discussion,
      and each target exists.
- [ ] The conclusion / final remarks introduce no new claims.

## C. Notation

- [ ] The notation table is complete and matches the text.
- [ ] One symbol, one meaning, across the whole paper — not per section — for
      every free symbol.
- [ ] No dummy variable shadows a free symbol in scope ($n$ the dimension and
      $\sum_{n=1}^{K}$ in the same paper).
- [ ] No dummy variable is referred to in prose outside its binder.
- [ ] One meaning, one symbol; index conventions are consistent (a preference
      for dummies, an invariant for free symbols).
- [ ] No symbol starts a sentence; no two formulas touch without a word between.
- [ ] The blah test passes: replace formulas by "blah" and the paragraphs still
      read as English.
- [ ] No confusable glyphs (`l`, `\epsilon`, `\emptyset`, $\iota$, $\kappa$).
- [ ] No subscripted subscripts or superscripts.
- [ ] Displays punctuated as parts of sentences; no colon before a display that
      completes the sentence; numbered only where referenced or important.
- [ ] Every defined term appears in exactly its defined form, never inflected.

## D. Prose

- [ ] No Tier A vocabulary survives outside terms of art.
- [ ] No throat-clearing openers; no per-section closing summaries.
- [ ] Sentence-length variation is real (audit reports sd and CV).
- [ ] No run of four sentences with the same shape or opener type.
- [ ] Em-dashes ≤ 1 per paragraph; transitions (*moreover, furthermore,
      additionally*) ≤ 1 per two paragraphs.
- [ ] Bullet lists only where the content is genuinely enumerable.
- [ ] Tense consistent; `we` used as author-and-reader, not as a formal `I`.
- [ ] No superlatives about your own work.
- [ ] Every negative or concessive sentence answers a doubt the text itself
      raises; defences of choices nobody in the paper questioned are cut.
- [ ] Every back-reference resolves to a numbered place in this paper.
- [ ] Defences are collected in one designated place (limitations, discussion,
      final remarks), not distributed through the body; each appears once.
- [ ] Every negative sentence in the body is a boundary, not a defence: deleting
      it would make a statement false or ambiguous.
- [ ] No revision residue ("in the revised version", "as requested", "following
      the reviewer's suggestion") and no private shorthand or internal names.
- [ ] For translated drafts: articles, "Let us consider", *which*/*that*,
      *respectively*, calques — all checked.
- [ ] Terminology deprecated by the venue's style manual replaced in your own
      prose (master/slave → leader/follower, blacklist/whitelist →
      denylist/allowlist); cited titles left as published.
- [ ] No generic "he" and no "he or she" / "s/he" repairs; terms of art
      (double-blind, dummy variable) left alone.

## E. References and attribution

- [ ] Every `.bib` entry was verified against a real record this session, or came
      from the author. No exceptions, no "probably right".
- [ ] Every attributed claim is a claim the cited work actually makes.
- [ ] Citation phrasing matches the attribution grammar (`[X] proved` vs `see [X]`).
- [ ] No `[2–19]`-style range citations.
- [ ] Specific locations (`[A, §3.1]`) given for results quoted from long works.
- [ ] Bibliography style internally consistent; one spelling per author.
- [ ] Every `\cite` key resolves; every `.bib` entry is cited or deliberately kept.
- [ ] Every entry was exported from a real record (MathSciNet, zbMATH, arXiv,
      DOI), not typed; `doi`/`eprint`/`mrnumber` retained so a referee can check.
- [ ] `bibcheck.py` clean: no duplicates, one spelling per person, one key
      convention, capitals braced, `--` in page ranges, no manager bloat.
- [ ] Acknowledgements name people correctly; permission obtained for attributed
      unpublished ideas.
- [ ] No author or affiliation line was invented.
- [ ] Any remaining `\todo{}` is listed for the user, not silently shipped.

## F. Figures, tables, numerics

- [ ] The rig is reported: how instances were generated, the geometry and its
      selection rule, the protocol, the sample size, the number of instances, the
      level of every nuisance parameter, and which of them the method may know.
      Realised quantities are printed next to nominal ones (`experiments.md`).
- [ ] Every table in the paper comes from one setting: same protocol, same
      nuisance levels, same sample size. A claim that two runs share draws is
      checked against the seed streams, not assumed.
- [ ] The interval half-width is smaller than the smallest difference the paper
      claims; one kind of interval is used throughout.
- [ ] Every figure and table is referenced in the text with a sentence saying what
      to look at.
- [ ] Figures small enough to sit inside the flow; huge ones moved to an appendix.
- [ ] Each figure supports one stated sentence; the plot type answers the actual
      question (no pie charts, no dual axes, no 3-D bars).
- [ ] Colourblind-safe palette, redundant encoding (colour *and* style), a
      perceptually uniform colourmap for sequential data — checked in grayscale.
- [ ] Figures designed at final print size; in-figure fonts match the body text;
      vector formats for drawn plots.
- [ ] Captions carry: what is plotted with units, what the uncertainty is and
      over what $n$, the conditions, and one sentence on what to notice.
- [ ] Each figure is produced by a committed script that reads a data file; no
      hand-edited PDFs.
- [ ] Experimental setup reproducible: dimensions, distributions, seeds, tolerances.
- [ ] Negative results and failure regimes reported.
- [ ] Numerical results described in `numerically checked` language, never as proof.
- [ ] Every measured number has an uncertainty and an $n$; the caption says which
      quantity the $\pm$ is (SD, SE, 95% CI, IQR) — and $1.96s$ is not a CI for
      a mean, $1.96 s/\sqrt{n}$ is (use the $t$ multiplier when $n \lesssim 30$).
- [ ] Skewed or heavy-tailed quantities (runtimes) reported as median and range,
      not mean and SD.
- [ ] Digits printed do not exceed what the uncertainty supports; decimals
      consistent down each column.
- [ ] Every comparison claim has a named test, a stated null, one/two-sidedness,
      the exact $p$-value (not $p < 0.05$), and an effect size with its interval.
- [ ] Paired data tested with a paired test.
- [ ] Multiple comparisons corrected, and the correction named.
- [ ] Non-significant differences reported as an interval, not as "no effect".
- [ ] Bold in tables means "best, or not distinguishable from best", and the
      caption states the rule; no bolding where no test was possible.
- [ ] Every error bar and shaded band defined in its caption.
- [ ] Rate claims come from a fit with a CI on the exponent over a stated range,
      not from eyeballing a log--log slope.
- [ ] Lemma-verification numbers report the maximum violation, sample count and
      parameter ranges — never a mean.
- [ ] `statcheck.py` clean, or every remaining flag consciously accepted.

## G. Mechanics

- [ ] Compiles with no warnings that matter: no undefined references, no missing
      citations, no overfull boxes on displayed formulas.
- [ ] No page break inside a display; no line break leaving a lone symbol.
- [ ] Hyphen / en-dash / minus / em-dash each used correctly.
- [ ] `main.tex` contains no content — only preamble, macros, and `\input`s.
- [ ] The `.bbl` is committed alongside the source for an arXiv submission.
- [ ] Page limit measured at the seam, not by a landmark: the last allowed page
      ends with the last bibliography entry, the next begins with the appendix.
- [ ] Every sentence touched by the length pass re-checked against the table it
      summarises — cutting words edits claims (`structure.md`).
- [ ] Venue requirements met: length, template, anonymization, section naming,
      reference style, abstract citation policy.

## H. Shipping

- [ ] Artefact complete: method, hyperparameters and search budget, data source
      and version, splits, seeds, hardware, compute spent including failed runs.
- [ ] `README` maps every table and figure to the command that reproduces it.
- [ ] Lemma-verification scripts included, one per lemma.
- [ ] Anything not releasable is named as such, with a suggested substitute.
- [ ] Every use of a model classified: instrumental (prose, formatting, code
      whose failure modes your evidence covers) versus contributory (experiments
      run, data cleaned, algorithms chosen or implemented, proof steps supplied,
      results not independently verified).
- [ ] For each piece of generated code that produces numbers: named the evidence
      — comparison against data already held, a test against a closed form,
      benchmark table, reference implementation or invariant, or a close read —
      and confirmed it covers the regime actually reported.
- [ ] No rendering script computes anything: aggregation, binning, smoothing,
      NaN handling and error bars live upstream, in code that was read or tested.
- [ ] Every contributory use disclosed, named specifically rather than in a
      blanket sentence.
- [ ] The venue's current AI-assistance policy was read; where it demands more
      than the provenance rule above, the venue wins. No model listed as an
      author. (`disclosure.md`)
- [ ] You can reconstruct and defend every step of the paper without the model.
- [ ] Venue template unmodified — no shrunk margins, no negative `\vspace`.
- [ ] Double-blind: names, affiliations, acknowledgements, funding and PDF
      metadata scrubbed; own work cited in the third person; repository link
      anonymised.
- [ ] arXiv: source uploaded, `.bbl` committed, licence chosen, compiled result
      checked on arXiv itself.
- [ ] The exact submitted source is tagged in version control.

## Self-refereeing pass

Read the paper once as a hostile referee, in a single sitting, without editing.
Ask, in this order:

1. What is the main theorem, in one sentence? If it takes longer, the paper does
   not present it well.
2. Is it new? Which anchor paper is closest, and what exactly does this add?
3. Where is the proof's load-bearing step, and did I believe it?
4. Which hypothesis, if dropped, breaks the proof? Does the paper say so?
5. What would I ask the author to add? Add it now.

Then let the draft sit for a few days and re-read. Nearly every draft loses a
paragraph and gains a sentence at this stage.
