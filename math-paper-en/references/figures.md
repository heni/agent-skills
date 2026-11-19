# Figures and tables

Distilled from Rougier, Droettboom & Bourne, *Ten Simple Rules for Better
Figures* (PLoS Comput. Biol. 10(9), 2014), Tufte's *The Visual Display of
Quantitative Information*, and the statistical reporting rules in
`numerics.md` — which govern every number that appears in a figure or table and
are not repeated here.

Contents: [Know the message](#know-the-message) · [Choosing the plot](#choosing-the-plot)
· [Ink and clutter](#ink-and-clutter) · [Colour](#colour) · [Size, type and format](#size-type-and-format)
· [Captions](#captions) · [Tables](#tables-versus-figures) · [Reproducibility](#reproducible-figures)

## Know the message

Before drawing anything, write the one sentence the figure exists to support. If
you cannot, the figure is decoration and belongs in an appendix or nowhere. A
figure that supports two sentences is two figures.

Then decide who reads it. A figure for a specialist referee can be dense; a
figure carrying the paper's headline result will be reproduced in talks and
must survive being projected badly.

## Choosing the plot

The plot type follows from the question, not from what the library makes easy.

| question | plot |
|---|---|
| how does $y$ change with $x$ | line, or scatter with a fitted curve |
| how do a few groups compare | dot plot with intervals; bar charts waste space and force a zero baseline |
| what is the distribution | histogram, ECDF, violin, or the raw points — not mean ± SD alone |
| how do many methods rank across many datasets | critical-difference diagram (Demšar) |
| how do two quantities relate | scatter, with the identity line if that is the comparison |
| what is the structure of a matrix or field | heatmap with a perceptually uniform colourmap |
| how does a quantity scale | log–log with the fitted exponent and its interval |

Do not use a pie chart. Do not use a 3-D bar chart. Do not use a dual $y$-axis:
the reader cannot tell which curve belongs to which scale, and the apparent
crossing point is an artefact of the scaling you chose.

Plot the raw points when there are few enough — twenty runs as twenty dots plus
an interval says more than a bar with a whisker, and it exposes bimodality and
outliers that a summary hides.

## Ink and clutter

Every mark should carry information. Remove: background grids darker than the
data, boxes around the whole plot, tick marks on all four sides, drop shadows,
gradient fills, legends that repeat what a direct label would say, redundant
decimal places on axis ticks.

Prefer labelling curves directly next to the curve over a legend in a corner —
it removes a lookup step for the reader.

Keep axis ranges honest. A truncated $y$-axis magnifies a difference; if you
truncate, break the axis visibly and say so in the caption. Start bar charts at
zero, since the bar's length is the encoding.

## Colour

- **Assume the reader is colourblind and the printer is grayscale.** Roughly 8%
  of male readers cannot separate red from green. Use a colourblind-safe
  qualitative palette (Okabe–Ito, ColorBrewer), and check the figure in
  grayscale before submitting.
- **Encode redundantly.** Colour *and* line style, or colour *and* marker
  shape. Then the figure survives both grayscale and a bad projector.
- **Sequential data needs a perceptually uniform map** — viridis, magma,
  cividis. The rainbow/jet map invents boundaries where the data is smooth and
  hides real structure where it is steep; it is the single most common
  scientific-plotting error.
- **Diverging data needs a diverging map** with the neutral colour at the
  meaningful zero.
- Do not use colour to encode something a position could encode better.

## Size, type and format

- **Design at final print size.** A figure drawn at 20 cm wide and shrunk into a
  single column has 6-point axis labels. Set the figure size in the plotting
  code to the column width and check the output at 100%.
- **Font sizes inside the figure should match the paper's body text**, within a
  point or two. Mismatched fonts across figures are visible on the page.
- **Vector formats** (PDF, EPS) for anything drawn; raster (PNG at ≥300 dpi)
  only for images and for scatter plots with so many points that the vector
  file becomes unusable. Never JPEG a plot — the artefacts land on the axes.
- Small and numerous beats large and few: a reader can compare four 4-cm panels
  on one page but not four half-page figures across three pages. If a figure
  must be huge, move it to an appendix and link it.
- Use the same visual conventions for the same object throughout: if the
  proposed method is blue with circles in Figure 2, it is blue with circles
  everywhere.

## Captions

The caption is read more often than the figure is studied, and often instead of
the surrounding text. It must contain:

1. **What is plotted** — quantity on each axis with units, and what one mark is.
2. **The uncertainty** — what the error bars, band or shading represent (SD, SE,
   95% CI, IQR) and over what $n$. See `numerics.md`; an undefined error bar is
   a decoration.
3. **The conditions** — dimensions, parameters, dataset, anything needed to know
   which experiment this is.
4. **What to notice** — one sentence. Not a repetition of the result section,
   but a pointer: "the two curves separate only beyond $n = 10^3$".

Every figure and table is referenced in the text, and the reference says what to
look at. A float nobody points to will be skipped.

## Tables versus figures

Use a table when the reader needs to read off exact values or when the entries
are not commensurable; use a figure when the message is a shape, a trend or a
comparison. A table with twelve rows that all say "our method is a bit better"
is a figure.

Table hygiene: align on the decimal point, units in the header not in every
cell, direction of goodness in the header ($\uparrow$/$\downarrow$), booktabs
rules rather than vertical lines, no cell carrying a number that appears nowhere
in the text. Bolding rules and significance are in `numerics.md`.

## Reproducible figures

Every figure is generated by a script that is committed alongside the paper, is
named after the figure, and reads a data file rather than embedding numbers.
Then a referee's "please add the $n=50$ case" is a re-run, not a redraw, and the
figure in the camera-ready cannot silently disagree with the figure in the
submission.

Do not hand-edit a generated PDF in a drawing program. If the annotation is
worth having, it goes in the script.

**Keep computation out of the rendering script.** Aggregation, binning,
smoothing, NaN handling, rescaling and the derivation of error bars belong
upstream, in the experiment code, and their result belongs in the data file the
figure script reads. Two payoffs: the numbers in the figure are the numbers in
the table, and the figure script becomes verifiable by inspection -- you check
it by comparing the picture against the file it read. A script that quietly
computes its own error bars cannot be checked that way, and that is precisely
where a caption ends up claiming a confidence interval over a standard
deviation.
