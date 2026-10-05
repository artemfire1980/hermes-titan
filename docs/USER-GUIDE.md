# Hermes-Titan: руководство пользователя

> Как подключиться, что набирать в Telegram, как диагностировать.
> Полные справочники — `docs/OPERATIONS.md`, `docs/STRUCTURE.md`.
> Обновлено: 2026-10-03.

## 1. Что такое HERMES-TITAN

Автономная AI-платформа на Khadas VIM4 (ARM64, 8 GB RAM) поверх Hermes Agent.
Задачи: исследование (SearXNG + FreeLLMAPI), написание кода (Aider + NVIDIA NIM),
Kanban, память (Holographic), cron.

**Ключевые пути:**
- Репо проекта: `~/ai-system` (симлинк на `/mnt/ai-ssd/ai-system`)
- HERMES_HOME: `/mnt/ai-ssd/hermes/`
- Конфиг Hermes: `/mnt/ai-ssd/hermes/config.yaml`
- Gateway: `hermes-gateway-469b1f3f.service` (user systemd)

Полная карта — `docs/STRUCTURE.md`.

## 2. Подключение к VIM4

### 2.1. SSH — два способа

**Способ А: локальная сеть**

    ssh khadas@<локальный-IP>

Работает только из той же сети (Wi-Fi/Ethernet).

**Способ Б: Tailscale**

    ssh khadas@khadas.taila31870.ts.net

Работает откуда угодно, если на клиенте установлен Tailscale и он залогинен
под тем же аккаунтом (artemfire1980).

На Windows: установить Tailscale-клиент → залогиниться → `ssh khadas@khadas.taila31870.ts.net`.

### 2.2. Проверка состояния (одна команда)

    cd ~/ai-system && ./scripts/selfcheck.sh

### 2.3. Активация окружения (для ручной работы)

    export HERMES_HOME=/mnt/ai-ssd/hermes
    source "$HERMES_HOME/hermes-agent/venv/bin/activate"
    cd ~/ai-system

## 3. Telegram — основной интерфейс

### 3.1. Первичная настройка (если бот ещё не настроен)

    hermes gateway setup           # интерактивно: выбрать Telegram, вставить токен и ID
    hermes gateway install --start-now
    sudo loginctl enable-linger khadas   # чтобы gateway работал после logout

Проверка:

    hermes gateway status

Должно быть `active (running)`. Юнит: `hermes-gateway-469b1f3f.service`.

### 3.2. 67 команд Telegram

Полный список — `docs/OPERATIONS.md`, раздел 3. Ключевые:

| Команда | Что делает |
|---------|-----------|
| `/new` | Новая сессия (сброс контекста) |
| `/status` | Информация о сессии |
| `/model` | Сменить модель (интерактивно) |
| `/personality` | Сменить персону |
| `/resume` | Продолжить именованную сессию |
| `/sessions` | Список сессий |
| `/title` | Задать имя сессии |
| `/retry` | Повторить последний запрос |
| `/undo` | Отменить последний обмен |
| `/compress` | Сжать контекст вручную |
| `/usage` | Использование токенов и лимиты |
| `/insights` | Аналитика |
| `/memory` | Управление памятью |
| `/kanban` | Kanban-доска |
| `/bg <задача>` | Задача в фоне |
| `/queue <задача>` | Поставить в очередь |
| `/steer` | Вмешаться в работу агента |
| `/plan` | Планирование |
| `/review` | Ревью |
| `/loop` | Циклическая задача |
| `/goal`, `/subgoal` | Цели и подцели |
| `/approve`, `/deny` | Approve/deny опасных команд |
| `/pause` | Emergency stop |
| `/sethome` | Установить текущий чат как home channel |
| `/help` | Полный список команд |
| `/commands` | Список команд |
| `/reload_skills` | Пересканировать skills |
| `/reload_mcp` | Пересканировать MCP |
| `/rollback` | Откат файловых изменений (чекпоинты) |
| `/diff` | Показать diff |
| `/yolo` | Отключить подтверждения (осторожно!) |
| `/reasoning` | Уровень reasoning |
| `/fast` | Быстрый режим |
| `/voice` | Голосовой режим |
| `/restart`, `/update`, `/version` | Служебные |
| `/debug` | Debug-информация |

### 3.3. Home channel

`/sethome` — установить текущий чат как «домашний» для доставки cron-задач и уведомлений.

Текущий home channel: `170690883` (Artem).

## 4. Сценарии использования

### 4.1. Исследование темы

В Telegram:

    исследуй <тема>

Что происходит: SearXNG → извлечение → Executive Summary → ответ в чат.

Из CLI:

    cd ~/ai-system && python3 scripts/research_runner.py --topic '<тема>'

Требует SearXNG (Docker `127.0.0.1:8888`) и FreeLLMAPI (`127.0.0.1:3001`).

### 4.2. Написание кода

В Telegram:

    напиши код для <задача> в проекте <имя>
    поправь <файл> в проекте <имя>

Что происходит: Aider (NVIDIA NIM Ultra) в изолированной зоне
`/mnt/ai-ssd/ai-system/projects/` → diff → одобрение → коммит.

Из CLI:

    cd ~/ai-system && python3 scripts/aider_runner.py <project> '<task>'

Правила Aider: модель `nvidia_nim/nvidia/nemotron-3-ultra-550b-a55b`,
**без** `~/.aider.model.settings.yml`, с `--no-show-model-warnings`.

### 4.3. Kanban

В Telegram:

    /kanban

