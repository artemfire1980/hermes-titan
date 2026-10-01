from __future__ import annotations

import asyncio
import logging
import random
import time

logger = logging.getLogger("deep-research")

"""LLM gateway components: adaptive pacer and circuit breaker for Deep Research Agent."""


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
