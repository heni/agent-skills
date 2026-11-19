# The paper's lifecycle: artefact, disclosure, submission, review

Contents: [Reproducibility artefact](#the-reproducibility-artefact) ·
[Disclosing AI assistance](#disclosing-ai-assistance) (see also `disclosure.md`) · [Submission mechanics](#submission-mechanics)
· [Anonymisation](#anonymisation-for-double-blind-review) · [Responding to reviewers](#responding-to-reviewers)
· [After acceptance](#after-acceptance)

The artefact answers "can someone re-run this?"; the paper's own setup paragraph
answers "can someone rebuild the experiment from the text?". They overlap but are
not the same list — what belongs in the text is in `experiments.md`, under
Report the rig.

## The reproducibility artefact

Anything with a numerical section ships with the means to redo it. The item list
below follows the machine-learning reproducibility checklists (Pineau et al.,
the NeurIPS code-submission process; Gundersen's reproducibility factors) and
transfers directly to numerical mathematics.

**Method.** A complete description of the algorithm, including the parts that
felt too obvious to write down; the loss or objective; every hyperparameter and
how it was chosen; the search space if it was tuned, and the budget spent
searching.

**Data.** Source and version of every dataset, the split and how it was made,
any preprocessing, and the licence. For synthetic data, the generator — as code,
not as prose.

**Experiment.** Number of runs, the seeds, the hardware, the wall-clock and the
total compute budget including failed and discarded runs. Reporting only the
runs that worked is the cheapest form of selective reporting.

**Code.** A repository with an environment specification (lockfile, container,
or exact versions), an entry point per experiment, and a `README` mapping each
table and figure in the paper to the command that produces it:

```
Table 2   python -m experiments.bench --config configs/table2.yaml
Figure 3  python -m figures.fig3 --data results/sweep.parquet
```

That mapping is what makes an artefact usable. Without it, a reader with your
code still cannot reproduce your Table 2.

**Numerical verification.** The lemma checks from `evidence.md` are part of the
artefact: one script per lemma, named after it, with the sweep ranges in the
file. They are the cheapest thing you can offer a sceptical referee.

For anything you cannot release — proprietary data, licensed inputs — say so
explicitly and say what a reader could substitute. Silence reads as
carelessness or as concealment.

## Disclosing AI assistance

A model cannot be an author, and the human authors remain responsible for every
claim, proof, citation and number. Beyond that, disclosure tracks where the
scientific content came from: prose editing and rendering code under an author
who owns the theory and checked the work is instrumental; experiments run, data
cleaned, algorithms chosen or implemented, or proof steps supplied are
contributory and are declared. Several publishers demand more than that; the
venue's policy wins, and when in doubt you disclose.

The tiers, the test, where this agrees and disagrees with ACL / Elsevier /
Springer / Science, and a statement to adapt are in `disclosure.md`. Read it
before submitting.

## Submission mechanics

- **Read the venue's author guidelines end to end once**, before the last day.
  Length limits, whether references count against them, template version,
  supplementary-material rules, and the anonymisation policy all change between
  editions.
- **Use the venue's template unmodified.** Shrinking margins, `\vspace{-…}`
  before every section, or a smaller font is the most reliably detected form of
  cheating, and several conferences desk-reject for it.
- **arXiv**: upload the source, not just the PDF. arXiv does not run BibTeX, so
  commit the generated `.bbl`. Check the compiled result on arXiv before
  announcing — it uses its own TeX Live version. Choose the licence
  deliberately. Cross-list to the secondary category that matches your actual
  readership.
- **Version discipline.** Keep the exact source of the submitted version tagged
  in version control. When the referee report arrives four months later you will
  need to know what they read.

## Anonymisation for double-blind review

- Remove names, affiliations, acknowledgements and funding from the manuscript,
  and check the PDF metadata — the author field survives `\author{}` removal in
  many toolchains.
- Cite your own prior work in the third person ("Smith et al. showed"), not as
  "in our previous work [12]". Do not remove the citation; that damages the
  paper and is not required.
- Anonymise the repository link (an anonymous mirror), or say the code will be
  released on acceptance.
- Check whether the venue permits a concurrent arXiv preprint. Most do; a few
  do not, and the rule is usually about *advertising* the preprint during
  review rather than about its existence.

## Responding to reviewers

The response document is a piece of technical writing with its own conventions,
and it is judged.

**Structure.** One numbered item per reviewer point, in the reviewers' order,
each with: a one-line restatement of the point, the response, and the exact
change made with a pointer (`§4.2, new paragraph`; `Table 3, new column`). Use
colour or an explicit marker for changed text in the revised manuscript.

**Changes go in the paper, arguments go in the response.** The manuscript states
the result; it does not record that a referee once doubted it. A defence written
into the paper reads to the next reader as an answer to a question nobody asked
(see `prose.md`, "Context leaks").

**Stance.** Thank briefly and once, at the top, not per item. Then be factual.
Three kinds of point and three responses:

- **Right, and fixable.** Say so plainly, make the change, point at it. This is
  most points. Do not argue.
- **Right, and not fixable within scope.** Concede it, say why it is out of
  scope, and add it to the limitations or the open problems. A stated limitation
  is stronger than a defended weakness.
- **Based on a misreading.** Assume the misreading is the paper's fault, because
  usually it is. Fix the text that permitted it, then say what you changed. "As
  stated in §3" is the worst sentence in a rebuttal; if they missed it, it was
  not stated well enough.

Never leave a point unanswered — an editor scanning for unaddressed items will
find it. Never respond with new claims that are not in the revised manuscript.
Never argue about the reviewer's competence, however tempting; it does not work
and it is remembered.

**When the reviewer is wrong on the mathematics**, show the argument in the
response, add it to the paper if it belongs there, and stay neutral in tone. A
short, complete, unemotional derivation ends the exchange.

## After acceptance

- Proofread the galleys against your source; copy editors introduce errors in
  mathematics with some regularity, and the errors become yours on publication.
- Update the arXiv version to match, and keep updating it as typos surface —
  including after publication.
- A wrong proof or a missed attribution in the published version cannot be
  quietly fixed in an update; that needs an erratum or an acknowledgement of
  priority.
- Post the artefact where you promised to post it, on the day you promised.
