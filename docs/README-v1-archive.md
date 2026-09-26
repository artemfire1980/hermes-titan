# 🤖 Hermes Agent System для VIM4 — Полная документация для AI-агентов

**Версия**: 3.1
**Дата**: 2026-09-21
**Платформа**: Khadas VIM4 (ARM64), Ubuntu 24.04.5 LTS  
**Репозиторий**: https://github.com/<GITHUB_USER>/<REPO_NAME>

---

## 📋 Содержание

1. Обзор архитектуры
2. Файловая система и пути
3. Системные компоненты
4. Скрипты и runners
5. Скиллы Hermes
6. Docker контейнеры
7. Безопасность
8. Автоматизация (Cron)
9. Git и автопуш
10. Примеры использования
11. API и интерфейсы
12. Troubleshooting
13. Восстановление системы
14. Разработка и модификация

---

## 🏗️ 1. Обзор архитектуры

### Логическая схема

```
┌─────────────────────────────────────────────────────────────┐
│                    TELEGRAM USER (Artem)                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Hermes Gateway (systemd service)                 │
│              PID: ~388199 | RAM: ~305MB                       │
│              Port: internal only                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┼───────────────────┐
        ↓                   ↓                   ↓
   ┌─────────┐        ┌─────────┐         ┌─────────┐
   │ /research│        │ Aider   │         │ General │
   │  skill   │        │  skill  │         │  chat   │
   └─────────┘        └─────────┘         └─────────┘
        ↓                   ↓                   ↓
   ┌─────────┐        ┌─────────┐         ┌─────────┐
   │research-│        │aider-   │         │  LLM    │
   │runner.py│        │runner.py│         │  calls  │
   └─────────┘        └─────────┘         └─────────┘
        ↓                   ↓                   ↓
   ┌─────────┐        ┌─────────┐         ┌─────────┐
   │ SearXNG │        │ NVIDIA  │         │FreeLLM  │
   │  :8888  │        │   NIM   │         │  :3001  │
   └─────────┘        └─────────┘         └─────────┘
```

### Ключевые принципы

1. **Единый source of truth**: `~/ai-system/` — git-репозиторий, синхронизируется с GitHub
2. **Симлинки вместо копий**: `~/bin/*` → `~/ai-system/scripts/*`
3. **Защита ядра**: Aider НЕ может модифицировать `~/ai-system` и `~/.hermes`
4. **Автопуш каждые 6 часов**: `git-auto-push.sh` с проверкой секретов
5. **Hermes читает скиллы из**: `/mnt/ai-ssd/hermes/skills/` (= `~/.hermes/skills/`)
6. **HERMES_HOME**: `/mnt/ai-ssd/hermes`

---

## 📁 2. Файловая система и пути

### Полная карта путей

```
/mnt/ai-ssd/                        ← SSD (быстрый NVMe)
├── hermes/                         ← HERMES_HOME (реальное расположение)
│   ├── hermes-agent/               ← Python код Hermes + venv
│   │   ├── venv/                   ← Python venv с aider 0.86.2
│   │   ├── hermes_cli/             ← CLI модуль
│   │   └── tools/                  ← mcp_death_supervisor.py
│   ├── skills/                     ← 60 встроенных скиллов (13 категорий)
│   │   ├── aider-delegate/SKILL.md
│   │   ├── research/
│   │   │   ├── deep-research/SKILL.md
│   │   │   ├── arxiv/SKILL.md
│   │   │   ├── competitor-news-monitor/SKILL.md
│   │   │   ├── grounded-citations/SKILL.md
│   │   │   └── llm-wiki/SKILL.md
│   │   ├── software-development/   ← 12 скиллов
│   │   ├── creative/               ← 10 скиллов
│   │   ├── productivity/           ← 14 скиллов
│   │   └── ...                     ← apple, devops, email, media, etc.
│   ├── skill-bundles/              ← Точки входа для команд
│   │   └── research.yaml           ← /research команда
│   ├── config.yaml                 ← Основной конфиг Hermes
│   ├── auth.json                   ← Credentials
│   ├── .env → ~/ai-system/.env     ← Симлинк на секреты
│   ├── mcp-servers/                ← MCP серверы
│   │   └── node_modules/@upstash/context7-mcp/
│   ├── node/                       ← Node.js для MCP
│   ├── logs/                       ← Логи работы
│   ├── kanban.db                   ← База задач
│   ├── state.db                    ← База состояний
│   └── cron/                       ← Hermes cron jobs
│       └── jobs.json               ← 2 активных job'а

/home/khadas/
├── .hermes → /mnt/ai-ssd/hermes    ← Симлинк (удобный алиас)
├── ai-system/                      ← Git репозиторий (source of truth)
│   ├── .git/
│   ├── .env                        ← Секреты (НЕ в git!)
│   ├── .gitignore                  ← Защита секретов
│   ├── README.md                   ← Эта документация
│   ├── scripts/                    ← Все runner'ы и wrapper'ы
│   │   ├── research-runner.py      ← Deep Research v3.0 (997 строк)
│   │   ├── research-telegram.sh    ← Telegram wrapper
│   │   ├── aider-runner.py         ← Aider wrapper v2.2 (331 строка)
│   │   ├── task_ledger.py          ← SQLite ledger для задач
│   │   ├── ledger-viewer.py        ← CLI для просмотра истории
│   │   ├── git-auto-push.sh        ← Автопуш каждые 6 часов
│   │   ├── git-credential-github.sh← GitHub credential helper
│   │   ├── sync-tasks-to-supabase.py
│   │   ├── backup-projects.sh
│   │   ├── check-memory-peak.sh
│   │   ├── check_r2_budget.sh
│   │   └── check-freellm-quotas.sh
│   ├── configs/                    ← Конфигурации (nginx, docker)
│   │   └── hermes/.env.example
│   ├── freellmapi/                 ← Docker compose для FreeLLMAPI
│   │   └── docker-compose.yml
│   ├── searxng/                    ← Docker compose для SearXNG
│   │   └── docker-compose.yml
│   ├── data/                       ← Runtime данные
│   │   ├── tasks.db                ← Task ledger SQLite
│   │   └── runtime.sqlite3
│   ├── logs/                       ← Логи системы
│   │   ├── aider/                  ← Логи Aider запусков
│   │   └── git-auto-push.log
│   ├── runtime/                    ← НЕ в git (runtime данные)
│   │   ├── locks/
│   │   ├── queue/
│   │   └── state/
│   └── research/                   ← НЕ в git (результаты исследований)
│       ├── reports/*.md
│       └── cache/
├── bin/                            ← Исполняемые симлинки
│   ├── research-runner.py     → ~/ai-system/scripts/research-runner.py
│   ├── research-telegram.sh   → ~/ai-system/scripts/research-telegram.sh
│   ├── aider-runner.py        → ~/ai-system/scripts/aider-runner.py
│   ├── task_ledger.py         → ~/ai-system/scripts/task_ledger.py
│   ├── ledger-viewer.py       → ~/ai-system/scripts/ledger-viewer.py
│   ├── git-auto-push.sh       → ~/ai-system/scripts/git-auto-push.sh
│   ├── git-credential-github.sh → ~/ai-system/scripts/git-credential-github.sh
│   ├── sync-tasks-to-supabase.py → ~/ai-system/scripts/sync-tasks-to-supabase.py
│   ├── backup-projects.sh     → ~/ai-system/scripts/backup-projects.sh
│   ├── check-memory-peak.sh   → ~/ai-system/scripts/check-memory-peak.sh
│   └── sync-hermes-vim4.sh    → ~/.hermes/scripts/sync-hermes-vim4.sh
├── projects/                     ← Git проекты пользователя
│   └── aider-test/             ← Тестовый проект Aider
├── research/                     ← Результаты исследований
│   ├── reports/                ← Markdown отчёты
│   └── cache/                  ← Кэш HTML и evidences
├── work/, code/, dev/          ← Разрешённые для Aider папки
└── .config/systemd/user/
    └── hermes-gateway.service  ← Systemd unit + drop-ins
```

