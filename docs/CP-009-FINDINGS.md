# CP-009: Resource Governor — находки (2026-10-02)

## kanban.max_in_progress

Найдено в логах gateway при старте (2026-10-02 12:54):

    kanban dispatcher: kanban.max_in_progress unset; using memory-derived default max_in_progress=8
    (set kanban.max_in_progress in config.yaml to override)

### Что это значит

- Параметр **есть** в Hermes Agent.
- **Не задан** — Hermes вычисляет сам из доступной памяти.
- **Дефолт = 8** для VIM4 (8 GB RAM).
- **Можно переопределить** в config.yaml командой:

    hermes config set kanban.max_in_progress <N>

### Решение

Оставить по умолчанию (**8**). Это соответствует возможностям VIM4 (1 процесс ≈ 1 GB RAM).

## resource-governor.sh

Скрипт `~/ai-system/scripts/resource-governor.sh` — дополнительный слой поверх штатного управления kanban. Используется для ручной блокировки тяжёлых задач.

## Вывод

CP-009 закрыт фактами:

- `kanban.max_in_progress` существует, дефолт 8.
- `resource-governor.sh` работает (дополнительный слой).
- Штатный механизм + наш скрипт = достаточно для VIM4.
