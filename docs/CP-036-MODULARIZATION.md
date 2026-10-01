# CP-036: Модуляризация research_runner.py

**Дата:** 2026-10-01
**Цель:** разбить монолитный `research_runner.py` (858 строк) на 12 модулей.

## Результат

| Модуль | Что содержит |
|--------|--------------|
| `research/models.py` | Evidence |
| `research/text_utils.py` | `_relevance_score`, `normalize_scope`, `normalize_geography` |
| `research/json_utils.py` | `repair_json`, `parse_json_resilient` |
| `research/config.py` | env-константы, `EXTRACT_PROMPT`, `_load_dotenv` |
| `research/checkpoint.py` | CheckpointManager |
| `research/scoring.py` | SourceQualityScorer, ConfidenceScorer |
| `research/evidence.py` | FactValidator, EvidenceVerifier, ConflictDict, ConflictDetector |
| `research/lineage.py` | detect_lineage |
| `research/llm.py` | AdaptivePacer, CircuitBreaker, LLMGateway, MODEL_CHAIN_EXTRACT |
| `research/fetch.py` | AsyncFetcher |
| `research/search.py` | TokenBucket, DEFAULT_SEARCH_CATEGORIES, AsyncSearcher |
| `research/runner.py` | DeepResearch |

**`research_runner.py`** = 97 строк (тонкий CLI + реэкспорт для обратной совместимости).

## Метод

- `auto-modularize.sh` — автоматизация через Aider (Ultra).
- Каждый шаг — отдельный коммит с pytest 42 passed.
- Aider вызывался с точечным промптом (<100 строк), не читал весь файл.

## Проблемы и решения

- **Шаг 13 сломал тесты** (удалил импорты, нужные для `from research_runner import X`).
- **13-fix:** восстановлены импорты обратной совместимости с `# pylint: disable=unused-import`.

## Итог

- 18 коммитов CP-036.
- 12 модулей + тонкий CLI.
- pytest 42 passed на каждом шаге.
- Тесты используют обратную совместимость через реэкспорт.

## Коммиты

9278fe7 CP-036 (шаг 13-fix): обратная совместимость research_runner
96f4a7b CP-036 (шаг 12b/13): модуль research.runner
9ed8ff6 CP-036 (шаг 12a/13): модуль research.config
b603c8d CP-036 (шаг 11/13): модуль research.search
05c7561 CP-036 (шаг 10/13): модуль research.fetch
dd64bf4 CP-036 (шаг 9b/13): модуль research.llm — MODEL_CHAIN_EXTRACT + LLMGateway
0b78e0d CP-036 (шаг 9a/13): модуль research.llm — AdaptivePacer + CircuitBreaker
eae51b4 CP-036 (шаг 8/13): модуль research.lineage — detect_lineage
f50994d CP-036 (шаг 7b/13): модуль research.evidence — ConflictDict + ConflictDetector
b88eb18 CP-036 (шаг 7a/13): модуль research.evidence — FactValidator + EvidenceVerifier
d0aa36d CP-036 (шаг 6b/13): модуль research.scoring — ConfidenceScorer
303d165 CP-036 (шаг 6a/13): модуль research.scoring — SourceQualityScorer
cf94288 CP-036 (шаг 5/13): модуль research.checkpoint
08809ed CP-036: auto-modularize.sh — автоматизация шагов
c5d8920 CP-036 (шаг 4/13): модуль research.config
78bcc4e CP-036 (шаг 3/13): модуль research.json_utils
4383545 CP-036 (шаг 2/13): модуль research.text_utils
152af0c CP-036 (шаг 1/13): модуль research.models
