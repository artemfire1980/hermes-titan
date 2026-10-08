---
name: update-hermes
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

### Phase 3 — Compare with local stack

Our components live in three places. Check all of them, do not assume a component is gone:

- Local skills: `$HERMES_HOME/skills/<category>/<name>/SKILL.md`
- Our scripts (git repo): `~/ai-system/scripts/`
- Skills in git repo: `~/ai-system/skills/`

For each component, run `search_files` first, then judge. A file that exists in this repo exists — never report "already removed" without an explicit not-found result.

| Component | Where to look | May be replaced by | Caveat |
|---|---|---|---|
| voice-transcription | `$HERMES_HOME/skills/media/` | `stt.streaming` (v0.21.6+) | streaming is CLI/TUI only; Telegram still needs the skill |
| task_ledger.py | `~/ai-system/scripts/` | Kanban (DEC-043) | partial migration only |
| send_to_telegram.py | `~/ai-system/scripts/` | `hermes send` | verified replacement on v0.21.5 |
| resource-governor.sh | `~/ai-system/scripts/` | `hermes pause` | NOT a replacement — pause is global emergency stop, governor is MAX_HEAVY throttle |
| progressive-skill | `$HERMES_HOME/plugins/` | `plugins.isolation: host` (v0.21.6+) | verify after update |
| rubit-mcp-mail | `hermes mcp list` | built-in mail MCP | not shipped in v0.21.6 |

Completion criterion: every row has a factual finding (path found / not found) and a recommendation (keep / replace / defer).

### Phase 4 — Report

Send a summary to Telegram. No system changes yet. Use the explicit chat_id — home-channel resolution is slow and times out on this host.

    hermes send -t telegram:170690883 "Hermes update check: current <version> @ <commit>, latest <tag> (<date>). Reply /update-hermes confirm to apply."

Completion criterion: message delivered to Telegram; no files changed.

### Phase 5 — Apply (only on /update-hermes confirm)

Run with a full backup and without prompting:

    hermes update --yes --backup

After it completes, walk the post-update checklist below.

Completion criterion: hermes --version shows the new version and every checklist item passes.

## Post-update checklist

Run each; a failing item must be reported, not silently skipped.

- Holographic patch re-applied (DEC-030): the post-merge hook runs it automatically; verify with `git -C "$HERMES_HOME/hermes-agent" diff --stat plugins/memory/holographic/`.
- PyYAML in runtime Python (DEC-041): run the runtime python3.14 and `import yaml`.
- av version is 18.1.0, not 19.x (DEC-052): run the runtime python3.14 and `import av`.
- browser-harness and nemo-relay still commented in pyproject.toml.
- code_execution disabled for Telegram: `hermes tools list --platform telegram | grep code_execution`.
- progressive-skill plugin active: `hermes plugins list | grep progressive-skill`.
- MCP whitelists unchanged: `hermes mcp list` shows kiln (74), rubit-mail (5), moysklad (4).
- Gateway running: `hermes gateway status`.

## Quick Reference

| Goal | Command |
|---|---|
| Version | hermes --version |
| Current commit | git -C "$HERMES_HOME/hermes-agent" rev-parse HEAD |
| Update plan (read-only) | hermes update --plan |
| Latest releases | curl -s api.github.com/repos/NousResearch/hermes-agent/releases |
| Check (CDN, may 403) | hermes update --check |
| Apply update | hermes update --yes --backup |
| Send to Telegram | hermes send -t telegram:170690883 "<text>" |

## Pitfalls

- hermes update --check returns HTTP 403. The Nous CDN is unreachable from this host (DEC-013). Use the GitHub API for changelogs.
- hermes update --plan does not show the target version. It only lists the current install kind and the services that will be restarted. Get the target from GitHub.
- We are on a feature branch plus a carried commit. hermes update may switch branches or stash local patches. Always pass --backup; verify the branch after update.
- .dirty in hermes --version means uncommitted patches are present. They are pyproject.toml (browser-harness / nemo-relay comments) and the Holographic plugin. If they vanish after update, re-apply via the post-merge hook or by hand.
- Do not use --keep-stash unless you intend to drop local patches permanently.
- hermes send -t telegram (without explicit chat_id) times out on this host due to slow home-channel resolution. Always pass the chat_id.

## Verification

- hermes --version reports the expected version and no unexpected .dirty flag.
- Every item in the post-update checklist passes.
- The Telegram report from Phase 4 was delivered.
- hermes gateway status shows the gateway running.
- hermes mcp list shows all three MCP servers with unchanged tool counts.
