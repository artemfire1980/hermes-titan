#!/usr/bin/env python3
"""Deep Research Agent v3.0 — Production-Grade for VIM4"""

import argparse
import asyncio
import hashlib
import json
import logging
import os
import random
import re
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from difflib import SequenceMatcher
from pathlib import Path

import httpx
from research.checkpoint import CheckpointManager

# === CONFIG ===
# _env_candidates, _load_dotenv перенесены в research.config (CP-036)
# Импорт: from research.config import _env_candidates, _load_dotenv (выше)
from research.config import _load_dotenv
from research.json_utils import parse_json_resilient
from research.models import Evidence
from research.scoring import ConfidenceScorer, SourceQualityScorer
from research.text_utils import (
    _relevance_score,
    normalize_geography,
    normalize_scope,
)

# Production-grade summary generator
from summary_generator import ExecutiveSummaryGenerator, SummaryConfig

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("deep-research")

_load_dotenv()

FREELLM_URL = os.environ.get("FREELLM_URL", "http://127.0.0.1:3001")
FREELLM_API_KEY = os.environ.get("OPENAI_API_KEY", "")
SEARXNG_URL = os.environ.get("SEARXNG_URL", "http://127.0.0.1:8888")
RESEARCH_DIR = Path(os.environ.get("RESEARCH_DIR", str(Path.home() / "research")))
REPORTS_DIR = RESEARCH_DIR / "reports"
CACHE_DIR = RESEARCH_DIR / "cache"
WORKING_DIR = RESEARCH_DIR / "working"
METRICS_FILE = RESEARCH_DIR / "metrics.jsonl"

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
# ConflictDict, ConflictDetector пока остаются (шаг 7b)
# Импорт: from research.evidence import FactValidator, EvidenceVerifier (выше)
from research.evidence import EvidenceVerifier, FactValidator


