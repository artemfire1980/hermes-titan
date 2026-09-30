"""Checkpoint manager for Deep Research Agent.

Модуль не имеет внутренних зависимостей — только stdlib.
"""

from __future__ import annotations

import json
import os
from datetime import datetime


class CheckpointManager:
    SCHEMA_VERSION = 2

    def __init__(self, d):
        self.d = d
        d.mkdir(parents=True, exist_ok=True)

    def save(self, rid, state):
        p = self.d / f"{rid}.json"
        t = p.with_suffix(".json.tmp")
        state["schema_version"] = self.SCHEMA_VERSION
        state["last_updated"] = datetime.now().isoformat()
        with open(t, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        t.replace(p)

    def load(self, rid):
        p = self.d / f"{rid}.json"
        if not p.exists():
            return None
        try:
            s = json.loads(p.read_text(encoding="utf-8"))
            return s if s.get("schema_version") == self.SCHEMA_VERSION else None
        except:
            return None

    def cleanup(self, rid):
        p = self.d / f"{rid}.json"
        if p.exists():
            p.unlink()
