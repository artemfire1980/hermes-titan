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

Вывод: список сессий (title, session_id, snippet, link).

### 2. Показать пользователю

- Заголовок сессии.
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

## Verification

- `python3 ~/ai-system/scripts/session_search_ru.py "Самсонов"` — находит сессии.
- Snippet релевантен запросу.

## Quick Reference

| Задача | Команда |
|---|---|
| Поиск | `python3 ~/ai-system/scripts/session_search_ru.py "запрос"` |
| С лимитом | `... --limit 5` |
| Читать сессию | `session_search(session_id=<id>, around_message_id=<msg_id>)` |
