"""
Production-grade Executive Summary generator.

Architecture:
  Evidence → LLM (JSON) → Pydantic schema → Citation validator → (Repair ×1) → Render
  Failure → Deterministic fallback (top-claims by authority+metrics)

Key decisions (from expert review):
  - JSON scanner via raw_decode, NOT regex (handles nested JSON)
  - Pydantic validates STRUCTURE only, citation IDs validated separately
  - top_p=1.0 (not 0.1) to avoid artificial constraint stacking
  - max_tokens=1500 (not 2000) - enough for 7 bullets
  - Fallback uses top_claims_by_authority, not first N lines
"""
import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


# ============================================================================
# Schema layer: structure + text only, NO citation ID validation
# ============================================================================

class ExecutiveSummary(BaseModel):
    """Pydantic schema: validates structure only."""
    bullets: List[str] = Field(
        ...,
        min_length=5,
        max_length=7,
        description="5-7 bullet points with [N] citations",
    )

    @field_validator("bullets", mode="before")
    @classmethod
    def normalize_bullets(cls, bullets: List) -> List[str]:
        """
        Normalize bullets from various LLM formats to list[str].
        
        Accepts:
        - ["- Bullet [1]", ...]  (standard)
        - [{"text": "Bullet", "citation": 1}, ...]  (structured)
        - [{"text": "Bullet [1]"}, ...]  (mixed)
        """
        if not isinstance(bullets, list):
            raise ValueError(f"bullets must be a list, got {type(bullets)}")
        
        normalized = []
        for i, item in enumerate(bullets):
            if isinstance(item, str):
                # Already a string
                normalized.append(item)
            elif isinstance(item, dict):
                # Structured format: {"text": "...", "citation": N} or {"text": "... [N]"}
                text = item.get("text", "")
                if not text:
                    raise ValueError(f"Bullet {i + 1} dict missing 'text' field")
                
                # Check if citation already in text
                if not re.search(r"\[\d+\]", text):
                    # Add citation from dict
                    citation = item.get("citation") or item.get("citations")
                    if citation:
                        if isinstance(citation, list):
                            citation_str = "".join(f"[{c}]" for c in citation)
                        else:
                            citation_str = f"[{citation}]"
                        text = f"{text} {citation_str}"
                
                normalized.append(text)
            else:
                raise ValueError(f"Bullet {i + 1} must be string or dict, got {type(item)}")
        
        return normalized

    @field_validator("bullets")
    @classmethod
    def validate_bullets_structure(cls, bullets: List[str]) -> List[str]:
        """Check each bullet is a string with at least one [N] citation."""
        cleaned: List[str] = []
        citation_pattern = re.compile(r"\[(\d+)\]")

        for i, raw_bullet in enumerate(bullets):
            if not isinstance(raw_bullet, str):
                raise ValueError(f"Bullet {i + 1} is not a string")

            bullet = raw_bullet.strip()
            if bullet.startswith("- "):
                bullet = bullet[2:].strip()

            if len(bullet) < 20:
                raise ValueError(f"Bullet {i + 1} too short ({len(bullet)} chars)")
            if len(bullet) > 500:
                raise ValueError(f"Bullet {i + 1} too long ({len(bullet)} chars)")

            citations = [int(c) for c in citation_pattern.findall(bullet)]
            if not citations:
                raise ValueError(
                    f"Bullet {i + 1} has no [N] citation: '{bullet[:50]}...'"
                )

            cleaned.append(f"- {bullet}")

        return cleaned


# ============================================================================
# JSON extractor: scanner-based, NOT regex
# ============================================================================

