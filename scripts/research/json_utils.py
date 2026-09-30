"""JSON repair and resilient parsing for Deep Research Agent.

Модуль не имеет внутренних зависимостей — только stdlib.
"""

from __future__ import annotations

import json
import logging
import re

logger = logging.getLogger(__name__)


def repair_json(text):
    s = text.strip()
    s = re.sub(r"^\s*```(?:json)?\s*", "", s)
    s = re.sub(r"\s*```\s*$", "", s)
    start = min([i for i in (s.find("{"), s.find("[")) if i != -1], default=-1)
    if start > 0:
        s = s[start:]
    s = re.sub(r",\s*([}\]])", r"\1", s)
    s = (
        s.replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2018", "'")
        .replace("\u2019", "'")
    )
    s = re.sub(r"\bNaN\b|\bInfinity\b|\b-Infinity\b", "null", s)
    s = re.sub(r"\bNone\b", "null", s)
    s = re.sub(r"\bTrue\b", "true", s)
    s = re.sub(r"\bFalse\b", "false", s)
    # Close unbalanced brackets
    stack = []
    in_str = False
    esc = False
    for ch in s:
        if esc:
            esc = False
            continue
        if ch == "\\":
            esc = True
            continue
        if ch == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch in "{[":
            stack.append(ch)
        elif ch in "}]":
            if stack:
                stack.pop()
    if in_str:
        s += '"'
    for opener in reversed(stack):
        s += "}" if opener == "{" else "]"
    return s.strip()


def parse_json_resilient(text, array_key="evidences"):
    # Normalize empty / whitespace-only JSON (any spacing, fences, [] or {})
    normalized = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", text.strip()).strip()
    if (
        not normalized
        or re.fullmatch(r"\{\s*\}", normalized)
        or re.fullmatch(r"\[\s*\]", normalized)
    ):
        return {"evidences": []}
    for candidate in (text, repair_json(text)):
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                # Treat empty dict as no evidences
                if not parsed or all(v is None or v == [] or v == {} for v in parsed.values()):
                    return {"evidences": []}
                return parsed
            if isinstance(parsed, list):
                return {"evidences": parsed}
        except:
            continue
    # Salvage individual objects
    objs = []
    starts = []
    in_str = False
    esc = False
    for i, ch in enumerate(text):
        if esc:
            esc = False
            continue
        if ch == "\\":
            esc = True
            continue
        if ch == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch == "{":
            starts.append(i)
        elif ch == "}" and starts:
            start = starts.pop()
            try:
                obj = json.loads(repair_json(text[start : i + 1]))
                if isinstance(obj, dict) and obj:
                    objs.append(obj)
            except:
                continue
    if objs:
        items = [o for o in objs if array_key not in o]
        if items:
            logger.warning("JSON salvaged: %d objects recovered", len(items))
        return {array_key: items}
    return None
