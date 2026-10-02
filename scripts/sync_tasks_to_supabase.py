#!/usr/bin/env python3
"""Sync local task ledger to Supabase (idempotent upsert)."""

import json
import os
import sqlite3
import sys
from pathlib import Path

from supabase import create_client

DB_PATH = Path.home() / "ai-system" / "data" / "tasks.db"


from env_utils import default_candidates, load_env


def main():
    load_env(default_candidates())

    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        print("❌ SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY missing")
        sys.exit(1)

    if not DB_PATH.exists():
        print("ℹ️ Local task DB not found, nothing to sync")
        return

    supabase = create_client(url, key)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM tasks ORDER BY timestamp DESC LIMIT 100").fetchall()
    conn.close()

    if not rows:
        print("ℹ️ No tasks to sync")
        return

    synced = 0
    errors = 0
    for row in rows:
        data = dict(row)
        # Convert JSON fields
        for json_key in ("changed_files", "pre_existing_changes"):
            if data.get(json_key):
                try:
                    data[json_key] = json.loads(data[json_key])
                except (json.JSONDecodeError, TypeError):
                    data[json_key] = None
        try:
            supabase.table("tasks").upsert(data).execute()
            synced += 1
        except Exception as e:
            errors += 1
            print(f"⚠️ {data.get('task_id')}: {e}")

    print(
        f"✅ Synced {synced}/{len(rows)} tasks to Supabase"
        + (f" ({errors} errors)" if errors else "")
    )


if __name__ == "__main__":
    main()
