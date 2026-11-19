# Prose: flow that reads like a mathematician wrote it

Contents: [What natural means here](#what-natural-means-here) ·
[Sentence craft](#sentence-craft) · [Paragraphs and transitions](#paragraphs-and-transitions)
· [Tense, voice, person](#tense-voice-person) · [Register](#register-downshift-it) ·
[LLM tells](#llm-tells) · [Vocabulary](#vocabulary) · [Rhythm and burstiness](#rhythm)
· [Structural tells](#structural-tells) · [Russian interference](#russian-interference)
· [How to run an edit pass](#how-to-run-an-edit-pass)

## What natural means here

Not "literary". Mathematical English is a downshifted register: repetitive where
repetition helps, plain where a synonym would cost precision, short-sentenced,
present-tense. A paper that reads like Zinsser wrote it is fine; a paper that
reads like a marketing deck is not; a paper that reads like a model filling in a
template is the failure mode this file exists to prevent.

Two constraints, both real:

- **A large share of your readers are not native speakers**, are skimming, and
  have limited patience. Ten plain *therefore*s beat one *henceforth*.
- **A referee who suspects machine authorship stops trusting the mathematics.**
  That suspicion is triggered by style, not content, and it is expensive.

Neither constraint is served by tricks. Detectors measure surface statistics
(token predictability, sentence-length variance) plus marker vocabulary; they have
substantial false-positive rates, are biased against non-native writers, and no
edit guarantees an outcome. Do not promise a score. Write text that a specialist
would have written, and the surface statistics follow.

## Sentence craft

- **Short sentences by default.** If a sentence needs three clauses, it usually
  needs to be two sentences.
- **Commas mark structure, not breathing.** Every clause and subclause gets commas
  on both sides: "Consider an integer $x$, whose square is 4, and which is
  positive."
- **Avoid semicolons** in the body. They assert a logical connection that is better
  made explicit as a sentence, or by a word like *hence*. (They are fine in lists
  of conditions.)
- **Keep the sentence parseable left to right.** "Smith remarked in a paper about
  the scarcity of data" and "In the theory of rings, groups and other algebraic
  structures are treated" both garden-path the reader.
- **Do not drop `that`** after *assume*, *suppose*, *show*: "Assume that $A$ is a
  group." But never "We have that $x=y$" — write "We have $x=y$."
- **`that` vs `which`**: `which` only after a comma or a preposition, or
  interrogatively. "commas that aren't necessary", not "commas which aren't
  necessary".
- **Put the load-bearing clause last.** Emphasis comes from position, not from
  `\textbf`.
- **Keep sticky words apart.** Unusual or long words stay in the reader's ear;
  don't reuse one twice in a paragraph.
- **Motivate before you assert.** If a reader will ask "why is that true?", answer
  before you tell them why it matters.

## Paragraphs and transitions

- Paragraphs short — three to six sentences. Long blocks discourage reading before
  they are read. But a run of two-sentence paragraphs chops the argument up; vary.
- One idea per paragraph, and the first sentence says which idea.
- Transitions carry logic, not decoration. *Hence*, *therefore*, *so*, *it follows
  that*, *conversely*, *on the other hand*, *in contrast*, *for the same reason*,
  *the point is that* — chosen because they are true of the relation between the
  two sentences.
- Do not open consecutive paragraphs with the same connective. Do not open three
  consecutive sentences with *Thus / Consequently / Therefore*.
- Signposts inside long arguments are cheap and valuable: "We first dispose of the
  degenerate case." "This is where the assumption is used."

## Tense, voice, person

- **Present** for mathematical facts, which do not stop being true: "Lemma 2 gives
  ...", "the map is continuous". Past for what was done in the paper's own
  narrative ("we introduced ... in §2") and for things now known to be wrong.
- Pick present-throughout or sequential-narrative and stay consistent; mixing
  tenses on one subject is jarring.
- **`we`** — author and reader together, the default. Fine for single authors. Not
  a formal substitute for `I`; avoid `I` unless the author's identity matters.
- Active over passive when `we` removes the contortion: "We can now prove the
  following result" beats "The following result can now be proved". Passive is
  correct where the agent is genuinely irrelevant.
- Be humble about your own work: no superlatives, explicit or implied. Let the
  theorem be interesting; do not call it interesting.

## Register: downshift it

- Repetition is not a defect in mathematics. Reusing the same word for the same
  thing is a service; varying it is a hazard.
- Avoid literary vocabulary where plain words exist: *henceforth*, *heretofore*,
  *aforementioned*, *whilst*, *utilize*, *commence*.
- One spelling standard, and let it be the common one (US spelling unless the
  venue says otherwise): *color*, not *colour*.
- No bold or italic emphasis in body prose; reserve `\emph` for a term at its
  definition.
- Humor is allowed only when understanding the joke requires understanding the
  mathematics, and only if it survives a third reading.

## LLM tells

These are the patterns that make a reader think "a model wrote this". Every item
here is also, independently, a writing defect — which is why fixing them is safe.

### Openers and throat-clearing

Delete on sight: *It is worth noting that*, *It is important to note that*, *It
should be emphasized that*, *Notably*, *Importantly*, *First and foremost*, *Last
but not least*, *In order to* (→ *to*), *In today's rapidly evolving landscape*,
*As we have seen*, *It is well known that* (unless you then cite it).

Rewrite, don't just delete, when the sentence needed a connective; usually the
sentence order already carries the logic.

### The closing summary reflex

Models end every section with a sentence restating what the section did
("In summary, we have shown that ..."), and end papers with "In conclusion, this
work ...". A paper needs at most one such recap, at the end of a long proof or a
long section, and it should add the statement in the theorem's notation, not
repeat the section title.

### Symmetric triads

Three parallel items, three parallel clauses, three parallel adjectives, over and
over. Real writing has twos and fours and ones. If a paragraph has a triad, check
whether the third item earns its place or was generated to complete the pattern.

### "Not only X, but also Y" and "It's not X — it's Y"

Both are model reflexes. Prefer a plain sentence: "The bound is also independent
of the dimension."

### Em-dash habit

At most one em-dash per paragraph, and few of those. Commas, parentheses, or a
relative clause do the same work without the signature.

### Hedging clusters

*may potentially*, *could possibly*, *it is generally considered that*. Choose one
hedge or none. In a math paper, either you proved it or you did not.

### Over-signposting

"In this section, we will present the following three contributions." Then a
bulleted list. Then, at the end, "In this section, we presented ...". One
sentence at the start, none at the end.

### Uniform enthusiasm

Every result "significant", every method "robust", every finding "compelling".
Grade your own claims: some results are minor, and saying so is a strength.

## Vocabulary

Words whose frequency in the literature jumped abruptly after 2022 — the
data-driven marker set (Kobak et al., *Science Advances* 2025, on excess
vocabulary in 15M PubMed abstracts) — plus the common workshop list. **These are
flags, not bans.** If the word is a term of art in your context (*spanning* tree,
*integration*, *alignment*, *refinement*, *projection*, *robust* control), keep
it; the audit script excludes math mode but cannot know your field.

Tier A — almost never right in a mathematical paper:

> delve (into), underscore, showcase, pivotal, crucial (as filler), realm,
> landscape, tapestry, journey, embark, groundbreaking, cutting-edge,
> revolutionize, transformative, unparalleled, seamless(ly), holistic,
> multifaceted, intricate, intricacies, nuanced (as filler), meticulous(ly),
> foster, bolster, unveil, unravel, illuminate (as filler), testament to,
> paving the way for, shedding light on, in the realm of, plays a pivotal role,
> a game changer, at the forefront of

Tier B — usually a plainer word is better; keep only when precise:

| flagged | plainer |
|---|---|
| leverage (verb) | use, exploit, apply |
| utilize | use |
| comprehensive | complete, full |
| enhance / augment | improve, increase, strengthen |
| facilitate | allow, make possible |
| encompass | contain, include |
| ensure | guarantee, force |
| demonstrate (of a proof) | show, prove |
| highlight | show, point out |
| significant (non-statistical) | large, substantial — or give the number; in a paper with statistics, reserve the word for its technical sense (see `numerics.md`) |
| robust (as filler) | stable, reliable, or the actual property |
| various / numerous | the number, or *several* |
| methodologies | methods |
| insights | results, observations |
| align with | agree with, match |
| pinpoint | locate, identify |
| streamline | simplify |
| harness | use |

Tier C — density words. Fine once, a tell in bulk: *moreover*, *furthermore*,
*additionally*, *consequently*, *thereby*, *overall*, *notably*. Cap them at
roughly one per two paragraphs and prefer *hence*, *so*, *then*, *but*, *and*.

## Rhythm

Detectors and readers both notice uniformity. Human mathematical prose alternates:
a nine-word sentence, then a thirty-word one carrying a construction, then a
four-word signpost. Model prose sits at 15–25 words per sentence, paragraph after
paragraph.

Targets that correlate with natural text (`audit.py` reports all three):

- sentence-length standard deviation ≥ 8 words, coefficient of variation ≥ 0.45;
- no more than 60% of sentences in the 15–25 word band;
- no run of four consecutive sentences of the same shape (same opener type, same
  length band, same clause count).

Do not manufacture variance by padding. Get it by writing what the argument needs:
short sentences for claims and signposts, long ones for constructions and
conditions.

## Structural tells

- **Bullet lists where prose belongs.** Convert `itemize` runs to connected
  paragraphs unless the content is genuinely enumerable (assumption lists,
  parameter tables, case distinctions). A paper full of bullets reads like slides.
- **Section-shaped uniformity.** Every section the same length with the same
  internal shape (intro sentence, three subsections, summary) is a template
  signature. Sections should be as long as their content.
- **Header stacking.** Do not create a heading for two sentences.
- **Tables of contents in short papers**, **restating the abstract in the
  introduction**, **repeating the contribution list in the conclusion**.

## Context leaks

A paper is read by someone who was not present while it was written. Everything
the reader needs is on the page; nothing on the page should require knowing what
happened off it. The characteristic failure is not a missing definition — those
get caught — but a sentence that answers a question the text never asked.

**The tell is a dangling negation or concession.** "This method does not require
independence." "The construction should not be confused with the one in [12]."
"We do not claim optimality." Read cold, each of these plants a doubt the reader
did not have, and then dispels it. The reader now suspects there is a reason the
author felt the need. Usually there is: a referee said it, a coauthor objected,
the author defended the choice in a meeting — and the defence, not the doubt,
made it into the manuscript.

Other forms of the same leak:

- **Dangling back-references.** "As discussed above", "as we mentioned", "the
  aforementioned issue" — pointing at a conversation rather than at a section.
  Every back-reference resolves to a numbered place in this paper or it goes.
- **Revision residue.** "In the revised version", "we have now added", "as
  requested", "following the reviewer's suggestion", "this addresses the concern
  about". These belong in the response letter; the manuscript states the
  result, not its editorial history. This is the practical reason the response
  is a separate document: **changes go in the paper, arguments go in the
  response.**
- **Private shorthand.** Internal project names, dataset nicknames, "the old
  pipeline", "our previous setup", a variable named after a collaborator's
  suggestion. Meaningful to four people.
- **Accumulated hedges.** Each review round adds a qualifier, none is ever
  removed, and the claim ends up defended against six objections at once and
  asserting nothing.

**The fix.** For every negative, defensive or concessive sentence, find the
sentence in the paper that raises the doubt it answers. Three outcomes:

1. The doubt is raised in the text → keep the answer, and put it near the doubt.
2. A reader would genuinely form the doubt but the text does not raise it → add
   the doubt, in one clause, then answer it. Now it is an argument rather than a
   reflex.
3. Neither → delete the sentence. The objection lived in a conversation, and it
   stays there.

The same test catches the mirror-image defect: an assertion whose justification
lived in the conversation and never reached the page.

## Defensive density

The previous section is about defences with no antecedent. This one is about
their quantity and their location, which is a separate defect: a paper can be
free of leaks and still exhaust the reader by fending off objections for twenty
pages. A reader finishing such a paper remembers what it is not.

**A scientific paper should leave the impression of a positive contribution.**
That is not a matter of tone. Prose dense in negation is measurably harder to
process — each negation is a proposition the reader must construct and then
cancel — and a body section that alternates claim and disclaimer never lets the
argument accumulate.

### Boundary versus defence

They look alike and behave oppositely.

A **boundary** is part of the claim. "The constant is uniform in $n$ but not in
the condition number." "The rate holds for $\alpha \in (0,1/2)$." Without it the
statement is false or vague, so it belongs exactly where the statement is, in
the theorem, the assumption list or the caption. Boundaries are not defensive
even when phrased negatively, and the rule that every positive claim carries its
boundary stands unchanged.

A **defence** answers an objection. "We do not claim optimality." "A full
treatment of the non-convex case is beyond the scope of this work." "This is not
a limitation in practice." Removing it leaves the statement true. These are the
ones that must be rationed and grouped.

The test: delete the sentence. If a theorem becomes false or ambiguous, it was a
boundary — restore it. If only the author's comfort changes, it was a defence.

### Where defences live

- **One designated place.** Limitations, Discussion, or a Final Remarks
  subsection. Stated together, in a paragraph the reader enters knowing what it
  is for, they read as command of the subject. Scattered, the same sentences
  read as anxiety.
- **A Scope paragraph in the introduction**, if the exclusions are large enough
  that a reader would otherwise pick up the wrong paper: two or three sentences,
  once, and never repeated.
- **Legitimately negative mathematics is not in this budget at all.**
  Non-existence theorems, impossibility results, counterexamples, proofs by
  contradiction, statements that a hypothesis cannot be removed, negative
  experimental results — these are contributions, and they are as positive a
  claim as any. "No polynomial-time algorithm exists unless P = NP" is not a
  defensive sentence.

### Symptoms of an overdefended draft

- Every result paragraph ends with a qualification.
- The same limitation appears in the abstract, the introduction, twice in the
  body and again in the conclusion. It goes once, in the designated place, and
  the abstract states it only if it changes what the result is.
- Assumptions are apologised for rather than motivated. "We unfortunately must
  assume" → say what the assumption buys and whether it is known to be
  necessary.
- Accumulated review scar tissue: a qualifier added per round, none removed.

**Prior art, and what is specific here.** Measuring this is old: Hyland's
metadiscourse framework (*Hedging in Scientific Research Articles*, 1998;
*Metadiscourse*, 2005) established hedges and boosters as countable features,
and the corpus literature has been reporting their density by section for
decades — introductions hedge, conclusions boost. Most writing guidance built on
it runs the other way, asking whether a claim is hedged *enough* to match its
evidence, which is a real and separate question (`evidence.md`). What this
section adds is the opposite direction plus one test: the boundary-versus-
defence distinction, decided by whether deleting the sentence falsifies a
statement. The density figure the audit reports is cruder than the linguistic
taxonomy — it counts negations, not hedges — so read it as a pointer to a
section worth rereading, not as a measurement.

**Practical pass.** Collect every defensive sentence in the draft into one list.
Most will merge; several will turn out to say the same thing. Put the survivors
in the designated section, and check that the body still says what was proved.
`scripts/audit.py` measures negation density per section and exempts the
sections where negation is the subject matter.

## Deprecated terminology

A small part of inclusive-language guidance has hardened into venue
requirement, and that part is checked like any other author guideline — page
limits, reference style, template version. The rest is house style that varies
between publishers and changes; this file does not reproduce it.

**Treat as requirements.**

- `master/slave`, `blacklist/whitelist`. The IEEE SA Style Manual deprecates all
  three under IEEE Policy 9.27, and IEEE conferences ask for alternatives. In
  control and multi-agent work the substitutes are the field's own and are more
  precise anyway: **leader/follower**, **primary/secondary**, **driver/driven**,
  **teleoperator/teleoperated**. For lists: **allowlist/denylist**. If you cite
  older work that uses the old term, the citation keeps its title; your prose
  does not have to.
- **Generic `he`.** Every house style has moved off it. Rewrite in the plural
  ("readers who follow this construction will see"), use "the reader" and repeat
  the noun, or use singular *they*. Avoid the clunky repairs — "he or she",
  "s/he", "his/her" — which draw attention to the problem they are solving.
  Mathematical prose usually needs no personal pronoun at all: "one checks
  that", "we obtain", the passive where the agent is irrelevant.

**Treat as house style, and look it up.** Elsevier, Springer Nature, Nature and
the medical journals publish inclusive-language guidance of varying strength;
some ask authors to confirm they have read it. Check the venue's page once, at
the same time you check the length limit. Where human subjects are involved,
sex and gender reporting has its own standard (SAGER) and it is a reporting
requirement, not a style preference.

**Two limits, both of which follow from rules already in this file.**

- **Do not rename a term of art for style reasons.** *Double-blind* review,
  *dummy variable*, *blind deconvolution*, *degenerate* case, *dominated*
  convergence, *abelian*, *sanity check* in numerical analysis — these are the
  field's exact strings, readers pattern-match on them, and substituting them
  costs precision and signals that the author is outside the field. The rule
  against synonymising technical terms applies here unchanged.
- **Do not overcorrect.** Prose visibly assembled from substitutions reads as a
  filled-in checklist, which is the same register defect as the LLM tells above.
  Fix what the venue requires and what is genuinely settled; leave the rest.

## Russian interference

For drafts translated from Russian, and for Russian-speaking authors writing
directly in English. These are the recurring items:

| Russian pattern | Typical wrong English | Write |
|---|---|---|
| Рассмотрим... | Let us consider... (every paragraph) | Consider..., We consider... |
| данный / указанный | the given, the said | this, the |
| В работе показано, что | In the work it is shown that | We show that |
| достаточно большое | sufficiently big | sufficiently large |
| при этом | at that, herewith | and, while, here |
| в качестве | as a quality of | as |
| позволяет получить | allows to obtain | gives, yields |
| является + noun | is being a | is |
| Missing articles | "Consider matrix $A$" | "Consider the matrix $A$" |
| Extra articles | "the mathematics", "the infinity" | mathematics, infinity |
| соответственно | correspondingly (for respectively) | respectively |
| точность | accuracy vs. precision confusion | pick the technical one deliberately |
| условие / состояние | condition (for state) | state, condition — distinguish |
| ведущий / ведомый | master / slave | leader / follower, driver / driven |
| (нет родового местоимения) | generic "he" for the reader | plural, "the reader", or no pronoun |

Also: Russian mathematical prose favors long multi-clause sentences and heavy
passives; both must be broken up in English. Word order carrying emphasis in
Russian must become word choice or position in English, not italics.

Translation procedure: translate for meaning first, ignoring style; then treat the
English as a first draft and run this whole file on it. Do not translate
sentence-by-sentence — that is what makes translated papers read wrong.

## How to run an edit pass

1. **Threshold.** If a passage is already natural — varied rhythm, no marker
   vocabulary, clean logic — leave it alone. Editing for its own sake degrades
   text. This is the rule that most often gets ignored.
2. **Subtract, don't add.** A de-LLM rewrite should be no longer than the
   original. If a fix needs more words, it is a content change (a claim, a
   boundary, evidence) — handle it as one and tell the user.
3. **Never touch protected regions**: math mode, `verbatim`, `\texttt`, paths,
   identifiers, `\label`/`\ref`/`\cite` keys, `siunitx` numbers, LaTeX comments.
4. **Never synonymize a technical term** to satisfy a vocabulary rule. If a
   flagged word is the field's term, it stays.
5. **Read a paragraph aloud** (or at speed, mentally). Monotone means rewrite one
   sentence, not all of them.
6. **Report the changes** as a short list of what and why, so the author can veto.
   Do not silently rewrite an author's voice.