class ConflictDict(dict):
    """Dict с атрибутным доступом — совместимость с .type и ["conflict_type"]."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)


class ConflictDetector:
    @classmethod
    def detect(cls, evidences):
        groups = defaultdict(list)
        for e in evidences:
            if e.value is None or not e.metric:
                continue
            # Убираем scope из ключа - он уже нормализован через aliases
            key = (e.metric, normalize_geography(e.geography), e.unit, e.currency)
            groups[key].append(e)
        conflicts = []
        for key, grp in groups.items():
            if len(grp) < 2:
                continue
            vals = [e.value for e in grp]
            mn, mx = min(vals), max(vals)
            if mn == 0:
                continue
            div = (mx - mn) / mn
            stypes = {e.source_type for e in grp}
            years = {e.year for e in grp if e.year}
            scopes = {e.market_scope for e in grp}
            if len(years) > 1:
                ct, th = "TIME_DIFF", 0.30
            elif len(scopes) > 1:
                ct, th = "SCOPE_DIFF", 0.30
            elif len(stypes) > 1:
                ct, th = "METHODOLOGY_DIFF", 0.25
            else:
                ct, th = "DIRECT_CONFLICT", 0.15
            if div > th:
                conflicts.append(
                    ConflictDict(
                        {
                            "metric_key": [str(k) for k in key],
                            "conflict_type": ct,
                            "type": ct,
                            "divergence": round(div, 3),
                            "threshold": th,
                            "evidences": [
                                {
                                    "evidence_id": e.evidence_id,
                                    "value": e.value,
                                    "value_raw": e.value_raw,
                                    "source_url": e.source_url,
                                    "source_type": e.source_type,
                                    "year": e.year,
                                }
                                for e in grp
                            ],
                            "resolution_hint": {
                                "DIRECT_CONFLICT": "report both",
                                "METHODOLOGY_DIFF": "explain methodology",
                                "SCOPE_DIFF": "clarify scope",
                                "TIME_DIFF": "note time diff",
                            }.get(ct, "report both"),
                        }
                    )
                )
        return conflicts


# === ADAPTIVE PACER (AIMD) ===
class AdaptivePacer:
    def __init__(self, min_interval=2.0, max_interval=15.0, start_interval=5.0):
        self.min_interval = min_interval
        self.max_interval = max_interval
        self.interval = start_interval
        self._lock = asyncio.Lock()
        self._next_allowed = 0.0

    async def wait_turn(self):
        async with self._lock:
            now = time.monotonic()
            if now < self._next_allowed:
                delay = self._next_allowed - now
                logger.debug("pacer: sleeping %.1fs (interval=%.1fs)", delay, self.interval)
                await asyncio.sleep(delay)
            jitter = self.interval * random.uniform(-0.15, 0.15)
            self._next_allowed = time.monotonic() + self.interval + jitter

    def on_success(self):
        self.interval = max(self.min_interval, self.interval * 0.9)

    def on_throttle(self):
        self.interval = min(self.max_interval, self.interval * 2.0)
        logger.warning("pacer: throttled -> interval=%.1fs", self.interval)

    def on_server_error(self):
        self.interval = min(self.max_interval, self.interval * 1.5)


# === CIRCUIT BREAKER ===
class CircuitBreaker:
    def __init__(self, threshold=5, timeout=30.0):
        self.threshold = threshold
        self.timeout = timeout
        self.failures = 0
        self.state = "closed"
        self.opened_at = 0.0

    def allow(self):
        if self.state == "closed":
            return True
        if self.state == "open":
            if time.monotonic() - self.opened_at >= self.timeout:
                self.state = "half_open"
                logger.info("circuit breaker: half_open")
                return True
            return False
        return True

    def record_success(self):
        if self.state == "half_open":
            logger.info("circuit breaker: closed")
        self.failures = 0
        self.state = "closed"

    def record_failure(self):
        self.failures += 1
        if self.state == "half_open" or self.failures >= self.threshold:
            self.state = "open"
            self.opened_at = time.monotonic()
            logger.warning("circuit breaker: OPEN for %ds", self.timeout)

    async def wait_if_open(self):
        while not self.allow():
            remaining = self.timeout - (time.monotonic() - self.opened_at)
            await asyncio.sleep(min(max(remaining, 1.0), 10.0))


# === JSON UTILS ===
# repair_json, parse_json_resilient перенесены в research.json_utils (CP-036)
# Импорт: from research.json_utils import repair_json, parse_json_resilient (выше)


# === MODEL FALLBACK CHAIN ===
# FreeLLMAPI сам маршрутизирует/ротирует провайдеров, поэтому здесь одна логическая модель.
# Для явной ротации задайте FREELLM_MODEL_CHAIN="model-a,model-b,model-c".
MODEL_CHAIN_EXTRACT = [
    m.strip() for m in os.environ.get("FREELLM_MODEL_CHAIN", "auto").split(",") if m.strip()
] or ["auto"]


# === LLM GATEWAY (resilient client) ===
class LLMGateway:
    def __init__(self, base_url, api_key, max_attempts=4):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.max_attempts = max_attempts
        self.semaphore = asyncio.Semaphore(1)
        self.pacer = AdaptivePacer(start_interval=5.0)
        self.breaker = CircuitBreaker(threshold=5, timeout=30.0)
        self.call_count = 0
        self.token_usage = {"input": 0, "output": 0}
        self._client = None

    async def _get_client(self):
        if self._client is None or self._client.is_closed:
            import httpx

            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(connect=10.0, read=180.0, write=30.0, pool=10.0),
                limits=httpx.Limits(max_connections=4, max_keepalive_connections=2),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
        return self._client

    async def aclose(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def chat(
        self,
        prompt=None,
        task_type="general",
        max_tokens=1500,
        temp=0.2,
        use_fusion=False,
        model_offset=0,
        *,
        system_prompt=None,
        messages=None,
        json_mode=None,
    ):
        """Backward-compatible chat().

        Старые вызовы: chat(prompt, task_type=...)
        Новые вызовы:  chat(messages=[...], task_type=...)
                       chat(prompt, system_prompt=..., task_type=...)
        """
        import httpx

        # ─── Формирование messages ───
        if messages is None:
            if prompt is None:
                raise ValueError("chat(): нужен prompt или messages")
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
        else:
            if prompt is not None or system_prompt is not None:
                raise ValueError("chat(): передавайте либо messages, либо prompt/system_prompt")

        # ─── JSON mode: явный или дефолт по task_type ───
        if json_mode is None:
            wants_json = not use_fusion and task_type in ("extract", "plan", "summary")
        else:
            wants_json = bool(json_mode) and not use_fusion

        chain = (
            MODEL_CHAIN_EXTRACT
            if (not use_fusion and task_type in ("extract", "plan"))
            else ["fusion" if use_fusion else "auto"]
        )
        last_err = None

        for attempt in range(1, self.max_attempts + 1):
            model = (
                "fusion" if use_fusion else chain[min(model_offset + attempt - 1, len(chain) - 1)]
            )

            # ─── Best-effort JSON: 1 retry без response_format при rejection ───
            use_json = wants_json
            resp = None
            for json_retry in range(2):
                payload = {
                    "model": model,
                    "messages": messages,
                    "temperature": temp,
                    "max_tokens": max_tokens,
                    "stream": False,
                }
                if use_json:
                    payload["response_format"] = {"type": "json_object"}
                if use_fusion:
                    payload["fusion"] = {"panel_size": 3, "show_details": False}

                await self.breaker.wait_if_open()
                async with self.semaphore:
                    await self.pacer.wait_turn()
                    try:
                        client = await self._get_client()
                        resp = await client.post(
                            "/v1/chat/completions",
                            json=payload,
                            headers={"x-freellm-task-type": task_type},
                        )
                    except httpx.TransportError as e:
                        last_err = str(e)
                        self.breaker.record_failure()
                        await asyncio.sleep(
                            min(4 * (2 ** (attempt - 1)), 60) * random.uniform(0.7, 1.3)
                        )
                        resp = None
                        break

                # Проверяем 400 на rejection response_format
                if resp.status_code == 400 and use_json and json_retry == 0:
                    body = resp.text[:300].lower()
                    if any(
                        k in body
                        for k in (
                            "response_format",
                            "json_object",
                            "json_schema",
                            "not support",
                            "unrecognized",
                            "unsupported",
                        )
                    ):
                        logger.warning(
                            "model=%s отверг response_format=json_object -> retry без него", model
                        )
                        use_json = False
                        wants_json = False
                        continue
                break

            if resp is None:
                continue

            if resp.status_code == 429:
                self.pacer.on_throttle()
                last_err = f"429 on model={model} (rotating)"
                logger.warning("429 on model=%s -> next attempt rotates model", model)
                ra = resp.headers.get("retry-after")
                wait = (
                    float(ra)
                    if ra and ra.isdigit()
                    else min(4 * (2 ** (attempt - 1)), 60) * random.uniform(0.7, 1.3)
                )
                await asyncio.sleep(wait)
                continue
            if resp.status_code >= 500:
                self.pacer.on_server_error()
                self.breaker.record_failure()
                last_err = f"{resp.status_code} on model={model} (rotating)"
                logger.warning(
                    "%d on model=%s -> next attempt rotates model", resp.status_code, model
                )
                await asyncio.sleep(min(5 * attempt, 60) * random.uniform(0.7, 1.3))
                continue
            if resp.status_code == 400:
                raise RuntimeError(f"400 bad request: {resp.text[:200]}")
            if resp.status_code != 200:
                last_err = f"{resp.status_code}"
                await asyncio.sleep(5 * attempt)
                continue
            try:
                data = resp.json()
                text = data["choices"][0]["message"]["content"] or ""
            except Exception as e:
                last_err = f"malformed: {e}"
                await asyncio.sleep(5)
                continue
            if not text.strip() and attempt < self.max_attempts:
                self.pacer.on_server_error()
                last_err = f"empty content on model={model} (rotating)"
                logger.warning("empty content on model=%s -> rotating model", model)
                await asyncio.sleep(2 * attempt)
                continue
            self.call_count += 1
            self.breaker.record_success()
            self.pacer.on_success()
            usage = data.get("usage") or {}
            self.token_usage["input"] += usage.get("prompt_tokens", 0) or 0
            self.token_usage["output"] += usage.get("completion_tokens", 0) or 0
            return text
        raise RuntimeError(f"LLM failed after {self.max_attempts} attempts: {last_err}")

    async def chat_json(self, prompt, task_type, max_tokens=1200, retries=1, use_fusion=False):
        last_err = None
        for att in range(retries + 1):
            try:
                text = await self.chat(
                    prompt,
                    task_type=task_type,
                    max_tokens=max_tokens,
                    temp=0.0,
                    use_fusion=use_fusion,
                    model_offset=att,
                )
                ak = "subtopics" if task_type == "plan" else "evidences"
                parsed = parse_json_resilient(text, array_key=ak)
                if parsed:
                    return parsed
                last_err = "JSON parse returned None"
                logger.warning("RAW RESPONSE (first 500 chars): %s", text[:500])
            except Exception as e:
                last_err = str(e)
            logger.warning("LLM JSON fail (%d): %s", att + 1, last_err)
            prompt += (
                "\n\nВАЖНО: Верни КОРОТКИЙ валидный JSON. Максимум 3 evidences. Только JSON объект."
            )
        raise RuntimeError(f"LLM task={task_type} failed: {last_err}")

    def stats(self):
        return {
            "calls": self.call_count,
            "tokens": self.token_usage,
            "pacer_interval": round(self.pacer.interval, 1),
            "breaker": self.breaker.state,
        }


# Версия алгоритма extraction — при изменении инвалидирует кэш
CACHE_VERSION = "extract-v1"


class AsyncFetcher:
    TTL = 30
    MC = 100000
    MH = 3000000
    UA = "Mozilla/5.0 (compatible; DeepResearchAgent/3.0)"

    def __init__(self, cd, mc=2):
        self.cd = cd
        cd.mkdir(parents=True, exist_ok=True)
        self.sem = asyncio.Semaphore(mc)
        self._exec = ThreadPoolExecutor(max_workers=2, thread_name_prefix="trafilatura")
        self._client = None

    async def _get_client(self):
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=30.0,
                headers={"User-Agent": self.UA},
                follow_redirects=True,
            )
        return self._client

    async def aclose(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
        if self._exec:
            self._exec.shutdown(wait=True)

    def _cp(self, url):
        return self.cd / f"{hashlib.sha256(url.encode()).hexdigest()[:16]}.txt"

    def _cg(self, p):
        if not p.exists():
            return None
        if (datetime.now() - datetime.fromtimestamp(p.stat().st_mtime)).days > self.TTL:
            return None
        return p.read_text(encoding="utf-8")[: self.MC]

    def _save_evidence_cache(self, url, query, evidences):
        """Сохраняет извлечённые evidences в self.cd/evidences/{hash}.json (ключ — пара url + запрос)."""
        try:
            key = hashlib.sha256(f"{CACHE_VERSION}::{url}::{query}".encode()).hexdigest()[:16]
            cache_dir = self.cd / "evidences"
            cache_dir.mkdir(parents=True, exist_ok=True)
            payload = {
                "url": url,
                "query": query,
                "saved_at": datetime.now().isoformat(),
                "evidences": evidences,
            }
            (cache_dir / f"{key}.json").write_text(
                json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            logger.info("💾 Кэш сохранён: %d evidences для %s", len(evidences), url[:60])
        except Exception as e:
            logger.warning("Не удалось сохранить кэш evidences для %s: %s", url[:60], e)

    def _load_evidence_cache(self, url, query, ttl_days=7):
        """Загружает evidences из кэша. Возвращает None, если кэша нет, он устарел (TTL), пуст или повреждён."""
        try:
            key = hashlib.sha256(f"{CACHE_VERSION}::{url}::{query}".encode()).hexdigest()[:16]
            cache_file = self.cd / "evidences" / f"{key}.json"
            if not cache_file.exists():
                return None
            payload = json.loads(cache_file.read_text(encoding="utf-8"))
            saved_at = datetime.fromisoformat(payload["saved_at"])
            # Проверка срока жизни кэша (TTL)
            if (datetime.now() - saved_at).total_seconds() > ttl_days * 86400:
                return None
            evidences = payload.get("evidences")
            if not isinstance(evidences, list) or not evidences:
                return None
            return evidences
        except Exception as e:
            logger.warning("Не удалось прочитать кэш evidences для %s: %s", url[:60], e)
            return None

    async def fetch(self, url):
        import trafilatura

        async with self.sem:
            cf = self._cp(url)
            cached = self._cg(cf)
            if cached:
                return cached
            try:
                cl = await self._get_client()
                r = await cl.get(url)
                if r.status_code != 200:
                    return ""
                html = r.text
                if len(html) > self.MH:
                    logger.warning("Skip large %d: %s", len(html), url)
                    return ""
            except Exception as e:
                logger.warning("Fetch fail %s: %s", url, e)
                return ""
            loop = asyncio.get_running_loop()
            text = await loop.run_in_executor(
                self._exec,
                lambda: (
                    trafilatura.extract(
                        html, include_tables=True, include_comments=False, fast=True
                    )
                    or ""
                ),
            )
            if text and len(text) < 500:
                text2 = await loop.run_in_executor(
                    self._exec,
                    lambda: (
                        trafilatura.extract(html, include_tables=True, include_comments=False) or ""
                    ),
                )
                if len(text2) > len(text):
                    text = text2
            if text:
                lines = []
                skip = [
                    "cookie",
                    "privacy policy",
                    "sign in",
                    "subscribe",
                    "© 20",
                    "all rights reserved",
                    "подписаться",
                ]
                for ln in text.split("\n"):
                    if len(ln.strip()) < 40:
                        continue
                    if any(p in ln.lower() for p in skip):
                        continue
                    lines.append(ln)
                text = "\n".join(lines)[: self.MC]
                cf.write_text(text, encoding="utf-8")
            return text


class TokenBucket:
    def __init__(self, rate=1.0, cap=3):
        self.rate, self.cap, self.tokens, self.last = rate, cap, cap, time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self):
        async with self._lock:
            now = time.monotonic()
            self.tokens = min(self.cap, self.tokens + (now - self.last) * self.rate)
            self.last = now
            if self.tokens < 1:
                wait = (1 - self.tokens) / self.rate
                await asyncio.sleep(wait)
                self.tokens = 0
                self.last = time.monotonic()  # CP-019: avoid double-credit after sleep
            else:
                self.tokens -= 1


# Категории SearXNG для research pipeline.
# general — wikipedia, wikidata, duckduckgo, mojeek
# it — github, stackoverflow, superuser, askubuntu, mdn, docker hub, pypi, arch linux wiki
# science — arxiv, semantic scholar, pubmed, google scholar
# news НЕ включаем — у нас нет news-движков.
DEFAULT_SEARCH_CATEGORIES = ["general", "it", "science"]


class AsyncSearcher:
    def __init__(self, url, mc=3):
        self.url = url.rstrip("/")
        self.sem = asyncio.Semaphore(mc)
        self.bucket = TokenBucket(1.0, 3)
        self._client = None

    async def _get_client(self):
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=20.0)
        return self._client

    async def search(self, query, cats=None):
        cats = cats or DEFAULT_SEARCH_CATEGORIES
        async with self.sem:
            await self.bucket.acquire()
            cl = await self._get_client()
            try:
                r = await cl.get(
                    f"{self.url}/search",
                    params={
                        "q": query,
                        "format": "json",
                        "categories": ",".join(cats),
                        "language": "auto",
                    },
                )
                if r.status_code == 429:
                    logger.warning("429: %s", query)
                    return []
                r.raise_for_status()
                return r.json().get("results", [])[:10]
            except Exception as e:
                logger.warning("Search fail '%s': %s", query, e)
                return []

    async def aclose(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None


def detect_lineage(evidences):
    """Prefilter O(n) → fuzzy только внутри групп. Вместо O(n²)."""
    from collections import defaultdict

    groups = defaultdict(list)
    for e in evidences:
        title = (e.source_title or "").strip().lower()
        if title:
            groups[title].append(e)
    for grp in groups.values():
        if len(grp) < 2:
            continue
        for i, a in enumerate(grp):
            for b in grp[i + 1 :]:
                if b.parent_source_id:
                    continue
                if (
                    a.source_title
                    and b.source_title
                    and SequenceMatcher(
                        None, a.source_title.lower(), b.source_title.lower()
                    ).ratio()
                    > 0.9
                ):
                    b.parent_source_id = a.evidence_id
    return len(set(e.parent_source_id or e.evidence_id for e in evidences))


EXTRACT_PROMPT = """Fact extraction specialist. Извлеки ТОЛЬКО из текста. Не придумывай.
ПОДТЕМА: {subtopic}
ДОКУМЕНТ:
{document}
Верни JSON: {{"evidences":[{{"claim":"...","metric":"market_size|market_share|production|growth_rate|other","value":12.0,"value_raw":"12 млн т","unit":"million_tonnes|USD_bn|percent","currency":null,"year":2023,"forecast_type":"historical|current|published_forecast","evidence_text":"ТОЧНАЯ цитата","market_scope":"...","geography":"...","confidence":"high|medium|low"}}]}}
Максимум 5 evidences. evidence_text=ДОСЛОВНАЯ цитата. Никаких placeholder. Пустой список если нет."""


class DeepResearch:
    def __init__(self, topic, depth=3):
        self.topic = topic
        self.depth = depth
        self.rid = self._mkid(topic)
        self.ckpt = CheckpointManager(WORKING_DIR)
        self.searcher = AsyncSearcher(SEARXNG_URL, 3)
        self.fetcher = AsyncFetcher(CACHE_DIR, 2)
        self.llm = LLMGateway(FREELLM_URL, FREELLM_API_KEY, max_attempts=4)
        self.evidences = []
        self.sources = {}
        self.subtopics = []
        self.done = {}
        self.ext_total = 0
        self.processed_urls_by_subtopic: dict = {}  # Единый источник истины для resume
        self.drop_total = 0

    async def aclose(self):
        """Гарантированное закрытие ресурсов."""
        for name, obj in [
            ("fetcher", self.fetcher),
            ("searcher", self.searcher),
            ("llm", getattr(self, "llm", None)),
        ]:
            if obj is None or not hasattr(obj, "aclose"):
                continue
            try:
                await obj.aclose()
            except Exception as e:
                logger.warning("%s.aclose: %s", name, e)

    @staticmethod
    def _mkid(topic):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = re.sub(r"[^\w]+", "_", topic.lower(), flags=re.UNICODE)[:30].strip("_")
        return f"{ts}_{slug or 'research'}"

    async def plan(self):
        """
        Plan research: generate subtopics adapted to topic type.

        Strategy:
        - Detect topic type by keywords (market / product / generic)
        - Use tailored subtopics per type (no LLM needed for planning)
        - Only use LLM for optional scope enrichment
        """
        n = max(1, self.depth * 3)
        topic = self.topic
        topic_lower = topic.lower()

        # ---- Detect topic type ----
        market_kw = [
            "market",
            "industry",
            "рынок",
            "отрасль",
            "индустр",
            "market size",
            "cagr",
            "forecast",
            "доля рынка",
        ]
        product_kw = [
            "specifications",
            "specs",
            "review",
            "technical",
            "характеристики",
            "спецификация",
            "обзор",
            "features",
            "benchmark",
            "hardware",
            "software",
        ]

        is_market = any(kw in topic_lower for kw in market_kw)
        is_product = any(kw in topic_lower for kw in product_kw)

        # ---- Subtopic templates ----
        if is_market:
            templates = [
                (
                    "Market size, growth rate and forecast",
                    "market size growth forecast",
                    "市场规模 增长率 预测",
                    "размер рынка темпы роста прогноз",
                ),
                (
                    "Key players, market share and competitive landscape",
                    "key players market share competitive",
                    "主要厂商 市场份额 竞争格局",
                    "ключевые игроки доля рынка конкуренция",
                ),
                (
                    "Technology trends, innovations and applications",
                    "technology trends innovations applications",
                    "技术趋势 创新 应用",
                    "технологические тренды инновации",
                ),
                (
                    "Regional markets and geography",
                    "regional market geography",
                    "区域市场 地理",
                    "региональные рынки география",
                ),
                (
                    "Industry segments and end-use applications",
                    "industry segments end-use applications",
                    "行业细分 终端应用",
                    "сегменты отрасли применение",
                ),
                (
                    "Supply chain, materials and pricing",
                    "supply chain materials pricing",
                    "供应链 材料 定价",
                    "цепочка поставок материалы цены",
                ),
            ]
        elif is_product:
            templates = [
                (
                    "Technical specifications and features",
                    "technical specifications features",
                    "技术规格 特性",
                    "технические характеристики особенности",
                ),
                (
                    "Software support, OS and compatibility",
                    "software support operating system compatibility",
                    "软件支持 操作系统 兼容性",
                    "поддержка ПО операционная система совместимость",
                ),
                (
                    "Price, availability and ordering",
                    "price availability buy order",
                    "价格 供货 订购",
                    "цена наличие заказ",
                ),
                (
                    "Reviews, benchmarks and comparisons",
                    "review benchmark comparison test",
                    "评测 基准 对比 测试",
                    "обзор бенчмарк сравнение тест",
                ),
                (
                    "Use cases, projects and community",
                    "use cases projects community",
                    "用例 项目 社区",
                    "сценарии проекты сообщество",
                ),
            ]
        else:
            templates = [
                (
                    "Overview and key facts",
                    "overview key facts",
                    "概述 关键事实",
                    "обзор ключевые факты",
                ),
                (
                    "Details, specifications and features",
                    "details specifications features",
                    "细节 规格 特性",
                    "детали характеристики особенности",
                ),
                (
                    "Comparisons and alternatives",
                    "comparison alternatives versus",
                    "对比 替代方案",
                    "сравнение альтернативы",
                ),
                (
                    "Reviews and user feedback",
                    "review user feedback opinions",
                    "评测 用户反馈",
                    "обзоры отзывы пользователей",
                ),
            ]

        # ---- Build subtopics ----
        selected = templates[:n] if n <= len(templates) else templates
        subtopics = []
        for name, en_q, zh_q, ru_q in selected:
            subtopics.append(
                {
                    "name": name,
                    "queries": [
                        {"text": f"{topic} {en_q} 2024 2025", "lang": "en"},
                        {"text": f"{topic} {zh_q} 2024 2025", "lang": "zh"},
                        {"text": f"{topic} {ru_q} 2024 2025", "lang": "ru"},
                    ],
                    "categories": DEFAULT_SEARCH_CATEGORIES,
                }
            )
        self.subtopics = subtopics
        logger.info(
            "Plan: %d subtopics (type=%s)",
            len(subtopics),
            "market" if is_market else ("product" if is_product else "generic"),
        )
        return subtopics

    async def process_subtopic(self, idx, st):
        name = st.get("name", f"sub-{idx}")
        logger.info("[%d/%d] %s", idx + 1, len(self.subtopics), name)
        # Load processed URLs from checkpoint for this subtopic
        processed_urls = set(self.processed_urls_by_subtopic.get(str(idx), set()))
        seen, queries = set(), []
        for q in st.get("queries", []):
            txt = q["text"] if isinstance(q, dict) else str(q)
            h = hashlib.sha256(txt.lower().strip().encode()).hexdigest()
            if h not in seen:
                seen.add(h)
                queries.append({"text": txt, "categories": st.get("categories")})
        if not queries:
            self.done[str(idx)] = True
            return
        results = await asyncio.gather(
            *[self.searcher.search(q["text"], q.get("categories")) for q in queries]
        )
        url_seen, url_meta, url_snippet = set(), {}, {}
        for batch in results:
            for r in batch:
                u = r.get("url", "")
                if not u or not u.startswith("http"):
                    continue
                h = hashlib.sha256(u.encode()).hexdigest()
                if h in url_seen:
                    continue
                url_seen.add(h)
                title = r.get("title", "") or ""
                snippet = r.get("content", "") or ""
                url_meta[u] = title or snippet[:80]
                url_snippet[u] = f"{title} {snippet}"
        if not url_meta:
            logger.warning("No URLs: %s", name)
            self.done[str(idx)] = True
            return
        query_terms = set()
        for q in queries:
            query_terms.update(t for t in re.split(r"\W+", q["text"].lower()) if len(t) > 2)
        scored = []
        for u in url_meta:
            rel = _relevance_score(url_snippet.get(u, ""), query_terms)
            auth = SourceQualityScorer.authority(u)
            if rel >= 0.15 or auth >= 0.9:
                scored.append((rel * 2 + auth, u))
        scored.sort(key=lambda x: x[0], reverse=True)
        urls = [u for _, u in scored]
        # Фильтрация уже обработанных URL (для resume)
        skipped = sum(1 for u in urls if u in processed_urls)
        urls = [u for u in urls if u not in processed_urls]
        logger.info(
            "Filtered URLs: %d/%d valuable+relevant, %d skipped (already processed)",
            len(urls),
            len(url_meta),
            skipped,
        )
        texts = await asyncio.gather(*[self.fetcher.fetch(u) for u in urls])
        docs = {u: t for u, t in zip(urls, texts) if t and len(t) > 200}
        for u in docs:
            self.sources.setdefault(
                u, {"title": url_meta.get(u, ""), "authority": SourceQualityScorer.authority(u)}
            )
        # MICRO-BATCHING: 1 document = 1 extract call
        # Build dedup index once before document loop (O(1) per evidence)
        existing_keys = {e.dedup_key for e in self.evidences}
        for url, doc_text in docs.items():
            doc_chunk = doc_text[:6000]  # Limit input size
            # Проверяем кэш evidences для пары (url, подтема) перед вызовом LLM
            cached_evidences = self.fetcher._load_evidence_cache(url, name, ttl_days=7)
            prompt = EXTRACT_PROMPT.format(subtopic=name, document=doc_chunk)
            try:
                if cached_evidences:
                    # Кэш найден — LLM extraction не выполняем
                    raw_evs = cached_evidences if isinstance(cached_evidences, list) else []
                    if not isinstance(raw_evs, list):
                        raw_evs = []
                    logger.info("📖 Кэш использован: %d evidences для %s", len(raw_evs), url[:60])
                else:
                    data = await self.llm.chat_json(prompt, task_type="extract", max_tokens=1200)
                    raw_evs = data.get("evidences", []) if isinstance(data, dict) else []
                    if not isinstance(raw_evs, list):
                        raw_evs = []
                    # Пустая экстракция -> ОДИН упрощённый ретрай, затем документ пропускается
                    if not raw_evs:
                        logger.info("Empty evidences, one simplified retry for %s", url[:50])
                        simple_prompt = f'Найди факты с числами в тексте. Верни JSON: {{"evidences":[{{"claim":"...","evidence_text":"...","year":2024}}]}}\nТЕКСТ:\n{doc_chunk[:2000]}'
                        try:
                            data2 = await self.llm.chat_json(
                                simple_prompt, task_type="extract", max_tokens=800
                            )
                            raw_evs = data2.get("evidences", []) if isinstance(data2, dict) else []
                        except Exception as e:
                            logger.warning("Simplified retry failed %s: %s", url[:50], e)
                            raw_evs = []
                    # Кэша нет — результат LLM extraction сохраняем (только непустой)
                    if isinstance(raw_evs, list) and raw_evs:
                        self.fetcher._save_evidence_cache(url, name, raw_evs)
                if not isinstance(raw_evs, list):
                    raw_evs = []
                for raw in raw_evs[:5]:
                    ev = self._build_ev(raw, name, url, url_meta.get(url, ""))
                    if ev is None:
                        self.drop_total += 1
                        continue
                    hard, soft = FactValidator.validate(ev)
                    if hard:
                        logger.info("Drop (%s): %s", "; ".join(hard), ev.claim[:60])
                        self.drop_total += 1
                        continue
                    ok, method, score = EvidenceVerifier.verify(ev.evidence_text, doc_text)
                    if not ok:
                        logger.info("Verify fail: %s", ev.claim[:60])
                        self.drop_total += 1
                        continue
                    ev.verification_status = f"verified_{method}"
                    ev.verification_score = score
                    ev.verification_method = method
                    ev.confidence = ConfidenceScorer.score(ev)
                    if soft:
                        ev.confidence = "low"
                        logger.info("Soft-keep low (%s): %s", "; ".join(soft), ev.claim[:60])
                    # Dedup by hash (incremental — O(1) per evidence)
                    if ev.dedup_key not in existing_keys:
                        self.evidences.append(ev)
                        self.ext_total += 1
                        existing_keys.add(ev.dedup_key)
                    else:
                        logger.debug("Dedup: skipped duplicate evidence")
            except Exception as e:
                logger.error("Extract fail '%s' (%s): %s", name, url[:50], e)
                self.drop_total += 1
                continue
            # Save progress after each document
            processed_urls.add(url)
            # P0-4: единый источник — self.processed_urls_by_subtopic
            self.processed_urls_by_subtopic[str(idx)] = set(processed_urls)
            self.save_ckpt()
        logger.info("Done: %d evidences total, %d dropped", len(self.evidences), self.drop_total)
        self.done[str(idx)] = True

    def _build_ev(self, raw, subtopic, url, title):
        claim = (raw.get("claim") or "").strip()
        if not claim or len(claim) < 10:
            return None
        evt = (raw.get("evidence_text") or "").strip()
        if len(evt) < 15:
            return None
        try:
            val = float(raw["value"]) if raw.get("value") is not None else None
        except:
            val = None
        e = Evidence(
            claim=claim,
            metric=raw.get("metric"),
            value=val,
            value_raw=raw.get("value_raw"),
            unit=raw.get("unit"),
            currency=raw.get("currency"),
            year=None,
            forecast_type=raw.get("forecast_type", "historical"),
            source_url=url,
            source_title=title,
            source_type=SourceQualityScorer.guess_type(url, title),
            evidence_text=evt,
            market_scope=normalize_scope(raw.get("market_scope", "")),
            geography=normalize_geography(raw.get("geography", "")),
            confidence=raw.get("confidence", "medium"),
            subtopic=subtopic,
        )
        # Безопасный парсинг year (баг #8: "2023/24", "н/д" не должны ронять)
        try:
            if raw.get("year") is not None:
                e.year = int(raw["year"])
        except (ValueError, TypeError):
            e.year = None
        e.source_authority = SourceQualityScorer.authority(url)
        e.evidence_quality = SourceQualityScorer.quality(
            evt, val is not None or bool(re.search(r"\d", evt))
        )
        # Присваиваем evidence_id для метрики independent_sources
        e.evidence_id = hashlib.sha256(f"{e.claim}|{url}|{e.value}|{e.year}".encode()).hexdigest()[
            :16
        ]

        return e

    def save_ckpt(self):
        self.ckpt.save(
            self.rid,
            {
                "research_id": self.rid,
                "topic": self.topic,
                "depth": self.depth,
                "subtopics": self.subtopics,
                "done": self.done,
                "evidences": [e.to_dict() for e in self.evidences],
                "sources": self.sources,
                "ext_total": self.ext_total,
                "drop_total": self.drop_total,
                "processed_urls_by_subtopic": {
                    k: sorted(v) for k, v in self.processed_urls_by_subtopic.items()
                },
            },
        )

    def load_ckpt(self):
        s = self.ckpt.load(self.rid)
        if not s:
            return False
        self.subtopics = s.get("subtopics", [])
        self.done = s.get("done", {})
        self.evidences = [Evidence.from_dict(d) for d in s.get("evidences", [])]
        self.sources = s.get("sources", {})
        self.ext_total = s.get("ext_total", 0)
        self.drop_total = s.get("drop_total", 0)
        self.processed_urls_by_subtopic = {
            k: set(v) for k, v in s.get("processed_urls_by_subtopic", {}).items()
        }
        logger.info(
            "Resumed %s: %d/%d done, %d evidences",
            self.rid,
            len(self.done),
            len(self.subtopics),
            len(self.evidences),
        )
        return True

    async def build_report(self):
        ranked = sorted(self.sources.items(), key=lambda kv: kv[1]["authority"], reverse=True)
        cmap = {url: i + 1 for i, (url, _) in enumerate(ranked)}
        conflicts = ConflictDetector.detect(self.evidences)
        independent = detect_lineage(self.evidences)
        verified = sum(1 for e in self.evidences if e.verification_status.startswith("verified"))
        stats = {
            "subtopics_analyzed": len(self.done),
            "unique_sources": len(self.sources),
            "independent_sources": independent,
            "evidences_extracted": self.ext_total,
            "evidences_verified": verified,
            "evidences_dropped": self.drop_total,
            "conflicts_detected": len(conflicts),
            **self.llm.stats(),
        }
        top = sorted(
            self.evidences, key=lambda e: e.source_authority * e.evidence_quality, reverse=True
        )[:10]
        bullets = "\n".join(f"- {e.claim} [{cmap.get(e.source_url, '?')}]" for e in top)
        if not self.evidences:
            exec_lines = ["Нет данных для анализа"]
        else:
            # NEW: Try production-grade pipeline first
            try:
                logger.info(f"NEW pipeline: starting with {len(self.evidences)} evidences")
                valid_ids = set(cmap.values())
                logger.info(f"NEW pipeline: valid_ids = {sorted(valid_ids)}")
                config = SummaryConfig(
                    model="auto",
                    temperature=0.0,
                    top_p=1.0,
                    max_tokens=1500,
                    max_retries=1,
                    use_fusion=False,  # CRITICAL: disable fusion for structured output
                )
                generator = ExecutiveSummaryGenerator(llm_chat_func=self.llm.chat, config=config)
                logger.info("NEW pipeline: calling generate_summary...")
                result = await generator.generate_summary(
                    topic=self.topic,
                    facts=bullets,
                    valid_citation_ids=valid_ids,
                    evidences=self.evidences,
                    url_to_cid=cmap,
                )
                logger.info("NEW pipeline: generate_summary returned successfully")
                exec_lines = result.bullets
                logger.info(
                    f"Summary generated via NEW pipeline (source={result.source}, attempts={result.attempts})"
                )

            except Exception as new_pipeline_error:
                logger.error(f"Summary pipeline failed: {new_pipeline_error}")
                exec_lines = bullets.splitlines()
        by_metric = defaultdict(list)
        for e in self.evidences:
            if e.metric and e.value_raw:
                by_metric[e.metric].append(e)
        tbl = []
        for met in sorted(by_metric):
            rows = sorted(
                by_metric[met], key=lambda e: (e.year or 0, e.source_authority), reverse=True
            )[:15]
            tbl.append(
                f"### {met}\n\n| Значение | Год | Scope | География | Источник |\n|----------|-----|-------|-----------|----------|"
            )
            for e in rows:
                tbl.append(
                    f"| {e.value_raw} | {e.year or '—'} | {e.market_scope} | {e.geography} | [{cmap.get(e.source_url, '?')}] |"
                )
            tbl.append("")
        conf = []
        if conflicts:
            conf.append("## Расхождения источников\n")
            for c in conflicts:
                conf.append(
                    f"- **{c['metric_key'][0]}** ({c['conflict_type']}): {c['divergence'] * 100:.0f}% (порог {c['threshold'] * 100:.0f}%)"
                )
                for ev in c["evidences"]:
                    conf.append(f"  - {ev['value_raw']} — [{cmap.get(ev['source_url'], '?')}]")
            conf.append("")
        src = ["## Источники\n"]
        for url, meta in ranked:
            src.append(
                f"[{cmap[url]}] {url} — {meta['title'][:70]}, authority: {meta['authority']:.1f}"
            )
        lines = [
            "---",
            f'topic: "{self.topic}"',
            f"date: {datetime.now().isoformat(timespec='seconds')}",
            f"depth: {self.depth}",
            f'research_id: "{self.rid}"',
        ]
        for k, v in stats.items():
            lines.append(f"{k}: {v}")
        lines += ["---", "", f"# {self.topic}", "", "## Executive Summary", ""] + exec_lines + [""]
        if tbl:
            lines += ["## Ключевые метрики", ""] + tbl
        lines += conf + src
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        rp = REPORTS_DIR / f"{self.rid}.md"
        rp.write_text("\n".join(lines), encoding="utf-8")
        sidecar = {
            "research_id": self.rid,
            "topic": self.topic,
            "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "stats": stats,
            "evidences": [
                dict(e.to_dict(), citation_number=cmap.get(e.source_url)) for e in self.evidences
            ],
            "citation_map": {str(n): url for url, n in cmap.items()},
            "conflicts": conflicts,
        }
        sp = REPORTS_DIR / f"{self.rid}.evidence.json"
        sp.write_text(json.dumps(sidecar, ensure_ascii=False, indent=2), encoding="utf-8")
        try:
            with open(METRICS_FILE, "a") as mf:
                mf.write(
                    json.dumps(
                        {
                            "research_id": self.rid,
                            "topic": self.topic,
                            **stats,
                            "rss_mb": self._rss(),
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        except:
            pass
        return {"report": str(rp), "sidecar": str(sp), "stats": stats}

    @staticmethod
    def _rss():
        try:
            for ln in open("/proc/self/status"):
                if ln.startswith("VmRSS"):
                    return round(int(ln.split()[1]) / 1024, 1)
        except:
            pass
        return -1

    async def run(self, dry_run=False):
        t0 = time.time()
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        resumed = self.load_ckpt()
        if not resumed:
            await self.plan()
            self.save_ckpt()
        if dry_run:
            print(f"research_id: {self.rid}")
            print(json.dumps({"subtopics": self.subtopics}, ensure_ascii=False, indent=2))
            return {"research_id": self.rid, "dry_run": True}
        for idx, st in enumerate(self.subtopics):
            if self.done.get(str(idx)):
                continue
            await self.process_subtopic(idx, st)
            self.save_ckpt()
            rss = self._rss()
            if rss > 0:
                logger.info("RSS: %.0f MB", rss)
        result = await self.build_report()
        self.ckpt.cleanup(self.rid)
        await self.llm.aclose()
        result["elapsed_sec"] = round(time.time() - t0, 1)
        result["rss_mb"] = self._rss()
        print("\n===== RESEARCH COMPLETE =====")
        for k, v in result.get("stats", {}).items():
            print(f"  {k}: {v}")
        for k in ("report", "sidecar", "elapsed_sec", "rss_mb"):
            if k in result:
                print(f"  {k}: {result[k]}")
        return result


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
