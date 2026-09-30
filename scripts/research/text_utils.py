"""Text utilities for Deep Research Agent.

Модуль не имеет внутренних зависимостей — только stdlib.
"""

from __future__ import annotations

SCOPE_ALIASES = {
    "chocolate": ["chocolate", "шоколад", "choco", "шоколадные изделия", "巧克力"],
    "sugar_confectionery": ["sugar confectionery", "сахаристые", "candy", "糖果", "sweets"],
    "biscuits": ["biscuits", "cookies", "печенье", "饼干", "crackers"],
    "all_confectionery": [
        "all confectionery",
        "кондитерские изделия",
        "整体糖果",
        "confectionery market",
        "confectionery",
    ],
}

GEOGRAPHY_ALIASES = {
    "China": ["china", "китай", "中国", "prc", "people's republic of china"],
    "Russia": ["russia", "россия", "rf", "russian federation"],
    "USA": ["usa", "united states", "сша", "america", "us"],
    "EU": ["eu", "european union", "ес", "europe"],
    "Global": ["global", "worldwide", "глобальный", "мир"],
}


def _relevance_score(text, query_terms):
    """Доля query-термов, встреченных в title+snippet. 0.0..1.0"""
    if not text or not query_terms:
        return 0.0
    tl = text.lower()
    hits = sum(1 for t in query_terms if t in tl)
    return hits / len(query_terms)


def normalize_scope(s):
    s = (s or "").lower().strip()
    for c, a in SCOPE_ALIASES.items():
        if s in [x.lower() for x in a]:
            return c
    return s or "unknown"


def normalize_geography(g):
    g = (g or "").lower().strip()
    for c, a in GEOGRAPHY_ALIASES.items():
        if g in [x.lower() for x in a]:
            return c
    return g or "unknown"
