import os

import requests
from dotenv import load_dotenv

load_dotenv("/mnt/ai-ssd/hermes/.env")
TOKEN = os.getenv("MOYSKLAD_TOKEN")
H = {"Authorization": f"Bearer {TOKEN}", "Accept-Encoding": "gzip"}
BASE = "https://api.moysklad.ru/api/remap/1.2"

# Список email, которым уже отправляли предложение
target_emails = [
    "nalslad@mail.ru",
    "zelenovaog@dalimo.ru",
    "belonogova_ai@constell-group.ru",
    "edronova@mail.ru",
    "konditer-ama@mail.ru",
    "zakup@osko-cf.ru",
    "zakup@cplan.ru",
    "kurapov.yv@rusprod.ru",
    "sokolova-sg@cf64.ru",
    "sweetmarieli@mail.ru",
    "snab@kfsibir.ru",
    "slavia-msn@mail.ru",
    "slavia_pk@mail.ru",
    "ershovayu@damol.pro",
    "ksenia@besnacksy.com",
    "sparta109@mail.ru",
    "korostylev@sup.spkf.ru",
    "hurshed001@mail.ru",
    "snab@uralcond.ru",
    "kxsales@yandex.ru",
    "nikolai_kaplunov@mail.ru",
    "redaktor15@gmail.com",
    "chekanova@shokolat-e.ru",
    "svetlana.muschak@gmail.com",
    "sn@uniant.ru",
    "vnekrasov@ukmp.ru",
    "snab2@altey-kf.ru",
    "halva2002@inbox.ru",
    "onts02@suharik.kirov.ru",
    "welldollc@gmail.com",
    "ak@v-shok.ru",
    "zakup@vanslad.ru",
    "manager3@triumf-kf.ru",
    "muralev@davaice.ru",
    "ishenkoae@dalimo.ru",
    "info@goodcookies.ru",
    "r_agiyarov@mail.ru",
    "mvi@fedmol.com",
    "s.sherbakov@izobiliegroup.ru",
    "promagrok@mail.ru",
    "o.koktysh@kmki.ru",
    "v.chirkova@gk-kim.ru",
    "shtepinaoa@ugrus.com",
    "r_kalyanov@lkray.ru",
    "info@micaello.ru",
    "snab@micaello.ru",
]

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

# 2. Ищем совпадения по email в контактных лицах
created = 0
found_cp = 0

for cp in all_cp:
    # Получаем контактные лица
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

    # Проверяем email
    match = False
    for c in contacts_rows:
        c_email = c.get("email")
        if c_email and c_email.strip() in target_emails:
            match = True
            break

    if match:
        found_cp += 1
        # Создаем событие
        event_url = f"{BASE}/entity/counterparty/{cp['id']}/notes"
        payload = {"description": "Отправлено коммерческое предложение (по email)"}
        r = requests.post(event_url, headers=H, json=payload)
        if r.status_code in (200, 201):
            created += 1
            print(f"✅ {cp.get('name')} — событие создано")
        else:
            print(f"❌ {cp.get('name')} — ошибка {r.status_code}")

print(f"\nНайдено контрагентов с email из списка: {found_cp}")
print(f"✅ Создано событий: {created}")
