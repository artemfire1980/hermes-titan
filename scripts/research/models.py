"""Evidence schema for Deep Research Agent.

Модуль не имеет внутренних зависимостей — только stdlib.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass, field


@dataclass
class Evidence:
    evidence_id: str = ""
    claim: str = ""
    metric: str | None = None
    value: float | None = None
    value_raw: str | None = None
    unit: str | None = None
    currency: str | None = None
    year: int | None = None
    period_start: str | None = None
    period_end: str | None = None
    forecast_type: str = "historical"
    source_url: str = ""
    source_title: str = ""
    source_type: str = "unknown"
    source_authority: float = 0.5
    evidence_quality: float = 0.5
    parent_source_id: str | None = None
    evidence_text: str = ""
    evidence_text_original: str | None = None
    market_scope: str = "unknown"
    geography: str = "unknown"
    verification_status: str = "unverified"
    verification_score: float = 0.0
    verification_method: str = "none"
    confidence: str = "medium"
    source_urls: list[str] = field(default_factory=list)
    subtopic: str = ""

    @property
    def dedup_key(self):
        norm = re.sub(r"\W+", " ", self.claim.lower()).strip()[:100]
        return hashlib.sha256(
            f"{norm}|{self.source_url}|{self.year}|{self.value}".encode()
        ).hexdigest()[:16]

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        known = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in d.items() if k in known})
