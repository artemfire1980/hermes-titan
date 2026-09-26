# Hermes-Titan v7.2

Автономная инженерная платформа на Khadas VIM4 (ARM64, 8 GB) поверх Hermes Agent.

## Состояние

- **Контрольная точка:** CP-005
- **Версия:** 0.5.0
- **Хранилище:** `/mnt/ai-ssd/ai-system` (симлинк `~/ai-system`)
- **GitHub:** `artemfire1980/hermes-titan`

## Архитектура

- **Ядро:** Hermes Agent `v0.21.5+2453` (`/mnt/ai-ssd/hermes/`)
- **Модель:** FreeLLMAPI (`auto`, 1M контекст)
- **Поиск:** SearXNG (`http://127.0.0.1:8888`)
- **Telegram:** whitelist по `TELEGRAM_ALLOWED_USERS`
- **Двигатель данных:** `scripts/research-runner.py` (evidence pipeline)
- **Executive Summary:** `scripts/summary_generator.py` (Pydantic + citations)
- **Исполнитель кода:** `scripts/aider-runner.py` (изоляция через `/mnt/ai-ssd/ai-system/projects/`)

## Тесты

21 passed in 0.44s

## Документация

- `DECISIONS.md` — архитектурные решения (DEC-001…DEC-018)
- `ARCHITECTURE.md` — общая архитектура
- `docs/HERMES-CAPABILITY-MATRIX.md` — аудит возможностей ядра (CP-003)
- `docs/CODE_EDITING_RULES.md` — правила работы с кодом
- `docs/PERSONALIZATION.md` — инструкция по настройке env
- `IMPLEMENTATION_NOTES.md` — архитектура Executive Summary pipeline
- `IMPLEMENTATION_STATUS.md` — статус внедрения
- `docs/README-v1-archive.md` — документация старой системы (архив)

## Принципы

12 принципов проекта — см. `DECISIONS.md`:
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
