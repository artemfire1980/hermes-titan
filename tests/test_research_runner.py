"""Tests for research_runner.py P0 fixes (CP-020/CP-021).

Covers:
- P0-1: LLMGateway.chat() messages API + single POST
- P0-2: repair retry contains original facts
- P0-3: JSON mode best-effort fallback on 400
- P0-4: checkpoint processed_urls_by_subtopic round-trip
- P0-2 (fallback): url_to_cid передаётся в generate_fallback_summary
"""
import asyncio
import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

# Ensure scripts/ is importable
ROOT = Path(__file__).parent.parent.resolve()
SCRIPTS = ROOT / "scripts"
for p in (str(ROOT), str(SCRIPTS)):
    if p not in sys.path:
        sys.path.insert(0, p)

import research_runner as rr  # noqa: E402
import summary_generator as sg  # noqa: E402


# ─── P0-1: single POST ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_chat_sends_one_request(monkeypatch):
    """chat() должен отправить РОВНО один HTTP-запрос (двойной POST — регрессия CP-020)."""
    import httpx

    calls = {"n": 0}

    class FakeResp:
        status_code = 200
        headers = {}
        text = ""

        def json(self):
            return {"choices": [{"message": {"content": "ok"}}], "usage": {}}

    async def fake_post(self, url, json=None, headers=None):
        calls["n"] += 1
        return FakeResp()

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    gw = rr.LLMGateway("http://test", "k", max_attempts=1)
    result = await gw.chat("hello world", task_type="general", json_mode=False)
    await gw.aclose()

    assert result == "ok"
    assert calls["n"] == 1, f"Ожидался 1 POST, было {calls['n']}"


# ─── P0-1: messages / system_prompt API ─────────────────────────────

@pytest.mark.asyncio
async def test_chat_with_messages(monkeypatch):
    """chat(messages=[...]) → payload['messages'] должен быть ровно переданным."""
    import httpx

    captured = {}

    class FakeResp:
        status_code = 200
        headers = {}
        text = ""

        def json(self):
            return {"choices": [{"message": {"content": "ok"}}], "usage": {}}

    async def fake_post(self, url, json=None, headers=None):
        captured["payload"] = json
        return FakeResp()

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    gw = rr.LLMGateway("http://test", "k", max_attempts=1)
    msgs = [
        {"role": "system", "content": "system instruction"},
        {"role": "user", "content": "facts here"},
    ]
    await gw.chat(messages=msgs, task_type="summary", json_mode=False)
    await gw.aclose()

    assert captured["payload"]["messages"] == msgs


@pytest.mark.asyncio
async def test_chat_with_system_prompt(monkeypatch):
    """chat(prompt, system_prompt=...) → messages = [system, user]."""
    import httpx

    captured = {}

    class FakeResp:
        status_code = 200
        headers = {}
        text = ""

        def json(self):
            return {"choices": [{"message": {"content": "ok"}}], "usage": {}}

    async def fake_post(self, url, json=None, headers=None):
        captured["payload"] = json
        return FakeResp()

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    gw = rr.LLMGateway("http://test", "k", max_attempts=1)
    await gw.chat("user prompt", system_prompt="system instruction",
                  task_type="general", json_mode=False)
    await gw.aclose()

    assert captured["payload"]["messages"] == [
        {"role": "system", "content": "system instruction"},
        {"role": "user", "content": "user prompt"},
    ]


@pytest.mark.asyncio
async def test_chat_rejects_prompt_and_messages():
    """chat() должен отклонить prompt + messages одновременно."""
    gw = rr.LLMGateway("http://test", "k")
    with pytest.raises(ValueError):
        await gw.chat("p", messages=[{"role": "user", "content": "x"}])
    with pytest.raises(ValueError):
        await gw.chat(messages=None, prompt=None)
    await gw.aclose()


# ─── P0-3: JSON mode best-effort fallback ───────────────────────────

@pytest.mark.asyncio
async def test_summary_json_mode_400_fallback(monkeypatch):
    """При 400 с rejection response_format → retry без него, второй payload без response_format."""
    import httpx

    payloads = []

    class FakeResp:
        def __init__(self, status_code, text):
            self.status_code = status_code
            self.text = text
            self.headers = {}

        def json(self):
            return {"choices": [{"message": {"content": '{"bullets": []}'}}], "usage": {}}

    async def fake_post(self, url, json=None, headers=None):
        payloads.append(json)
        if len(payloads) == 1:
            return FakeResp(400, "response_format is unsupported")
        return FakeResp(200, "")

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    gw = rr.LLMGateway("http://test", "k", max_attempts=1)
    await gw.chat("p", task_type="summary", json_mode=True)
    await gw.aclose()

    assert "response_format" in payloads[0]
    assert "response_format" not in payloads[1]


# ─── P0-2: repair retry contains facts ──────────────────────────────

@pytest.mark.asyncio
async def test_repair_contains_facts():
    """Repair-попытка должна содержать исходные facts + previous_error."""
    calls = []

    async def mock_llm_chat(messages=None, **kwargs):
        calls.append(messages)
        if len(calls) == 1:
            raise ValueError("invalid JSON")
        return '{"bullets": ["- A valid Russian bullet [1]", "- B [1]", "- C [1]", "- D [1]", "- E [1]"]}'

    gen = sg.ExecutiveSummaryGenerator(
        mock_llm_chat, sg.SummaryConfig(max_retries=1)
    )
    await gen.generate_summary("topic", "ORIGINAL_FACTS_MARKER", {1})

    assert len(calls) >= 2
    repair_messages = calls[1]
    repair_text = " ".join(m["content"] for m in repair_messages)
    assert "ORIGINAL_FACTS_MARKER" in repair_text
    assert "<previous_error>" in repair_text


# ─── P0-4: checkpoint processed_urls round-trip ─────────────────────

def test_checkpoint_processed_urls(tmp_path):
    """save_ckpt → load_ckpt сохраняет processed_urls_by_subtopic."""
    d = rr.DeepResearch.__new__(rr.DeepResearch)
    d.ckpt = rr.CheckpointManager(tmp_path)
    d.rid = "r1"
    d.topic = "t"
    d.depth = 1
    d.subtopics = []
    d.done = {}
    d.evidences = []
    d.sources = {}
    d.ext_total = 0
    d.drop_total = 0
    d.processed_urls_by_subtopic = {"0": {"http://a", "http://b"}}
    d.save_ckpt()

    d2 = rr.DeepResearch.__new__(rr.DeepResearch)
    d2.ckpt = rr.CheckpointManager(tmp_path)
    d2.rid = "r1"
    d2.load_ckpt()

    assert d2.processed_urls_by_subtopic["0"] == {"http://a", "http://b"}


# ─── P0-2 fallback: url_to_cid ──────────────────────────────────────

def test_fallback_uses_url_to_cid():
    """generate_fallback_summary использует url_to_cid для проставления citation IDs."""
    ev = SimpleNamespace(
        source_url="https://example.com",
        source_authority=1.0,
        evidence_quality=1.0,
        metric=None,
        year=2025,
        claim="Достаточно длинное проверяемое утверждение о рынке",
    )
    bullets = sg.generate_fallback_summary(
        facts_text="",
        valid_citation_ids={7},
        evidences=[ev],
        url_to_cid={"https://example.com": 7},
    )
    assert bullets
    assert "[7]" in bullets[0]


