#!/bin/bash
# Автопуш изменений в GitHub (раз в 6 часов через cron)
# БЕЗОПАСНОСТЬ: белый список + проверка на секреты
set -euo pipefail

REPO_DIR="$HOME/ai-system"
BRANCH=main
LOG_FILE="$REPO_DIR/logs/git-auto-push.log"
LOCK_FILE="/tmp/git-auto-push.lock"

# Логирование
exec >> "$LOG_FILE" 2>&1
echo "=== $(date '+%Y-%m-%d %H:%M:%S') ==="

# Защита от параллельного запуска
if ! mkdir "$LOCK_FILE" 2>/dev/null; then
    echo "SKIP: уже запущен другой экземпляр"
    exit 0
fi
trap 'rmdir "$LOCK_FILE" 2>/dev/null' EXIT

cd "$REPO_DIR" || exit 1

# 1. Добавляем ТОЛЬКО безопасные директории (белый список)
git add scripts/ configs/ tests/ docs/ .gitignore README.md ARCHITECTURE.md DECISIONS.md CHANGELOG.md IMPLEMENTATION_NOTES.md IMPLEMENTATION_STATUS.md pytest.ini 2>/dev/null || true

# 2. Проверка: есть ли изменения?
if [ -z "$(git status --porcelain 2>/dev/null)" ]; then
    echo "INFO: изменений нет, пропуск"
    exit 0
fi

# 3. БЕЗОПАСНОСТЬ: проверка на секреты в staged файлах
SECRETS_FOUND=0
SECRETS_PATTERN='(api[_-]?key|secret|password|token|private[_-]?key)[[:space:]]*[:=][[:space:]]*['"'"'"]?[A-Za-z0-9+/=_\-]{16,}'

for file in $(git diff --cached --name-only | grep -v '\.gitignore$'); do
    if grep -Eiq "$SECRETS_PATTERN" "$file" 2>/dev/null; then
        echo "❌ BLOCKED: возможный секрет в файле: $file"
        echo "   Найденные строки:"
        grep -Ein "$SECRETS_PATTERN" "$file" 2>/dev/null | head -3
        echo "   Файл будет исключён из коммита."
        git reset HEAD "$file" 2>/dev/null || true
        SECRETS_FOUND=1

        # Отправляем уведомление в Telegram
        if [ -n "${TELEGRAM_BOT_TOKEN:-}" ] && [ -n "${TELEGRAM_CHAT_ID:-}" ]; then
            MSG="⚠️ Автопуш: возможный секрет в $file (файл исключён из коммита)"
            curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
                -d chat_id="$TELEGRAM_CHAT_ID" \
                -d text="$MSG" >/dev/null 2>&1 || true
        fi
    fi
done

if [ "$SECRETS_FOUND" -eq 1 ]; then
    echo "⚠️ Некоторые файлы исключены из-за возможных секретов"
fi

# 4. Проверка: есть ли что коммитить после фильтрации?
if [ -z "$(git diff --cached --name-only)" ]; then
    echo "INFO: после проверки безопасности коммитить нечего"
    exit 0
fi

# 5. Показать что будет закоммичено
echo "Staged файлы:"
git diff --cached --name-only


# 6.5. Selfcheck: не даём сломанному коду попасть в main
echo "🔍 Selfcheck..."
if [ -x "$REPO_DIR/scripts/selfcheck.sh" ]; then
    if ! "$REPO_DIR/scripts/selfcheck.sh"; then
        echo "❌ Selfcheck не пройден — коммит отменён"
        # Сбрасываем staging чтобы не было "висящих" изменений
        git reset HEAD >/dev/null 2>&1 || true
        exit 1
    fi
else
    echo "⚠️ selfcheck.sh не найден или не исполняемый"
fi
# 6. Коммит
git commit -m "auto: $(date '+%Y-%m-%d %H:%M:%S') [$(git diff --cached --name-only | wc -l) files]"

# 7. Пуш
if git push origin "$BRANCH"; then
    echo "✅ Успешно запушено в origin/$BRANCH"
else
    echo "❌ Ошибка пуша — расхождение с origin. Останавливаюсь без rebase."
    if [ -n "${TELEGRAM_BOT_TOKEN:-}" ] && [ -n "${TELEGRAM_CHAT_ID:-}" ]; then
        curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
            -d chat_id="$TELEGRAM_CHAT_ID" -d text="⚠️ git-auto-push: конфликт с origin, нужен ручной разбор" >/dev/null 2>&1 || true
    fi
    exit 1
fi
