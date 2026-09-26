#!/bin/bash
# Мониторинг peak RAM для hermes-gateway

PEAK_FILE=~/ai-system/runtime/memory_peak.txt
mkdir -p ~/ai-system/runtime

while true; do
    current=$(systemctl --user show hermes-gateway.service -p MemoryCurrent --value 2>/dev/null)
    if [ -n "$current" ] && [ "$current" != "[not set]" ]; then
        # Сохранить если это новый максимум
        old_peak=$(cat "$PEAK_FILE" 2>/dev/null || echo 0)
        if [ "$current" -gt "$old_peak" ]; then
            echo "$current" > "$PEAK_FILE"
        fi
    fi
    sleep 60  # проверять каждую минуту
done
