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

Check for updates of the **infrastructure layer** (not Hermes itself — see skill `update-hermes`): FreeLLMAPI Docker image, Hermes plugins, MCP servers. Show what changed. Apply only on explicit confirmation.

## When to Use

- User says "обнови стек", "проверь обновления FreeLLMAPI", "update stack", "check plugins updates".
- Weekly, to catch new FreeLLMAPI releases.
- Do NOT use for updating Hermes itself — use skill `update-hermes`.

## Prerequisites

- `docker` + `docker compose` on PATH.
- `hermes` CLI.
- `HERMES_HOME=/mnt/ai-ssd/hermes`.
- `GITHUB_TOKEN` in `/mnt/ai-ssd/hermes/.env` (for releases API).

## Phases

Phases 1–4 read-only. Phase 5 changes the system and requires explicit `/update-stack confirm`.

### Phase 1 — Current versions

Run via `terminal`:

    # FreeLLMAPI: текущий тег образа (из docker-compose.yml) + версия из GitHub Releases
    grep -E "image:" /mnt/ai-ssd/freellmapi/docker-compose.yml
    curl -s --max-time 10 "https://api.github.com/repos/tashfeenahmed/freellmapi/releases/latest" | python3 -c "import sys,json; print('latest tag:', json.load(sys.stdin).get('tag_name'))"
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

### Phase 4 — Report

Send a summary to Telegram. No system changes yet.

    hermes send -t telegram:170690883 "Stack update check: FreeLLMAPI <текущий> → <последний>, плагины: <список>, MCP: <список>. Reply /update-stack confirm to apply."

Completion criterion: message delivered; no files changed.

### Phase 5 — Apply (only on /update-stack confirm)

**FreeLLMAPI:**

    cd /mnt/ai-ssd/freellmapi
    docker compose pull
    docker compose up -d

Проверка: `docker inspect freellmapi --format '{{.Image}}'` (digest должен измениться), `curl /v1/models` (модели на месте).

**Плагины (git-based, например progressive-skill):**

    hermes plugins update <name>

**Плагины (community, например holographic):**

    hermes plugins install holographic --force --yes-deps --enable

**MCP (rubit-mail):** uvx автоматически тянет последнюю версию при следующем вызове. Ничего не делать.

**Скрипты в `~/ai-system/scripts/`:** свои, не обновляются.

Completion criterion: digest изменился (если было обновление), `hermes plugins list` показывает новые версии, MCP работает.

## Post-update checklist

- FreeLLMAPI: `docker ps` — `Up`, `healthy`.
- FreeLLMAPI: `curl -H "Authorization: Bearer $HERMES_CUSTOM_127_0_0_1_3001_API_KEY" http://127.0.0.1:3001/v1/models` — 262+ моделей.
- Gateway: `hermes gateway status` — running.
- Telegram: `hermes send -t telegram:170690883 "test"` — sent.
- Обновить `docs/OUR-STACK.md` — новые версии.

## Pitfalls

- **`hermes plugins update` для community-плагинов** — падает (no .git). Только `--force` переустановка.
- **FreeLLMAPI `:latest`** — плавающий тег. `docker compose pull` тянет новый digest. **Проверять digest**, а не тег.
- **`ENCRYPTION_KEY` в `.env`** — не менять (провайдерские ключи зашифрованы).
- **Volume `freellmapi-data`** — не удалять.
- **`/v1/models` требует API key** — брать из `.env`: `HERMES_CUSTOM_127_0_0_1_3001_API_KEY`.
- **`--deliver` в cron** — не использовать (баг). Скрипты сами шлют через `hermes send`.

## Verification

- FreeLLMAPI: `docker inspect freellmapi --format '{{.Image}}'` — новый digest.
- `hermes plugins list` — версии актуальны.
- `hermes gateway status` — running.
- Telegram — сообщение доставлено.

## Quick Reference

| Goal | Command |
|---|---|
| FreeLLMAPI digest | `docker inspect freellmapi --format '{{.Image}}'` |
| FreeLLMAPI latest | `curl -s api.github.com/repos/tashfeenahmed/freellmapi/releases/latest` |
| Plugin updates | `hermes plugins list --json` |
| Update git plugin | `hermes plugins update <name>` |
| Reinstall community plugin | `hermes plugins install <name> --force --yes-deps --enable` |
| MCP list | `hermes mcp list` |
| rubit-mcp-mail latest | `curl -s pypi.org/pypi/rubit-mcp-mail/json` |

## Ссылки

- `docs/OUR-STACK.md` — инвентарь.
- DEC-060 — обновление Hermes v0.22.0.
- Skill `update-hermes` — Hermes сам.
