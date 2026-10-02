# Оптимизация системного промпта Hermes для Telegram (CP-037)

**Дата:** 2026-10-02
**Контекст:** оптимизация фиксированного overhead в Telegram

## Итоговые цифры

| Компонент | Оригинал | После оптимизации | Экономия |
|-----------|---------:|------------------:|---------:|
| System prompt | ~30 000 B | **13 153 B** | **−56%** |
| Skills index | ~14 600 B | **0 B** | **−100%** |
| Memory | 3 469 B | 1 626 B | — |
| User profile | 2 583 B | 1 638 B | — |
| Tools JSON | ~49 000 B | **36 322 B** | **−26%** |
| **ИТОГО** | **~101 KB** | **~52 KB** | **−48%** |

## Что сделано

### 1. Плагин `progressive-skill`

- Установлен из `freehul/progressive-skill`
- Демотирует описания скиллов в names-only (имена остаются видимыми)
- Использует нативный механизм `compact_categories` Hermes
- **Эффект:** Skills: 5 456 → **0 B**

### 2. `tools.compact_schemas: true`

- Убирает parameter-level descriptions из JSON-схем
- Обрезает tool descriptions до первого предложения
- **Эффект:** System prompt: 16 477 → **13 153 B**

### 3. `tool_search.defer`

- Deferred: `delegation`, `session_search`, `todo_list`, `cronjob_manage`, `image_generate`, `computer_use`, `process_manage`
- **Эффект:** часть tools не грузится в промпт сразу

### 4. `skills.platform_disabled.telegram`

Отключены 20 скиллов:
airtable, ascii-video, box, claude-code, claude-design, codex, computer-use, google-workspace, humanizer, inspecting-hermes-desktop-dom, manim-video, maps, meeting-action-items, notion, opencode, popular-web-designs, songwriting-and-ai-music, teams-meeting-pipeline, weekly-review-planning, xurl

**Результат:** бот видит 35 скиллов в 10 категориях.

## Что НЕ удалось

### `skills.prompt_mode: compact`

- Опция существует в коде (PR #40993)
- **Но не активируется** через `config set` — `not a recognized config key`
- Причина: upstream **сознательно не удаляет имена скиллов** (silent-capability-loss regression)

### `tools.deferrable`

- Опция есть в main (PR #40993)
- **Но не активируется** — `not a recognized config key`
- Можно попробовать вручную через `config.yaml`

## Что осталось

**Дальнейшая оптимизация:**

1. **`tools.deferrable`** — принудительный defer для core tools:
   - `session_search` (~1 400 B)
   - `todo` (~150 B)
   - `cronjob` (~100 B)
   - **Экономия:** ~2 500 B

2. **Cache tools schema** (Issue #20880) — ждать, пока появится в main.

3. **Boilerplate в system prompt** — патч ядра или плагин:
   - `## Skills` guidance: 2 932 B → ~600 B
   - Memory guidance: 1 134 B → ~250 B
   - Docs reference: 470 B → ~90 B
   - **Экономия:** ~3 800 B

## Источники

- RFC #64876 — Prompt Architecture Optimization
- Issue #34667 — 30KB system prompt
- Issue #67273 — 31 tools, 12,150 tokens schemas
- Issue #20880 — 70% input-token overhead
- PR #40993 — `compact_schemas`, `compact` mode, `deferrable`
- PR #39184 — Skill index optimization (10.6 KB → 4.9 KB)
- Issue #10164 — 100KB overhead, prefill benchmark
- Medium — 26 tools, 44,428 B tool schemas
