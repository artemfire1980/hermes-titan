# Hermes-Titan v7.2

Автономная инженерная платформа на Khadas VIM4 (ARM64, 8 GB) поверх Hermes Agent.

## Состояние

- **Контрольная точка:** CP-037
- **Версия:** 0.37.0
- **Хранилище:** `/mnt/ai-ssd/ai-system` (симлинк `~/ai-system`)
- **GitHub:** `artemfire1980/hermes-titan`

## Архитектура

- **Ядро:** Hermes Agent `v0.21.5+4925.gb4c9def` (`/mnt/ai-ssd/hermes/`)
- **Модель:** FreeLLMAPI `v0.13.2` (Docker `127.0.0.1:3001`, `auto`, 1M контекст)
- **Aider:** `nvidia_nim/nvidia/nemotron-3-ultra-550b-a55b`
- **Поиск:** SearXNG (Docker, 10 движков) + Exa (`extract_backend`, semantic extract)
- **Telegram:** whitelist + home channel + уведомления
- **Kanban:** board `hermes-titan` + native tools + dispatcher
- **Память:** Holographic (patch v2) + built-in + memory tool
- **Двигатель данных:** `scripts/research_runner.py` (shim) + `scripts/research/` (CP-036)
- **Executive Summary:** `scripts/summary_generator.py` (Pydantic + citations)
- **Исполнитель кода:** `scripts/aider_runner.py` (изоляция через `/mnt/ai-ssd/ai-system/projects/`)

## Документация

- **`docs/OPERATIONS.md`** — полный справочник: команды, скрипты, диагностика
- **`docs/USER-GUIDE.md`** — руководство пользователя: подключение, Telegram, сценарии, диагностика
- **`docs/PROJECT-MAP.md`** — навигация по canonical sources
- **`docs/PROJECT-STATE.md`** — текущее состояние проекта
- **`docs/STRUCTURE.md`** — карта проекта: пути, носители, компоненты
- **`DECISIONS.md`** — 50 архитектурных решений (DEC-001…DEC-050)
- **`ARCHITECTURE.md`** — общая архитектура
- **`docs/RECOVERY.md`** — три уровня восстановления

## Тесты

42 passed

Покрытие:
- `test_conflict_detector.py` (3 теста)
- `test_evidence_verifier.py` (4 теста)
- `test_research_runner.py` (8 тестов, P0-fixes)
- `test_summary_generator.py` (13 тестов)
- `test_llm_gateway.py` (6 тестов, respx)
- `test_async_fetcher.py` (8 тестов, respx)

## Документация

- `ARCHITECTURE.md` — общая архитектура
- `CHANGELOG.md` — история версий
- `IMPLEMENTATION_STATUS.md` — статус внедрения
- `IMPLEMENTATION_NOTES.md` — Executive Summary pipeline
- `docs/HERMES-CAPABILITY-MATRIX.md` — аудит возможностей ядра (CP-003)
- `docs/CODE_EDITING_RULES.md` — правила работы с кодом
- `docs/PERSONALIZATION.md` — настройка env
- `docs/RECOVERY.md` — восстановление (3 уровня)
- `docs/CHECKLIST.md` — чек-лист всех CP
- `docs/TASK-LEDGER-DECISION.md` — решение по трекеру задач
- `docs/MEMORY-BENCHMARK.md` — бенчмарк памяти (CP-008)
- `docs/CP-008-BASELINE.md` — baseline CP-008

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
