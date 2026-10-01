from __future__ import annotations

import re
import urllib.parse

"""Source quality scoring for Deep Research Agent."""


class SourceQualityScorer:
    HIGH = {
        "statista.com",
        "reuters.com",
        "bloomberg.com",
        "worldbank.org",
        "imf.org",
        "gov.cn",
        "rosstat.gov.ru",
        "nature.com",
        "science.org",
        "ft.com",
        "wsj.com",
        "businesstat.ru",
        "euromonitor.com",
        "minpromtorg.gov.ru",
        "government.ru",
    }
    LOW = [
        "blogspot",
        "medium.com",
        "wordpress",
        "seo-",
        "marketing-",
        "top10",
        "wikihow",
        "livejournal",
    ]

    @classmethod
    def authority(cls, url):
        d = urllib.parse.urlparse(url).netloc.lower()
        for h in cls.HIGH:
            if d == h or d.endswith(f".{h}"):
                return 1.0
        if d.endswith((".gov", ".edu", ".ac.uk", ".ac.cn", ".gov.ru")):
            return 0.9
        if any(p in d for p in cls.LOW):
            return 0.3
        return 0.5

    @classmethod
    def quality(cls, text, has_nums):
        s = 0.5
        if has_nums:
            s += 0.2
        if any(
            m in text.lower() for m in ["по данным", "according to", "согласно", "по информации"]
        ):
            s += 0.2
        if re.search(r"\b(19|20)\d{2}\b", text):
            s += 0.1
        return min(round(s, 4), 1.0)

    @classmethod
    def guess_type(cls, url, title=""):
        u = url.lower()
        d = urllib.parse.urlparse(u).netloc
        if u.endswith(".pdf"):
            return "annual_report" if "report" in u else "document"
        if d.endswith((".gov", ".gov.ru", "gov.cn")) or "rosstat" in d:
            return "official_stat"
        if any(k in d for k in ["statista", "euromonitor", "businesstat", "mintel"]):
            return "industry_report"
        if any(
            k in d for k in ["reuters", "bloomberg", "interfax", "ria", "tass", "kommersant", "rbc"]
        ):
            return "news"
        if any(k in d for k in ["blogspot", "medium", "wordpress", "habr"]):
            return "blog"
        return "news"


class ConfidenceScorer:
    @classmethod
    def score(cls, e):
        s = 0
        if e.source_authority > 0.8:
            s += 2
        elif e.source_authority > 0.6:
            s += 1
        if e.evidence_quality > 0.7:
            s += 2
        elif e.evidence_quality > 0.5:
            s += 1
        if e.year and 2020 <= e.year <= 2026:
            s += 1
        if e.value is not None:
            s += 1
        if e.verification_status == "verified_exact":
            s += 2
        elif e.verification_status.startswith("verified_"):
            s += 1
        if s >= 6:
            return "high"
        if s >= 4:
            return "medium"
        return "low"
