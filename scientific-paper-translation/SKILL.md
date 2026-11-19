---
name: scientific-paper-translation
description: Перевод технических научных статей (IEEE, IFAC, ACM, CDC) с полным сохранением графиков, формул, алгоритмов и двухколоночной вёрстки оригинала. Использовать при переводе статей на русский с извлечением векторной/растровой графики из PDF, воспроизведением псевдокода, таблиц и библиографии; pandoc + XeLaTeX как основной путь рендеринга; обязательный тест на overfull по логу компиляции и пиксельная проверка полей.
---
# НАВЫК: Перевод научных статей с извлечением графиков (v4)

## Описание
Комплексный навык для профессионального перевода технических научных статей (особенно IEEE, IFAC, ACM, CDC) с сохранением всех графиков, формул, алгоритмов и структуры. Использует pandoc + XeLaTeX как основной путь рендеринга. По умолчанию воспроизводит **колоночную раскладку оригинала** (двухколоночную для IEEE/CDC/L-CSS) и проверяет по логу компиляции, что ни одна формула, таблица или строка не выходит за границы колонки. Включает методы извлечения векторной и растровой графики из PDF, оформление псевдокода, библиографии и создание профессионально оформленного переведённого документа.

## Когда использовать этот навык
- Перевод научных статей на русский (или другой язык)
- Необходимость сохранить графики в высоком качестве
- Работа с PDF, содержащими смесь векторной графики и растровых изображений
- Создание профессионально оформленных переводов с LaTeX-формулами, алгоритмами и библиографией

---

## ИЗМЕНЕНИЯ В v4 (относительно v3)
- ✅ **Двухколоночная вёрстка по умолчанию**, если оригинал двухколоночный (Часть 2A): автоопределение раскладки, YAML-блок, правила для плавающих объектов, таблиц и широких формул
- ✅ **Обязательный тест на overfull**: разбор `.log` XeLaTeX, любой `Overfull \hbox` > 2 pt в двухколоночном режиме — блокер (Часть 11)
- ✅ Скрипт `check_layout.py`: overfull/underfull, LaTeX-ошибки, `??`, английские маркеры, пиксельная проверка полей
- ✅ Правила разбиения длинных формул под ширину колонки (`aligned`, `multline`, перенос слагаемых)
- ✅ **Стиль перевода**: безличный академический («в работе рассматривается», «предложен»), не «мы изучаем»; запрет на дословные кальки (fleet → группа/формация) — Часть 3
- ✅ Римская нумерация таблиц (`\thetable`), локализация ключевых слов `algpseudocode` в шаблоне
- ✅ Уточнена работа с `\tag` внутри amsthm: `\[ … \qquad\text{(N)} \]`, а не `\begin{equation}` (иначе двойная нумерация)

## ИЗМЕНЕНИЯ В v3 (относительно v2)
- ✅ Добавлен раздел по **алгоритмам и псевдокоду** (`algorithm`/`algpseudocode`) — критично для IEEE/CDC статей
- ✅ Добавлен **второй сценарий извлечения**: «сохранить текст векторных подписей при кропе»
- ✅ **Proactive workflow подбора bbox** через предварительный рендер всей страницы
- ✅ Раздел по **библиографии** в стиле `thebibliography`
- ✅ Добавлены **PDF-метаданные** через `hyperref`
- ✅ Расширена **проверка качества** (подсчёт формул, поиск битых ссылок)
- ✅ Добавлен раздел про **транслитерацию имён**
- ✅ Сокращён ReportLab fallback (помечен как deprecated)

---

## ОБЩАЯ СТРАТЕГИЯ

### Основной путь: pandoc + XeLaTeX
- **Формулы**: Полноценный LaTeX-рендеринг (дроби, суммы, интегралы, матрицы)
- **Алгоритмы**: Окружение `algorithm` + `algpseudocode` с локализованными ключевыми словами
- **Теоремы/Леммы**: Нативные окружения `amsthm`
- **Библиография**: Окружение `thebibliography` для IEEE-стиля
- **Таблицы**: `booktabs` с профессиональными стилями
- **Шрифты**: Через `fontspec` — любые системные шрифты для кириллицы
- **Качество**: Типографское, идентичное оригинальным IEEE-статьям

### Запасной путь: ReportLab (deprecated)
Использовать **только** если pandoc/xelatex недоступны. В современном окружении Claude pandoc + xelatex + DejaVu присутствуют всегда. См. Часть 8.

### Раскладка: одна или две колонки
**Правило:** если оригинал свёрстан в две колонки (IEEE Trans., L-CSS, CDC/ACC, IFAC, большинство конференций) — перевод делается **двухколоночным**, чтобы соответствие страниц/рисунков/таблиц с оригиналом сохранялось и документ читался как та же статья. Одноколоночный вариант — только если оригинал одноколоночный (arXiv-препринты в `article`, Automatica, SIAM) или если пользователь просил иначе. Автоопределение — Часть 2A.

### Как проверить окружение

```bash
# Шаг 1: Проверить наличие инструментов
which pandoc xelatex
pandoc --version | head -1
xelatex --version | head -1

# Шаг 2: Проверить ключевые LaTeX-пакеты
kpsewhich fontspec.sty amsmath.sty unicode-math.sty booktabs.sty \
          algorithm.sty algpseudocode.sty microtype.sty

# Шаг 3: Проверить кириллические шрифты
fc-list | grep -i "dejavu serif" | head -3
```

**Если всё есть → основной путь. lmodern может отсутствовать (обходится кастомным шаблоном).**

---

## ЧАСТЬ 1: ИЗВЛЕЧЕНИЕ ГРАФИКОВ ИЗ PDF

### 🎯 Proactive workflow определения координат

**Перед попытками угадать bbox — отрендерить всю страницу при высоком DPI и определить координаты визуально.** Это экономит 2–3 итерации.

```python
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
```

После просмотра определяем pixel-границы в превью, делим на `scale` — получаем PDF-координаты для финального кропа при высоком DPI.

### Три типа графики в PDF — три стратегии

