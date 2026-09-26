# Решение по трекеру задач

**Дата:** 2026-09-26
**Контекст:** CP-007 — двигатель разработки

## Решение

**Используем штатный `hermes kanban`.** Своя `tasks.db` **не создаётся**.

## Обоснование

1. **Kanban покрывает всё:**
   - Доски (`boards`) — изоляция потоков работ.
   - Задачи (`create/list/show/assign/claim/complete`).
   - Зависимости (`link/unlink`).
   - Ревью (`request-review/request-changes`).
   - Swarm (`swarm`) — параллельные воркеры.
   - LLM-помощники (`specify/decompose`).
   - Обслуживание (`gc/repair/stats/tail/watch`).

2. **Интеграция с gateway:** dispatcher встроен, ticks every 60s.

3. **Интеграция с project:** `hermes project bind-board` даёт детерминированные
   worktree + branch для задач.

4. **Интеграция с Aider:** worker → terminal tool → `aider-runner.py`.

5. **Проверено:** задача `t_a11011c9` завершена за 26 секунд полным циклом.

## Что НЕ используем

- Свою `tasks.db` (`scripts/task_ledger.py`) — оставлен **только для логирования**
  запусков Aider (импортируется из `aider-runner.py`).
- `scripts/ledger-viewer.py` — для просмотра старой `tasks.db` (архив).

## Старая `data/tasks.legacy.db`

Сохранена как **архив** (`data/tasks.legacy.db`, 36 KB).
Просмотр: `sqlite3 data/tasks.legacy.db "SELECT * FROM tasks LIMIT 10;"`.

## Что отложено

- Своя БД для **git-тегов, решений, артефактов** — если kanban не покроет
  в будущем. Пока не нужно.
