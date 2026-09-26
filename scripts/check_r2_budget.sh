#!/bin/bash
set -euo pipefail

# Загрузка .env
[ -f "$HOME/ai-system/.env" ] && set -a && . "$HOME/ai-system/.env" && set +a

: "${R2_ENDPOINT:?R2_ENDPOINT required (put it in ~/ai-system/.env)}"
R2_BUCKET="${R2_BUCKET:-hermes-helper}"
LOG_FILE="$HOME/ai-system/logs/r2_budget.log"
ALERT_THRESHOLD_GB=8

# Подсчет размера bucket
SIZE_BYTES=$(aws s3 ls "s3://$R2_BUCKET" --recursive --endpoint-url "$R2_ENDPOINT" 2>/dev/null \
  | awk '{total += $3} END {print total+0}')

# Дробные GB (чтобы алерт срабатывал именно с 8.0, а не с 9)
SIZE_GB=$(awk -v b="$SIZE_BYTES" 'BEGIN{printf "%.2f", b/1024/1024/1024}')

echo "$(date): R2 Usage: ${SIZE_GB} GB / 10 GB" | tee -a "$LOG_FILE"

if awk -v s="$SIZE_GB" -v t="$ALERT_THRESHOLD_GB" 'BEGIN{exit !(s>t)}'; then
    echo "$(date): ⚠️ WARNING: R2 usage above ${ALERT_THRESHOLD_GB} GB!" | tee -a "$LOG_FILE"
fi
