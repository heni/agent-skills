# Experiments that survive review

Read this before the first production run, not after. Each rule below is a
re-run someone did because a referee — or a coauthor reading the draft — asked a
question the setup could not answer.

The rules are about the relation between a measurement and the claim it
supports, so they do not depend on the field. The concrete instances do: they
come from papers whose measurements are simulations with tunable nuisance
parameters, and they are marked where they appear. Read an instance as one
shape the failure takes, and translate it — the nuisance parameter that has to
be swept is a contrast in one paper, a noise level in another, a class
imbalance, a mesh size, a temperature. What does not translate is the excuse
that your field is different: if a *measurement* in the paper came from a run,
every rule here applies to it.

One class is deliberately outside: numbers produced to check a proof — a lemma
swept over random instances, a constant verified numerically. Those are
verification, not measurement; they are reported as a worst case over what was
tried, carry no interval, and answer to `evidence.md` instead. A paper whose
only numbers are of that kind can skip this file.

Contents: [The viability pass](#the-viability-pass) · [Report the rig](#report-the-rig)
· [One setting per paper](#one-setting-per-paper) · [Resolution before claims](#resolution-before-claims)
· [Free knobs get swept](#free-knobs-get-swept) · [Fixed-budget comparisons](#fixed-budget-comparisons)
· [Reproducibility of the setup, not just the seed](#reproducibility-of-the-setup-not-just-the-seed)
· [Verify the trivial steps](#verify-the-trivial-steps) · [What stays in the lab notebook](#what-stays-in-the-lab-notebook)

## The viability pass

Before any sweep, walk the setup once asking two questions about every quantity
the method consumes:

1. **Who knows this, and from where?** A quantity that only the simulator knows
   is an oracle. Oracles are allowed in an analysis — they are not allowed in the
   experiment that claims practicality. Typical smuggled oracles: a noise level
   the estimator "subtracts", a reference signal every agent "receives", a
   covariance the deployment would have to estimate from data.
2. **Is the steady state the one the paper talks about?** A model whose
   equilibrium is degenerate — nothing moves, nothing drifts, no load — makes the
   measured quantity meaningless even when the arithmetic is right.

Both failures are invisible to tests: the code is correct, the numbers are
reproducible, and the experiment answers the wrong question. The cost of finding
them late is the whole experimental section.

A useful discipline: write the "what an agent/sensor/node actually has" list into
the experiment README before coding, and make the code read from that list. If a
step needs something not on it, that is the design problem surfacing early.

## Report the rig

Anything a reader would need to rebuild the experiment belongs in the paper, in
one paragraph, and it is longer than most authors expect. What fills it depends
on where the numbers come from:

- **Simulation.** How instances were generated (distribution, size, any
  rejection or admissibility condition and how often it fired); the structural
  parameters and the rule that set them — a radius chosen so each node sees
  about $3d$ others is informative, a radius of $0.098$ is not; the protocol or
  schedule, and what makes the resulting object the one the theory assumes.
- **Learned models on data.** Splits and how they were drawn; preprocessing; the
  hyperparameter search space, its budget, and the same budget for every method
  compared; the checkpoint or stopping criterion; the number of seeds and what
  is varied across them; the hardware and the compute actually spent.
- **Physical measurement.** Instrument and its settings; calibration, its date
  and what it is traceable to; the order in which conditions were run and
  whether it was randomised or blinded; environmental controls; units and the
  reference they are quoted against.
- **Numerical methods.** Discretisation and mesh or step size; solver
  tolerances and stopping rules; the arithmetic precision; the linear-algebra
  backend and thread count; and, whenever a timing is reported, exactly what
  lies inside the timed region.

Common to all four: the sample size per estimate and the number of independent
instances; every level of every nuisance parameter, and which of them the method
is allowed to know; and the realised quantities, not only the nominal ones. A
nominal setting and what the run produced differ more often than authors expect
— a requested sparsity against the sparsity drawn, a target acceptance rate
against the observed one, a nominal number of links per node against the mean
degree realised. Print both, and say which one the symbol in the text means.

The test for the paragraph: hand it to someone with the code and no access to
you. Every number they would have to ask about is a defect.

## One setting per paper

Sweeps drift. A parameter fixed in April is silently different from the same
parameter in June, and the two tables stop being comparable — which nobody
notices until a referee lines them up. Before the final runs, freeze one setting
for the whole paper: protocol, nuisance levels, sample size, estimator. Then
re-run everything that goes into a table under it, even the cells that "cannot
have changed".

When a table must show two regimes (with and without a nuisance, two
architectures), run them on **shared draws** if you intend to say so, and check
the seed streams before writing "the same instances": sharing a random seed base
is not sharing draws if the two workers consume the stream differently. Either
pair them properly or say only what is true — "the same instances and the same
grid" is a weaker claim that costs nothing to defend.

## Resolution before claims

Decide the smallest difference the paper will claim, then size the runs so the
interval is narrower than it. Doing it the other way round produces a curve that
looks saturated when the plateau is the error bar. The sample size this implies,
and the arithmetic behind it, are in `numerics.md`; the design consequence is
here.

**Profiling buys resolution.** If the estimator is the expensive part, a
constant-factor speedup in its inner loop converts one-for-one into narrower
intervals at the same wall clock — often a better investment than a longer run,
and sometimes the difference between a claim you can make and one you cannot.

## Free knobs get swept

If the setup has a knob nobody fixed on physical grounds — a contrast, a
signal-to-nuisance ratio, a horizon — do three things in order:

1. **Find the invariance.** Often only a combination matters — a ratio, a
   dimensionless group, a normalised size. Check it numerically on the quantity
   you report, at the tolerance that quantity deserves: a decision (a recovered
   support, a selected model) can agree exactly, while a float agrees to
   rounding, not bit for bit. If the invariance holds, the knob is
   one-dimensional and the paper should say so.
2. **Sweep it** rather than picking a value, and record the sweep before the
   final runs.
3. **Pick the operating point by a stated rule** — the smallest value that meets
   the target, say — and print the rule next to the number. Where the sweep is
   over instances you will also report on, choose on held-out instances (a
   validation split, a separate seed block, a pilot set): selecting a value
   against the numbers in the table is tuning on the test set, whatever the
   field calls it. A reader who sees a
   bare "the signal is $10^3$ times the nuisance" wonders what happened at
   $10^2$; a reader who sees "at $10^2$ no practical sample size recovers" knows.

Scaling a knob with the problem size to keep results flat — making the signal
stronger as the instances get harder — is a design choice a referee will read as
tuning unless it has a reason outside the results. One honest reason does exist: a
success criterion that is an AND over $k$ items — every element of a set
recovered, every constraint satisfied, every frame tracked — falls with $k$ even
when each item is exactly as hard as before. That is an artefact of the metric,
not of the difficulty, and the cure is to report the per-item figure alongside
it, not to make the items easier as $k$ grows.

## Fixed-budget comparisons

When configurations differ in what they consume, hold the total fixed and vary
the split. Twice the observation time is not an improvement; twice the
observation time spent differently is the interesting comparison. Say the budget in the
caption: "a fixed budget $B=RT$, spent as $R$ repetitions of $T$ samples each".

This is also how a nuisance turns into a result. A condition that the deployment
cannot avoid — an environment that keeps changing between runs, a device that
must be recalibrated, a stream that arrives in chunks — is usually written up as
something the method survives. Held at a fixed budget it can instead be shown to
pay: the varying condition supplies diversity the single long run does not. Only
with the budget fixed, though; otherwise the plot measures nothing but the
larger budget.

## Reproducibility of the setup, not just the seed

Seeds are the easy half. The hard half is that every *structural* parameter must
be recorded with the run, and must be a parameter, not a module constant that
someone edits mid-campaign. If a constant changes while a campaign is running,
earlier stages stop reproducing under an indistinguishable configuration — the
worst failure mode there is, because nothing errors.

- Write the full parameter set into the run's first log record.
- Give legacy stages their old value explicitly, so re-running them reproduces
  what they wrote.
- Re-derive one logged cell from the current code as a gate before publishing
  numbers from a campaign that spans code changes.

## Verify the trivial steps

The protocol for checking a claim numerically is in `evidence.md`, and it
applies to the setup as much as to the proofs: the errors live in the steps that
look too simple to check. Two examples from one control-theory
manuscript, both three lines of code away from being caught and neither visible
to a test suite: an error coordinate defined against the wrong reference point,
so that its stationary mean carried the target configuration rather than the
error; and a sampling protocol whose realised mean degree ran $70\%$ above the
nominal one, so the symbol $d$ in the text named neither. The pattern
generalises past this example — the code implements what the author believed,
and the belief is what goes unchecked.

## After a length pass, re-check the claims

Cutting for a page limit edits claims, not only words. A dropped adjective turns
"no placement recovers *every* source" into a false statement; a dropped clause
turns "at $s=4$ the rate reaches $0.95$ at $4\%$" into a table-wide claim that
fails at $s=8$; a compressed caption turns a subsample into "a separate pool".
Those are three real defects from one page-fitting pass, all introduced by
cutting words.

Treat the length pass as a content edit: after it, re-read every sentence you
touched against the table it summarises, and re-run the numbers check. The
mechanics of measuring a page limit are in `structure.md`.

## What stays in the lab notebook

Not every measurement earns a line in the paper. A second interval computed as a
cross-check, a sensitivity curve that came out flat, the timing of a component,
the sample size needed by an alternative estimator — these belong in the
experiment's README or theory file, where they are ready for a rebuttal, and out
of the text.

When one of these leaks into the paper it arrives as a sentence answering a
question the reader never asked; `prose.md` has the tell and the cure. Cut it —
the reader who does ask is answered from the notebook.

What the notebook owes the paper is separate from what the reproducibility
artefact owes the reader: the rig paragraph above is what goes in the text,
while seeds, run counts, compute budget and hardware travel with the artefact
(`lifecycle.md`).
