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

## Установка

Каноническое место — `~/.agents/skills/` (нативно сканируется Kimi Code и
Codex CLI). Клонируем в отдельный каталог и выставляем симлинки: прямой клон
в `~/.agents/skills/` вложит скиллы на лишний уровень (`agent-skills/<имя>`)
и они не будут найдены:

    git clone git@github.com:heni/agent-skills.git ~/src/agent-skills
    ln -s ~/src/agent-skills/<имя> ~/.agents/skills/<имя>   # Kimi Code, Codex CLI
    ln -s ~/src/agent-skills/<имя> ~/.claude/skills/<имя>   # Claude Code

## Обновление

    cd ~/src/agent-skills && git pull

## Зависимости между скиллами

`agent-pipeline-init` ссылается на `review-fix-loop` (цикл качества §7
генерируемого AGENTS.md). Оба живут в этом репозитории; раздельная установка
не предполагается.

## Лицензия

MIT (см. LICENSE).
