import fitz, re, os, subprocess

def verify_translation(md_path, pdf_path, original_pdf=None):
    # 1. Базовые проверки
    size_kb = os.path.getsize(pdf_path) / 1024
    doc = fitz.open(pdf_path)
    print(f"📄 Pages: {doc.page_count}, Size: {size_kb:.0f} KB")

    # 2. Подсчёт формул
    with open(md_path) as f:
        md = f.read()
    md_formulas = len(re.findall(r'\\qquad\\text\{\(\d+\)\}', md))
    pdf_text = "\n".join(page.get_text() for page in doc)
    pdf_formulas = len(set(re.findall(r'\((\d+)\)', pdf_text)))
    print(f"📐 Formulas in MD: {md_formulas}, distinct (N) in PDF: {pdf_formulas}")

    # 3. Поиск битых ссылок (?? — признак unresolved \ref)
    if "??" in pdf_text:
        print("⚠️  Found '??' in PDF — possible broken \\ref")

    # 4. Проверка отсутствия английских заголовков-обрывков
    en_markers = ["Introduction", "Conclusion", "Acknowledgments", "Abstract"]
    found = [m for m in en_markers if m in pdf_text]
    if found:
        print(f"⚠️  English section markers in PDF: {found}")

    # 5. Сравнение с оригиналом (опционально)
    if original_pdf:
        orig = fitz.open(original_pdf)
        orig_text = "\n".join(p.get_text() for p in orig)
        orig_formulas = len(set(re.findall(r'\((\d+)\)', orig_text)))
        print(f"📋 Original formulas: {orig_formulas} vs translation: {pdf_formulas}")
        if abs(orig_formulas - pdf_formulas) > 2:
            print("⚠️  Significant formula count mismatch")
        orig.close()

    doc.close()
    print("✅ Verification complete")

if __name__ == "__main__":
    md, pdf = sys.argv[1], sys.argv[2]
    original = sys.argv[3] if len(sys.argv) > 3 else None
    verify_translation(md, pdf, original)
