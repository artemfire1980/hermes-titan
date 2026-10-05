# HERMES-TITAN — Current State

> Компактный снимок «где мы сейчас». Обновляется вручную.
> Обновлено: 2026-10-03.

## Current

- **Контрольная точка:** CP-037
- **Версия:** 0.37.0
- **Ветка:** main
- **HEAD:** 7887cb2
- **Последнее решение:** DEC-049 (SearXNG + Exa)

## Active work

- Persistent memory architecture (внедрение)

## Last completed

- 2026-10-05: Kiln MCP (71 read-tool) — 3D-принтер ZAV (DEC-053)
- 2026-10-05: rubit-mcp-mail (5 read-tool) — почта Mail.ru (DEC-054)
- 2026-10-05: МойСклад — официальный MCP, 4 read-only tools (DEC-056)
- 2026-10-05: docs/INTEGRATIONS.md, KILN.md, MAIL.md, MOYSKLAD.md, PRINTER-CONFIG.md

- STT (faster-whisper + av 18.1.0) — DEC-052

- CP-037 (оптимизация промпта Telegram)
- Аудит кодовой базы 2026-10-02 (DEC-048, 9 правок)
- Очистка системы 2026-10-03 (~2.2 ГБ)
- Exa `extract_backend` (DEC-049)
- Документация: OPERATIONS.md, STRUCTURE.md, USER-GUIDE.md
- Drift fix: README (49 DEC), IMPLEMENTATION_STATUS (CP-011)
- Memory hygiene: Holographic очищен, MEMORY.md/USER.md перезаписаны

## Next

1. Фаза 2 — deterministic consistency check (gen_agent_brief + check_consistency)
2. Фаза 3 — CONVENTIONS.md для Aider
3. Фаза 4 — Aider `--read CONVENTIONS.md`
4. Фаза 6 — пересмотр `max_in_progress` (8 → 2)

## Blocked

- Нет.

## Episodic memory

- **`state.db`** — FTS5 (`messages_fts` + `messages_fts_trigram`).
- **Toolset** `session_search` — enabled.
- **Использование:** поиск по прошлым сессиям (731 messages в 15 sessions на 2026-10-03).
- **Не дублировать** эпизоды в `MEMORY.md` — они уже индексируются.

## Known warnings

- DEC-036 противоречит DEC-038 (`ensure-hrr-numpy` удалён, но DEC-036 описывает старое состояние). Не критично.
- `max_in_progress=8` — вероятный OOM при 8 воркерах. Пересмотреть.
- `docs/PROJECT-MAP.md` и `docs/PROJECT-STATE.md` — обновлять вручную при изменениях.

## Canonical navigation

См. `docs/PROJECT-MAP.md`.
