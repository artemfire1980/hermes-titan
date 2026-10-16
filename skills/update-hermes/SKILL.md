---
name: update-hermes
query: "Hermes update, обновление Hermes, hermes update, версия Hermes, v0.22.0, upgrade"
description: Check and apply Hermes Agent updates safely.
version: 0.1.0
author: Artem (artemfire1980), Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Update, Hermes, Maintenance, Upgrade, Version]
---

# Update Hermes

Check for Hermes Agent updates, report what changed, and apply them only after explicit confirmation. Handles the local patch stack (Holographic, pyproject.toml, av pin) that a naive git pull would break.

## When to Use

- User says "обнови гермес", "проверь обновления", "update hermes", "is there a new version?".
- Periodically (e.g. weekly) to catch upstream releases.
- Do NOT use for updating FreeLLMAPI, SearXNG, MCP servers, or Python packages — that is a separate concern.

## Память (Holographic) — перед ответом

При вопросах про **обновление Hermes** — **сначала** recall:

1. `recall("Hermes update")` — процедура, блокеры, ветки.
2. `recall("Hermes [тема]")` — конкретика:
   - `recall("Hermes v0.22.0")` — текущая версия, Holographic community.
   - `recall("Hermes pyproject")` — browser-harness/nemo-relay, android.
   - `recall("Hermes CDN")` — 403, обход.

**Процедура (Phase 5 в этом skill):**
1. Бэкап-ветка + push.
2. Правка pyproject.toml.
3. `git fetch --tags && git checkout vX.Y.Z`.
4. `uv lock && hermes pm install`.
5. `hermes plugins install holographic --force --yes-deps --enable`.
6. `hermes gateway restart`.

**Документация:** DEC-060 в `DECISIONS.md`.

## Prerequisites

- HERMES_HOME set (currently /mnt/ai-ssd/hermes).
- hermes CLI on PATH (from the active venv).
- Network access to api.github.com (the Nous CDN is unavailable — HTTP 403, DEC-013).
- Read access to /mnt/ai-ssd/hermes/hermes-agent (git install).

## Phases

Phases 1-4 are read-only. Phase 5 changes the system and requires explicit /update-hermes confirm.

### Phase 1 — Current state

Run via terminal:

    hermes --version
    git -C "$HERMES_HOME/hermes-agent" rev-parse HEAD
    git -C "$HERMES_HOME/hermes-agent" branch --show-current
    hermes update --plan

Completion criterion: version string, current commit, branch, and the update plan are all printed. Note any .dirty suffix (local patches present) and any carried commits.

### Phase 2 — Latest upstream release

The Nous CDN returns HTTP 403 (hermes update --check fails). Use the GitHub API instead:

    curl -s --max-time 10 "https://api.github.com/repos/NousResearch/hermes-agent/releases?per_page=3"

For the body of a specific release, replace the placeholder with a real tag:

    curl -s --max-time 10 "https://api.github.com/repos/NousResearch/hermes-agent/releases/tags/v0.21.6"

Completion criterion: latest tag, release date, and changelog body retrieved. Compare tag to the current version.

### Phase 3 — Compare with OUR-STACK

**Читай** `~/ai-system/docs/OUR-STACK.md` — инвентарь наших решений.
**Для** каждого пункта — **проверь** changelog новой версии (Phase 2) и реши:

| Метка | Что значит |
|---|---|
| ✅ **Заменяется** | Hermes добавил нативное — наше можно **убрать** |
| ⚠️ **Проверить** | Не очевидно — нужен ручной review |
| ❌ **Остаётся** | Нет замены — оставить наше |

**Сформируй отчёт:**

Что можно убрать (заменено встроенным)
[наше решение] → [встроенное Hermes, версия]
...

Что остаётся нашим
kiln MCP (74 tools) — самодельный

moysklad MCP (4 tools) — официальный

update-hermes skill
...

Что проверить вручную
voice-transcription → stt.streaming (есть ли в нашей версии?)

progressive-skill → upstream skills system

backup.sh → hermes backup

Breaking changes
...

Новые фичи Hermes (из changelog)
...

**Completion criterion:** отчёт содержит 5 секций (убрать / остаётся / проверить / breaking / новые).

**После Phase 5** (apply) — **обнови `OUR-STACK.md`**: перенеси убранное в «удалено», добавь новое.

### Phase 4 — Report

Send a summary to Telegram. No system changes yet. Use the explicit chat_id — home-channel resolution is slow and times out on this host.

    hermes send -t telegram:170690883 "Hermes update check: current <version> @ <commit>, latest <tag> (<date>). Reply /update-hermes confirm to apply."

Completion criterion: message delivered to Telegram; no files changed.

### Phase 5 — Apply (проверено 2026-10-16, v0.22.0)

Процедура:
1. Бэкап: `git checkout -b titan-pre-update-$(date +%Y%m%d)`, commit, push.
2. Правка pyproject.toml: browser-harness/nemo-relay закомментировать, environments исключить android.
3. `git fetch origin --tags && git checkout v0.22.0`
4. `uv lock && hermes pm install` — должно быть ✓ venv.
5. `hermes plugins install holographic --force --yes-deps --enable`
6. `hermes gateway restart`

Post-update:
- `hermes --version` → vX.Y.Z stable.
- `hermes plugins list | grep holographic` → enabled 0.13.0+.
- `hermes doctor` → memory provider active.
- `hermes send -t telegram:170690883 "test"` → sent.
