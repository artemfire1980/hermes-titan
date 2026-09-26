#!/bin/bash
# Telegram wrapper для Deep Research Agent v3 (60min timeout)
# + отправка готового отчёта в Telegram в формате DOCX
set -uo pipefail

TOPIC="${1:?Usage: research-telegram.sh \"topic\" [depth]}"
DEPTH="${2:-3}"


# Проверка безопасности: тема не должна содержать shell injection символы
if echo "$TOPIC" | grep -qE '[`$;|&]'; then
    echo "❌ Ошибка безопасности: тема содержит недопустимые символы"
    echo "Запрещены: \` \$ ; | & (shell injection)"
    echo "Скобки (), цифры, буквы, пунктуация — разрешены"
    exit 1
fi

VENV_PYTHON=~/.hermes/hermes-agent/venv/bin/python
SCRIPTS_DIR=~/ai-system/scripts
REPORTS_DIR=~/research/reports
TIMEOUT_MIN=60

echo "🔬 Запуск исследования: $TOPIC"
echo "📊 Глубина: $DEPTH"
echo "⏱️  Таймаут: ${TIMEOUT_MIN} мин"
echo ""

# Запомнить какие отчёты уже есть (чтобы найти новый)
BEFORE_FILES=$(ls -1 "$REPORTS_DIR"/*.md 2>/dev/null | sort)

# Запустить runner с таймаутом
timeout $((TIMEOUT_MIN * 60)) $VENV_PYTHON ~/bin/research-runner.py \
    --topic "$TOPIC" --depth "$DEPTH" > /tmp/research.log 2>&1
RC=$?

if [ $RC -eq 124 ]; then
    echo "❌ Таймаут: исследование не завершилось за ${TIMEOUT_MIN} минут"
    tail -20 /tmp/research.log
    exit 1
elif [ $RC -ne 0 ]; then
    echo "❌ Ошибка research-runner (exit code: $RC)"
    tail -30 /tmp/research.log
    exit $RC
fi

# Найти новый отчёт
AFTER_FILES=$(ls -1 "$REPORTS_DIR"/*.md 2>/dev/null | sort)
NEW_MD=$(comm -13 <(echo "$BEFORE_FILES") <(echo "$AFTER_FILES") | tail -1)

if [ -z "$NEW_MD" ]; then
    echo "⚠️ Новый отчёт не найден в $REPORTS_DIR"
    echo "Последний отчёт:"
    ls -lt "$REPORTS_DIR"/*.md 2>/dev/null | head -1
    NEW_MD=$(ls -t "$REPORTS_DIR"/*.md 2>/dev/null | head -1)
fi

if [ -z "$NEW_MD" ]; then
    echo "❌ Нет отчётов в $REPORTS_DIR"
    exit 1
fi

echo ""
echo "✅ Отчёт создан: $NEW_MD"

# Конвертировать MD → DOCX
NEW_DOCX="${NEW_MD%.md}.docx"
echo "📄 Конвертация в DOCX..."
if $VENV_PYTHON "$SCRIPTS_DIR/md2docx.py" "$NEW_MD" "$NEW_DOCX" 2>&1; then
    echo "✅ DOCX создан: $NEW_DOCX"

    # Извлечь статистику из frontmatter
    STATS=$(awk '/^---$/{n++; if(n==2) exit} n>=1{print}' "$NEW_MD" | head -20)
    EVIDENCES=$(echo "$STATS" | grep -E "^evidences_extracted:" | awk '{print $2}')
    SOURCES=$(echo "$STATS" | grep -E "^unique_sources:" | awk '{print $2}')
    CONFLICTS=$(echo "$STATS" | grep -E "^conflicts_detected:" | awk '{print $2}')

    CAPTION="📊 Исследование завершено
Тема: $TOPIC
Глубина: $DEPTH
Источников: ${SOURCES:-?}
Фактов: ${EVIDENCES:-?}
Конфликтов: ${CONFLICTS:-0}"

    # Отправить DOCX в Telegram
    echo ""
    echo "📤 Отправка в Telegram..."
    if $VENV_PYTHON "$SCRIPTS_DIR/send-to-telegram.py" "$NEW_DOCX" --caption "$CAPTION"; then
        echo "✅ Отчёт отправлен в Telegram"
    else
        echo "⚠️ Не удалось отправить DOCX в Telegram"
    fi

    # Дополнительно отправить Executive Summary как текст
    echo ""
    echo "📝 Отправка Executive Summary как текста..."
    SUMMARY=$(sed -n '/^## Executive Summary/,/^## /{/^## Executive Summary/d;/^## /d;p}' "$NEW_MD" | head -30)
    if [ -n "$SUMMARY" ]; then
        MSG="🔬 *Исследование: $TOPIC*

$SUMMARY

📎 Полный отчёт в прикреплённом DOCX"
        $VENV_PYTHON "$SCRIPTS_DIR/send-to-telegram.py" "$NEW_DOCX" \
            --caption "$CAPTION" --message "$MSG" 2>/dev/null || true
    fi
else
    echo "⚠️ Не удалось сконвертировать в DOCX"
    echo "MD отчёт доступен: $NEW_MD"
fi

echo ""
echo "===== РЕЗУЛЬТАТ ====="
tail -10 /tmp/research.log
