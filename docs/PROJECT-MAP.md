# HERMES-TITAN — Project Map

> Навигационный индекс. Не документация, а «карта источников истины».
> Обновлено: 2026-10-03.

## Canonical sources

| Тема | Источник |
|------|----------|
| Архитектура | `ARCHITECTURE.md` |
| Решения | `DECISIONS.md` |
| Операции | `docs/OPERATIONS.md` |
| Структура | `docs/STRUCTURE.md` |
| User guide | `docs/USER-GUIDE.md` |
| Implementation | `IMPLEMENTATION_STATUS.md` |
| История | `CHANGELOG.md` |
| Текущее состояние | `docs/PROJECT-STATE.md` |
| Recovery | `docs/RECOVERY.md` |
| Правила кода | `docs/CODE_EDITING_RULES.md` |
| Этот файл | `docs/PROJECT-MAP.md` |

## Source-of-truth rules

1. **Runtime / code** побеждает документацию.
2. **Git** — авторитет для истории кода.
3. **DECISIONS.md** — авторитет для архитектурных решений.
4. **PROJECT-STATE.md** — авторитет для текущего состояния.
5. **CHANGELOG.md** — история, не текущее состояние.
6. **README.md** — витрина, не технический источник.
7. **MEMORY.md** не дублирует canonical documents.

## Как навигировать

| Вопрос | Куда идти |
|--------|-----------|
| Что такое проект? | `README.md` + `ARCHITECTURE.md` |
| Почему сделано так? | `DECISIONS.md` |
| Как выполнить команду? | `docs/OPERATIONS.md` |
| Где что лежит? | `docs/STRUCTURE.md` |
| Где мы сейчас? | `docs/PROJECT-STATE.md` |
| Что было недавно? | `CHANGELOG.md` секция `[Unreleased]` |
| Как восстановить? | `docs/RECOVERY.md` |

## Стек (кратко)

- **Платформа:** Khadas VIM4, ARM64, 8 GB RAM, Ubuntu 24.04.5.
- **Ядро:** Hermes Agent `v0.21.5+4925.gb4c9def` (форк Nous Research).
- **Модель:** FreeLLMAPI (Docker `127.0.0.1:3001`, `auto`, 1M ctx).
- **Поиск:** SearXNG (Docker `127.0.0.1:8888`) + Exa (`extract_backend`, DEC-049).
- **Код:** Aider с NVIDIA NIM Ultra (DEC-020), изоляция `~/ai-system/projects/`.
- **Память:** Holographic (DEC-025) + built-in MEMORY.md/USER.md.
- **Kanban:** board `hermes-titan`, dispatcher в gateway (тик 60 сек).
- **Telegram:** home chat `170690883`.

## Hard constraints

- ARM64, 8 GB RAM — не предлагать тяжёлые решения.
- Локальный-first: облака только при явной нужде.
- Секреты только в `.env` (не в git).
- Не предлагать: Kubernetes, distributed systems, тяжёлые БД, cloud-only.
- `max_in_progress` — default 8 (пересмотр — открытый вопрос).

## Ключевые пути

- HERMES_HOME: `/mnt/ai-ssd/hermes/`
- Проект: `/mnt/ai-ssd/ai-system/` (симлинк `~/ai-system`)
- Конфиг Hermes: `/mnt/ai-ssd/hermes/config.yaml`
- Секреты: `/mnt/ai-ssd/hermes/.env`
- Gateway: `hermes-gateway-469b1f3f.service` (user systemd)
