"""Утилиты извлечения графики из PDF и подготовки перевода.

Навык scientific-paper-translation (v4). Функции перенесены сюда из SKILL.md
(Части 1, 2, 2A) байт-в-байт, чтобы использоваться копированием, а не
перепечаткой. Правки вносятся в скилл, не в рабочие копии.

Состав:
    preview_page              — рендер страницы в PNG для визуального подбора bbox
    extract_raster_images     — Стратегия A: прямое извлечение встроенных растров
    crop_with_overlay_text    — Стратегия B: кроп с сохранением векторных подписей
    remove_text_keep_graphics — Стратегия C, шаг 1: удаление текста
    extract_graphs_from_clean_pdf — Стратегия C, шаг 2: кадрирование по координатам
    detect_columns            — автоопределение одно-/двухколоночной раскладки
    fix_tags                  — замена \\tag{N} на \\qquad\\text{(N)} для pandoc
"""

import re

import fitz


def preview_page(pdf_path, page_num, scale=2):
    """Сохранить целую страницу как PNG для визуального подбора координат.
    Размер pixmap: width = page.rect.width * scale, height аналогично.
    Чтобы получить PDF-координаты bbox: pixel_xy / scale."""
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    print(f"Page size (PDF pt): {page.rect}")
    mat = fitz.Matrix(scale, scale)
    pix = page.get_pixmap(matrix=mat)
    pix.save(f"preview_page{page_num+1}.png")
    doc.close()


def extract_raster_images(pdf_path, output_dir):
    """Извлекает все растровые изображения из PDF в исходном качестве."""
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc[page_num]
        for img_index, img in enumerate(page.get_images()):
            xref = img[0]
            base = doc.extract_image(xref)
            ext = base["ext"]
            with open(f"{output_dir}/page{page_num+1}_img{img_index+1}.{ext}", "wb") as f:
                f.write(base["image"])
            print(f"page{page_num+1}_img{img_index+1}: {base['width']}x{base['height']}")
    doc.close()


def crop_with_overlay_text(pdf_path, page_num, bbox, output_path, dpi=288):
    """Кадрирование области с СОХРАНЕНИЕМ всего векторного текста.
    Используется для схем с векторными подписями поверх растра."""
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    scale = dpi / 72
    mat = fitz.Matrix(scale, scale)
    clip = fitz.Rect(*bbox)
    pix = page.get_pixmap(matrix=mat, clip=clip)
    pix.save(output_path)
    print(f"Saved {output_path}: {pix.width}x{pix.height}")
    doc.close()


def remove_text_keep_graphics(input_pdf, output_pdf, pages_to_process):
    """Удаляет весь текст из PDF, оставляя только векторную графику."""
    doc = fitz.open(input_pdf)
    for page_num in pages_to_process:
        page = doc[page_num]
        for block in page.get_text("dict")["blocks"]:
            if block["type"] == 0:  # текстовый блок
                page.add_redact_annot(fitz.Rect(block["bbox"]), fill=(1, 1, 1))
        page.apply_redactions()
    doc.save(output_pdf)
    doc.close()


def extract_graphs_from_clean_pdf(clean_pdf, output_dir, coordinates, dpi=600):
    """Извлекает графики из PDF без текста по заданным координатам."""
    doc = fitz.open(clean_pdf)
    for fig_name, info in coordinates.items():
        page = doc[info['page']]
        mat = fitz.Matrix(dpi/72, dpi/72)
        pix = page.get_pixmap(matrix=mat, clip=fitz.Rect(info['bbox']))
        pix.save(f"{output_dir}/{fig_name}.png")
    doc.close()


def detect_columns(pdf_path, page_num=1, min_frac=0.6):
    # Возвращает 2, если текстовые блоки страницы образуют две колонки
    # (достаточная доля блоков целиком в левой половине и достаточная — в правой),
    # иначе 1. По умолчанию смотрим страницу 2 (на первой — шапка и аннотация).
    doc = fitz.open(pdf_path)
    page = doc[min(page_num, len(doc) - 1)]
    mid = page.rect.width / 2
    left = right = spanning = 0
    for b in page.get_text("dict")["blocks"]:
        if b["type"] != 0:
            continue
        x0, _, x1, _ = b["bbox"]
        if x1 < mid + 10:
            left += 1
        elif x0 > mid - 10:
            right += 1
        else:
            spanning += 1
    doc.close()
    total = left + right + spanning
    two = total and (left + right) / total >= min_frac and left and right
    return 2 if two else 1


def fix_tags(content):
    return re.sub(r'\\tag\{([^}]+)\}',
                  lambda m: f'\\qquad\\text{{({m.group(1)})}}', content)


def optimize_png(path, output_path=None, max_width=2000):
    """Ужать PNG шире max_width px (Проблема 7, Часть 10)."""
    from PIL import Image
    img = Image.open(path)
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    out = output_path or path
    img.save(out, optimize=True, compress_level=9)
    return out
