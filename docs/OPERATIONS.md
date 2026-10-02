# OPERATIONS.md — Управление Hermes-Titan

**Дата:** 2026-10-03
**Версия проекта:** 0.37.0 (CP-037)
**Версия Hermes:** v0.21.5+4925.gb4c9def.dirty
**HERMES_HOME:** /mnt/ai-ssd/hermes/

> **Источники истины (по приоритету):**
> 1. --help реальных команд
> 2. Этот документ (для сценариев)
> 3. DECISIONS.md (архитектурные решения)
> 4. README.md, IMPLEMENTATION_STATUS.md (статус)
>
> **No config guessing:** если не описано — сначала --help, потом действие.

---

## 1. Быстрый старт

    docker ps | grep -E freellmapi|searxng       # контейнеры
    sudo tailscale status | head -3               # Tailscale
    hermes gateway status                         # Gateway
    hermes memory status | head -6                # Память
    ~/ai-system/scripts/selfcheck.sh              # Self-check

**Ожидаем:**
- Контейнеры: Up, freellmapi — (healthy)
- Tailscale: khadas — active
- Gateway: Active (running), unit hermes-gateway-469b1f3f.service
- Memory: Provider holographic, Status available

---

## 2. Доступ к системе

### 2.1. SSH

    ssh khadas@192.168.0.XXX              # локальная сеть
    ssh khadas@khadas.taila31870.ts.net   # через Tailscale
    sudo systemctl status ssh              # OpenSSH-сервер

### 2.2. Tailscale

    sudo tailscale status
    sudo tailscale ip -4                  # 100.109.234.119
    sudo tailscale funnel status          # (Funnel on)
    sudo tailscale serve status           # tailnet only
    tailscale debug prefs | grep -i dns   # CorpDNS: true

**Выключить Funnel:**
    sudo tailscale funnel --bg --https=443 off

**Включить обратно:**
    sudo tailscale funnel --bg --https=443 http://127.0.0.1:3001

### 2.3. FreeLLMAPI

- Внутри VIM4: http://127.0.0.1:3001/
- Через Tailscale/Funnel: https://khadas.taila31870.ts.net/

Проверка API:
    curl -s http://127.0.0.1:3001/api/ping

### 2.4. Cron ticker

    ls -la /mnt/ai-ssd/hermes/cron/
    cat /mnt/ai-ssd/hermes/cron/ticker_last_success

Содержит: executions.db, ticker_heartbeat, ticker_last_success, output/.

---


## 3. Telegram — core-команды (67)

> Все команды доступны в Telegram-боте. Core-команды — часть ядра Hermes, не зависят от скиллов.
>
> Источник: hermes_cli/commands_platforms.py, функция telegram_menu_commands().
>
> Полный список: 102 команды, 0 скрыто (из них 35 — skill, см. раздел 4).

### 3.1. Управление сессией

| Команда | Описание |
|---------|----------|
| /help | Справка. /help skills — список скиллов, /help text — фильтр |
| /new | Новая сессия (свежий ID + история) |
| /status | Статус сессии, модель, токены, контекст |
| /version | Версия Hermes Agent |
| /profile | Активный профиль и домашняя директория |
| /whoami | Уровень доступа (admin / user) |
| /start | Подтвердить platform start pings |
| /stop | Убить все фоновые процессы |
| /sessions | Просмотр и возобновление сессий |
| /resume | Возобновить именованную сессию |
| /title | Название текущей сессии |
| /save | Экспорт текущего разговора |

### 3.2. Модель и провайдеры

| Команда | Описание |
|---------|----------|
| /model | Сменить модель (session-scoped; --global для постоянной) |
| /fast | Fast mode: normal/fast/auto/cold/ultrafast |
| /codex_runtime | Переключить codex app-server runtime |
| /reasoning | Уровень reasoning + отображение |

### 3.3. Контекст и токены

| Команда | Описание |
|---------|----------|
| /compress | Сжать контекст (here [N] — сохранить N ходов; --preview) |
| /context | Детальный вид окна контекста + gauge, категории, stats |
| /usage | Токены и лимиты; reset — погасить банк Codex |
| /insights | Аналитика использования |

### 3.4. Откат и правки

