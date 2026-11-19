#!/usr/bin/env python3
"""
Mechanical audit of an English mathematical paper in LaTeX.

Reports, with line numbers:
  * LLM-marker vocabulary (tiers A/B/C), math mode excluded
  * terminology deprecated by venue style manuals, and generic 'he'
  * throat-clearing phrases and model-reflex constructions
  * defensive density: negations per 100 words by section, with the
    sections whose subject is negation exempted
  * context leaks: revision residue, dangling back-references,
    defensive negations answering a doubt the text never raises
  * sentence-length uniformity (sd, coefficient of variation, band share, runs)
  * em-dash and transition-word density
  * sentences opening with a symbol; adjacent formulas with no word between
  * colon before a display that completes the sentence
  * free-symbol usage and collisions (bound/dummy variables excluded)
  * confusable glyphs
  * undefined / unused \\label, \\cite keys missing from the .bib (or, with a
    hand-written thebibliography, from the \\bibitem keys), uncited entries
  * leftover \\todo, "it can be shown", "clearly", and similar gap-fillers
  * bullet-list density

Flags are advisory. A flagged word may be a term of art; the script excludes math
mode but knows nothing about your field.

Usage:
    python3 audit.py main.tex [--bib refs.bib] [--no-follow] [--json out.json]
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import statistics
import sys
from collections import Counter, defaultdict

# --------------------------------------------------------------------------
# vocabulary
# --------------------------------------------------------------------------

TIER_A = [
    "delve", "delves", "delved", "delving", "underscore", "underscores",
    "underscored", "underscoring", "showcase", "showcases", "showcased",
    "showcasing", "pivotal", "realm", "realms", "landscape", "tapestry",
    "groundbreaking", "cutting-edge", "revolutionize", "revolutionizes",
    "revolutionizing", "transformative", "unparalleled", "seamless",
    "seamlessly", "holistic", "multifaceted", "intricate", "intricately",
    "intricacies", "meticulous", "meticulously", "foster", "fosters",
    "fostering", "bolster", "bolsters", "bolstering", "unveil", "unveils",
    "unveiling", "unravel", "unravels", "unraveling", "unravelling",
    "testament", "burgeoning", "myriad", "plethora", "paramount",
    "invaluable", "commendable", "noteworthy", "impactful", "elucidate",
    "elucidates", "elucidating", "harnessing", "spearhead", "spearheading",
]

TIER_A_PHRASES = [
    "delve into", "delve deeper", "shed light on", "shedding light on",
    "paving the way", "pave the way", "in the realm of", "a testament to",
    "plays a pivotal role", "play a pivotal role", "plays a crucial role",
    "at the forefront of", "a game changer", "game-changer",
    "in today's rapidly", "ever-evolving", "rich tapestry",
    "navigate the complexities", "unlock the potential", "harness the power",
]

TIER_B = {
    "leverage": "use, exploit, apply",
    "leverages": "uses, exploits",
    "leveraging": "using, exploiting",
    "utilize": "use",
    "utilizes": "uses",
    "utilized": "used",
    "utilizing": "using",
    "comprehensive": "complete, full",
    "enhance": "improve, strengthen",
    "enhances": "improves",
    "enhanced": "improved",
    "enhancing": "improving",
    "augment": "increase, extend",
    "facilitate": "allow, make possible",
    "facilitates": "allows",
    "encompass": "contain, include",
    "encompasses": "contains",
    "encompassing": "containing",
    "methodologies": "methods",
    "insights": "results, observations",
    "pinpoint": "locate, identify",
    "streamline": "simplify",
    "harness": "use",
    "crucial": "important, essential -- or say why",
    "vital": "important, necessary",
    "robustly": "reliably -- or the actual property",
    "significantly": "give the number",
    "substantially": "give the number",
    "various": "give the number, or 'several'",
    "numerous": "many, or the number",
    "compelling": "convincing, strong",
    "nuanced": "subtle, or be specific",
    "align": "agree, match (unless alignment is a term of art)",
    "aligns": "agrees, matches",
}

TIER_C = [
    "moreover", "furthermore", "additionally", "consequently", "thereby",
    "overall", "notably", "importantly", "essentially", "ultimately",
]

THROAT_CLEARING = [
    "it is worth noting that", "it is worth mentioning", "it is important to note",
    "it is important to mention", "it should be noted that", "it should be emphasized",
    "it is crucial to note", "first and foremost", "last but not least",
    "in order to", "as we have seen", "as mentioned earlier",
    "in this section, we will", "in this section we will",
    "in summary,", "in conclusion,", "to summarize,",
    "it is well known that", "needless to say",
]

REFLEX_PATTERNS = [
    (r"\bnot only\b[^.]{0,120}\bbut also\b", "'not only X but also Y' -- model reflex; use a plain sentence"),
    (r"\bis not (?:just|merely)\b[^.]{0,80}\bit is\b", "'not just X -- it is Y' -- model reflex"),
    (r"\bmay potentially\b|\bcould possibly\b|\bmight potentially\b", "stacked hedges; choose one or none"),
    (r"\bplays? an? (?:key|central|important|significant) role\b", "vague; say what it does"),
    (r"\bwe conduct extensive\b|\bextensive experiments\b", "padding; state what was run"),
    (r"\bdeep(?:er)? understanding\b|\bdeep insights?\b", "vague claim"),
]

GAP_FILLERS = [
    (r"\bit can be shown that\b", "gap-filler: show it or cite it"),
    (r"\bit is (?:easy|easily) (?:seen|shown|verified)\b", "gap-filler: is it? one line of proof is cheaper than a referee report"),
    (r"\bclearly,?\s", "'clearly' -- usually marks the step the referee will question"),
    (r"\bobviously,?\s", "'obviously' -- same"),
    (r"\bit follows (?:immediately|trivially)\b", "state from what"),
    (r"\ba standard argument\b", "name the argument or give it"),
    (r"\bsimilarly,? (?:one|we) (?:can|obtain|get)\b", "check that it really is similar"),
    (r"\bwe omit the (?:details|proof)\b", "acceptable only with a pointer"),
]

NEGATION = re.compile(
    r"\b(?:not|no|nor|never|none|neither|cannot|can't|won't|doesn't|don't|isn't|"
    r"aren't|wasn't|weren't|without|unable|fails?\s+to|failed\s+to|lacks?|"
    r"lacking|nothing|nowhere|nonexistent|impossible|un(?:able|likely))\b", re.I)

# sections where negation IS the subject matter, not defensiveness
NEGATION_EXEMPT = re.compile(
    r"discussion|limitation|final\s+remark|conclusion|open\s+problem|"
    r"counterexample|impossib|scope|threat|future\s+work|related\s+work", re.I)

SECTION_CMD = re.compile(r"\\(?:sub)*section\*?\s*\{([^{}]*)\}")

CONTEXT_LEAKS = [
    (r"\bin the revised (?:version|manuscript|draft)\b|\bwe have now (?:added|included|clarified|revised)\b"
     r"|\bas (?:requested|suggested)\b|\bfollowing the (?:reviewer|referee|editor)"
     r"|\bthe (?:reviewer|referee)(?:'s|s')?\b|\bin response to the (?:comment|concern)",
     "revision residue: belongs in the response letter, not the manuscript"),
    (r"\bas (?:we )?(?:mentioned|discussed|noted|said) (?:above|earlier|before|previously)\b"
     r"|\bthe aforementioned\b|\bas noted above\b",
     "back-reference with no target: point at a numbered section, or cut"),
    (r"\bshould not be confused with\b|\bis not intended to\b|\bwe do not claim\b"
     r"|\bit is not our (?:intention|aim|goal)\b|\bcontrary to what (?:one|the reader) might\b"
     r"|\bthis does not (?:imply|mean) that\b",
     "defensive negation: is the doubt it answers raised anywhere in the paper?"),
]

DEPRECATED = [
    (r"\bmaster[-/ ]?slave\b|\bslave\b(?![a-z])", "master/slave: deprecated by the IEEE SA Style Manual "
     "(Policy 9.27); use leader/follower, primary/secondary, driver/driven"),
    (r"\bmaster\b(?=\s+(?:node|device|clock|process|branch|copy|unit|agent))",
     "'master' in this sense is deprecated; use primary/leader"),
    (r"\bblack\s?list(?:ed|ing|s)?\b", "blacklist: deprecated; use denylist/blocklist"),
    (r"\bwhite\s?list(?:ed|ing|s)?\b", "whitelist: deprecated; use allowlist"),
]

CLUNKY_PRONOUN = [
    (r"\bhe\s+or\s+she\b|\bshe\s+or\s+he\b|\bs/he\b|\bhis[/ ]or[/ ]her\b|\bhis/her\b",
     "clunky pronoun repair; rewrite in the plural or drop the pronoun"),
    (r"\b(?:the\s+reader|the\s+user|the\s+author|a\s+researcher|the\s+practitioner|one)\b"
     r"[^.;]{0,60}?\b(?:he|his|him)\b",
     "generic 'he'; use the plural, repeat the noun, or drop the pronoun"),
]

CONFUSABLES = [
    (r"(?<![\\a-zA-Z])\\epsilon\b", r"\epsilon reads as \in; use \varepsilon"),
    (r"(?<![\\a-zA-Z])\\emptyset\b", r"\emptyset looks like a computer zero; use \varnothing"),
    (r"(?<![\\a-zA-Z])\\iota\b", r"\iota is hard to distinguish from i"),
    (r"(?<![\\a-zA-Z])\\upsilon\b", r"\upsilon looks like v"),
    (r"(?<![\\a-zA-Z])\\kappa\b", r"\kappa looks like k -- acceptable only if k is unused"),
    (r"(?<![\\a-zA-Z0-9])l(?![a-zA-Z])", r"bare 'l' in math reads as 1; use \ell"),
    (r"\*", "'*' as multiplication is programming notation; use juxtaposition or \\times"),
]

VERBATIM_ENVS = {"verbatim", "lstlisting", "minted", "Verbatim", "alltt"}
MATH_ENVS = {
    "equation", "equation*", "align", "align*", "aligned", "gather", "gather*",
    "multline", "multline*", "eqnarray", "eqnarray*", "array", "cases",
    "displaymath", "split", "IEEEeqnarray", "IEEEeqnarray*",
}
LIST_ENVS = {"itemize", "enumerate", "description"}

ABBREV = {
    "e.g.", "i.e.", "cf.", "resp.", "etc.", "vs.", "fig.", "eq.", "sec.",
    "thm.", "prop.", "lem.", "def.", "no.", "vol.", "pp.", "al.", "approx.",
    "st.", "dr.", "prof.", "ch.", "ex.",
}


# --------------------------------------------------------------------------
# loading and stripping
# --------------------------------------------------------------------------

class Line:
    __slots__ = ("path", "no", "raw", "prose")

    def __init__(self, path, no, raw, prose):
        self.path = path
        self.no = no
        self.raw = raw
        self.prose = prose

    def where(self):
        return "%s:%d" % (os.path.basename(self.path), self.no)


def read_tex(path, follow=True, _seen=None):
    """Return a list of Line objects, following \\input and \\include."""
    _seen = _seen or set()
    real = os.path.realpath(path)
    if real in _seen:
        return []
    _seen.add(real)
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            raw_lines = fh.read().splitlines()
    except OSError as exc:
        print("cannot read %s: %s" % (path, exc), file=sys.stderr)
        return []

    base = os.path.dirname(path)
    out = []
    for i, raw in enumerate(raw_lines, 1):
        out.append(Line(path, i, raw, None))
        if not follow:
            continue
        m = re.search(r"\\(?:input|include)\{([^}]+)\}", strip_comment(raw))
        if m:
            child = m.group(1).strip()
            if not child.endswith(".tex"):
                child += ".tex"
            cand = child if os.path.isabs(child) else os.path.join(base, child)
            if os.path.exists(cand):
                out.extend(read_tex(cand, follow, _seen))
    return out


def strip_comment(s):
    out, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if c == "\\" and i + 1 < n:
            out.append(s[i:i + 2])
            i += 2
            continue
        if c == "%":
            break
        out.append(c)
        i += 1
    return "".join(out)


MATH_SPANS = [
    (re.compile(r"\$\$.*?\$\$", re.S), " MATH "),
    (re.compile(r"(?<!\\)\$.*?(?<!\\)\$", re.S), " MATH "),
    (re.compile(r"\\\[.*?\\\]", re.S), " MATH "),
    (re.compile(r"\\\(.*?\\\)", re.S), " MATH "),
]

CMD_ARG_DROP = re.compile(
    r"\\(?:label|ref|eqref|cref|Cref|autoref|pageref|cite[a-zA-Z]*|nocite|"
    r"bibliography|bibliographystyle|usepackage|documentclass|input|include|"
    r"newcommand|renewcommand|DeclareMathOperator|texttt|verb|url|href|"
    r"includegraphics|SI|num|todo)\s*\*?(?:\[[^\]]*\])*(?:\{[^{}]*\})*"
)
CMD_KEEP_ARG = re.compile(r"\\(?:emph|textit|textbf|text|mbox|footnote|caption|section|subsection|subsubsection|paragraph|title)\s*\*?\{")
GENERIC_CMD = re.compile(r"\\[a-zA-Z@]+\s*\*?")


DISPLAY_OPEN = "\\["
DISPLAY_CLOSE = "\\]"


def display_state(body, state):
    """Track multi-line \\[ ... \\] and $$ ... $$ displays.

    Returns (is_math_line, new_state). Balanced same-line displays leave the
    state untouched and are handled by the span substitutions instead.
    """
    if state == "bracket":
        return True, (None if DISPLAY_CLOSE in body else "bracket")
    if state == "dollar":
        return True, (None if "$$" in body else "dollar")
    tail = body
    if DISPLAY_OPEN in tail:
        after = tail.split(DISPLAY_OPEN, 1)[1]
        if DISPLAY_CLOSE not in after:
            return False, "bracket"
    if tail.count("$$") % 2 == 1:
        return False, "dollar"
    return False, None


def build_prose(lines):
    """Fill line.prose with math/markup-free text, and return per-line env state."""
    in_verbatim = None
    in_math_env = None
    in_display = None
    for ln in lines:
        raw = ln.raw
        body = strip_comment(raw)

        if in_verbatim:
            if re.search(r"\\end\{%s\}" % re.escape(in_verbatim), body):
                in_verbatim = None
            ln.prose = ""
            continue
        m = re.search(r"\\begin\{([A-Za-z*]+)\}", body)
        if m and m.group(1) in VERBATIM_ENVS:
            in_verbatim = m.group(1)
            ln.prose = ""
            continue

        if in_math_env:
            if re.search(r"\\end\{%s\}" % re.escape(in_math_env).replace(r"\*", r"\*"), body):
                in_math_env = None
            ln.prose = " MATH "
            continue
        if m and m.group(1) in MATH_ENVS:
            if not re.search(r"\\end\{%s\}" % re.escape(m.group(1)), body):
                in_math_env = m.group(1)
            ln.prose = " MATH "
            continue

        is_disp, in_display = display_state(body, in_display)
        if is_disp:
            ln.prose = " MATH "
            continue

        text = body
        for pat, rep in MATH_SPANS:
            text = pat.sub(rep, text)
        text = CMD_ARG_DROP.sub(" ", text)
        text = CMD_KEEP_ARG.sub(" ", text)
        text = re.sub(r"\\(?:begin|end)\{[A-Za-z*]+\}", " ", text)
        text = GENERIC_CMD.sub(" ", text)
        text = text.replace("{", " ").replace("}", " ").replace("&", " ")
        text = re.sub(r"[ \t]+", " ", text)
        if in_display:
            text = text.split(DISPLAY_OPEN)[0].split("$$")[0] + " MATH "
        ln.prose = text
    return lines


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def prose_blocks(lines):
    """Yield (list_of_lines, joined_text) for each blank-line-separated block."""
    block = []
    for ln in lines:
        if ln.prose is not None and ln.prose.strip():
            block.append(ln)
        else:
            if block:
                yield block, " ".join(b.prose for b in block)
                block = []
    if block:
        yield block, " ".join(b.prose for b in block)


SENT_END = re.compile(r"(?<=[.!?])\s+")


def split_sentences(text):
    parts, buf = [], ""
    for chunk in SENT_END.split(text):
        buf = (buf + " " + chunk).strip() if buf else chunk.strip()
        low = buf.lower().split()
        if low and low[-1] in ABBREV:
            continue
        if buf:
            parts.append(buf)
        buf = ""
    if buf:
        parts.append(buf)
    return [p for p in parts if len(p.split()) >= 2]


def find_words(lines, words):
    """Return {word: [(where, sentence_fragment), ...]}."""
    hits = defaultdict(list)
    lookup = {w.lower(): w for w in words}
    for ln in lines:
        if not ln.prose:
            continue
        for m in re.finditer(r"[A-Za-z][A-Za-z'\-]*", ln.prose):
            w = m.group(0).lower()
            if w in lookup:
                frag = ln.prose.strip()
                hits[lookup[w]].append((ln.where(), frag[:90]))
    return hits


def find_patterns(lines, patterns):
    hits = []
    for ln in lines:
        if not ln.prose:
            continue
        low = ln.prose.lower()
        for pat, msg in patterns:
            if re.search(pat, low):
                hits.append((ln.where(), msg, ln.prose.strip()[:90]))
    return hits


def find_phrases(lines, phrases):
    hits = []
    for ln in lines:
        if not ln.prose:
            continue
        low = " " + re.sub(r"\s+", " ", ln.prose.lower()) + " "
        for ph in phrases:
            if ph in low:
                hits.append((ln.where(), ph, ln.prose.strip()[:90]))
    return hits


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------

def check_vocabulary(lines, rep):
    a = find_words(lines, TIER_A)
    ap = find_phrases(lines, TIER_A_PHRASES)
    b = find_words(lines, list(TIER_B))
    c = find_words(lines, TIER_C)
    rep["tier_a"] = {w: v for w, v in a.items()}
    rep["tier_a_phrases"] = ap
    rep["tier_b"] = {w: v for w, v in b.items()}
    rep["tier_c_counts"] = {w: len(v) for w, v in c.items()}
    rep["tier_c_hits"] = {w: v for w, v in c.items()}


def check_phrasing(lines, rep):
    rep["throat_clearing"] = find_phrases(lines, THROAT_CLEARING)
    rep["reflexes"] = find_patterns(lines, REFLEX_PATTERNS)
    rep["gap_fillers"] = find_patterns(lines, GAP_FILLERS)
    rep["deprecated_terms"] = find_patterns(lines, DEPRECATED)
    rep["context_leaks"] = find_patterns(lines, CONTEXT_LEAKS)
    rep["pronoun_issues"] = find_patterns(lines, CLUNKY_PRONOUN)


def check_negation_density(lines, rep):
    """Negation per 100 words, by section. Defences scattered through the body
    are the target; sections whose subject is negation are exempt."""
    sections, cur = [], {"title": "(front matter)", "words": 0, "neg": 0,
                         "where": lines[0].where() if lines else "?"}
    for ln in lines:
        m = SECTION_CMD.search(strip_comment(ln.raw))
        if m:
            if cur["words"]:
                sections.append(cur)
            cur = {"title": re.sub(r"\\[a-zA-Z]+|[{}]", "", m.group(1)).strip()
                   or "(untitled)",
                   "words": 0, "neg": 0, "where": ln.where()}
        if ln.prose:
            text = ln.prose.replace("MATH", " ")
            cur["words"] += len(text.split())
            cur["neg"] += len(NEGATION.findall(text))
    if cur["words"]:
        sections.append(cur)

    out, flagged = [], []
    for sec in sections:
        if sec["words"] < 80:
            continue
        dens = 100.0 * sec["neg"] / sec["words"]
        exempt = bool(NEGATION_EXEMPT.search(sec["title"]))
        row = {"title": sec["title"], "where": sec["where"], "words": sec["words"],
               "negations": sec["neg"], "per_100w": round(dens, 1),
               "exempt": exempt}
        out.append(row)
        if not exempt and dens > 2.0:
            flagged.append(row)
    rep["negation_by_section"] = out
    rep["negation_flagged"] = sorted(flagged, key=lambda r: -r["per_100w"])


def check_rhythm(lines, rep):
    sentences, para_lengths, emdash_per_para, trans_per_para = [], [], [], []
    for block, text in prose_blocks(lines):
        sents = split_sentences(text)
        if not sents:
            continue
        sentences.extend(sents)
        para_lengths.append(len(sents))
        raw_join = " ".join(b.raw for b in block)
        emdash_per_para.append(raw_join.count("---") + raw_join.count("\u2014"))
        low = text.lower()
        trans_per_para.append(sum(low.count(w) for w in TIER_C))

    lens = [len(s.split()) for s in sentences]
    if len(lens) < 5:
        rep["rhythm"] = {"n_sentences": len(lens), "note": "too few sentences to judge"}
        return

    mean = statistics.fmean(lens)
    sd = statistics.pstdev(lens)
    cv = sd / mean if mean else 0.0
    band = sum(1 for x in lens if 15 <= x <= 25) / len(lens)

    def band_of(x):
        return 0 if x < 12 else (1 if x <= 25 else 2)

    run, best, prev = 1, 1, None
    for x in lens:
        b = band_of(x)
        if b == prev:
            run += 1
            best = max(best, run)
        else:
            run, prev = 1, b

    rep["rhythm"] = {
        "n_sentences": len(lens),
        "mean_len": round(mean, 1),
        "sd_len": round(sd, 1),
        "cv": round(cv, 2),
        "share_15_25": round(band, 2),
        "longest_same_band_run": best,
        "max_sentence": max(lens),
        "min_sentence": min(lens),
        "n_paragraphs": len(para_lengths),
        "emdash_total": sum(emdash_per_para),
        "paras_over_1_emdash": sum(1 for x in emdash_per_para if x > 1),
        "transition_words": sum(trans_per_para),
        "transitions_per_para": round(
            sum(trans_per_para) / max(1, len(para_lengths)), 2),
    }
    rep["rhythm_verdict"] = []
    if sd < 8:
        rep["rhythm_verdict"].append(
            "sentence-length sd %.1f < 8: uniform rhythm" % sd)
    if cv < 0.45:
        rep["rhythm_verdict"].append(
            "coefficient of variation %.2f < 0.45: uniform rhythm" % cv)
    if band > 0.60:
        rep["rhythm_verdict"].append(
            "%.0f%% of sentences are 15-25 words (>60%%): model-typical band" % (band * 100))
    if best >= 4:
        rep["rhythm_verdict"].append(
            "%d consecutive sentences in the same length band" % best)
    if rep["rhythm"]["paras_over_1_emdash"]:
        rep["rhythm_verdict"].append(
            "%d paragraphs with more than one em-dash" % rep["rhythm"]["paras_over_1_emdash"])
    if rep["rhythm"]["transitions_per_para"] > 0.5:
        rep["rhythm_verdict"].append(
            "transition words %.2f per paragraph (>0.5)" % rep["rhythm"]["transitions_per_para"])


def check_math_prose(lines, rep):
    sym_start, adjacent, colon_display = [], [], []
    for ln in lines:
        body = strip_comment(ln.raw)
        if re.search(r"(?:^|(?<=[.!?])\s+)\$", body.strip()):
            sym_start.append((ln.where(), body.strip()[:90]))
        if re.search(r"\$[^$]+\$\s*,?\s*\$", body):
            adjacent.append((ln.where(), body.strip()[:90]))
        if re.search(r":\s*(?:\\\[|\\begin\{(?:equation|align|gather|multline))", body):
            colon_display.append((ln.where(), body.strip()[:90]))
    # colon on its own line followed by a display
    for i, ln in enumerate(lines[:-1]):
        body = strip_comment(ln.raw).rstrip()
        if body.endswith(":"):
            nxt = strip_comment(lines[i + 1].raw).lstrip()
            if nxt.startswith("\\[") or nxt.startswith("$$") or re.match(
                    r"\\begin\{(equation|align|gather|multline)", nxt):
                colon_display.append((ln.where(), body[-60:]))
    rep["sentence_starts_with_symbol"] = sym_start
    rep["adjacent_formulas"] = adjacent
    rep["colon_before_display"] = colon_display


# --------------------------------------------------------------------------
# bound vs free variables
#
# Uniqueness of meaning is a property of FREE terms. A bound (dummy) variable
# lives inside its binder and may be reused elsewhere without ambiguity: the
# i of \sum_{i=1}^{n} in section 2 and the i of \sum_{i\in I} in section 5 are
# different variables and nobody is confused. Flagging them as collisions is
# noise. What does matter is (a) collisions among free symbols, and (b) a
# bound variable shadowing a free symbol that is in scope -- reusing n as a
# summation index when n is the dimension of the problem.
#
# The scope approximation below is deliberately generous: a variable bound
# anywhere in a math chunk is treated as bound throughout that chunk.
# --------------------------------------------------------------------------

BINDER_OPS = (
    "sum|prod|coprod|bigcup|bigcap|bigsqcup|bigoplus|bigotimes|bigodot|biguplus|"
    "bigvee|bigwedge|lim|limsup|liminf|varlimsup|varliminf|max|min|sup|inf|"
    "argmax|argmin|bigwedge|bigvee"
)
BINDER_SUB_GROUP = re.compile(
    r"\\(?:" + BINDER_OPS + r")\s*(?:\\limits|\\nolimits)?\s*_\s*\{([^{}]*)\}")
BINDER_SUB_ONE = re.compile(
    r"\\(?:" + BINDER_OPS + r")\s*(?:\\limits|\\nolimits)?\s*_\s*"
    r"([A-Za-z]|\\[a-zA-Z]+)(?![A-Za-z])")
FAMILY_SUB = re.compile(r"[\}\)\]]\s*_\s*\{([^{}]*)\}")
QUANTIFIER = re.compile(
    r"\\(?:forall|exists|nexists)\s*"
    r"((?:[A-Za-z]|\\[a-zA-Z]+)(?:\s*,\s*(?:[A-Za-z]|\\[a-zA-Z]+))*)")
MAPSTO = re.compile(r"([A-Za-z]|\\[a-zA-Z]+)\s*\\mapsto")
SETBUILDER = re.compile(r"\\\{(.{0,60}?)(?:\\mid|\\colon|\\vert|\s:\s|:)")
SETBUILDER_IN = re.compile(r"\\\{\s*([A-Za-z]|\\[a-zA-Z]+)\s*\\in(?![a-zA-Z])")
INTEGRAL = re.compile(r"\\(?:int|iint|iiint|idotsint|oint)(?![a-zA-Z])")
DIFFERENTIAL = re.compile(
    r"(?:\\,|\\;|\\:|\s)\s*(?:\\mathrm\s*\{\s*d\s*\}|\\operatorname\s*\{\s*d\s*\}|d)"
    r"\s*([A-Za-z]|\\[a-zA-Z]+)(?![A-Za-z])")
PROSE_BINDER = re.compile(
    r"\bfor\s+(?:all|each|every|any|some)\s+\$([^$]{1,20})\$", re.I)

IDENT = re.compile(r"(?<![\\A-Za-z])([A-Za-z]|\\[a-zA-Z]+)(?![A-Za-z])")


def _idents(text):
    """Single-letter Latin identifiers and Greek macros in a fragment."""
    out = set()
    for m in IDENT.finditer(text):
        sym = m.group(1)
        if sym.startswith("\\") and sym[1:] not in GREEK:
            continue
        out.add(sym)
    return out


def _binder_group(group):
    """Identifiers bound by a subscript group such as 'i=1', 'i\\in I', 'i<j'."""
    left = re.split(r"\\in\b|\\subseteq\b|\\subset\b", group, maxsplit=1)[0]
    left = re.split(r"\\to\b|\\rightarrow\b", left, maxsplit=1)[0]
    return _idents(left)


def bound_in_chunk(chunk, raw_line=""):
    """Over-approximate the set of variables bound somewhere in this chunk."""
    bound = set()
    for m in BINDER_SUB_GROUP.finditer(chunk):
        bound |= _binder_group(m.group(1))
    for m in BINDER_SUB_ONE.finditer(chunk):
        bound |= _idents(m.group(1))
    for m in FAMILY_SUB.finditer(chunk):
        bound |= _binder_group(m.group(1))
    for m in QUANTIFIER.finditer(chunk):
        bound |= _idents(m.group(1))
    for m in MAPSTO.finditer(chunk):
        bound |= _idents(m.group(1))
    for m in SETBUILDER.finditer(chunk):
        bound |= _binder_group(m.group(1))
    for m in SETBUILDER_IN.finditer(chunk):
        bound |= _idents(m.group(1))
    if INTEGRAL.search(chunk):
        for m in DIFFERENTIAL.finditer(chunk):
            bound |= _idents(m.group(1))
    if raw_line:
        for m in PROSE_BINDER.finditer(raw_line):
            bound |= _idents(m.group(1))
    return bound


def check_symbols(lines, rep):
    """Collect single-letter math symbols and look for collisions."""
    math_chunks = []
    in_env = None
    in_display = None
    for ln in lines:
        body = strip_comment(ln.raw)
        if in_display:
            math_chunks.append((ln, body))
            _, in_display = display_state(body, in_display)
            continue
        if in_env:
            math_chunks.append((ln, body))
            if re.search(r"\\end\{%s\}" % re.escape(in_env), body):
                in_env = None
            continue
        m = re.search(r"\\begin\{([A-Za-z*]+)\}", body)
        if m and m.group(1) in MATH_ENVS:
            math_chunks.append((ln, body))
            if not re.search(r"\\end\{%s\}" % re.escape(m.group(1)), body):
                in_env = m.group(1)
            continue
        for pat in (r"\$\$(.+?)\$\$", r"(?<!\\)\$(.+?)(?<!\\)\$", r"\\\[(.+?)\\\]", r"\\\((.+?)\\\)"):
            for mm in re.finditer(pat, body):
                math_chunks.append((ln, mm.group(1)))
        rest = body
        for pat in (r"\$\$.+?\$\$", r"(?<!\\)\$.+?(?<!\\)\$", r"\\\[.+?\\\]", r"\\\(.+?\\\)"):
            rest = re.sub(pat, " ", rest)
        opened, in_display = display_state(rest, None)
        if in_display:
            sep = DISPLAY_OPEN if in_display == "bracket" else "$$"
            math_chunks.append((ln, rest.split(sep, 1)[-1]))

    usage = defaultdict(Counter)          # symbol -> role counter, FREE uses
    bound_uses = Counter()                # symbol -> uses as a bound variable
    places = defaultdict(list)
    bound_places = defaultdict(list)

    prepared = []
    ever_bound = set()
    for ln, chunk in math_chunks:
        cleaned = re.sub(
            r"\\(?:text|mathrm|mathbb|mathcal|mathbf|mathfrak|operatorname)\s*\{[^{}]*\}",
            " ", chunk)
        bound = bound_in_chunk(cleaned, ln.raw)
        ever_bound |= bound
        prepared.append((ln, cleaned, bound))

    # a symbol carrying free occurrences in a substantive formula is a free
    # symbol of the paper; only then does a lone "$n$" in prose mean it
    substantive_free = set()
    for ln, cleaned, bound in prepared:
        if IDENT.fullmatch(cleaned.strip()):
            continue
        for m in IDENT.finditer(cleaned):
            sym = m.group(1)
            if sym.startswith("\\") and sym[1:] not in GREEK:
                continue
            if sym not in bound:
                substantive_free.add(sym)

    for ln, cleaned, bound in prepared:
        # a lone "$i$" in running prose is a mention of a dummy variable bound
        # elsewhere, not a new free symbol -- unless the letter is also free
        # somewhere in a real formula, in which case the mention is free too
        lone = IDENT.fullmatch(cleaned.strip())
        if (lone and lone.group(1) in ever_bound
                and lone.group(1) not in substantive_free):
            bound = bound | {lone.group(1)}
        for m in IDENT.finditer(cleaned):
            sym = m.group(1)
            if sym.startswith("\\") and sym[1:] not in GREEK:
                continue
            if sym in bound:
                bound_uses[sym] += 1
                if len(bound_places[sym]) < 6:
                    bound_places[sym].append(ln.where())
                continue
            tail = cleaned[m.end():m.end() + 2]
            if tail.startswith("("):
                role = "function-application"
            elif tail.startswith("_"):
                role = "subscripted"
            elif tail.startswith("^"):
                role = "superscripted"
            else:
                role = "bare"
            usage[sym][role] += 1
            if len(places[sym]) < 6:
                places[sym].append(ln.where())

    # (a) collisions among FREE occurrences only
    collisions = []
    for sym, roles in usage.items():
        if roles["function-application"] and roles["bare"]:
            collisions.append((sym, dict(roles), places[sym]))
    collisions.sort(key=lambda t: -sum(t[1].values()))

    # (b) a dummy variable shadowing a free symbol
    shadowing = []
    for sym, n_bound in bound_uses.items():
        n_free = sum(usage.get(sym, {}).values())
        if n_free:
            shadowing.append((sym, n_free, n_bound,
                              places.get(sym, [])[:3], bound_places[sym][:3]))
    shadowing.sort(key=lambda t: -(t[1] + t[2]))

    rep["symbol_usage"] = {
        s: {"roles": dict(r), "free": sum(r.values()),
            "bound": bound_uses.get(s, 0), "where": places[s]}
        for s, r in sorted(usage.items(), key=lambda kv: -sum(kv[1].values()))
    }
    rep["bound_only"] = sorted(
        (s, n) for s, n in bound_uses.items() if not usage.get(s))
    rep["symbol_collisions"] = collisions
    rep["symbol_shadowing"] = shadowing

    conf = []
    for ln, chunk in math_chunks:
        for pat, msg in CONFUSABLES:
            if re.search(pat, chunk):
                conf.append((ln.where(), msg, chunk.strip()[:60]))
    seen = set()
    rep["confusables"] = [c for c in conf if not (c[:2] in seen or seen.add(c[:2]))]

    both = []
    joined = " ".join(c for _, c in math_chunks)
    for a, b in ((r"\\epsilon", r"\\varepsilon"), (r"\\phi", r"\\varphi"),
                 (r"\\emptyset", r"\\varnothing"), (r"\\rho", r"\\varrho")):
        if re.search(a + r"\b", joined) and re.search(b + r"\b", joined):
            both.append("%s and %s both used -- confirm they mean different things"
                        % (a.replace("\\\\", "\\"), b.replace("\\\\", "\\")))
    rep["variant_glyphs"] = both


GREEK = {
    "alpha", "beta", "gamma", "delta", "epsilon", "varepsilon", "zeta", "eta",
    "theta", "vartheta", "iota", "kappa", "lambda", "mu", "nu", "xi", "pi",
    "varpi", "rho", "varrho", "sigma", "varsigma", "tau", "upsilon", "phi",
    "varphi", "chi", "psi", "omega", "Gamma", "Delta", "Theta", "Lambda", "Xi",
    "Pi", "Sigma", "Upsilon", "Phi", "Psi", "Omega", "ell",
}


def check_refs(lines, bib_path, rep):
    labels, refs, cites = Counter(), Counter(), Counter()
    bibitems = Counter()
    label_where, cite_where = {}, defaultdict(list)
    bibitem_where = {}
    for ln in lines:
        body = strip_comment(ln.raw)
        for m in re.finditer(r"\\bibitem\s*(?:\[[^\]]*\])?\s*\{([^}]*)\}", body):
            key = m.group(1).strip()
            if key:
                bibitems[key] += 1
                bibitem_where.setdefault(key, ln.where())
        for m in re.finditer(r"\\label\{([^}]*)\}", body):
            labels[m.group(1)] += 1
            label_where.setdefault(m.group(1), ln.where())
        for m in re.finditer(r"\\(?:ref|eqref|cref|Cref|autoref|pageref)\{([^}]*)\}", body):
            for key in m.group(1).split(","):
                refs[key.strip()] += 1
        for m in re.finditer(r"\\cite[a-zA-Z]*\s*(?:\[[^\]]*\])*\{([^}]*)\}", body):
            for key in m.group(1).split(","):
                k = key.strip()
                if k:
                    cites[k] += 1
                    cite_where[k].append(ln.where())

    rep["duplicate_labels"] = [l for l, c in labels.items() if c > 1]
    rep["undefined_refs"] = sorted(k for k in refs if k not in labels)
    rep["unused_labels"] = sorted(l for l in labels if l not in refs)

    rep["bibitems"] = len(bibitems)
    rep["duplicate_bibitems"] = [k for k, c in bibitems.items() if c > 1]

    if bib_path and os.path.exists(bib_path):
        with open(bib_path, encoding="utf-8", errors="replace") as fh:
            bib = fh.read()
        bib_keys = set(re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", bib))
        rep["bib_keys"] = len(bib_keys)
        rep["cites_missing_from_bib"] = sorted(
            (k, cite_where[k][:3]) for k in cites if k not in bib_keys)
        rep["bib_entries_uncited"] = sorted(bib_keys - set(cites))
        entries = re.findall(r"@(\w+)\s*\{\s*([^,\s]+)\s*,((?:[^@])*)", bib)
        thin = []
        for etype, key, body in entries:
            low = body.lower()
            fields = set(re.findall(r"([a-z]+)\s*=", low))
            missing = [f for f in ("title", "year") if f not in fields]
            if etype.lower() not in ("misc", "unpublished") and "author" not in fields:
                missing.append("author")
            if missing:
                thin.append((key, missing))
        rep["bib_incomplete"] = thin
    elif bibitems:
        # No .bib, but a hand-written thebibliography: citation integrity is
        # still checkable against the \bibitem keys. What is lost is
        # entry-level provenance, which is bibcheck.py's job.
        rep["bib_keys"] = None
        rep["cites_missing_from_bibitems"] = sorted(
            (k, cite_where[k][:3]) for k in cites if k not in bibitems)
        rep["bibitems_uncited"] = sorted(k for k in bibitems if k not in cites)
    else:
        rep["bib_keys"] = None
        rep["cites_used"] = sorted(cites)


def check_misc(lines, rep):
    todos, lists, items = [], 0, 0
    for ln in lines:
        if re.search(r"\\todo\b|TODO|FIXME|XXX", ln.raw):
            todos.append((ln.where(), ln.raw.strip()[:90]))
        body = strip_comment(ln.raw)
        m = re.search(r"\\begin\{([A-Za-z*]+)\}", body)
        if m and m.group(1) in LIST_ENVS:
            lists += 1
        items += len(re.findall(r"\\item\b", body))
    rep["todos"] = todos
    rep["lists"] = {"environments": lists, "items": items}


# --------------------------------------------------------------------------
# reporting
# --------------------------------------------------------------------------

def hr(title):
    return "\n" + title + "\n" + "-" * len(title)


def render(rep):
    out = []
    out.append("MATHEMATICAL PAPER AUDIT")
    out.append("=" * 24)
    out.append("files: %d, prose lines: %d" % (rep["n_files"], rep["n_prose_lines"]))

    r = rep.get("rhythm", {})
    out.append(hr("1. Rhythm and density"))
    if "note" in r:
        out.append("  " + r["note"])
    else:
        out.append("  sentences %d | mean %.1f | sd %.1f | cv %.2f | 15-25w share %.0f%%"
                   % (r["n_sentences"], r["mean_len"], r["sd_len"], r["cv"],
                      r["share_15_25"] * 100))
        out.append("  range %d-%d words | longest same-band run %d | paragraphs %d"
                   % (r["min_sentence"], r["max_sentence"],
                      r["longest_same_band_run"], r["n_paragraphs"]))
        out.append("  em-dashes %d (%d paragraphs with >1) | transitions %.2f/paragraph"
                   % (r["emdash_total"], r["paras_over_1_emdash"],
                      r["transitions_per_para"]))
        if rep.get("rhythm_verdict"):
            for v in rep["rhythm_verdict"]:
                out.append("  ! " + v)
        else:
            out.append("  ok: variation within human range")

    out.append(hr("2. Vocabulary (tier A -- almost never right)"))
    if not rep["tier_a"] and not rep["tier_a_phrases"]:
        out.append("  clean")
    for w, hits in sorted(rep["tier_a"].items(), key=lambda kv: -len(kv[1])):
        out.append("  %-16s x%-3d %s" % (w, len(hits), ", ".join(h[0] for h in hits[:6])))
    for where, ph, frag in rep["tier_a_phrases"]:
        out.append("  %-16s %s  | %s" % ("[phrase]", where, ph))

    out.append(hr("3. Vocabulary (tier B -- prefer a plainer word)"))
    if not rep["tier_b"]:
        out.append("  clean")
    for w, hits in sorted(rep["tier_b"].items(), key=lambda kv: -len(kv[1])):
        out.append("  %-16s x%-3d -> %s   [%s]"
                   % (w, len(hits), TIER_B[w], ", ".join(h[0] for h in hits[:4])))

    tc = rep["tier_c_counts"]
    out.append(hr("4. Transition density (tier C)"))
    if tc:
        out.append("  " + ", ".join("%s x%d" % (w, n) for w, n in
                                    sorted(tc.items(), key=lambda kv: -kv[1])))
    else:
        out.append("  clean")

    out.append(hr("5. Throat-clearing and model reflexes"))
    n = 0
    for where, ph, frag in rep["throat_clearing"]:
        out.append("  %-22s %s" % (where, ph)); n += 1
    for where, msg, frag in rep["reflexes"]:
        out.append("  %-22s %s" % (where, msg)); n += 1
    if not n:
        out.append("  clean")

    out.append(hr("6. Gap-fillers in proofs"))
    if rep["gap_fillers"]:
        for where, msg, frag in rep["gap_fillers"]:
            out.append("  %-22s %s" % (where, msg))
            out.append("      %s" % frag)
    else:
        out.append("  clean")

    out.append(hr("6a. Context leaks"))
    if rep.get("context_leaks"):
        for where, msg, frag in rep["context_leaks"][:15]:
            out.append("  %-22s %s" % (where, msg))
            out.append("      %s" % frag)
    else:
        out.append("  clean")

    out.append(hr("6a2. Defensive density (negations per 100 words)"))
    rows = rep.get("negation_by_section") or []
    if not rows:
        out.append("  not enough prose per section to measure")
    else:
        for r in rows:
            out.append("  %-34s %5.1f /100w  (%d in %d words)%s"
                       % (r["title"][:34], r["per_100w"], r["negations"],
                          r["words"], "  [exempt]" if r["exempt"] else ""))
        if rep.get("negation_flagged"):
            out.append("  ! body sections above 2.0 -- check whether these are")
            out.append("    boundaries (part of the claim, keep) or defences")
            out.append("    (collect them in the limitations/discussion section):")
            for r in rep["negation_flagged"]:
                out.append("      %-22s %s" % (r["where"], r["title"][:40]))

    out.append(hr("6b. Terminology and pronouns"))
    n = 0
    for where, msg, frag in rep.get("deprecated_terms", []):
        out.append("  %-22s %s" % (where, msg)); n += 1
    for where, msg, frag in rep.get("pronoun_issues", []):
        out.append("  %-22s %s" % (where, msg))
        out.append("      %s" % frag); n += 1
    if not n:
        out.append("  clean")
    else:
        out.append("  (a cited title keeps its original wording; a term of art is")
        out.append("   not renamed for style -- see prose.md)")

    out.append(hr("7. Symbols in sentences"))
    for key, title in (("sentence_starts_with_symbol", "sentence starts with a symbol"),
                       ("adjacent_formulas", "two formulas with no word between"),
                       ("colon_before_display", "colon before a display")):
        hits = rep.get(key, [])
        if hits:
            out.append("  %s (%d):" % (title, len(hits)))
            for where, frag in hits[:12]:
                out.append("      %-22s %s" % (where, frag))
            if len(hits) > 12:
                out.append("      ... %d more" % (len(hits) - 12))
    if not any(rep.get(k) for k in ("sentence_starts_with_symbol",
                                    "adjacent_formulas", "colon_before_display")):
        out.append("  clean")

    out.append(hr("8. Notation (free symbols; bound variables excluded)"))
    if rep["symbol_collisions"]:
        out.append("  free symbol used both as a function head and as a bare quantity --")
        out.append("  confirm each denotes ONE object (a map written both f and f(x) is fine):")
        for sym, roles, where in rep["symbol_collisions"][:12]:
            out.append("      %-10s %s   [%s]" % (sym, roles, ", ".join(where[:4])))
        if len(rep["symbol_collisions"]) > 12:
            out.append("      ... %d more" % (len(rep["symbol_collisions"]) - 12))
    else:
        out.append("  no free symbol used both as a function head and as a bare quantity")

    sh = rep.get("symbol_shadowing") or []
    if sh:
        out.append("  dummy variable shadowing a free symbol"
                   " (reusing the free letter as an index):")
        for sym, n_free, n_bound, fw, bw in sh[:10]:
            out.append("      %-10s free x%-3d [%s]  bound x%-3d [%s]"
                       % (sym, n_free, ", ".join(fw), n_bound, ", ".join(bw)))
        if len(sh) > 10:
            out.append("      ... %d more" % (len(sh) - 10))
    else:
        out.append("  no dummy variable shadows a free symbol")

    for msg in rep.get("variant_glyphs", []):
        out.append("  ! " + msg)
    if rep.get("confusables"):
        out.append("  confusable glyphs:")
        for where, msg, frag in rep["confusables"][:15]:
            out.append("      %-22s %s" % (where, msg))
    top = list(rep["symbol_usage"].items())[:18]
    if top:
        out.append("  most used free symbols:")
        out.append("      " + ", ".join("%s(%d)" % (s, d["free"]) for s, d in top))
    bo = rep.get("bound_only") or []
    if bo:
        out.append("  bound only (dummy variables, reuse is fine):")
        out.append("      " + ", ".join("%s(%d)" % (s, n) for s, n in bo[:18]))

    out.append(hr("9. Cross-references and bibliography"))
    for key, title in (("duplicate_labels", "duplicate labels"),
                       ("undefined_refs", "\\ref to a missing label"),
                       ("unused_labels", "labels never referenced")):
        v = rep.get(key) or []
        if v:
            out.append("  %s (%d): %s" % (title, len(v), ", ".join(map(str, v[:12]))))
    if rep.get("bib_keys") is not None:
        out.append("  bib entries: %d" % rep["bib_keys"])
        miss = rep.get("cites_missing_from_bib") or []
        if miss:
            out.append("  ! \\cite keys not in the .bib (%d):" % len(miss))
            for k, where in miss[:12]:
                out.append("      %-24s %s" % (k, ", ".join(where)))
        unc = rep.get("bib_entries_uncited") or []
        if unc:
            out.append("  uncited .bib entries (%d): %s"
                       % (len(unc), ", ".join(unc[:12])))
        thin = rep.get("bib_incomplete") or []
        if thin:
            out.append("  ! incomplete entries (verify against the real record):")
            for k, missing in thin[:12]:
                out.append("      %-24s missing: %s" % (k, ", ".join(missing)))
    elif rep.get("bibitems"):
        n = rep["bibitems"]
        out.append("  no .bib; checked against %d \\bibitem key%s in the tex"
                   % (n, "" if n == 1 else "s"))
        dup = rep.get("duplicate_bibitems") or []
        if dup:
            out.append("  ! duplicate \\bibitem keys (%d): %s"
                       % (len(dup), ", ".join(dup[:12])))
        miss = rep.get("cites_missing_from_bibitems") or []
        if miss:
            out.append("  ! \\cite keys with no \\bibitem (%d):" % len(miss))
            for k, where in miss[:12]:
                out.append("      %-24s %s" % (k, ", ".join(where)))
        unc = rep.get("bibitems_uncited") or []
        if unc:
            out.append("  \\bibitem entries never cited (%d): %s"
                       % (len(unc), ", ".join(unc[:12])))
        out.append("  entry-level provenance (DOI, arXiv id, duplicates) needs a")
        out.append("  .bib and bibcheck.py; it was not checked")
    else:
        out.append("  no .bib given (--bib) -- citation verification not run")

    out.append(hr("10. Leftovers"))
    if rep["todos"]:
        for where, frag in rep["todos"][:20]:
            out.append("  %-22s %s" % (where, frag))
    else:
        out.append("  no \\todo / TODO markers")
    out.append("  lists: %d environments, %d items"
               % (rep["lists"]["environments"], rep["lists"]["items"]))

    out.append("")
    out.append("Flags are advisory. Terms of art override the vocabulary lists;")
    out.append("verify every bibliography entry against a real record by hand.")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tex")
    ap.add_argument("--bib", default=None)
    ap.add_argument("--no-follow", action="store_true",
                    help="do not follow \\input / \\include")
    ap.add_argument("--json", default=None, help="also write the raw report as JSON")
    args = ap.parse_args()

    lines = read_tex(args.tex, follow=not args.no_follow)
    if not lines:
        sys.exit("nothing to audit")
    build_prose(lines)

    bib = args.bib
    if bib is None:
        for ln in lines:
            m = re.search(r"\\bibliography\{([^}]+)\}", strip_comment(ln.raw))
            if m:
                cand = m.group(1).split(",")[0].strip()
                if not cand.endswith(".bib"):
                    cand += ".bib"
                cand = os.path.join(os.path.dirname(args.tex), cand)
                if os.path.exists(cand):
                    bib = cand
                break

    rep = {
        "n_files": len({l.path for l in lines}),
        "n_prose_lines": sum(1 for l in lines if l.prose and l.prose.strip()),
    }
    check_vocabulary(lines, rep)
    check_phrasing(lines, rep)
    check_rhythm(lines, rep)
    check_negation_density(lines, rep)
    check_math_prose(lines, rep)
    check_symbols(lines, rep)
    check_refs(lines, bib, rep)
    check_misc(lines, rep)

    print(render(rep))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(rep, fh, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