| Тип графики                                        | Стратегия                          |
|----------------------------------------------------|------------------------------------|
| **A.** Чистое растровое изображение (графики matplotlib и т.п.) | `extract_image` — прямое извлечение |
| **B.** Растр + векторные подписи поверх (схемы с метками) | Прямой кроп **без удаления текста** |
| **C.** Векторная графика, перемешанная с текстом статьи | Удаление текста + кадрирование |

#### ✅ Стратегия A: Прямое извлечение встроенных изображений

Самая быстрая. Подходит для графиков из matplotlib, R, gnuplot — они в PDF лежат как готовые растровые изображения.

```python
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
```

**Когда применять:** размеры извлечённых изображений ≥ 800 px по ширине, и они визуально полные (все подписи на месте).

#### ✅ Стратегия B: Прямой кроп с сохранением векторного текста

**Критически важный кейс** для схем типа «узлы графа + векторные подписи стрелок». Растровая подложка извлекается через `extract_image`, **но подписи стрелок** (например, $\mathbf{u}_{i,j}^{[k]}$) **отрендерены как векторный текст поверх растра и в извлечённом PNG отсутствуют**.

Признак ситуации: после Стратегии A на схеме нет важных меток, которые видны в исходном PDF.

```python
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
```

**Workflow:**
1. `preview_page` → определить bbox визуально
2. `crop_with_overlay_text` с этим bbox
3. Если подпись «Fig. N.» оригинала попала в кроп — сузить нижнюю границу

#### ✅ Стратегия C: Удаление текста + кадрирование

Для случая, когда векторная графика **перемешана** с текстом статьи в одном content stream (раньше так делал TikZ в IEEE-шаблонах).

```python
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
```

### Удаление подписи «Fig. N.» из кропа

Часто английская подпись рисунка попадает в bbox. После определения общего bbox сузить y-границу на 30–60 PDF-pt, чтобы убрать подпись (она будет заменена на русскую через `\caption{}`).

### Система координат PDF

- Начало — **левый верхний угол** в PyMuPDF (`fitz.Rect`).
- Единицы: points (1/72 дюйма). Letter: 612×792, A4: 595×842.
- Для двухколоночного IEEE (Letter): левая колонка x ≈ 50–290, правая x ≈ 310–565.

---

## ЧАСТЬ 2: PANDOC + XELATEX (ОСНОВНОЙ ПУТЬ)

### Pipeline

```
Исходный PDF → Извлечение графиков → Написание Markdown+LaTeX → pandoc+xelatex → PDF
```

### Шаг 1: Подготовка окружения

```bash
pip install PyMuPDF Pillow --break-system-packages -q
which pandoc xelatex
fc-list | grep -i "dejavu"
```

### Шаг 2: Кастомный шаблон pandoc (обход lmodern)

```bash
pandoc -D latex > custom_template.tex
sed -i 's/\\usepackage{lmodern}/% \\usepackage{lmodern} % skipped/' custom_template.tex
```

### Шаг 3: Структура Markdown-файла

```markdown
---
title: "Название статьи на русском"
author:
  - "Авторы (транслитерированные)"
date: ""
documentclass: article
papersize: a4
fontsize: 10pt
geometry: "margin=2cm"
header-includes:
  - \usepackage{fontspec}
  - \setmainfont{DejaVu Serif}
  - \setsansfont{DejaVu Sans}
  - \setmonofont{DejaVu Sans Mono}
  - \usepackage{unicode-math}
  - \setmathfont{Latin Modern Math}
  - \usepackage{amsmath,amssymb,amsthm}
  - \usepackage{graphicx}
  - \usepackage{float}
  - \usepackage{booktabs}
  - \usepackage{caption}
  - \usepackage{algorithm}
  - \usepackage{algpseudocode}
  - \usepackage[hidelinks]{hyperref}
  - \hypersetup{pdftitle={Название},pdfauthor={Авторы},pdflang={ru-RU}}
  - \usepackage{enumitem}
  - \newtheorem{definition}{Определение}
  - \newtheorem{assumption}{Предположение}
  - \newtheorem{lemma}{Лемма}
  - \newtheorem{theorem}{Теорема}
  - \newtheorem*{remark}{Замечание}
  - \captionsetup{font=small,labelfont=bf}
  - \renewcommand{\abstractname}{Аннотация}
  - \renewcommand{\refname}{Литература}
  - \renewcommand{\figurename}{Рис.}
  - \renewcommand{\tablename}{Таблица}
  - \floatname{algorithm}{Алгоритм}
  - \renewcommand{\algorithmicrequire}{\textbf{Вход:}}
  - \renewcommand{\algorithmicensure}{\textbf{Выход:}}
---
```

### Шаг 4: Компиляция

```bash
pandoc translation.md \
  -o translation.pdf \
  --pdf-engine=xelatex \
  --template=custom_template.tex \
  -V colorlinks=true \
  -V linkcolor=blue
```

### ⚠️ КРИТИЧЕСКИЕ ОГРАНИЧЕНИЯ pandoc

#### Проблема: `\tag{}` внутри окружений amsthm

```
! Package amsmath Error: \tag not allowed here.
```

**Решение: заменить `\tag{N}` на `\qquad\text{(N)}`, а окружение — на `\[ … \]` (не `\begin{equation}`, иначе amsmath добавит свой номер):**

```python
import re
def fix_tags(content):
    return re.sub(r'\\tag\{([^}]+)\}',
                  lambda m: f'\\qquad\\text{{({m.group(1)})}}', content)
```

#### Проблема: Markdown `$$...$$` внутри `\begin{theorem}`

Pandoc конвертирует `$$...$$` в `\[...\]`, что может конфликтовать с amsthm. Внутри теорем использовать чистый LaTeX (`\begin{equation*}...\end{equation*}` или `\[...\]`).


---

## ЧАСТЬ 2A: ДВУХКОЛОНОЧНАЯ ВЁРСТКА (новое в v4)

### Автоопределение раскладки оригинала

```python
import fitz

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
```

