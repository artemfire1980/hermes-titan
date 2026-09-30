"""
Unit tests for summary_generator module.
Tests JSON extraction, Pydantic validation, citation validation, and fallback.
"""

# Add parent directory to path
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.summary_generator import (
    ExecutiveSummary,
    ExecutiveSummaryGenerator,
    SummaryConfig,
    extract_last_valid_json,
    generate_fallback_summary,
    render_markdown,
    validate_citations,
)


def test_extract_json_with_think_tags():
    """Test JSON extraction with <think> tags (DeepSeek-R1 style)."""
    text = """
<think>
Let me analyze the facts...
1. The user wants an executive summary
2. I need to extract key points
</think>

Here is the response:
```json
{
  "bullets": [
    "- Факт номер один о компании [1]",
    "- Факт номер два о рынке [2]",
    "- Факт номер три о доходах [1]",
    "- Факт номер четыре о продукте [3]",
    "- Факт номер пять о прогнозах [2]"
  ]
}
```
"""
    result = extract_last_valid_json(text)
    assert "bullets" in result
    assert len(result["bullets"]) == 5
    print("✅ test_extract_json_with_think_tags PASSED")


def test_extract_json_nested():
    """Test JSON extraction handles nested structures (regex would fail here)."""
    text = """
Some reasoning text...
{
  "bullets": [
    {"text": "Nested claim", "citations": [1]},
    {"text": "Another claim", "citations": [2]}
  ],
  "metadata": {"count": 2}
}
"""
    result = extract_last_valid_json(text)
    assert "bullets" in result
    assert len(result["bullets"]) == 2
    print("✅ test_extract_json_nested PASSED")


def test_extract_json_multiple():
    """Test that LAST valid JSON is extracted when multiple present."""
    text = """
{"bullets": ["- First attempt [1]", "- Second [2]"]}
Some more text...
{
  "bullets": [
    "- Real bullet 1 [1]",
    "- Real bullet 2 [2]",
    "- Real bullet 3 [3]",
    "- Real bullet 4 [4]",
    "- Real bullet 5 [5]"
  ]
}
"""
    result = extract_last_valid_json(text)
    assert len(result["bullets"]) == 5
    assert "Real bullet 1" in result["bullets"][0]
    print("✅ test_extract_json_multiple PASSED")


def test_pydantic_schema_validation():
    """Test Pydantic validates structure only."""
    # Valid
    valid_data = {
        "bullets": [
            "- Bullet one with citation [1]",
            "- Bullet two with citation [2]",
            "- Bullet three with citation [3]",
            "- Bullet four with citation [4]",
            "- Bullet five with citation [5]",
        ]
    }
    summary = ExecutiveSummary.model_validate(valid_data)
    assert len(summary.bullets) == 5
    print("✅ test_pydantic_schema_validation PASSED")


def test_pydantic_rejects_no_citations():
    """Test Pydantic rejects bullets without citations."""
    invalid_data = {
        "bullets": [
            "- Bullet without citation",
            "- Another bullet",
            "- Third bullet",
            "- Fourth bullet",
            "- Fifth bullet",
        ]
    }
    try:
        ExecutiveSummary.model_validate(invalid_data)
        assert False, "Should have raised validation error"
    except Exception as e:
        assert "no [N] citation" in str(e)
    print("✅ test_pydantic_rejects_no_citations PASSED")


def test_citation_validator():
    """Test separate citation validator."""
    bullets = [
        "- Bullet one [1]",
        "- Bullet two [2]",
        "- Bullet three [3]",
        "- Bullet four [4]",
        "- Bullet five [5]",
    ]
    valid_ids = {1, 2, 3, 4, 5}

    result = validate_citations(bullets, valid_ids)
    assert len(result) == 5
    print("✅ test_citation_validator PASSED")


def test_citation_validator_rejects_invalid():
    """Test citation validator rejects invalid IDs."""
    bullets = ["- Bullet one [1]", "- Bullet two [99]"]
    valid_ids = {1, 2, 3}

    try:
        validate_citations(bullets, valid_ids)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "99" in str(e)
    print("✅ test_citation_validator_rejects_invalid PASSED")


