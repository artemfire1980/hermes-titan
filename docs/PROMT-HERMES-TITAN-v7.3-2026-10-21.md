# Промт для новой сессии — HERMES-TITAN v7.4 (2026-10-27)

## Контекст

Проект **Hermes-Titan v7.3** — локальная автономная AI-платформа на **Khadas VIM4** (ARM64, 8 ГБ RAM, Ubuntu 24.04.5, ядро 5.15.137). Работаем поверх **Hermes Agent (Nous Research)**. Пользователь: **Артём** (`artemfire1980`).

**Ключевые пути:**
- `HERMES_HOME` = `/mnt/ai-ssd/hermes`
- project = `~/ai-system` (симлинк `/mnt/ai-ssd/ai-system`)
- GitHub = `github.com/artemfire1980/hermes-titan`, `origin/main` = **`bbb85a2`**
- **hermes-agent** = `/mnt/ai-ssd/hermes/hermes-agent`, ветка **`titan-v0.22.5-20261027`**, коммит **`bf0203a794a0`**
- FreeLLMAPI: Docker, `127.0.0.1:3001`, **v0.16.10**
- MCP: kiln (74), rubit-mail (5), moysklad (4)

**Активация:**
```bash
export HERMES_HOME=/mnt/ai-ssd/hermes
source "$HERMES_HOME/hermes-agent/venv/bin/activate"
cd ~/ai-system

---

## Часть 0. Актуальные версии (проверено 2026-10-21)

| Компонент | Версия | Источник |
|---|---|---|
| **Hermes Agent** | **v0.22.5** (2026.9.24) · stable · local `d923a5eb487a` | `hermes --version` |
| **Hermes ветка** | **`titan-v0.22.5-20261027`**, коммит `bf0203a794a0` | `git branch --show-current` |
| **FreeLLMAPI** | **v0.16.10** (тег `ghcr.io/tashfeenahmed/freellmapi:v0.16.10`) | `docker inspect` |
| **Holographic** | **community plugin 0.19.2** (itpartypattaya, `catalog:community@a6d00931`) | `hermes plugins list` |
| **progressive-skill** | **3.2.1** (git) | `hermes plugins list` |
| **DEC** | **DEC-001…DEC-064** | `DECISIONS.md` |
| **Holographic facts** | **73** (29 entities) | `memory_store.db` |
| **MEMORY.md** | **1134 chars** | `/mnt/ai-ssd/hermes/memories/MEMORY.md` |
| **Skills (local)** | **15** | `hermes skills list` |
| **Cron jobs** | **3** (moysklad, mail, update-stack) | `hermes cron list` |

**Важно:** `origin/main` может быть впереди `bbb85a2` — **всегда** `git fetch` + `git log --oneline -5 origin/main`.

---

## Часть 1. Как работает память (архитектура)

**Четыре слоя:**

| Слой | Где | Что | Когда |
|---|---|---|---|
| **MEMORY.md** | `/mnt/ai-ssd/hermes/memories/MEMORY.md` (**~1134 chars**) | Universal: Platform, Hard constraints, Gotchas, Kiln safety, Запрещено, маршрутизация | **Всегда** в контексте |
| **Holographic** | `memory_store.db` (**73 факта**) | Детали проектов + алгоритмы | **Recall** по ключевым словам |
| **Skills** | `HERMES_HOME/skills/` (**15 наших**) | Процедуры + алгоритмы | **Автотриггер** по `query:` |
| **docs** | `~/ai-system/docs/` | Детальная документация | Читается по необходимости |

**Правило маршрутизации** (в MEMORY.md):
запрос про проект → skill (по query) → recall(Holographic) → API (если свежее)

**Правило сессий** (в MEMORY.md):
«из предыдущего запроса», «что я спрашивал», «раньше» → recall("история сессий") → session-search-ru

---

## Часть 2. Что сделано за сессии 2026-10-16 → 2026-10-21

### 2.1. Hermes обновлён v0.22.0 → v0.22.2 (2026-10-20)

**Путь (ручной, т.к. `hermes update` на форке не видит upstream):**
1. `git fetch --tags` → `v0.22.2` = `d923a5eb48`.
2. `git checkout v0.22.2` (detached).
3. Titan-патчи в `pyproject.toml`:
   - `browser-harness==0.1.13` → закомментирован (строка ~134);
   - `nemo-relay>=0.10,<0.11` → закомментирован (строка ~216, **`]` на отдельной строке 217**);
   - `environments = [...]` → `sys_platform != 'android'` (строка ~603).
4. `uv lock` → 322 пакета, удалены `browser-harness`, `cdp-use`, `fetch-use`, `nemo-relay`.
5. `hermes pm install` → exit 0.
6. `hermes gateway restart` → running, Telegram polling OK.
7. Ветка `titan-v0.22.5-20261027`, коммит `bf0203a794a0` (+10/−96).
8. Smoke: менеджер (пример) — **273/233 (162/7/64)/40** ✅.

**Блокеры и обходы:**
- CDN Nous 403 → `git checkout <tag>` напрямую.
- `browser-harness` битый wheel → закомментирован в `pyproject.toml`.
- `nemo-relay` → закомментирован.
- `tool.uv.environments` → `sys_platform != 'android'`.
- **Holographic — community plugin** `itpartypattaya/hermes-plugin-holographic`, `memory_store.db` совместим (additive schema).
- **Русский встроен** — PR #129521 **закрыт** (2026-10-20).

### 2.2. FreeLLMAPI обновлён v0.16.5 → v0.16.10 (2026-10-20)

- Обновление через **Telegram `update-stack`** (интерактивный `/update-stack confirm` принимается из Telegram) + вручную (`sed` → `docker compose pull/up`).
- Контейнер `healthy`, `/health` 200, `restarts=0`.
- **Точка отката:** `/mnt/ai-ssd/freellmapi/docker-compose.yml.bak.20261020_104346` (v0.16.5).
- **Правило:** аварийный откат — **только по явному решению**, не автоматически.

### 2.3. Holographic — 60 фактов

**Покрытие:** Артём (persona), Hermes-TITAN (universal), Hermes update, Kiln, Запрещено, Navigation, МойСклад, Почта, Research, Voice, update-hermes, OUR-STACK, email owner, MEMORY структура, cron, Email-анализ, session_search, **Hermes v0.22.2**, **FreeLLMAPI v0.16.10**, **PR #129521 закрыт**, **Telegram update-stack**, **менеджеры (архив)**.

**Ключевые факты:** #96 (session_search trigram), #97 (email-анализ менеджера), #98 (Hermes v0.22.2), #99 (FreeLLMAPI v0.16.10), #100 (PR #129521), #101 (Telegram update-stack), #102 (менеджеры — архив).

### 2.4. Skills — 15 local

| Проект | Skills |
|---|---|
| **МойСклад** | `moysklad-workflow`, `moysklad-query`, `data-integration` |
| **Kiln** | `kiln-printer`, `kiln-analyze`, `kiln-safety` |
| **Почта** | `mail`, `email-correspondence-analyzer`, `himalaya`, `email-inbox-triage` |
| **Hermes update** | `update-hermes` |
| **Stack update** | `update-stack` |
| **Voice** | `voice-transcription` |
| **Research** | `industry-event-research`, `competitor-news-monitor` |
| **Persona** | `user-preferences-artem` |
| **Session search** | `session-search-ru` |

### 2.5. Cron — 3 jobs (все active)

| Job | Schedule | Script/Skill | Deliver |
|---|---|---|---|
| `moysklad-refresh-weekly` | `0 6 * * 1` (Пн 6:00) | `moysklad_refresh.py` | local (скрипт сам шлёт в Telegram) |
| `mail-check-daily` | `0 9 * * *` | `mail_check.py` | local (скрипт сам шлёт) |
| `update-stack-weekly` | `0 10 * * 1` (Пн 10:00) | skill `update-stack` | telegram |

**Баг `--deliver` в cron:** не работает — скрипты **сами** шлют через `hermes send`.

### 2.6. Email-анализ — «кому давно не писал»

**Данные:**
- `emails_all.json` — 18932 письма (INBOX 9253 + Sent 9679).
- `email_base.json` — **1702** контрагента с email (`/mnt/ai-ssd/hermes/cache/moysklad-audit/`).
- `analysis_overdue_v2.json` — **1661** контрагент.

**Отчёт по менеджеру (пример, 2026-10-19):** всего 418, с email **273**, >90 дней **233** (>180 **162**, 90–180 **7**, никогда **64**), действующих **40**.

### 2.7. `session_search` — обход бага с кириллицей

**Проблема:** встроенный `session_search` использует `messages_fts` (unicode61) — плохо ищет русский.
**Решение:** `session-search-ru` skill + `session_search_ru.py` — `messages_fts_trigram` (FTS5 trigram).


### 2.8. `update_docs.py` — авто-обновление версий

- Собирает факты: `hermes --version`, тег FreeLLMAPI из `docker-compose.yml`, версия Holographic из `hermes plugins list`.
- Заменяет версии в `README.md`, `IMPLEMENTATION_STATUS.md`, `docs/OUR-STACK.md`, `ARCHITECTURE.md`.
- **НЕ трогает `CHANGELOG.md`** — исторические записи.
- Коммитит + пушит. Выводит `Changed: [...]`.
- **Защита:** если `git status --short` не пуст — docs пропускается.

### 2.9. Документация (актуализирована 2026-10-21)

**Коммит `bbb85a2`:** README.md, IMPLEMENTATION_STATUS.md, OUR-STACK.md, ARCHITECTURE.md — версии v0.22.2 / v0.16.10 / 0.19.2.

| Файл | Строк |
|---|---|
| `README.md` | 100 |
| `IMPLEMENTATION_STATUS.md` | 71 |
| `DECISIONS.md` | 1369 |
| `CHANGELOG.md` | 102 |
| `ARCHITECTURE.md` | 45 |

**Новые документы:** `docs/OUR-STACK.md`, `docs/EMAIL-OVERDUE-2026-10-18.md`, `docs/EMAIL-OVERDUE-SAMSONOV-2026-10-18.md`, `docs/MEMORY-SNAPSHOT.md`, `docs/USER-SNAPSHOT.md`, **`docs/PROMT-HERMES-TITAN-v7.3-2026-10-21.md`** (этот файл).

---

## Часть 3. Что НЕ сделано (приоритеты)

### P1 — закрыто

1. ~~PR #129521~~ — **закрыт 2026-10-20** (встроено в v0.22.0+).
2. ~~Передача клиентов менеджера~~ — **отменено** (клиенты остаются как есть).

### P2 — опционально

1. **`update_docs.py`** — LLM-анализ `git log` не всегда добавляет новые секции. Тестировать на реальном diff.
2. **`session-search-ru`** — проверить через Telegram.
3. **`analyze_emails_v2.py`** — добавить `--owner` в отчёт (не только в консоль).
4. **Telegram** — сетевые проблемы (sticky IPv4 работает, но иногда timeout).

### P3 — косметика

- `voice-transcription` — устарел (STT встроен в Hermes, DEC-051).
- `.save` в `.gitignore`.
- `kiln-wrapper.sh` — shebang на 3-й строке.
- Бэкапы `docker-compose.yml.bak.*` (3 шт.) — можно почистить старые (v0.16.3).

---

## Часть 4. Как должно работать (целевая архитектура)

### Пример 1. «Сколько клиентов менеджера давно не писали?»
User → email-correspondence-analyzer (query) → recall("менеджер") → 233
**Ожидаемый ответ:** «273 с email, 233 давно не писали (162 >180, 7 90-180, 64 никогда), 40 действующих.»

### Пример 2. «Что я спрашивал про менеджера в прошлый раз?»
User → recall("история сессий") → session-search-ru → trigram FTS → сессия

### Пример 3. «Обнови стек»
User → update-stack (query) → Phase 1 (теги) → Phase 1.5 (docs) → Phase 2-4 (changelog + Telegram) → Phase 5 (apply)

### Пример 4. «Обнови Hermes»
User → update-hermes (skill) → Phase 1 (state) → Phase 2 (changelog) → Phase 3 (compare OUR-STACK) → Phase 4 (план) → Phase 5 (apply)

**⚠️ Важно:** на форк-ветке `hermes update` **не видит upstream v0.22.2** — показывает «v0.22.0». Обновление — **вручную**: `git fetch --tags` → `git checkout <tag>` → titan-патчи → `uv lock` → `pm install` → `gateway restart` → smoke.

---

## Часть 5. Как код давать (правила)

### ❌ НЕЛЬЗЯ:
- `python3 -c "..."` для сложных скриптов (**bash интерпретирует `!`, `` ` ``, `$`**).
- Вставлять markdown в терминал.
- Многострочные bash-блоки без `cat > /tmp/file << 'EOF'`.
- `docker compose config` без `--services`.
- `sudo` для Hermes.
- Править `config.yaml` вручную (только `hermes config set`).
- **Править `pyproject.toml` по номеру строки** — строки сдвигаются! Только **по шаблону** (Python find / `sed` regex).
- **`hermes memory add`** — **не существует**! Память — через `hermes chat -q "Добавь в holographic факт: ..."` (→ `fact_store`).