### Критически важные симлинки

| Путь | Цель | Назначение |
|------|------|------------|
| `~/.hermes` | `/mnt/ai-ssd/hermes` | HERMES_HOME |
| `~/.hermes/.env` | `~/ai-system/.env` | Секреты для Hermes |
| `~/bin/*.py, *.sh` | `~/ai-system/scripts/` | Единый источник кода |
| `~/bin/sync-hermes-vim4.sh` | `~/.hermes/scripts/` | Hermes-специфичный |

---

## ⚙️ 3. Системные компоненты

### 3.1. Hermes Gateway (systemd)

**Версия**: v0.21.3 (The Pantheon Release, сентябрь 2026)
**Установка**: shallow clone (`--depth 1`) для экономии места на SSD
**Важные изменения в v0.21.3**:
- state.db reliability campaign (44 issues closed)
- Bot Mode — общество агентов с группчатами
- Cron jobs с памятью между запусками (`continuity=true`)
- Live subagent steering — управление subagents в реальном времени
- Password-blind credential vault
- MCP command center

**Расположение**: `~/.config/systemd/user/hermes-gateway.service`

**Конфигурация (основной unit)**:

```ini
[Unit]
Description=Hermes Agent Gateway - Messaging Platform Integration
After=network-online.target
Wants=network-online.target
StartLimitIntervalSec=0

[Service]
Type=simple
ExecStart=/home/khadas/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway run
WorkingDirectory=/mnt/ai-ssd/hermes
Environment="PATH=/mnt/ai-ssd/hermes/hermes-agent/venv/bin:/mnt/ai-ssd/hermes/hermes-agent/node_modules/.bin:/mnt/ai-ssd/hermes/node/bin:/mnt/ai-ssd/hermes/node:/home/khadas/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="VIRTUAL_ENV=/home/khadas/.hermes/hermes-agent/venv"
Environment="HERMES_HOME=/mnt/ai-ssd/hermes"
Environment="HERMES_SUPERVISED_CHILD=1"
Restart=always
RestartSec=5
RestartForceExitStatus=75
SuccessExitStatus=75
RestartPreventExitStatus=78
KillMode=mixed
KillSignal=SIGTERM
ExecReload=/bin/kill -USR1 $MAINPID
ExecStopPost=-/home/khadas/.hermes/hermes-agent/venv/bin/python -m gateway.cgroup_cleanup
TimeoutStopSec=70
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
```

**Drop-in файлы** (`hermes-gateway.service.d/`):

**memory.conf** — ограничение памяти:

```ini
[Service]
MemoryAccounting=yes
MemoryHigh=768M
MemoryMax=1600M
MemorySwapMax=512M
```

**override.conf** — загрузка секретов:

```ini
[Service]
EnvironmentFile=-/home/khadas/ai-system/.env
```

**security.conf** — контроль доступа Telegram:

```ini
[Service]
Environment="TELEGRAM_ALLOWED_USERS=<TELEGRAM_CHAT_ID>"
Environment="GATEWAY_ALLOW_ALL_USERS=false"
```

**workdir.conf** — рабочая директория:

```ini
[Service]
WorkingDirectory=/home/khadas/work
```

**Управление**:

```bash
# Старт/стоп/рестарт
systemctl --user start hermes-gateway.service
systemctl --user stop hermes-gateway.service
systemctl --user restart hermes-gateway.service

# Статус
systemctl --user status hermes-gateway.service --no-pager

# Логи
journalctl --user -u hermes-gateway.service -f
journalctl --user -u hermes-gateway.service --since "1 hour ago"

# Автозапуск
systemctl --user enable hermes-gateway.service
systemctl --user disable hermes-gateway.service
```

**Метрики работы**:
- **Память**: ~305MB (норма: 250-400MB)
- **CPU**: ~1h за 30h работы
- **Tasks**: 32 процесса (включая MCP server)

### 3.2. MCP сервер Context7

**Процесс**: `/home/khadas/.hermes/node/bin/node`  
**Скрипт**: `/home/khadas/.hermes/mcp-servers/node_modules/@upstash/context7-mcp/dist/index.js`  
**PID**: ~388218  
**Версия**: v4.1.0  
**Протокол**: stdio  
**Лог**: `~/.hermes/logs/mcp-stderr.log`

**Конфиг в `~/.hermes/config.yaml`**:

```yaml
mcp_servers:
  context7:
    args:
    - /home/khadas/.hermes/mcp-servers/node_modules/@upstash/context7-mcp/dist/index.js
    command: /home/khadas/.hermes/node/bin/node
    connect_timeout: 60
```

### 3.3. Hermes конфигурация

**Файл**: `~/.hermes/config.yaml`

```yaml
model:
  base_url: http://127.0.0.1:3001/v1
  provider: freellmapi
  context_length: 65536

web:
  search_backend: searxng

mcp_servers:
  context7:
    command: /home/khadas/.hermes/node/bin/node
    args: [/home/khadas/.hermes/mcp-servers/node_modules/@upstash/context7-mcp/dist/index.js]

streaming:
  enabled: true

agent:
  disabled_toolsets: [video, video_gen, tts, stt, computer_use, browser-use]

delegation:
  max_concurrent_children: 1
  orchestrator_enabled: false

plugins:
  enabled: []

providers:
  freellmapi:
    api: http://127.0.0.1:3001/v1
    key_env: OPENAI_API_KEY

skills:
  guard_agent_created: true
  write_approval: true
```

---

## 🔧 4. Скрипты и runners

### 4.1. research-runner.py (v3.0)

**Путь**: `~/ai-system/scripts/research-runner.py` (симлинк `~/bin/research-runner.py`)  
**Размер**: 997 строк  
**Назначение**: Deep Research Agent с пайплайном `plan → search → fetch → extract → verify → validate → report`

**Использование**:

```bash
# Базовый запуск
python3 ~/bin/research-runner.py --topic "тема" --depth 3

# Варианты глубины
python3 ~/bin/research-runner.py --topic "тема" --depth 1   # quick
python3 ~/bin/research-runner.py --topic "тема" --depth 5   # deep

# Возобновление прерванного
python3 ~/bin/research-runner.py --resume research_id

# Dry run (без реального запуска)
python3 ~/bin/research-runner.py --topic "тема" --dry-run
```

