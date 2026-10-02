from __future__ import annotations

import re
from collections import defaultdict
from difflib import SequenceMatcher

from research.text_utils import normalize_geography

"""Evidence validation and verification for Deep Research Agent."""


class FactValidator:
    PATTERNS = [
        r"(?i)\bcompany\s+[a-z0-9]\b",
        r"(?i)\blocal company\b",
        r"(?i)\bplayer\s+\d+\b",
        r"(?i)\bигрок\s+\d+\b",
        r"(?i)\bcompany\s+\d+\b",
        r"\bXXX+\b",
        r"(?i)\bTBD\b",
    ]

    @classmethod
    def validate(cls, e):
        """Возвращает (hard, soft). hard -> drop, soft -> confidence=low."""
        hard = []
        soft = []
        text = f"{e.claim} {e.evidence_text}"
        for p in cls.PATTERNS:
            if re.search(p, text):
                hard.append(f"placeholder: {p}")
        if e.metric == "market_share":
            if not e.market_scope or e.market_scope == "unknown":
                soft.append("market_share без scope")
            if not e.geography or e.geography == "unknown":
                soft.append("market_share без geo")
            if not e.year:
                soft.append("market_share без year")
        if e.value is None and e.value_raw:
            m = re.search(
                r"(-?\d+(?:[.,]\d+)?)", e.value_raw.replace("\u00a0", "").replace(" ", "")
            )
            if m:
                try:
                    e.value = float(m.group(1).replace(",", "."))
                except ValueError:
                    pass
        return hard, soft


class EvidenceVerifier:
    @classmethod
    def verify(cls, ev_text, doc):
        if not ev_text or not doc:
            return False, "none", 0.0
        en = re.sub(r"\s+", " ", ev_text.lower()).strip()
        dn = re.sub(r"\s+", " ", doc.lower()).strip()

        # Проверка чисел: все числа из evidence должны быть в документе
        # Нормализуем десятичные разделители: 22,3 -> 22.3
        def _norm(s: str) -> str:
            return s.replace(",", ".")

        ev_nums = {_norm(n) for n in re.findall(r"\d+(?:[.,]\d+)?", ev_text)}
        doc_nums = {_norm(n) for n in re.findall(r"\d+(?:[.,]\d+)?", doc)}
        if ev_nums and not ev_nums.issubset(doc_nums):
            # Числа в evidence не найдены в документе - это выдумка
            return False, "number_mismatch", 0.0
        if en[:200] in dn:
            return True, "exact", 1.0
        w = min(len(en), 500)
        # Адаптивные пороги: для коротких текстов ниже (DEC-017)
        if w >= 30:
            step = max(w // 2, 100)
            for i in range(0, max(1, len(dn) - w), step):
                r = SequenceMatcher(None, en[:w], dn[i : i + w]).ratio()
                if r > 0.70:
                    return True, "fuzzy", r
        # Нормализация единиц измерения и токенизация (DEC-017)
        UNIT_MAP = {"млрд": "миллиардов", "млн": "миллионов", "тыс": "тысяч"}

        def _expand_units(s):
            for abbr, full in UNIT_MAP.items():
                s = re.sub(rf"\b{abbr}\b\.?", full, s)
            return s

        en_norm = _expand_units(en.replace(",", "."))
        dn_norm = _expand_units(dn.replace(",", "."))
        et = set(re.findall(r"[a-zа-яё0-9]+", en_norm))
        dt = set(re.findall(r"[a-zа-яё0-9]+", dn_norm))
        if len(et) >= 3:
            ov = len(et & dt) / len(et)
            if ov > 0.60:
                return True, "token_overlap", ov
        return False, "none", 0.0


class ConflictDict(dict):
    """Dict с атрибутным доступом — совместимость с .type и ["conflict_type"]."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)


class ConflictDetector:
    @classmethod
    def detect(cls, evidences):
        groups = defaultdict(list)
        for e in evidences:
            if e.value is None or not e.metric:
                continue
            # Убираем scope из ключа - он уже нормализован через aliases
            key = (e.metric, normalize_geography(e.geography), e.unit, e.currency)
            groups[key].append(e)
        conflicts = []
        for key, grp in groups.items():
            if len(grp) < 2:
                continue
            vals = [e.value for e in grp]
            mn, mx = min(vals), max(vals)
            if mn == 0:
                continue
            div = (mx - mn) / mn
            stypes = {e.source_type for e in grp}
            years = {e.year for e in grp if e.year}
            scopes = {e.market_scope for e in grp}
            if len(years) > 1:
                ct, th = "TIME_DIFF", 0.30
            elif len(scopes) > 1:
                ct, th = "SCOPE_DIFF", 0.30
            elif len(stypes) > 1:
                ct, th = "METHODOLOGY_DIFF", 0.25
            else:
                ct, th = "DIRECT_CONFLICT", 0.15
            if div > th:
                conflicts.append(
                    ConflictDict(
                        {
                            "metric_key": [str(k) for k in key],
                            "conflict_type": ct,
                            "type": ct,
                            "divergence": round(div, 3),
                            "threshold": th,
                            "evidences": [
                                {
                                    "evidence_id": e.evidence_id,
                                    "value": e.value,
                                    "value_raw": e.value_raw,
                                    "source_url": e.source_url,
                                    "source_type": e.source_type,
                                    "year": e.year,
                                }
                                for e in grp
                            ],
                            "resolution_hint": {
                                "DIRECT_CONFLICT": "report both",
                                "METHODOLOGY_DIFF": "explain methodology",
                                "SCOPE_DIFF": "clarify scope",
                                "TIME_DIFF": "note time diff",
                            }.get(ct, "report both"),
                        }
                    )
                )
        return conflicts
