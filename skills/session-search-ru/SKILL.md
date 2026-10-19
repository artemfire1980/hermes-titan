---
name: session-search-ru
query: "история сессий, предыдущий запрос, что я спрашивал, раньше, вчера, session_search, кириллица"
description: Поиск по истории сессий Hermes с поддержкой кириллицы (trigram).
version: 0.1.0
author: Artem (artemfire1980), Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Session, Search, History, Cyrillic, Trigram]
---

# Session Search RU

Поиск по прошлым сессиям Hermes с **точной** поддержкой кириллицы. Обход проблемы: встроенный `session_search` использует `messages_fts` (unicode61) — плохо ищет русский. Скрипт использует `messages_fts_trigram` (FTS5 trigram) — работает точно.

## Когда использовать

- Пользователь говорит «из предыдущего запроса», «что я спрашивал», «как я говорил», «раньше», «вчера».
- Запрос **на русском** (кириллица).
- Встроенный `session_search` **не нашёл** (или нашёл мусор).

**НЕ использовать** для поиска в интернете или документации — только для истории сессий Hermes.

## Prerequisites

- `state.db` в `/mnt/ai-ssd/hermes/state.db`.
- Скрипт `~/ai-system/scripts/session_search_ru.py`.

## Процедура

### 1. Запустить поиск

    python3 ~/ai-system/scripts/session_search_ru.py "Самсонов"

Вывод: список сессий (title, session_id, snippet, link). **Одна сессия = одна строка** (дедуп по `session_id`).

**Временные маркеры (обязательно):**
- «в прошлый раз», «раньше», «до этого» → добавь `--before today`
- «вчера» → добавь `--before yesterday`
- «на этой неделе» → `--after <7 дней назад>`
- если пользователь помнит **конкретную** сессию, а её нет в топ-10 → `--limit 20`

### 2. Показать пользователю

- **Список сессий** (не одно сообщение): заголовок + snippet + link.
- Если сессий > 5 — покажи **топ-5** и напиши «ещё N — скажи, покажу».
- Snippet (первые 150 символов).
- Link `@session:default/<id>`.

### 3. Если нужно прочитать всю сессию

    # Запомнить session_id из вывода
    # Затем через встроенный session_search:
    # session_search(session_id=<id>, around_message_id=<msg_id>)

## Completion criterion

Пользователь получил список сессий с релевантным snippet.

## Pitfalls

- **Встроенный `session_search`** — плохо ищет кириллицу (`messages_fts` = unicode61). **Не использовать** для русского.
- **`messages_fts_trigram`** — требует минимум 3 символа (trigram). Запросы из 1–2 букв не работают.
- **Кириллица + латиница** — trigram работает для обоих.
- **Свежесть ≠ релевантность.** Сортировка по времени: если сегодня было много запросов с тем же словом, старая сессия уйдёт за топ-10. Решение: `--limit 20` или `--before <дата>`.
- **«В прошлый раз» — не всегда вчера.** Если пользователь говорит «в прошлый раз», а сегодня уже были сессии — `--before today` отсечёт сегодняшние тесты.

## Verification

- `python3 ~/ai-system/scripts/session_search_ru.py "Самсонов"` — находит сессии.
- Snippet релевантен запросу.

## Quick Reference

| Задача | Команда |
|---|---|
| Поиск | `python3 ~/ai-system/scripts/session_search_ru.py "запрос"` |
| С лимитом | `... --limit 5` |
| «В прошлый раз» | `... "запрос" --before today` |
| «Вчера» | `... "запрос" --before yesterday` |
| Конкретная старая сессия | `... "запрос" --limit 20 --before 2026-10-01` |
| Читать сессию | `session_search(session_id=<id>, around_message_id=<msg_id>)` |
