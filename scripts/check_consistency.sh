#!/bin/bash
# check_consistency.sh — проверка drift в документации HERMES-TITAN.
# Запускает 4 check-скрипта. Exit 0 — всё ок, 1 — есть drift.
set -uo pipefail

REPO="$(git rev-parse --show-toplevel 2>/dev/null || echo "$(dirname "$0")/..")"
cd "$REPO" || exit 1

CHECKS_DIR="$REPO/scripts/checks"
ERRORS=0

echo "🔍 === Consistency check ==="
echo

# 1. DEC уникальность/непрерывность
echo "── 1/4 DEC order ──"
if python3 "$CHECKS_DIR/check_dec_order.py"; then
    :
else
    ERRORS=$((ERRORS + 1))
fi
echo

# 2. README DEC count
echo "── 2/4 README DEC count ──"
if python3 "$CHECKS_DIR/check_doc_counts.py"; then
    :
else
    ERRORS=$((ERRORS + 1))
fi
echo

# 3. CP sync
echo "── 3/4 CP sync ──"
if python3 "$CHECKS_DIR/check_cp_sync.py"; then
    :
else
    ERRORS=$((ERRORS + 1))
fi
echo

# 4. INDEX.md актуальность
echo "── 4/4 DEC index ──"
if python3 "$CHECKS_DIR/check_dec_index.py" --check; then
    :
else
    ERRORS=$((ERRORS + 1))
fi
echo

if [ "$ERRORS" -eq 0 ]; then
    echo "✅ Consistency OK"
    exit 0
fi

echo "❌ Найдено проблем: $ERRORS"
exit 1