| Команда | Описание |
|---------|----------|
| /undo | Откатить N ходов пользователя (default 1) и повторить промпт |
| /retry | Повторить последнее сообщение |
| /rollback | Список/восстановление чекпоинтов (файловые правки) |
| /diff | Показать git-изменения в рабочей директории |
| /branch | Ветвление сессии (--here — остаться) |

### 3.5. Одобрения и безопасность

| Команда | Описание |
|---------|----------|
| /approve | Одобрить ожидающую опасную команду |
| /deny | Отклонить опасную команду |
| /yolo | YOLO-режим (пропуск всех одобрений) |
| /approvals | Режим одобрений опасных команд |
| /pause | Глобальная пауза; /pause off — возобновить |

### 3.6. Фоновые задачи и очереди

| Команда | Описание |
|---------|----------|
| /bg | Запустить промпт в фоновой сессии |
| /queue | Очередь промптов |
| /steer | Вставить сообщение после следующего tool call |
| /btw | Боковой вопрос |
| /agents | Активные агенты |
| /loop | Повторяющийся промпт с интервалом |
| /heartbeat | Recurring prompt при простое |

### 3.7. Память и обучение

| Команда | Описание |
|---------|----------|
| /memory | Ожидающие записи / approval gate |
| /refine | Сохранить уроки в память/скиллы |
| /learn | Изучить переиспользуемый скилл |
| /skills | Управление скиллами |
| /bundles | Список skill-бандлов |
| /curator | Фоновое обслуживание скиллов |

### 3.8. Kanban и планирование

| Команда | Описание |
|---------|----------|
| /kanban | Мультипрофильная доска коллаборации |
| /goal | Постоянная цель между ходами |
| /plan | markdown-план в .hermes/plans/ |
| /review | Независимый субагент для review |
| /moa | Mixture of Agents preset |

### 3.9. Автоматизация

| Команда | Описание |
|---------|----------|
| /init | Сгенерировать AGENTS.md из repo-скана |
| /suggestions | Просмотр предложенных автоматизаций |
| /blueprint | Автоматизация из шаблона |
| /sethome | Установить текущий чат как home channel |

### 3.10. Инфраструктура

| Команда | Описание |
|---------|----------|
| /egress | Статус Docker egress proxy |
| /reload_mcp | Перезагрузить MCP-серверы |
| /reload_skills | Пересканировать .hermes/skills/ |
| /platform | Pause/resume/list сбойных платформ |
| /restart | Graceful restart gateway |
| /update | Обновить Hermes Agent |
| /debug | Upload debug report |

### 3.11. Аккаунт Nous

| Команда | Описание |
|---------|----------|
| /login | Войти в Nous account |
| /topup | Баланс Nous и billing |

### 3.12. Настройки

| Команда | Описание |
|---------|----------|
| /personality | Персона агента |
| /voice | Голосовой режим |
| /footer | Runtime-метаданные footer |
| /busy | Поведение при работе Hermes |
| /topic | Telegram DM topic sessions |
| /commands | Все команды и скиллы (paginated) |

---


## 4. Telegram — skill-команды

> 55 установлено, 20 отключено для Telegram, 35 доступно.
>
> Источник: hermes skills list + skills.platform_disabled.telegram в /mnt/ai-ssd/hermes/config.yaml.
>
> Обоснование отключения — DEC-040: оптимизация промпта Telegram, overhead ~101 KB → ~52 KB (−48%).
> Детали: docs/PROMPT-OPTIMIZATION-CP037.md

### 4.1. Доступные (35)

#### Autonomous AI Agents (1)

| Команда | Описание |
|---------|----------|
| /hermes-agent | Использовать, настраивать, расширять Hermes Agent |

#### Creative (3)

| Команда | Описание |
|---------|----------|
| /baoyu-infographic | Инфографика: 21 layout × 21 style |
| /design-md | Google DESIGN.md: автор/валидация/экспорт |
| /p5js | p5.js скетчи: генеративное искусство, шейдеры |

#### DevOps (1)

| Команда | Описание |
|---------|----------|
| /sdlc-review | Review Kanban handoffs и маршрутизация верификации |

#### Email (2)

| Команда | Описание |
|---------|----------|
| /email-inbox-triage | Триаж inbox: приоритеты, thread summarization |
| /himalaya | Himalaya CLI: IMAP/SMTP email |

#### Media (3)

| Команда | Описание |
|---------|----------|
| /gif-search | Поиск/скачивание GIF из Tenor |
| /songsee | Аудио спектрограммы/фичи |
| /youtube-content | YouTube транскрипты → summaries, threads |

