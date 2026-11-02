import csv
import os

import requests
from dotenv import load_dotenv

load_dotenv("/mnt/ai-ssd/hermes/.env")
TOKEN = os.getenv("MOYSKLAD_TOKEN")
H = {"Authorization": f"Bearer {TOKEN}", "Accept-Encoding": "gzip"}
BASE = "https://api.moysklad.ru/api/remap/1.2"

# 1. Читаем CSV
data = []
with open("/mnt/ai-ssd/hermes/cache/samsonov_emails_found_v2.csv", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f, delimiter=";")
    for row in reader:
        email = row.get("Email", "").strip()
        inn = row.get("ИНН", "").strip()
        if email and "@" in email:
            data.append({"email": email, "inn": inn})

print(f"К загрузке: {len(data)} email")

# 2. Загружаем всех контрагентов (с пагинацией)
all_cp = []
offset = 0
while True:
    r = requests.get(
        f"{BASE}/entity/counterparty?limit=1000&offset={offset}&expand=contactpersons", headers=H
    )
    if r.status_code != 200:
        print(f"Ошибка API: {r.status_code}")
        break
    rows = r.json().get("rows", [])
    all_cp.extend(rows)
    offset += len(rows)
    if len(rows) < 1000:
        break

print(f"Загружено контрагентов: {len(all_cp)}")

# 3. Обновляем контактные лица
updated = 0
created = 0
errors = 0

for item in data:
    email = item["email"]
    inn = item["inn"]

    cp = None
    for c in all_cp:
        if inn and c.get("inn") == inn:
            cp = c
            break

    if not cp:
        continue

    contacts = cp.get("contactpersons", [])
    if isinstance(contacts, dict):
        contacts = contacts.get("rows", [])

    if contacts:
        contact = contacts[0]
        contact_id = contact.get("id")
        contact_url = f"{BASE}/entity/counterparty/{cp['id']}/contactpersons/{contact_id}"
        payload = {"email": email}
        r = requests.put(contact_url, headers=H, json=payload)
        if r.status_code == 200:
            updated += 1
        else:
            errors += 1
    else:
        payload = {"name": "Контактное лицо", "email": email}
        r = requests.post(
            f"{BASE}/entity/counterparty/{cp['id']}/contactpersons", headers=H, json=payload
        )
        if r.status_code == 200:
            created += 1
        else:
            errors += 1

print(f"✅ Обновлено контактных лиц: {updated}")
print(f"✅ Создано новых контактных лиц: {created}")
print(f"❌ Ошибок: {errors}")
