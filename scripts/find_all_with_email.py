import csv
import os

import requests
from dotenv import load_dotenv

load_dotenv("/mnt/ai-ssd/hermes/.env")
TOKEN = os.getenv("MOYSKLAD_TOKEN")
H = {"Authorization": f"Bearer {TOKEN}", "Accept-Encoding": "gzip"}
BASE = "https://api.moysklad.ru/api/remap/1.2"

# 1. ID статуса и владельца
STATE_ID = "21798e98-bca2-11e3-47b6-002590a28eca"
OWNER_ID = "f689640d-f14b-11e3-753d-002590a28eca"

# 2. Загружаем всех контрагентов
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

print(f"Всего загружено: {len(all_cp)}")

# 3. Фильтруем
result = []
count = 0
for cp in all_cp:
    # Тег "глазури"
    tags = [t.lower() for t in cp.get("tags", [])]
    if "глазури" not in tags:
        continue

    # Владелец Самсонов (по ID)
    owner = cp.get("owner", {})
    owner_href = owner.get("meta", {}).get("href", "") if isinstance(owner, dict) else ""
    if OWNER_ID not in owner_href:
        continue

    # Статус "в разработке" (по ID)
    state = cp.get("state", {})
    state_href = state.get("meta", {}).get("href", "") if isinstance(state, dict) else ""
    if STATE_ID not in state_href:
        continue

    # Получаем контактные лица (отдельным запросом)
    contacts = cp.get("contactpersons", {})
    if isinstance(contacts, dict) and "meta" in contacts:
        href = contacts["meta"]["href"]
        r = requests.get(href, headers=H)
        if r.status_code == 200:
            contacts_rows = r.json().get("rows", [])
        else:
            contacts_rows = []
    elif isinstance(contacts, list):
        contacts_rows = contacts
    else:
        contacts_rows = []

    # Ищем email в контактных лицах
    email_found = ""
    for c in contacts_rows:
        c_email = c.get("email")
        if c_email and "@" in str(c_email):
            email_found = c_email
            break

    if email_found:
        result.append({"name": cp.get("name"), "inn": cp.get("inn", ""), "email": email_found})
        count += 1
        if count % 10 == 0:
            print(f"  Найдено: {count}...")

# 4. Вывод
print(f"\n=== Найдено клиентов: {len(result)} ===")
print(f"{'Название':<40} | {'ИНН':<12} | {'Email'}")
print("-" * 80)
for r in result:
    print(f"{r['name']:<40} | {r['inn']:<12} | {r['email']}")

# 5. Сохраняем в CSV
csv_path = "/mnt/ai-ssd/hermes/cache/samsonov_glazur_in_development_with_email.csv"
with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f, delimiter=";", quoting=csv.QUOTE_ALL)
    writer.writerow(["Название", "ИНН", "Email"])
    for r in result:
        writer.writerow([r["name"], r["inn"], r["email"]])

print(f"\n✅ Сохранено в {csv_path}")