Результат сообщать пользователю одной фразой («оригинал двухколоночный → перевод свёрстан в две колонки»).

### YAML для двух колонок

Отличия от одноколоночного шаблона — `classoption`, поля, `microtype`, `emergencystretch`:

```yaml
documentclass: article
classoption: twocolumn
papersize: a4
fontsize: 10pt
geometry: "margin=1.6cm, columnsep=0.6cm"
header-includes:
  # ... стандартный блок из Приложения ...
  - \usepackage{microtype}
  - \setlength{\emergencystretch}{3em}
  - \hyphenation{про-ек-ци-он-но-управ-ля-е-мый на-блю-да-те-лей вос-ста-нов-ле-ния}
```

DejaVu Serif широкий; без `microtype` + `emergencystretch` узкая колонка даёт рваные межсловные пробелы и overfull-строки. Список `\hyphenation` пополнять длинными терминами конкретной статьи, если в логе остаются underfull-строки.

### Плавающие объекты

| Объект | Одна колонка | Две колонки |
|---|---|---|
| `figure`, `table`, `algorithm` | `[H]` | `[!t]` (`[H]` рвёт колонки и оставляет пустоты) |
| Рисунок | `width=0.6\textwidth` | `width=\columnwidth` |
| Широкий рисунок/таблица на обе колонки | — | `figure*` / `table*` (всегда уходят наверх следующей страницы; только если в колонку не помещается даже с `\resizebox`) |
| Примечание под таблицей | `minipage{0.85\textwidth}` | `minipage{\columnwidth}` |

### Таблицы в колонке

Практически любая таблица IEEE шире колонки при DejaVu. Порядок действий:
1. `\small` или `\footnotesize`, `\setlength{\tabcolsep}{3.5pt}`, `@{}` по краям спецификации столбцов
2. Сократить заголовки/метки строк («без нормализации столбцов» → «без норм. столбцов»)
3. Если всё ещё не влезает — `\resizebox{\columnwidth}{!}{\begin{tabular}…\end{tabular}}` (масштабирует вместе со шрифтом; сначала шаги 1–2, иначе текст станет нечитаемым)
4. Крайний случай — `table*`

Шаблон:
```latex
\begin{table}[!t]
\centering
\caption{...}
\footnotesize
\setlength{\tabcolsep}{3.5pt}
\resizebox{\columnwidth}{!}{%
\begin{tabular}{@{}lccc@{}}
\toprule ... \bottomrule
\end{tabular}}
\par\smallskip
\begin{minipage}{\columnwidth}\small Примечание под таблицей. \end{minipage}
\end{table}
```

### Формулы в колонке

Ширина колонки ≈ 8.3 см; формула с двумя условиями через `\qquad` в неё обычно не помещается. Правила:
- `\qquad` → `\quad` → `\ ` — первое, что пробовать
- Два утверждения в одной строке (`A = B,\qquad C = D`) → `aligned` в две строки, `\tag` остаётся снаружи:
  ```latex
  \begin{equation}
  \begin{aligned}
  \Delta_j &= U_m^{\top}(\Gamma_j)_O U_m,\\
  \Phi &= [\,\operatorname{svec}\Delta_j\,]_{j\in V}
  \end{aligned} \tag{4}
  \end{equation}
  ```
- Длинная сумма → перенос слагаемого на следующую строку с `&\quad+`
- Условия после формулы (`i\in F,\ \eta_0\equiv 0`) → отдельная строка `aligned`
- `multline` — для одной длинной цепочки без выравнивания
- Номер уравнения, ушедший под формулу, — штатное поведение amsmath, не ошибка

**Внутри amsthm** (теорема/следствие) формулу с номером оформлять как `\[ … \qquad\text{(N)} \]`. `\begin{equation}` внутри теоремы даёт **вторую, автоматическую** нумерацию (2), (3) рядом с текстовой (5), (6).

### Аннотация и шапка

В `twocolumn` pandoc-шаблон ставит заголовок и аннотацию в одну колонку — допустимо. Аннотация на всю ширину (как в IEEE) требует `\twocolumn[...]` и ломает pandoc-шаблон; по умолчанию не делать.

### Тест на выход за границы колонки — ОБЯЗАТЕЛЬНО

Компилировать через промежуточный `.tex`, чтобы получить `.log`:

```bash
pandoc translation.md -s -o translation.tex --template=custom_template.tex
xelatex -interaction=nonstopmode translation.tex > /dev/null
grep -c "Overfull" translation.log        # должно быть 0
grep -A1 "Overfull" translation.log | head # какие строки .tex виноваты
```

Каждый `Overfull \hbox (N pt too wide) detected at line L` — открыть строку `L` в `translation.tex`, найти это место в `.md`, применить правила выше, пересобрать. В двухколоночном режиме **любой overfull > 2 pt — блокер**; сдавать документ с непустым списком нельзя. Underfull-строки — предупреждение (лечится `\hyphenation`), не блокер.

Итоговый PDF всё равно собирать штатной командой pandoc (Часть 2, Шаг 4) — `.tex`-сборка нужна только ради лога.

---

## ЧАСТЬ 3: ПРАВИЛА ПЕРЕВОДА НАУЧНЫХ СТАТЕЙ

### Структура перевода

1. **Заголовок** — перевести полностью
2. **Авторы** — транслитерировать (см. ниже подробнее)
3. **Аффилиации** — перевести названия университетов, в скобках можно дать оригинал
4. **Аннотация** — полный перевод
5. **Ключевые слова** — перевести
6. **Разделы** — сохранить нумерацию (I, II, III...)
7. **Подразделы** — сохранить буквенную нумерацию (A, B, C...)
8. **Формулы** — переменные латинские, текст вокруг на русском
9. **Теоремы/Леммы** — «Теорема 1:», «Лемма 2:», «Доказательство.»
10. **Рисунки** — «Рис. 1.», подписи перевести
11. **Таблицы** — «Таблица I.», содержимое перевести
12. **Алгоритмы** — «Алгоритм 1», ключевые слова локализованы
13. **Литература** — **оставить на языке оригинала**, имена авторов не транслитерировать


