#!/usr/bin/env python3
"""Task Ledger — SQLite storage for Aider execution history.

Protects against Hermes context compression loss.
Single source of truth for all coding tasks.

Schema versioning via PRAGMA user_version.
UPSERT semantics: preserves started_at, updates only provided fields.
"""

import json
import sqlite3
import sys
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path.home() / "ai-system" / "data" / "tasks.db"
SCHEMA_VERSION = 2


def _utc_now():
    return datetime.now(UTC).isoformat()


def _ensure_schema(conn):
    """Create or migrate schema. Idempotent via PRAGMA user_version."""
    ver = conn.execute("PRAGMA user_version").fetchone()[0]

    if ver >= SCHEMA_VERSION:
        return

    # Base table (v1)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            project TEXT NOT NULL,
            task TEXT NOT NULL,
            status TEXT NOT NULL,
            initial_head TEXT,
            final_head TEXT,
            commit_hash TEXT,
            commit_message TEXT,
            changed_files TEXT,
            exit_code INTEGER,
            elapsed_seconds REAL,
            error_message TEXT,
            dirty_before INTEGER,
            pre_existing_changes TEXT
        )
    """)

    # v2 migration: add started_at / finished_at
    if ver < 2:
        existing = {r[1] for r in conn.execute("PRAGMA table_info(tasks)").fetchall()}
        if "started_at" not in existing:
            conn.execute("ALTER TABLE tasks ADD COLUMN started_at TEXT")
        if "finished_at" not in existing:
            conn.execute("ALTER TABLE tasks ADD COLUMN finished_at TEXT")
        # Backfill started_at for existing rows from timestamp
        conn.execute(
            "UPDATE tasks SET started_at = COALESCE(started_at, timestamp) WHERE started_at IS NULL"
        )

    conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_timestamp ON tasks(timestamp)")
    conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
    conn.commit()


def get_conn():
    """Get SQLite connection with WAL mode for concurrency."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    _ensure_schema(conn)
    return conn


def log_task(task_id, project, task, status, **kwargs):
    """Log task execution. UPSERT: updates only provided fields, preserves started_at.

    Special handling:
    - timestamp: updated on every call (last activity)
    - started_at: set on first INSERT, never overwritten
    - finished_at: set when status is terminal
    """
    with closing(get_conn()) as conn:
        # JSON-encode lists
        if kwargs.get("changed_files"):
            kwargs["changed_files"] = json.dumps(kwargs["changed_files"])
        if kwargs.get("pre_existing_changes"):
            kwargs["pre_existing_changes"] = json.dumps(kwargs["pre_existing_changes"])

        now = _utc_now()
        terminal = {
            "COMPLETED",
            "FAILED",
            "AIDER_FAILED",
            "TIMEOUT",
            "POST_FLIGHT_FAILED",
            "DIRTY_REPOSITORY",
            "INVALID_PROJECT",
            "NOT_GIT_REPOSITORY",
            "GIT_STATUS_FAILED",
            "GIT_CONFLICT",
            "AIDER_BUSY",
            "AIDER_NOT_FOUND",
            "NVIDIA_API_KEY_MISSING",
            "NO_ORIGIN_REMOTE",
            "DETACHED_HEAD",
        }

        # Columns for INSERT
        cols = ["task_id", "timestamp", "started_at", "project", "task", "status"]
        vals = [task_id, now, now, project, task, status]

        for key, val in kwargs.items():
            cols.append(key)
            vals.append(val)

        placeholders = ",".join(["?"] * len(vals))
        col_names = ",".join(cols)

        # Update clause: all except task_id, started_at
        update_cols = [c for c in cols if c not in ("task_id", "started_at")]
        update_clause = ",".join(f"{c}=excluded.{c}" for c in update_cols)

        # finished_at handling
        if status in terminal:
            finished_at_set = ", finished_at = excluded.timestamp"
        else:
            finished_at_set = ""

        conn.execute(
            f"""
            INSERT INTO tasks ({col_names})
            VALUES ({placeholders})
            ON CONFLICT(task_id) DO UPDATE SET
                {update_clause}
                {finished_at_set}
        """,
            vals,
        )
        conn.commit()


def get_recent_tasks(limit=10):
    """Get recent tasks for display."""
    with closing(get_conn()) as conn:
        rows = conn.execute(
            """
            SELECT * FROM tasks
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]


def get_task(task_id):
    """Get specific task by ID."""
    with closing(get_conn()) as conn:
        row = conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
        return dict(row) if row else None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: task_ledger.py [init|list|get <task_id>]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "init":
        get_conn()
        with closing(get_conn()) as conn:
            ver = conn.execute("PRAGMA user_version").fetchone()[0]
        print(f"✅ Task ledger initialized: {DB_PATH} (schema v{ver})")

    elif cmd == "list":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        tasks = get_recent_tasks(limit)
        for t in tasks:
            status_icon = "✅" if t["status"] == "COMPLETED" else "❌"
            print(f"{status_icon} {t['timestamp'][:16]} | {t['project'][-30:]} | {t['status']}")
            if t.get("commit_message"):
                print(f"   └─ {t['commit_message']}")

    elif cmd == "get" and len(sys.argv) > 2:
        task = get_task(sys.argv[2])
        if task:
            print(json.dumps(task, indent=2, ensure_ascii=False))
        else:
            print(f"Task {sys.argv[2]} not found")

    else:
        print("Unknown command")
        sys.exit(1)
