# DEC Index

> Автогенерируется `scripts/checks/check_dec_index.py`.
> Источник: `DECISIONS.md` (57 записей).
> **Не редактировать вручную.**

| ID | Заголовок |
|----|-----------|
| [DEC-001](../DECISIONS.md#dec-001-переустановка-начисто) | Переустановка начисто |
| [DEC-002](../DECISIONS.md#dec-002-проект-на-ssd-симлинк-в-home) | Проект на SSD, симлинк в home |
| [DEC-003](../DECISIONS.md#dec-003-ядро-в-минимальной-комплектации-blank-slate) | Ядро в минимальной комплектации (Blank Slate) |
| [DEC-004](../DECISIONS.md#dec-004-freellmapi-обязательный-компонент) | FreeLLMAPI — обязательный компонент |
| [DEC-005](../DECISIONS.md#dec-005-searxng-обязательный-компонент) | SearXNG — обязательный компонент |
| [DEC-006](../DECISIONS.md#dec-006-ctx7-в-режиме-cliskills-не-mcp) | ctx7 в режиме CLI+Skills (не MCP) |
| [DEC-007](../DECISIONS.md#dec-007-freellmapi-образ-проверка-нескольких-источников) | FreeLLMAPI образ — проверка нескольких источников |
| [DEC-008](../DECISIONS.md#dec-008-fstab-по-uuid-не-label) | fstab по UUID, не LABEL |
| [DEC-009](../DECISIONS.md#dec-009-бэкап-старой-системы-зашифрован) | Бэкап старой системы зашифрован |
| [DEC-010](../DECISIONS.md#dec-010-hermes-pm-repair-обязательный-шаг-после-установки-из-исходников) | `hermes pm repair` — обязательный шаг после установки из исходников |
| [DEC-011](../DECISIONS.md#dec-011-systemd-юнит-обновляется-через-hermes-setup-hermes-gateway-setup) | systemd-юнит обновляется через `hermes setup` / `hermes gateway setup` |
| [DEC-012](../DECISIONS.md#dec-012-pm-сам-управляет-зависимостями-платформ) | PM сам управляет зависимостями платформ |
| [DEC-013](../DECISIONS.md#dec-013-cdn-nous-403-ffmpegripgreppm-artifacts-недоступны) | CDN Nous 403 — ffmpeg/ripgrep/PM artifacts недоступны |
| [DEC-014](../DECISIONS.md#dec-014-searxng-через-docker-подключён-к-hermes) | SearXNG через Docker, подключён к Hermes |
| [DEC-015](../DECISIONS.md#dec-015-freellmapi-база-восстановлена-из-старого-freeapidb) | FreeLLMAPI база восстановлена из старого `freeapi.db` |
| [DEC-016](../DECISIONS.md#dec-016-перенос-скриптов-из-старой-системы-cp-005) | Перенос скриптов из старой системы (CP-005) |
| [DEC-017](../DECISIONS.md#dec-017-нормализация-единиц-и-токенизация-в-evidenceverifier) | Нормализация единиц и токенизация в EvidenceVerifier |
| [DEC-018](../DECISIONS.md#dec-018-conflictdict-компромисс-между-dict-api-и-атрибутным-доступом) | ConflictDict — компромисс между dict-API и атрибутным доступом |
| [DEC-019](../DECISIONS.md#dec-019-memory-limits-для-gateway) | Memory limits для gateway |
| [DEC-020](../DECISIONS.md#dec-020-aider-модель-nemotron-3-ultra-550b-a55b) | Aider модель — nemotron-3-ultra-550b-a55b |
| [DEC-021](../DECISIONS.md#dec-021-kanban-project-aider-интеграция) | Kanban + Project + Aider — интеграция |
| [DEC-022](../DECISIONS.md#dec-022-kanban-workspace-types) | Kanban workspace types |
| [DEC-023](../DECISIONS.md#dec-023-memory-provider-built-in-only) | Memory provider — built-in only |
| [DEC-024](../DECISIONS.md#dec-024-hindsight-отклонён-возврат-к-built-in) | Hindsight отклонён — возврат к built-in |
| [DEC-025](../DECISIONS.md#dec-025-memory-provider-holographic) | Memory provider — Holographic |
| [DEC-026](../DECISIONS.md#dec-026-resource-governor-блокировка-тяжёлых-задач) | Resource governor — блокировка тяжёлых задач |
| [DEC-027](../DECISIONS.md#dec-027-три-уровня-восстановления) | Три уровня восстановления |
| [DEC-028](../DECISIONS.md#dec-028-kanban-toolset-включён-native-tools) | Kanban toolset включён (native tools) |
| [DEC-029](../DECISIONS.md#dec-029-kanban-workspace-types-проверено) | Kanban workspace types — проверено |
| [DEC-030](../DECISIONS.md#dec-030-holographic-патч-автоматика-переприменения) | Holographic — патч + автоматика переприменения |
| [DEC-031](../DECISIONS.md#dec-031-holographic-восстановление-fts5-dec-030-дополнение) | Holographic — восстановление FTS5 + DEC-030 дополнение |
| [DEC-032](../DECISIONS.md#dec-032-journal-mode-wal-для-всех-баз-hermes) | journal_mode = WAL для всех баз Hermes |
| [DEC-033](../DECISIONS.md#dec-033-fallback-не-используется-freellmapi-сам-ротирует) | Fallback не используется — FreeLLMAPI сам ротирует |
| [DEC-034](../DECISIONS.md#dec-034-python-файлы-переименованы-в-underscore) | Python-файлы переименованы в underscore |
| [DEC-035](../DECISIONS.md#dec-035-cp-021-не-тегирован) | CP-021 не тегирован |
| [DEC-036](../DECISIONS.md#dec-036-holographic-hrr-требует-numpy-в-runtime-venv) | Holographic HRR требует NumPy в runtime venv |
| [DEC-037](../DECISIONS.md#dec-037-rufftoml-должен-быть-в-git-до-первого-ci-прогона) | ruff.toml должен быть в git ДО первого CI-прогона |
| [DEC-038](../DECISIONS.md#dec-038-ensure-hrr-numpy-удалён-storepy-в-патч-v3) | ensure-hrr-numpy удалён, store.py в патч v3 |
| [DEC-039](../DECISIONS.md#dec-039-upstream-pr-129521-entity-extraction) | Upstream PR #129521 — entity extraction |
| [DEC-040](../DECISIONS.md#dec-040-оптимизация-промпта-для-telegram-cp-037) | Оптимизация промпта для Telegram (CP-037) |
| [DEC-041](../DECISIONS.md#dec-041-pyyaml-в-runtime-python-для-плагинов) | PyYAML в runtime Python для плагинов |
| [DEC-042](../DECISIONS.md#dec-042-kanbanmax-in-progress-оставить-по-умолчанию) | kanban.max_in_progress — оставить по умолчанию |
| [DEC-043](../DECISIONS.md#dec-043-модуляризация-research-runnerpy-cp-036) | Модуляризация research_runner.py (CP-036) |
| [DEC-044](../DECISIONS.md#dec-044-pr-129521-статус-ожидания-ci-approve) | PR #129521 — статус ожидания CI approve |
| [DEC-045](../DECISIONS.md#dec-045-cp-036-модуляризация-research-runnerpy) | CP-036 — модуляризация research_runner.py |
| [DEC-046](../DECISIONS.md#dec-046-nemo-relay-отсутствует-штатное-состояние) | nemo_relay отсутствует — штатное состояние |
| [DEC-047](../DECISIONS.md#dec-047-единый-парсер-env-scriptsenv-utilspy) | Единый парсер .env — scripts/env_utils.py |
| [DEC-048](../DECISIONS.md#dec-048-аудит-2026-10-02-урок-про-pyc-сироты) | Аудит 2026-10-02 — урок про .pyc-сироты |
| [DEC-049](../DECISIONS.md#dec-049-web-searxng-search-exa-extract) | Web — SearXNG (search) + Exa (extract) |
| [DEC-050](../DECISIONS.md#dec-050-kanbanmax-in-progress-пересмотр-8-2) | kanban.max_in_progress — пересмотр 8 → 2 |
| [DEC-051](../DECISIONS.md#dec-051-локальный-stt-faster-whisper) | Локальный STT (faster-whisper) |
| [DEC-052](../DECISIONS.md#dec-052-runtime-venv-hermes-где-ставить-python-пакеты) | Runtime venv Hermes — где ставить Python-пакеты |
| [DEC-053](../DECISIONS.md#dec-053-kiln-mcp-3d-принтер-zav) | Kiln MCP — 3D-принтер ZAV |
| [DEC-054](../DECISIONS.md#dec-054-rubit-mcp-mail-почта-mailru) | rubit-mcp-mail — почта Mail.ru |
| [DEC-055](../DECISIONS.md#dec-055-мойсклад-mcp-отложено) | МойСклад MCP — ОТЛОЖЕНО |
| [DEC-056](../DECISIONS.md#dec-056-мойсклад-официальный-mcp) | МойСклад — официальный MCP |
| [DEC-057](../DECISIONS.md#dec-057-правила-безопасности-mcp) | Правила безопасности MCP |
