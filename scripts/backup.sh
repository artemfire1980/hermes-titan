#!/bin/bash
# backup.sh — бэкап наших данных (вне HERMES_HOME)
set -euo pipefail

ROOT="$HOME/ai-system"
STAMP=$(date +%Y%m%d-%H%M%S)
DIR="$ROOT/backups/$STAMP"

mkdir -p "$DIR"

echo "=== Бэкап наших данных в $DIR ==="

# 1. Дамп tasks.db (если есть)
if [ -f "$ROOT/data/tasks.db" ]; then
  sqlite3 "$ROOT/data/tasks.db" ".dump" > "$DIR/tasks_dump.sql"
  echo "✓ tasks.db дамп"
fi

# 2. legacy база (архив, копируем целиком)
if [ -f "$ROOT/data/tasks.legacy.db" ]; then
  cp "$ROOT/data/tasks.legacy.db" "$DIR/"
  echo "✓ tasks.legacy.db"
fi

# 3. Configs
if [ -d "$ROOT/configs" ] && [ -n "$(ls -A "$ROOT/configs" 2>/dev/null)" ]; then
  cp -r "$ROOT/configs" "$DIR/configs"
  echo "✓ configs"
fi

# 4. Documentation (markdown в корне)
for f in README.md ARCHITECTURE.md DECISIONS.md CHANGELOG.md \
         IMPLEMENTATION_NOTES.md IMPLEMENTATION_STATUS.md; do
  [ -f "$ROOT/$f" ] && cp "$ROOT/$f" "$DIR/" && echo "✓ $f"
done

# 5. Docs directory
if [ -d "$ROOT/docs" ]; then
  mkdir -p "$DIR/docs"
  find "$ROOT/docs" -maxdepth 1 -type f -name "*.md" -exec cp {} "$DIR/docs/" \;
  echo "✓ docs/ (top-level .md)"
fi

# 6. Manifest
cat > "$DIR/manifest.json" << MANIFEST
{
  "timestamp": "$STAMP",
  "commit": "$(cd "$ROOT" && git rev-parse HEAD 2>/dev/null || echo unknown)",
  "tag": "$(cd "$ROOT" && git describe --tags --always 2>/dev/null || echo unknown)",
  "note": "Наши данные. HERMES_HOME покрыт hermes backup."
}
MANIFEST

echo "✓ manifest.json"
echo
echo "=== Содержимое бэкапа ==="
find "$DIR" -type f | sort
echo
echo "=== Размер ==="
du -sh "$DIR"
echo "✓ Бэкап завершён: $DIR"
