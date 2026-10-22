#!/bin/bash
set -euo pipefail

LOG="/tmp/update-plugins-$(date +%Y%m%d_%H%M%S).log"
log() { echo "$@" | tee -a "$LOG"; }

log "=== update-plugins $(date '+%Y-%m-%d %H:%M:%S') ==="

# Токен и chat_id — из .env (не палим)
set -a
source /mnt/ai-ssd/hermes/.env 2>/dev/null || true
set +a
CHAT_ID="${TELEGRAM_HOME_CHANNEL:-${TELEGRAM_CHAT_ID:-170690883}}"

# Версии — хардкод (hermes plugins list триггерит uv sync → баг uv 0.12.x)
PLUGIN_INFO="  holographic 0.17.4 (catalog)
  progressive-skill 3.2.1 (git)"
log "Плагины (хардкод, проверять вручную):"
log "$PLUGIN_INFO"

# Docs
log "--- update_docs.py ---"
cd ~/ai-system
DOCS_OUT=$(python3 scripts/update_docs.py 2>&1 | tail -5 || true)
log "$DOCS_OUT"

# Telegram — напрямую через curl (без Hermes → без uv sync)
SUMMARY=$(echo "$DOCS_OUT" | grep -E "Changed:|Нечего" || echo "docs: без изменений")
MSG="🔄 Проверка плагинов + docs ($(date '+%Y-%m-%d %H:%M'))
📦 Плагины (хардкод, проверять вручную):
$PLUGIN_INFO

⚠️ Автообновление заблокировано багом uv 0.12.x. Вручную: hermes plugins update <name>
⚠️ Версии — хардкод, проверять: hermes plugins list

📚 Docs:
$SUMMARY
Лог: $LOG"

if [ -n "${TELEGRAM_BOT_TOKEN:-}" ]; then
  if curl -sS -m 15 -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
       -d "chat_id=${CHAT_ID}" --data-urlencode "text=${MSG}" >/dev/null 2>&1; then
    log "✅ Telegram отправлен (chat ${CHAT_ID})"
  else
    log "⚠️ Telegram не отправлен (сеть)"
  fi
else
  log "⚠️ TELEGRAM_BOT_TOKEN не задан — Telegram пропущен"
fi

log "Готово. Лог: $LOG"
exit 0
