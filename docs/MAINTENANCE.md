# HERMES-TITAN — Maintenance Guide

> Как поддерживать документацию, память и CI в консистентном состоянии.
> Обновлено: 2026-10-03.

## 1. Consistency check

**Что это:** автоматическая проверка drift в документации. Ловит:
- Дубли/пропуски DEC.
- README `<N> решений` ≠ реальному числу DEC.
- CP в README / IMPLEMENTATION_STATUS / PROJECT-STATE расходятся.
- `docs/INDEX.md` устарел.

**Где:** `scripts/check_consistency.sh` (wrapper над 4 check-скриптами в `scripts/checks/`).

**Как запускать:**

    bash scripts/check_consistency.sh

Exit 0 — OK, exit 1 — drift.

**Где вызывается автоматически:**
- В `scripts/selfcheck.sh` (секция 9) — перед коммитом.
- В CI (`.github/workflows/ci.yml`, job `consistency`) — при push/PR в `main`.

## 2. Чек-лист: добавление нового DEC

1. Добавить `## DEC-NNN: Заголовок` в `DECISIONS.md`.
2. Обновить `README.md`: `<N> архитектурных решений (DEC-001…DEC-NNN)`.
3. Регенерировать `docs/INDEX.md`:

       python3 scripts/checks/check_dec_index.py

4. Запустить проверку:

       bash scripts/check_consistency.sh

5. Коммит: `feat(dec): DEC-NNN — <краткое описание>`.

## 3. Чек-лист: изменение контрольной точки (CP)

1. Обновить `IMPLEMENTATION_STATUS.md`:
   - `Версия: X.Y.Z · Контрольная точка: CP-NNN`.
   - Таблица компонентов.
2. Обновить `docs/PROJECT-STATE.md`:
   - Раздел `Current` → `Контрольная точка: CP-NNN`.
   - Раздел `Last completed`.
3. Запустить проверку:

       bash scripts/check_consistency.sh


## 4. Память (Hermes)

| Слой | Где | Что | Когда обновлять |
|------|-----|-----|-----------------|
| **SOUL.md** | `/mnt/ai-ssd/hermes/SOUL.md` | Личность, тон | Редко |
| **USER.md** | `/mnt/ai-ssd/hermes/memories/USER.md` | Профиль | При изменении |
| **MEMORY.md** | `/mnt/ai-ssd/hermes/memories/MEMORY.md` | Hot facts, gotchas | При новых DEC |
| **Holographic** | `memory_store.db` | Semantic facts | **Сам наполняется** |
| **Episodic** | `state.db` | Сессии, FTS5 | **Сам наполняется** |

**Правила:**
- `MEMORY.md` ≤ 2200 символов. **Не дублировать DECISIONS.md.**
- Holographic **сам наполняется** — не писать вручную.
- Episodic — через `state.db` FTS5 (`session_search` toolset).
- **Не увеличивать лимиты** — bloat = проблема.

## 5. Aider + CONVENTIONS.md

**CONVENTIONS.md** (`docs/CONVENTIONS.md`) — правила для Aider (стиль, workflow, запреты).
**Подключается автоматически** через `aider_runner.py` → `--read`.

**Когда редактировать:**
- Изменение стиля кода.
- Новые ограничения для Aider-сессий.
- Не дублировать `CODE_EDITING_RULES.md` (методы правки).

## 6. CI

**Файл:** `.github/workflows/ci.yml`.

**Jobs:**
- `test` — `pytest` + `ruff`.
- `consistency` — `bash scripts/check_consistency.sh`.
- `gitleaks` — проверка секретов.

**При падении:**
- `test` — фиксить код.
- `consistency` — фиксить drift (см. §1–3).
- `gitleaks` — **утечка секрета!** Остановиться, отозвать ключ.

## 7. PROJECT-MAP / PROJECT-STATE

**PROJECT-MAP.md** — навигация. Обновлять при:
- Новом canonical document.
- Изменении source-of-truth rules.

**PROJECT-STATE.md** — текущее состояние. Обновлять при:
- Смене CP / HEAD.
- Завершении крупной работы.
- Новых known warnings.

## 8. Быстрая шпаргалка

| Задача | Команда |
|--------|---------|
| Проверить drift | `bash scripts/check_consistency.sh` |
| Полная проверка перед коммитом | `bash scripts/selfcheck.sh` |
| Регенерировать INDEX | `python3 scripts/checks/check_dec_index.py` |
| Проверить INDEX (без правки) | `python3 scripts/checks/check_dec_index.py --check` |
| Проверить CP sync | `python3 scripts/checks/check_cp_sync.py` |
| Проверить DEC порядок | `python3 scripts/checks/check_dec_order.py` |
| Проверить README count | `python3 scripts/checks/check_doc_counts.py` |

## 9. Ссылки

- `docs/PROJECT-MAP.md` — навигация по canonical sources.
- `docs/PROJECT-STATE.md` — текущее состояние.
- `docs/INDEX.md` — автогенерированный список DEC.
- `docs/OPERATIONS.md` — полный справочник команд.
- `docs/USER-GUIDE.md` — руководство пользователя.
- `DECISIONS.md` — архитектурные решения.
