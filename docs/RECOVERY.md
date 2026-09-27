# Восстановление системы Hermes-Titan

Три уровня восстановления — от частного к полному.

## Уровень 1 — Чекпоинты сессии

**Когда:** агент сломал файл в проекте, нужен откат правок.

**Инструменты:**
- В сессии Hermes: `/rollback` (откат последней правки).
- CLI: `hermes checkpoints status` (проверить размер).
- Обслуживание: `hermes checkpoints prune` (удалить устаревшие).
- Полная очистка: `hermes checkpoints clear` (ВСЕ чекпоинты — осторожно).

**Путь:** `/mnt/ai-ssd/hermes/checkpoints/`.

## Уровень 2 — История проекта (git-теги CP)

**Когда:** весь проект `~/ai-system` сломан, нужен откат к контрольной точке.

**Инструменты:**
- Посмотреть теги: `cd ~/ai-system && git tag -l "CP-*"`.
- Откат: `git checkout CP-XXX` (detached HEAD, для просмотра).
- Полный откат main: `git reset --hard CP-XXX && git push --force-with-lease origin main`.
- Клонирование с GitHub: `git clone git@github.com:artemfire1980/hermes-titan.git`.

**Теги:** CP-000 … CP-011 (по мере прохождения).

## Уровень 3 — Полный бэкап

### 3.1. Штатный бэкап Hermes

**Full (zip всего HERMES_HOME, кроме кода):**
hermes backup -o /path/to/hermes-full.zip -k 3
- Размер: ~2.2 MB (проверено 2026-09-27).
- `-k 3` — хранить 3 последних.
- Восстановление: `hermes import /path/to/hermes-full.zip`.

**Quick (snapshot критичных файлов):**
hermes backup --quick -l <label>

- Создаёт snapshot в `HERMES_HOME/state-snapshots/<timestamp>-<label>/`.
- **Игнорирует `-o`** — всегда пишет в `state-snapshots/`.
- Восстановление: `/snapshot restore <timestamp>-<label>` (внутри Hermes).

### 3.2. Наши данные (`~/ai-system`)

**Бэкап:**

~/ai-system/scripts/backup.sh
- Создаёт `~/ai-system/backups/<timestamp>/`.
- Содержит: `tasks_dump.sql`, `tasks.legacy.db`, `configs/`, `docs/`, `*.md`, `manifest.json`.
- Размер: ~236 KB (проверено 2026-09-27).
- **`backups/` в `.gitignore`** — не коммитится.

**Восстановление:**
- Скопировать нужные файлы из `backups/<timestamp>/` обратно в `~/ai-system/`.
- SQLite: `sqlite3 ~/ai-system/data/tasks.db < backups/<timestamp>/tasks_dump.sql`.

## Полное восстановление VIM4 с нуля

1. OOWOW → Ubuntu 24.04.5 LTS (Fenix 1.7.5).
2. Подключить SSD, смонтировать в `/mnt/ai-ssd`.
3. `git clone git@github.com:artemfire1980/hermes-titan.git ~/ai-system`.
4. Установить Hermes: `HERMES_HOME=/mnt/ai-ssd/hermes curl … install.sh | bash`.
5. `hermes import <полный бэкап.zip>`.
6. Проверить: `hermes doctor`, `hermes memory status`, `hermes gateway status`.
7. Docker: `cd /mnt/ai-ssd/freellmapi && docker compose up -d`, то же для SearXNG.
8. Проверка: `curl http://127.0.0.1:3001/api/ping`, `curl http://127.0.0.1:8888/`.

## Тест восстановления (mandatory)

Раз в неделю (или перед крупными изменениями):
1. `hermes backup -o /tmp/test-backup.zip`.
2. `hermes checkpoints status`.
3. `~/ai-system/scripts/backup.sh`.
4. Убедиться: файлы созданы, размеры разумные.
5. `git status` — чистый.

Полный тест восстановления — на CP-011.
