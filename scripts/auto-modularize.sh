#!/bin/bash
# auto-modularize.sh — автоматизация шага модуляризации CP-036
# Использование: auto-modularize.sh <N> <module_name> <prompt_file>
set -euo pipefail

N="${1:?номер шага (4, 5, ...)}"
MODULE="${2:?имя модуля (config, checkpoint, ...)}"
PROMPT_FILE="${3:?путь к промпту}"

WS="/mnt/ai-ssd/ai-system/projects/modularize"
AI="$HOME/ai-system"

echo "=== Шаг $N/13: модуль research.$MODULE ==="

# 1. Очистить workspace
rm -rf "$WS"
mkdir -p "$WS/research"

# 2. Скопировать актуальные файлы
cp "$AI/scripts/research_runner.py" "$WS/"
cp "$AI/scripts/research/"*.py "$WS/research/"

# 3. Git init
cd "$WS"
git init -q
git config user.email "aider@local"
git config user.name "Aider"
git add . && git commit -qm "init step $N"

# 4. Aider
cd "$AI"
source /mnt/ai-ssd/hermes/hermes-agent/venv/bin/activate
source /mnt/ai-ssd/hermes/.env

echo "=== Aider запускается (timeout 900s) ==="
python3 scripts/aider_runner.py "$WS" "$(cat "$PROMPT_FILE")" \
  --task-id "cp036-step${N}-$(date +%s)" \
  --timeout 900 2>&1 | tail -15

# 5. Проверка в workspace
cd "$WS"
python3 -m py_compile research/*.py research_runner.py && echo "✓ py_compile OK"

# 6. Копирование обратно
cp research_runner.py "$AI/scripts/research_runner.py"
for f in research/*.py; do
  [ "$f" = "research/__init__.py" ] && continue
  cp "$f" "$AI/scripts/research/"
done
echo "✓ Скопировано в $AI/scripts/"

# 7. Pytest в ~/ai-system
cd "$AI"
python3 -m pytest tests/ -q 2>&1 | tail -3

echo ""
echo "=== Шаг $N готов. Проверь результат, потом: ==="
echo "  cd ~/ai-system"
echo "  ruff check --fix scripts/research/ scripts/research_runner.py"
echo "  ruff format scripts/research/ scripts/research_runner.py"
echo "  git add scripts/research/ scripts/research_runner.py"
echo "  git commit -m 'CP-036 (шаг $N/13): модуль research.$MODULE'"
echo "  git push origin main"