def extract_last_valid_json(text: str) -> Dict[str, Any]:
    """
    Extracts last valid JSON object via JSONDecoder.raw_decode.
    
    Robust to:
    - <think>...</think> tags (DeepSeek-R1, QwQ)
    - ```json ... ``` markdown wrappers
    - Reasoning text before/after JSON
    - Nested JSON structures (unlike regex approaches)
    """
    decoder = json.JSONDecoder()
    clean_text = text.strip()
    
    # Remove <think>...</think> blocks (but not required - scanner ignores them)
    clean_text = re.sub(r"(?s)<think>.*?</think>", "", clean_text).strip()
    
    # Remove markdown code fences
    clean_text = re.sub(r"```(?:json)?\s*", "", clean_text)
    clean_text = re.sub(r"```\s*", "", clean_text).strip()

    # Find ALL JSON objects via scanner, return LAST valid one
    last_valid: Optional[Dict[str, Any]] = None
    pos = 0
    length = len(clean_text)

    while pos < length:
        # Find next '{'
        open_brace = clean_text.find("{", pos)
        if open_brace == -1:
            break

        try:
            obj, end_index = decoder.raw_decode(clean_text, open_brace)
            if isinstance(obj, dict) and "bullets" in obj:
                last_valid = obj
            pos = end_index
        except json.JSONDecodeError:
            pos = open_brace + 1
            continue

    if last_valid is not None:
        return last_valid

    # Fallback: try parsing entire text as JSON
    try:
        parsed = json.loads(clean_text)
        if isinstance(parsed, dict) and "bullets" in parsed:
            return parsed
    except json.JSONDecodeError:
        pass

    raise ValueError("No valid JSON object with 'bullets' field found in LLM response")


# ============================================================================
# Citation validator: separate from Pydantic (no runtime context dependency)
# ============================================================================

def validate_citations(bullets: List[str], valid_citation_ids: Set[int]) -> List[str]:
    """
    Validates that all [N] citations in bullets exist in valid_citation_ids.
    Returns cleaned bullets or raises ValueError.
    """
    citation_pattern = re.compile(r"\[(\d+)\]")
    cleaned: List[str] = []

    for i, bullet in enumerate(bullets):
        # Strip leading "- " if present
        text = bullet.strip()
        if text.startswith("- "):
            text = text[2:].strip()

        citations = [int(c) for c in citation_pattern.findall(text)]

        if valid_citation_ids:
            invalid_cids = [c for c in citations if c not in valid_citation_ids]
            if invalid_cids:
                raise ValueError(
                    f"Bullet {i + 1} cites invalid IDs {invalid_cids}. "
                    f"Valid IDs: {sorted(valid_citation_ids)}"
                )

        cleaned.append(f"- {text}")

    return cleaned


# ============================================================================
# Fallback: deterministic selection by authority, NOT first N lines
# ============================================================================

def top_claims_by_authority(
    evidences: List[Any],
    valid_citation_ids: Set[int],
    top_n: int = 7
) -> List[str]:
    """
    Selects top-N most authoritative claims from evidence.
    
    Scoring:
      - source_authority (0-1): primary factor
      - evidence_quality (0-1): secondary factor  
      - has_metric: +0.2 bonus
      - has_year: +0.1 bonus
    
    Returns formatted bullet strings with citations.
    """
    if not evidences:
        return []

    scored_claims = []
    citation_pattern = re.compile(r"\[(\d+)\]")

    for e in evidences:
        # Skip evidences with invalid citations
        if hasattr(e, 'citation_number') and e.citation_number not in valid_citation_ids:
            continue

        # Calculate score
        authority = getattr(e, 'source_authority', 0.5)
        quality = getattr(e, 'evidence_quality', 0.5)
        has_metric = 1.0 if getattr(e, 'metric', None) else 0.0
        has_year = 1.0 if getattr(e, 'year', None) else 0.0

        score = authority * 0.5 + quality * 0.3 + has_metric * 0.2 + has_year * 0.1

        claim = getattr(e, 'claim', '').strip()
        citation_num = getattr(e, 'citation_number', None)

        if claim and citation_num and citation_num in valid_citation_ids:
            scored_claims.append((score, claim, citation_num))

    # Sort by score descending, take top N
    scored_claims.sort(key=lambda x: x[0], reverse=True)
    top_claims = scored_claims[:top_n]

    # Format as bullet points
    bullets = []
    for score, claim, cid in top_claims:
        # Ensure claim doesn't already have citation
        if not citation_pattern.search(claim):
            claim = f"{claim} [{cid}]"
        bullets.append(f"- {claim}")

    return bullets


