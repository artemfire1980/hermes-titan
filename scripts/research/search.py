from __future__ import annotations

import asyncio
import logging
import time

import httpx

logger = logging.getLogger("deep-research")

"""SearXNG search client for Deep Research Agent."""


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
