# Hermes-Titan v7.2

Автономная инженерная платформа на Khadas VIM4 (ARM64, 8 GB) поверх Hermes Agent.

## Состояние

- **Контрольная точка:** DEC-060
- **Версия:** v0.22.0
- **Хранилище:** `/mnt/ai-ssd/ai-system` (симлинк `~/ai-system`)
- **GitHub:** `artemfire1980/hermes-titan`

## Архитектура

- **Ядро:** Hermes Agent `v0.22.0+1.g494038c` (`/mnt/ai-ssd/hermes/`)
- **Модель:** FreeLLMAPI `v0.16.7` (Docker `127.0.0.1:3001`, `auto`, 1M контекст)
- **Aider:** `nvidia_nim/nvidia/nemotron-3-ultra-550b-a55b`
- **Поиск:** SearXNG (Docker, 10 движков) + Exa (`extract_backend`, semantic extract)
- **Telegram:** whitelist + home channel + уведомления
- **Kanban:** board `hermes-titan` + native tools + dispatcher
- **Память:** Holographic community 0.17.7 + built-in + memory tool
- **Двигатель данных:** `scripts/research_runner.py` (shim) + `scripts/research/` (CP-036)
- **Executive Summary:** `scripts/summary_generator.py` (Pydantic + citations)
- **Исполнитель кода:** `scripts/aider_runner.py` (изоляция через `/mnt/ai-ssd/ai-system/projects/`)

## Автоматизация (cron)

| Job | Schedule | Что |
|---|---|---|
| `moysklad-refresh-weekly` | Пн 6:00 | email_base.json из МойСклад (1701 контрагент с email) |
| `mail-check-daily` | 9:00 | непрочитанные в INBOX Mail.ru → Telegram |
| `update-stack-weekly` | Пн 10:00 | changelog FreeLLMAPI/плагины/MCP → Telegram (на русском) |

**Скрипты:** `scripts/moysklad_refresh.py`, `scripts/mail_check.py`, `scripts/sync-cron-scripts.sh`.

## Skills (15 local)

- **МойСклад** (3): `moysklad-workflow`, `moysklad-query`, `data-integration`.
- **Kiln** (3): `kiln-printer`, `kiln-analyze`, `kiln-safety`.
- **Почта** (4): `mail`, `email-correspondence-analyzer`, `himalaya`, `email-inbox-triage`.
- **Обновление** (2): `update-hermes`, `update-stack`.
- **История** (1): `session-search-ru` (trigram FTS для кириллицы).
- **Voice** (1): `voice-transcription`.
- **Research** (2): `industry-event-research`, `competitor-news-monitor`.
- **Персона** (1): `user-preferences-artem`.

## Документация

- **`docs/OPERATIONS.md`** — полный справочник: команды, скрипты, диагностика
- **`docs/USER-GUIDE.md`** — руководство пользователя: подключение, Telegram, сценарии, диагностика
- **`docs/PROJECT-MAP.md`** — навигация по canonical sources
- **`docs/PROJECT-STATE.md`** — текущее состояние проекта
- **`docs/MAINTENANCE.md`** — как поддерживать документацию, память и CI
- **`docs/WORKFLOW.md`** — workflow автономного внедрения (Telegram → Hermes → Aider → git)
- **`docs/INTEGRATIONS.md`** — внешние интеграции (MCP: почта, CRM, 3D-принтер)
- **`docs/KILN.md`** — 3D-принтер через Kiln MCP (71 read-tool)
- **`docs/MAIL.md`** — почта Mail.ru (read-only)
- **`docs/MOYSKLAD.md`** — CRM (МойСклад, read-only, DEC-056)
- **`docs/PRINTER-CONFIG.md`** — конфиг принтера ZAV
- **`docs/SECURITY.md`** — правила безопасности MCP
- **`docs/STRUCTURE.md`** — карта проекта: пути, носители, компоненты
- **`DECISIONS.md`** — 60 архитектурных решений (DEC-001…DEC-060)
- **`ARCHITECTURE.md`** — общая архитектура
- **`docs/RECOVERY.md`** — три уровня восстановления
- **`CHANGELOG.md`** — история версий
- **`IMPLEMENTATION_STATUS.md`** — статус внедрения
- **`IMPLEMENTATION_NOTES.md`** — Executive Summary pipeline
- **`docs/HERMES-CAPABILITY-MATRIX.md`** — аудит возможностей ядра (CP-003)
- **`docs/CODE_EDITING_RULES.md`** — правила работы с кодом
- **`docs/PERSONALIZATION.md`** — настройка env
- **`docs/CHECKLIST.md`** — чек-лист всех CP
- **`docs/TASK-LEDGER-DECISION.md`** — решение по трекеру задач
- **`docs/MEMORY-BENCHMARK.md`** — бенчмарк памяти (CP-008)
- **`docs/CP-008-BASELINE.md`** — baseline CP-008

## Тесты

42 passed

Покрытие:
- `test_conflict_detector.py` (3 теста)
- `test_evidence_verifier.py` (4 теста)
- `test_research_runner.py` (8 тестов, P0-fixes)
- `test_summary_generator.py` (13 тестов)
- `test_llm_gateway.py` (6 тестов, respx)
- `test_async_fetcher.py` (8 тестов, respx)

## Принципы (12)

1. Hermes-first
2. Discover-before-build
3. Reuse-before-build
4. Proof-before-install
5. No config guessing
6. Cloud-backed, local-execution
7. Telegram-first
8. Aider isolation
9. Mandatory recovery
10. Checkpoint-after-proof
11. Official-binary-first
12. Minimal-surface