### ✅ МОЖНО:
- **Один блок — одна команда.**
- **Heredoc** (`cat > /tmp/file << 'EOF'`) — единственный безопасный способ для многострочных скриптов.
- **`python3 /tmp/script.py`** — если скрипт создан через heredoc.
- **`nano`** — только для markdown-документов.
- **`set -euo pipefail`** в каждом bash-скрипте.
- **Не палить секреты** — только имена переменных.

---

## Часть 6. Как ответы давать (формат)

### Перед каждым шагом:
1. **Что делаем** (одно предложение).
2. **Критерий** (как поймём, что получилось).
3. **Что может пойти не так** (1–2 риска).
4. **Команда** (блок bash/python).

### После вывода:
1. **Анализ** (что показал вывод).
2. **Проверка критерия** (получилось или нет).
3. **Следующий шаг** (только если критерий выполнен).

### Язык:
- **Русский.**
- **Коротко и по делу** (без воды).
- **Конкретика** (файлы, строки, цифры).
- **Не пересказывать** то, что уже сделано.

---

## Часть 7. Чек-лист для нового чата (проверить всё тестами)

### 7.1. Проверка состояния

```bash
export HERMES_HOME=/mnt/ai-ssd/hermes
source "$HERMES_HOME/hermes-agent/venv/bin/activate"
cd ~/ai-system

git fetch origin
git status --short
git log --oneline -5 origin/main

hermes --version
hermes gateway status 2>&1 | tail -3
hermes cron list
hermes mcp list
```