**Параметры**:
- `--topic TOPIC` — тема исследования
- `--depth N` — глубина (1=quick, 3=default, 5=deep)
- `--resume ID` — возобновить по ID
- `--dry-run` — только планирование

**Под-компоненты**:
- `AsyncSearcher` → SearXNG (127.0.0.1:8888)
- `AsyncFetcher` → HTML кэш в `~/research/cache/` (TTL 30 дней)
- `LLMGateway` → FreeLLMAPI (127.0.0.1:3001)
- `EvidenceVerifier` → проверка цитат
- `Evidence Cache` → `~/research/cache/evidences/` (TTL 7 дней)

**Выходные данные**:
- Отчёт: `~/research/reports/YYYY-MM-DD_HHMM_тема.md`
- Sidecar: `~/research/reports/YYYY-MM-DD_HHMM_тема.evidence.json`
- Логи: `/tmp/research-*.log`

### 4.2. aider-runner.py (v2.2)

**Путь**: `~/ai-system/scripts/aider-runner.py` (симлинк `~/bin/aider-runner.py`)  
**Размер**: 331 строка  
**Назначение**: Безопасный wrapper для запуска Aider из Hermes

**Использование**:

```bash
# Базовый запуск
~/bin/aider-runner.py "<PROJECT_PATH>" "<TASK_DESCRIPTION>"

# С флагами
~/bin/aider-runner.py "/home/khadas/projects/my-app" "Add function" --allow-dirty
~/bin/aider-runner.py "/home/khadas/projects/my-app" "Refactor" --push
~/bin/aider-runner.py "/path" "task" --timeout 3600
```

**Selfcheck перед автопушем** (5 smoke-тестов):
- `scripts/selfcheck.sh` запускается перед каждым автопушем
- Проверяет: синтаксис Python/Bash, FORBIDDEN_ROOTS, NVIDIA key в env, save_ckpt без двойного I/O, self.drop_total
- Если selfcheck упал — коммит отменяется, сломанный код не попадёт в main

**Критическая безопасность — ALLOWED_ROOTS и FORBIDDEN_ROOTS**:

```python
ALLOWED_ROOTS = [
    HOME / "projects",      # Пользовательские проекты
    HOME / "research",      # Результаты исследований
    HOME / "work",          # Рабочая папка
    HOME / "code",          # Код
    HOME / "dev",           # Разработка
    HOME / "Desktop",       # Desktop
    HOME / "Documents",     # Документы
    HOME / "Downloads",     # Загрузки
    HOME / "tmp",           # Временные файлы
]

FORBIDDEN_ROOTS = [
    HOME / "ai-system",              # Сам репозиторий системы
    HOME / ".hermes",                 # Ядро Hermes Agent
    Path("/mnt/ai-ssd/hermes"),       # Физический путь Hermes
]
```

**Порядок проверок**:
1. Проверка FORBIDDEN_ROOTS (если внутри → BLOCK)
2. Проверка ALLOWED_ROOTS (если вне → BLOCK)
3. Git root validation
4. Dirty check
5. Запуск Aider

**Возвращаемые статусы** (JSON):

```json
{
  "ok": true,
  "task_id": "uuid",
  "status": "COMPLETED",
  "timestamp": "2026-09-20T06:48:42+00:00",
  "project": "/home/khadas/projects/my-app",
  "commit_hash": "abc1234",
  "diff_stat": "2 files changed, 10 insertions(+)",
  "elapsed_seconds": 45
}
```

**Статусы ошибок**:
- `COMPLETED` — успешно
- `DIRTY_REPOSITORY` — есть незакоммиченные изменения
- `AIDER_BUSY` — другой Aider уже работает
- `TIMEOUT` — превышен таймаут (1800с)
- `INVALID_PROJECT` — путь вне ALLOWED_ROOTS или не существует
- `NOT_GIT_REPOSITORY` — не git репозиторий
- `DETACHED_HEAD` — нельзя пушить
- `FORBIDDEN` — путь в FORBIDDEN_ROOTS
- `NVIDIA_API_KEY_MISSING` — отсутствует ключ

### 4.3. task_ledger.py

**Путь**: `~/ai-system/scripts/task_ledger.py`  
**Назначение**: SQLite storage для истории задач Aider

**База данных**: `~/ai-system/data/tasks.db`

**Схема**:

```sql
CREATE TABLE tasks (
    task_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    project TEXT NOT NULL,
    task TEXT NOT NULL,
    status TEXT NOT NULL,
    initial_head TEXT,
    final_head TEXT,
    commit_hash TEXT,
    commit_message TEXT,
    changed_files TEXT,
    exit_code INTEGER,
    elapsed_seconds REAL,
    error_message TEXT,
    dirty_before INTEGER,
    pre_existing_changes TEXT
);

CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_project ON tasks(project);
CREATE INDEX idx_tasks_timestamp ON tasks(timestamp);
```

**API**:

```python
import task_ledger

# Логирование задачи
task_ledger.log_task(
    task_id="uuid",
    project="/home/khadas/projects/app",
    task="Add function calculate_tax",
    status="COMPLETED",
    commit_hash="abc1234",
    elapsed_seconds=45.2,
    exit_code=0,
    changed_files=["main.py", "utils.py"]
)
```

### 4.4. ledger-viewer.py

**Путь**: `~/ai-system/scripts/ledger-viewer.py`  
**Назначение**: CLI для просмотра истории задач Aider

**Использование**:

```bash
# Статистика
~/bin/ledger-viewer.py stats

# Последние N задач
~/bin/ledger-viewer.py recent 10

# Детали конкретной задачи
~/bin/ledger-viewer.py show <task_id>
```

**Пример вывода stats**:

```
📊 СТАТИСТИКА TASK LEDGER
============================================================
Всего задач: 7

📈 По статусам:
  COMPLETED                3
  INVALID_PROJECT          4

📁 По проектам:
  /home/khadas/projects/aider-test   3
  unknown                              4
```

### 4.5. git-auto-push.sh

**Путь**: `~/ai-system/scripts/git-auto-push.sh`  
**Назначение**: Автопуш изменений в GitHub каждые 6 часов с проверкой на секреты

**Алгоритм**:
1. `cd ~/ai-system`
2. `git add scripts/ configs/ tests/ docs/ freellmapi/docker-compose.yml freellmapi/models_blacklist.txt searxng/docker-compose.yml .gitignore README.md` (белый список)
3. Проверка наличия изменений
4. Regex проверка на секреты в staged файлах
5. Если секреты найдены → BLOCKED + Telegram уведомление
6. `git commit -m "auto: $(date)"`
7. `git push origin main`
8. При ошибке: `git pull --rebase origin main` + retry push

**Regex паттерн для секретов**:

```bash
SECRETS_PATTERN='(api[_-]?key|secret|password|token|private[_-]?key)\s*[:=]\s*["\x27][A-Za-z0-9+/=_\-]{16,}'
```

**Лог**: `~/ai-system/logs/git-auto-push.log`  
**Lock**: `/tmp/git-auto-push.lock` (защита от параллельного запуска)

