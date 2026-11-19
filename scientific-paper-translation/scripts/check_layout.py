import re, sys, subprocess, fitz

def tex_log_check(md, template="custom_template.tex", max_overfull_pt=2.0):
    subprocess.run(["pandoc", md, "-s", "-o", "chk.tex", "--template", template], check=True)
    subprocess.run(["xelatex", "-interaction=nonstopmode", "chk.tex"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log = open("chk.log", errors="replace").read()
    tex = open("chk.tex").read().splitlines()
    bad = []
    pat = r"Overfull \\hbox \(([\d.]+)pt too wide\)[^\n]*?(?:at line|lines) (\d+)"
    for m in re.finditer(pat, log):
        pt, line = float(m.group(1)), int(m.group(2))
        if pt > max_overfull_pt:
            src = tex[line - 1][:100] if line - 1 < len(tex) else ""
            bad.append((pt, line, src))
    errs = re.findall(r"^! .*", log, flags=re.M)
    under = len(re.findall(r"Underfull \\hbox", log))
    return bad, errs, under

def margin_check(pdf, margin_pt=40, dpi=72, thresh=250, min_pixels=30):
    # Тёмные пиксели в левом/правом поле каждой страницы.
    doc = fitz.open(pdf); hits = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72), colorspace=fitz.csGRAY)
        w, h, buf = pix.width, pix.height, pix.samples
        m = int(margin_pt * dpi / 72)
        def dark(x0, x1):
            return sum(1 for y in range(h) for x in range(x0, x1) if buf[y * w + x] < thresh)
        l, r = dark(0, m), dark(w - m, w)
        if l > min_pixels or r > min_pixels:
            hits.append((i + 1, l, r))
    doc.close(); return hits

if __name__ == "__main__":
    md, pdf = sys.argv[1], sys.argv[2]
    bad, errs, under = tex_log_check(md)
    for e in errs: print("LaTeX error:", e)
    for pt, line, src in bad: print(f"Overfull {pt:.1f}pt at .tex line {line}: {src}")
    print(f"Underfull lines: {under} (не блокер; лечится \\hyphenation)")
    for p, l, r in margin_check(pdf): print(f"Page {p}: ink in margins (left={l}px, right={r}px)")
    txt = "\n".join(pg.get_text() for pg in fitz.open(pdf))
    if "??" in txt: print("'??' in PDF — broken \\ref")
    en = [w for w in ["Introduction", "Conclusion", "Abstract", "Acknowledgments"] if w in txt]
    if en: print("English markers:", en)
    print("layout check OK" if not (bad or errs) else "FIX BEFORE DELIVERY")
