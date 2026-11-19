#!/usr/bin/env bash
# Согласованность пайплайна. Гейт меряет то, что умеет мерить: наличие нарушений,
# не верность утверждений (см. AGENTS.md §6).
#
# Расширять ТОЛЬКО с подстановкой дефекта: внести нарушение, которое пункт обязан
# поймать, убедиться, что падает с внятным сообщением; убрать — снова молчит.
# Исключение из гейта — строка с маркером, а не файл: файл, исключённый ради
# своего же шаблона, уносит из проверки свои комментарии.
#
# Свежесть по mtime: после git clone/checkout все mtime — «сейчас», гейт свежести
# может ложно сработать. Лечится пересборкой артефактов, не touch.
#
# Режим --init full|core: сверка состава дерева с выбранными модулями (запускается
# после инициализации проекта и вручную при смене набора модулей).
set -u
cd "$(dirname "$0")/.." || exit 1
fail=0
err() { echo "check: $1"; fail=1; }

in_git=0
git rev-parse --is-inside-work-tree >/dev/null 2>&1 && in_git=1

# 1. Пайплайн-файлы не в git-индексе.
if [ "$in_git" = 1 ]; then
  for f in AGENTS.md TODO.md HISTORY.md AI.md AI backlog.md; do
    if [ -n "$(git ls-files -- "$f")" ]; then
      err "пайплайн-файл попал в индекс: $f"
    fi
  done
fi

# 2. Артефакты не старше своих исходников. Записывать пары "артефакт:исходник1,исходник2"
#    из фактической сборки проекта; пример ниже — закомментирован.
FRESHNESS='
# build/report.pdf:report.md,data.csv
'
while IFS=: read -r art srcs; do
  case "$art" in ''|\#*) continue ;; esac
  if [ ! -e "$art" ]; then
    err "артефакт отсутствует: $art"
    continue
  fi
  for src in ${srcs//,/ }; do
    [ -e "$src" ] || { err "исходник артефакта отсутствует: $src (для $art)"; continue; }
    [ "$src" -nt "$art" ] && err "протух: $art старше своего исходника $src"
  done
done <<< "$FRESHNESS"

# 3. В закоммиченном содержимом нет отсылок к пайплайн-файлам (см. AGENTS.md §5).
#    Границы слова: без \b «AI.md» совпадает с OPENAI.md. .gitignore исключён —
#    он обязан перечислять имена пайплайн-файлов. Шаблон — перечнем форм записи
#    имени, а не одним примером.
if [ "$in_git" = 1 ]; then
  hits=$(git grep -nE '\b(AGENTS|TODO|HISTORY|AI)\.md\b|\bbacklog\.md\b' -- . \
           ':(exclude).gitignore' ':(exclude)tools/check.sh' 2>/dev/null)
  [ -n "$hits" ] && { err "отсылка к пайплайн-файлу в закоммиченном содержимом:"; echo "$hits" | head -5; }
fi

# 4. Целостность AGENTS.md: ссылки §N резолвятся в заголовки, маркеров сборки не
#    осталось, нумерация разделов подряд. Живёт в гейте насовсем: ловит правки,
#    после которых ссылка ведёт в вырезанный раздел.
if [ -f AGENTS.md ]; then
  grep -qE '<!-- optional|<!-- /optional -->' AGENTS.md && err "маркеры сборки <!-- optional --> остались в AGENTS.md"
  secs=$(grep -oE '^## [0-9]+\.' AGENTS.md | grep -oE '[0-9]+')
  for r in $(grep -oE '§[0-9]+' AGENTS.md | grep -oE '[0-9]+' | sort -n | uniq); do
    grep -qx "$r" <<< "$secs" || err "AGENTS.md ссылается на §$r, а раздела $r нет"
  done
  prev=""
  for s in $secs; do
    if [ -n "$prev" ] && [ "$s" -ne "$((prev + 1))" ]; then
      err "дыра в нумерации разделов AGENTS.md: после $prev идёт $s"
    fi
    prev="$s"
  done
fi

# --init full|core: состав дерева соответствует наборам модулей.
if [ "${1:-}" = "--init" ]; then
  mode="${2:?укажите режим: --init full|core}"
  have() { [ -e "$1" ]; }
  case "$mode" in
    full)
      for f in AI.md AI/method.md docs/glossary.md; do
        have "$f" || err "режим full: отсутствует $f"
      done
      ;;
    core)
      for f in AI.md AI docs/glossary.md; do
        have "$f" && err "режим core: выключенный модуль присутствует: $f"
      done
      if grep -qiE 'glossary|AI\.md|петл|review-fix' AGENTS.md 2>/dev/null; then
        err "режим core: AGENTS.md упоминает выключенные модули"
      fi
      ;;
    *) err "неизвестный режим --init: $mode (full|core)" ;;
  esac
fi

exit "$fail"