#### Note-taking (1)

| Команда | Описание |
|---------|----------|
| /obsidian | Чтение, поиск, создание, правка заметок Obsidian |

#### Productivity (6)

| Команда | Описание |
|---------|----------|
| /document-to-action-items | Извлечение обязательств, дедлайнов |
| /docx | Создание/чтение/правка Word |
| /pdf | PDF: создание, чтение, merge, fill |
| /powerpoint | Создание/чтение/правка .pptx |
| /product-price-monitor | Мониторинг цен |
| /xlsx | Excel .xlsx |

#### Research (5)

| Команда | Описание |
|---------|----------|
| /arxiv | Поиск статей arXiv |
| /competitor-news-monitor | Наблюдение за компаниями |
| /grounded-citations | Grounding в цитатах |
| /industry-event-research | Поиск выставок (local) |
| /llm-wiki | Karpathy LLM Wiki |

#### Software Development (11)

| Команда | Описание |
|---------|----------|
| /codebase-inspection | Инспекция кодовой базы с pygount |
| /dogfood | QA веб-приложений |
| /github | GitHub через gh CLI |
| /hermes-agent-skill-authoring | Авторство in-repo SKILL.md |
| /node-inspect-debugger | Debug Node.js |
| /python-debugpy | Debug Python |
| /requesting-code-review | Pre-commit review |
| /simplify-code | Параллельная 4-агентная чистка |
| /spike | Одноразовые эксперименты |
| /systematic-debugging | 4-фазная отладка root cause |
| /test-driven-development | TDD: RED-GREEN-REFACTOR |

#### Web (1)

| Команда | Описание |
|---------|----------|
| /blocked-page-recovery | Когда fetch падает: 403/429, paywalls |

### 4.2. Отключённые для Telegram (20)

Установлены, но не показываются в меню:

    airtable, ascii-video, box, claude-code, claude-design, codex,
    computer-use, google-workspace, humanizer, inspecting-hermes-desktop-dom,
    manim-video, maps, meeting-action-items, notion, opencode,
    popular-web-designs, songwriting-and-ai-music, teams-meeting-pipeline,
    weekly-review-planning, xurl

Включить обратно: убрать из skills.platform_disabled.telegram в config.yaml.

### 4.3. Управление скиллами

    hermes skills list                     # все
    hermes skills list --enabled-only      # включённые
    hermes skills search <текст>           # поиск
    hermes skills install <name>           # установить
    hermes skills inspect <name>           # preview
    hermes skills audit                    # пересканировать
    hermes skills update                   # обновить hub
    hermes skills uninstall <name>         # удалить

---


## 5. Telegram — сценарии использования

### 5.1. Начать работу

    /new

Свежая сессия. Использовать перед каждой новой задачей.

### 5.2. Исследовать тему

    исследуй квантование LLM для ARM64

**Что происходит:** Hermes запускает research_runner.py → AsyncSearcher → SearXNG → AsyncFetcher → EvidenceVerifier → summary_generator.py → Executive Summary → результат в Telegram.

### 5.3. Написать код

    напиши код для парсинга JSON в проекте my-project

**Что происходит:** проверка /mnt/ai-ssd/ai-system/projects/my-project → aider_runner.py my-project '...' → Aider правит в изоляции → post-flight compile → commit → diff в Telegram.

### 5.4. Узнать статус

    /status
    статус системы

### 5.5. Проверить Kanban

    /kanban
    hermes kanban list

### 5.6. Откатить изменения

    /rollback
    /rollback <N>

### 5.7. Сменить модель

    /model
    /model freellmapi:auto

Важно: смена session-scoped. Для постоянной — --global.

### 5.8. Фоновая задача

    /bg проверь все контейнеры и пришли отчёт

### 5.9. Очередь

    /queue промпт 1
    /queue промпт 2

### 5.10. Поставить цель

    /goal каждый день присылать сводку новостей по AI

### 5.11. План

    /plan рефакторинг research_runner.py

Создаст markdown-план в .hermes/plans/ без выполнения.

---

## 6. Aider — исполнитель кода

### 6.1. Основная команда

    cd ~/ai-system
    python3 scripts/aider_runner.py <project> <task> [flags]

project — путь внутри /mnt/ai-ssd/ai-system/projects/ (относительный или абсолютный).
task — текст задачи для Aider.