### Стиль изложения (новое в v4)

Русская математическая/техническая статья пишется в **безличном академическом стиле**; авторское «мы» допустимо, но не как основная конструкция. Ориентиры: Грамота.ру (научный стиль — пассив, безличные и неопределённо-личные конструкции), Сосинский «Как написать математическую статью по-английски» (набор клише), практика журналов РАН (АиТ, Матем. сборник, УМН).

| Английский оборот | Не так | Так |
|---|---|---|
| We study / We consider | Мы изучаем | В работе рассматривается / изучается |
| We propose X | Мы предлагаем X | Предложен X / Предлагается X |
| We prove / show | Мы доказываем | Доказана теорема / Показано, что |
| We give conditions | Мы даём условия | Получены условия |
| Our approach / our forcing | Наш подход / наше возбуждение | Предлагаемый подход / входное воздействие |
| In this paper we… | В этой статье мы… | В настоящей работе… |
| We run it on… | Мы запускаем его на… | Алгоритм применяется к… |
| Related work | Связанные работы | Обзор литературы |
| Contributions | Вклад | Основные результаты |
| Case study | Пример-исследование | Прикладной пример / модельный пример |
| Concluding remarks | Заключительные замечания | Заключение |
| Deployment (experimental setup) | Развёртывание | Постановка эксперимента |

**Не калькировать термины дословно.** Сверять, как понятие называется в русскоязычной литературе по предмету:

| English | Калька (плохо) | Норма |
|---|---|---|
| fleet (of robots) | флот | группа роботов / формация |
| shape (of formation) | форма | строй |
| reference signal | опорный сигнал | задающее воздействие |
| feedforward | упреждение | упреждающая составляющая / прямая связь |
| leader / followers | — | лидер (ведущий) / ведомые |
| solver | решатель | метод / алгоритм (восстановления, решения) |
| sweep | свип | перебор по сетке параметров |
| stacking (matrices) | стэкинг | вертикальная конкатенация / объединение |
| snapshot (sample) | снимок | отсчёт / выборочное значение |
| raw coordinates | сырые координаты | исходные координаты |
| oracle quantity | оракульная величина | недоступная на практике / идеальная (допустимо «оракульная» с пояснением) |
| i.i.d. | н.о.р. | независимые одинаково распределённые (при первом упоминании развернуть) |
| whitening | — | отбеливание (устоявшийся термин) |
| spikes (sparse anomalies) | пики | всплески (не «выбросы» — конфликт с outliers) |
| sensing matrix | сенсинг-матрица | матрица измерений |
| support (of a vector) | поддержка | носитель |
| round (algorithm iteration) | раунд | шаг / итерация («раунд» — только для communication rounds) |
| ride on connectivity | ехать на связности | обеспечиваться связностью |

Аббревиатуры методов (RIP, OMP, NNLS, BPDN) — оставлять латиницей с расшифровкой при первом упоминании; CS в тексте писать полностью — «сжатые измерения».

### Транслитерация имён авторов

| Случай                          | Как поступать                                |
|---------------------------------|----------------------------------------------|
| Славянские имена в оригинале на латинице (Tolstonogov, Granichin) | Восстановить кириллицу (Толстоногов, Граничин) |
| Иностранные имена (Cabecinhas, Batista, Pascoal, Xavier) | Транслитерировать в основном тексте (Кабесиньяс, Батишта, Пашкоал, Шавьер) |
| **В библиографии**              | **Всегда оригинал на латинице, никаких изменений** |
| Имена в благодарностях          | Транслитерировать или оставить оригинал + русское в скобках |
| Аффилиации                      | Перевести название, оригинал можно в скобках |

### Математическая терминология (RU)

| English                  | Русский                                  |
|--------------------------|------------------------------------------|
| steady state             | стационарное состояние                   |
| convergence              | сходимость                               |
| Lyapunov function        | функция Ляпунова                         |
| almost surely            | почти наверняка (п.н.)                   |
| eigenvalue               | собственное значение                     |
| algebraic connectivity   | алгебраическая связность                 |
| order parameter          | параметр порядка                         |
| pursuit-evasion          | преследование–уклонение                  |
| swarm                    | рой                                      |
| heading                  | курс                                     |
| noise                    | шум                                      |
| adjacency matrix         | матрица смежности                        |
| Laplacian                | лапласиан / матрица Лапласа              |
| phase transition         | фазовый переход                          |
| operator splitting       | расщепление операторов                   |
| consensus                | консенсус (часто без перевода)           |
| warm start / cold start  | тёплый / холодный старт                  |
| trust region             | доверительная область                    |
| smoothed approximation   | сглаженная аппроксимация                 |
| time of arrival (ToA)    | время прихода (ToA, оставлять аббревиатуру) |

### Что переводить, что нет в формулах

- **Переводить:** текст вокруг формул, названия переменных в описании
- **НЕ переводить:** сами формулы, имена переменных ($\beta_m$, $\Gamma_\text{rel}$, $V(t)$)
- **Оставлять:** стандартные обозначения (`arg`, `atan2`, `sgn`, `cos`, `sin`, `sup`, `inf`, `lim`)
- **Аббревиатуры методов:** ToA, TDoA, ADMM, DADMM, RSS, AoA — оставлять латинскими, с расшифровкой при первом упоминании

---

## ЧАСТЬ 4: РАБОТА С ФОРМУЛАМИ В LaTeX

### Базовые конструкции