**Ожидаем:** git status пусто, origin/main `bbb85a2`+, Hermes **v0.22.5**, cron 3, MCP 3.

```bash
docker ps | grep freellmapi
docker inspect freellmapi --format '{{.Config.Image}}' 2>&1

python3 -c "import sqlite3; c=sqlite3.connect('/mnt/ai-ssd/hermes/memory_store.db').cursor(); c.execute('SELECT COUNT(*) FROM facts'); print('facts:', c.fetchone()[0]); c.execute('SELECT COUNT(*) FROM entities'); print('entities:', c.fetchone()[0])"
python3 -c "print('MEMORY.md chars:', len(open('/mnt/ai-ssd/hermes/memories/MEMORY.md').read()))"
hermes doctor 2>&1 | grep -i "MEMORY.md"
```

**Ожидаем:** FreeLLMAPI **v0.16.10**, Holographic **73 facts / 29 entities**, MEMORY.md **~1134 chars**.

### 7.2. Тест Hermes — email-анализ

```bash
hermes chat -q "Сколько клиентов менеджера с email, и сколько давно не писали?" 2>&1 | tail -10
```
**Ожидаем:** 273 / 233 (162 >180, 7 90-180, 64 никогда) / 40 действующих.

### 7.3. Тест Hermes — session_search