### 6.2. Флаги

| Флаг | По умолчанию | Описание |
|------|--------------|----------|
| --timeout N | 1800 (30 мин) | Таймаут в секундах |
| --push | выкл | Запушить после успеха |
| --allow-dirty | выкл | Разрешить работу в грязном репо |
| --task-id UUID | авто | Свой ID задачи |

### 6.3. Примеры

    python3 scripts/aider_runner.py test-aider 'add hello.py with a greeting function'
    python3 scripts/aider_runner.py my-project 'fix bug in parser' --push
    python3 scripts/aider_runner.py test-aider 'small fix' --timeout 600

### 6.4. Модель

По умолчанию: nvidia_nim/nvidia/nemotron-3-ultra-550b-a55b (DEC-020).
Override: AIDER_MODEL=other-model python3 scripts/aider_runner.py ...

### 6.5. Изоляция

Разрешено: /mnt/ai-ssd/ai-system/projects/

Запрещено:

    /mnt/ai-ssd/hermes/                    Ядро Hermes
    /mnt/ai-ssd/ai-system/scripts/         Скрипты
    /mnt/ai-ssd/ai-system/configs/         Конфиги
    /mnt/ai-ssd/ai-system/docs/            Документация
    /mnt/ai-ssd/ai-system/tests/           Тесты
    /home/khadas/.ssh/                     SSH-ключи
    /home/khadas/.config/                  Системные конфиги

Механизмы:
- resolve_project() — двойная проверка (requested + git root)
- FORBIDDEN проверяется первым
- Lock через fcntl.flock
- Fail-closed: git error → STOP
- Post-flight py_compile — синтаксические ошибки → откат
- killpg при таймауте

### 6.6. Результат (JSON)

Успех:

    {"ok": true, "task_id": "uuid", "status": "COMPLETED",
     "project": "...", "exit_code": 0, "elapsed_seconds": 42.5,
     "commit": {"hash": "...", "message": "...", "author": "Aider"},
     "changed_files": [...], "push": {...}, "log": "..."}

Ошибка:

    {"ok": false, "task_id": "uuid", "status": "POST_FLIGHT_FAILED",
     "message": "Syntax errors; rolled back", "errors": [...],
     "rolled_back": true, "log": "..."}

### 6.7. Статусы

COMPLETED, INVALID_PROJECT, NOT_GIT_REPOSITORY, AIDER_BUSY, AIDER_NOT_FOUND,
NVIDIA_API_KEY_MISSING, DIRTY_REPOSITORY, NO_ORIGIN_REMOTE, DETACHED_HEAD,
AIDER_FAILED, TIMEOUT, POST_FLIGHT_FAILED, GIT_CONFLICT, GIT_STATUS_FAILED.

### 6.8. Логи и Ledger

    ls -la ~/ai-system/logs/aider/
    cat ~/ai-system/logs/aider/<task_id>.log
    python3 scripts/ledger_viewer.py
    sqlite3 ~/ai-system/data/tasks.db 'SELECT task_id, status FROM tasks ORDER BY timestamp DESC LIMIT 10;'

---


## 7. Research Engine — глубокое исследование

### 7.1. Команда

    cd ~/ai-system
    python3 scripts/research_runner.py --topic '<тема>' [--depth N] [--dry-run] [--resume ID]

### 7.2. Флаги

| Флаг | По умолчанию | Описание |
|------|--------------|----------|
| --topic | — | Тема (обязательно) |
| --depth | 3 | Глубина |
| --dry-run | выкл | Без LLM-запросов |
| --resume ID | — | Продолжить с чекпоинта |

### 7.3. Примеры

    python3 scripts/research_runner.py --topic 'ARM64 optimization for LLM inference'
    python3 scripts/research_runner.py --topic 'quantization methods' --depth 5
    python3 scripts/research_runner.py --topic 'test' --dry-run
    python3 scripts/research_runner.py --resume abc123

### 7.4. Архитектура (Deep Research Agent v3.0)

DEC-043: монолитный файл 858 строк разбит на 12 модулей в research/.
research_runner.py = 97 строк (тонкий CLI + реэкспорт для тестов).
Метод: auto-modularize.sh + Aider (Ultra). Итог: 18 коммитов, 42 pytest passed.
Детали: docs/CP-036-MODULARIZATION.md.

Модули (CP-036):

