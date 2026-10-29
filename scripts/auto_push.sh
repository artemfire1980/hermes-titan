#!/bin/bash
set -euo pipefail
cd ~/ai-system

# Переключаемся на main, чтобы случайно не запушить в другую ветку
git checkout main || { echo "Ошибка переключения на main"; exit 1; }

if [[ -z $(git status --porcelain) ]]; then
    echo "Нет изменений для пуша."
    exit 0
fi

git add -A
git commit -m "auto: обновление от Hermes ($(date '+%Y-%m-%d %H:%M'))" || true
git push origin main
echo "✅ Изменения запушены в main."
