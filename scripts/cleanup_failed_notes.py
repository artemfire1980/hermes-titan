import os

import requests
from dotenv import load_dotenv

load_dotenv("/mnt/ai-ssd/hermes/.env")
TOKEN = os.getenv("MOYSKLAD_TOKEN")
H = {"Authorization": f"Bearer {TOKEN}", "Accept-Encoding": "gzip"}
BASE = "https://api.moysklad.ru/api/remap/1.2"

OWNER_ID = "f689640d-f14b-11e3-753d-002590a28eca"  # Самсонов

# 1. Загружаем всех контрагентов
all_cp = []
offset = 0
while True:
    url = f"{BASE}/entity/counterparty?limit=1000&offset={offset}"
    r = requests.get(url, headers=H)
    if r.status_code != 200:
        break
    rows = r.json().get("rows", [])
    all_cp.extend(rows)
    offset += len(rows)
    if len(rows) < 1000:
        break

print(f"Всего контрагентов: {len(all_cp)}")

deleted = 0

for cp in all_cp:
    # Только Самсонов
    owner = cp.get("owner", {})
    owner_href = owner.get("meta", {}).get("href", "") if isinstance(owner, dict) else ""
    if OWNER_ID not in owner_href:
        continue

    notes_url = f"{BASE}/entity/counterparty/{cp['id']}/notes"
    r = requests.get(notes_url, headers=H)
    if r.status_code != 200:
        continue

    for note in r.json().get("rows", []):
        text = note.get("description", "")
        note_id = note.get("id")

        # Удаляем только мусорные заметки
        if "Не удалось сжать текст" in text:
            del_url = f"{BASE}/entity/counterparty/{cp['id']}/notes/{note_id}"
            r_del = requests.delete(del_url, headers=H)
            if r_del.status_code == 200:
                deleted += 1
                print(f"🗑️ Удалено: {cp.get('name')} — {text}")
            else:
                print(f"❌ Ошибка: {cp.get('name')} — {r_del.status_code}")

print(f"\n✅ Удалено мусорных заметок: {deleted}")
