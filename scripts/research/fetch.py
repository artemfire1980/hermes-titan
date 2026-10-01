from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import httpx

logger = logging.getLogger("deep-research")

"""Async fetcher for Deep Research Agent."""

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
