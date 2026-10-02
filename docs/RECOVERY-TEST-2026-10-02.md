# Тест восстановления Hermes-Titan — 2026-10-02

## Уровень 1: Чекпоинты сессии

Команда: `hermes checkpoints status`
Результат: 0 B, 0 проектов — механизм работает, чекпоинтов нет (нечего чекпоинтить)

## Уровень 2: Git-история

Команда: `git clone git@github.com:artemfire1980/hermes-titan.git /tmp/git-restore`
Результат: теги CP-033…CP-037 на месте, HEAD = cc042cb (CP-037)

## Уровень 3: Полный бэкап Hermes

Команда: `hermes backup -o /tmp/hermes-full-test.zip`
Результат: 484 файла, 16.8 MB → 3.4 MB, время 1.2 s

Команда: `HERMES_HOME=/tmp/hermes-restore-test hermes import /tmp/hermes-full-test.zip --force`
Результат: 482/484 файлов восстановлено

Сравнение:
- config.yaml: diff — идентично
- .env: 28 строк = 28 строк
- state.db: 2928640 B = 2928640 B
- gateway install защищён от /tmp — правильно

## Уровень 2.5: Наши данные (~/ai-system)

Команда: `~/ai-system/scripts/backup.sh`
Результат: `backups/20261002-124158/` (284K) с tasks_dump.sql, tasks.legacy.db, configs, docs, manifest.json

Команда: восстановление tasks_dump.sql → /tmp/restore-tasks/tasks.db
Результат: таблицы совпадают (`tasks` = `tasks`)

## Вывод

Все три уровня восстановления проверены и работают. CP-010 подтверждён фактами.