```bash
hermes chat -q "Что я спрашивал про менеджера в прошлый раз?" 2>&1 | tail -10
```
**Ожидаем:** ссылку на сессию + цитату.

### 7.4. Тест Hermes — update-stack

```bash
hermes chat -q "Проверь обновления стека" 2>&1 | tail -20
```
**Ожидаем:** отчёт на русском (FreeLLMAPI v0.16.10 — актуально).

### 7.5. Тест скриптов

```bash
python3 ~/ai-system/scripts/analyze_emails_v2.py --owner "Менеджер" 2>&1 | tail -5
python3 ~/ai-system/scripts/session_search_ru.py "менеджер" --limit 3 2>&1 | head -10
python3 ~/ai-system/scripts/update_docs.py 2>&1 | head -10
```
**Ожидаем:** 233/64/162/7; 3 сессии; Changed: [].

### 7.6. Проверка skills

```bash
hermes skills list 2>&1 | grep -iE "moysklad|kiln|mail|email|update|voice|session-search"
```
**Ожидаем:** 15 local skills.

### 7.7. Проверка документации

```bash
ls -la ~/ai-system/docs/ | grep -iE "our-stack|email-overdue|memory-snapshot|user-snapshot|promt"
wc -l ~/ai-system/README.md ~/ai-system/IMPLEMENTATION_STATUS.md ~/ai-system/DECISIONS.md ~/ai-system/CHANGELOG.md ~/ai-system/ARCHITECTURE.md
```
**Ожидаем:** 5+ docs на месте, строки 100/71/1369/102/45.

