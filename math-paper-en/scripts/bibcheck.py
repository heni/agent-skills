#!/usr/bin/env python3
"""
Lint a .bib file for the things a bibliography actually gets wrong.

audit.py already checks the .tex side (cite keys with no entry, entries never
cited, entries missing author/title/year). This script checks the .bib itself:

  * provenance     -- entries with no DOI, arXiv id or URL cannot be checked by
                      a reader or by you; they are the ones that turn out to be
                      invented or misremembered
  * duplicates     -- same DOI, same arXiv id, same normalised title, same key
  * author spelling-- the same surname written several ways across entries
                      (Erdos / Erdos / Erdoes) makes one person look like three
  * key convention -- mixed alphanumeric and snake_case keys
  * title casing   -- capitals that BibTeX will lowercase unless braced
  * page ranges    -- hyphen where an en-dash is required
  * bloat          -- abstract/keywords/file/annote fields dumped in by a
                      reference manager
  * field hygiene  -- 'and' separators, stray month/issn, year sanity

Usage:
    python3 bibcheck.py refs.bib [--json out.json]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict

ENTRY = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,(.*?)\n\s*\}\s*(?=@|\Z)",
                   re.S)
FIELD = re.compile(r"(\w+)\s*=\s*(\{.*?\}|\"[^\"]*\"|[^,\n]+)\s*,?\s*(?=\n\s*\w+\s*=|\Z)",
                   re.S)

BLOAT = {"abstract", "keywords", "file", "annote", "annotation", "mendeley-tags",
         "bdsk-file-1", "bdsk-url-1", "readstatus", "rating", "owner",
         "timestamp", "groups", "priority"}
PROVENANCE = {"doi", "eprint", "archiveprefix", "url", "mrnumber", "zblnumber",
              "isbn"}
NO_PROVENANCE_TYPES = {"unpublished", "misc", "personal", "communication"}


def strip_braces(v):
    v = v.strip()
    while v and v[0] in "{\"" and v[-1] in "}\"":
        v = v[1:-1].strip()
    return v


def parse(text):
    out = []
    for etype, key, body in ENTRY.findall(text):
        fields = {}
        for name, value in FIELD.findall(body + "\n"):
            fields[name.lower()] = strip_braces(value)
        out.append({"type": etype.lower(), "key": key, "fields": fields,
                    "raw": body})
    return out


def fold(s):
    """Lowercase, strip diacritics and punctuation -- for comparing names."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("\\", " ")
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def surnames(author_field):
    """Rough surname extraction from a BibTeX author field."""
    out = []
    for person in re.split(r"\s+and\s+", author_field):
        person = person.strip().strip("{}")
        if not person:
            continue
        if "," in person:
            out.append(person.split(",")[0].strip())
        else:
            parts = person.split()
            if parts:
                out.append(parts[-1])
    return out


def norm_title(t):
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


