#!/usr/bin/env python3
"""Еженедельное обновление email_base.json из МойСклад.

Запуск: cron (Пн 6:00). Логи: /mnt/ai-ssd/hermes/logs/moysklad_refresh.log
"""

import gzip
import json
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

OUT_DIR = Path("/mnt/ai-ssd/hermes/cache/moysklad-audit")
OUT_FILE = OUT_DIR / "email_base.json"
LOG_FILE = Path("/mnt/ai-ssd/hermes/logs/moysklad_refresh.log")
BASE = "https://api.moysklad.ru/api/remap/1.2"
BATCH = 100


def log(msg):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")


def load_token():
    env = Path("/mnt/ai-ssd/hermes/.env")
    for line in env.read_text().splitlines():
        if line.startswith("MOYSKLAD_TOKEN="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("MOYSKLAD_TOKEN не найден")


def fetch(token, path, params=None):
    url = BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json;charset=utf-8",
            "Accept-Encoding": "gzip",
        },
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    raw = gzip.decompress(raw)
                return json.loads(raw)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(10)
                continue
            raise


def main():
    log("=== start refresh ===")
    try:
        token = load_token()
        offset = 0
        total = None
        items = []
        while True:
            data = fetch(
                token,
                "/entity/counterparty",
                {
                    "limit": BATCH,
                    "offset": offset,
                    "expand": "contactpersons,owner",
                },
            )
            rows = data.get("rows", [])
            if total is None:
                total = data["meta"]["size"]
            for r in rows:
                emails = set()
                if r.get("email"):
                    emails.add(r["email"])
                for cp in r.get("contactpersons", {}).get("rows") or []:
                    if cp.get("email"):
                        emails.add(cp["email"])
                if emails:
                    items.append(
                        {
                            "id": r["id"],
                            "name": r.get("name"),
                            "companyType": r.get("companyType"),
                            "tags": r.get("tags", []),
                            "owner": (r.get("owner") or {}).get("name"),
                            "emails": sorted(emails),
                        }
                    )
            offset += BATCH
            log(f"  {min(offset, total)}/{total}, с email: {len(items)}")
            if offset >= total:
                break
            time.sleep(0.3)

        OUT_DIR.mkdir(parents=True, exist_ok=True)
        OUT_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
        log(f"OK: {len(items)} контрагентов с email -> {OUT_FILE}")
        msg = f"📊 МойСклад: email_base.json обновлён — {len(items)} контрагентов с email (из {total})"
        print(msg)
        subprocess.run(["hermes", "send", "-t", "telegram:170690883", msg], timeout=30, check=False)
        return 0
    except Exception as e:
        log(f"ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
