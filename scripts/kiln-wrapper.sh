# NOTE: не используется Hermes (Hermes -> прямой путь к kiln3d).
# Оставлен как пример wrapper-подхода.
#!/bin/bash
# Kiln MCP wrapper — прогревает Kiln перед подачей на stdin.
set -euo pipefail
KILN_BIN="/home/khadas/.cache/uv/archive-v0/vZuWT9b7EakyQtIV/bin/kiln3d"
exec "$KILN_BIN" serve
