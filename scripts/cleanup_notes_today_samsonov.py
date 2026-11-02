import os
import time

import requests
from dotenv import load_dotenv

load_dotenv("/mnt/ai-ssd/hermes/.env")
TOKEN = os.getenv("MOYSKLAD_TOKEN")
H = {"Authorization": f"Bearer {TOKEN}", "Accept-Encoding": "gzip"}
BASE = "https://api.moysklad.ru/api/remap/1.2"

OWNER_ID = "f689640d-f14b-11e3-753d-002590a28eca"  # Самсонов
today = "2026-10-30"  # Фиксируем дату

print(f"Ищем заметки за: {today} (только Самсонов)")


def safe_get(url, headers, retries=3):
    for i in range(retries):
        try:
            r = requests.get(url, headers=headers, timeout=30)
            return r
        except Exception as e:
            if i == retries - 1:
                print(f"❌ Ошибка GET: {e}")
                return None
            time.sleep(2)


def safe_delete(url, headers, retries=3):
    for i in range(retries):
        try:
            r = requests.delete(url, headers=headers, timeout=30)
            return r
        except Exception as e:
            if i == retries - 1:
                print(f"❌ Ошибка DELETE: {e}")
                return None
            time.sleep(2)


# 1. Загружаем всех контрагентов
all_cp = []
offset = 0
while True:
    url = f"{BASE}/entity/counterparty?limit=1000&offset={offset}"
    r = safe_get(url, H)
    if not r or r.status_code != 200:
        break
    rows = r.json().get("rows", [])
    all_cp.extend(rows)
    offset += len(rows)
    if len(rows) < 1000:
        break

print(f"Всего контрагентов: {len(all_cp)}")

deleted = 0
kept = 0

for cp in all_cp:
    owner = cp.get("owner", {})
    owner_href = owner.get("meta", {}).get("href", "") if isinstance(owner, dict) else ""
    if OWNER_ID not in owner_href:
        continue

    notes_url = f"{BASE}/entity/counterparty/{cp['id']}/notes"
    r = safe_get(notes_url, H)
    if not r or r.status_code != 200:
        continue

    notes = r.json().get("rows", [])
    for note in notes:
        text = note.get("description", "")
        note_id = note.get("id")
        created = note.get("created", "")

        if created.startswith(today):
            if not text.startswith("Отправлено коммерческое предложение"):
                del_url = f"{BASE}/entity/counterparty/{cp['id']}/notes/{note_id}"
                r_del = safe_delete(del_url, H)
                if r_del and r_del.status_code == 200:
                    deleted += 1
                    print(f"🗑️ Удалено: {cp.get('name')} — {text[:50]}...")
                else:
                    print(
                        f"❌ Ошибка удаления: {cp.get('name')} — {r_del.status_code if r_del else 'нет ответа'}"
                    )
            else:
                kept += 1

print(f"\n✅ Удалено сегодняшних заметок (Самсонов): {deleted}")
print(f"✅ Оставлено: {kept}")
