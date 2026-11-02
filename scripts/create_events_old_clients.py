import csv
import os

import requests
from dotenv import load_dotenv

load_dotenv("/mnt/ai-ssd/hermes/.env")
TOKEN = os.getenv("MOYSKLAD_TOKEN")
H = {"Authorization": f"Bearer {TOKEN}", "Accept-Encoding": "gzip"}
BASE = "https://api.moysklad.ru/api/remap/1.2"

# 1. Читаем список ИНН, которым мы только что загрузили email (исключаем их)
new_inns = set()
with open("/mnt/ai-ssd/hermes/cache/samsonov_emails_found_v2.csv", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f, delimiter=";")
    for row in reader:
        email = row.get("Email", "").strip()
        inn = row.get("ИНН", "").strip()
        if email and "@" in email:
            new_inns.add(inn)

print(f"Исключаем {len(new_inns)} новых клиентов (им email уже проставлен)")

# 2. Получаем ID статуса "в разработке"
r = requests.get(f"{BASE}/entity/counterparty/metadata/states", headers=H)
state_id = None
for s in r.json().get("rows", []):
    if "разработке" in s["name"].lower():
        state_id = s["id"]
        break

# 3. Загружаем всех контрагентов Самсонова с тегом "глазури" и статусом "в разработке"
all_cp = []
offset = 0
while True:
    url = f"{BASE}/entity/counterparty?limit=1000&offset={offset}&expand=owner,contactpersons"
    r = requests.get(url, headers=H)
    if r.status_code != 200:
        break
    rows = r.json().get("rows", [])
    all_cp.extend(rows)
    offset += len(rows)
    if len(rows) < 1000:
        break

print(f"Всего загружено контрагентов: {len(all_cp)}")

# 4. Фильтруем "старых" клиентов
old_clients = []
for cp in all_cp:
    # Тег "глазури"
    tags = [t.lower() for t in cp.get("tags", [])]
    if "глазури" not in tags:
        continue

    # Менеджер Самсонов
    owner = cp.get("owner", {})
    owner_href = owner.get("meta", {}).get("href", "") if isinstance(owner, dict) else ""
    # ID Самсонова: f689640d-f14b-11e3-753d-002590a28eca
    if "f689640d-f14b-11e3-753d-002590a28eca" not in owner_href:
        continue

    # Статус "в разработке"
    state = cp.get("state", {})
    state_href = state.get("meta", {}).get("href", "") if isinstance(state, dict) else ""
    # ID статуса "в разработке": 21798e98-bca2-11e3-47b6-002590a28eca
    if "21798e98-bca2-11e3-47b6-002590a28eca" not in state_href:
        continue

    # Исключаем новых (которым только что загрузили email)
    inn = cp.get("inn", "")
    if inn in new_inns:
        continue

    # Проверяем, есть ли email (в поле email или в контактных лицах)
    email = cp.get("email")
    contacts = cp.get("contactpersons", [])
    if isinstance(contacts, dict):
        contacts = contacts.get("rows", [])

    has_email = False
    if email and "@" in str(email):
        has_email = True
    else:
        for c in contacts:
            c_email = c.get("email")
            if c_email and "@" in str(c_email):
                has_email = True
                break

    if has_email:
        old_clients.append(cp)

print(f"Найдено 'старых' клиентов с email (кому уже отправляли): {len(old_clients)}")

# 5. Создаем события
created = 0
errors = 0

for cp in old_clients:
    event_url = f"{BASE}/entity/counterparty/{cp['id']}/notes"
    payload = {
        "description": "Отправлено коммерческое предложение (предыдущая рассылка)",
        "eventType": "note",
    }
    r = requests.post(event_url, headers=H, json=payload)
    if r.status_code in (200, 201):
        created += 1
    else:
        print(f"❌ Ошибка для {cp.get('name')}: {r.status_code} - {r.text[:200]}")
        errors += 1

print(f"✅ Создано событий: {created}")
print(f"❌ Ошибок: {errors}")
