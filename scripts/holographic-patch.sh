#!/bin/bash
# holographic-patch.sh — переприменяемый патч Holographic memory.
# v1: on_memory_write replace/remove (issue #55095).
# v2: retrieval_count для ВСЕХ результатов search() (issue #101521).
# v3: расширенный _extract_entities в store.py (Cyrillic, ALL CAPS, CamelCase, стоп-слова).
# Идемпотентен: повторный запуск — no-op.
set -euo pipefail

HOLO_DIR="/mnt/ai-ssd/hermes/hermes-agent/plugins/memory/holographic"
INIT="$HOLO_DIR/__init__.py"
RETR="$HOLO_DIR/retrieval.py"
STORE="$HOLO_DIR/store.py"
MARKER="$HOLO_DIR/.holographic-patch-applied"

if [ ! -d "$HOLO_DIR" ]; then
  echo "✗ Holographic не найден: $HOLO_DIR" >&2
  exit 1
fi

# Идемпотентность: маркер v3 в каждом из трёх файлов
ALREADY=1
grep -q 'HOLOGRAPHIC_PATCH_v2' "$INIT"  || ALREADY=0
grep -q 'HOLOGRAPHIC_PATCH_v2' "$RETR"  || ALREADY=0
grep -q 'HOLOGRAPHIC_PATCH_v3' "$STORE" || ALREADY=0

if [ "$ALREADY" = "1" ]; then
  echo "✓ Патч уже применён (v3)"
  touch "$MARKER"
  exit 0
fi

echo "=== Применяю патч Holographic v3 ==="

[ -f "$INIT.orig" ]  || cp "$INIT"  "$INIT.orig"
[ -f "$RETR.orig" ]  || cp "$RETR"  "$RETR.orig"
[ -f "$STORE.orig" ] || cp "$STORE" "$STORE.orig"

python3 - << 'PY_EOF'
from pathlib import Path

INIT  = Path("/mnt/ai-ssd/hermes/hermes-agent/plugins/memory/holographic/__init__.py")
RETR  = Path("/mnt/ai-ssd/hermes/hermes-agent/plugins/memory/holographic/retrieval.py")
STORE = Path("/mnt/ai-ssd/hermes/hermes-agent/plugins/memory/holographic/store.py")

# --- Patch 1 (v1 → v2): on_memory_write replace/remove ---
init_src = INIT.read_text()
if "HOLOGRAPHIC_PATCH_v1" in init_src and "HOLOGRAPHIC_PATCH_v2" not in init_src:
    init_src = init_src.replace("HOLOGRAPHIC_PATCH_v1", "HOLOGRAPHIC_PATCH_v2", 1)
    INIT.write_text(init_src)
    print("✓ Patch 1: upgraded v1 → v2")
elif "HOLOGRAPHIC_PATCH_v2" in init_src:
    print("⚠ Patch 1: уже v2")
else:
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

old2 = '''        results = sorted(candidates, key=lambda x: x["score"], reverse=True)[:limit]
        for fact in results:
            fact.pop("hrr_vector", None)  # callers expect JSON-serializable dicts
        return results'''
