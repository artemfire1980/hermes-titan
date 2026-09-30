"""Тесты LLMGateway.chat через respx (mock HTTP)."""

import httpx
import pytest
import research_runner as rr
import respx

# ─── Helpers ────────────────────────────────────────────────────────


def _make_gateway(url="http://test-llm.local"):
    """Минимальный LLMGateway для тестов."""
    return rr.LLMGateway(base_url=url, api_key="test-key")


def _ok_json(content="Hello!"):
    return {"choices": [{"message": {"content": content}}]}


# ─── Тесты ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
@respx.mock
async def test_chat_ok():
    """Успешный вызов: 200 → content возвращается."""
    respx.post("http://test-llm.local/v1/chat/completions").mock(
        return_value=httpx.Response(200, json=_ok_json("hi"))
    )
    gw = _make_gateway()
    try:
        result = await gw.chat("Say hi", task_type="general", max_tokens=10)
        assert result == "hi"
    finally:
        await gw.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_chat_429_retries():
    """429 → retry → 200 OK."""
    route = respx.post("http://test-llm.local/v1/chat/completions")
    route.side_effect = [
        httpx.Response(429, json={"error": "rate limit"}),
        httpx.Response(200, json=_ok_json("ok after retry")),
    ]
    gw = _make_gateway()
    try:
        result = await gw.chat("Say hi", task_type="general", max_tokens=10)
        assert result == "ok after retry"
        assert route.call_count == 2
    finally:
        await gw.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_chat_502_retries():
    """502 → retry → 200 OK."""
    route = respx.post("http://test-llm.local/v1/chat/completions")
    route.side_effect = [
        httpx.Response(502, json={"error": "bad gateway"}),
        httpx.Response(200, json=_ok_json("recovered")),
    ]
    gw = _make_gateway()
    try:
        result = await gw.chat("Say hi", task_type="general", max_tokens=10)
        assert result == "recovered"
        assert route.call_count == 2
    finally:
        await gw.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_chat_transport_error_retries():
    """TransportError (ConnectError) → retry → 200 OK."""
    route = respx.post("http://test-llm.local/v1/chat/completions")
    route.side_effect = [
        httpx.ConnectError("simulated"),
        httpx.Response(200, json=_ok_json("after transport")),
    ]
    gw = _make_gateway()
    try:
        result = await gw.chat("Say hi", task_type="general", max_tokens=10)
        assert result == "after transport"
        assert route.call_count == 2
    finally:
        await gw.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_get_client_reuse():
    """_get_client() возвращает тот же объект (persistent client)."""
    gw = _make_gateway()
    try:
        cl1 = await gw._get_client()
        cl2 = await gw._get_client()
        assert cl1 is cl2
    finally:
        await gw.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_chat_messages_api():
    """chat(messages=[...]) — не требует prompt."""
    respx.post("http://test-llm.local/v1/chat/completions").mock(
        return_value=httpx.Response(200, json=_ok_json("from messages"))
    )
    gw = _make_gateway()
    try:
        result = await gw.chat(
            messages=[{"role": "user", "content": "hi"}],
            task_type="general",
            max_tokens=10,
        )
        assert result == "from messages"
    finally:
        await gw.aclose()