**Cron**: `0 */6 * * *` (0:00, 6:00, 12:00, 18:00 UTC)

**Ручной запуск**:

```bash
~/bin/git-auto-push.sh
tail -30 ~/ai-system/logs/git-auto-push.log
```

### 4.6. git-credential-github.sh

**Путь**: `~/ai-system/scripts/git-credential-github.sh`  
**Назначение**: Git credential helper для GitHub fine-grained token

**Конфиг в git**:

```bash
git config --global credential.helper '!/home/khadas/bin/git-credential-github.sh'
```

**Алгоритм**:
1. Читает `~/ai-system/.env`
2. Извлекает `GITHUB_TOKEN` и `GITHUB_USER`
3. При запросе `get` возвращает credentials через stdout:

```
protocol=https
host=github.com
username=$GITHUB_USER
password=$GITHUB_TOKEN
```

**Тест**:

```bash
echo "protocol=https
host=github.com" | ~/bin/git-credential-github.sh get
```

### 4.7. research-telegram.sh

**Путь**: `~/ai-system/scripts/research-telegram.sh`  
**Назначение**: Wrapper для запуска research-runner с выводом в Telegram

**Использование**:

```bash
~/bin/research-telegram.sh "тема" 3    # тема + depth
~/bin/research-telegram.sh "тема" 1    # quick
```

**Безопасность**:
- Проверка темы на shell injection: `grep -qE '[`$()]'`
- Таймаут: 60 минут
- Лог: `/tmp/research.log`

**Парсинг sidecar**:

```bash
SIDECAR_PATH=$(grep -oP '(?<=sidecar: ).*' /tmp/research.log | tail -1)
```

### 4.8. helper-скрипты

**sync-tasks-to-supabase.py**: синхронизация задач из task_ledger в Supabase  
**backup-projects.sh**: бэкап `~/projects/`  
**check-memory-peak.sh**: проверка пика памяти Hermes  
**check_r2_budget.sh**: проверка бюджета Cloudflare R2  
**check-freellm-quotas.sh**: проверка квот FreeLLMAPI

---

## 🎯 5. Скиллы Hermes

### 5.1. Архитектура скиллов

**Расположение**: `~/.hermes/skills/` (= `/mnt/ai-ssd/hermes/skills/`)

**Структура категории**:

```
skills/
├── research/
│   ├── DESCRIPTION.md           # Описание категории
│   ├── deep-research/SKILL.md   # Конкретный скилл
│   ├── arxiv/SKILL.md
│   └── ...
└── ...
```

**Формат SKILL.md**:

```yaml
---
name: deep-research
description: Глубокое исследование рынков через команду /research
tags: [research, analysis, market, telegram]
triggers:
  - /research
  - изучи рынок
  - исследуй
  - проведи анализ
---

# Deep Research Agent

## Активация
Skill активируется при:
1. Команде `/research тема` в Telegram
2. Запросах "изучи рынок", "проведи исследование"

## Workflow
...
```

### 5.2. Категории скиллов (13 категорий, 60 скиллов)

| Категория | Количество | Примеры скиллов |
|-----------|-----------|-----------------|
| `aider-delegate` | 1 | Делегирование в Aider |
| `research` | 5 | deep-research, arxiv, competitor-news-monitor, grounded-citations, llm-wiki |
| `software-development` | 12 | github, codebase-inspection, requesting-code-review, simplify-code, systematic-debugging, tdd, python-debugpy, node-inspect-debugger |
| `creative` | 10 | architecture-diagram, ascii-video, manim-video, p5js, songwriting-and-ai-music |
| `productivity` | 14 | airtable, notion, google-workspace, obsidian, xlsx, docx, pdf, powerpoint |
| `autonomous-ai-agents` | 5 | claude-code, codex, computer-use, hermes-agent, opencode |
| `apple` | 4 | apple-notes, apple-reminders, findmy, imessage (НЕ работают на Linux!) |
| `media` | 3 | gif-search, songsee, youtube-content |
| `email` | 2 | email-inbox-triage, himalaya |
| `note-taking` | 1 | obsidian |
| `social-media` | 1 | xurl |
| `devops` | 1 | sdlc-review |
| `web` | 1 | blocked-page-recovery |

### 5.3. Skill Bundles (точки входа)

**Расположение**: `~/.hermes/skill-bundles/`

**Назначение**: Обёртки для Telegram slash-команд. Регистрируют команду и делегируют в skill.

**Пример `~/.hermes/skill-bundles/research.yaml`**:

```yaml
name: research
description: "Запустить глубокое исследование через команду /research"
skills:
  - deep-research
prompt: |
  Пользователь вызвал команду /research с аргументами: {args}
  
  Следуй инструкциям из skill "deep-research" для обработки этого запроса.
  Передай все аргументы как есть — skill сам распарсит флаги --quick и --depth.
  
  ВАЖНО: НЕ вызывай runner-скрипты напрямую из этого bundle.
  Вместо этого, следуй workflow из skill deep-research (парсинг темы, 
  определение depth, запуск runner'а, отправка результата).
```

**Разделение ответственности**:
- **Bundle** (slash-команда): распознаёт `/research`, загружает skill, передаёт `{args}`
- **Skill** (SKILL.md): парсит флаги (`--quick`, `--depth N`), запускает runner, форматирует результат

### 5.4. Подробно: skill deep-research

**Файл**: `~/.hermes/skills/research/deep-research/SKILL.md`

**Триггеры**:
- `/research тема`
- "изучи рынок"
- "исследуй"
- "проведи анализ"
- "подготовь отчёт"
- "market research"
- "industry analysis"

**Workflow**:

**Шаг 1: Парсинг команды**

```
/research тема                → тема, depth=3 (default)
/research тема --depth 5      → тема, depth=5
/research тема --quick        → тема, depth=1
```

**Шаг 2: Валидация темы**  
Если тема слишком широкая (< 3 слов или абстрактная):

```
Какие аспекты интересуют?
Какой период?
Какие регионы/игроки?
```

**Шаг 3: Запуск исследования**

```bash
~/bin/research-telegram.sh "ТЕМА" DEPTH
```

**Шаг 4: Отправка результата в Telegram**

```
🎉 ИССЛЕДОВАНИЕ ГОТОВО
━━━━━━━━━━━━━━━━━━━━
📋 Тема: ...
📊 X слов | Y источников | Z KB
━━━ Ключевые выводы ━━━
• Вывод 1
• Вывод 2
• ...
📁 Файл: ~/research/reports/...

Хочешь:
🔄 Углубить (depth=5)?
📊 Сравнить с другим рынком?
🔍 Деталь по конкретному разделу?
```

**Troubleshooting**:
- SearXNG не отвечает: `cd ~/ai-system/searxng && docker compose up -d`
- Отчёт с 0 источниками: перезапустить с `depth=5`
- Не уложился в таймаут: использовать `terminal(background=true, notify=true)`

### 5.5. Подробно: skill aider-delegate

**Файл**: `~/.hermes/skills/aider-delegate/SKILL.md`

**Триггеры**:
- "используй Aider в ~/projects/..."
- "запусти Aider"
- "сделай через Aider"
- "Aider, добавь функцию"
- "попроси Aider исправить"

