---
name: update-stack
description: Check and apply updates for FreeLLMAPI, Hermes plugins, and MCP servers.
version: 0.1.0
author: Artem (artemfire1980), Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Update, Stack, FreeLLMAPI, Plugins, MCP, Infrastructure]
---

# Update Stack

Проверка обновлений **инфраструктуры** (not Hermes itself — see skill `update-hermes`): FreeLLMAPI Docker image, Hermes plugins, MCP servers. Показать что нового. Применять только по явному подтверждению.

## Когда использовать

- User says "обнови стек", "проверь обновления FreeLLMAPI", "update stack", "check plugins updates".
- Weekly, to catch new FreeLLMAPI releases.
- Do NOT use for updating Hermes itself — use skill `update-hermes`.

## Требования

- `docker` + `docker compose` on PATH.
- `hermes` CLI.
- `HERMES_HOME=/mnt/ai-ssd/hermes`.
- `GITHUB_TOKEN` in `/mnt/ai-ssd/hermes/.env` (for releases API).

## Фазы

Phases 1–4 read-only. Phase 5 changes the system and requires explicit `/update-stack confirm`.

### Phase 1 — Current versions

Run via `terminal`:

    # FreeLLMAPI: текущий тег образа (из docker-compose.yml) + версия из GitHub Releases
    grep -E "image:" /mnt/ai-ssd/freellmapi/docker-compose.yml
    curl -s --max-time 10 "https://api.github.com/repos/tashfeenahmed/freellmapi/releases/latest" | python3 -c "import sys,json; print('latest tag:', json.load(sys.stdin).get('tag_name'))"
    # FreeLLMAPI: локальный digest (running container) + registry digest (по тегу) — сравнить их
    docker inspect freellmapi --format '{{.Image}}'
    # Registry digest: GHCR — токен + OCI index Accept-заголовок (см. pitfall ниже)
    TOKEN=$(curl -s --max-time 10 "https://ghcr.io/token?scope=repository:tashfeenahmed/freellmapi:pull" | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))")
    curl -s --max-time 15 "https://ghcr.io/v2/tashfeenahmed/freellmapi/manifests/<TAG>" -H "Accept: application/vnd.oci.image.index.v1+json" -H "Authorization: Bearer $TOKEN" | python3 -c "
import sys,json
for m in json.load(sys.stdin).get('manifests',[]):
    p=m.get('platform',{})
    if p.get('architecture')=='arm64': print('registry arm64:', m.get('digest'))
"
    # Плагины
    hermes plugins list --json 2>&1 | python3 -c "import sys,json; [print(p['name'],p.get('version'),p.get('update_available',False)) for p in json.load(sys.stdin) if p.get('name') in ('holographic','progressive-skill')]"
    # MCP
    hermes mcp list 2>&1 | tail -10

Completion criterion: **два** digest для FreeLLMAPI (локальный + registry). Если они **совпадают** — FreeLLMAPI актуален, **даже если** changelog говорит о новой версии. Если **разные** — есть обновление.

### Phase 2 — Latest upstream

FreeLLMAPI releases (GitHub API):

    curl -s --max-time 10 "https://api.github.com/repos/tashfeenahmed/freellmapi/releases/latest"

Plugins updates:

    hermes plugins list --json 2>&1 | python3 -c "import sys,json; [print(p['name']) for p in json.load(sys.stdin) if p.get('update_available',False)]"

MCP (rubit-mcp-mail on PyPI):

    curl -s --max-time 10 "https://pypi.org/pypi/rubit-mcp-mail/json" | python3 -c "import sys,json; d=json.load(sys.stdin); print('Latest:', d['info']['version'])"

Completion criterion: latest tag for FreeLLMAPI, list of updatable plugins, latest PyPI version.

### Phase 3 — Compare with OUR-STACK

Read `~/ai-system/docs/OUR-STACK.md`. For each component:

- FreeLLMAPI: current digest vs latest tag → **обновить** / **актуально**.
- Plugins: `update_available` → **обновить** / **актуально**.
- MCP: latest PyPI version vs installed → **обновить** / **актуально**.

**Важно про Holographic:** community-плагин (не git). `hermes plugins update holographic` **не работает** (no .git). Обновление — только переустановкой:
`hermes plugins install holographic --force --yes-deps --enable`.

Completion criterion: written list per component (обновить / актуально / пропустить).

