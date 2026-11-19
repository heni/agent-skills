# Reporting numbers: uncertainty, tests, tables

Contents: [No bare numbers](#no-bare-numbers) · [Which interval](#which-interval-sd-se-ci-or-range)
· [Resolution before claims](#resolution-before-claims) · [Significant digits](#significant-digits) · [Hypothesis tests](#hypothesis-tests)
· [Multiple comparisons](#multiple-comparisons) · [Marking the best in a table](#marking-the-best-in-a-table)
· [Figures and error bars](#figures-and-error-bars) · [Rates and fits](#rates-and-fits)
· [Verification numbers are different](#verification-numbers-are-different) ·
[Wording](#wording)

## No bare numbers

A measured quantity is reported as **estimate + uncertainty + n**. A table cell
containing `0.847` and nothing else tells the reader nothing about whether
`0.851` in the next column is better, and the referee will ask.

> Over $n = 20$ seeds the method reaches $0.847 \pm 0.006$ (mean $\pm$ 95\% CI)
> against $0.851 \pm 0.009$ for the baseline.

State $n$ — the number of seeds, instances, folds or repetitions — once per
table or figure, in the caption. State what the $\pm$ means in the same place.
A `±` whose meaning is never defined is worse than no `±`.

The exception is a quantity with no sampling variability: a dimension, an
iteration count of a deterministic algorithm, an exact combinatorial value.
Those are reported bare, and it should be obvious from context why.

## Which interval: SD, SE, CI or range

These are four different things and the choice is not cosmetic.

| what you want to say | report | formula |
|---|---|---|
| how much individual runs scatter | sample standard deviation | $s$ |
| how well the mean is pinned down | standard error, or a CI | $s/\sqrt{n}$ |
| a 95% interval for the mean, $n$ large | $\bar{x} \pm 1.96\,s/\sqrt{n}$ | normal approximation |
| the same, $n$ small ($n \lesssim 30$) | $\bar{x} \pm t_{0.975,\,n-1}\, s/\sqrt{n}$ | $t$ multiplier, not 1.96 |
| skewed or heavy-tailed data | median and IQR, or a bootstrap percentile CI | — |
| worst case matters (runtimes, violations) | median with min–max range, or a quantile | — |

**One kind of interval per quantity, across the whole paper.** Different
quantities legitimately take different intervals — a proportion, a mean runtime
and a convergence constant are not summarised the same way. What is not
legitimate is the same quantity appearing with a Clopper--Pearson interval in a
table and a bootstrap bar in a figure: the reader wonders what the difference
hides, and usually it hides nothing. Fix the choice per quantity, name it where
that quantity is first reported, and keep a cross-check interval in the lab
notebook rather than in a caption.

**Clustered trials.** When trials share an instance — the same random graph, the
same subject, the same scene — they are not independent, and a pooled binomial
or $t$ interval is optimistic. Resample whole clusters (a bootstrap over
instances) to check. If they disagree, the clustered interval is the honest one
and the design needs more instances rather than more trials per instance. If
they agree, report whichever your field expects — in subject- or site-based
work that is the clustered one, and reporting the pooled interval because it
came out the same invites the question of why you computed two. The agreement is a property
of the design, not of the method: raise the trials per instance at a fixed
number of instances and the pooled interval drifts optimistic again, so re-check
it whenever the design changes.

Two mistakes are common enough to name:

- **$\pm 1.96 s$ is not a confidence interval for the mean.** It is roughly a
  95% interval for a *single future run*. If the claim is "our method is better
  on average", the relevant interval is $\pm 1.96\, s/\sqrt{n}$, which is
  $\sqrt{n}$ times narrower. Both are legitimate to report; they answer
  different questions, and the caption must say which one is on the page.
- **$n$ is small, so $1.96$ is wrong.** With 5 seeds the two-sided 95%
  multiplier is $2.78$, with 10 it is $2.26$. Using 1.96 at $n=5$ understates
  the interval by 40%.

For timings, throughput and anything with a hard floor and a long right tail,
the mean is a poor summary: report the median and the range, and say so.

For a proportion (accuracy, success rate) over $n$ trials, use a Wilson
interval rather than $\hat{p} \pm 1.96\sqrt{\hat{p}(1-\hat{p})/n}$, which
misbehaves near 0 and 1 and for small $n$.

When the estimator is complicated or the distribution unknown, bootstrap:
resample the runs $B \ge 2000$ times, report the 2.5th and 97.5th percentiles,
and say $B$.

## Resolution before claims

Decide the smallest difference the paper will claim, then size the runs so the
interval is narrower than it. The reverse order produces a specific, common
artifact: a curve that looks saturated because each point's uncertainty swamps
the step between points. A success proportion measured at $\pm0.06$ cannot show
a rise of $0.03$ per step, and reporting that it "plateaus" is a claim the data
does not carry. At $\pm0.02$ the same cells may climb monotonically — the plateau was the
error bar all along.

The design-side consequences — when to profile instead of running longer, and
how this interacts with fixing one setting for the whole paper — are in
`experiments.md`.

Two cases the arithmetic below does not cover. **A systematic floor** —
calibration error, instrument drift, a biased estimator, a fixed discretisation
— does not shrink with $N$, so past a point more repetitions buy nothing and the
honest report is the floor itself, separated from the statistical part.
**Deterministic runs** have no interval at all: a solver on a fixed input
returns what it returns, and an apparent plateau there is round-off, a tolerance
or a mesh, never sampling noise. Diagnose it by varying the tolerance or the
precision, not by running again.

Practical form: for a proportion near $p$, the half-width is about
$2\sqrt{p(1-p)/N}$, so resolving a step $\Delta$ needs roughly
$N\gtrsim4p(1-p)/\Delta^2$ trials per point — at $p\approx0.9$ and
$\Delta=0.03$, about $400$; at $\Delta=0.02$, about $900$. Budget that before
running, and if it is unaffordable, either claim less or make the estimator
cheaper. Profiling is a legitimate way to buy resolution: a constant-factor
speedup in the inner loop converts directly into narrower intervals.

## Significant digits

Print no more digits than the uncertainty supports. If the CI half-width is
$0.006$, the estimate is $0.847$, not $0.8471523$. Rule of thumb: one or two
significant digits in the uncertainty, and the estimate rounded to the same
decimal place.

Within a column, use the same number of decimals in every cell. Mixed
precision in one column is the most visible sign that the numbers were pasted
in by hand from different runs.

## Hypothesis tests

When the paper claims that one method beats another, say so with a test, and
report it completely:

> On the 18 shared instances, the paired Wilcoxon signed-rank test rejects
> equality in favour of the proposed method ($W = 21$, $p = 0.0031$, two-sided);
> the median improvement is $0.9$ points (95\% CI $[0.4, 1.5]$).

Required elements:

1. **Which test, and why it fits.** Paired data (same instances, same seeds,
   both methods) needs a paired test — paired $t$, or Wilcoxon signed-rank if
   normality is doubtful. Independent groups need the unpaired version. Using
   an unpaired test on paired data throws away most of your power.
2. **The null hypothesis**, stated, and whether the test is one- or two-sided.
   One-sided only if the direction was fixed before the data were seen.
3. **$n$** and the test statistic.
4. **The exact $p$-value**: $p = 0.031$, not $p < 0.05$. Thresholds discard
   information; $p = 0.049$ and $p = 0.0002$ are not the same evidence. Below
   $10^{-4}$, $p < 10^{-4}$ is fine.
5. **An effect size with its own interval.** A $p$-value says the difference is
   detectable, not that it matters. The magnitude and its CI say whether anyone
   should care.

Do not run a test that was not planned, and do not report the one test out of
twelve that came out below 0.05 as if it had been the only one. If tests were
exploratory, say so, and treat the result as a hypothesis rather than a finding.

The ASA's statement on $p$-values (Wasserstein & Lazar, *The American
Statistician* 70 (2016), 129–133) is the standard reference for what a
$p$-value is not, and three of its six principles bear directly on how a paper
should be written: a $p$-value is **not** the probability that the hypothesis is
true; conclusions should **not** rest on whether a $p$-value crossed a
threshold; and a $p$-value **does not** measure the size of an effect or the
importance of a result. Which is the argument for reporting an exact $p$
alongside an effect size and its interval, rather than a starred table.

**A non-significant result is not evidence of no difference.** Report the CI:
"the difference is $0.2 \pm 1.1$ points, consistent with no improvement" is a
usable statement; "the difference was not significant" is not.

## Multiple comparisons

Comparing $k$ methods across $m$ datasets produces $k(k-1)m/2$ pairwise tests,
and at $\alpha = 0.05$ roughly one in twenty will fire on noise alone. Correct
for it and say which correction:

- **Holm–Bonferroni** when you need family-wise error control over a modest
  number of comparisons — uniformly better than plain Bonferroni, same
  assumptions, one line of code.
- **Benjamini–Hochberg** when there are many comparisons and controlling the
  false discovery rate is the honest goal.
- **Friedman test followed by a Nemenyi post-hoc** for the standard
  "$k$ methods over $m$ datasets" layout; the critical-difference diagram is the
  conventional way to display it.

This is Demšar's recommendation (*Statistical Comparisons of Classifiers over
Multiple Data Sets*, JMLR 7 (2006), 1–30), which is the reference to cite and
the default to follow: **Wilcoxon signed-rank for two methods, Friedman with a
post-hoc test for more**, both non-parametric, both robust to the fact that
datasets differ wildly in difficulty. The same paper names the practices to
avoid: averaging accuracies across incommensurable datasets, and running
multiple paired $t$-tests without correction. A later refinement replaces
Nemenyi with a Holm- or Bergmann–Hommel-adjusted post-hoc, which is more
powerful at the same error rate.

Report both the raw and the adjusted $p$-values, or state that the reported ones
are adjusted and by what.

## Marking the best in a table

Bold means "this is the best". That claim needs the same support as any other.

**The rule to use**, and to state in the caption verbatim:

> Best result per row in bold; results not statistically distinguishable from
> the best (paired $t$-test, $\alpha = 0.05$, Holm-corrected) are also bold.
> Mean $\pm$ 95\% CI over $n = 20$ seeds.

So: find the best entry, test every other entry against it, and bold everything
the test cannot separate from it. If three methods tie within noise, three
numbers are bold and the reader learns something true. Bolding the highest
number when the top four are within a hair of each other is a claim the data do
not support, and a referee who checks will notice.

Where a test is impossible (one run per cell, no variance estimate), do not bold
at all — or bold and say explicitly that no significance is claimed. Underlining
the runner-up is a common convention and needs the same caption sentence.

Other table hygiene worth the minute it costs: align on the decimal point, give
units in the header rather than in every cell, put the direction of goodness in
the header ($\uparrow$ / $\downarrow$), and never let a table carry a number
that appears nowhere in the text.

## Figures and error bars

Every error bar is defined in the caption: SD, SE, a 95% CI, or an IQR, and
over what $n$. An undefined error bar is a decoration.

For a shaded band around a curve, same rule, and say whether the band is
pointwise or simultaneous — pointwise bands are what everyone plots, and two
curves whose pointwise bands overlap may still differ significantly, so do not
read significance off the picture.

Log-scale axes need the base stated. A broken axis needs to be visibly broken.

## Rates and fits

A claim of the form "the error decays as $n^{-1/2}$" is a fit, and gets fit
discipline: report the estimated exponent with a CI, the range of $n$ over which
the fit was made, and the residual behaviour. Do not read a slope off a log–log
plot by eye and assert it as a rate. Two decades of $n$ is the usual minimum
before an exponent means anything.

If the theory predicts an exponent, say whether the estimated CI contains it.
That is the interesting sentence, and it is often omitted.

## Verification numbers are different

The numerical checks of lemmas described in `evidence.md` are not measurements
and do not take confidence intervals. There the quantity of interest is the
**worst case**: report the maximum violation over the sweep, the number of
samples, the parameter ranges covered, and the tolerance.

> Checked on $10^4$ random instances, $n \in [2, 200]$,
> $\sigma \in [10^{-3}, 10^{2}]$: maximum violation $3\cdot 10^{-14}$,
> consistent with double-precision round-off at the observed condition numbers.

A mean violation is meaningless here — one counterexample refutes the lemma. If
the maximum violation grows with a parameter, that growth is the finding, and it
belongs in the paper.

## Wording

- "Significant" in a paper with statistics means *statistically* significant.
  For magnitude, write "large", "substantial", or give the number. Mixing the
  two senses in one paper is a real ambiguity, not a stylistic quibble.
- "Trending towards significance" and "marginally significant" mean nothing;
  give $p$ and the CI.
- "We observe an improvement of 3 points" needs the interval in the same
  sentence, not two paragraphs later.
- Numerical evidence keeps the `numerically checked` language from the claim
  ledger: "the experiments indicate", "consistent with", "we observe" — never
  "we show", "it follows", "this proves".

`scripts/statcheck.py` mechanically flags the recurring omissions: bare `±`
never defined, `p < 0.05` instead of an exact value, "significant" with no test
nearby, bolded table entries with no significance rule in the caption, columns
with inconsistent decimal places, error bars never defined, and tables whose
cells carry no uncertainty at all.
