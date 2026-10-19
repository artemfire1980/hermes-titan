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


def _parse_bound(value: str | None) -> float | None:
    """'today' | 'yesterday' | 'YYYY-MM-DD' -> unix ts, или None."""
    if not value:
        return None
    conn = sqlite3.connect(str(DB))
    cur = conn.cursor()
    if value == "today":
        ts = cur.execute("SELECT strftime('%s','now','start of day')").fetchone()[0]
    elif value == "yesterday":
        ts = cur.execute("SELECT strftime('%s','now','start of day','-1 day')").fetchone()[0]
    else:
        ts = cur.execute("SELECT strftime('%s', ?)", (value,)).fetchone()[0]
    conn.close()
    if ts is None:
        raise SystemExit(f"Не понял дату: {value!r} (нужно YYYY-MM-DD|today|yesterday)")
    return float(ts)


def search(
    query: str,
    limit: int = 10,
    before: str | None = None,
    after: str | None = None,
) -> list[dict]:
    conn = sqlite3.connect(str(DB))
    cur = conn.cursor()
    before_ts = _parse_bound(before)
    after_ts = _parse_bound(after)

    # Собираем С ЗАПАСОМ по сообщениям — потом дедуп по session_id.
    fetch_limit = max(limit * 30, 200)
    where = ["messages_fts_trigram MATCH ?"]
    params: list = [query]
    if before_ts is not None:
        where.append("m.timestamp < ?")
        params.append(before_ts)
    if after_ts is not None:
        where.append("m.timestamp > ?")
        params.append(after_ts)
    params.append(fetch_limit)

    cur.execute(
        f"""
        SELECT m.session_id, substr(m.content, 1, 200) as snippet, m.timestamp,
               s.title, s.message_count
        FROM messages_fts_trigram f
        JOIN messages m ON m.id = f.rowid
        LEFT JOIN sessions s ON s.id = m.session_id
        WHERE {" AND ".join(where)}
        ORDER BY m.timestamp DESC
        LIMIT ?
        """,
        params,
    )
    # Дедуп: одна сессия = одна строка (самое свежее совпадение).
    seen: set[str] = set()
    results = []
    for sid, snippet, ts, title, msgs in cur.fetchall():
        if sid in seen:
            continue
        seen.add(sid)
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
        if len(results) >= limit:
            break
    conn.close()
    return results


def main():
    parser = argparse.ArgumentParser(description="Поиск по истории сессий (кириллица)")
    parser.add_argument("query", help="Поисковый запрос")
    parser.add_argument("--limit", type=int, default=10, help="Максимум сессий")
    parser.add_argument("--before", help="Только до даты (YYYY-MM-DD|today|yesterday)")
    parser.add_argument("--after", help="Только после даты (YYYY-MM-DD|today|yesterday)")
    args = parser.parse_args()

    results = search(args.query, args.limit, before=args.before, after=args.after)
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
