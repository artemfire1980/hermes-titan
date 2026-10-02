# Hermes-Titan: структура проекта

> Карта по фактам на 2026-10-03. При расхождении с реальностью — приоритет у `ls` и `git ls-files`.

## 1. Носители

| Носитель | Устройство | Точка монтирования | Размер |
|----------|------------|--------------------|--------|
| eMMC | `/dev/mmcblk0p2` | `/` | 29 GB (28% занято) |
| SSD | `/dev/sda1` | `/mnt/ai-ssd` | 110 GB (4% занято) |

## 2. Ключевые пути

| Компонент | Путь | Носитель |
|-----------|------|----------|
| **HERMES_HOME** | `/mnt/ai-ssd/hermes/` | SSD |
| Ядро Hermes | `/mnt/ai-ssd/hermes/hermes-agent/` | SSD |
| venv Hermes | `/mnt/ai-ssd/hermes/hermes-agent/venv/` | SSD |
| Конфиг Hermes | `/mnt/ai-ssd/hermes/config.yaml` | SSD |
| Секреты Hermes | `/mnt/ai-ssd/hermes/.env` | SSD |
| Память | `/mnt/ai-ssd/hermes/memory_store.db` | SSD |
| Скиллы Hermes | `/mnt/ai-ssd/hermes/skills/` | SSD |
| Плагины Hermes | `/mnt/ai-ssd/hermes/plugins/` (в т.ч. `progressive-skill/`) | SSD |
| Kanban | `/mnt/ai-ssd/hermes/kanban/boards/hermes-titan/kanban.db` | SSD |
| Чекпоинты | `/mnt/ai-ssd/hermes/checkpoints/` | SSD |
| Runtime Python | `/mnt/ai-ssd/hermes/tools/python-3.14.7+.../` | SSD |
| Логи Hermes | `/mnt/ai-ssd/hermes/logs/` | SSD |
| Cron | `/mnt/ai-ssd/hermes/cron/` | SSD |
| Проект (git) | `/mnt/ai-ssd/ai-system/` | SSD |
| Симлинк | `~/ai-system` → `/mnt/ai-ssd/ai-system` | eMMC → SSD |
| Персональный env | `~/hermes-titan.env` | eMMC |
| Systemd unit | `~/.config/systemd/user/hermes-gateway-469b1f3f.service` | eMMC |
| Drop-in | `~/.config/systemd/user/hermes-gateway-469b1f3f.service.d/runtime.conf` | eMMC |
| SSH-ключи | `~/.ssh/` | eMMC |
| FreeLLMAPI | `/mnt/ai-ssd/freellmapi/` (Docker) | SSD |
| SearXNG | `/mnt/ai-ssd/searxng/` (Docker) | SSD |
| Бэкап старой системы | `/mnt/ai-ssd/pre-wipe-staging/vim4_golden_snapshot.7z` | SSD |

## 3. Структура репозитория `~/ai-system`

| Путь | Что внутри |
|------|-----------|
| `scripts/` | 21 скрипт + поддиректории (`research/`, `coding-engine/`, `data-engine/`) |
| `scripts/research/` | 12 модулей (CP-036 модуляризация) |
| `docs/` | `OPERATIONS.md`, `CHECKLIST.md`, `CODE_EDITING_RULES.md`, CP-008/009/036, HERMES-CAPABILITY-MATRIX, MEMORY-BENCHMARK, PERSONALIZATION, PROMPT-OPTIMIZATION-CP037, RECOVERY, RECOVERY-TEST-2026-10-02, TASK-LEDGER-DECISION |
| `configs/` | `hermes/.env.example`, `holographic-entities.patch`, `research/sidecar_v1.json`, `searxng/{docker-compose.yml,limiter.toml,settings.yml}`, `systemd/hermes-gateway-memory.conf` |
| `data/` | `tasks.db` (110 KB, active), `tasks.legacy.db` (36 KB) |
| `projects/` | Зона Aider: `modularize/`, `test-aider/`, `tg-persist/` |
| `skills/` | Пусто (`.gitkeep`) — наши скиллы пока не создавались |
| `tests/` | 6 тест-файлов, 42 теста |
| `backups/` | Наши бэкапы (в `.gitignore`) |
| `logs/` | Логи проекта (в `.gitignore`) |
| `runtime/` | Runtime (в `.gitignore`) |
| `.github/workflows/ci.yml` | GitHub Actions CI |
| `ruff.toml`, `pytest.ini` | Конфиги линтера и тестов |
| `requirements*.txt` | Python-зависимости |

## 4. Симлинки

- `~/ai-system` → `/mnt/ai-ssd/ai-system` (eMMC → SSD)

## 5. Что НЕ проверено

- Содержимое `scripts/coding-engine/`, `scripts/data-engine/` — предположительно пусто.
- Содержимое `/mnt/ai-ssd/hermes/backups/`, `state-snapshots/` — не смотрели.
- Архив `pre-wipe-staging/vim4_golden_snapshot.7z` — не раскрывали.

## 6. Источники

- `ls -la` по ключевым директориям
- `grep` по скриптам (кто использует `tasks.db`)
- `find` по `.github`, `configs`
- `systemctl --user list-units`
- `docker ps`, `tailscale status`, `df`, `free`
- `hermes --version`, `hermes status --all`

---

**Создан:** 2026-10-03
**Источник:** сессия валидации OPERATIONS.md + карта от пользователя
