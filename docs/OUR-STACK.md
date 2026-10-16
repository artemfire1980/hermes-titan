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
| progressive-skill | 3.2.0 | git | upstream skills system — проверить |

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
| Holographic memory | community 0.13.0 | — |
| MEMORY.md | universal | — |

## 8. Как обновлять этот файл

- При добавлении нового решения — добавить в таблицу.
- При обновлении Hermes — проверить «Может быть заменено».
- При удалении нашего решения — удалить из таблицы.