new2 = '''        results = sorted(candidates, key=lambda x: x["score"], reverse=True)[:limit]
        for fact in results:
            fact.pop("hrr_vector", None)  # callers expect JSON-serializable dicts
        # HOLOGRAPHIC_PATCH_v2: increment retrieval_count for ALL returned facts
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
    RETR.write_text(retr_src.replace(old2, new2, 1))
    print("✓ Patch 2b: retrieval_count в search()")
else:
    if "HOLOGRAPHIC_PATCH_v1" in retr_src:
        retr_src = retr_src.replace("HOLOGRAPHIC_PATCH_v1", "HOLOGRAPHIC_PATCH_v2", 1)
        RETR.write_text(retr_src)
        print("✓ Patch 2: upgraded v1 → v2")
    else:
        print("⚠ Patch 2: уже v2")

# --- Patch 3 (v3): _extract_entities в store.py ---
# Логика: если расширенные паттерны УЖЕ есть — только добавить маркер.
# Если upstream-версия — заменить блок целиком.
store_src = STORE.read_text()

if "HOLOGRAPHIC_PATCH_v3" in store_src:
    print("⚠ Patch 3: уже v3")
else:
    # Проверка: расширенные паттерны уже на месте? (есть Cyrillic класс [А-ЯЁ] в _RE_SINGLE_ENTITY)
    has_extended_re = "А-ЯЁ" in store_src and "_RE_SINGLE_ENTITY = (" in store_src
    has_stop_words = "_STOP_WORDS" in store_src

    if has_extended_re and has_stop_words:
        # Оба изменения уже на месте — добавляем только маркер
        print("✓ Patch 3a: _RE_SINGLE_ENTITY уже расширен (маркер добавлен)")
        print("✓ Patch 3b: _STOP_WORDS уже на месте (маркер добавлен)")
        # Вставить маркер в комментарий перед _RE_SINGLE_ENTITY
        marker_line = "# HOLOGRAPHIC_PATCH_v3: расширенные паттерны (Cyrillic, ALL CAPS, CamelCase, single word)"
        if marker_line not in store_src:
            store_src = store_src.replace(
                "_RE_SINGLE_ENTITY = (",
                marker_line + "\n_RE_SINGLE_ENTITY = (",
                1,
            )
        # Вставить маркер в _STOP_WORDS
        marker_stop = "        # HOLOGRAPHIC_PATCH_v3: стоп-слова + дедуп подстрок"
        if marker_stop not in store_src:
            store_src = store_src.replace(
                "        _STOP_WORDS = {",
                marker_stop + "\n        _STOP_WORDS = {",
                1,
            )
        STORE.write_text(store_src)
    else:
        # upstream-версия — полная замена
        old_re = '''_RE_SINGLE_ENTITY = (re.compile(r'\\b([A-Z][a-z]+(?:\\s+[A-Z][a-z]+)+)\\b'), re.compile(r'"([^"]+)"'), re.compile(r"'([^']+)'"))'''
        new_re = '''# HOLOGRAPHIC_PATCH_v3: расширенные паттерны (Cyrillic, ALL CAPS, CamelCase, single word)
_RE_SINGLE_ENTITY = (
    re.compile(r'\\b([A-ZА-ЯЁ][a-zа-яё]+(?:\\s+[A-ZА-ЯЁ][a-zа-яё]+)+)\\b'),
    re.compile(r'\\b([A-Z]{2,}\\d*)\\b'),
    re.compile(r'\\b([A-Z][a-z]+[A-Z][a-zA-Z0-9]*)\\b'),
    re.compile(r'\\b([A-ZА-ЯЁ][a-zа-яё]{2,})\\b'),
    re.compile(r'"([^"]+)"'),
    re.compile(r"'([^']+)'"),
)'''
        if old_re not in store_src:
            raise SystemExit("✗ Patch 3a: ни расширенный, ни upstream _RE_SINGLE_ENTITY не найдены")
        store_src = store_src.replace(old_re, new_re, 1)
        print("✓ Patch 3a: _RE_SINGLE_ENTITY заменён на расширенный")

        old_loop = '''        uniq: dict[str, str] = {}  # lower-cased key -> first-seen spelling, insertion-ordered
        for name in filter(None, (n.strip() for n in raw)):
            uniq.setdefault(name.lower(), name)
        return list(uniq.values())'''
        new_loop = '''        # HOLOGRAPHIC_PATCH_v3: стоп-слова + дедуп подстрок
        _STOP_WORDS = {
            "имя", "язык", "автомобиль", "цель", "поиск", "материал", "хост",
            "проект", "инструмент", "the", "a", "an", "this", "that",
            "google", "search", "and", "or", "is", "are", "was", "were",
        }
        uniq: dict[str, str] = {}
        for name in filter(None, (n.strip() for n in raw)):
            key = name.lower()
            if key in _STOP_WORDS or len(name) < 3:
                continue
            if any(key in existing_key for existing_key in uniq.keys()):
                continue
            uniq = {k: v for k, v in uniq.items() if k not in key}
            uniq[key] = name
        return list(uniq.values())'''
        if old_loop not in store_src:
            raise SystemExit("✗ Patch 3b: старый uniq-loop не найден")
        store_src = store_src.replace(old_loop, new_loop, 1)
        print("✓ Patch 3b: _STOP_WORDS + дедуп")
        STORE.write_text(store_src)

PY_EOF

# Синтаксическая проверка
python3 -m py_compile "$INIT"  && echo "✓ __init__.py OK"
python3 -m py_compile "$RETR"  && echo "✓ retrieval.py OK"
python3 -m py_compile "$STORE" && echo "✓ store.py OK"

touch "$MARKER"
echo "✓ Патч Holographic v3 применён"