**Ограничения (FORBIDDEN_ROOTS)**:
- ❌ НЕЛЬЗЯ: `~/ai-system` (ядро системы)
- ❌ НЕЛЬЗЯ: `~/.hermes` (Hermes)
- ❌ НЕЛЬЗЯ: `/mnt/ai-ssd/hermes` (физический путь Hermes)

**Разрешённые директории**:
- ✅ `~/projects/*` (пользовательские проекты)
- ✅ `~/research/*` (результаты исследований)
- ✅ `~/work/*`, `~/code/*`, `~/dev/*` (рабочие папки)
- ✅ `~/Desktop`, `~/Documents`, `~/Downloads`

**Выполнение**:

```bash
python3 /home/khadas/bin/aider-runner.py "<PROJECT_PATH>" "<TASK_DESCRIPTION>"
```

**Обработка DIRTY_REPOSITORY**:
1. Сообщить пользователю о незакоммиченных изменениях
2. Спросить разрешение на `--allow-dirty`
3. НИКОГДА не добавлять `--allow-dirty` автоматически

**Обработка ошибок**:
- `AIDER_BUSY` — "Другая задача Aider выполняется. Подождите."
- `TIMEOUT` — "Превышен таймаут. task_id: X, лог: /path/to/log"
- `AIDER_FAILED` — "Ошибка Aider: exit_code=N"
- `FORBIDDEN` — "Путь в запрещённой директории"

---

## 🐳 6. Docker контейнеры

### 6.1. FreeLLMAPI (LLM Router)

**Контейнер**: `freellmapi`  
**Образ**: `ghcr.io/tashfeenahmed/freellmapi:v0.11.1`  
**Порт**: `127.0.0.1:3001`  
**Статус**: healthy  
**Конфиг**: `~/ai-system/freellmapi/docker-compose.yml`

**Назначение**: Маршрутизатор запросов к 34+ LLM провайдерам

**Проверка**:

```bash
docker ps | grep freellmapi
curl http://127.0.0.1:3001/v1/models
docker logs freellmapi --tail 50
```

**Управление**:

```bash
cd ~/ai-system/freellmapi
docker compose up -d
docker compose down
docker compose restart
docker compose logs -f
```

### 6.2. SearXNG (Meta-search)

**Контейнер**: `searxng`  
**Порт**: `127.0.0.1:8888`  
**Статус**: healthy  
**Конфиг**: `~/ai-system/searxng/docker-compose.yml`

**Назначение**: Приватный мета-поисковик для исследований

**Проверка**:

```bash
docker ps | grep searxng
curl "http://127.0.0.1:8888/search?q=test&format=json"
docker logs searxng --tail 50
```

**Управление**:

```bash
cd ~/ai-system/searxng
docker compose up -d
docker compose down
docker compose restart
docker compose logs -f
```

---

## 🔐 7. Безопасность

### 7.1. Четыре уровня защиты

#### Уровень 1: .gitignore

**Файл**: `~/ai-system/.gitignore`

**Защищает от коммита**:

```gitignore
# Секреты
.env
.env.save
*.key
*.pem
*.secret

# Runtime
runtime/
*.log
logs/aider/

# Кэш
research/cache/
research/working/
__pycache__/
*.pyc

# Тестовые файлы
main.py
test-*.py
*.tmp

# Бэкапы
*.backup.*
docker-compose.yml.bak.*
docker-compose.yml.broken.*

# Все .env файлы кроме example
.env.*
!.env.example
```

#### Уровень 2: Regex проверка в git-auto-push.sh

**Паттерн**:

```bash
SECRETS_PATTERN='(api[_-]?key|secret|password|token|private[_-]?key)\s*[:=]\s*["\x27][A-Za-z0-9+/=_\-]{16,}'
```

**При обнаружении**:
- Файл исключается из коммита (`git reset HEAD`)
- Уведомление в Telegram
- Логирование в `git-auto-push.log`

#### Уровень 3: FORBIDDEN_ROOTS в aider-runner.py

**Запрещённые для Aider директории**:

```python
FORBIDDEN_ROOTS = [
    HOME / "ai-system",              # Сам репозиторий системы
    HOME / ".hermes",                 # Ядро Hermes Agent
    Path("/mnt/ai-ssd/hermes"),       # Физический путь Hermes
]
```

#### Уровень 4: Credential helper

**Файл**: `~/bin/git-credential-github.sh`  
**Настройка**: `git config --global credential.helper '!/home/khadas/bin/git-credential-github.sh'`

**Принцип**: Токены НЕ хранятся в `~/.git-credentials` в plaintext, а читаются из `.env` при каждом запросе.

### 7.2. Секреты в .env

**Файл**: `~/ai-system/.env` (НЕ в git!)

**Переменные**:

```bash
# Telegram
TELEGRAM_BOT_TOKEN=***
TELEGRAM_CHAT_ID=<TELEGRAM_CHAT_ID>
TELEGRAM_ALLOWED_USERS=<TELEGRAM_CHAT_ID>
TELEGRAM_HOME_CHANNEL=***
TELEGRAM_HOME_CHANNEL_THREAD_ID=***

# API ключи
OPENAI_API_KEY=***
NVIDIA_API_KEY=***
AWS_ACCESS_KEY_ID=***
AWS_SECRET_ACCESS_KEY=***

# GitHub
GITHUB_TOKEN=***
GITHUB_USER=<GITHUB_USER>
GITHUB_REPO=hermes-vim4

# Supabase
SUPABASE_URL=***
SUPABASE_SERVICE_ROLE_KEY=***
SUPABASE_ANON_KEY=***

# SearXNG
SEARXNG_URL=http://127.0.0.1:8888
SEARXNG_BASE_URL=http://127.0.0.1:8888

# Прочее
FREELLMAPI_PORT=3001
HERMES_TIMEZONE=Europe/Minsk
ENCRYPTION_KEY=***
```

### 7.3. Политика Aider

**Разрешено**:
- `~/projects/*`
- `~/research/*`
- `~/work/*`, `~/code/*`, `~/dev/*`
- `~/Desktop`, `~/Documents`, `~/Downloads`, `~/tmp`

**Запрещено**:
- `~/ai-system/*` (репозиторий системы)
- `~/.hermes/*` (ядро Hermes)
- `/mnt/ai-ssd/hermes/*` (физический путь)
- `~/.ssh`, `~/.bashrc` (системные)

---

## ⏰ 8. Автоматизация (Cron)

### 8.1. Системный crontab

**Файл**: `crontab -l`

```cron
0 3 * * * /home/khadas/ai-system/scripts/check_r2_budget.sh >> /home/khadas/ai-system/logs/r2_cron.log 2>&1
0 */6 * * * /home/khadas/bin/git-auto-push.sh
```

**Задачи**:
- **03:00 UTC** — проверка бюджета R2
- **Каждые 6 часов** — автопуш изменений в GitHub

### 8.2. Hermes cron jobs

**Файл**: `~/.hermes/cron/jobs.json`

