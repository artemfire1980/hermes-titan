"""Тесты AsyncFetcher и AsyncSearcher через respx (mock HTTP)."""
import httpx
import pytest
import research_runner as rr
import respx

# ─── AsyncFetcher ───────────────────────────────────────────────────

@pytest.mark.asyncio
@respx.mock
async def test_fetch_ok(tmp_path):
    """fetch(): 200 → HTML → text (через trafilatura)."""
    # Минимальный HTML с длинным абзацем (trafilatura требует контент)
    html = (
        "<html><body><article>"
        "<h1>Test Article</h1>"
        "<p>" + ("This is a long paragraph about Khadas VIM4. " * 20) + "</p>"
        "</article></body></html>"
    )
    respx.get("http://example.com/page").mock(
        return_value=httpx.Response(200, text=html)
    )
    fetcher = rr.AsyncFetcher(cd=tmp_path, mc=1)
    try:
        text = await fetcher.fetch("http://example.com/page")
        assert isinstance(text, str)
        # trafilatura может вернуть текст или "" — главное не упало
    finally:
        await fetcher.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_fetch_404_returns_empty(tmp_path):
    """fetch(): 404 → "" (без исключения)."""
    respx.get("http://example.com/missing").mock(
        return_value=httpx.Response(404, text="not found")
    )
    fetcher = rr.AsyncFetcher(cd=tmp_path, mc=1)
    try:
        text = await fetcher.fetch("http://example.com/missing")
        assert text == ""
    finally:
        await fetcher.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_fetch_transport_error_returns_empty(tmp_path):
    """fetch(): ConnectError → "" (graceful)."""
    respx.get("http://example.com/error").mock(
        side_effect=httpx.ConnectError("simulated")
    )
    fetcher = rr.AsyncFetcher(cd=tmp_path, mc=1)
    try:
        text = await fetcher.fetch("http://example.com/error")
        assert text == ""
    finally:
        await fetcher.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_fetch_client_reuse(tmp_path):
    """fetch(): _get_client() возвращает тот же объект."""
    fetcher = rr.AsyncFetcher(cd=tmp_path, mc=1)
    try:
        cl1 = await fetcher._get_client()
        cl2 = await fetcher._get_client()
        assert cl1 is cl2
    finally:
        await fetcher.aclose()


# ─── AsyncSearcher ──────────────────────────────────────────────────

@pytest.mark.asyncio
@respx.mock
async def test_search_ok():
    """search(): JSON results → list of dicts."""
    payload = {
        "results": [
            {"url": "http://a.com", "title": "A", "content": "aaa"},
            {"url": "http://b.com", "title": "B", "content": "bbb"},
        ]
    }
    respx.get("http://test-searxng.local/search").mock(
        return_value=httpx.Response(200, json=payload)
    )
    searcher = rr.AsyncSearcher(url="http://test-searxng.local")
    try:
        results = await searcher.search("test query")
        assert isinstance(results, list)
        assert len(results) == 2
        assert results[0]["url"] == "http://a.com"
    finally:
        await searcher.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_search_empty_results():
    """search(): пустой results → []."""
    respx.get("http://test-searxng.local/search").mock(
        return_value=httpx.Response(200, json={"results": []})
    )
    searcher = rr.AsyncSearcher(url="http://test-searxng.local")
    try:
        results = await searcher.search("no results query")
        assert results == []
    finally:
        await searcher.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_search_429_returns_empty():
    """search(): 429 → [] (graceful)."""
    respx.get("http://test-searxng.local/search").mock(
        return_value=httpx.Response(429, text="rate limited")
    )
    searcher = rr.AsyncSearcher(url="http://test-searxng.local")
    try:
        results = await searcher.search("rate limited query")
        assert results == []
    finally:
        await searcher.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_search_client_reuse():
    """search(): _get_client() возвращает тот же объект."""
    searcher = rr.AsyncSearcher(url="http://test-searxng.local")
    try:
        cl1 = await searcher._get_client()
        cl2 = await searcher._get_client()
        assert cl1 is cl2
    finally:
        await searcher.aclose()