### Phase 4 — Отчёт в Telegram (на русском)

Собери отчёт **по-русски** и отправь в Telegram. Никаких изменений в системе.

**⚠️ ОБЯЗАТЕЛЬНО: все три блока (`📦 FreeLLMAPI`, `🧩 Плагины`, `🔌 MCP`) должны быть в отчёте. Не сокращать, не выбрасывать. Если данных по блоку нет — пиши `— не проверялось`. Отчёт без любого из трёх блоков считается неполным и должен быть дополнен перед отправкой.**

**⚠️ Changelog обязателен:** если есть обновление (FreeLLMAPI или плагин) — **всегда** включай `📰 Что нового` с ключевыми пунктами из GitHub Releases / PyPI. Не писать «нет данных», если они есть.

**Формат отчёта:**
🔄 Проверка обновлений стека (дата)

📦 FreeLLMAPI

· Текущая: v0.16.4 (тег в docker-compose.yml)
· Последняя: v0.16.4 (GitHub Releases)
· Статус: ✅ актуально / ⚠️ есть обновление

🧩 Плагины

· holographic 0.17.4 — ✅ актуально / ⚠️ обновить
· progressive-skill 3.2.1 — ✅ / ⚠️

🔌 MCP

· rubit-mail 1.0.0 — ✅ / ⚠️
· kiln (74 инструментов) — ✅
· moysklad (4) — ✅

📰 Что нового (если есть обновление)

· [из changelog: новые фичи, провайдеры, фиксы]

Ответь /update-stack confirm — применю обновления.

**Команда:**

    hermes send -t telegram:170690883 "$(cat <<'EOF'
🔄 Проверка обновлений стека

📦 FreeLLMAPI: <текущая> → <последняя>
🧩 Плагины: <список>
🔌 MCP: <список>

📰 Что нового:
<changelog>

Ответь /update-stack confirm — применю.
EOF
)"

Completion criterion: сообщение доставлено в Telegram, на русском языке, с версиями и changelog.

### Phase 5 — Apply

**Два режима:**
- **`/update-stack confirm`** — пошагово: применить только то, что выявлено в Phase 4, и отчитаться.
- **`/update-stack apply`** — **сразу весь цикл** (compose tag → pull → up → Phase 5.1 → docs → отчёт), без дополнительного подтверждения. Используй, когда пользователь пишет «обнови стек», «примени обновление», «сделай всё сам».


**FreeLLMAPI:**

0. **Определи new tag** из Phase 1/2 (например, `v0.16.5`). Если обновления нет — пропусти блок.
1. **Бэкап + обнови тег в `docker-compose.yml`** (иначе `pull` тянет latest, но файл остаётся старым):
       cd /mnt/ai-ssd/freellmapi
       cp -a docker-compose.yml "docker-compose.yml.bak.$(date +%Y%m%d-%H%M%S)"
       sed -i "s|freellmapi:v[0-9.]*|freellmapi:<NEW_TAG>|" docker-compose.yml
       grep -n "image:" docker-compose.yml
2. **Pull + up:**
       docker compose pull
       docker compose up -d
3. **Обнови `docs/OUR-STACK.md`** (автоматически, через скрипт):
       python3 ~/ai-system/scripts/update-ourstack.py --freellmapi <NEW_TAG>
   — если обновлялись плагины, добавь `--holographic <v>` / `--progressive <v>`.
4. **Сразу переходи к Phase 5.1 (пост-чек).**

Проверка: `docker inspect freellmapi --format '{{.Image}}'` (digest должен измениться), `curl /v1/models` (модели на месте).

**Плагины (git-based, например progressive-skill):**

    hermes plugins update <name>

**Плагины (community, например holographic):**

    hermes plugins install holographic --force --yes-deps --enable

**MCP (rubit-mail):** uvx автоматически тянет последнюю версию при следующем вызове. Ничего не делать.

**Скрипты в `~/ai-system/scripts/`:** свои, не обновляются.

### Phase 5.1 — Пост-чек (автоматически, без ручного вмешательства)

