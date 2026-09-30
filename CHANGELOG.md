# История изменений

## [0.30.0] - 2026-09-30

### Добавлено
- CP-030: mock HTTP через respx (14 тестов) + persistent client в AsyncFetcher
- CP-029: чистка тестов + ruff config
- CP-028: тесты без exec() и хардкодов
- CP-027: requirements.txt / requirements-dev.txt / requirements.lock.txt
- CP-026: performance — persistent clients, CACHE_VERSION, prefilter lineage

### Изменено
- CP-031: удалён мёртвый код (~70 строк), архивы, дубликаты
- CP-016: все БД переведены в WAL
- CP-015: Holographic FTS5 recovery
- CP-014: Holographic patch v2 (on_memory_write, retrieval_count)

### Исправлено
- CP-022…CP-025: by_metric NameError, citation_number, JSON mode, system_prompt
- CP-012…CP-013: Kanban native tools + 3 workspace types
- CP-006: Aider модель Ultra (без YAML)

## [0.11.0] - 2026-09-27

### Добавлено
- CP-011: базовый уровень + CHECKLIST.md
- CP-010: восстановление (3 уровня)
- CP-009: resource governor
- CP-008: Holographic memory
- CP-007: Kanban + Aider

## [0.5.0] - 2026-09-26

### Добавлено
- CP-006: ctx7 + Aider
- CP-005: аудит старой системы
- CP-004: FreeLLMAPI + SearXNG
- CP-003: аудит возможностей ядра
- CP-002: Telegram

## [0.1.0] - 2026-09-25

### Добавлено
- CP-000: фундамент на SSD
- CP-001: ядро Hermes

### Безопасность
- Секреты вне Git
- gitleaks (двухфазный скан)