**⚠️ Важно (новая security policy Hermes v0.21.1+)**:
- Cron скрипты **должны лежать** в `/mnt/ai-ssd/hermes/scripts/`
- **Symlink'и блокируются** (Hermes разрешает symlink и проверяет реальный путь)
- **Решение**: копировать скрипты, не линковать

**Синхронизация скриптов**:
```bash
# Скрипт синхронизирует cron-скрипты из ~/ai-system/scripts/ в /mnt/ai-ssd/hermes/scripts/
/mnt/ai-ssd/hermes/scripts/sync-cron-scripts.sh
```

**Запускать после**:
- Каждого коммита в `~/ai-system/scripts/`
- Обновления cron скриптов
- Можно добавить в `git-auto-push.sh` для автоматизации

**Управление через CLI**:

```bash
# Список всех jobs
hermes cron list

# Создать новый
hermes cron create

# Редактировать
hermes cron edit <job_name>

# Пауза/возобновление
hermes cron pause <job_name>
hermes cron resume <job_name>

# Ручной запуск
hermes cron run <job_name>

# Удалить
hermes cron remove <job_name>

# Статус планировщика
hermes cron status

# История запусков
hermes cron runs

# Инциденты (повторяющиеся ошибки)
hermes cron incidents
```

**Активные jobs**:

#### 8.2.1. tasks-sync-supabase

```json
{
  "id": "b6f30ecaf0b5",
  "name": "tasks-sync-supabase",
  "script": "sync-tasks-cron.sh",
  "schedule": "30 3 * * *",
  "status": "ok",
  "deliver": "telegram"
}
```

**Назначение**: Синхронизация задач из task_ledger в Supabase

#### 8.2.2. freellm-quota-check

```json
{
  "id": "e20e31e40270",
  "name": "freellm-quota-check",
  "script": "check-freellm-quotas.sh",
  "schedule": "0 9 * * *",
  "status": "ok",
  "deliver": "telegram"
}
```

**Назначение**: Проверка квот FreeLLMAPI провайдеров

### 8.3. История выполнения

**Расположение**: `~/.hermes/cron/output/<job_id>/<timestamp>.md`

**Пример**:

```
~/.hermes/cron/output/e20e31e40270/2026-09-20_09-00-21.md
```

---

## 🔄 9. Git и автопуш

### 9.0. Настройка git для ARM (VIM4)

**Проблема**: `git fetch` может падать на ARM с ошибкой `curl 92 HTTP/2 stream 5 was not closed cleanly`

**Решение** (глобально):
```bash
git config --global http.version HTTP/1.1
git config --global http.postBuffer 524288000
git config --global http.lowSpeedLimit 0
git config --global http.lowSpeedTime 999999
```

**Для Hermes Agent** (локально в install directory):
```bash
cd /mnt/ai-ssd/hermes/hermes-agent
git config --local http.version HTTP/1.1
git config --local http.postBuffer 524288000
```

**Обновление Hermes Agent** (shallow clone — экономит 500+ MB на SSD):
```bash
cd /mnt/ai-ssd/hermes/hermes-agent
git fetch --depth 1 --tags origin
git checkout -f v2026.9.14  # или последняя версия
# Переустановка зависимостей:
source /mnt/ai-ssd/hermes/hermes-agent/venv/bin/activate
pip install -e .
```

### 9.1. Репозиторий

**URL**: `https://github.com/<GITHUB_USER>/<REPO_NAME>.git`  
**Локальный путь**: `~/ai-system`  
**Ветка**: `main`  
**Пользователь**: `<GITHUB_USER> <<EMAIL>>`

### 9.2. Структура репозитория

```
~/ai-system/
├── .git/
├── .env                        ← НЕ в git (секреты)
├── .gitignore                  ← Защита секретов
├── README.md                   ← Эта документация
├── scripts/                    ← Все runner'ы (13 файлов)
│   ├── research-runner.py
│   ├── research-telegram.sh
│   ├── aider-runner.py
│   ├── task_ledger.py
│   ├── ledger-viewer.py
│   ├── git-auto-push.sh
│   ├── git-credential-github.sh
│   ├── sync-tasks-to-supabase.py
│   ├── backup-projects.sh
│   ├── check-memory-peak.sh
│   ├── check_r2_budget.sh
│   └── check-freellm-quotas.sh
├── configs/
│   └── hermes/.env.example
├── freellmapi/docker-compose.yml
├── searxng/docker-compose.yml
├── data/                       ← Runtime данные (НЕ в git)
├── logs/                       ← Логи (НЕ в git)
├── runtime/                    ← Runtime (НЕ в git)
└── research/                   ← Отчёты (НЕ в git)
```

### 9.3. Алгоритм автопуша

**Скрипт**: `~/bin/git-auto-push.sh`  
**Расписание**: `0 */6 * * *`

```bash
1. cd ~/ai-system
2. git add scripts/ configs/ tests/ docs/ freellmapi/docker-compose.yml freellmapi/models_blacklist.txt searxng/docker-compose.yml .gitignore README.md
3. Проверка изменений: git status --porcelain
4. Regex проверка на секреты в staged файлах
5. Если секреты:
   - git reset HEAD <file>
   - Telegram уведомление
   - exit 1
6. git commit -m "auto: $(date)"
7. git push origin main
8. При ошибке push:
   - git pull --rebase origin main
   - git push origin main (retry)
```

**Лог**: `~/ai-system/logs/git-auto-push.log`

### 9.4. Что попадает в GitHub

| Тип | Попадает? | Причина |
|-----|-----------|---------|
| `scripts/*.py` | ✅ | Исходный код |
| `scripts/*.sh` | ✅ | Wrapper'ы |
| `.gitignore` | ✅ | Конфиг безопасности |
| `README.md` | ✅ | Документация |
| `configs/hermes/.env.example` | ✅ | Пример (без секретов) |
| `freellmapi/docker-compose.yml` | ✅ | Конфиг Docker |
| `.env` | ❌ | Секреты |
| `data/*.db` | ❌ | Runtime |
| `logs/` | ❌ | Логи |
| `runtime/` | ❌ | Runtime |
| `research/reports/` | ❌ | Тяжёлые отчёты |

---

## 💡 10. Примеры использования

### 10.1. Deep Research через Telegram

**Команды**:

```
/deep-research рынок электромобилей в Китае 2025
/research квантовые компьютеры --quick
/research AI в медицине --depth 5
```

**Ожидаемое поведение**:
1. Hermes распознаёт команду `/research`
2. Активирует skill `deep-research`
3. Skill парсит флаги и определяет depth
4. Запускает `~/bin/research-telegram.sh "тема" <depth>`
5. Через 3-30 минут присылает Executive Summary в Telegram
6. Отчёт сохраняется в `~/research/reports/YYYY-MM-DD_HHMM_тема.md`

### 10.2. Aider через Telegram

**Команды**:

```
Используй Aider в ~/projects/my-app чтобы добавить функцию calculate_tax
Aider, исправь баг в ~/projects/webapp
Рефакторинг ~/code/backend с помощью Aider
```

