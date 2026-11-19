# agent-skills

Скиллы для кодинг-агентов, образующие наш сессионный пайплайн работы. Формат —
каталоговый SKILL.md (фронтматтер с `name`/`description`), совместимый с
экосистемой Agent Skills.

## Состав

| Скилл | Назначение |
|---|---|
| `agent-pipeline-init` | Инициализация проекта под сессионный пайплайн: `AGENTS.md` с правилами и чек-листом закрытия сессии, журналы (TODO/backlog/HISTORY), накопитель инсайтов (`AI.md` + главы `AI/`), глоссарий-источник правды, машинные гейты. Зависит от `review-fix-loop`. |
| `review-fix-loop` | Адаптивная петля review→fix: профили (code/prose/proof/config/data), детерминированные гейты первыми, структурированный леджер находок, триаж по настойчивости, защита от смещений ревьюера. |
| `math-paper-en` | Написание и аудит англоязычных математических статей (LaTeX): проза, нотация, цитаты, воспроизводимость экспериментов, pre-submission audit. |
| `scientific-paper-translation` | Перевод технических научных статей (IEEE, IFAC, ACM, CDC) с сохранением графики, формул, алгоритмов и двухколоночной вёрстки оригинала (pandoc + XeLaTeX). Код вынесен в `scripts/` (библиотека pdf_tools, драйвер pipeline, гейты check_layout/verify_translation), скелеты документов — в `templates/`, к ним pytest-тесты на синтетических PDF (`tests/`). |

## Установка

Каноническое место — `~/.agents/skills/` (нативно сканируется Kimi Code и
Codex CLI). Клонируем в отдельный каталог и выставляем симлинки: прямой клон
в `~/.agents/skills/` вложит скиллы на лишний уровень (`agent-skills/<имя>`)
и они не будут найдены:

    git clone git@github.com:heni/agent-skills.git ~/agent-skills
    ln -s ~/agent-skills/<имя> ~/.agents/skills/<имя>   # Kimi Code, Codex CLI
    ln -s ~/agent-skills/<имя> ~/.claude/skills/<имя>   # Claude Code

## Обновление

    cd ~/agent-skills && git pull

## Проверка целостности

    ./validate.py              # static checks over every skill directory
    ./validate.py --with-tests # also runs pytest where a skill has tests/

Checks: frontmatter (name matches the directory, description within the
indexing length limit), no changelogs or assembly markers left in SKILL.md,
`${KIMI_SKILL_DIR}` references resolve, scripts/*.py compile.

## История версий

История версий каждого скилла — в `HISTORY.md` в его каталоге (тело SKILL.md —
текущее состояние, журнал грузится по надобности).

## Зависимости между скиллами

`agent-pipeline-init` ссылается на `review-fix-loop` (цикл качества §7
генерируемого AGENTS.md). Оба живут в этом репозитории; раздельная установка
не предполагается.

## Лицензия

MIT (см. LICENSE).
