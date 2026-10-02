#!/bin/bash
# resource-governor.sh — блокировка тяжёлых задач (MAX_HEAVY=1)
set -euo pipefail

LOCK_DIR="$HOME/ai-system/runtime/locks"
LOCK_FILE="$LOCK_DIR/heavy.lock"
FLOCK_FILE="$LOCK_DIR/heavy.flock"
MAX_HEAVY="${MAX_HEAVY:-1}"

mkdir -p "$LOCK_DIR"

usage() {
  cat <<EOF
Использование: $0 {acquire|release|status} [task_name]

  acquire <task>  — захватить слот (если свободен)
  release <task>  — освободить слот
  status          — показать память + занятые слоты

MAX_HEAVY=$MAX_HEAVY (переопределяется env)
EOF
  exit 1
}

case "${1:-}" in
  acquire)
    TASK="${2:?Укажите имя задачи}"
    [[ "$TASK" != *:* ]] || { echo "✗ Имя задачи не должно содержать ':'" >&2; exit 1; }
    exec 9>"$FLOCK_FILE"
    flock -w 30 9 || { echo "✗ Таймаут ожидания lock (30s)" >&2; exit 1; }

    if [ -f "$LOCK_FILE" ]; then
      COUNT=$(wc -l < "$LOCK_FILE")
    else
      COUNT=0
    fi
    if [ "$COUNT" -ge "$MAX_HEAVY" ]; then
      echo "✗ Занято ($COUNT/$MAX_HEAVY):"
      cat "$LOCK_FILE"
      exec 9>&-
      exit 1
    fi

    echo "$TASK:$$:$(date -Iseconds)" >> "$LOCK_FILE"
    echo "✓ Выделено для '$TASK' (PID $$)"
    exec 9>&-
    ;;

  release)
    TASK="${2:?Укажите имя задачи}"
    [[ "$TASK" != *:* ]] || { echo "✗ Имя задачи не должно содержать ':'" >&2; exit 1; }
    exec 9>"$FLOCK_FILE"
    flock -w 30 9 || { echo "✗ Таймаут ожидания lock (30s)" >&2; exit 1; }

    if [ -f "$LOCK_FILE" ]; then
      awk -F: -v t="$TASK" '$1 != t' "$LOCK_FILE" > "$LOCK_FILE.tmp" && mv "$LOCK_FILE.tmp" "$LOCK_FILE"
      echo "✓ Освобождено '$TASK'"
    fi
    exec 9>&-
    ;;

  status)
    echo "=== Память ==="
    free -h | head -2
    echo
    echo "=== Занятые слоты (MAX_HEAVY=$MAX_HEAVY) ==="
    if [ -f "$LOCK_FILE" ] && [ -s "$LOCK_FILE" ]; then
      cat "$LOCK_FILE"
    else
      echo "(нет)"
    fi
    ;;

  *)
    usage
    ;;
esac