После `docker compose up -d` **сразу** выполни проверки и **включи результат в тот же Telegram-отчёт**:

    sleep 10
    docker ps --filter "name=freellmapi" --format "table {{.Image}}\t{{.Status}}"
    curl -s -o /tmp/models.json -w "http_code=%{http_code}\n" -H "Authorization: Bearer $HERMES_CUSTOM_127_0_0_1_3001_API_KEY" http://127.0.0.1:3001/v1/models
    python3 -c "import json; d=json.load(open('/tmp/models.json')); print('models:', len(d.get('data',[])))"
    docker exec freellmapi env 2>/dev/null | grep -cE "CONTEXT_HANDOFF|MODEL_ROUTING" || true
    docker logs freellmapi --since 2m 2>&1 | grep -iE "error|panic|fatal" | head -5 || echo "no errors"

**В отчёт добавь блок:**

    ✅ Пост-чек:
    · Контейнер: <Up (healthy)>
    · Модели: <N> (http <code>)
    · ENV: context_handoff=<on/off>, routing_overrides=<yes/no>
    · Ошибки в логах: <нет / список>

**Если что-то не так** (не healthy, 0 моделей, ошибки) — **сразу откат**: `docker compose down && docker compose up -d <предыдущий тег>` и сообщи в Telegram.

**После успешного пост-чека отправь в Telegram итог:**

    ✅ Обновление выполнено
    · FreeLLMAPI: <old> → <new> (healthy, N моделей)
    · compose: тег обновлён
    · docs/OUR-STACK.md: обновлён (update-ourstack.py)
    · пост-чек: OK


Completion criterion: digest изменился (если было обновление), `hermes plugins list` показывает новые версии, MCP работает, **пост-чек выполнен и включён в отчёт**.

## Чек-лист после обновления

- FreeLLMAPI: `docker ps` — `Up`, `healthy`.
- FreeLLMAPI: `curl -H "Authorization: Bearer $HERMES_CUSTOM_127_0_0_1_3001_API_KEY" http://127.0.0.1:3001/v1/models` — 262+ моделей.
- Gateway: `hermes gateway status` — running.
- Telegram: `hermes send -t telegram:170690883 "test"` — sent.
- Обновить `docs/OUR-STACK.md` — новые версии.

## Подводные камни

- **`hermes plugins update` для community-плагинов** — падает (no .git). Только `--force` переустановка.
- **FreeLLMAPI `:latest`** — плавающий тег. `docker compose pull` тянет новый digest. **Проверять digest**, а не тег.
- **GHCR manifest API** — без токена ответ 401, с токеном без подходящего `Accept` вернёт «OCI index found, but Accept header does not support OCI indexes». Бирь токен из `https://ghcr.io/token?scope=repository:tashfeenahmed/freellmapi:pull`, запрашивай `application/vnd.oci.image.index.v1+json` и фильтруй манифесты по `platform.architecture=arm64` (VIM4 — arm64).
- **`ENCRYPTION_KEY` в `.env`** — не менять (провайдерские ключи зашифрованы).
- **Volume `freellmapi-data`** — не удалять.
- **`/v1/models` требует API key** — брать из `.env`: `HERMES_CUSTOM_127_0_0_1_3001_API_KEY`.
- **`--deliver` в cron** — не использовать (баг). Скрипты сами шлют через `hermes send`.

## Проверка

- FreeLLMAPI: `docker inspect freellmapi --format '{{.Image}}'` — новый digest.
- `hermes plugins list` — версии актуальны.
- `hermes gateway status` — running.
- Telegram — сообщение доставлено.

## Быстрая справка

| Goal | Command |
|---|---|
| FreeLLMAPI digest | `docker inspect freellmapi --format '{{.Image}}'` |
| FreeLLMAPI latest | `curl -s api.github.com/repos/tashfeenahmed/freellmapi/releases/latest` |
| FreeLLMAPI registry digest | `curl ghcr.io/.../manifests/<TAG>` + `Accept: application/vnd.oci.image.index.v1+json` + bearer token, фильтр arm64 |
| Plugin updates | `hermes plugins list --json` |
| Update git plugin | `hermes plugins update <name>` |
| Reinstall community plugin | `hermes plugins install <name> --force --yes-deps --enable` |
| MCP list | `hermes mcp list` |
| rubit-mcp-mail latest | `curl -s pypi.org/pypi/rubit-mcp-mail/json` |

## Ссылки

- `docs/OUR-STACK.md` — инвентарь.
- DEC-060 — обновление Hermes v0.22.0.
- Skill `update-hermes` — Hermes сам.