```latex
% Инлайн
$e^{i\theta_j} \equiv (\cos\theta_j, \sin\theta_j)$

% Выносная с номером (вне amsthm)
$$V(t) = \frac{1}{2}\sum_m\sum_i\left(\sigma_i^m(t)\right)^2 \qquad\text{(15)}$$

% Система уравнений (выровненная)
$$\begin{aligned}
\mathbf{x}_i^{[k+1]} &= \arg\min_{\mathbf{x}_i} f_i(\mathbf{x}_i) + \tfrac{1}{2}\sum_{j \in \mathcal{N}_i}\|\mathbf{x}_i - \mathbf{y}_{i,j}^{[k]}\|^2_{\Theta} \\
\mathbf{y}_{i,j}^{[k+1]} &= \tfrac{1}{2}\left(\mathbf{x}_i^{[k+1]} + \mathbf{x}_j^{[k+1]}\right)
\end{aligned}$$

% Линейная система (матрица)
$$\begin{bmatrix} 1 + \rho_t|\mathcal{N}| & 1/v \\ 1/v & 1/v^2 + \rho_p|\mathcal{N}| \end{bmatrix}
\begin{bmatrix} t^* \\ r^* \end{bmatrix} =
\begin{bmatrix} \tau + \rho_t|\mathcal{N}|\bar{a}_t \\ \tau/v + \rho_p|\mathcal{N}|\|\mathbf{d}\| \end{bmatrix} \qquad\text{(24)}$$

% Операторы
$\operatorname{atan2}(\mathbf{u})$, $\operatorname{sgn}(x)$, $\arg\min_x$, $\limsup_{t\to\infty}$

% Нормы (взвешенная)
$\|\mathbf{x}\|_2$, $\|\mathbf{x}\|_\Theta$

% Множества и кардинальность
$\mathcal{N}_i = \{j \mid (i,j) \in \mathcal{E}\}$, $|\mathcal{N}|$

% Вероятность
$\mathbb{P}(A)$, $\mathbb{E}[\xi]$, $\operatorname{Var}[\xi]$

% Индексы итераций
$\mathbf{x}_i^{[k+1]}$, $\mathbf{u}_{i,j}^{[k]}$
```

### Греческие буквы и спецсимволы

```latex
\alpha, \beta, \gamma, \delta, \varepsilon, \theta, \kappa,
\lambda, \mu, \xi, \pi, \rho, \sigma, \tau, \phi, \varphi, \psi, \omega
\Gamma, \Delta, \Theta, \Lambda, \Phi, \Psi, \Omega
\mathbb{R}, \mathbb{Z}, \mathbb{N}, \mathbb{P}, \mathbb{E}
\mathcal{L}, \mathcal{G}, \mathcal{F}, \mathcal{V}, \mathcal{E}, \mathcal{N}
```

### Опциональные \newcommand для удобства

Если в статье часто встречаются одни и те же конструкции, объявить в `header-includes`:

```latex
\newcommand{\R}{\mathbb{R}}
\newcommand{\E}{\mathbb{E}}
\newcommand{\norm}[1]{\left\|#1\right\|}
\newcommand{\inner}[2]{\langle #1, #2 \rangle}
```

---

## ЧАСТЬ 5: ВСТАВКА РИСУНКОВ И ТАБЛИЦ

### Рисунки

```latex
\begin{figure}[H]
\centering
\includegraphics[width=0.85\textwidth]{extracted_graphs/fig2.png}
\caption{Подпись на русском с формулами $\mathbf{y}_{i,j}$.}
\end{figure}
```

### Многопанельный рисунок (top/bottom)

```latex
\begin{figure}[H]
\centering
\includegraphics[width=0.85\textwidth]{extracted_graphs/fig5_top.png}\\[4pt]
\includegraphics[width=0.85\textwidth]{extracted_graphs/fig5_bottom.png}
\caption{Сверху: оценённое время эмиссии. Снизу: оценённое положение цели.}
\end{figure}
```

**Рекомендации по ширине (одноколоночный документ):**
- Одноколоночная фигура: `width=0.45\textwidth`
- Двухколоночная фигура: `width=0.85\textwidth`
- Схема с подписями стрелок: `width=0.95\textwidth`
- Полная ширина: `width=\textwidth`

**В двухколоночном документе** — всегда `width=\columnwidth` и `[!t]`, см. Часть 2A.

### Таблицы

```latex
\begin{table}[H]
\centering
\caption{Параметры системы}
\begin{tabular}{llc}
\toprule
Символ & Величина & Значение \\
\midrule
$N$ & Число агентов в каждом рое & 100 \\
$v_0$ & Постоянная скорость агента & 1 \\
$R_c$ & Радиус кооперативного взаимодействия & 50 \\
\bottomrule
\end{tabular}
\end{table}
```

---

## ЧАСТЬ 6: АЛГОРИТМЫ И ПСЕВДОКОД (новое в v3)

В IEEE/CDC/IFAC-статьях псевдокод встречается почти всегда. Используем пакеты `algorithm` (плавающее окружение) и `algpseudocode` (синтаксис).

### Подключение и локализация

В `header-includes`:

```latex
\usepackage{algorithm}
\usepackage{algpseudocode}
\floatname{algorithm}{Алгоритм}
\renewcommand{\algorithmicrequire}{\textbf{Вход:}}
\renewcommand{\algorithmicensure}{\textbf{Выход:}}
% При желании также:
\renewcommand{\algorithmicwhile}{\textbf{пока}}
\renewcommand{\algorithmicdo}{\textbf{выполнить}}
\renewcommand{\algorithmicend}{\textbf{конец}}
\renewcommand{\algorithmicif}{\textbf{если}}
\renewcommand{\algorithmicthen}{\textbf{то}}
\renewcommand{\algorithmicelse}{\textbf{иначе}}
\renewcommand{\algorithmicfor}{\textbf{для}}
\renewcommand{\algorithmicreturn}{\textbf{вернуть}}
```

**Примечание:** многие переводчики оставляют английские `for/while/if/then/end` — это норма для научного русского текста и улучшает читаемость. Локализовать имеет смысл только `Require/Ensure` и `\Comment{}`.

### Структура блока

