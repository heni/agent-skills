#!/usr/bin/env bash
# Согласованность пайплайна. Гейт меряет то, что умеет мерить: наличие нарушений,
# не верность утверждений (см. AGENTS.md §6).
#
# Расширять ТОЛЬКО с подстановкой дефекта: внести нарушение, которое пункт обязан
# поймать, убедиться, что падает с внятным сообщением; убрать — снова молчит.
# Исключение из гейта — строка с маркером, а не файл: файл, исключённый ради
# своего же шаблона, уносит из проверки свои комментарии.
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
#    Шаблон — перечнем форм записи имени, а не одним примером.
if [ "$in_git" = 1 ]; then
  hits=$(git grep -nE 'AGENTS\.md|TODO\.md|HISTORY\.md|AI\.md|backlog\.md' -- . ':!tools/check.sh' 2>/dev/null)
  [ -n "$hits" ] && { err "отсылка к пайплайн-файлу в закоммиченном содержимом:"; echo "$hits" | head -5; }
fi

exit "$fail"
