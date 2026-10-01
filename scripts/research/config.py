"""Environment configuration for Deep Research Agent."""

from __future__ import annotations

import logging
import os
from pathlib import Path

logger = logging.getLogger("deep-research")


def _env_candidates():
    """Пути к .env в порядке приоритета."""
    candidates = []
    # 1. HERMES_HOME (основной источник — там Hermes хранит .env)
    hh = os.environ.get("HERMES_HOME")
    if hh:
        candidates.append(Path(hh) / ".env")
    # 2. /mnt/ai-ssd/hermes/.env (hardcoded для VIM4 на случай, если HERMES_HOME не выставлен)
    candidates.append(Path("/mnt/ai-ssd/hermes/.env"))
    # 3. ~/.hermes/.env (если HERMES_HOME не задан и нет симлинка)
    candidates.append(Path.home() / ".hermes" / ".env")
    # 4. Fallback: локальный .env в ai-system (для тестов/отладки)
    candidates.append(Path.home() / "ai-system" / ".env")
    return candidates


def _load_dotenv():
    """Загружает .env из первого доступного источника. Не перезаписывает уже установленные env."""
    for env_file in _env_candidates():
        if not env_file.exists():
            continue
        logger.info("Loading env from: %s", env_file)
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            os.environ.setdefault(k, v)
        return  # грузим только первый найденный
    logger.warning("No .env file found in candidates: %s", [str(p) for p in _env_candidates()])


# === CONSTANTS (moved from research_runner.py, CP-036, step 12a) ===

FREELLM_URL = os.environ.get("FREELLM_URL", "http://127.0.0.1:3001")
FREELLM_API_KEY = os.environ.get("OPENAI_API_KEY", "")
SEARXNG_URL = os.environ.get("SEARXNG_URL", "http://127.0.0.1:8888")
RESEARCH_DIR = Path(os.environ.get("RESEARCH_DIR", str(Path.home() / "research")))
REPORTS_DIR = RESEARCH_DIR / "reports"
CACHE_DIR = RESEARCH_DIR / "cache"
WORKING_DIR = RESEARCH_DIR / "working"
METRICS_FILE = RESEARCH_DIR / "metrics.jsonl"

CACHE_VERSION = "extract-v1"

EXTRACT_PROMPT = """Fact extraction specialist. Извлеки ТОЛЬКО из текста. Не придумывай.
ПОДТЕМА: {subtopic}
ДОКУМЕНТ:
{document}
Верни JSON: {{"evidences":[{{"claim":"...","metric":"market_size|market_share|production|growth_rate|other","value":12.0,"value_raw":"12 млн т","unit":"million_tonnes|USD_bn|percent","currency":null,"year":2023,"forecast_type":"historical|current|published_forecast","evidence_text":"ТОЧНАЯ цитата","market_scope":"...","geography":"...","confidence":"high|medium|low"}}]}}
Максимум 5 evidences. evidence_text=ДОСЛОВНАЯ цитата. Никаких placeholder. Пустой список если нет."""
