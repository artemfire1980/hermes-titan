#!/usr/bin/env python3
"""Сбор всех писем из Mail.ru через IMAP (батчами, INBOX + Sent)."""

import email
import imaplib
import json
import sys
from email.header import decode_header
from email.utils import parsedate_to_datetime
from pathlib import Path

SECRETS = Path.home() / ".config" / "rubit-mcp-mail" / "secrets.json"
OUT = Path("/mnt/ai-ssd/hermes/cache/moysklad-audit/emails_all.json")
USER = "artem_s@chocoladovo.by"
HOST = "imap.mail.ru"
# MUTF-7 имена Mail.ru
FOLDERS = ["INBOX", "&BB4EQgQ,BEAEMAQyBDsENQQ9BD0ESwQ1-"]  # INBOX + Sent
BATCH = 200


def load_password():
    data = json.loads(SECRETS.read_text(encoding="utf-8"))
    return data.get("password:mailru") or data.get("mailru")


def decode_hdr(h):
    if not h:
        return ""
    parts = decode_header(h)
    out = []
    for part, enc in parts:
        if isinstance(part, bytes):
            try:
                out.append(part.decode(enc or "utf-8", errors="replace"))
            except Exception:
                out.append(part.decode("utf-8", errors="replace"))
        else:
            out.append(part)
    return " ".join(out)


def fetch_batch(imap, ids):
    items = []
    if not ids:
        return items
    ids_str = ",".join(i.decode() if isinstance(i, bytes) else str(i) for i in ids)
    status, data = imap.fetch(ids_str, "(RFC822.HEADER)")
    if status != "OK":
        return items
    for chunk in data:
        if not isinstance(chunk, tuple) or len(chunk) < 2:
            continue
        msg = email.message_from_bytes(chunk[1])
        try:
            dt = parsedate_to_datetime(msg.get("Date"))
            date_iso = dt.isoformat() if dt else None
        except Exception:
            date_iso = None
        items.append(
            {
                "from": decode_hdr(msg.get("From")),
                "to": decode_hdr(msg.get("To")),
                "subject": decode_hdr(msg.get("Subject")),
                "date": date_iso,
            }
        )
    return items


def main():
    pwd = load_password()
    if not pwd:
        print("password not found", file=sys.stderr)
        return 1
    imap = imaplib.IMAP4_SSL(HOST)
    imap.login(USER, pwd)

    all_items = []
    for folder in FOLDERS:
        try:
            status, _ = imap.select(folder, readonly=True)
            if status != "OK":
                print(f"skip {folder}", file=sys.stderr)
                continue
            status, data = imap.search(None, "ALL")
            ids = data[0].split()
            total = len(ids)
            print(f"{folder}: {total} msgs", file=sys.stderr)
            for start in range(0, total, BATCH):
                batch = ids[start : start + BATCH]
                items = fetch_batch(imap, batch)
                for item in items:
                    item["folder"] = folder
                all_items.extend(items)
                print(f"  {min(start + BATCH, total)}/{total}", file=sys.stderr)
        except Exception as e:
            print(f"{folder}: {e}", file=sys.stderr)
    imap.logout()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(all_items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: {len(all_items)} -> {OUT}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
