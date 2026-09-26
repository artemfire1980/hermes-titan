#!/usr/bin/env python3
"""Просмотр истории задач Aider из task_ledger БД."""
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path.home() / "ai-system" / "data" / "tasks.db"

def show_stats():
    """Показать общую статистиистику."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    print("📊 СТАТИСТИКА TASK LEDGER")
    print("=" * 60)
    
    total = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    print(f"Всего задач: {total}")
    
    print("\n📈 По статусам:")
    for row in conn.execute("SELECT status, COUNT(*) as cnt FROM tasks GROUP BY status ORDER BY cnt DESC"):
        print(f"  {row['status']:20s} {row['cnt']:3d}")
    
    print("\n📁 По проектам:")
    for row in conn.execute("SELECT project, COUNT(*) as cnt FROM tasks GROUP BY project ORDER BY cnt DESC"):
        print(f"  {row['project']:40s} {row['cnt']:3d}")
    
    conn.close()

def show_recent(limit=10):
    """Показать последние N задач."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    print(f"\n📋 ПОСЛЕДНИЕ {limit} ЗАДАЧ")
    print("=" * 80)
    
    rows = conn.execute("""
        SELECT task_id, timestamp, project, task, status, elapsed_seconds, exit_code
        FROM tasks ORDER BY timestamp DESC LIMIT ?
    """, (limit,)).fetchall()
    
    for r in rows:
        status_icon = "✅" if r['status'] == 'COMPLETED' else "❌" if r['status'] in ('FAILED', 'TIMEOUT') else "⏳"
        print(f"{status_icon} {r['timestamp'][:16]} | {r['status']:12s} | {r['elapsed_seconds'] or 0:.0f}s | {r['project']}")
        print(f"  📝 {r['task'][:70]}{'...' if len(r['task']) > 70 else ''}")
        print()
    
    conn.close()

def show_task(task_id):
    """Показать детали конкретной задачи."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    row = conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
    if not row:
        print(f"❌ Задача {task_id} не найдена")
        return
    
    print(f"\n🔍 ДЕТАЛИ ЗАДАЧИ {task_id}")
    print("=" * 80)
    for key in row.keys():
        val = row[key]
        if val is not None and val != "" and val != 0:
            print(f"  {key:20s}: {val}")
    
    conn.close()

if __name__ == "__main__":
    if not DB_PATH.exists():
        print(f"❌ БД не найдена: {DB_PATH}")
        sys.exit(1)
    
    if len(sys.argv) == 1 or sys.argv[1] == "stats":
        show_stats()
    elif sys.argv[1] == "recent":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        show_recent(limit)
    elif sys.argv[1] == "show" and len(sys.argv) > 2:
        show_task(sys.argv[2])
    else:
        print("Использование:")
        print("  ledger-viewer.py stats          — статистика")
        print("  ledger-viewer.py recent [N]     — последние N задач")
        print("  ledger-viewer.py show <task_id> — детали задачи")

