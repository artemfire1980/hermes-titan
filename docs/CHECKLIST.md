# Чек-лист внедрения v7.2

Финальная проверка всех контрольных точек. Дата: 2026-09-27.

## CP-000 — Фундамент

- [x] Структура на SSD (`/mnt/ai-ssd/ai-system`, симлинк `~/ai-system`)
- [x] `.gitignore` с защитой секретов
- [x] Документация (README, ARCHITECTURE, DECISIONS, CHANGELOG)
- [x] gitleaks (рабочее дерево + история)
- [x] Тег `CP-000` на GitHub

## CP-001 — Ядро Hermes

- [x] Установка из исходников на SSD (`HERMES_HOME=/mnt/ai-ssd/hermes`)
- [x] FreeLLMAPI как custom provider (auto, 1M ctx)
- [x] Тестовый диалог CLI
- [x] Тег `CP-001` (ретро)

## CP-002 — Telegram

- [x] python-telegram-bot через PM
- [x] `.env` с токеном + whitelist
- [x] systemd user service `hermes-gateway-*`
- [x] Linger включён
- [x] Бот отвечает разрешённому, игнорирует остальных
- [x] Home channel установлен
- [x] Тег `CP-002`

## CP-003 — Аудит возможностей

- [x] `docs/HERMES-CAPABILITY-MATRIX.md`
- [x] Изменения в план v7.2 зафиксированы
- [x] Тег `CP-003`

## CP-004 — FreeLLMAPI + SearXNG

- [x] FreeLLMAPI (Docker, 77 ключей, 314 моделей)
- [x] SearXNG (Docker, JSON API)
- [x] Tailscale Serve для Dashboard
- [x] `web.search_backend=searxng`
- [x] Тест поиска через SearXNG
- [x] Тег `CP-004`

## CP-005 — Аудит старой системы

- [x] Распаковка `vim4_golden_snapshot.7z`
- [x] Перенос 16 скриптов + 4 теста + docs
- [x] Секреты перенесены в `HERMES_HOME/.env`
- [x] gitleaks
- [x] Уборка архива
- [x] Тег `CP-005`

## CP-006 — ctx7 + Aider

- [x] Node.js v24.21.0 LTS
- [x] ctx7 0.5.12 (CLI+Skills, DEC-006)
- [x] Aider 0.86.2 через pipx
- [x] `aider-runner.py` с Ultra
- [x] Тест: hello.py + goodbye.py созданы
- [x] Тег `CP-006`

## CP-007 — Двигатель разработки

- [x] Kanban board `hermes-titan`
- [x] Project `hermes-titan` + bind-board
- [x] Dispatcher в gateway
- [x] Интеграция: task → worker → Aider (26s тест)
- [x] DEC-021 (kanban) + DEC-022 (workspace)
- [x] Тег `CP-007`

## CP-008 — Память

- [x] Holographic (bundled, local)
- [x] Smoke-test 5/5 перефраз
- [x] Memory tool включён
- [x] DEC-024 (Hindsight отклонён) + DEC-025 (Holographic)
- [x] Тег `CP-008`

## CP-009 — Управление ресурсами

- [x] `scripts/resource-governor.sh`
- [x] MAX_HEAVY=1, flock
- [x] Тест: acquire / release / блокировка
- [x] DEC-026
- [x] Тег `CP-009`

## CP-010 — Восстановление

- [x] `scripts/backup.sh` (наши данные)
- [x] `hermes backup` full + quick
- [x] `docs/RECOVERY.md`
- [x] Тест восстановления (git clone)
- [x] DEC-027
- [x] Тег `CP-010`

## CP-011 — Базовый уровень

- [x] Все 21 unit-тест проходят
- [x] `IMPLEMENTATION_STATUS.md` актуальный
- [x] `docs/CHECKLIST.md` (этот файл)
- [x] Тест восстановления пройден
- [x] Тег `CP-011`

## Правила проекта (12 принципов)

- [x] Hermes-first
- [x] Discover-before-build
- [x] Reuse-before-build
- [x] Proof-before-install
- [x] No config guessing
- [x] Cloud-backed, local-execution
- [x] Telegram-first
- [x] Aider isolation (`/mnt/ai-ssd/ai-system/projects/`)
- [x] Mandatory recovery
- [x] Checkpoint-after-proof
- [x] Official-binary-first
- [x] Minimal-surface

## Отложено (не критично)

- `hermes fallback` — нет второго провайдера
- Облачные хранилища (Supabase/R2) — при доказанной нужде
- OpenViking memory provider — отложен
- `hermes tools enable kanban` — agent tools для kanban (сейчас через CLI)
