from __future__ import annotations

from difflib import SequenceMatcher

"""Source lineage detection for Deep Research Agent."""


def detect_lineage(evidences):
    """Prefilter O(n) → fuzzy только внутри групп. Вместо O(n²)."""
    from collections import defaultdict

    groups = defaultdict(list)
    for e in evidences:
        title = (e.source_title or "").strip().lower()
        if title:
            groups[title].append(e)
    for grp in groups.values():
        if len(grp) < 2:
            continue
        for i, a in enumerate(grp):
            for b in grp[i + 1 :]:
                if b.parent_source_id:
                    continue
                if (
                    a.source_title
                    and b.source_title
                    and SequenceMatcher(
                        None, a.source_title.lower(), b.source_title.lower()
                    ).ratio()
                    > 0.9
                ):
                    b.parent_source_id = a.evidence_id
    return len(set(e.parent_source_id or e.evidence_id for e in evidences))