- research.checkpoint — CheckpointManager
- research.config — WORKING_DIR, _load_dotenv
- research.evidence — ConflictDetector, EvidenceVerifier, FactValidator
- research.fetch — AsyncFetcher
- research.lineage — detect_lineage
- research.llm — LLMGateway
- research.models — Evidence
- research.scoring — ConfidenceScorer, SourceQualityScorer
- research.search — AsyncSearcher
- research.text_utils — _relevance_score, normalize_*
- research.runner — DeepResearch
- research.json_utils — repair_json, parse_json_resilient

### 7.5. Чекпоинты

При Ctrl+C — agent.save_ckpt(), вывод: Interrupted. Resume: --resume <id>.

### 7.6. Пайплайн

Plan → Search (SearXNG) → Fetch → Extract (LLM) → Evidence → Score → Summarize → Output.

### 7.7. Тесты

    python3 -m pytest tests/research/ -v

---

## 8. Executive Summary — генератор сводок

Файл: scripts/summary_generator.py
Используется: внутри research_runner.py.

### 8.1. Архитектура

    Evidence → LLM (JSON) → Pydantic schema → Citation validator → (Repair ×1) → Render
    Failure → Deterministic fallback

### 8.2. Ключевые решения

- JSON scanner через raw_decode, не regex
- Pydantic валидирует только структуру
- top_p=1.0, max_tokens=1500
- Fallback — top_claims_by_authority

---

## 9. Send to Telegram

Файл: scripts/send_to_telegram.py

### 9.1. Команда

    python3 scripts/send_to_telegram.py <file> [--caption TEXT] [--message TEXT]

Что делает: отправляет файл как document через Bot API sendDocument.

Требует: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID в .env.

### 9.2. Пример

    python3 scripts/send_to_telegram.py ~/ai-system/report.md --caption 'Отчёт за сегодня'

---

## 10. Task Ledger

БД: ~/ai-system/data/tasks.db
Схема version: 2

Таблица tasks:

    task_id (PK), timestamp, project, task, status,
    initial_head, final_head, commit_hash, commit_message,
    changed_files, exit_code, elapsed_seconds, error_message,
    dirty_before, pre_existing_changes,
    started_at, finished_at

Индексы: idx_tasks_status, idx_tasks_project, idx_tasks_timestamp

Записей: ~28

Просмотр:

    python3 scripts/ledger_viewer.py
    sqlite3 ~/ai-system/data/tasks.db 'SELECT task_id, project, status FROM tasks ORDER BY timestamp DESC LIMIT 10;'

Используется автоматически aider_runner.py, не для ручного вызова.

---


## 11. Kanban

Board: hermes-titan (активный)
Второй board: default (пустой)
Project: hermes-titan (p_7464919e)

### 11.1. Проверка

    hermes kanban list
    hermes kanban boards list
    hermes kanban assignees               # → default
    hermes project list                   # → hermes-titan

### 11.2. Задачи

    hermes kanban list --status in_progress
    hermes kanban list --status todo

### 11.3. Интеграция Kanban→Hermes→Aider

- Протестирована (26s тест, CP-007)
- Dispatcher в gateway
- Worker создаётся из task → вызывает Aider

### 11.4. kanban.max_in_progress

DEC-042: параметр не задан явно, Hermes использует memory-derived default = 8.
8 процессов ≈ 8 GB RAM, соответствует VIM4.

Переопределение (если понадобится):
    hermes config set kanban.max_in_progress <N>

Детали: DEC-021, DEC-022, DEC-028, DEC-029, DEC-042.

---

## 12. Память

Провайдер: holographic (local)
Плюс: built-in (MEMORY.md / USER.md)
Memory tool: включён

### 12.1. Проверка

    hermes memory status

Ожидаем:

    Built-in (MEMORY.md / USER.md):
      Memory injection:   enabled
      User profile:       enabled
      Memory tool:        enabled
    Provider:  holographic
    Plugin:    installed
    Status:    available

### 12.2. Патч Holographic v3

Файл: scripts/holographic-patch.sh

