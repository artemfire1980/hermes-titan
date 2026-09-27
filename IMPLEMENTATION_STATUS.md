# Статус внедрения v7.2

Версия: 0.9.0 · Контрольная точка: CP-009

## Состояние компонентов

| Компонент | Статус | Точка |
|-----------|--------|-------|
| Фундамент + защита | ✅ | CP-000 |
| Ядро Hermes (v0.21.5+2453) | ✅ | CP-001 |
| Модель через FreeLLMAPI (auto, 1M ctx) | ✅ | CP-001.4 |
| Telegram-бот | ✅ | CP-002 |
| Аудит возможностей ядра | ✅ | CP-003 |
| FreeLLMAPI (Docker, 253 модели) | ✅ | CP-004 |
| SearXNG (Docker, JSON API) | ✅ | CP-004 |
| Tailscale Serve для Dashboard | ✅ | CP-004 |
| Аудит старой системы (CP-005) | ✅ | CP-005 |
| ctx7 + Aider (CP-006) | ✅ | CP-006 |
| Kanban `hermes-titan` | ✅ | CP-007 |
| Project `hermes-titan` (`p_7464919e`) | ✅ | CP-007 |
| Интеграция Kanban→Hermes→Aider | ✅ (26s тест) | CP-007 |
| Memory provider: Holographic | ✅ (recall 5/5) | CP-008 |
| Resource governor (CP-009) | ✅ | CP-009 |
| Скрипты перенесены из бэкапа | ✅ | CP-005 |

## Не сделано

- `hermes fallback` — нет второго провайдера (отложено)
- Облачные хранилища — при доказанной нужде
- Внешний memory provider — по бенчмарку (CP-008)

## Следующие шаги


- CP-006 — ctx7 + Aider
- CP-007 — двигатель разработки (kanban)
- CP-008 — бенчмарк памяти
- CP-009 — управление ресурсами
- CP-010 — восстановление (backup + import + checkpoints)
- CP-011 — базовый уровень разработки

## Тесты

Все unit-тесты перенесённых скриптов **проходят**:

21 passed in 0.44s

Покрытие:
- `EvidenceVerifier` — 4 теста (exact, fuzzy, no_match, numbers)
- `ConflictDetector` — 3 теста (same_metric, no_conflict, time_diff)
- `ExecutiveSummaryGenerator` — 12 тестов (JSON extraction, Pydantic, citations, fallback)
- `wrapper_sidecar` — 1 тест

Исправленные баги:
- DEC-017 — нормализация единиц в `EvidenceVerifier`
- DEC-018 — `ConflictDict` для совместимости API