---

## Часть 8. Что делать в новом чате (первые шаги)

1. **Активировать окружение** (Часть 7.1).
2. **Прогнать все тесты** (Часть 7.1–7.7) — понять, что работает, что сломано.
3. **Спросить пользователя** — какую задачу решаем.
4. **Если что-то сломано** — починить (по отчёту тестов).
5. **Продолжить** с P2/P3 (Часть 3).

**Рекомендация:** начать с **P2 — `update_docs.py` LLM-анализ** (тест на реальном diff) и **`--owner` в отчёт `analyze_emails_v2.py`**. P3 — косметика.

---

## Часть 9. Ключевые файлы (для справки)

| Файл | Что |
|---|---|
| `/mnt/ai-ssd/hermes/memories/MEMORY.md` | Universal память (~1134 chars) |
| `/mnt/ai-ssd/hermes/memory_store.db` | Holographic (~60 фактов) |
| `~/ai-system/docs/OUR-STACK.md` | Инвентарь |
| `~/ai-system/docs/EMAIL-OVERDUE-2026-10-18.md` | Общий отчёт |
| `~/ai-system/docs/MEMORY-SNAPSHOT.md`, `USER-SNAPSHOT.md` | Снимки памяти |
| `~/ai-system/docs/PROMT-HERMES-TITAN-v7.3-2026-10-21.md` | **Этот промт** |
| `~/ai-system/scripts/moysklad_refresh.py` | Cron: email_base.json (1702) |
| `~/ai-system/scripts/mail_check.py` | Cron: почта (unread) |
| `~/ai-system/scripts/analyze_emails_v2.py` | Email-анализ с `--owner` |
| `~/ai-system/scripts/session_search_ru.py` | Trigram FTS для кириллицы |
| `~/ai-system/scripts/update_docs.py` | Авто-обновление docs (версии) |
| `~/ai-system/scripts/sync-cron-scripts.sh` | Синхронизация скриптов в HERMES_HOME |
| `/mnt/ai-ssd/hermes/skills/devops/update-stack/SKILL.md` | Phase 1 (теги), Phase 1.5 (docs), Phase 2–5 |
| `/mnt/ai-ssd/hermes/skills/devops/update-hermes/SKILL.md` | 5 фаз + Phase 3 (OUR-STACK) |
| `/mnt/ai-ssd/hermes/config.yaml` | Конфиг Hermes (v0.22.2, reasoning_effort: low) |
| `/mnt/ai-ssd/freellmapi/docker-compose.yml` | FreeLLMAPI v0.16.10 (фиксированный тег) |

---

## Часть 10. Известные баги и особенности

1. **--deliver в cron** — не работает. Скрипты сами шлют через hermes send.
2. **session_search (встроенный)** — плохо ищет кириллицу. Для русского — session-search-ru (trigram).
3. **hermes config get agent.reasoning_effort** — warning, но читается из config.yaml.
4. **Telegram** — сетевые проблемы (ConnectError), sticky IPv4 работает.
5. **docker-compose.yml** — не git-репо, бэкап docker-compose.yml.bak.*.

