# Аудит возможностей ядра Hermes

**Дата:** 2026-09-26
**Версия Hermes:** v0.21.5+2453.gd0288be (main @ d0288be5)
**Автор:** аудит проведён в рамках CP-003

---

## Цель

Зафиксировать, что Hermes Agent умеет **из коробки**, чтобы не строить самописные решения там, где ядро уже покрывает задачу.

**Принцип:** Hermes-first. Своё — только для реально недостающего.

---

## Матрица возможностей

| Возможность | Штатное в Hermes | Нужно своё? | Обоснование |
|-------------|------------------|-------------|-------------|
| **Задачи / канбан** | `hermes kanban` (boards, tasks, dependencies, swarm, dispatch, LLM-decompose, review-workflow) | ❌ нет | Покрывает CP-007 полностью |
| **Проекты** | `hermes project` (multi-folder, bind-board, per-profile state) | ❌ нет | Покрывает CP-007 |
| **Память (built-in)** | `MEMORY.md` + `USER.md` (всегда работает) | ❌ нет | Базовое покрытие |
| **Память (внешняя)** | `hermes memory` — 7 провайдеров: byterover, holographic, honcho, mem0, openviking, retaindb, supermemory | ⏳ по бенчмарку (CP-008) | Свой не строим, выбираем по бенчмарку |
| **Скиллы** | `hermes skills` — 53 builtin + `browse/search/install` из registry | ❌ нет | Покрывает CP-003 |
| **Скиллы (bundles)** | `hermes bundles` — алиасы для групп скиллов | ❌ нет | Дополнительно |
| **Плагины** | `hermes plugins` — install/search/list/enable/disable | ❌ нет | Дополнительно |
| **MCP** | `hermes mcp` — add/remove/list/test/catalog/install | ❌ нет | Дополнительно (не используем сейчас) |
| **Fallback провайдеров** | `hermes fallback` — chain с auto-retry | ❌ нет | Покрывает CP-004 |
| **Модели** | `hermes model` — интерактивный селектор + `hermes config set` | ❌ нет | Покрывает CP-001.4 |
| **Auth (pooled credentials)** | `hermes auth` — add/list/remove/priority/refresh | ❌ нет | Дополнительно |
| **Секреты (внешние)** | `hermes secrets` (Bitwarden, 1Password) | ❌ нет | Не используем |
| **Бэкапы** | `hermes backup` (full + `--quick` + `-k N`) + `hermes import` | ⏳ частично | Свой backup.sh для наших данных в `~/ai-system` |
| **Чекпоинты** | `hermes checkpoints status/prune/clear` (shadow git) | ❌ нет | Покрывает CP-010 |
| **Безопасность** | `hermes security` (OSV.dev audit) | ❌ нет | Дополнительно |
| **Smoke-test проекта** | `hermes verify` | ❌ нет | Дополнительно |
| **Аналитика** | `hermes insights` | ❌ нет | Дополнительно |
| **Cron** | `hermes cron` (create/list/update/pause/resume/run) | ❌ нет | Покрывает scheduled tasks |
| **Gateway** | `hermes gateway` (setup/install/start/stop/status) | ❌ нет | Покрывает CP-002 |
| **Web UI** | `hermes dashboard` (порт 9119) | ❌ нет | Дополнительно |
| **Headless backend** | `hermes serve` | ❌ нет | Дополнительно |
| **ACP** | `hermes acp` (Agent Client Protocol) | ❌ нет | Дополнительно |
| **Профили** | `hermes profile` (изолированные инстансы) | ❌ нет | Дополнительно |
| **Сессии** | `hermes sessions list/rename/export/prune/delete` | ❌ нет | Дополнительно |
| **Логи** | `hermes logs` (agent/errors/gateway/gui/desktop) | ❌ нет | Покрывает отладку |
| **Kanban swarm** | `hermes kanban swarm` — параллельные воркеры → верификатор → синтезатор | ❌ нет | Покрывает research-orchestration |

---

## Что оставляем самописным

| Компонент | Почему |
|-----------|--------|
| **`aider-wrapper.sh`** | Изоляция исполнителя кода (CP-006), security |
| **`git-auto-push.sh`** | Secret detection + auto-commit для `~/ai-system` |
| **`backup.sh` (для наших данных)** | Дамп `tasks.db` (если будет), `configs/`, документации |
| **`tasks.db` (частично)** | Только для того, что kanban не покрывает: git-теги, решения, артефакты. Решение — на CP-007 после изучения схемы `kanban.db` |
| **`research_runner.py`** (если будет) | Уникальный pipeline с citations, если SearXNG + skills не покроют |
| **`ctx7` через CLI+Skills** | DEC-006 — не MCP |

---

## Изменения в плане v7.2

Сравнение плана с фактами:

| CP в плане | Изменение |
|------------|-----------|
| CP-002 | Ручной systemd unit → **`hermes gateway install`** (штатно) |
| CP-003 | Свой аудит → **`hermes tools list` / `hermes skills list` / `hermes plugins list`** |
| CP-004 | Ручной провайдер → **`hermes config set model.provider` + `hermes auth add`** |
| CP-007 | Своя tasks.db → **`hermes kanban`**, своя БД только для реально недостающего |
| CP-008 | «Провайдеры определяются версией» → **фиксированный список 7 провайдеров** |
| CP-010 | Свой backup.sh + ручной restore → **`hermes backup` + `hermes import`** для ядра, свой скрипт только для наших данных |

---

## Выводы

1. **Ядро Hermes покрывает ~85% плана v7.2.** Самописного кода — минимум.
2. **`hermes kanban` + `hermes project`** — заменяют предполагавшуюся свою систему задач.
3. **`hermes backup` + `hermes checkpoints`** — заменяют свой слой бэкапов для ядра.
4. **`hermes memory` (7 провайдеров)** — выбор по бенчмарку (CP-008), не своё.
5. **Свой код остаётся** только для: изоляции Aider, secret detection, и уникального research-pipeline (если понадобится).

---

## Действия для следующих CP

- **CP-004 (FreeLLMAPI):** добавить `hermes fallback` после настройки primary. Проверить `hermes auth add` для OpenAI-совместимых.
- **CP-005 (аудит старой системы):** распаковать `vim4_golden_snapshot.7z` (пароль отдельно), сравнить с тем, что уже есть в ядре.
- **CP-007 (двигатель разработки):** сначала изучить схему `kanban.db`, потом решать про свою tasks.db.
- **CP-008 (память):** бенчмарк по 7 провайдерам (`hermes memory setup`).
- **CP-010 (бэкапы):** `hermes backup --quick` + `hermes backup` (полный) + свой скрипт для `~/ai-system`.
