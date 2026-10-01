#!/usr/bin/env python3
"""Deep Research Agent v3.0 — Production-Grade for VIM4"""

import argparse
import asyncio
import logging
import sys

from research.checkpoint import CheckpointManager

# === CONFIG ===
# _env_candidates, _load_dotenv перенесены в research.config (CP-036)
# Импорт: from research.config import _env_candidates, _load_dotenv (выше)
from research.config import (
    WORKING_DIR,
    _load_dotenv,
)

# Production-grade summary generator

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("deep-research")

_load_dotenv()


# === URL PREFILTER ===
JUNK_DOMAINS = {
    # Нерелевантные научные/образовательные сайты (часто попадают в поиск по ошибке)
    # Microsoft/Google/Apple support
    "support.microsoft.com",
    "answers.microsoft.com",
    "learn.microsoft.com",
    "support.google.com",
    "support.apple.com",
    "community.adobe.com",
    "maps.google.com",
    "google.com/maps",
    "waze.com",
    "translate.google.com",
    "informeddelivery.usps.com",
    "tools.usps.com",
    "myaccount.microsoft.com",
    "account.microsoft.com",
    "webcache.googleusercontent.com",
    "usps.com",
    "fedex.com",
    "ups.com",
    "dhl.com",
    "17track.net",
    "gdeposylka.ru",
    "reddit.com",
    "quora.com",
    "stackoverflow.com",
    "stackexchange.com",
    "facebook.com",
    "instagram.com",
    "twitter.com",
    "x.com",
    "tiktok.com",
    "pinterest.com",
    "vk.com",
    "youtube.com",
    "youtu.be",
    "vimeo.com",
    "amazon.com",
    "ebay.com",
    "aliexpress.com",
    "ozon.ru",
    "wildberries.ru",
    "avito.ru",
    "medium.com",
    "blogspot.com",
    "livejournal.com",
    "wordpress.com",
    "4pda.to",
    "otzovik.com",
    "irecommend.ru",
    "pikabu.ru",
}
JUNK_PATHS = [
    "/forum/",
    "/forums/",
    "/thread/",
    "/threads/",
    "/viewtopic",
    "/showthread",
    "/support/",
    "/help/",
    "/tracking",
    "/track/",
    "/login",
    "/signin",
    "/cart",
    "/privacy",
    "/terms",
    "/cookie",
    "/tag/",
    "/tags/",
    "/search?",
    "/community/",
    "/member/",
    "/profile/",
    "/user/",
]
JUNK_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".zip",
    ".rar",
    ".exe",
    ".mp4",
    ".mp3",
    ".docx",
    ".xlsx",
)

JUNK_DOMAIN_SUBSTRINGS = (
    "support.",
    "forum",
    "forums.",
    "board.",
    "community.",
    "translate.",
    "webcache.",
    "moodle.",
    "sso.",
    "account.microsoft",
)


# === TEXT UTILS ===
# _relevance_score, SCOPE_ALIASES, GEOGRAPHY_ALIASES,
# normalize_scope, normalize_geography перенесены в research.text_utils (CP-036)
# Импорт: from research.text_utils import ... (выше)


# === CHECKPOINT ===
# CheckpointManager перенесён в research.checkpoint (CP-036)
# Импорт: from research.checkpoint import CheckpointManager (вые)


# === SCORING ===
# SourceQualityScorer, ConfidenceScorer перенесены в research.scoring (CP-036, шаги 6a+6b)
# Импорт: from research.scoring import SourceQualityScorer, ConfidenceScorer (выше)

# === EVIDENCE ===
# FactValidator, EvidenceVerifier перенесены в research.evidence (CP-036, шаг 7a)
# ConflictDict, ConflictDetector перенесены в research.evidence (CP-036, шаг 7b)
# Импорт: from research.evidence import ConflictDetector, ConflictDict, EvidenceVerifier, FactValidator (выше)

# === JSON UTILS ===
# repair_json, parse_json_resilient перенесены в research.json_utils (CP-036)
# Импорт: from research.json_utils import repair_json, parse_json_resilient (выше)
# === LLM GATEWAY ===
# MODEL_CHAIN_EXTRACT, LLMGateway перенесены в research.llm (CP-036, шаг 9b)
# Импорт: from research.llm import AdaptivePacer, CircuitBreaker, LLMGateway, MODEL_CHAIN_EXTRACT (выше)
# Версия алгоритма extraction — при изменении инвалидирует кэш
# CACHE_VERSION = "extract-v1"  # moved to research.config
# === FETCHER ===
# AsyncFetcher перенесён в research.fetch (CP-036, шаг 10)
# Импорт: from research.fetch import AsyncFetcher (выше)

# === LINEAGE ===
# detect_lineage перенесена в research.lineage (CP-036, шаг 8)
# Импорт: from research.lineage import detect_lineage (выше)

# === LLM GATEWAY ===
# AdaptivePacer, CircuitBreaker перенесены в research.llm (CP-036, шаг 9a)
# LLMGateway перенесён в research.llm (CP-036, шаг 9b)
# Импорт: from research.llm import AdaptivePacer, CircuitBreaker, LLMGateway, MODEL_CHAIN_EXTRACT (выше)

# === SEARCH ===
# TokenBucket, DEFAULT_SEARCH_CATEGORIES, AsyncSearcher перенесены в research.search (CP-036, шаг 11)
# Импорт: from research.search import TokenBucket, DEFAULT_SEARCH_CATEGORIES, AsyncSearcher (выше)

# EXTRACT_PROMPT moved to research.config


# === DEEP RESEARCH ===
# DeepResearch перенесён в research.runner (CP-036, шаг 12b)
# Импорт: from research.runner import DeepResearch (выше)
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