def generate_fallback_summary(
    facts_text: str,
    valid_citation_ids: Set[int],
    evidences: Optional[List[Any]] = None
) -> List[str]:
    """
    Deterministic fallback when LLM generation fails.
    
    Priority:
      1. Use top_claims_by_authority if evidences provided
      2. Otherwise extract claims with valid citations from facts_text
    """
    # Priority 1: use structured evidences if available
    if evidences:
        bullets = top_claims_by_authority(evidences, valid_citation_ids, top_n=7)
        if len(bullets) >= 5:
            return bullets

    # Priority 2: extract from facts_text
    bullets = []
    citation_pattern = re.compile(r"\[(\d+)\]")
    lines = facts_text.split("\n")

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        cids = [int(c) for c in citation_pattern.findall(stripped)]
        if not cids:
            continue

        # Check all citations are valid
        if valid_citation_ids and not all(c in valid_citation_ids for c in cids):
            continue

        if not stripped.startswith("- "):
            stripped = f"- {stripped}"

        bullets.append(stripped)
        if len(bullets) >= 7:
            break

    # If we have enough bullets, return them
    if len(bullets) >= 5:
        return bullets[:7]

    # Emergency fallback: create minimal valid output
    if not bullets and valid_citation_ids:
        min_cid = min(valid_citation_ids)
        bullets = [
            f"- Исследование содержит данные по теме [{min_cid}]",
            f"- Найдено несколько релевантных источников [{min_cid}]",
            f"- Требуется дополнительный анализ для детальных выводов [{min_cid}]",
            f"- Основные факты собраны из открытых источников [{min_cid}]",
            f"- Полный отчёт доступен в прикреплённом документе [{min_cid}]",
        ]

    return bullets[:7]


# ============================================================================
# Generator: main pipeline
# ============================================================================

@dataclass
class SummaryConfig:
    """Configuration for summary generation."""
    model: str = "auto"
    temperature: float = 0.0
    top_p: float = 1.0  # NOT 0.1 - avoid artificial constraint stacking
    max_tokens: int = 1500  # Enough for 7 bullets, not 2000
    max_retries: int = 1
    use_fusion: bool = False  # CRITICAL: disable fusion for structured output


@dataclass
class SummaryResult:
    """Result of summary generation."""
    bullets: List[str]
    source: str  # "llm" or "fallback"
    attempts: int
    errors: List[str] = field(default_factory=list)