```latex
\begin{algorithm}[H]
\caption{Распределённый алгоритм ToA-локализации}
\begin{algorithmic}[1]
\Require Граф $\mathcal{G} = (\mathcal{N}, \mathcal{E})$, параметры $\sigma, \rho_t, \rho_p$
\For{$i \in \mathcal{N}$} \Comment{Подготовка, параллельно}
  \State Инициализировать $\mathbf{x}_i^{[0]}$ согласно (11)
  \State Передать $\mathbf{x}_i^{[0]}$ всем соседям $j \in \mathcal{N}_i$
  \For{$j \in \mathcal{N}_i$}
    \State $\mathbf{y}_{i,j}^{[0]} \gets \tfrac{1}{2}(\mathbf{x}_i^{[0]} + \mathbf{x}_j^{[0]})$
    \State $\mathbf{u}_{i,j}^{[0]} \gets 0$
  \EndFor
\EndFor
\For{$k = 0, 1, 2, \ldots$} \Comment{Главный цикл DADMM}
  \State \Comment{Этап 1}
  \State Передать $\mathbf{u}_{i,j}^{[k]}$ всем соседям
  \State Обновить $\mathbf{x}_i^{[k+1]}$ (см. Приложение A)
  \State \Comment{Этап 2}
  \State $\mathbf{y}_{i,j}^{[k+1]} \gets \tfrac{1}{2}(\mathbf{x}_i^{[k+1]} + \mathbf{x}_j^{[k+1]} + \mathbf{u}_{i,j}^{[k]} + \mathbf{u}_{j,i}^{[k]})$
  \State \Comment{Этап 3}
  \State $\mathbf{u}_{i,j}^{[k+1]} \gets \mathbf{u}_{i,j}^{[k]} + \mathbf{x}_i^{[k+1]} - \mathbf{y}_{i,j}^{[k+1]}$
  \State \Comment{Проверка останова}
  \State $r_i \gets \max_{j \in \mathcal{N}_i}\|\mathbf{x}_i^{[k+1]} - \mathbf{y}_{i,j}^{[k+1]}\|_\Theta$
  \If{$r_i \le \varepsilon_{\text{feas}}$ \textbf{и} $s_i \le \varepsilon_{\text{conv}}$}
    \State Завершить итерации в приёмнике $i$
  \EndIf
\EndFor
\end{algorithmic}
\end{algorithm}
```

### Полезные команды algpseudocode

| Команда                  | Назначение                                |
|--------------------------|-------------------------------------------|
| `\State`                 | Обычная строка                            |
| `\Comment{текст}`        | Комментарий справа (через `▷`)            |
| `\If{...}` ... `\EndIf`  | Условие                                   |
| `\For{...}` ... `\EndFor`| Цикл                                      |
| `\While{...}` ... `\EndWhile` | Цикл с условием                      |
| `\Function{Имя}{арг}` ... `\EndFunction` | Функция                   |
| `\Return X`              | Возврат значения                          |
| `\gets`                  | Оператор присваивания `←`                 |

### Альтернатива: пакет `algorithmicx` напрямую

Если нужен более тонкий контроль (свои ключевые слова, нестандартное оформление) — использовать `algorithmicx` напрямую вместо `algpseudocode`.

---

## ЧАСТЬ 7: БИБЛИОГРАФИЯ (новое в v3)

### Вариант 1: Окружение `thebibliography` (рекомендуемый для IEEE-стиля)

Даёт идеальную согласованность с оригиналом — теги [1], [2] в тексте автоматически соответствуют записям.

```latex
\begin{thebibliography}{99}
\bibitem{ref1} G. C. Hays et al., "Translating Marine Animal Tracking Data into Conservation Policy and Management," \textit{Trends in Ecology \& Evolution}, vol. 34, no. 5, pp. 459--473, May 2019.

\bibitem{ref2} M. Espinoza, T. J. Farrugia, D. M. Webber, F. Smith, and C. G. Lowe, "Testing a new acoustic telemetry technique to quantify long-term, fine-scale movements of aquatic animals," \textit{Fisheries Research}, vol. 108, no. 2-3, pp. 364--371, Mar. 2011.

% ... и так далее
\end{thebibliography}
```

В Markdown-файле вставлять блок как чистый LaTeX (pandoc его не трогает).

### Вариант 2: Markdown-список (проще, но без автонумерации)

```markdown
# Литература

[1] G. C. Hays et al., "Translating Marine Animal Tracking Data...", *Trends in Ecology & Evolution*, vol. 34, no. 5, pp. 459–473, May 2019.

[2] M. Espinoza et al., "Testing a new acoustic telemetry technique...", *Fisheries Research*, vol. 108, no. 2-3, pp. 364–371, Mar. 2011.
```

**Когда какой:** для академической публикации — Вариант 1; для предварительного перевода или внутреннего использования — Вариант 2 проще и быстрее.

### Правила оформления

- **Имена авторов:** всегда оригинал, не транслитерировать
- **Названия работ:** оригинал, в кавычках
- **Журналы/конференции:** `\textit{}` или `*курсив*`
- **Тире в номерах страниц:** `--` (en-dash) в LaTeX, `–` (Unicode) в Markdown
- **Знак &:** `\&` в LaTeX, `&` в Markdown

---

## ЧАСТЬ 8: REPORTLAB FALLBACK (deprecated)

⚠️ В современном окружении Claude pandoc + xelatex доступны почти всегда. Этот раздел оставлен только на крайний случай.

```bash
pip install PyMuPDF reportlab Pillow --break-system-packages
```

Ключевые моменты:
- Регистрация шрифтов DejaVu через `pdfmetrics.registerFont`
- Формулы — Unicode-приближение (нет полноценных дробей, матриц, вложенных индексов)
- Для сложных формул — рендерить через matplotlib как PNG

**Ограничения:**
- Нет `\frac{}{}` — только `a/b`
- Нет матриц
- Нет вложенных индексов
- Нет `\sqrt{}` — только `√`

Если попали в ситуацию, где нужен ReportLab — попробуйте сначала установить недостающий компонент pandoc/xelatex/fontspec.

---

## ЧАСТЬ 9: ПОЛНЫЙ WORKFLOW

