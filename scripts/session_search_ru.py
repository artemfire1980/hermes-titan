#!/usr/bin/env python3
"""Поиск по истории сессий Hermes с поддержкой кириллицы (trigram FTS).

Использование:
    python3 session_search_ru.py "Самсонов"
    python3 session_search_ru.py "клиенты кондитерка" --limit 5

Возвращает: session_id, title, matched snippet, link.
"""

import argparse
import sqlite3
import sys
from pathlib import Path

DB = Path("/mnt/ai-ssd/hermes/state.db")


def search(query: str, limit: int = 10) -> list[dict]:
    conn = sqlite3.connect(str(DB))
    cur = conn.cursor()
    # Trigram FTS — точный поиск по кириллице
    cur.execute(
        """
        SELECT m.session_id, substr(m.content, 1, 200) as snippet, m.timestamp,
               s.title, s.message_count
        FROM messages_fts_trigram f
        JOIN messages m ON m.id = f.rowid
        LEFT JOIN sessions s ON s.id = m.session_id
        WHERE messages_fts_trigram MATCH ?
        ORDER BY m.timestamp DESC
        LIMIT ?
        """,
        (query, limit),
    )
    results = []
    for sid, snippet, ts, title, msgs in cur.fetchall():
        results.append(
            {
                "session_id": sid,
                "snippet": snippet,
                "timestamp": ts,
                "title": title or "?",
                "message_count": msgs,
                "link": f"@session:default/{sid}",
            }
        )
    conn.close()
    return results


def main():
    parser = argparse.ArgumentParser(description="Поиск по истории сессий (кириллица)")
    parser.add_argument("query", help="Поисковый запрос")
    parser.add_argument("--limit", type=int, default=10, help="Максимум результатов")
    args = parser.parse_args()

    results = search(args.query, args.limit)
    if not results:
        print(f"Ничего не найдено по запросу: {args.query}")
        return 1

    print(f"Найдено: {len(results)}")
    for i, r in enumerate(results, 1):
        print(f"\n{i}. {r['title']}")
        print(f"   session_id: {r['session_id']}")
        print(f"   messages: {r['message_count']}")
        print(f"   snippet: {r['snippet'][:150].strip()}...")
        print(f"   link: {r['link']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
