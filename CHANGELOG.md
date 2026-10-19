# История изменений

## [Unreleased] - 2026-10-19

### Добавлено (сессия 2026-10-16 → 2026-10-19)
- Hermes обновлён v0.22.0 → **v0.22.0 stable** (DEC-060).
- Holographic вынесен из ядра → **community plugin 0.17.4** (itpartypattaya).
- Skill `update-hermes` — 5 фаз, Phase 3 (Compare с OUR-STACK).
- Skill `update-stack` — FreeLLMAPI/плагины/MCP, русский отчёт в Telegram.
- Skill `session-search-ru` — trigram FTS для кириллицы.
- Cron jobs (3): `moysklad-refresh-weekly`, `mail-check-daily`, `update-stack-weekly`.
- Скрипты: `moysklad_refresh.py`, `mail_check.py`, `session_search_ru.py`, `sync-cron-scripts.sh`.
- `docs/OUR-STACK.md` — инвентарь сторонних решений.
- `docs/EMAIL-OVERDUE-2026-10-18.md`, `docs/EMAIL-OVERDUE-SAMSONOV-2026-10-18.md`.
- `docs/MEMORY-SNAPSHOT.md`, `docs/USER-SNAPSHOT.md`.
- FreeLLMAPI v0.16.5 → **v0.16.5** (фиксированный тег).
- Holographic 53 факта (все проекты + персона).
- MEMORY.md сокращён с 2978 до **1035 chars** (universal + маршрутизация).
- 16 skills обновлены (query + recall + алгоритмы).

### Исправлено
- Email-анализ: `PUBLIC_DOMAINS` — ложные domain-матчи убраны (108 → 59 корпоративных).
- Email-анализ: `--owner` — универсальный отчёт по фамилии менеджера.
- `moysklad_refresh.py`: `expand=owner` — owner сразу в email_base.json (1701/1702).
- `session_search`: кириллица через trigram FTS (обход unicode61).
- `agent.reasoning_effort: low` — применён.

### Удалено
- `holographic-patch.sh` (не нужен в v0.22.0).
- `holographic-patch.service`, `holographic-patch.timer` (systemd).

## [Unreleased] - 2026-10-02

### Исправлено (аудит кодовой базы)
- Проведён статический аудит репозитория двумя проходами; подтверждено 9 находок, 11 фейков (галлюцинации из устаревшего `.pyc` монолита).
- `resource-governor.sh`: regex-инъекция в `sed` → `awk -F:` + валидация `:` в имени задачи; `flock -w 30` вместо вечного ожидания.
- `aider_runner.py`: убран хардкод `/home/khadas/...`, удалён дубль `import sys`.
- `git-auto-push.sh`: `git reset HEAD` при падении selfcheck → только своих путей (`STAGE_PATHS`).
- `research/*`: 7 голых `except:` сужены до конкретных исключений; sidecar получил `schema_version: "1.0"`.
- `.env`-парсинг: три копии → единый `scripts/env_utils.py`.
- `DECISIONS.md`: разграничены `SEARXNG_BASE_URL` (контейнер) и `SEARXNG_URL` (код), убрана мёртвая `SEARXNG_INSTANCE_URL`.
- `.gitignore`: добавлен `.ruff_cache/`.
- Удалены `.pyc`-сироты монолита `research-runner.py` (причина галлюцинаций аудита).

### Добавлено
- Web: `extract_backend: exa` — семантическое извлечение контента (DEC-049). `search_backend` остаётся SearXNG. Exa работает keyless (без API-ключа, rate-limited).
- STT: локальный `faster-whisper 1.2.1` + `av 18.1.0`, модель `base`, язык `ru` (DEC-052).
- Runtime venv Hermes: правильная установка extras через `pm.sync_venv` (DEC-052).
- Kiln MCP (kiln3d 1.4.1.1) — 3D-принтер ZAV, 71 read-only tool (DEC-053).
- rubit-mcp-mail 1.0.0 — почта Mail.ru, 5 read-only tool (DEC-054).
- МойСклад — **официальный MCP** (`mcp.moysklad.ru`), 4 generic read-only tools (DEC-056).
- Правила безопасности MCP зафиксированы: `docs/SECURITY.md` + `MEMORY.md` (DEC-057).
- МойСклад MCP alpha — отложено (DEC-055, пересмотрено DEC-056).
- Документация: `docs/INTEGRATIONS.md`, `docs/KILN.md`, `docs/MAIL.md`, `docs/MOYSKLAD.md`, `docs/PRINTER-CONFIG.md`.

## [0.30.0] - 2026-09-30

### Добавлено
- CP-030: mock HTTP через respx (14 тестов) + persistent client в AsyncFetcher
- CP-029: чистка тестов + ruff config
- CP-028: тесты без exec() и хардкодов
- CP-027: requirements.txt / requirements-dev.txt / requirements.lock.txt
- CP-026: performance — persistent clients, CACHE_VERSION, prefilter lineage

### Изменено
- CP-031: удалён мёртвый код (~70 строк), архивы, дубликаты
- CP-016: все БД переведены в WAL
- CP-015: Holographic FTS5 recovery
- CP-014: Holographic patch v2 (on_memory_write, retrieval_count)

### Исправлено
- CP-022…CP-025: by_metric NameError, citation_number, JSON mode, system_prompt
- CP-012…CP-013: Kanban native tools + 3 workspace types
- CP-006: Aider модель Ultra (без YAML)

## [0.11.0] - 2026-09-27

### Добавлено
- CP-011: базовый уровень + CHECKLIST.md
- CP-010: восстановление (3 уровня)
- CP-009: resource governor
- CP-008: Holographic memory
- CP-007: Kanban + Aider

## [0.5.0] - 2026-09-26

### Добавлено
- CP-006: ctx7 + Aider
- CP-005: аудит старой системы
- CP-004: FreeLLMAPI + SearXNG
- CP-003: аудит возможностей ядра
- CP-002: Telegram

## [0.1.0] - 2026-09-25

### Добавлено
- CP-000: фундамент на SSD
- CP-001: ядро Hermes

### Безопасность
- Секреты вне Git
- gitleaks (двухфазный скан)
