#!/bin/bash
# Синхронизация скриптов из git в HERMES_HOME/scripts/
set -euo pipefail
SRC=~/ai-system/scripts
DST=/mnt/ai-ssd/hermes/scripts
for f in moysklad_refresh.py mail_check.py; do
    cp "$SRC/$f" "$DST/$f"
    echo "✓ $f"
done
echo "Done."
