#!/bin/bash
# Проверка перед коммитом: синтаксис + static analysis + тесты + secrets.
set -u

REPO_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/.." && pwd)"
cd "$REPO_DIR" || { echo "❌ не могу перейти в $REPO_DIR"; exit 1; }
export PYTHONDONTWRITEBYTECODE=1

VENV="/mnt/ai-ssd/hermes/hermes-agent/venv/bin"
PY="$VENV/python3"
RUFF="$VENV/ruff"

# ── 1. Python синтаксис ────────────────────────────────────────
echo "🔍 === Python синтаксис ==="
py_count=0
for f in scripts/*.py; do
    [ -f "$f" ] || continue
    python3 -c 'import sys; compile(open(sys.argv[1], encoding="utf-8").read(), sys.argv[1], "exec")' "$f" \
        || { echo "❌ синтаксическая ошибка: $f"; exit 1; }
    py_count=$((py_count + 1))
done
[ "$py_count" -gt 0 ] || { echo "❌ не найдено ни одного .py"; exit 1; }
echo "✅ Python: $py_count файлов"

# ── 2. Bash синтаксис ──────────────────────────────────────────
echo ""
echo "🔍 === Bash синтаксис ==="
sh_count=0
for f in scripts/*.sh; do
    [ -f "$f" ] || continue
    bash -n "$f" || { echo "❌ синтаксическая ошибка: $f"; exit 1; }
    sh_count=$((sh_count + 1))
done
[ "$sh_count" -gt 0 ] || { echo "❌ не найдено ни одного .sh"; exit 1; }
echo "✅ Bash: $sh_count файлов"

# ── 3. ruff static analysis ────────────────────────────────────
echo ""
echo "🔍 === ruff (F,E9) ==="
if [ -x "$RUFF" ]; then
    if ! "$RUFF" check --select F,E9 scripts/ tests/; then
        echo "❌ ruff: ошибки найдены"; exit 1
    fi
    echo "✅ ruff: All checks passed"
else
    echo "⚠ ruff не найден: $RUFF — пропускаю"
fi

# ── 4. pytest ──────────────────────────────────────────────────
echo ""
echo "🔍 === pytest ==="
if [ -x "$PY" ]; then
    if ! "$PY" -m pytest tests/ -q --no-header 2>&1 | tail -3; then
        echo "❌ pytest: тесты упали"; exit 1
    fi
else
    echo "⚠ python venv не найден: $PY — пропускаю"
fi

# ── 5. gitleaks (secret scan) ──────────────────────────────────
echo ""
echo "🔍 === gitleaks ==="
if command -v gitleaks >/dev/null 2>&1; then
    if ! gitleaks detect --no-git --source . --no-banner --redact; then
        echo "❌ gitleaks: секреты найдены"; exit 1
    fi
    echo "✅ gitleaks: no leaks"
else
    echo "⚠ gitleaks не установлен — пропускаю"
fi

# ── 6. Smoke test: FORBIDDEN_ROOTS защита ──────────────────────
echo ""
echo "🔍 === Smoke: FORBIDDEN_ROOTS защита ==="
# Тестируем ИМЕННО FORBIDDEN_ROOTS: /mnt/ai-ssd/hermes (ядро)
OUTPUT="$("$PY" ./scripts/aider_runner.py /mnt/ai-ssd/hermes "test" 2>&1 || true)"
if echo "$OUTPUT" | grep -qE "FORBIDDEN|INVALID_PROJECT"; then
    echo "✅ FORBIDDEN_ROOTS защита работает"
else
    echo "❌ FORBIDDEN_ROOTS защита не сработала"
    echo "Вывод: $OUTPUT" | head -5
    exit 1
fi

# ── 7. Smoke test: NVIDIA key не в argv ────────────────────────
echo ""
echo "🔍 === Smoke: NVIDIA key не в argv ==="
if grep -q -- '--api-key.*nvidia' scripts/aider_runner.py; then
    echo "❌ NVIDIA key в argv"; exit 1
fi
if grep -q 'NVIDIA_NIM_API_KEY' scripts/aider_runner.py; then
    echo "✅ NVIDIA key через env"
else
    echo "❌ NVIDIA key не найден в env"; exit 1
fi

# ── 8. Smoke test: drop_total инициализирован ──────────────────
echo ""
echo "🔍 === Smoke: self.drop_total инициализирован ==="
if grep -q "self\.drop_total\s*=\s*0" scripts/research_runner.py; then
    echo "✅ self.drop_total инициализирован"
else
    echo "❌ self.drop_total не инициализирован"; exit 1
fi

echo ""
echo "✅ === Selfcheck пройден ==="