```
1. Анализ исходного PDF
   ├── detect_columns → выбрать одно-/двухколоночный YAML (Часть 2A)
   ├── preview_page для каждой страницы с рисунками
   ├── extract_raster_images — попробовать Стратегию A
   └── Решить по каждому рисунку: A, B или C

2. Извлечение графиков
   ├── A: прямое extract_image
   ├── B: прямой crop_with_overlay_text (для схем с метками)
   └── C: remove_text_keep_graphics + кадрирование
   Сохранить всё в extracted_graphs/

3. Перевод текста
   ├── Структурировать по разделам
   ├── Перевести с сохранением формул
   ├── Транслитерация имён в тексте, оригинал в библиографии
   └── Алгоритмы — переписать в окружении algorithm

4. Сборка документа
   ├── Кастомный template (обход lmodern)
   ├── header-includes с algorithm, hyperref, метаданные
   ├── pandoc -s → .tex → xelatex → .log (проверка Overfull)
   └── pandoc → xelatex → PDF

5. Верификация (см. Часть 11): check_layout.py, визуальный просмотр страниц с формулами/таблицами
```

### Пример: вызов всего pipeline

```python
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
```

---

## ЧАСТЬ 10: ЧАСТЫЕ ПРОБЛЕМЫ И РЕШЕНИЯ

### Проблема 1: `lmodern.sty not found`
**Решение:** Кастомный шаблон без `\usepackage{lmodern}` (см. Часть 2, Шаг 2).

### Проблема 2: `\tag not allowed here`
**Решение:** Заменить `\tag{N}` на `\qquad\text{(N)}` или вынести формулу за пределы `amsthm`.

### Проблема 3: Кириллица — квадратики
**Решение:** `\setmainfont{DejaVu Serif}` в `header-includes`.

### Проблема 4: На схеме отсутствуют важные подписи
**Причина:** Векторный текст поверх растровой подложки, удалённый Стратегией C.
**Решение:** Использовать Стратегию B — прямой кроп без `apply_redactions`.

### Проблема 5: Координаты графиков не подобраны
**Решение:** `preview_page` → визуальный осмотр → деление пиксельных координат на scale.

### Проблема 6: Низкое качество графиков
**Решение:** `mat = fitz.Matrix(600/72, 600/72)` или 1200/72 для экстра-качества.

### Проблема 7: Слишком большой файл (> 20 МБ)
**Решение:** Ужать большие PNG перед вставкой:

```python
from PIL import Image
img = Image.open("graph.png")
if img.width > 2000:
    ratio = 2000 / img.width
    img = img.resize((2000, int(img.height * ratio)), Image.LANCZOS)
img.save("graph_opt.png", optimize=True, compress_level=9)
```

### Проблема 8: Алгоритм ломает компиляцию
**Возможные причины:**
- Не подключён `algorithm` или `algpseudocode`
- В `\State` есть `&` или `_` без экранирования
- Незакрытый `\For`/`\If` (нужен `\EndFor`/`\EndIf`)

**Решение:** проверить полные пары начала/конца, экранировать спецсимволы.

### Проблема 10: Формулы/таблицы вылезают за колонку
**Решение:** Часть 2A — `aligned`/перенос слагаемых для формул, `\resizebox{\columnwidth}` для таблиц, `[!t]` вместо `[H]`. Проверять `grep Overfull translation.log` до нуля.

### Проблема 11: Двойная нумерация формул в теоремах — (5) и рядом (2)
**Причина:** `\begin{equation}` внутри amsthm с текстовым `\qquad\text{(5)}`.
**Решение:** внутри теорем только `\[ … \qquad\text{(N)} \]`.

### Проблема 12: Таблицы нумеруются арабскими, в оригинале — римские
**Решение:** `\renewcommand{\thetable}{\Roman{table}}` в `header-includes`.

### Проблема 13: Регулярка по `\begin{equation}…\end{equation}` с `re.S` захватывает несколько формул
**Причина:** нежадный `.*?` всё равно стартует с первого `\begin{equation}` в файле и тянется до первого подходящего конца.
**Решение:** `(?:(?!\\end\{equation\}).)*?` вместо `.*?`, либо правки по номерам строк с последующим `grep -n 'begin{equation}\|end{equation}\|^\\\[\|^\\\]'` для проверки парности.

### Проблема 9: Длинные URL ломают вёрстку
**Решение:** обернуть в `\url{...}` (требует `hyperref`):
```markdown
доступны на \url{https://github.com/user/repo}
```

---

## ЧАСТЬ 11: РАСШИРЕННАЯ ПРОВЕРКА КАЧЕСТВА (новое в v3)

После компиляции — не только проверить, что PDF открывается, но и подтвердить целостность контента.

### Скрипт верификации

```python
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
```


### Скрипт `check_layout.py` (новое в v4): overfull + выход за поля

Запускать после каждой сборки. Первая часть читает `.log` XeLaTeX, вторая — растрирует страницы и ищет тёмные пиксели в полях (ловит то, что не попадает в лог: `\includegraphics` шире колонки, ошибки `\resizebox`).

```python
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
```

```bash
python3 check_layout.py translation.md translation.pdf
```

Критерий сдачи в двухколоночном режиме: **0 overfull > 2 pt, 0 LaTeX-ошибок, нет `??`**. Пиксельная проверка полей может давать ложные срабатывания на номерах страниц и колонтитулах — смотреть глазами.

### Визуальная проверка страниц

Отрендерить страницы с формулами, таблицами и алгоритмом (`page.get_pixmap(matrix=fitz.Matrix(1.3, 1.3))`) и просмотреть. Типичные дефекты в две колонки: таблица «наезжает» на соседнюю колонку, формула с `\qquad` выходит за правый край, `[H]` оставляет полупустую колонку, `\resizebox` сделал таблицу нечитаемо мелкой.

### Проверка warnings от xelatex

```bash
pandoc translation.md -o translation.pdf --pdf-engine=xelatex \
  --template=custom_template.tex 2>&1 | grep -iE "warning|overfull|underfull"
```

### Что обязательно проверять глазами

