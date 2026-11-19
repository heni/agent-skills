"""Тесты библиотеки scientific-paper-translation на синтетических PDF.

Фикстуры строятся через PyMuPDF — внешние файлы не нужны.
Запуск: python3 -m pytest tests/ -q
"""

import io
import shutil
import subprocess
import sys
from pathlib import Path

import fitz
import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import pdf_tools
from check_layout import margin_check
import verify_translation


def make_png(width=120, height=80, color=(200, 60, 60)):
    img = Image.new("RGB", (width, height), color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def blank_pdf(path, pages=1):
    doc = fitz.open()
    for _ in range(pages):
        doc.new_page(width=595, height=842)
    doc.save(path)
    doc.close()
    return path


def add_text(pdf_path, lines_positions):
    """lines_positions: [(x, y, text), ...]"""
    doc = fitz.open(pdf_path)
    page = doc[0]
    for x, y, text in lines_positions:
        page.insert_text(fitz.Point(x, y), text)
    doc.saveIncr()
    doc.close()
    return pdf_path


def add_image(pdf_path, rect, png_bytes=None):
    doc = fitz.open(pdf_path)
    doc[0].insert_image(fitz.Rect(*rect), stream=png_bytes or make_png())
    doc.saveIncr()
    doc.close()
    return pdf_path


# --- чистые функции ---

def test_fix_tags():
    assert pdf_tools.fix_tags(r"\tag{5}") == r"\qquad\text{(5)}"
    assert pdf_tools.fix_tags("a \\tag{12} b \\tag{3}") == \
        "a \\qquad\\text{(12)} b \\qquad\\text{(3)}"


def test_optimize_png(tmp_path):
    src = tmp_path / "big.png"
    Image.new("RGB", (3000, 1500), (10, 10, 10)).save(src)
    out = pdf_tools.optimize_png(str(src), max_width=2000)
    with Image.open(out) as img:
        assert img.width == 2000
        assert img.height == 1000
    small = tmp_path / "small.png"
    Image.new("RGB", (500, 300), (10, 10, 10)).save(small)
    pdf_tools.optimize_png(str(small))
    with Image.open(small) as img:
        assert img.width == 500


# --- PDF-структура ---

def test_detect_columns_one(tmp_path):
    p = blank_pdf(tmp_path / "one.pdf")
    add_text(p, [(60, 100 + 14 * i, f"Строка текста номер {i} слева") for i in range(8)])
    assert pdf_tools.detect_columns(str(p), page_num=0) == 1


def test_detect_columns_two(tmp_path):
    p = blank_pdf(tmp_path / "two.pdf")
    lines = [(60, 100 + 14 * i, f"Левая колонка строка {i}") for i in range(6)]
    lines += [(320, 100 + 14 * i, f"Правая колонка строка {i}") for i in range(6)]
    add_text(p, lines)
    assert pdf_tools.detect_columns(str(p), page_num=0) == 2


def test_extract_raster_images(tmp_path):
    p = blank_pdf(tmp_path / "img.pdf")
    add_image(p, (100, 100, 220, 180))
    out = tmp_path / "out"
    out.mkdir()
    pdf_tools.extract_raster_images(str(p), str(out))
    files = list(out.iterdir())
    assert len(files) == 1 and files[0].suffix == ".png"
    with Image.open(files[0]) as img:
        assert (img.width, img.height) == (120, 80)


def test_crop_with_overlay_text_geometry(tmp_path):
    p = blank_pdf(tmp_path / "crop.pdf")
    add_image(p, (100, 100, 220, 180))
    out = tmp_path / "crop.png"
    pdf_tools.crop_with_overlay_text(str(p), 0, (100, 100, 220, 180), str(out), dpi=288)
    with Image.open(out) as img:
        assert img.width == 120 * 4
        assert img.height == 80 * 4


def test_remove_text_keep_graphics(tmp_path):
    p = tmp_pdf = blank_pdf(tmp_path / "mixed.pdf")
    add_text(p, [(60, 100, "Подпись, которую надо удалить")])
    doc = fitz.open(p)
    doc[0].draw_rect(fitz.Rect(60, 200, 200, 300), color=(0, 0, 0), width=2)
    doc.saveIncr()
    doc.close()
    clean = tmp_path / "clean.pdf"
    pdf_tools.remove_text_keep_graphics(str(p), str(clean), [0])
    doc = fitz.open(clean)
    assert doc[0].get_text().strip() == ""
    assert len(doc[0].get_drawings()) >= 1
    doc.close()


def test_extract_graphs_from_clean_pdf(tmp_path):
    p = blank_pdf(tmp_path / "clean_src.pdf")
    add_image(p, (50, 50, 170, 130))
    out = tmp_path / "figs"
    out.mkdir()
    pdf_tools.extract_graphs_from_clean_pdf(
        str(p), str(out), {"fig1": {"page": 0, "bbox": (50, 50, 170, 130)}}, dpi=144)
    with Image.open(out / "fig1.png") as img:
        assert img.width == 120 * 2
        assert img.height == 80 * 2


# --- проверка полей (гейт вёрстки) ---

def test_margin_check_clean(tmp_path):
    p = blank_pdf(tmp_path / "clean_m.pdf")
    add_text(p, [(80, 400, "Текст внутри полосы набора")])
    assert margin_check(str(p)) == []


def test_margin_check_ink_in_margin(tmp_path):
    p = blank_pdf(tmp_path / "dirty_m.pdf")
    doc = fitz.open(p)
    doc[0].draw_rect(fitz.Rect(10, 300, 30, 500), fill=(0, 0, 0))
    doc.saveIncr()
    doc.close()
    hits = margin_check(str(p))
    assert hits and hits[0][0] == 1 and hits[0][1] > 0


# --- verify_translation: смоук на синтетике ---

def test_verify_translation_smoke(tmp_path, capsys):
    md = tmp_path / "tr.md"
    md.write_text("Формула $$x=1 \\qquad\\text{(1)}$$ и ещё $$y=2 \\qquad\\text{(2)}$$\n")
    p = blank_pdf(tmp_path / "tr.pdf")
    add_text(p, [(60, 100, "Введение (1) и (2)")])
    verify_translation.verify_translation(str(md), str(p))
    out = capsys.readouterr().out
    assert "Verification complete" in out
    assert "English section markers" not in out


def test_verify_translation_flags_markers(tmp_path, capsys):
    md = tmp_path / "tr2.md"
    md.write_text("текст \\qquad\\text{(1)}\n")
    p = blank_pdf(tmp_path / "tr2.pdf")
    add_text(p, [(60, 100, "Introduction (1) ??")])
    verify_translation.verify_translation(str(md), str(p))
    out = capsys.readouterr().out
    assert "English section markers" in out
    assert "'??'" in out


# --- интеграционный: tex_log_check требует pandoc + xelatex ---

@pytest.mark.skipif(not (shutil.which("pandoc") and shutil.which("xelatex")),
                    reason="нужны pandoc и xelatex")
def test_tex_log_check_no_overfull(tmp_path, monkeypatch):
    from check_layout import tex_log_check
    # tex_log_check пишет chk.* относительно cwd — изолируем tmp_path,
    # иначе прогон тестов из каталога скилла мусорит в него
    monkeypatch.chdir(tmp_path)
    template = subprocess.run(["pandoc", "-D", "latex"], capture_output=True,
                              text=True, check=True).stdout
    tpl = tmp_path / "tpl.tex"
    tpl.write_text(template.replace(r"\usepackage{lmodern}",
                                    r"% \usepackage{lmodern}"))
    md = tmp_path / "doc.md"
    md.write_text("---\ntitle: Тест\n---\n\nПривет, мир.\n")
    bad, errs, _ = tex_log_check(str(md), template=str(tpl))
    assert errs == []
    assert bad == []