def check(entries):
    rep = {"n_entries": len(entries)}

    # --- duplicates --------------------------------------------------------
    by_key, by_doi, by_eprint, by_title = (defaultdict(list) for _ in range(4))
    for e in entries:
        f = e["fields"]
        by_key[e["key"]].append(e["key"])
        if f.get("doi"):
            by_doi[f["doi"].lower().rstrip(".")].append(e["key"])
        if f.get("eprint"):
            by_eprint[f["eprint"].lower()].append(e["key"])
        if f.get("title"):
            by_title[norm_title(f["title"])].append(e["key"])
    rep["duplicate_keys"] = {k: v for k, v in by_key.items() if len(v) > 1}
    rep["duplicate_doi"] = {k: v for k, v in by_doi.items() if len(v) > 1}
    rep["duplicate_eprint"] = {k: v for k, v in by_eprint.items() if len(v) > 1}
    rep["duplicate_title"] = {k: v for k, v in by_title.items() if len(v) > 1}

    # --- provenance --------------------------------------------------------
    rep["no_provenance"] = [
        e["key"] for e in entries
        if e["type"] not in NO_PROVENANCE_TYPES
        and not (PROVENANCE & set(e["fields"]))
    ]

    # --- author spelling ---------------------------------------------------
    variants = defaultdict(Counter)
    for e in entries:
        for sn in surnames(e["fields"].get("author", "")):
            variants[fold(sn)][sn] += 1
    rep["name_variants"] = {
        k: dict(v) for k, v in variants.items() if len(v) > 1
    }

    # --- key convention ----------------------------------------------------
    styles = Counter()
    for e in entries:
        k = e["key"]
        if re.fullmatch(r"[A-Z][A-Za-z+]{0,5}\d{2}[a-z]?", k):
            styles["alphanumeric (Kra96)"] += 1
        elif re.fullmatch(r"[a-z]+\d{4}[a-z0-9]*", k):
            styles["author-year (krantz1996)"] += 1
        elif "_" in k or "-" in k:
            styles["snake/kebab"] += 1
        else:
            styles["other"] += 1
    rep["key_styles"] = dict(styles)

    # --- per-entry hygiene -------------------------------------------------
    issues = defaultdict(list)
    for e in entries:
        f, k = e["fields"], e["key"]
        title = f.get("title", "")
        # capitals BibTeX will eat
        words = re.findall(r"\b[A-Za-z][A-Za-z0-9]*\b", title)
        risky = [w for w in words[1:]
                 if (w[1:].lower() != w[1:] or (w.isupper() and len(w) > 1))]
        unbraced = [w for w in risky if "{%s}" % w not in title]
        if unbraced:
            issues[k].append("unbraced capitals in title: " + ", ".join(unbraced[:5]))
        pages = f.get("pages", "")
        if pages and re.search(r"\d\s*-\s*\d", pages) and "--" not in pages:
            issues[k].append("page range uses a hyphen, needs '--': %s" % pages)
        bl = sorted(BLOAT & set(f))
        if bl:
            issues[k].append("reference-manager bloat: " + ", ".join(bl))
        y = f.get("year", "")
        if y and not re.fullmatch(r"\d{4}", y.strip()):
            issues[k].append("year is not a bare 4-digit number: %r" % y)
        au = f.get("author", "")
        if au and ("&" in au or (";" in au)):
            issues[k].append("authors separated by '&' or ';'; BibTeX wants 'and'")
        if f.get("eprint") and not f.get("archiveprefix") and not f.get("eprinttype"):
            issues[k].append("eprint without archivePrefix/eprinttype")
        if e["type"] == "article" and not f.get("journal") and not f.get("journaltitle"):
            issues[k].append("article without a journal")
        if e["type"] == "inproceedings" and not f.get("booktitle"):
            issues[k].append("inproceedings without a booktitle")
    rep["issues"] = {k: v for k, v in issues.items()}
    return rep


def render(rep):
    o = ["BIBLIOGRAPHY LINT", "=" * 17, "entries: %d" % rep["n_entries"], ""]

    def block(title, body_lines):
        o.append(title)
        o.append("-" * len(title))
        o.extend(body_lines or ["  clean"])
        o.append("")

    prov = rep["no_provenance"]
    block("1. Provenance (no DOI / arXiv id / URL / MR number)",
          ["  %s" % k for k in prov[:30]] +
          (["  ... %d more" % (len(prov) - 30)] if len(prov) > 30 else []) +
          (["", "  These cannot be checked by a reader. Re-fetch each from the",
            "  publisher, arXiv, MathSciNet or zbMATH -- do not retype it."]
           if prov else []))

    dups = []
    for label, key in (("same key", "duplicate_keys"),
                       ("same DOI", "duplicate_doi"),
                       ("same arXiv id", "duplicate_eprint"),
                       ("same title", "duplicate_title")):
        for val, keys in rep[key].items():
            dups.append("  %-14s %s   [%s]" % (label, val[:50], ", ".join(keys)))
    block("2. Duplicates", dups)

    nv = ["  %-16s %s" % (k, ", ".join("%s x%d" % (s, n) for s, n in v.items()))
          for k, v in rep["name_variants"].items()]
    block("3. One person, several spellings", nv)

    ks = rep["key_styles"]
    ks_lines = ["  " + ", ".join("%s: %d" % (s, n) for s, n in ks.items())]
    if len([n for n in ks.values() if n]) > 1:
        ks_lines.append("  ! mixed key conventions -- pick one and convert")
    block("4. Key convention", ks_lines)

    il = []
    for k, v in rep["issues"].items():
        il.append("  %s" % k)
        il.extend("      %s" % x for x in v)
    block("5. Per-entry hygiene", il)

    o.append("Nothing here proves an entry is real. Provenance fields make it")
    o.append("checkable; only opening the record proves it.")
    return "\n".join(o)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bib")
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    try:
        text = open(a.bib, encoding="utf-8", errors="replace").read()
    except OSError as exc:
        sys.exit("cannot read %s: %s" % (a.bib, exc))
    entries = parse(text)
    if not entries:
        # An empty bibliography is a legitimate early state; only an unreadable
        # file is an error, and that exits above.
        print("no entries in %s yet -- nothing to lint" % a.bib)
        return
    rep = check(entries)
    print(render(rep))
    if a.json:
        json.dump(rep, open(a.json, "w", encoding="utf-8"), indent=2,
                  ensure_ascii=False)


if __name__ == "__main__":
    main()
