import os

import requests
from dotenv import load_dotenv

load_dotenv("/mnt/ai-ssd/hermes/.env")
TOKEN = os.getenv("MOYSKLAD_TOKEN")
H = {"Authorization": f"Bearer {TOKEN}", "Accept-Encoding": "gzip"}
BASE = "https://api.moysklad.ru/api/remap/1.2"

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

# 2. Проверяем заметки у каждого
deleted = 0
kept = 0

for cp in all_cp:
    notes_url = f"{BASE}/entity/counterparty/{cp['id']}/notes"
    r = requests.get(notes_url, headers=H)
    if r.status_code != 200:
        continue

    notes = r.json().get("rows", [])
    for note in notes:
        text = note.get("description", "")
        note_id = note.get("id")

        # Если текст НЕ начинается с "Отправлено коммерческое предложение (по email)"
        if not text.startswith("Отправлено коммерческое предложение (по email)"):
            del_url = f"{BASE}/entity/counterparty/{cp['id']}/notes/{note_id}"
            r_del = requests.delete(del_url, headers=H)
            if r_del.status_code == 200:
                deleted += 1
                print(f"🗑️ Удалено: {cp.get('name')} — {text[:50]}...")
            else:
                print(f"❌ Ошибка удаления: {cp.get('name')} — {r_del.status_code}")
        else:
            kept += 1

print(f"\n✅ Удалено заметок: {deleted}")
print(f"✅ Оставлено заметок: {kept}")