**Ожидаемое поведение**:
1. Hermes распознаёт запрос на Aider
2. Проверяет что путь в ALLOWED_ROOTS (не в FORBIDDEN)
3. Запускает `~/bin/aider-runner.py "<path>" "<task>"`
4. Aider вносит изменения и делает commit
5. Hermes присылает результат в Telegram
6. Задача логируется в `~/ai-system/data/tasks.db`

### 10.3. Статус и мониторинг

**Команды**:

```
Статус исследования
Покажи последние задачи Aider
Проверь здоровье системы
```

### 10.4. Локальный запуск (CLI)

```bash
# Запустить исследование напрямую
~/bin/research-runner.py --topic "тема" --depth 3

# Посмотреть историю Aider
~/bin/ledger-viewer.py stats
~/bin/ledger-viewer.py recent 10

# Ручной автопуш
~/bin/git-auto-push.sh

# Логи автопуша
tail -f ~/ai-system/logs/git-auto-push.log
```

---

## 🔌 11. API и интерфейсы

### 11.1. FreeLLMAPI (LLM Router)

**Endpoint**: `http://127.0.0.1:3001/v1`

**Совместимость**: OpenAI API format

**Пример запроса**:

```bash
curl http://127.0.0.1:3001/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "auto",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

**Список моделей**:

```bash
curl http://127.0.0.1:3001/v1/models
```

### 11.2. SearXNG (Meta-search)

**Endpoint**: `http://127.0.0.1:8888`

**Поиск**:

```bash
curl "http://127.0.0.1:8888/search?q=test&format=json"
```

**Параметры**:
- `q` — запрос
- `format` — json или html
- `categories` — general, news, images, etc.
- `language` — ru-RU, en-US, etc.
- `time_range` — day, week, month, year

### 11.3. Telegram Bot API

**Chat ID**: `<TELEGRAM_CHAT_ID>`  
**Allowed users**: `<TELEGRAM_CHAT_ID>`

**Slash-команды**:
- `/research <тема>` — запустить исследование
- `/commands` — список доступных команд
- `/help` — помощь

### 11.4. Hermes Gateway Internal

**Socket**: `~/.hermes/gateway.sock`  
**PID file**: `~/.hermes/gateway.pid`  
**State**: `~/.hermes/gateway_state.json`

---

## 🛠️ 12. Troubleshooting

### 12.1. Hermes Gateway не запускается

**Диагностика**:

```bash
systemctl --user status hermes-gateway.service
journalctl --user -u hermes-gateway.service -n 50
ls -la ~/ai-system/.env
docker ps
```

**Решение**:

```bash
systemctl --user restart hermes-gateway.service
cd ~/ai-system/freellmapi && docker compose up -d
cd ~/ai-system/searxng && docker compose up -d
```

### 12.2. Aider не делает коммиты

**Диагностика**:

```bash
cat ~/.aider.conf.yml | grep -E "auto-commits|dirty-commits"
cd ~/projects/my-app && git status
tail -30 ~/ai-system/logs/aider/aider-*.log
```

**Решение**:

```bash
# Включить auto-commits
sed -i 's/^auto-commits: false/auto-commits: true/' ~/.aider.conf.yml
sed -i 's/^dirty-commits: false/dirty-commits: true/' ~/.aider.conf.yml
```

### 12.3. Исследование не завершается

**Диагностика**:

```bash
tail -50 /tmp/research-*.log
curl "http://127.0.0.1:8888/search?q=test&format=json"
curl http://127.0.0.1:3001/v1/models
docker ps | grep -E "searxng|freellmapi"
```

**Решение**:

```bash
# Использовать --quick
/research тема --quick

# Перезапустить Docker
cd ~/ai-system/searxng && docker compose restart
cd ~/ai-system/freellmapi && docker compose restart
```

### 12.4. Автопуш не работает

**Диагностика**:

```bash
crontab -l | grep git-auto-push
tail -30 ~/ai-system/logs/git-auto-push.log
ls -la ~/bin/git-auto-push.sh
cd ~/ai-system && git remote -v
```

**Решение**:

```bash
# Ручной запуск
~/bin/git-auto-push.sh

# Добавить cron заново
(crontab -l 2>/dev/null | grep -v 'git-auto-push.sh'; \
 echo "0 */6 * * * /home/khadas/bin/git-auto-push.sh") | crontab -
```

### 12.5. SearXNG не отвечает

**Диагностика**:

```bash
docker ps | grep searxng
docker logs searxng --tail 30
curl "http://127.0.0.1:8888/search?q=test&format=json"
```

**Решение**:

```bash
cd ~/ai-system/searxng
docker compose down
docker compose up -d
docker logs searxng -f
```

### 12.6. Hermes: "history is temporarily unavailable" / state.db недоступен

**Симптомы**:
- Hermes пишет: `⚠️ This session's history is temporarily unavailable`
- Сообщения не обрабатываются
- Просит "inspect state.db"

**Причина**: обычно после обновления Hermes Agent старый gateway процесс держит lock на state.db

**Решение**:
```bash
# 1. Правильный перезапуск gateway
hermes gateway restart

# 2. Подождать 5 секунд
sleep 5

# 3. Проверить что новый процесс запущен
ps aux | grep hermes.*gateway | grep -v grep

# 4. Проверить статус
hermes status
```

**Дополнительно** (если не помогает):
```bash
# WAL checkpoint вручную
sqlite3 /mnt/ai-ssd/hermes/state.db "PRAGMA wal_checkpoint(TRUNCATE);"

# Integrity check
sqlite3 /mnt/ai-ssd/hermes/state.db "PRAGMA integrity_check;"

# Если всё ok — перезапустить gateway
hermes gateway restart
```

**Не делайте**:
- ❌ Не удаляйте state.db (потеряете все sessions)
- ❌ Не убивайте gateway через `kill -9` (может повредить БД)
- ✅ Используйте `hermes gateway restart` — он делает graceful drain

### 12.7. FreeLLMAPI не отвечает

**Диагностика**:

```bash
docker ps | grep freellmapi
docker logs freellmapi --tail 30
curl http://127.0.0.1:3001/v1/models
```

**Решение**:

```bash
cd ~/ai-system/freellmapi
docker compose down
docker compose up -d
docker logs freellmapi -f
```

### 12.7. Task ledger не логирует

**Диагностика**:

```bash
ls -la ~/ai-system/data/tasks.db
~/bin/ledger-viewer.py stats
python3 -c "import sys; sys.path.insert(0, '/home/khadas/bin'); import task_ledger; print(task_ledger.__file__)"
```

**Решение**:

```bash
# Проверить права
chmod 644 ~/ai-system/data/tasks.db

# Проверить что БД не corrupted
sqlite3 ~/ai-system/data/tasks.db "PRAGMA integrity_check;"
```

### 12.8. Команда `/research` не работает

**Диагностика**:

```bash
ls -la ~/.hermes/skill-bundles/
cat ~/.hermes/skill-bundles/research.yaml
ls -la ~/.hermes/skills/research/deep-research/
tail -30 ~/.hermes/logs/agent.log | grep -iE 'research|skill|bundle'
```

**Решение**:

```bash
# Перезапустить gateway
systemctl --user restart hermes-gateway.service

# Проверить что bundle существует
cat ~/.hermes/skill-bundles/research.yaml
```

