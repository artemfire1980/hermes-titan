# Архитектура

- **Ядро** — готовый Hermes Agent. Наш код — тонкий слой.
- **Два двигателя**: данные (детерминированное извлечение) и разработка (исследование + код).
- **Обязательная инфраструктура**: FreeLLMAPI (агрегатор бесплатных моделей) + SearXNG (метапоиск).
- **Три уровня восстановления**: чекпоинты сессии, история проекта (git), полный бэкап.
- **Облачные хранилища** — только при доказанной необходимости.

## Ядро и стек (2026-10-19)

- **Hermes Agent** — v0.22.0+1.g494038c (stable).
- **FreeLLMAPI** — v0.16.6 (фиксированный тег, `127.0.0.1:3001`, `auto`, 1M ctx).
- **SearXNG** — Docker, `127.0.0.1:8888` + Exa (semantic extract).
- **Aider** — `nvidia_nim/nvidia/nemotron-3-ultra-550b-a55b`.
- **Kanban** — board `hermes-titan`, dispatcher в gateway (60s).
- **MCP** — kiln (74 tools), rubit-mail (5), moysklad (4).

## Память

- **MEMORY.md** — 1035 chars (universal + маршрутизация).
- **Holographic** — community 0.17.4, 53 факта, 29 entities.
- **Skills** — 15 local (query + recall + алгоритмы).
- **Docs** — OUR-STACK, MOYSKLAD-OUR-SETUP, EMAIL-OVERDUE, MEMORY-SNAPSHOT.

**Маршрутизация:** keyword → skill (query) → recall → API (если свежее).

## Автоматизация (cron)

| Job | Schedule | Что |
|---|---|---|
| `moysklad-refresh-weekly` | Пн 6:00 | email_base.json (1701) |
| `mail-check-daily` | 9:00 | unread в INBOX |
| `update-stack-weekly` | Пн 10:00 | changelog FreeLLMAPI/плагины/MCP + Telegram |

**Скрипты:** `~/ai-system/scripts/` → копии в `HERMES_HOME/scripts/`. Синхронизация — `sync-cron-scripts.sh`.

## Три уровня восстановления

- **Чекпоинты** сессии.
- **История** проекта (git).
- **Полный бэкап** (`hermes backup`).

## Облачные хранилища

Только при доказанной необходимости.
