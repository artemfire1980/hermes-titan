#!/bin/bash
# holographic-patch.sh — переприменяемый патч Holographic memory.
# Закрывает баги:
#   1. on_memory_write игнорирует replace/remove (issue #55095)
#   2. retrieval_count никогда не инкрементируется (issue #101521)
# Идемпотентен: повторный запуск — no-op.
set -euo pipefail

HOLO_DIR="/mnt/ai-ssd/hermes/hermes-agent/plugins/memory/holographic"
INIT="$HOLO_DIR/__init__.py"
RETR="$HOLO_DIR/retrieval.py"
MARKER="$HOLO_DIR/.holographic-patch-applied"

if [ ! -d "$HOLO_DIR" ]; then
  echo "✗ Holographic не найден: $HOLO_DIR" >&2
  exit 1
fi

# Проверка идемпотентности: marker + реальная проверка патчей в коде
ALREADY=1
grep -q 'HOLOGRAPHIC_PATCH_v1' "$INIT" || ALREADY=0
grep -q 'HOLOGRAPHIC_PATCH_v1' "$RETR" || ALREADY=0

if [ "$ALREADY" = "1" ]; then
  echo "✓ Патч уже применён (v1)"
  touch "$MARKER"
  exit 0
fi

echo "=== Применяю патч Holographic v1 ==="

# Бэкап (один раз — оригиналы до патча)
[ -f "$INIT.orig" ] || cp "$INIT" "$INIT.orig"
[ -f "$RETR.orig" ] || cp "$RETR" "$RETR.orig"

python3 - << 'PY_EOF'
from pathlib import Path

INIT = Path("/mnt/ai-ssd/hermes/hermes-agent/plugins/memory/holographic/__init__.py")
RETR = Path("/mnt/ai-ssd/hermes/hermes-agent/plugins/memory/holographic/retrieval.py")

# --- Patch 1: on_memory_write replace/remove ---
init_src = INIT.read_text()
old1 = '''    def on_memory_write(self, action: str, target: str, content: str) -> None:
        """Mirror built-in memory writes as facts."""
        if action == "add" and self._store and content:
            try:
                self._store.add_fact(content, category="user_pref" if target == "user" else "general")
            except Exception as e:
                logger.debug("Holographic memory_write mirror failed: %s", e)'''

new1 = '''    def on_memory_write(self, action: str, target: str, content: str) -> None:
        """Mirror built-in memory writes as facts. HOLOGRAPHIC_PATCH_v1.

        Handles add/replace/remove: replace = remove old + add new;
        remove = delete matching fact. Best-effort, never raises.
        """
        if not self._store or not content:
            return
        try:
            cat = "user_pref" if target == "user" else "general"
            if action == "add":
                self._store.add_fact(content, category=cat)
            elif action in ("replace", "remove"):
                # remove any existing fact with the same content (best-effort)
                try:
                    existing = self._store.list_facts(limit=1000)
                except Exception:
                    existing = []
                for f in existing:
                    if f.get("content") == content:
                        try:
                            self._store.remove_fact(int(f["fact_id"]))
                        except Exception:
                            pass
                if action == "replace":
                    self._store.add_fact(content, category=cat)
        except Exception as e:
            logger.debug("Holographic memory_write mirror failed: %s", e)'''

if "HOLOGRAPHIC_PATCH_v1" not in init_src:
    if old1 not in init_src:
        raise SystemExit("✗ Patch 1: старый on_memory_write не найден")
    INIT.write_text(init_src.replace(old1, new1, 1))
    print("✓ Patch 1: on_memory_write (add/replace/remove)")
else:
    print("⚠ Patch 1: уже применён")

# --- Patch 2: retrieval_count increment ---
retr_src = RETR.read_text()
old2 = '''        max_rank = max([abs(f["fts_rank_raw"]) for f in results] + [1e-6])
        for fact in results:
            fact["fts_rank"] = abs(fact.pop("fts_rank_raw")) / max_rank
        return results'''

new2 = '''        max_rank = max([abs(f["fts_rank_raw"]) for f in results] + [1e-6])
        for fact in results:
            fact["fts_rank"] = abs(fact.pop("fts_rank_raw")) / max_rank
        # HOLOGRAPHIC_PATCH_v1: increment retrieval_count (issue #101521)
        try:
            ids = [f["fact_id"] for f in results if "fact_id" in f]
            if ids:
                ph = ",".join("?" * len(ids))
                self.store._write(
                    f"UPDATE facts SET retrieval_count = retrieval_count + 1 "
                    f"WHERE fact_id IN ({ph})",
                    ids,
                )
        except Exception:
            pass  # best-effort, never break search
        return results'''

if "HOLOGRAPHIC_PATCH_v1" not in retr_src:
    if old2 not in retr_src:
        raise SystemExit("✗ Patch 2: старый _fts_candidates return не найден")
    RETR.write_text(retr_src.replace(old2, new2, 1))
    print("✓ Patch 2: retrieval_count increment")
else:
    print("⚠ Patch 2: уже применён")
PY_EOF

# Синтаксическая проверка
python3 -m py_compile "$INIT" && echo "✓ __init__.py синтаксис OK"
python3 -m py_compile "$RETR" && echo "✓ retrieval.py синтаксис OK"

touch "$MARKER"
echo "✓ Патч Holographic v1 применён"
