"""Драйвер полного pipeline перевода (Часть 9 навыка scientific-paper-translation).

Функция translate_paper — дословно из SKILL.md; добавлен только __main__:
    python3 translate_paper.py input.pdf output.pdf translation.md
Примитивы извлечения — в pdf_tools.py.
"""

import fitz, os, re, subprocess


def translate_paper(input_pdf, output_pdf, markdown_content):
    # 1. Извлечь изображения (Стратегия A)
    os.makedirs("extracted_graphs", exist_ok=True)
    doc = fitz.open(input_pdf)
    for page_num in range(len(doc)):
        for idx, img in enumerate(doc[page_num].get_images()):
            xref = img[0]
            base = doc.extract_image(xref)
            with open(f"extracted_graphs/p{page_num}_img{idx}.{base['ext']}", "wb") as f:
                f.write(base["image"])
    doc.close()

    # 2. Кастомный шаблон
    result = subprocess.run(["pandoc", "-D", "latex"], capture_output=True, text=True)
    template = result.stdout.replace(r'\usepackage{lmodern}',
                                       r'% \usepackage{lmodern}')
    with open("custom_template.tex", "w") as f:
        f.write(template)

    # 3. Исправить \tag → \qquad\text{(N)}
    fixed = re.sub(r'\\tag\{([^}]+)\}',
                   lambda m: f'\\qquad\\text{{({m.group(1)})}}', markdown_content)
    with open("translation.md", "w") as f:
        f.write(fixed)

    # 4. Компилировать
    subprocess.run([
        "pandoc", "translation.md", "-o", output_pdf,
        "--pdf-engine=xelatex",
        "--template=custom_template.tex",
        "-V", "colorlinks=true", "-V", "linkcolor=blue"
    ], check=True)


if __name__ == "__main__":
    import sys
    inp, out, md = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(md) as f:
        translate_paper(inp, out, f.read())
