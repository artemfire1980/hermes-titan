#!/usr/bin/env python3
"""Deep Research Agent v3.0 — Production-Grade for VIM4"""

import argparse
import asyncio
import logging
import sys

from research.checkpoint import CheckpointManager

# === CONFIG ===
from research.config import (
    WORKING_DIR,
    _load_dotenv,
)

# Импорты для обратной совместимости с тестами
# (тесты используют `from research_runner import X` и `rr.X`)
# pylint: disable=unused-import

# Production-grade summary generator

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("deep-research")

_load_dotenv()


# === CHECKPOINT ===
# CheckpointManager перенесён в research.checkpoint (CP-036)

# === SCORING ===
# SourceQualityScorer, ConfidenceScorer перенесены в research.scoring (CP-036, шаги 6a+6b)

# === EVIDENCE ===
# FactValidator, EvidenceVerifier перенесены в research.evidence (CP-036, шаг 7a)
# ConflictDict, ConflictDetector перенесены в research.evidence (CP-036, шаг 7b)

# === JSON UTILS ===
# repair_json, parse_json_resilient перенесены в research.json_utils (CP-036)

# === LLM GATEWAY ===
# MODEL_CHAIN_EXTRACT, LLMGateway перенесены в research.llm (CP-036, шаг 9b)
# CACHE_VERSION = "extract-v1"  # moved to research.config

# === FETCHER ===
# AsyncFetcher перенесён в research.fetch (CP-036, шаг 10)

# === LINEAGE ===
# detect_lineage перенесена в research.lineage (CP-036, шаг 8)

# === SEARCH ===
# TokenBucket, DEFAULT_SEARCH_CATEGORIES, AsyncSearcher перенесены в research.search (CP-036, шаг 11)

# EXTRACT_PROMPT moved to research.config


# === DEEP RESEARCH ===
from research.runner import DeepResearch


def main():
    ap = argparse.ArgumentParser(description="Deep Research Agent v3.0")
    ap.add_argument("--topic", required=False)
    ap.add_argument("--depth", type=int, default=3)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--resume", metavar="ID")
    args = ap.parse_args()
    if args.resume:
        ckpt = CheckpointManager(WORKING_DIR)
        s = ckpt.load(args.resume)
        if not s:
            print(f"No checkpoint: {args.resume}", file=sys.stderr)
            sys.exit(1)
        agent = DeepResearch(s["topic"], s.get("depth", 3))
        agent.rid = args.resume
    else:
        if not args.topic:
            print("--topic required", file=sys.stderr)
            sys.exit(1)
        agent = DeepResearch(args.topic, args.depth)

    async def _run_and_close():
        try:
            await agent.run(dry_run=args.dry_run)
        finally:
            await agent.aclose()

    try:
        asyncio.run(_run_and_close())
    except KeyboardInterrupt:
        agent.save_ckpt()
        print(f"\nInterrupted. Resume: --resume {agent.rid}")


if __name__ == "__main__":
    main()
