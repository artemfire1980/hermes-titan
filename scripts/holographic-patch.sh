#!/bin/bash
# holographic-patch.sh — переприменяемый патч Holographic memory.
# v1: on_memory_write replace/remove (issue #55095).
# v2: retrieval_count для ВСЕХ результатов search() (issue #101521).
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

# Идемпотентность по маркеру v2 в обоих файлах
ALREADY=1
grep -q 'HOLOGRAPHIC_PATCH_v2' "$INIT" || ALREADY=0
grep -q 'HOLOGRAPHIC_PATCH_v2' "$RETR" || ALREADY=0

if [ "$ALREADY" = "1" ]; then
  echo "✓ Патч уже применён (v2)"
  touch "$MARKER"
  exit 0
fi

echo "=== Применяю патч Holographic v2 ==="

[ -f "$INIT.orig" ] || cp "$INIT" "$INIT.orig"
[ -f "$RETR.orig" ] || cp "$RETR" "$RETR.orig"

python3 - << 'PY_EOF'
import re
from pathlib import Path

INIT = Path("/mnt/ai-ssd/hermes/hermes-agent/plugins/memory/holographic/__init__.py")
RETR = Path("/mnt/ai-ssd/hermes/hermes-agent/plugins/memory/holographic/retrieval.py")

# --- Patch 1 (v1 → v2): on_memory_write replace/remove ---
init_src = INIT.read_text()
if "HOLOGRAPHIC_PATCH_v1" in init_src and "HOLOGRAPHIC_PATCH_v2" not in init_src:
    init_src = init_src.replace("HOLOGRAPHIC_PATCH_v1", "HOLOGRAPHIC_PATCH_v2", 1)
    INIT.write_text(init_src)
    print("✓ Patch 1: upgraded v1 → v2")
elif "HOLOGRAPHIC_PATCH_v2" in init_src:
    print("⚠ Patch 1: уже v2")
else:
    # v1 ещё не применён — применить с нуля
    old1 = '''    def on_memory_write(self, action: str, target: str, content: str) -> None:
        """Mirror built-in memory writes as facts."""
        if action == "add" and self._store and content:
            try:
                self._store.add_fact(content, category="user_pref" if target == "user" else "general")
            except Exception as e:
                logger.debug("Holographic memory_write mirror failed: %s", e)'''

    new1 = '''    def on_memory_write(self, action: str, target: str, content: str) -> None:
        """Mirror built-in memory writes as facts. HOLOGRAPHIC_PATCH_v2.

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

    if old1 not in init_src:
        raise SystemExit("✗ Patch 1: старый on_memory_write не найден")
    INIT.write_text(init_src.replace(old1, new1, 1))
    print("✓ Patch 1: on_memory_write (v2)")

# --- Patch 2 (v2): retrieval_count для ВСЕХ results в search() ---
retr_src = RETR.read_text()

# 2a. Убрать v1-инкремент из _fts_candidates (если есть)
v1_block = '''        # HOLOGRAPHIC_PATCH_v1: increment retrieval_count (issue #101521)
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
'''
if v1_block in retr_src:
    retr_src = retr_src.replace(v1_block, "", 1)
    print("✓ Patch 2a: убран v1-инкремент из _fts_candidates")

# 2b. Добавить инкремент в search() перед `return results`
old2 = '''        results = sorted(candidates, key=lambda x: x["score"], reverse=True)[:limit]
        for fact in results:
            fact.pop("hrr_vector", None)  # callers expect JSON-serializable dicts
        return results'''

new2 = '''        results = sorted(candidates, key=lambda x: x["score"], reverse=True)[:limit]
        for fact in results:
            fact.pop("hrr_vector", None)  # callers expect JSON-serializable dicts
        # HOLOGRAPHIC_PATCH_v2: increment retrieval_count for ALL returned facts
        # (v1 incremented only FTS5 candidates in _fts_candidates — missed
        # HRR-reranked facts). See issue #101521.
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

if "HOLOGRAPHIC_PATCH_v2" not in retr_src:
    if old2 not in retr_src:
        raise SystemExit("✗ Patch 2b: search() return-блок не найден")
    retr_src = retr_src.replace(old2, new2, 1)
    RETR.write_text(retr_src)
    print("✓ Patch 2b: retrieval_count в search()")
else:
    if "HOLOGRAPHIC_PATCH_v1" in retr_src:
        retr_src = retr_src.replace("HOLOGRAPHIC_PATCH_v1", "HOLOGRAPHIC_PATCH_v2", 1)
        RETR.write_text(retr_src)
        print("✓ Patch 2: upgraded v1 → v2")
    else:
        print("⚠ Patch 2: уже v2")
PY_EOF

python3 -m py_compile "$INIT" && echo "✓ __init__.py OK"
python3 -m py_compile "$RETR" && echo "✓ retrieval.py OK"

touch "$MARKER"
echo "✓ Патч Holographic v2 применён"