6. **FreeLLMAPI :latest** — не использовать, только фиксированный тег v0.16.10.
7. **hermes plugins update для community-плагинов** — падает (no .git). Только --force переустановка.
8. **hermes plugins list в одиночном режиме** — может требовать подтверждения. Использовать grep без --json.
9. **prompt-size** завышает skills index (54 vs 35) — не критично.
10. **code_execution** возвращается после hermes pm install — отключать снова.

11. **pyproject.toml** — хрупкая правка. Правки — только по шаблону, не по номеру строки!
12. **update_docs.py** — только версии (LLM в Phase 1.5 — git log, но не всегда добавляет секции).
13. **trailing-whitespace** — может изменить файл после git add, коммит упадёт. git add + git commit снова.
14. **hermes memory add** — не существует. Память — через hermes chat -q "Добавь в holographic факт: ..." (→ fact_store).

15. **hermes update на форк-ветке** — не видит upstream. Обновление — вручную: git fetch --tags → git checkout <tag> → патчи → uv lock → pm install → gateway restart → smoke.
16. **Аварийный откат FreeLLMAPI** — только по явному решению, не автоматически.
17. **Telegram-бот может «соврать»** про обновление. Верить только hermes --version в CLI.
18. **Правки pyproject.toml по номеру строки опасны** — строки сдвигаются. Только по шаблону.

---

## Часть 11. Правила работы (все в силе)

- **NO CONFIG GUESSING** — сначала --help, потом действие.
- **Источник истины** — --help > официальная документация > GitHub API > план.
- **Один блок — одна команда.**
- **Markdown — только через nano или heredoc.**
- **set -euo pipefail** в bash.
- **Не палить секреты** — только имена переменных.
- **docker compose config** без --services — нельзя.

- **Не использовать sudo для Hermes.**
- **Не править config.yaml вручную** — только hermes config set.
- **Не хардкодить версии.**
- **Не публиковать наружу** (только Tailscale).
- **Не коммитить секреты.**
- **Pre-commit workflow:** если git commit упал на ruff-format/end-of-file-fixer/trailing-whitespace — git add + git commit снова. Норма.
- **Heredoc** (cat > file << 'EOF') — для коротких блоков; для длинных — python3 -c с тройными кавычками.

- **python3 -c "..."** — не использовать для сложных скриптов.
- **Правки pyproject.toml — только по шаблону**, не по номеру строки.
- **hermes memory add не существует** — через hermes chat -q "Добавь в holographic факт: ...".
- **Аварийный откат FreeLLMAPI — только по явному решению.**
- **Telegram-боту не верить** насчёт обновлений — только hermes --version.

---

**Начни с Части 7 (тесты).** Прогони всё, что работает, что сломано. Потом — спроси пользователя, какую задачу решаем. **Не перескакивать шаги.**

## Часть 12. Скрипты импорта клиентов (2026-10-27)

Созданы и запушены в git (коммит `bbb85a2`):
- `scripts/final_importer.py` — умный импорт клиентов (поиск дублей + создание).
- `scripts/check_duplicates_bulk.py` — проверка дублей без создания.
- `scripts/create_clients.py` — создание одного клиента (с выбором менеджера).
- `scripts/moysklad_mcp.py` — локальный MCP-сервер (не используется).

**Правила:**
- Названия транслитерируются в кириллицу (закон РФ).
- Статус "в разработке" (ID: `21798e98-bca2-11e3-47b6-002590a28eca`).
- Теги: `["глазури", "самсонов"]` или `["глазури", "хапанков"]`.
- Владелец определяется токеном: `MOYSKLAD_TOKEN` (Самсонов) или `MOYSKLAD_TOKEN_HAPANKOV` (Хапанков).
- Описание из колонки G записывается в заметку (событие).

**Известные проблемы:**
- Дубль Holographic в `hermes plugins list` (git + catalog) — косметический баг, игнорируем.
- `pm install` может падать на баге `uv 0.12.x` (Invalid Wheel-Version) — обходим через `pip`.
