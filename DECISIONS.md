# Решения

## DEC-001: Переустановка начисто

Обоснование: накопленный долг старой системы.
Откат: расшифровать `pre-wipe-staging/vim4_golden_snapshot.7z` (архив зашифрован, пароль отдельно).

## DEC-002: Проект на SSD, симлинк в home

Обоснование: защита eMMC от переполнения.
Откат: перенести обратно.

## DEC-003: Ядро в минимальной комплектации (Blank Slate)

Обоснование: осознанное включение возможностей.
Откат: перенастроить.

## DEC-004: FreeLLMAPI — обязательный компонент

Обоснование: агрегатор бесплатных тиров с адаптивным роутингом, чего нет в штатном подборе моделей.
Откат: переключиться на штатный подбор.

## DEC-005: SearXNG — обязательный компонент

Обоснование: приватный метапоиск, штатная интеграция в Hermes.
Откат: переключиться на другой веб-бэкенд.

## DEC-006: ctx7 в режиме CLI+Skills (не MCP)

Обоснование: переиспользуем terminal tool Hermes, избегаем лишнего слоя MCP.
Откат: `ctx7 setup --mcp`.

## DEC-007: FreeLLMAPI образ — проверка нескольких источников

Обоснование: ghcr.io может не иметь ARM64 manifest.
Откат: сборка из исходников.

## DEC-008: fstab по UUID, не LABEL

Обоснование: UUID стабильнее при переименовании.
Запись: `UUID=dbf51535-... /mnt/ai-ssd ext4 defaults,noatime,nofail,x-systemd.device-timeout=10 0 2`.
Проверено: переживает ребут.

## DEC-009: Бэкап старой системы зашифрован

Обнаружено при аудите: `vim4_golden_snapshot.7z` требует пароль.
Следствие для CP-005: пароль вводится интерактивно, не хранится в проекте.

## DEC-010: `hermes pm repair` — обязательный шаг после установки из исходников

Обоснование: `pip install -e .` не ставит все зависимости в PM-окружение Hermes.
Симптом: `venv_is_current=False` → бесконечный цикл `source-update completion failed`.
Решение: `hermes pm repair` — восстанавливает committed-окружение.
Источник: issue #122425 (upstream).

## DEC-011: systemd-юнит обновляется через `hermes setup` / `hermes gateway setup`

Обоснование: после ручного создания юнита он может быть устаревшим.
Симптом: `⚠ Installed gateway service definition is outdated`.
Решение: `hermes setup` или `hermes gateway restart` — автоматически обновляют unit.

## DEC-012: PM сам управляет зависимостями платформ

Обоснование: python-telegram-bot был поставлен в venv вручную, но PM использует свой Python.
Симптом: `Platform 'Telegram' dependencies missing — attempting install...`.
Решение: PM auto-install зависимостей; не ставить пакеты в hermes-agent/venv вручную.

## DEC-013: CDN Nous 403 — ffmpeg/ripgrep/PM artifacts недоступны

Обоснование: `hermes-assets.nousresearch.com` отдаёт 403 Forbidden.
Симптом: `⚠ install out of sync (ffmpeg, ripgrep)`.
Влияние: на работу не влияет — gateway, Telegram, модель работают.
Решение: игнорировать до фикса upstream. При необходимости — ручная установка.

## DEC-014: SearXNG через Docker, подключён к Hermes

Обоснование: приватный метапоиск, штатная интеграция Hermes.
Развёртывание: `/mnt/ai-ssd/searxng/` (Docker Compose), порт `127.0.0.1:8888`.
Конфиг: `web.search_backend=searxng`, `web.searxng_url=http://127.0.0.1:8888`.
Секрет: `SEARXNG_SECRET` в `.env` (права 600).
Тест: поиск "bitcoin price today" — успешно через SearXNG.

## DEC-015: FreeLLMAPI база восстановлена из старого `freeapi.db`