---

## 🔄 13. Восстановление системы

### 13.1. Полное восстановление из GitHub

```bash
# 1. Клонировать репозиторий
git clone https://github.com/<GITHUB_USER>/<REPO_NAME>.git ~/ai-system
cd ~/ai-system

# 2. Создать .env из примера
cp configs/hermes/.env.example .env
nano .env  # заполнить секреты

# 3. Создать симлинк ~/.hermes
ln -s /mnt/ai-ssd/hermes ~/.hermes

# 4. Создать все симлинки в ~/bin/
mkdir -p ~/bin
         git-auto-push.sh git-credential-github.sh task_ledger.py ledger-viewer.py \
    ln -sf ~/ai-system/scripts/$f ~/bin/$f
done

# 5. Установить Python зависимости
cd ~/.hermes/hermes-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Настроить git
git config --global user.name "<GITHUB_USER>"
git config --global user.email "<EMAIL>"
git config --global credential.helper '!/home/khadas/bin/git-credential-github.sh'

# 7. Запустить Docker контейнеры
cd ~/ai-system/freellmapi && docker compose up -d
cd ~/ai-system/searxng && docker compose up -d

# 8. Запустить Hermes Gateway
systemctl --user start hermes-gateway.service
systemctl --user enable hermes-gateway.service

# 9. Настроить cron
(crontab -l 2>/dev/null | grep -v 'git-auto-push.sh'; \
 echo "0 */6 * * * /home/khadas/bin/git-auto-push.sh") | crontab -

# 10. Проверка
systemctl --user status hermes-gateway.service
docker ps
~/bin/ledger-viewer.py stats
```

### 13.2. Восстановление только симлинков

```bash
mkdir -p ~/bin
         git-auto-push.sh git-credential-github.sh task_ledger.py ledger-viewer.py; do
    ln -sf ~/ai-system/scripts/$f ~/bin/$f
done
ls -la ~/bin/
```

### 13.3. Бэкап перед изменениями

```bash
# Бэкап .env
cp ~/ai-system/.env ~/ai-system/.env.backup.$(date +%Y%m%d)

# Бэкап конфигов
tar -czf ~/backup-hermes-$(date +%Y%m%d).tar.gz \
  ~/.hermes/config.yaml \
  ~/.aider.conf.yml \
  ~/ai-system/.gitignore

# Бэкап отчётов
tar -czf ~/backup-reports-$(date +%Y%m%d).tar.gz ~/research/reports/
```

---

## 🔧 14. Разработка и модификация

### 14.1. Добавление нового скрипта

```bash
# 1. Создать скрипт в scripts/
cat > ~/ai-system/scripts/my-script.py << 'EOF'
#!/usr/bin/env python3
# Описание
EOF
chmod +x ~/ai-system/scripts/my-script.py

# 2. Создать симлинк
ln -sf ~/ai-system/scripts/my-script.py ~/bin/my-script.py

# 3. Протестировать
~/bin/my-script.py

# 4. Закоммитить
cd ~/ai-system
git add scripts/my-script.py
git commit -m "feat: добавить my-script"
git push origin main
```

### 14.2. Добавление нового skill

```bash
# 1. Создать папку скилла
mkdir -p ~/.hermes/skills/my-category/my-skill

# 2. Создать SKILL.md
cat > ~/.hermes/skills/my-category/my-skill/SKILL.md << 'EOF'
---
name: my-skill
description: Описание скилла
tags: [tag1, tag2]
triggers:
  - /my-command
  - триггер фраза
---

# My Skill

## Активация
Описание когда активируется

## Workflow
Шаги выполнения

## Примеры
Примеры использования
EOF

# 3. Перезапустить gateway
systemctl --user restart hermes-gateway.service
```

### 14.3. Модификация существующего скрипта

```bash
# 1. Редактировать напрямую в scripts/
nano ~/ai-system/scripts/research-runner.py

# 2. Изменения автоматически доступны через симлинк ~/bin/
~/bin/research-runner.py --help

# 3. Закоммитить
cd ~/ai-system
git add scripts/research-runner.py
git commit -m "fix: описание изменения"
git push origin main
```

### 14.4. Добавление нового cron job

```bash
# 1. Создать скрипт
cat > ~/ai-system/scripts/my-cron.sh << 'EOF'
#!/bin/bash
# Логика cron job
echo "Running my cron job at $(date)"
EOF
chmod +x ~/ai-system/scripts/my-cron.sh

# 2. Добавить в системный cron
(crontab -l 2>/dev/null; echo "0 5 * * * /home/khadas/bin/my-cron.sh") | crontab -

# ИЛИ через Hermes cron (если нужен AI-агент)
hermes cron create
```

### 14.5. Оптимизация производительности

**O(n²) алгоритмы в research-runner.py**:
- `detect_lineage` — группировать по домену перед сравнением
- `EvidenceVerifier.verify` — ограничить окно первыми/последними N символами

**I/O оптимизации**:
- Убрать двойной `ckpt.load()` + `save()` в цикле по документам
- Держать `purls_map` в атрибуте агента

### 14.6. Мониторинг и метрики

```bash
# Память Hermes
systemctl --user status hermes-gateway.service | grep Memory

# Docker
docker stats --no-stream

# Диск
df -h /mnt/ai-ssd
du -sh ~/research/reports/

# Логи
tail -f ~/ai-system/logs/git-auto-push.log
tail -f ~/.hermes/logs/agent.log
```

---

## 📞 Поддержка

### Логи для диагностики

```bash
# Собрать все логи
tar -czf ~/hermes-logs-$(date +%Y%m%d).tar.gz \
  ~/ai-system/logs/ \
  /tmp/research-*.log \
  ~/.hermes/logs/ \
  ~/.hermes/cron/output/
```

### Контакты

- **Репозиторий**: https://github.com/<GITHUB_USER>/<REPO_NAME>
- **Автор**: Artem (<EMAIL>)
- **Telegram**: @<GITHUB_USER> (chat ID: <TELEGRAM_CHAT_ID>)

---

## 📄 Лицензия

MIT License

---

**Последнее обновление**: 2026-09-20  
**Версия документации**: 2.0  
**Строк**: 1200+

---

## 📋 Резюме для AI-агентов

Этот README даёт полное понимание системы:

1. **Архитектура**: симлинки `~/bin/` → `~/ai-system/scripts/` обеспечивают единый source of truth
2. **Безопасность**: 4 уровня защиты (gitignore, regex, FORBIDDEN_ROOTS, credential helper)
3. **Скиллы**: bundle → skill → runner, с правильным разделением ответственности
4. **Автопуш**: каждые 6 часов с проверкой секретов
5. **Aider**: НЕ может трогать ядро системы (FORBIDDEN_ROOTS)
6. **Исследования**: `/research тема --quick` = depth=1, `--depth N` = глубокое
7. **Восстановление**: полный скрипт из GitHub + симлинки

Любой AI-агент, прочитав этот документ, сможет:
- Понять архитектуру системы
- Запускать исследования и кодинг
- Диагностировать проблемы
- Добавлять новые компоненты
- Восстановить систему с нуля
