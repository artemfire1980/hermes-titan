#!/bin/bash
set -euo pipefail
cd ~/ai-system

if [[ -z $(git status --porcelain) ]]; then
    echo "Нет изменений для пуша."
    exit 0
fi

git add -A
git commit -m "auto: обновление от Hermes ($(date '+%Y-%m-%d %H:%M'))" || true
git push origin main
echo "✅ Изменения запушены в main."