- Все рисунки на месте и правильно подписаны
- Подписи стрелок на схемах не потеряны
- Формулы правильно отрендерены (особенно матрицы, дроби в дробях, индексы)
- Алгоритм отображается с правильными отступами и нумерацией строк
- Литература имеет ту же длину, что и в оригинале

---

## ЧАСТЬ 12: ЧЕКЛИСТ КАЧЕСТВА

### Перед началом
- [ ] `which pandoc xelatex` — оба есть
- [ ] DejaVu установлен (`fc-list | grep -i dejavu`)
- [ ] `kpsewhich algorithm.sty algpseudocode.sty` — оба есть
- [ ] Созданы рабочие директории

### Извлечение графиков
- [ ] Использован `preview_page` перед подбором bbox
- [ ] Для каждого рисунка выбрана правильная стратегия (A/B/C)
- [ ] Все подписи стрелок на схемах на месте
- [ ] DPI ≥ 288 для кропов, ≥ 600 для критичных деталей
- [ ] Формат PNG (не JPEG для графиков!)

### Перевод текста
- [ ] Сохранена структура: введение, разделы, выводы
- [ ] Все формулы корректно оформлены в LaTeX
- [ ] Математические обозначения согласованы
- [ ] Ссылки на рисунки/таблицы/алгоритмы на месте
- [ ] Алгоритмы оформлены в окружении `algorithm`
- [ ] Имена авторов транслитерированы в тексте
- [ ] Литература — оригинал, без транслитерации
- [ ] PDF-метаданные заполнены через `hyperref`

### Вёрстка
- [ ] Раскладка (1/2 колонки) соответствует оригиналу
- [ ] В twocolumn: `[!t]`, `\columnwidth`, `microtype`, `emergencystretch`
- [ ] `grep -c Overfull translation.log` == 0 (или все ≤ 2 pt)
- [ ] Таблицы читаемы после `\resizebox` (не мельче `\footnotesize`)

### Стиль
- [ ] Безличный стиль: нет «мы изучаем / мы предлагаем / наш»
- [ ] Термины сверены с русскоязычной литературой, кальки (флот, свип, стэкинг, решатель) устранены
- [ ] Заголовки разделов — по таблице Части 3 (Обзор литературы, Основные результаты, Заключение)

### Финальная проверка
- [ ] Запущены `verify_translation` и `check_layout.py` — нет предупреждений
- [ ] PDF открывается корректно
- [ ] Все изображения на месте
- [ ] Формулы рендерятся правильно
- [ ] Нет «??» в тексте PDF
- [ ] Нет английских заголовков-обрывков
- [ ] Размер файла разумный (< 20 МБ)

---

## ЧАСТЬ 13: БИБЛИОТЕКИ И ЗАВИСИМОСТИ

### Основной путь (pandoc + xelatex)

Обычно уже установлены в окружении Claude:
- `pandoc`, `xelatex`
- LaTeX-пакеты: `fontspec`, `amsmath`, `unicode-math`, `booktabs`, `float`, `algorithm`, `algpseudocode`, `hyperref`, `caption`, `graphicx`

Дополнительно ставить:
```bash
pip install PyMuPDF Pillow --break-system-packages
```

### Системные шрифты

```bash
# Ubuntu/Debian (обычно уже установлены)
apt-get install fonts-dejavu fonts-dejavu-core fonts-dejavu-extra
fc-list | grep DejaVu  # проверка
```

### Запасной путь (ReportLab, deprecated)

```bash
pip install PyMuPDF reportlab Pillow --break-system-packages
```

---

## ПРИЛОЖЕНИЕ: МИНИМАЛЬНЫЙ ШАБЛОН header-includes

Готовый блок для копирования в YAML frontmatter:

```yaml
header-includes:
  - \usepackage{fontspec}
  - \setmainfont{DejaVu Serif}
  - \setsansfont{DejaVu Sans}
  - \setmonofont{DejaVu Sans Mono}
  - \usepackage{unicode-math}
  - \setmathfont{Latin Modern Math}
  - \usepackage{amsmath,amssymb,amsthm}
  - \usepackage{graphicx,float,booktabs,caption,enumitem}
  - \usepackage{algorithm,algpseudocode}
  - \usepackage[hidelinks]{hyperref}
  - \hypersetup{pdftitle={Название},pdfauthor={Авторы},pdflang={ru-RU}}
  - \newtheorem{theorem}{Теорема}
  - \newtheorem{lemma}{Лемма}
  - \newtheorem{definition}{Определение}
  - \newtheorem*{remark}{Замечание}
  - \captionsetup{font=small,labelfont=bf}
  - \renewcommand{\abstractname}{Аннотация}
  - \renewcommand{\refname}{Литература}
  - \renewcommand{\figurename}{Рис.}
  - \renewcommand{\tablename}{Таблица}
  - \renewcommand{\thetable}{\Roman{table}}
  - \floatname{algorithm}{Алгоритм}
  - \renewcommand{\algorithmicrequire}{\textbf{Вход:}}
  - \renewcommand{\algorithmicensure}{\textbf{Выход:}}
  - \renewcommand{\algorithmicwhile}{\textbf{пока}}
  - \renewcommand{\algorithmicdo}{\textbf{выполнять}}
  - \renewcommand{\algorithmicend}{\textbf{конец}}
  - \renewcommand{\algorithmicif}{\textbf{если}}
  - \renewcommand{\algorithmicthen}{\textbf{то}}
  - \renewcommand{\algorithmicelse}{\textbf{иначе}}
  - \renewcommand{\algorithmicreturn}{\textbf{вернуть}}
  - \newcommand{\R}{\mathbb{R}}
  - \newcommand{\E}{\mathbb{E}}
  - \newcommand{\Var}{\operatorname{Var}}
  - \newcommand{\diag}{\operatorname{diag}}
```

### Двухколоночный вариант — добавить к YAML выше

```yaml
classoption: twocolumn
geometry: "margin=1.6cm, columnsep=0.6cm"
header-includes:
  # ... всё из блока выше плюс:
  - \usepackage{microtype}
  - \setlength{\emergencystretch}{3em}
```