Обоснование: 77 ключей провайдеров, 314 моделей — восстановлены без пересоздания.
Путь: `/mnt/ai-ssd/freellmapi/` (Docker Compose), порт `127.0.0.1:3001`.
Доступ: `https://khadas.taila31870.ts.net` (Tailscale Serve).
Ключ шифрования: `ENCRYPTION_KEY` в `.env` (права 400).

## DEC-016: Перенос скриптов из старой системы (CP-005)

Обоснование: `vim4_golden_snapshot.7z` содержал production-скрипты старой системы.
Перенесено (в `~/ai-system/scripts/`):
- `research-runner.py` — двигатель данных (evidence, dedup, conflict, circuit breaker)
- `summary_generator.py` — Executive Summary (Pydantic, citations, fallback)
- `aider-runner.py` — изолированный исполнитель кода
- `task_ledger.py` + `ledger-viewer.py` — лог запусков Aider (не конфликтует с kanban)
- `git-auto-push.sh` — auto-commit + gitleaks
- `research-telegram.sh`, `send-to-telegram.py`, `md2docx.py`
- `check-freellm-quotas.sh`, `check-memory-peak.sh`, `check_r2_budget.sh`
- `selfcheck.sh`, `backup-projects.sh`
- `sync-tasks-to-supabase.py` (Supabase перенесён по решению)
- Тесты: `tests/test_*.py` (4 файла)
- Документация: `CODE_EDITING_RULES.md`, `PERSONALIZATION.md`, `IMPLEMENTATION_NOTES.md`

Не перенесено: старые `.env`, `venv/`, `hermes-agent/`, `evals/`, `backup-projects/`.

Секреты перенесены в `/mnt/ai-ssd/hermes/.env`:
- `NVIDIA_API_KEY` (HTTP 200 — рабочий)
- `GITHUB_TOKEN` (HTTP 200)
- `SUPABASE_*` (HTTP 200)
- `AWS_*` (R2 access key 32 chars)
- `HERMES_TIMEZONE=Europe/Minsk`
- `SEARXNG_BASE_URL`, `SEARXNG_INSTANCE_URL`

`GITHUB_REPO=hermes-vim4` НЕ перенесён — у нас `hermes-titan`.

## DEC-017: Нормализация единиц и токенизация в EvidenceVerifier

Обоснование: `EvidenceVerifier` не верифицировал числовые утверждения с разными
десятичными разделителями (`22.3` vs `22,3`) и разными единицами (`млрд` vs `миллиардов`).

Симптом:
- `test_evidence_verifier_numbers`: `False, "none", 0.0` вместо `True`
- `test_evidence_verifier_fuzzy_match`: `False, "none", 0.0` вместо `True`

Решение:
- `_norm()` — нормализация десятичных разделителей (`,` → `.`)
- `UNIT_MAP` — словарь единиц (`млрд` → `миллиардов`, `млн` → `миллионов`, `тыс` → `тысяч`)
- `_tokens()` — токенизация через `re.findall(r"[a-zа-яё0-9]+")` (удаляет пунктуацию)
- Порог fuzzy понижен: `0.85 → 0.70` (числа отсекаются отдельно — риск ложных срабатываний низкий)
- Порог token_overlap: `0.70 → 0.60`, `len >= 5 → len >= 3`

Источник решения: консилиум двух ИИ (проверенные патчи).

## DEC-018: ConflictDict — компромисс между dict-API и атрибутным доступом

Обоснование: `ConflictDetector.detect()` возвращает `list[dict]`, тесты ожидают `.type`.

Симптом:
- `AttributeError: 'dict' object has no attribute 'type'`

Проверка consumers:
- Production использует только `len(conflicts)` (строка 935 `research-runner.py`)
- `.conflict_type` и `.type` в production не используются

Решение: `ConflictDict(dict)` с `__getattr__`:
- Работает как dict (`len()`, `["conflict_type"]`, JSON-сериализация)
- Даёт атрибутный доступ (`.type`, `.conflict_type`, `.divergence`)

