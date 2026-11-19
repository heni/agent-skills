# Evidence: claims, citations, terminology, verification

Contents: [Claim ledger](#the-claim-ledger) · [Citation verification](#citation-verification)
· [Citation grammar](#citation-grammar-what-a-phrasing-promises) · [Citing lists](#citing-a-body-of-work)
· [Terminology](#terminology) · [Novelty](#novelty-claims) ·
[Numerical verification of proofs](#numerical-verification-of-proofs) · [Owning generated code](#owning-generated-code)

## The claim ledger

Every assertion in the paper has exactly one of these statuses, and the prose must
match the status:

| status | licensed language | forbidden |
|---|---|---|
| proved here | "we prove", "it follows from Lemma 3", "Theorem 2 shows" | — |
| proved elsewhere | "[Smi14, Thm 2] shows", "by [Smi14]" | claiming it as new |
| numerically checked | "the experiments indicate", "consistent with", "we observe" | "we show", "it follows", "this proves" |
| conjectured | "we conjecture", "we expect", "it seems plausible" | any assertive form |
| known folklore | "it is standard that", with a source | "it is well known" with no source |

Mixing the rows is the most common substantive defect in a draft and the first
thing a referee catches. Before delivering any section, re-read its assertive
sentences against the ledger.

If a gap is found while writing — a step that does not close, a constant that is
not uniform, a case that was not handled — stop and tell the user. Never bridge it
with "it can be shown", "clearly", "a standard argument gives", or "similarly" if
you have not checked that the argument is in fact similar.

## A fix adds claims of its own

Corrections are where unsourced claims enter a finished draft. The defect is
found, the sentence is rewritten, and the rewrite acquires an explanation the
author supplied from intuition a minute earlier: "because otherwise no
stationary value exists", "which the projection removes", "as the experiment
in §5 shows". The original statement went through the ledger; the justification
attached to its repair did not.

Three from one review round on a single manuscript: an explanation that
contradicted the very equation it was defending, a pointer to an experiment that
had never been run, and a bound quoted from memory as $0.03$ where the data said
$0.0345$. Each was added
while closing a real defect, and each was more confidently phrased than the text
it replaced.

**Rule.** A justification added during a fix is a claim: it goes into the ledger,
or it goes. If it cannot be traced in three lines to a proof, a measurement or a
source, delete the justification and keep the corrected statement bare — an
unexplained true sentence is worth more than an explained one that is wrong.
Re-read a fix the next day as if someone else had written it; the fresh
confidence that makes fixes feel finished is exactly what hides them.

## Citation verification

**Nothing enters the bibliography unverified.** For each reference:

1. It came from the user, from a document in the session, or from a search result
   that showed the actual record.
2. Authors, title, venue, year, and (if cited by number) the theorem or section
   number were each seen, not reconstructed.
3. The claim attributed to it is a claim it actually makes. Recalling the gist of a
   paper is not verification; a paper that proves a bound for symmetric matrices
   does not prove it in general.

If any of the three fails, write

```latex
\todo{REF: needed — result X (bound on the spectral gap of Erdős–Rényi graphs)}
```

and list the gaps for the user at the end of the turn. An unverified citation is
worse than no citation: it survives review, propagates, and eventually embarrasses
the author. Bibliographies are copied blindly between papers, so errors do not
die.

When search tools are available, verify in a batch pass over the whole `.bib` at
the end, and report which entries were confirmed, which were corrected, and which
could not be found.

## Citation grammar: what a phrasing promises

The phrasing is not free choice; each form makes a different claim about who
proved what and how reliable the source is. Ordered from strongest attribution:

| form | what it says |
|---|---|
| "Roth proved the conjecture in [Roth]." | The proof is in that paper. |
| "Roth proved the conjecture [Roth]." | Roth proved it; this is the definitive version. |
| "Roth proved the conjecture, see [Roth]." | Roth proved it; [Roth] may be a survey or follow-up. |
| "Roth proved it [Roth], see also [Woolf]." | Woolf made a significant further contribution. |
| "Roth proved it in [Roth] (see also [Woolf])." | Woolf has a complete proof, perhaps fixing minor gaps. |
| "Roth proved it (see [Woolf])." | [Woolf] is the definitive source, e.g. the standard monograph. |
| "..., see e.g. [A, B, C]." | Classical; nobody will check. |
| "Roth claims to have proved it in [Roth]." | There is a known gap. Use deliberately, or not at all. |
| "personal communication" | Someone told you. Get permission first. |

Choose the row that is true. Do not use "see e.g." as a way of avoiding the work
of finding the right reference — a reader can tell.

## Citing a body of work

Never write "see [2–19] for related work". It helps no reader, gives no credit,
and flattens genuinely different contributions into one bracket. Instead, walk the
papers individually, strongest first, saying what each did, and stop when the list
stops being useful:

> Theorem 3 concerns partitions into even primes. The closest result is [A], on
> partitions into primes that are powers of two, which builds on the machinery of
> [B]. In a different direction, [C, D] treat even Fermat primes, and [E] recently
> established a semicircle law in that case under GRH.

In a math paper this discussion belongs in Final Remarks, with only the two or
three most relevant papers in the introduction; in a CS or ML venue it goes in the
introduction or a Related Work section.

## Terminology

- **Do not name what already has a name.** Before introducing a term, check
  whether the object is standard. Reintroducing "quasi-monotone sequences" under a
  new name is the terminological version of rediscovery.
- **Do not lend a source a term it never used.** Naming a construction with an
  established term and hanging a citation on it asserts that the cited work uses
  that term for that object. One real case: a paper called its setup "the
  pinning architecture of [X]" while [X] is a paper on containment control — two
  neighbouring but distinct lines, and the citation credited [X] with a name it
  never used. The same trap catches "the kernel trick of [Y]", "the [Z]
  estimator", "the [W] loss": anyone in the field notices. Either use the term
  the source uses, or describe the object and cite the source for what it
  actually proves. The check is one search and it is not optional: a term of art
  carries an attribution whether or not you intended one.
- **Do not name what does not need a name.** A term is justified when the object
  recurs and the name shortens the exposition. One use does not justify it.
- **If you do name something, define it formally, once, at first use**, mark the
  term with `\emph` there and never again, and keep the exact string thereafter.
- **Do not inflect a defined term.** "nice graph" stays "nice"; there is no
  "niceness".
- Naming a class after a person or place is a legitimate memorability device, but
  attribution sticks: readers will credit the name, not you.
- Abbreviations: expand at first use, then use consistently. Do not introduce an
  abbreviation used fewer than four times.

## Novelty claims

Before any sentence of the form "first", "new", "has not been considered", "unlike
prior work":

1. Search the literature and estimate the size of the relevant body of work.
2. Identify the anchor papers — the two to five that a referee in this area will
   have in mind.
3. Write down, for each anchor, what it proves and what the present result adds:
   a strictly larger class, a weaker hypothesis, a sharper constant, a new proof,
   or a transfer of a known technique to a new setting.
4. Classify the contribution honestly. *Rediscovery* is a defect. *Transporting a
   theorem to another area with a qualitatively new consequence* is a real
   contribution — but the paper must say which one it is and why the transfer is
   not routine.
5. Prefer the specific claim to the sweeping one. "The bound is the first that
   does not depend on the spectral gap" is checkable and defensible; "the first
   comprehensive study" is neither.

If the search cannot be run in the session, say so and mark the claim
`\todo{NOVELTY: unverified}` rather than asserting it.

## What needs a citation and what does not

A change of variables, a substitution, a completion of the square, the
observation that a projector kills a constant — these are steps a reader
reproduces on the page, and citing them reads as insecurity. What does need a
source is any *structural* fact you rely on but do not prove: that a matrix
class is positive definite under a stated condition, that a spectral quantity
has known bounds, that an architecture behaves as assumed. The test: could a
competent reader verify it in three lines? If yes, show the three lines; if no,
cite the place where it is proved.

Two things need a citation whatever their difficulty, because the reason is
credit rather than verification: an idea you took from someone, however easy it
is to re-derive once seen; and an artefact you used — a dataset, a benchmark, a
solver, a corpus — cited as its authors ask to be cited. "Everyone uses it" is
not an exemption; it is the reason the citation is cheap for you and matters to
them.

## Numerical verification of proofs

Every intermediate result that *can* be instantiated gets its own numerical
check before it enters the file — each lemma, each inequality, each explicit
constant, separately, never the theorem as a whole: a single end-to-end check
hides which step is wrong.

Many results cannot be instantiated — an existence statement over an uncountable
family, a claim about all primes, a limit — and for those the protocol below
does not apply. What applies instead is a worked special case, a degenerate
instance, or a sanity check on a consequence that is computable.

Protocol per claim:

1. **Instantiate.** Write the claim as an executable predicate on concrete data.
2. **Random sweep.** Sample the hypothesis space broadly (dimensions, parameters,
   distributions), not one comfortable configuration.
3. **Adversarial sweep.** Boundary and degenerate cases: $n=1$, empty set, equality
   cases, zero eigenvalues, ties, non-generic configurations. This is where wrong
   lemmas fail.
4. **Constants.** If the claim is $\|x\|\le C\rho^k$, check the constant numerically,
   not just the rate; a rate that holds with a constant blowing up in $n$ is a
   different theorem.
5. **Record.** Leave a comment next to the statement:
   `% checked: 1e4 samples, n in [2,200], sigma in [1e-3,1e2]; max violation 3e-14`
   plus the path to the script. This makes the check reproducible and tells a
   future reader what was and was not tested.
6. **A failure is information.** If a lemma fails numerically, the lemma is wrong,
   or the hypotheses are incomplete, or the constant is wrong. Report which
   before rewriting.

**Check the steps that look too simple to check** — in the setup as much as in
the proofs (`experiments.md` collects the experimental cases). The hard steps get verified
because they look hard. The errors live in the easy ones: a change of variables
missing an offset, a normalisation off by a factor, a counting formula whose
realised value differs from the nominal one. Each is three lines of code and
each is a public correction if wrong, and a test suite will not catch any of
them — the code implements what the author believed.

## Owning generated code

The same discipline applies to an implementation, not just to a statement, and
it is what decides whether generated code is yours (`disclosure.md`). **Code is
judged by whether your evidence covers its failure modes, not by whether you
read it.** There are three routes, and they catch different things:

- **Comparison against something you already hold** — a figure against the data
  file it rendered, a summary against the raw numbers. Cheap, and sufficient
  where the failure would be visible in the output: a rendering script that
  draws a finished results file is owned once the picture has been checked
  against the file, and reading its source adds nothing.
- **Testing against ground truth** — a closed form, a published benchmark table,
  a reference implementation, a conserved quantity, an invariant, a round trip
  through the inverse, a limiting case with a known answer, a convergence order
  the theory predicts. This is the strongest evidence available for numerical
  code, because it catches the failures you did not anticipate, which is exactly
  the set a code review misses.
- **Reading** — the weakest of the three, and good at one class: the code does
  not do what the specification says.

A transformation that produces new numbers with nothing to compare against — a
cleaning pipeline, a filter, a resampler — is unowned until one of the first two
routes has been taken. Its failures (3% of rows silently dropped, the outliers
your claim depends on clipped away) produce entirely plausible output.

Two limits:

- **A test owns only the behaviour it exercises.** Passing at $n \le 100$ says
  nothing about the $n = 10^4$ you report. The sweep ranges belong in the record
  next to the result.
- **Testing does not catch a correct implementation of a wrong specification.**
  The code does exactly what you asked and what you asked is not what the paper
  claims. That one is caught by reading, or by deriving the expected answer
  independently and finding it disagrees. Where the result is load-bearing, do
  both.

Corollary worth enforcing by construction: **keep computation out of rendering
scripts**. Aggregation, binning, smoothing, NaN handling and error bars live
upstream; the figure script reads a results file and draws it. Then the numbers
in the figure are the numbers in the table, and the script is checkable by
inspection.

Do not present the numerical checks as part of the proof in the paper — they are
evidence for the author, not for the reader. What may appear in the paper is a
separate numerical section, written in the language of the `numerically checked`
ledger row.

## When choices have to be made

Sweep instead of asking, where a sweep is possible. If it is unclear whether a
result should be stated for synthetic or real data, do both, in that order; if the
form of a misspecification matters, run the family rather than picking one. Reserve
questions for the choices that are genuinely the author's: what the paper claims,
which venue, what to leave out.