class ExecutiveSummaryGenerator:
    """Production-grade Executive Summary generator."""

    def __init__(self, llm_chat_func: Any, config: Optional[SummaryConfig] = None):
        """
        Args:
            llm_chat_func: Async callable with signature:
                async def chat(prompt, task_type, max_tokens, temp, use_fusion) -> str
            config: SummaryConfig instance
        """
        self.llm_chat = llm_chat_func
        self.config = config or SummaryConfig()

    def _build_prompts(
        self,
        topic: str,
        facts: str,
        valid_citation_ids: Set[int]
    ) -> tuple[str, str]:
        """Build system and user prompts for JSON generation."""
        sorted_ids = sorted(valid_citation_ids)
        min_id = sorted_ids[0] if sorted_ids else 1

        system_prompt = (
            "You are a strict data formatting engine. "
            "Output ONLY a valid JSON object. "
            "Do NOT include thinking, reasoning, commentary, or Markdown wrappers."
        )

        user_prompt = f"""<topic>{topic}</topic>

<facts>
{facts}
</facts>

<instructions>
Сгенерируй Executive Summary СТРОГО НА РУССКОМ ЯЗЫКЕ.

КРИТИЧНО:
- Все bullet points должны быть на РУССКОМ языке
- Даже если входные данные (facts, evidences) на английском — ОТВЕТ на русском
- НЕ используй английский язык в выводе
- НЕ смешивай русский и английский
- Переводи факты на русский, сохраняя цифры и цитаты [N].
Требования:
1. Ровно от 5 до 7 пунктов (bullet points).
2. Каждый пункт — законченное утверждение на русском языке (20-300 символов).
3. Каждый пункт ОБЯЗАН заканчиваться цитатой в формате [N].
4. Разрешено использовать ТОЛЬКО существующие номера ID цитат: {sorted_ids}
5. Пиши своими словами, перефразируй факты.
6. Верни ТОЛЬКО JSON объект следующего формата:
{{"bullets": ["- Пункт 1 [{min_id}]", "- Пункт 2 [{min_id}]"]}}
</instructions>

<example>
{{
  "bullets": [
    "- Кантонская выставка 2025 года станет крупнейшей торговой площадкой Китая [{min_id}]",
    "- В мероприятии примут участие свыше 25 000 компаний со всего мира [{min_id}]",
    "- Основное внимание будет уделено секторам электроники и автоматизации [{min_id}]",
    "- Ожидается прибытие более 200 тысяч международных закупщиков [{min_id}]",
    "- Выставка традиционно проходит в два этапа в Гуанчжоу [{min_id}]"
  ]
}}
</example>"""

        return system_prompt, user_prompt

    async def generate_summary(
        self,
        topic: str,
        facts: str,
        valid_citation_ids: Set[int],
        evidences: Optional[List[Any]] = None,
    ) -> SummaryResult:
        """
        Generate Executive Summary with validation, repair, and fallback.
        
        Pipeline:
          1. LLM generation (JSON mode)
          2. JSON extraction (scanner-based)
          3. Pydantic schema validation
          4. Citation validation (deterministic)
          5. On failure: repair retry (1 attempt)
          6. On failure: deterministic fallback
        """
        system_prompt, user_prompt = self._build_prompts(topic, facts, valid_citation_ids)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        errors = []
        attempts = 0
        raw_content = ""  # Initialize before loop to avoid UnboundLocalError on LLM exception

        for attempt in range(self.config.max_retries + 1):
            attempts += 1
            try:
                # Build request params
                params = {
                    "model": self.config.model,
                    "messages": messages,
                    "temperature": self.config.temperature,
                    "top_p": self.config.top_p,
                    "max_tokens": self.config.max_tokens,
                }

                # Build prompt from messages (take last user message)
                user_prompt = ""
                for msg in messages:
                    if msg["role"] == "user":
                        user_prompt = msg["content"]
                
                # Call LLM via provided callable (LLMGateway.chat or similar)
                raw_content = await self.llm_chat(
                    user_prompt,
                    task_type="summary",
                    max_tokens=self.config.max_tokens,
                    temp=self.config.temperature,
                    use_fusion=self.config.use_fusion
                )
                
                # Step 1: JSON extraction (scanner-based)
                json_data = extract_last_valid_json(raw_content)

                # Step 2: Pydantic schema validation
                summary_model = ExecutiveSummary.model_validate(json_data)

                # Step 3: Citation validation (separate from Pydantic)
                validated_bullets = validate_citations(
                    summary_model.bullets,
                    valid_citation_ids
                )

                logger.info(f"Summary generated successfully on attempt {attempts}")
                return SummaryResult(
                    bullets=validated_bullets,
                    source="llm",
                    attempts=attempts,
                    errors=errors,
                )

            except Exception as e:
                error_msg = f"Attempt {attempts} failed: {str(e)}"
                errors.append(error_msg)
                logger.warning(error_msg)

                if attempt < self.config.max_retries:
                    # Repair retry with error feedback
                    repair_prompt = (
                        f"Предыдущий ответ вызвал ошибку валидации:\n"
                        f"{str(e)}\n\n"
                        f"Исправь ошибку и выдай ТОЛЬКО валидный JSON с 5-7 пунктами "
                        f"на русском языке. Допустимые citation IDs: {sorted(valid_citation_ids)}"
                    )
                    # Only add assistant message if we got any response
                    # (raw_content may be empty if LLM call raised exception)
                    if raw_content:
                        messages.append({"role": "assistant", "content": raw_content})
                    messages.append({"role": "user", "content": repair_prompt})

        # All retries exhausted - use fallback
        logger.warning("All LLM attempts failed. Using deterministic fallback.")
        fallback_bullets = generate_fallback_summary(
            facts, valid_citation_ids, evidences
        )

        return SummaryResult(
            bullets=fallback_bullets,
            source="fallback",
            attempts=attempts,
            errors=errors,
        )


def render_markdown(bullets: List[str]) -> str:
    """Convert bullet list to Markdown format."""
    return "\n".join(bullets)
