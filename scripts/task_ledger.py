#!/usr/bin/env python3
"""Task Ledger — SQLite storage for Aider execution history.

Protects against Hermes context compression loss.
Single source of truth for all coding tasks.
"""
import sqlite3
import sys
import json
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path.home() / "ai-system" / "data" / "tasks.db"

def get_conn():
    """Get SQLite connection with WAL mode for concurrency."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    
    # Create table if not exists
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
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_timestamp ON tasks(timestamp)")
    conn.commit()
    return conn

def log_task(task_id, project, task, status, **kwargs):
    """Log task execution to SQLite."""
    with get_conn() as conn:
        # Convert lists to JSON
        if 'changed_files' in kwargs and kwargs['changed_files']:
            kwargs['changed_files'] = json.dumps(kwargs['changed_files'])
        if 'pre_existing_changes' in kwargs and kwargs['pre_existing_changes']:
            kwargs['pre_existing_changes'] = json.dumps(kwargs['pre_existing_changes'])
        
        # Build columns and values
        cols = ['task_id', 'timestamp', 'project', 'task', 'status']
        vals = [task_id, datetime.now(timezone.utc).isoformat(), project, task, status]
        
        for key, val in kwargs.items():
            cols.append(key)
            vals.append(val)
        
        placeholders = ','.join(['?'] * len(vals))
        col_names = ','.join(cols)
        
        conn.execute(f"""
            INSERT OR REPLACE INTO tasks ({col_names})
            VALUES ({placeholders})
        """, vals)
        conn.commit()

def get_recent_tasks(limit=10):
    """Get recent tasks for display."""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT * FROM tasks 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(row) for row in rows]

def get_task(task_id):
    """Get specific task by ID."""
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
        return dict(row) if row else None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: task_ledger.py [init|list|get <task_id>]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "init":
        get_conn()
        print(f"✅ Task ledger initialized: {DB_PATH}")
    
    elif cmd == "list":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        tasks = get_recent_tasks(limit)
        for t in tasks:
            status_icon = "✅" if t['status'] == 'COMPLETED' else "❌"
            print(f"{status_icon} {t['timestamp'][:16]} | {t['project'][-30:]} | {t['status']}")
            if t.get('commit_message'):
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
