from __future__ import annotations

import asyncio
import logging
import os
import random
import time

from research.json_utils import parse_json_resilient

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
