#!/usr/bin/env python3
"""
Check the statistical reporting in a LaTeX paper.

Flags the omissions that referees ask about and authors forget:

  * numbers reported without any uncertainty (tables of bare cells)
  * a "+/-" whose meaning is never defined (SD? SE? CI? over what n?)
  * "1.96 sigma" used as if it were a confidence interval for a mean
  * thresholded p-values (p < 0.05) instead of the exact value
  * "significant" with no test, p-value or interval nearby
  * bolded / underlined table entries with no rule stated in the caption
  * columns whose cells carry inconsistent numbers of decimals
  * error bars or shaded bands never defined in the caption
  * many comparisons with no multiple-testing correction mentioned
  * n (number of seeds / runs / instances) never stated

Every flag is advisory: a table of exact combinatorial values legitimately has
no error bars, and a deterministic iteration count legitimately has no CI.

Usage:
    python3 statcheck.py main.tex [--no-follow] [--json out.json]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict

TABLE_ENVS = ("table", "table*", "tabular", "tabularx", "longtable", "figure",
              "figure*")

UNCERTAINTY_WORDS = re.compile(
    r"\b(?:standard\s+(?:deviation|error)|std\.?\s*(?:dev)?|s\.?d\.?|s\.?e\.?(?:m\.?)?|"
    r"confidence\s+interval|\d{2}\s*\\?%\s*CI|\bCI\b|interquartile|IQR|"
    r"quartile|percentile|bootstrap|min-?max|range\s+over|median)\b", re.I)

N_STATED = re.compile(
    r"\b(?:n\s*=\s*\d+|\d+\s+(?:seeds?|runs?|repetitions?|replicates?|trials?|"
    r"instances?|folds?|samples?)|over\s+\d+\s+\w+)", re.I)

TEST_WORDS = re.compile(
    r"\b(?:t-?test|wilcoxon|mann-?whitney|friedman|nemenyi|kruskal|"
    r"kolmogorov|shapiro|anova|chi-?squared|binomial\s+test|permutation\s+test|"
    r"bootstrap|sign\s+test|likelihood\s+ratio\s+test|z-?test)\b", re.I)

P_EXACT = re.compile(r"\bp\s*(?:=|\\approx)\s*0?\.\d+|\bp\s*[<=]\s*10\^?\{?-\d")
P_THRESHOLD = re.compile(r"\bp\s*(?:<|>|\\le|\\leq|\\ge|\\geq|&lt;)\s*0?\.\d+")
P_STAR = re.compile(r"\$?\^?\{?\\?\*{1,3}\}?\$?\s*(?:$|[&\\\s])")

SIGNIFICANT = re.compile(r"\bsignifican(?:t|tly|ce)\b", re.I)
NONSTAT_SIG = re.compile(r"\bsignificant(?:ly)?\s+(?:contribution|figure|part|"
                         r"portion|amount|body\s+of)\b", re.I)
VAGUE = re.compile(r"\b(?:marginally\s+significant|trend(?:ing|ed)?\s+"
                   r"tow(?:ards?)?\s+significance|approaching\s+significance|"
                   r"highly\s+significant)\b", re.I)

CORRECTION = re.compile(
    r"\b(?:bonferroni|holm|benjamini|hochberg|false\s+discovery|FDR|"
    r"family-?wise|sidak|corrected\s+for\s+multiple|multiple\s+comparisons?)\b",
    re.I)

ERRORBAR = re.compile(r"\berror\s*bars?\b|\bshaded\s+(?:band|region|area)\b|"
                      r"\bconfidence\s+band\b", re.I)

SIGMA_CI = re.compile(r"1\.96\s*(?:\\,)?\s*(?:\\sigma|\\hat\{?\\sigma|s\b|"
                      r"\\mathrm\{?sd|SD)", re.I)
SE_FORM = re.compile(r"/\s*\\sqrt\s*\{?\s*n|\\sqrt\s*\{?\s*n\s*\}?\s*\)?\s*$|"
                     r"\bstandard\s+error\b|\bs\.?e\.?m?\b", re.I)

BOLD = re.compile(r"\\(?:textbf|mathbf|bf|bfseries|underline|uline)\b")
BOLD_RULE = re.compile(
    r"\b(?:bold|boldface|underlin)\w*\b[^.]{0,200}?"
    r"\b(?:best|significan|not\s+distinguish|indistinguishable|test|"
    r"\\alpha|p\s*[<=])", re.I | re.S)

NUMBER = re.compile(r"(?<![\w.])(\d+\.\d+|\d+)(?![\w.])")
PM = re.compile(r"\\pm|\\mp|±")


# --------------------------------------------------------------------------

class Line:
    __slots__ = ("path", "no", "raw")

    def __init__(self, path, no, raw):
        self.path, self.no, self.raw = path, no, raw

    def where(self):
        return "%s:%d" % (os.path.basename(self.path), self.no)


def strip_comment(s):
    out, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if c == "\\" and i + 1 < n:
            out.append(s[i:i + 2]); i += 2; continue
        if c == "%":
            break
        out.append(c); i += 1
    return "".join(out)


def read_tex(path, follow=True, _seen=None):
    _seen = _seen or set()
    real = os.path.realpath(path)
    if real in _seen:
        return []
    _seen.add(real)
    try:
        raw = open(path, encoding="utf-8", errors="replace").read().splitlines()
    except OSError as exc:
        print("cannot read %s: %s" % (path, exc), file=sys.stderr)
        return []
    base, out = os.path.dirname(path), []
    for i, r in enumerate(raw, 1):
        out.append(Line(path, i, r))
        if not follow:
            continue
        m = re.search(r"\\(?:input|include)\{([^}]+)\}", strip_comment(r))
        if m:
            child = m.group(1).strip()
            if not child.endswith(".tex"):
                child += ".tex"
            cand = child if os.path.isabs(child) else os.path.join(base, child)
            if os.path.exists(cand):
                out.extend(read_tex(cand, follow, _seen))
    return out


def collect_floats(lines):
    """Return [{start, end, lines, body, caption, kind}] for table/figure floats."""
    floats, stack = [], []
    for idx, ln in enumerate(lines):
        body = strip_comment(ln.raw)
        for m in re.finditer(r"\\begin\{([A-Za-z*]+)\}", body):
            if m.group(1) in TABLE_ENVS:
                stack.append({"kind": m.group(1), "start": idx, "lines": []})
        for st in stack:
            st["lines"].append(ln)
        for m in re.finditer(r"\\end\{([A-Za-z*]+)\}", body):
            if m.group(1) in TABLE_ENVS and stack:
                for j in range(len(stack) - 1, -1, -1):
                    if stack[j]["kind"] == m.group(1):
                        st = stack.pop(j)
                        st["end"] = idx
                        st["body"] = "\n".join(strip_comment(x.raw)
                                               for x in st["lines"])
                        cap = re.search(r"\\caption\*?\s*\{(.*)", st["body"], re.S)
                        st["caption"] = cap.group(1)[:1200] if cap else ""
                        floats.append(st)
                        break
    # drop an inner tabular when an enclosing table/figure covers the same rows
    outer = [f for f in floats if f["kind"].startswith(("table", "figure"))
             and not f["kind"].startswith("tabular")]
    kept = []
    for f in floats:
        if f["kind"].startswith(("tabular", "longtable")) and any(
                o is not f and o["start"] <= f["start"] and f["end"] <= o["end"]
                for o in outer):
            continue
        kept.append(f)
    kept.sort(key=lambda f: f["start"])
    return kept


def column_decimals(body):
    """Per-column decimal-place counts inside a tabular body."""
    cols = defaultdict(Counter)
    for row in re.split(r"\\\\", body):
        if "&" not in row or "\\begin" in row or "\\end" in row:
            continue
        for c, cell in enumerate(row.split("&")):
            cell = re.sub(r"\\[a-zA-Z]+", " ", cell)
            nums = re.findall(r"\d+\.(\d+)", cell)
            if len(nums) == 1:
                cols[c][len(nums[0])] += 1
    return cols


# --------------------------------------------------------------------------

def check(lines, rep):
    text = "\n".join(strip_comment(l.raw) for l in lines)

    # ---- p-values ---------------------------------------------------------
    thresholded, exact = [], 0
    for ln in lines:
        b = strip_comment(ln.raw)
        if P_THRESHOLD.search(b) and not re.search(r"p\s*<\s*10", b):
            thresholded.append((ln.where(), b.strip()[:95]))
        exact += len(P_EXACT.findall(b))
    rep["p_thresholded"] = thresholded
    rep["p_exact_count"] = exact

    # ---- "significant" without support ------------------------------------
    loose = []
    for i, ln in enumerate(lines):
        b = strip_comment(ln.raw)
        if not SIGNIFICANT.search(b) or NONSTAT_SIG.search(b):
            continue
        window = " ".join(strip_comment(x.raw)
                          for x in lines[max(0, i - 3):i + 4])
        if not (TEST_WORDS.search(window) or P_EXACT.search(window)
                or P_THRESHOLD.search(window) or UNCERTAINTY_WORDS.search(window)):
            loose.append((ln.where(), b.strip()[:95]))
    rep["significant_unsupported"] = loose

    rep["vague_significance"] = [
        (l.where(), strip_comment(l.raw).strip()[:95])
        for l in lines if VAGUE.search(strip_comment(l.raw))]

    # ---- 1.96 sigma used as a CI for a mean -------------------------------
    sigma_ci = []
    for i, ln in enumerate(lines):
        b = strip_comment(ln.raw)
        if SIGMA_CI.search(b):
            window = " ".join(strip_comment(x.raw)
                              for x in lines[max(0, i - 2):i + 3])
            if not SE_FORM.search(window):
                sigma_ci.append((ln.where(), b.strip()[:95]))
    rep["sigma_as_ci"] = sigma_ci

    # ---- tests present but no correction ----------------------------------
    n_tests = len(TEST_WORDS.findall(text))
    rep["n_test_mentions"] = n_tests
    rep["correction_mentioned"] = bool(CORRECTION.search(text))

    # ---- is n ever stated -------------------------------------------------
    rep["n_stated"] = bool(N_STATED.search(text))

    # ---- what does the +/- mean -------------------------------------------
    rep["pm_used"] = bool(PM.search(text))
    rep["pm_defined"] = bool(UNCERTAINTY_WORDS.search(text))

    # ---- floats -----------------------------------------------------------
    float_issues = []
    for fl in collect_floats(lines):
        where = "%s:%d" % (os.path.basename(fl["lines"][0].path),
                           fl["lines"][0].no)
        body, cap = fl["body"], fl["caption"]
        probs = []

        if fl["kind"].startswith(("table", "tabular", "longtable")):
            has_pm = bool(PM.search(body))
            n_numbers = len(NUMBER.findall(re.sub(r"\\[a-zA-Z]+", " ", body)))
            if not has_pm and n_numbers >= 8 and not UNCERTAINTY_WORDS.search(cap):
                probs.append("cells carry no uncertainty (%d numbers, no \\pm, "
                             "caption does not name an interval)" % n_numbers)
            if has_pm and not UNCERTAINTY_WORDS.search(cap):
                probs.append("\\pm in the table but the caption never says "
                             "what it is (SD? SE? CI? over what n?)")
            if BOLD.search(body) and not BOLD_RULE.search(cap):
                probs.append("bold/underline used but the caption states no rule "
                             "(best only, or everything indistinguishable from best?)")
            if not N_STATED.search(cap) and (has_pm or BOLD.search(body)):
                probs.append("n (seeds / runs / instances) not stated in the caption")
            if P_STAR.search(body) and "*" not in cap:
                probs.append("asterisks in cells with no legend in the caption")
            for c, counts in column_decimals(body).items():
                if len(counts) > 1 and sum(counts.values()) >= 3:
                    probs.append("column %d mixes decimal places: %s"
                                 % (c + 1, dict(counts)))

        if fl["kind"].startswith("figure"):
            if ERRORBAR.search(cap) and not UNCERTAINTY_WORDS.search(cap):
                probs.append("error bars / band mentioned but not defined")

        if probs:
            float_issues.append((where, fl["kind"], probs))
    rep["float_issues"] = float_issues
    return rep


def render(rep):
    o = ["STATISTICAL REPORTING CHECK", "=" * 27, ""]

    def block(title, body):
        o.append(title); o.append("-" * len(title))
        o.extend(body or ["  clean"]); o.append("")

    lines = []
    if rep["p_thresholded"]:
        lines.append("  thresholded p-values -- report the exact value:")
        for w, frag in rep["p_thresholded"][:12]:
            lines.append("      %-22s %s" % (w, frag))
    if rep["p_exact_count"]:
        lines.append("  exact p-values found: %d" % rep["p_exact_count"])
    if rep["n_test_mentions"] and not rep["correction_mentioned"]:
        lines.append("  ! %d statistical tests mentioned, no multiple-comparison "
                     "correction named" % rep["n_test_mentions"])
        lines.append("    (Holm-Bonferroni, Benjamini-Hochberg, or say why none "
                     "is needed)")
    block("1. p-values and tests", lines)

    lines = []
    for w, frag in rep["significant_unsupported"][:12]:
        lines.append("  %-22s %s" % (w, frag))
    if lines:
        lines.insert(0, "  'significant' with no test, p-value or interval within "
                        "3 lines:")
    for w, frag in rep["vague_significance"][:8]:
        lines.append("  %-22s vague: %s" % (w, frag))
    block("2. Use of 'significant'", lines)

    lines = []
    if rep["sigma_as_ci"]:
        lines.append("  1.96*sigma used with no standard error in sight --")
        lines.append("  a CI for the MEAN is 1.96*s/sqrt(n); 1.96*s is a spread")
        lines.append("  interval for a single run. Say which one you mean:")
        for w, frag in rep["sigma_as_ci"][:8]:
            lines.append("      %-22s %s" % (w, frag))
    if rep["pm_used"] and not rep["pm_defined"]:
        lines.append("  ! the paper uses +/- but never names the quantity "
                     "(SD, SE, CI, IQR)")
    if not rep["n_stated"]:
        lines.append("  ! n (seeds / runs / instances) is never stated anywhere")
    block("3. Uncertainty", lines)

    lines = []
    for where, kind, probs in rep["float_issues"]:
        lines.append("  %-22s (%s)" % (where, kind))
        lines.extend("      %s" % p for p in probs)
    block("4. Tables and figures", lines)

    o.append("Advisory. Exact combinatorial values and deterministic counts")
    o.append("legitimately carry no uncertainty; say so rather than leaving it open.")
    return "\n".join(o)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tex")
    ap.add_argument("--no-follow", action="store_true")
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    lines = read_tex(a.tex, follow=not a.no_follow)
    if not lines:
        sys.exit("nothing to check")
    rep = {}
    check(lines, rep)
    print(render(rep))
    if a.json:
        json.dump(rep, open(a.json, "w", encoding="utf-8"), indent=2,
                  ensure_ascii=False)


if __name__ == "__main__":
    main()