Альтернатива (отклонена): переписать тесты на `["conflict_type"]` — теряется совместимость.


### DEC-016 дополнение: что НЕ перенесено

Осознанно НЕ перенесено из архива:
- `backup-projects/` — старые бэкапы проектов (используем `hermes backup`)
- `runtime/`, `logs/` — runtime state старой системы
- `wiki/` — была пуста
- `data/runtime.sqlite3` — runtime state
- `.aider.chat.history.md`, `.aider.input.history` — мусор Aider
- `freellmapi/`, `searxng/` — старые конфиги (у нас свои в `/mnt/ai-ssd/`)

Перенесено в архивном виде:
- `docs/README-v1-archive.md` — старая документация v3.1
- `configs/hermes/config.yaml.v1-archive` — устаревший конфиг
- `data/tasks.legacy.db` — SQLite старая база задач

## DEC-019: Memory limits для gateway

Обоснование: в архиве найден `configs/systemd/hermes-gateway-memory.conf`
с лимитами `MemoryHigh=768M`, `MemoryMax=1600M`.

Проблема: текущий gateway использует до 1.6G. Лимит 1600M — на грани OOM kill.

Решение: **не применять** этот drop-in сейчас. Файл сохранён как референс.
При необходимости ограничивать память — использовать `MemoryMax=2048M`.


### DEC-006 (уточнение после CP-006): ctx7 CLI+Skills

Установлен: `ctx7@0.5.12` (npm global, Node.js v24.21.0 LTS).

Авторизация: OAuth через `ctx7 login` → device-code flow → сохранён API-ключ.
Конфиг: `~/.config/context7/`, `~/.local/state/context7/`.

Синтаксис:
- `ctx7 library <name> [query] [--json]` — найти libraryId
- `ctx7 docs <libraryId> <query> [--json]` — получить документацию

Hermes вызывает ctx7 через terminal tool:
- Пример: `ctx7 library react "hooks"` → получить libraryId
- Затем: `ctx7 docs /reactjs/react.dev "useEffect"` → документация

MCP-интеграция **не используется** (DEC-006). `ctx7 setup --cli` **не настроен для
Claude Code / Cursor / Codex** — Hermes не в списке ctx7, но это не мешает
CLI-режиму.


## DEC-020: Aider модель — nemotron-3-ultra-550b-a55b

Обоснование: Ultra — та же архитектура, что проверенный Super, но крупнее
(550B total / 55B active). 1M контекст, 65K вывод, agentic coding + tool calling.
Работает в старой системе без YAML.

Проверено:
- curl: `enable_thinking: false` → `Hi`
- Aider без YAML: файл создаётся, коммит создаётся
- Aider с YAML: НЕ работает (extra_params.chat_template_kwargs ломает запрос)

Решение: Aider вызывается с `--model nvidia_nim/nvidia/nemotron-3-ultra-550b-a55b`
без `.aider.model.settings.yml`. Warning `Unknown context window` подавляется
флагом `--no-show-model-warnings`.

Альтернативы (на будущее): Kimi K3 (не работает из-за always-on thinking),
nemotron-3-super (работает, но меньше), deepseek-v4.1-flash (зависает).


## DEC-021: Kanban + Project + Aider — интеграция

Обоснование: полная цепочка "задача → код" работает через штатный kanban Hermes.

Архитектура:
- Board: `hermes-titan` (default workdir `/mnt/ai-ssd/ai-system/projects`)
- Project: `hermes-titan` (`p_7464919e`), привязан к board
- Dispatcher: встроен в gateway, ticks every 60s

Цепочка: Kanban task → Dispatcher → Worker (profile default) → Hermes agent
→ Terminal tool → aider-runner.py → Aider + Ultra → результат.

Проверено: задача `t_a11011c9` (создать hello.py) завершена за 26 секунд.
Worker сам создал файл, проверил через `python3 hello`, отметил задачу `done`.

