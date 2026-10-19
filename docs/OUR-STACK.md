# OUR-STACK — что мы добавили поверх Hermes

> Инвентарь сторонних решений проекта HERMES-TITAN.
> Обновлять при добавлении/удалении.
> Проверять при обновлении Hermes — что можно заменить встроенным.

## 1. MCP-серверы

| Имя | Инструментов | Источник | Может быть заменено |
|---|---|---|---|
| kiln | 74 | самодельный (proxy) | — |
| rubit-mail | 5 | PyPI (rubit-mcp-mail 1.0.0) | встроенный mail MCP (если появится) |
| moysklad | 4 | официальный (mcp.moysklad.ru) | — |

## 2. Skills (наши)

| Skill | Проект | Может быть заменено |
|---|---|---|
| moysklad-workflow, moysklad-query, data-integration | МойСклад | — |
| kiln-printer, kiln-analyze, kiln-safety | Kiln | — |
| mail, email-correspondence-analyzer, himalaya, email-inbox-triage | Почта | встроенный email MCP (email-platform) |
| update-hermes | Hermes | — |
| voice-transcription | Voice | stt.streaming (v0.21.6+) — проверить |
| industry-event-research, competitor-news-monitor | Research | — |
| user-preferences-artem | Персонализация | — |

## 3. Скрипты (в ~/ai-system/scripts/)

| Скрипт | Назначение | Может быть заменено |
|---|---|---|
| resource-governor.sh | MAX_HEAVY-блокировка | hermes pause (другое) — НЕ замена |
| git-auto-push.sh | Автопуш в GitHub | — |
| backup.sh | Бэкап HERMES_HOME | hermes backup (встроен) — проверить |
| holographic-patch.sh | Патч Holographic | НЕ нужен в v0.22.0 (Holographic external) |
| selfcheck.sh | Самопроверка | hermes doctor (встроен) |
| send_to_telegram.py | Отправка в Telegram | hermes send (встроен) — ЗАМЕНЁН |
| aider_runner.py | Запуск Aider | — |
| research-telegram.sh | Research → Telegram | — |
| md2docx.py | MD → DOCX | — |

## 4. Плагины

| Плагин | Версия | Источник | Может быть заменено |
|---|---|---|---|
| progressive-skill | 3.2.1 | git | upstream skills system — проверить |

## 5. Патчи pyproject.toml

| Патч | Причина | Может быть убрано |
|---|---|---|
| `browser-harness` закомментирован | битый wheel (CDN Nous) | если wheel исправят |
| `nemo-relay` закомментирован | не нужен (DEC-046) | — |
| `tool.uv.environments` — android исключён | playwright не имеет wheel | если playwright исправят |

## 6. Cron / Timer

| Юнит | Назначение | Может быть заменено |
|---|---|---|
| holographic-patch.timer | (disabled) | НЕ нужен в v0.22.0 |
| git-auto-push (cron) | Автопуш | — |

## 7. Memory

| Компонент | Версия | Может быть заменено |
|---|---|---|
| Holographic memory | community 0.17.4 | — |
| MEMORY.md | universal | — |

## 8. Как обновлять этот файл

- При добавлении нового решения — добавить в таблицу.
- При обновлении Hermes — проверить «Может быть заменено».
- При удалении нашего решения — удалить из таблицы.

## 9. Cron jobs (Hermes)

| Job | Schedule | Script | Mode |
|---|---|---|---|
| `moysklad-refresh-weekly` | `0 6 * * 1` (Пн 6:00) | `moysklad_refresh.py` | `--no-agent`, deliver telegram |
| `mail-check-daily` | `0 9 * * *` (каждый день) | `mail_check.py` | `--no-agent`, deliver telegram |
| `update-stack-weekly` | `0 10 * * 1` (Пн 10:00) | skill `update-stack` | deliver telegram |

Скрипты:
- `~/ai-system/scripts/moysklad_refresh.py` (git) → `HERMES_HOME/scripts/` (копия).
- `~/ai-system/scripts/mail_check.py` (git) → `HERMES_HOME/scripts/` (копия).

Синхронизация: `~/ai-system/scripts/sync-cron-scripts.sh`.

## 10. Что удалено (cleanup 2026-10-17)

- `holographic-patch.sh` — не нужен в v0.22.0 (Holographic external).
- `holographic-patch.service` / `.timer` — systemd units удалены.
- `.titan-backup` файлы — очищены.

## 11. FreeLLMAPI

| Параметр | Значение |
|---|---|
| Версия | v0.16.4 (фиксированный тег, авто-обновление) |
| Образ | `ghcr.io/tashfeenahmed/freellmapi:v0.16.4` |
| Порт | `127.0.0.1:3001` |
| Стратегия | **reliable** (Самый надёжный) |
| Context Handoff | `on_model_switch` |
| Модель (auto) | DeepSeek V4 Flash (`routeway/deepseek-v4-flash:free`) |
| ENCRYPTION_KEY | в `.env` (не менять!) |
| Volume | `freellmapi-data` (не удалять!) |

**Обновление:**
1. `docker compose pull`
2. `docker compose up -d --force-recreate`
3. Проверить `X-Routed-Via` тестовым запросом.

**Что нового в v0.16.4:**
- Parallel (бесплатный поиск без ключа).
- Auray (новый провайдер).
- MCP: provider_list, quota_outlook, clear_cache.
- Автоочистка БД.
