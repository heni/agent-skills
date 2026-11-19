#!/usr/bin/env python3
"""Check a hard page limit at the seam, not by a landmark.

Where a venue counts the bibliography, the limit is met only if the last counted
page *ends* with the last reference: "the references start on page 6" passes
while an entry spills onto page 7. Where a venue excludes the references and the
appendix (NeurIPS, ICML, ICLR and many others), the seam is elsewhere — pass
`--after REFERENCES` so the check asks whether the overflow is the excluded
material rather than body text.

    python3 scripts/pagegate.py main.pdf --limit 6                 # IEEE-style
    python3 scripts/pagegate.py main.pdf --limit 9 --after REFERENCES,APPENDIX

`--after` names what may legitimately follow the limit; the marker is matched
ignoring spaces, since pdftotext renders small caps as "A PPENDIX". The check
passes when the marker heads the first uncounted page, or heads a line on the
last counted page (an appendix that begins mid-page and runs over is compliant).
It must head a line: "deferred to the appendix" in running text is a
cross-reference, and treating it as a heading would pass a paper whose body
really does overflow.

Exit status: 0 the limit is met, 1 it is exceeded, 2 the check could not be
performed — a missing tool, an unreadable PDF, or a page whose text cannot be
extracted at all (a full-page figure), where a silent pass would be worse than a
complaint. A build gate must treat 2 as failure. Needs poppler-utils.
"""
import argparse
import re
import shutil
import subprocess
import sys

OK, EXCEEDED, UNVERIFIED = 0, 1, 2


def run(cmd):
    """Run a poppler tool; return its stdout, or None if the call failed."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True)
    except OSError as e:
        print(f"pagegate: cannot run {cmd[0]}: {e}")
        return None
    if r.returncode != 0:
        tail = r.stderr.strip().splitlines()
        print(f"pagegate: {cmd[0]} failed: {tail[-1] if tail else 'exit ' + str(r.returncode)}")
        return None
    return r.stdout


def page_text(pdf, page):
    out = run(["pdftotext", "-f", str(page), "-l", str(page), pdf, "-"])
    return None if out is None else [ln.strip() for ln in out.split("\n") if ln.strip()]


def page_count(pdf):
    out = run(["pdfinfo", pdf])
    if out is None:
        return None
    m = re.search(r"^Pages:\s+(\d+)", out, re.M)
    if not m:
        print("pagegate: pdfinfo reported no page count")
        return None
    return int(m.group(1))


def squash(text):
    return re.sub(r"\s+", "", text).upper()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf")
    ap.add_argument("--limit", type=int, required=True,
                    help="last page the venue counts; what that includes is the "
                         "venue's rule, so set --after accordingly")
    ap.add_argument("--after", default="APPENDIX",
                    help="comma-separated headings that may follow the limit "
                         "(default APPENDIX; use REFERENCES,APPENDIX where the "
                         "bibliography is excluded from the count)")
    args = ap.parse_args(argv)

    missing = [t for t in ("pdftotext", "pdfinfo") if not shutil.which(t)]
    if missing:
        print(f"pagegate: {' and '.join(missing)} not found (install poppler-utils); "
              f"the limit was NOT checked")
        return UNVERIFIED

    markers = [squash(a) for a in args.after.split(",") if a.strip()]
    total = page_count(args.pdf)
    if total is None:
        return UNVERIFIED
    if total < args.limit:
        print(f"pages: {total}, limit: {args.limit} — the document is shorter than the limit")
        return OK

    last = page_text(args.pdf, args.limit)
    if last is None:
        return UNVERIFIED
    over = [] if total == args.limit else page_text(args.pdf, args.limit + 1)
    if over is None:
        return UNVERIFIED

    print(f"pages: {total}, limit: {args.limit}")
    print(f"page {args.limit} ends with:")
    for ln in last[-2:] or ["    (no extractable text)"]:
        print(f"    {ln}")
    if total == args.limit:
        print(f"nothing past page {args.limit}")
        return OK

    if not over:
        # An empty extraction is not evidence of an empty page: a full-page
        # figure extracts to nothing. Refuse to pass on no evidence.
        print(f"page {args.limit + 1} yields no extractable text — it may be a "
              f"figure page. Check it by eye; the limit was NOT verified")
        return UNVERIFIED

    print(f"page {args.limit + 1} starts with:")
    for ln in over[:2]:
        print(f"    {ln}")

    head = squash(" ".join(over[:2]))
    if any(head.startswith(m) for m in markers):
        print(f"OK: page {args.limit + 1} begins the excluded material")
        return OK
    # An appendix (or bibliography) that starts mid-way down the last counted
    # page legitimately runs over: everything past the marker is excluded. The
    # marker has to HEAD a line to count -- "deferred to the appendix" in running
    # text is a cross-reference, not a heading, and matching it anywhere on the
    # page would pass a paper whose body genuinely overflows.
    hit = next((m for line in last for m in markers
                if squash(line).startswith(m) and not squash(line).endswith(".")),
               None)
    if hit:
        print(f"OK: the excluded material starts on page {args.limit} and runs over")
        return OK
    print(f"FAIL: page {args.limit + 1} carries counted material, not "
          f"{args.after} — the limit is exceeded")
    return EXCEEDED


if __name__ == "__main__":
    sys.exit(main())