ВАЖНО: `--workspace scratch` (default) — эфемерный. Для сохранения
результатов использовать `--workspace worktree:` (git worktree) или
`--workspace dir:/abs/path`.

Не нужна своя `tasks.db` — kanban покрывает всё. Своя БД — только для
git-тегов/решений/артефактов, если понадобится (отложено).


## DEC-022: Kanban workspace types

`hermes kanban create --workspace` поддерживает 4 режима:

| Режим | Описание |
|-------|----------|
| `scratch` | Эфемерная директория, удаляется после задачи (default) |
| `worktree` | Git worktree в проекте задачи (через `--project`) |
| `worktree:<path>` | Git worktree в указанном репозитории |
| `dir:<path>` | Существующая директория |

Для production-задач использовать `--workspace worktree` (сохраняет
результат в git-ветке проекта) или `--workspace dir:/abs/path`.

Для одноразовых экспериментов — `scratch` (default).

## DEC-023: Memory provider — built-in only

Обоснование: на CP-008 проверено состояние памяти.

Решение: **оставляем built-in** (`MEMORY.md` + `USER.md`) как основной
провайдер. Внешние провайдеры (honcho, mem0, openviking, retaindb,
byterover) требуют API-ключей, которых у нас нет.

Локальный `holographic` — протестируем отдельно, если понадобится.
Результат бенчмарка — в `docs/MEMORY-BENCHMARK.md`.


## DEC-024: Hindsight отклонён — возврат к built-in

Обоснование: Hindsight Cloud протестирован на VIM4, **не работает** как ожидалось.

