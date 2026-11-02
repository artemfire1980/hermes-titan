import os

import requests
from dotenv import load_dotenv

load_dotenv("/mnt/ai-ssd/hermes/.env")
TOKEN = os.getenv("MOYSKLAD_TOKEN")
H = {"Authorization": f"Bearer {TOKEN}", "Accept-Encoding": "gzip"}
BASE = "https://api.moysklad.ru/api/remap/1.2"

# Ищем Элигита Азия
r = requests.get(f"{BASE}/entity/counterparty?filter=name~Элигита", headers=H)
data = r.json()
cp = data.get("rows", [])[0]
cp_id = cp["id"]
cp_name = cp["name"]

print(f"Найден: {cp_name} (ID: {cp_id})")

# Получаем заметки
notes_url = f"{BASE}/entity/counterparty/{cp_id}/notes"
r = requests.get(notes_url, headers=H)
notes = r.json().get("rows", [])

deleted = 0
for note in notes:
    text = note.get("description", "")
    if "Не удалось сжать текст" in text:
        note_id = note["id"]
        del_url = f"{BASE}/entity/counterparty/{cp_id}/notes/{note_id}"
        r_del = requests.delete(del_url, headers=H)
        if r_del.status_code == 200:
            deleted += 1
            print(f"🗑️ Удалено: {text[:50]}")
        else:
            print(f"❌ Ошибка: {r_del.status_code}")

print(f"\n✅ Удалено мусорных заметок: {deleted}")