def test_fallback_from_facts():
    """Test fallback extracts from facts text."""
    facts = """
- Данные о росте рынка на 15% в 2025 году [1]
- Ввод новых мощностей предприятия [2]
Неважная строка без цитаты
- Запуск новой линейки продукции [3]
- Экспортные поставки в страны СНГ [1]
- Увеличение штата сотрудников [2]
"""
    valid_ids = {1, 2, 3}
    fallback = generate_fallback_summary(facts, valid_ids)

    assert len(fallback) == 5
    assert all("[1]" in b or "[2]" in b or "[3]" in b for b in fallback)
    print("✅ test_fallback_from_facts PASSED")


def test_fallback_emergency():
    """Test emergency fallback when no valid bullets found."""
    facts = "No valid bullets here"
    valid_ids = {1, 2, 3}

    fallback = generate_fallback_summary(facts, valid_ids)
    assert len(fallback) >= 5
    assert all("[1]" in b for b in fallback)
    print("✅ test_fallback_emergency PASSED")


def test_render_markdown():
    """Test Markdown rendering."""
    bullets = [
        "- Bullet one [1]",
        "- Bullet two [2]",
        "- Bullet three [3]",
    ]
    markdown = render_markdown(bullets)
    assert markdown == "- Bullet one [1]\n- Bullet two [2]\n- Bullet three [3]"
    print("✅ test_render_markdown PASSED")


async def test_generator_with_mock_llm():
    """Test full generator pipeline with mock LLM."""

    # Mock LLM chat function
    async def mock_llm_chat(
        prompt=None, task_type=None, max_tokens=None, temp=None, use_fusion=None, **kwargs
    ):
        return """
<think>Thinking...</think>
{
  "bullets": [
    "- Кантонская выставка соберёт 25000 компаний [1]",
    "- Мероприятие проходит дважды в год [2]",
    "- Ожидается 200 тысяч байеров [1]",
    "- Выставка пройдет в Гуанчжоу [3]",
    "- Инновации в сфере AI и робототехники [2]"
  ]
}
"""

    config = SummaryConfig(model="test-model", max_retries=1)
    generator = ExecutiveSummaryGenerator(llm_chat_func=mock_llm_chat, config=config)

    facts = "Факты о выставке..."
    valid_ids = {1, 2, 3}

    result = await generator.generate_summary("Canton Fair", facts, valid_ids)

    assert result.source == "llm"
    assert result.attempts == 1
    assert len(result.bullets) == 5
    assert "- Кантонская выставка" in result.bullets[0]
    print("✅ test_generator_with_mock_llm PASSED")


async def test_generator_with_repair():
    """Test generator repair retry on validation failure."""
    # Mock LLM chat function that fails first, succeeds second
    call_count = 0

    async def mock_llm_chat(
        prompt=None, task_type=None, max_tokens=None, temp=None, use_fusion=None, **kwargs
    ):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return "Invalid JSON"
        else:
            return """{
        "bullets": [
            "- Первое длинное утверждение о рынке с цитатой [1]",
            "- Второе длинное утверждение о компаниях и их достижениях [2]",
            "- Третье длинное утверждение о прогнозах развития отрасли [3]",
            "- Четвёртое длинное утверждение о современных трендах [4]",
            "- Пятое длинное утверждение о статистике и показателях [5]"
        ]
    }"""

    config = SummaryConfig(model="test-model", max_retries=1)
    generator = ExecutiveSummaryGenerator(llm_chat_func=mock_llm_chat, config=config)

    result = await generator.generate_summary("Topic", "Facts", {1, 2, 3, 4, 5})

    assert result.source == "llm"
    assert result.attempts == 2  # First failed, second succeeded
    assert len(result.bullets) == 5
    print("✅ test_generator_with_repair PASSED")


async def test_generator_fallback_on_total_failure():
    """Test generator uses fallback when all retries fail."""

    # Mock LLM chat function that always fails
    async def mock_llm_chat(
        prompt=None, task_type=None, max_tokens=None, temp=None, use_fusion=None, **kwargs
    ):
        raise Exception("LLM completely failed")

    config = SummaryConfig(model="test-model", max_retries=1)
    generator = ExecutiveSummaryGenerator(llm_chat_func=mock_llm_chat, config=config)

    facts = "- Valid fact [1]\n- Another fact [2]\n- Third fact [3]\n- Fourth [4]\n- Fifth [5]"
    result = await generator.generate_summary("Topic", facts, {1, 2, 3, 4, 5})

    assert result.source == "fallback"
    assert len(result.bullets) >= 5
    print("✅ test_generator_fallback_on_total_failure PASSED")