Проблемы:
1. `hindsight_client` не подтягивается через Hermes PM — установлен вручную.
2. `fact_count: 0` — Hindsight не записывал память.
3. Local Embedded/External не работают на ARM64.
4. Конфликт с built-in — LLM предпочитает built-in.
5. `hindsight_client` удалится при следующем `hermes update` (issue #123784).

Решение: **откат к built-in only**. Hindsight полностью удалён:
- `config.yaml` — очищен от `memory.hindsight`, `plugins.disabled`.
- `.env` — удалены все `HINDSIGHT_*`.
- `$HERMES_HOME/hindsight/` — удалена.
- `plugins/hindsight/` — удалён через `hermes plugins remove`.
- `hindsight-client` — uninstall из venv.
- Bank `hermes-titan` в Hindsight Cloud — остался (можно удалить через UI).

Текущее состояние: built-in (`MEMORY.md` + `USER.md`), 7 bundled провайдеров доступны.

Следующий шаг: smoke-test **Holographic** (bundled, локальный, без ключей)
или **OpenViking** (semantic, ARM64 Docker) — по результатам теста.


## DEC-025: Memory provider — Holographic

Обоснование: Holographic прошёл smoke-test на VIM4.

Критерии выбора:
1. Bundled — переживёт `hermes update`.
2. Локальный — без ключей, без сервера.
3. ARM64 — работает.
4. Semantic recall — **5/5** через перефразированные запросы.
5. Built-in (MEMORY.md + USER.md) работает параллельно.
6. RAM/CPU — минимальные (SQLite + HRR).
7. Лицензия — MIT.

Тест (2026-09-26):
- Записано 5 фактов через Telegram.
- Gateway перезапущен.
- Задано 5 перефраз-запросов.
- **5/5 фактов найдено.**

Примеры:
- "материал для 3D-печати" → "полиамид 6 со стекловолокном" ✅
- "инструмент для кода" → "Aider" ✅
- "железо платформы" → "Khadas VIM4" ✅

Holographic использует HRR (Holographic Reduced Representations) — не vector
embedding, но ассоциативный метод. Для наших задач (парсинг, аналитика,
проекты) достаточно.

Архитектура: built-in + Holographic как один внешний provider.

Не выбраны:
- Hindsight — отклонён (DEC-024).
- OpenViking — отложен: +1 сервер, AGPL-3.0, RAM TBD. Не оправдан,
  пока Holographic справляется.
- OMEGA — не Hermes provider.
- Mastra OM — TypeScript framework.

### DEC-025 дополнение: memory toolset включён

После CP-008 обнаружено: `memory` toolset был disabled (в `agent.disabled_toolsets`).
Holographic работал как внешний provider, но агент не имел tool для явного memory_save/recall.

Решение: `hermes tools enable memory` — memory toolset включён.
Проверено: `hermes memory status` → `Memory tool: enabled ✓`.

Итог CP-008: built-in (MEMORY.md + USER.md) + Holographic (external) + memory tool (agent).

## DEC-026: Resource governor — блокировка тяжёлых задач

Обоснование: VIM4 8GB RAM. Одновременный Aider + research + gateway может
привести к OOM. Нужна защита.

Решение: `scripts/resource-governor.sh` (bash + flock).
- MAX_HEAVY=1 (по умолчанию, переопределяется env).
- Команды: `acquire <task>`, `release <task>`, `status`.
- Lock-файл: `runtime/locks/heavy.lock` (flock для атомарности).
- Проверено: acquire/release/status работают, второй acquire блокируется.

Интеграция: вызывать `acquire` перед тяжёлыми задачами (Aider, research),
`release` после. Не автоматизировано (решение человека или скрипта-обёртки).

## DEC-027: Три уровня восстановления

Уровень 1 — Чекпоинты сессии (shadow git):
- Инструмент: `hermes checkpoints` (status/prune/clear).
- Путь: `/mnt/ai-ssd/hermes/checkpoints/`.
- Назначение: откат правок агента (`/rollback`).

Уровень 2 — История проекта (git-теги CP):
- Инструмент: `git checkout CP-XXX` в `~/ai-system`.
- Назначение: откат всего проекта к контрольной точке.
- Проверено: тег `CP-009` на remote, clone работает (CP-000.5).

Уровень 3 — Полный бэкап:
- Full: `hermes backup -o <path>.zip` → zip всего HERMES_HOME (кроме кода).
- Quick: `hermes backup --quick -l <label>` → snapshot в
  `HERMES_HOME/state-snapshots/<timestamp>-<label>/`.
  ВАЖНО: `--quick` игнорирует `-o`, всегда пишет в state-snapshots.
- Восстановление full: `hermes import <path>.zip`.
- Восстановление quick: `/snapshot restore <timestamp>-<label>`.
- Наши данные: `~/ai-system/scripts/backup.sh` → tar в `backups/<timestamp>/`.

Комбинация: 1 (сессия) + 2 (проект) + 3 (ядро + наши данные).

## DEC-028: Kanban toolset включён (native tools)

Проблема: `hermes tools enable kanban` пишет в `platform_toolsets`, но gate
`_profile_has_kanban_toolset()` в старых версиях читал top-level `toolsets`.
Issue #83042 + PR #109274.

Решение (комбинация):
1. `hermes -p default tools enable kanban --platform cli`
2. `hermes -p default tools enable kanban --platform telegram`
3. `hermes -p default config set toolsets '["hermes-cli","kanban"]'` (legacy fallback)

Проверено:
- `hermes -p default chat -q "call kanban_list"` → agent вызвал kanban_list,
  получил задачу t_a11011c9 (status: done).
- `platform_toolsets.cli` и `.telegram` содержат kanban.
- top-level `toolsets` содержит kanban.

Источник: консилиум (Claude + Gemini + DeepSeek + GPT).

Осталось: проверить в Telegram (новая сессия).

Проверено в Telegram (2026-09-27):
- Бот вызвал kanban_list из Telegram-чата.
- Показал задачу t_a11011c9 (status: done).
- Полная цепочка: Telegram → Hermes → kanban_list → ответ.

DEC-028 финализирован.
