#!/bin/bash
# Проверка перед коммитом: синтаксис Python/Bash + smoke-тесты безопасности
set -u

REPO_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/.." && pwd)"
cd "$REPO_DIR" || { echo "❌ не могу перейти в $REPO_DIR"; exit 1; }
export PYTHONDONTWRITEBYTECODE=1

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

echo ""
echo "🔍 === Bash синтаксис ==="
sh_count=0
for f in scripts/*.sh scripts/aws-r2; do
    [ -f "$f" ] || continue
    bash -n "$f" || { echo "❌ синтаксическая ошибка: $f"; exit 1; }
    sh_count=$((sh_count + 1))
done
[ "$sh_count" -gt 0 ] || { echo "❌ не найдено ни одного .sh"; exit 1; }
echo "✅ Bash: $sh_count файлов"

echo ""
echo "🔍 === Smoke test: FORBIDDEN_ROOTS защита ==="
# FORBIDDEN_ROOTS теперь проверяется ДО AIDER_BIN, поэтому бинарник не нужен
OUTPUT="$(./scripts/aider-runner.py /etc "test" 2>&1 || true)"
if echo "$OUTPUT" | grep -q "FORBIDDEN\|INVALID_PROJECT\|Outside allowed"; then
    echo "✅ FORBIDDEN_ROOTS защита работает"
else
    echo "❌ FORBIDDEN_ROOTS защита не сработала"
    echo "Вывод скрипта:"
    echo "$OUTPUT" | head -10
    exit 1
fi

echo ""
echo "🔍 === Smoke test: NVIDIA key не в argv ==="
if grep -q -- '--api-key.*nvidia' scripts/aider-runner.py; then
    echo "❌ NVIDIA key всё ещё в argv (должен быть в env)"
    exit 1
fi
if grep -q 'NVIDIA_NIM_API_KEY.*api_key' scripts/aider-runner.py; then
    echo "✅ NVIDIA key передаётся через env"
else
    echo "❌ NVIDIA key не найден в env"
    exit 1
fi

echo ""
echo "🔍 === Smoke test: save_ckpt без двойного load ==="
# Извлекаем ТОЛЬКО тело save_ckpt (до следующего def)
SAVE_CKPT_BODY="$(awk '/def save_ckpt/{flag=1; next} /^[[:space:]]*def /{flag=0} flag' scripts/research-runner.py)"
if echo "$SAVE_CKPT_BODY" | grep -q "ckpt\.load"; then
    echo "❌ save_ckpt содержит лишний ckpt.load (двойной I/O)"
    echo "Тело save_ckpt:"
    echo "$SAVE_CKPT_BODY"
    exit 1
fi
echo "✅ save_ckpt без двойного I/O"

echo ""
echo "🔍 === Smoke test: self.drop_total инициализирован ==="
if grep -q "self\.drop_total\s*=\s*0" scripts/research-runner.py; then
    echo "✅ self.drop_total инициализирован"
else
    echo "❌ self.drop_total не инициализирован"
    exit 1
fi

echo ""
echo "✅ === Selfcheck пройден (5 smoke-тестов) ==="
