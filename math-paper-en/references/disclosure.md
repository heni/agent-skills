# Disclosing AI assistance

Read before submitting anything written with a model in the loop. The venue's
current author guidelines override this file; policies change yearly.

## Settled everywhere

A language model **cannot be an author** — ICMJE, COPE, Nature, Science,
Elsevier, Springer, IEEE, ACM and the ML conferences agree, because a model
cannot take responsibility for the work or approve the final version. The human
authors remain **fully responsible for every claim, proof, citation and number**,
however the text was produced.

## The line this skill draws

Disclosure tracks **where the scientific content came from**, not whether a tool
was present. Not "did a model touch this file" but "who originated the result,
and can the author reconstruct and defend it".

**Tier 1 — instrumental, no separate disclosure needed.** The human owns the
theory, designed the experiments, and directed and inspected the work
continuously; the model drafted or edited prose, restructured paragraphs,
tightened statements, formatted LaTeX, or wrote code whose failure modes the
author's evidence covers (`evidence.md`, "Owning generated code"). Removing the
model would change the wording, not the content. This is what a copy editor, a
compiler or a CAS does.

**Tier 2 — contributory, disclose it.** The model ran experiments or drove the
experimental loop; cleaned, filtered, labelled or repaired data, or made the
decisions behind that; selected or implemented an algorithm; proved a theorem,
found a proof step or supplied a lemma; or produced results the author has not
independently verified. The provenance of the science is then partly the
model's. Computer-assisted proofs have been declared as such since the Four
Colour Theorem, for the same reason.

**The test.** *Can you reconstruct and defend every step without the model, and
do you hold evidence adequate to the failure modes of what it produced?* If no,
it is Tier 2, however continuous the supervision felt. "I directed it closely"
is not the criterion; "I verified it and could have done it myself" is.

Two edges:

- **Finding a proof and checking a proof are different acts.** A model that
  reformatted your argument is Tier 1; one that supplied the step you were stuck
  on is Tier 2 even after you verified it — verification makes the result
  *correct*, not *yours*.
- **Literature search** is Tier 1 only because this skill already requires every
  reference to be verified against a real record. Without that, it is Tier 2 and
  worse.

## Where this meets venue policy

**Agrees.** ACL treats assistance purely with the language of the paper —
paraphrasing or polishing the author's own content rather than suggesting new
content — like a grammar checker, and separates it from new ideas, new text,
literature search and data manipulation. Elsevier's writing policy explicitly
excludes the research process from its scope. The criterion "disclose when the
assistance exceeds that of a typical editing service" appears in the
methodological literature.

**Disagrees.** Elsevier, Springer Nature, Science and Wiley require a
declaration for generative language polishing too — naming the tool, the purpose
and the extent of author oversight, placed immediately before the references.
Their carve-out covers spelling and grammar checkers and reference managers, not
language models. Under those policies Tier 1 still needs a sentence.

**So:** the venue wins on compliance; the tier rule tells you where the real
line of intellectual responsibility lies and what the statement should say.
**When in doubt, disclose** — a declaration costs two lines, an undisclosed
declarable use is a policy violation and the sanction lands on the human.

## Writing the statement

> The authors used a large language model to assist with drafting and editing
> the English text and with generating plotting code. All mathematical content,
> proofs, experimental design and numerical results are the authors' own; the
> authors verified every reference and every reported number, and take full
> responsibility for the content.

Adjust to what actually happened. For Tier 2 use, name the task specifically —
"an LLM implemented the baseline in §5.2, whose output was checked against the
reference implementation" — rather than a blanket sentence: a vague disclosure
invites the referee to imagine the worst case. Do not attribute your own error
to a model either.

## De-LLM editing is not concealment

The rules in `prose.md` exist because model-flavoured writing is bad writing.
Removing it improves the paper, and doing so while declaring the assistance is
honest. Using that editing *in order to hide* assistance a venue asks you to
declare is not, and no rule in this skill supports it.