Из CLI:

    hermes kanban list                       # список задач
    hermes kanban boards                     # список досок
    hermes kanban create <title>             # создать
    hermes kanban show <task-id>             # детали

Активная доска: `hermes-titan`. Dispatcher встроен в gateway (тик 60 сек).
Workspace по умолчанию — `scratch` (эфемерный).

### 4.4. Память

В Telegram:

    /memory

Встроенная память (MEMORY.md, USER.md) + Holographic provider.
Лимиты: MEMORY.md ~2200 символов, USER.md ~1375.

### 4.5. Cron

В Telegram (естественный язык):

    каждый день в 8 утра присылай сводку

Из CLI:

    hermes cron create
    hermes cron list
    hermes cron status

Доставка — на home channel (`/sethome`).

## 5. Диагностика

### 5.1. Бот не отвечает

    hermes gateway status
    journalctl --user -u hermes-gateway-469b1f3f.service -f

Проверить: токен бота актуален, числовой ID в `TELEGRAM_ALLOWED_USERS`,
gateway запущен.

### 5.2. FreeLLMAPI недоступен

    docker ps | grep freellmapi
    docker logs freellmapi --tail 50
    curl -s http://127.0.0.1:3001/v1/models -H "Authorization: Bearer $OPENAI_API_KEY" | head -c 200

### 5.3. SearXNG недоступен

    docker ps | grep searxng
    curl -s "http://127.0.0.1:8888/search?q=test&format=json" | head -c 200

### 5.4. Полная проверка системы

    cd ~/ai-system && ./scripts/selfcheck.sh
    hermes status --all
    hermes status --all --deep

### 5.5. Полная диагностика — `docs/OPERATIONS.md`, раздел 20.

## 6. Шпаргалка «задача → команда»

| Задача | Telegram | CLI |
|--------|----------|-----|
| Новая сессия | `/new` | — |
| Статус | `/status` | `hermes gateway status` |
| Сменить модель | `/model` | `hermes model` |
| Исследовать | `исследуй <тема>` | `python3 scripts/research_runner.py --topic '<тема>'` |
| Написать код | `напиши код для <задача>` | `python3 scripts/aider_runner.py <project> '<task>'` |
| Kanban | `/kanban` | `hermes kanban list` / `hermes kanban boards` |
| Память | `/memory` | `hermes memory status` |
| Скиллы | `/reload_skills` | `hermes skills list` |
| Cron | `каждый день в 8...` | `hermes cron create` |
| Откат | `/rollback` | `git reset --hard <CP>` |
| Фоновая задача | `/bg <задача>` | — |
| Очередь | `/queue <задача>` | — |
| Home channel | `/sethome` | — |
| Помощь | `/help` | `hermes --help` |

## 7. Ссылки

- `docs/OPERATIONS.md` — полный справочник (67 Telegram-команд, скрипты, диагностика).
- `docs/STRUCTURE.md` — карта проекта (пути, носители).
- `DECISIONS.md` — 48 архитектурных решений.
- `docs/RECOVERY.md` — три уровня восстановления.

---

**Создан:** 2026-10-03
**Статус:** черновик (валидирован по бесплатным командам; дорогие сценарии — по мере проверки).

## 8. Внешние интеграции (MCP)

**См.** `docs/INTEGRATIONS.md` — общий обзор.

### 8.1. Что подключено

| Сервис | Инструментов | Статус |
|---|---|---|
| **Почта Mail.ru** | 5 read | ✅ работает |
| **3D-принтер ZAV (Kiln)** | 71 read | ✅ работает |
| **CRM МойСклад** | — | ⏸️ отложено |

### 8.2. Почта — примеры

Покажи список папок в почте
Найди письма от example@mail.ru за последнюю неделю
Прочитай последнее письмо в INBOX

**Что НЕ работает:** отправка, ответы, вложения (только метаданные).

### 8.3. 3D-принтер — примеры

Покажи статус принтера ZAV
Сделай снимок принтера (требует камеры)
Проверь, можно ли напечатать model.stl
Сколько стоит печать model.stl?
Почему последняя печать упала?

**Что НЕ работает:** start_print, set_temperature, cancel_print — **исключены** (безопасность).

### 8.4. CRM МойСклад

**Отложено** — alpha-баг Unicode. См. `docs/MOYSKLAD.md`.

## 9. Что НЕ делать

### ❌ Не предлагать обход whitelist

Агент **не должен** предлагать:
- Прямой `curl` к API (обход MCP).
- Чтение токенов из `cabinets.json`, `.env`, `config.toml`.
- Использование **запрещённых** инструментов.
- «Давайте я добавлю write-инструмент» — **нет**.

### ❌ Не трогать

- **`hermes-agent/`** — апстрим Nous.
- **`config.yaml`** — только через `hermes config set` или **python-патч**.
- **Секреты** — не в git, не в чат.
- **`kiln3d install-mcp`** — не запускать (перезапишет config).

### ❌ Не запускать вслепую

- `setup.sh` из `pre-wipe-staging`.
- `docker compose config` без `--services`.
- Скрипты с `sudo` от Hermes.

## 10. Шпаргалка по MCP

| Задача | Команда |
|---|---|
| Список MCP | `hermes mcp list` |
| Добавить | `hermes mcp add <name> --command <bin> --env ... --args <args>` |
| Удалить | `hermes mcp remove <name>` |
| Тест | `hermes mcp test <name>` |
| Применить | `hermes gateway restart` |
| Просмотр tools | `hermes mcp test <name>` (полный вывод) |
