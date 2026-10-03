# DEC Index

> Автогенерируется `scripts/checks/check_dec_index.py`.
> Источник: `DECISIONS.md` (49 записей).
> **Не редактировать вручную.**

| ID | Заголовок |
|----|-----------|
| [DEC-001](DECISIONS.md#dec-001) | Переустановка начисто |
| [DEC-002](DECISIONS.md#dec-002) | Проект на SSD, симлинк в home |
| [DEC-003](DECISIONS.md#dec-003) | Ядро в минимальной комплектации (Blank Slate) |
| [DEC-004](DECISIONS.md#dec-004) | FreeLLMAPI — обязательный компонент |
| [DEC-005](DECISIONS.md#dec-005) | SearXNG — обязательный компонент |
| [DEC-006](DECISIONS.md#dec-006) | ctx7 в режиме CLI+Skills (не MCP) |
| [DEC-007](DECISIONS.md#dec-007) | FreeLLMAPI образ — проверка нескольких источников |
| [DEC-008](DECISIONS.md#dec-008) | fstab по UUID, не LABEL |
| [DEC-009](DECISIONS.md#dec-009) | Бэкап старой системы зашифрован |
| [DEC-010](DECISIONS.md#dec-010) | `hermes pm repair` — обязательный шаг после установки из исходников |
| [DEC-011](DECISIONS.md#dec-011) | systemd-юнит обновляется через `hermes setup` / `hermes gateway setup` |
| [DEC-012](DECISIONS.md#dec-012) | PM сам управляет зависимостями платформ |
| [DEC-013](DECISIONS.md#dec-013) | CDN Nous 403 — ffmpeg/ripgrep/PM artifacts недоступны |
| [DEC-014](DECISIONS.md#dec-014) | SearXNG через Docker, подключён к Hermes |
| [DEC-015](DECISIONS.md#dec-015) | FreeLLMAPI база восстановлена из старого `freeapi.db` |
| [DEC-016](DECISIONS.md#dec-016) | Перенос скриптов из старой системы (CP-005) |
| [DEC-017](DECISIONS.md#dec-017) | Нормализация единиц и токенизация в EvidenceVerifier |
| [DEC-018](DECISIONS.md#dec-018) | ConflictDict — компромисс между dict-API и атрибутным доступом |
| [DEC-019](DECISIONS.md#dec-019) | Memory limits для gateway |
| [DEC-020](DECISIONS.md#dec-020) | Aider модель — nemotron-3-ultra-550b-a55b |
| [DEC-021](DECISIONS.md#dec-021) | Kanban + Project + Aider — интеграция |
| [DEC-022](DECISIONS.md#dec-022) | Kanban workspace types |
| [DEC-023](DECISIONS.md#dec-023) | Memory provider — built-in only |
| [DEC-024](DECISIONS.md#dec-024) | Hindsight отклонён — возврат к built-in |
| [DEC-025](DECISIONS.md#dec-025) | Memory provider — Holographic |
| [DEC-026](DECISIONS.md#dec-026) | Resource governor — блокировка тяжёлых задач |
| [DEC-027](DECISIONS.md#dec-027) | Три уровня восстановления |
| [DEC-028](DECISIONS.md#dec-028) | Kanban toolset включён (native tools) |
| [DEC-029](DECISIONS.md#dec-029) | Kanban workspace types — проверено |
| [DEC-030](DECISIONS.md#dec-030) | Holographic — патч + автоматика переприменения |
| [DEC-031](DECISIONS.md#dec-031) | Holographic — восстановление FTS5 + DEC-030 дополнение |
| [DEC-032](DECISIONS.md#dec-032) | journal_mode = WAL для всех баз Hermes |
| [DEC-033](DECISIONS.md#dec-033) | Fallback не используется — FreeLLMAPI сам ротирует |
| [DEC-034](DECISIONS.md#dec-034) | Python-файлы переименованы в underscore |
| [DEC-035](DECISIONS.md#dec-035) | CP-021 не тегирован |
| [DEC-036](DECISIONS.md#dec-036) | Holographic HRR требует NumPy в runtime venv |
| [DEC-037](DECISIONS.md#dec-037) | ruff.toml должен быть в git ДО первого CI-прогона |
| [DEC-038](DECISIONS.md#dec-038) | ensure-hrr-numpy удалён, store.py в патч v3 |
| [DEC-039](DECISIONS.md#dec-039) | Upstream PR #129521 — entity extraction |
| [DEC-040](DECISIONS.md#dec-040) | Оптимизация промпта для Telegram (CP-037) |
| [DEC-041](DECISIONS.md#dec-041) | PyYAML в runtime Python для плагинов |
| [DEC-042](DECISIONS.md#dec-042) | kanban.max_in_progress — оставить по умолчанию |
| [DEC-043](DECISIONS.md#dec-043) | Модуляризация research_runner.py (CP-036) |
| [DEC-044](DECISIONS.md#dec-044) | PR #129521 — статус ожидания CI approve |
| [DEC-045](DECISIONS.md#dec-045) | CP-036 — модуляризация research_runner.py |
| [DEC-046](DECISIONS.md#dec-046) | nemo_relay отсутствует — штатное состояние |
| [DEC-047](DECISIONS.md#dec-047) | Единый парсер .env — scripts/env_utils.py |
| [DEC-048](DECISIONS.md#dec-048) | Аудит 2026-10-02 — урок про .pyc-сироты |
| [DEC-049](DECISIONS.md#dec-049) | Web — SearXNG (search) + Exa (extract) |
