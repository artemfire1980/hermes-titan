"""Общий парсер .env для scripts/."""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


def default_candidates():
    """Стандартный список путей .env по приоритету.

    1. $HERMES_HOME/.env (основной источник, если переменная задана)
    2. /mnt/ai-ssd/hermes/.env (hardcoded для VIM4)
    3. ~/.hermes/.env
    4. ~/ai-system/.env (fallback для тестов/отладки)
    """
    from pathlib import Path as _Path

    candidates = []
    hh = os.environ.get("HERMES_HOME")
    if hh:
        candidates.append(_Path(hh) / ".env")
    candidates.append(_Path("/mnt/ai-ssd/hermes/.env"))
    candidates.append(_Path.home() / ".hermes" / ".env")
    candidates.append(_Path.home() / "ai-system" / ".env")
    return candidates


def load_env(candidates, override=False, log=None):
    """Загружает .env из первого существующего кандидата.

    candidates: iterable[Path] — порядок приоритета.
    override: False (default) — setdefault (не перезаписывать уже установленные env).
    log: logging.Logger или None — если задан, логирует источник.
    """
    for env_file in candidates:
        if not env_file.exists():
            continue
        if log:
            log.info("Loading env from: %s", env_file)
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if override:
                os.environ[k] = v
            else:
                os.environ.setdefault(k, v)
        return
    if log:
        log.warning("No .env file found in candidates: %s", [str(p) for p in candidates])