Версии патча:
- v1: on_memory_write replace/remove (issue #55095)
- v2: retrieval_count для search() (issue #101521)
- v3: расширенный _extract_entities (Cyrillic, ALL CAPS, CamelCase, стоп-слова)

DEC-038: ensure-hrr-numpy (в bin/ + systemd drop-in) удалён — указывал на
несуществующий venv после hermes update. store.py включён в патч v3 (раньше
патчился вручную). Маркеры: строки 77, 237 в store.py.

Логика Patch 3 (store.py):
- Если _RE_SINGLE_ENTITY расширен (Cyrillic) и есть _STOP_WORDS → добавить маркеры v3, не менять код
- Иначе → полная замена upstream-версии на расширенную
- Бэкап store.py.orig (один раз)

Идемпотентность: маркеры HOLOGRAPHIC_PATCH_v1/v2/v3 в трёх файлах, повторный запуск — no-op.

Патчит:
- plugins/memory/holographic/__init__.py
- plugins/memory/holographic/retrieval.py
- plugins/memory/holographic/store.py

Переприменение:

    ~/ai-system/scripts/holographic-patch.sh

### 12.3. Управление через Telegram

    /memory              ожидающие записи / approval gate
    /refine              сохранить уроки
    /learn               изучить скилл

DEC-023, DEC-024, DEC-025, DEC-030, DEC-031, DEC-036 — детали.

---

## 13. Восстановление

Три уровня. Детали в docs/RECOVERY.md (85 строк).

### 13.1. Уровень 1 — Чекпоинты сессии

    /rollback                     в сессии Hermes
    hermes checkpoints status
    hermes checkpoints prune
    hermes checkpoints clear      ВСЕ чекпоинты — осторожно

Путь: /mnt/ai-ssd/hermes/checkpoints/.

### 13.2. Уровень 2 — Git-теги CP

    cd ~/ai-system
    git tag -l 'CP-*'
    git checkout CP-XXX
    git reset --hard CP-XXX
    git push --force-with-lease origin main

### 13.3. Уровень 3 — Полный бэкап

Штатный Hermes:

    hermes backup -o /path/to/hermes-full.zip -k 3   # ~2.2 MB
    hermes import /path/to/hermes-full.zip

Quick snapshot:

    hermes backup --quick -l <label>      # → HERMES_HOME/state-snapshots/
    /snapshot restore <timestamp>-<label> # в Hermes

Наши данные:

    ~/ai-system/scripts/backup.sh         # ~236 KB
    sqlite3 ~/ai-system/data/tasks.db < backups/<timestamp>/tasks_dump.sql

### 13.4. Полное восстановление VIM4 с нуля

1. OOWOW → Ubuntu 24.04.5 LTS
2. SSD → /mnt/ai-ssd
3. git clone git@github.com:artemfire1980/hermes-titan.git ~/ai-system
4. HERMES_HOME=/mnt/ai-ssd/hermes curl … install.sh | bash
5. hermes import <полный бэкап.zip>
6. hermes doctor, hermes memory status, hermes gateway status
7. Docker: cd /mnt/ai-ssd/freellmapi && docker compose up -d
8. Проверка: curl http://127.0.0.1:3001/api/ping, curl http://127.0.0.1:8888/

### 13.5. Тест восстановления (mandatory)

Раз в неделю или перед крупными изменениями:

    hermes backup -o /tmp/test-backup.zip
    hermes checkpoints status
    ~/ai-system/scripts/backup.sh
    git status

Пройден: 2026-10-02 (docs/RECOVERY-TEST-2026-10-02.md).

---

## 14. Правила работы с кодом

Детали: docs/CODE_EDITING_RULES.md

9 шаблонов:
1. Создать файл заново — cat > file << 'PYEOF'
2. Заменить кусок — Python-скрипт с .replace()
3. Заменить строку — sed -i
4. Добавить строку в конец — echo >>
5. Удалить файл — rm -f
6. Проверить синтаксис — python3 -m py_compile
7. Работа с chmod 444 — chmod 600 → правка → chmod 444
8. Поиск — grep -n, grep -rn
9. Показать содержимое — cat, head, tail, sed -n

---

## 15. Персонализация

Детали: docs/PERSONALIZATION.md

Env-переменные в /mnt/ai-ssd/hermes/.env:

    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_ALLOWED_USERS,
    GITHUB_USER, GITHUB_TOKEN, GITHUB_REPO,
    OPENAI_API_KEY, NVIDIA_API_KEY,
    SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_ANON_KEY,
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, R2_ENDPOINT

Проверка:

    grep -E '=<' ~/ai-system/.env && echo 'есть незаполненные' || echo 'всё заполнено'

---

## 16. config.yaml — структура

Файл: /mnt/ai-ssd/hermes/config.yaml (180 строк)
Config version: 49

Top-level секции:

- custom_providers — FreeLLMAPI (base_url http://127.0.0.1:3001/v1, model auto)
- database — journal_mode: wal (DEC-032)
- memory — provider: holographic
- model — api_key, base_url, default auto, provider custom
- platforms — telegram (enabled, home_channel chat_id 170690883)
- web — backend searxng, search_backend searxng, searxng_url
- plugins — enabled: [progressive-skill]
- toolsets — [hermes-cli, kanban]
- skills — platform_disabled.telegram (20 скиллов)
- tools — compact_schemas true, tool_search.defer (18 инструментов)

### 16.1. Оптимизация промпта Telegram (DEC-040)

- Плагин progressive-skill — Skills: 5 456 → 0 B
- tools.compact_schemas: true — System prompt: 16 477 → 13 153 B
- tool_search.defer — отложены delegation, session_search, todo и др.
- 20 скиллов отключены для Telegram
- 12 toolsets отключены для Telegram

Результат: ~101 KB → ~52 KB (−48%).
Детали: docs/PROMPT-OPTIMIZATION-CP037.md.

### 16.2. Deferred tools (18)

    computer_use, session_search, image_generate, todo_list, process_manage,
    cronjob_manage, drive_preview, gui_tour, desktop_preview, annotate_preview,
    show_tip, desktop_project, close_terminal, apply_layout, read_terminal,
    read_window_below, focus_pane, delegation

### 16.3. PyYAML в runtime Python (DEC-041)

Установлен в /mnt/ai-ssd/hermes/tools/python-3.14.7+.../bin/python3.14 -m pip install pyyaml.

Риск: при hermes update / hermes pm install runtime Python может перезаписаться.
Проверять после обновлений — иначе progressive-skill будет работать на defaults.

---

## 17. systemd units

### 17.1. Gateway

    systemctl --user status hermes-gateway-469b1f3f.service

- Путь: /home/khadas/.config/systemd/user/hermes-gateway-469b1f3f.service
- Drop-In: /home/khadas/.config/systemd/user/hermes-gateway-469b1f3f.service.d/runtime.conf
- Active: running
- Main PID: hermes
- Memory: ~220 MB
- Логи: journalctl --user -u hermes-gateway-469b1f3f.service -f

Имя юнита — динамическое (суффикс 469b1f3f, DEC-011). Обновляется через hermes gateway setup.

### 17.2. Linger

    loginctl show-user khadas | grep Linger

Должно быть Linger=yes — служба переживает выход из терминала.

---

## 18. Полный справочник скриптов

Все в ~/ai-system/scripts/:

| Скрипт | Назначение |
|--------|------------|
| aider_runner.py | Hermes → Aider (изоляция, ledger) |
| auto-modularize.sh | Автомодуляризация кода |
| backup-projects.sh | Бэкап проектов |
| backup.sh | Бэкап наших данных (~236 KB) |
| check-freellm-quotas.sh | Квоты FreeLLMAPI |
| check-memory-peak.sh | Пик памяти |
| check_r2_budget.sh | Бюджет R2 |
| env_utils.py | Единый парсер .env (DEC-047) |
| git-auto-push.sh | Авто-пуш |
| git-credential-github.sh | GitHub credential helper |
| holographic-patch.sh | Патч Holographic v3 |
| ledger_viewer.py | Просмотр task ledger |
| md2docx.py | MD → DOCX |
| research_runner.py | Deep Research Agent v3.0 |
| research-telegram.sh | Research → Telegram |
| resource-governor.sh | Управление тяжёлыми задачами (DEC-026) |
| selfcheck.sh | Self-check системы |
| send_to_telegram.py | Отправка файлов |
| summary_generator.py | Executive Summary |
| sync_tasks_to_supabase.py | Синхронизация с Supabase |
| task_ledger.py | SQLite task storage |

Поддиректории: coding-engine/, data-engine/, research/

### 18.1. env_utils.py (DEC-047)

Единый парсер .env для трёх скриптов: send_to_telegram.py, sync_tasks_to_supabase.py,
scripts/research/config.py.

Сигнатура: load_env(candidates, override=False, log=None)

Читает первый существующий файл из candidates, делает setdefault (не перезаписывает
уже установленные env), опционально логирует источник.

Не унифицированы candidates — три разных списка путей. Реально существует только
/mnt/ai-ssd/hermes/.env (HERMES_HOME). Остальные (~/ai-system/.env, ~/.hermes/.env)
не существуют — скрипты работают только если env уже установлен снаружи.

Коммит: faea162.

---

## 19. Hermes CLI — подтверждённые команды

| Команда | Подкоманды |
|---------|------------|
| hermes skills | trust, untrust, browse, search, install, inspect, list, check, update, audit, uninstall, reset, list-modified, diff, opt-out, opt-in, repair-official, publish, snapshot, tap, config |
| hermes kanban | create, list, show, comment, unblock, complete, swarm, stats, assignees, boards |
| hermes memory | setup, status, off, reset |
| hermes project | list |
| hermes gateway | status, start, stop, restart, list, setup, install |
| hermes backup | -o, -k N, --quick -l <label> |
| hermes import | существует |
| hermes checkpoints | status, prune, clear |
| hermes doctor | диагностика |
| hermes --version | v0.21.5+4925.gb4c9def.dirty |

---

## 20. Диагностика

- ~/ai-system/scripts/selfcheck.sh — самопроверка
- ~/ai-system/scripts/check-freellm-quotas.sh — квоты FreeLLMAPI
- ~/ai-system/scripts/check-memory-peak.sh — память
- ~/ai-system/scripts/check_r2_budget.sh — бюджет R2
- docker ps -a — контейнеры
- sudo tailscale status — Tailscale
- hermes gateway status — Gateway
- journalctl --user -u hermes-gateway-469b1f3f.service -f — логи gateway

### 20.1. Штатные warning-и (игнорировать)

DEC-046: ModuleNotFoundError: No module named 'nemo_relay' — штатное состояние.
nemo_relay — optional extra Hermes, помечен nemo-relay = false в uv.lock.
RelayHostRegistry ловит ImportError → NoopRelayRuntime. Relay-телеметрия не используется.
Игнорировать warning в логах.

---

## 21. Открытые вопросы и расхождения

### Расхождения в документации

README.md (устарело):
- Версия: 0.30.0 / CP-030
- Hermes: v0.21.5+3779
- Модели: 314

IMPLEMENTATION_STATUS.md (устарело):
- Версия Hermes: v0.21.5+2453
- Модели: 253

Факт:
- Версия Hermes: v0.21.5+4925.gb4c9def.dirty
- Версия проекта: 0.37.0 / CP-037

### Расхождения в .bashrc/MOTD

Строка cd ~/.hermes/hermes-agent && source venv/bin/activate — мёртвая, путь не существует.
Источник — MOTD или profile.d. Найти и поправить.

### TODO

- Отключить key expiry у VIM4 в Tailscale Admin
- Проверить точное число моделей FreeLLMAPI (нужен unified key)
- Обновить README.md под факт
- Поправить MOTD

---

## 22. Быстрая шпаргалка: задача → команда

| Задача | Telegram | Терминал |
|--------|----------|----------|
| Новая сессия | /new | — |
| Статус | /status | hermes gateway status |
| Сменить модель | /model freellmapi:auto | — |
| Исследовать | исследуй <тема> | python3 scripts/research_runner.py --topic '<тема>' |
| Написать код | напиши код для <задача> | python3 scripts/aider_runner.py <project> '<task>' |
| Kanban | /kanban | hermes kanban list |
| Откат | /rollback | git reset --hard CP-XXX |
| Память | /memory | hermes memory status |
| Скиллы | /skills | hermes skills list |
| План | /plan <задача> | — |
| Фон | /bg <задача> | — |
| Очередь | /queue <задача> | — |
| Логи gateway | — | journalctl --user -u hermes-gateway-469b1f3f.service -f |
| Справочник команд | /commands | — |

---

## 23. Статус документа

**Создан:** 2026-10-03
**Версия:** черновик 1
**Проверено:** частично
**Известные вопросы:**
- Раздел 4.1: /simplify-code — уточнить (не дубликат ли)
- Разделы 9-12: проверить ссылки на DEC
- Возможно упущены команды, отключённые пользователем (нужен полный audit)

**План:**
1. Проверить на реальных сценариях
2. Уточнить расхождения в README/IMPLEMENTATION_STATUS
3. Убрать пометку «черновик 1» после полной валидации
