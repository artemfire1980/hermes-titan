import email
import imaplib
import json
import os
import time
from email.header import decode_header
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv("/mnt/ai-ssd/hermes/.env")
TOKEN = os.getenv("MOYSKLAD_TOKEN")
H = {"Authorization": f"Bearer {TOKEN}", "Accept-Encoding": "gzip"}
BASE = "https://api.moysklad.ru/api/remap/1.2"
FREELLM_API = "http://127.0.0.1:3001/v1/chat/completions"
FREELLM_KEY = os.getenv("HERMES_CUSTOM_127_0_0_1_3001_API_KEY")


# 1. Загружаем клиентов (Самсонов + глазури, не архивные)
def get_clients():
    all_cp = []
    offset = 0
    while True:
        url = f"{BASE}/entity/counterparty?limit=1000&offset={offset}&filter=archived=false"
        r = requests.get(url, headers=H)
        if r.status_code != 200:
            break
        rows = r.json().get("rows", [])
        all_cp.extend(rows)
        offset += len(rows)
        if len(rows) < 1000:
            break

    result = []
    for cp in all_cp:
        # Тег "глазури"
        tags = [t.lower() for t in cp.get("tags", [])]
        if "глазури" not in tags:
            continue
        # Владелец Самсонов (по ID)
        owner = cp.get("owner", {})
        owner_href = owner.get("meta", {}).get("href", "") if isinstance(owner, dict) else ""
        if "f689640d-f14b-11e3-753d-002590a28eca" not in owner_href:
            continue
        # Получаем контактные лица
        contacts = cp.get("contactpersons", {})
        if isinstance(contacts, dict) and "meta" in contacts:
            href = contacts["meta"]["href"]
            r2 = requests.get(href, headers=H)
            if r2.status_code == 200:
                contacts_rows = r2.json().get("rows", [])
            else:
                contacts_rows = []
        else:
            contacts_rows = []
        # Ищем email
        email_addr = ""
        for c in contacts_rows:
            c_email = c.get("email")
            if c_email and "@" in str(c_email):
                email_addr = c_email.lower().strip()
                break
        if email_addr:
            result.append({"id": cp["id"], "name": cp.get("name"), "email": email_addr})
    return result


# 2. Читаем почту (последние 7 дней)
def get_emails():
    secrets_path = Path.home() / ".config" / "rubit-mcp-mail" / "secrets.json"
    data = json.loads(secrets_path.read_text(encoding="utf-8"))
    password = data.get("password:mailru") or data.get("mailru")

    imap = imaplib.IMAP4_SSL("imap.mail.ru", timeout=120)
    imap.login("artem_s@chocoladovo.by", password)
    imap.select("INBOX")

    # Письма за последние 7 дней
    _, data = imap.search(
        None, "SINCE", time.strftime("%d-%b-%Y", time.localtime(time.time() - 2 * 86400))
    )
    email_ids = data[0].split()

    emails = []
    for eid in email_ids[-50:]:  # Берем последние 50 писем (для теста)
        _, msg_data = imap.fetch(eid, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])

        # От кого
        from_header = msg.get("From", "")
        from_email = ""
        if "<" in from_header:
            from_email = from_header.split("<")[1].split(">")[0].lower()
        else:
            from_email = from_header.lower()

        # Тема
        subject = msg.get("Subject", "")
        subject = str(decode_header(subject)[0][0]) if decode_header(subject) else subject

        # Текст
        body = ""

        def decode_part(part):
            payload = part.get_payload(decode=True)
            if not payload:
                return ""
            charset = part.get_content_charset() or "utf-8"
            try:
                return payload.decode(charset, errors="ignore")
            except:
                return payload.decode("utf-8", errors="ignore")

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = decode_part(part)
                    if body:
                        break
        else:
            body = decode_part(msg)

        emails.append(
            {
                "from": from_email,
                "subject": subject,
                "body": body[:1000],  # Первые 1000 символов
                "date": msg.get("Date", ""),
            }
        )
    imap.logout()
    return emails


# 3. Сжимаем текст через FreeLLMAPI
def summarize(text):
    # Очищаем текст от цитат и подписей
    # Обрезаем по цитатам
    for marker in [
        "-----Original Message-----",
        "From:",
        "От:",
        "________________________________",
    ]:
        if marker in text:
            text = text.split(marker)[0]
    # Обрезаем по подписям
    for marker in ["Best regards", "С уважением", "С уважением,"]:
        if marker in text:
            text = text.split(marker)[0]
    text = text.strip()
    if not text:
        return "Текст письма пуст."

    payload = {
        "model": "qwen3-coder-plus",
        "messages": [
            {
                "role": "system",
                "content": "Сожми суть письма до 1-2 предложений. Только конкретика: что запросили, что ответили, что нужно сделать. Без воды.",
            },
            {"role": "user", "content": text},
        ],
        "temperature": 0.2,
        "max_tokens": 150,
    }
    import time

    for attempt in range(3):
        try:
            r = requests.post(
                FREELLM_API,
                headers={"Authorization": f"Bearer {FREELLM_KEY}"},
                json=payload,
                timeout=60,
            )
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"].strip()
            elif r.status_code in (429, 502, 503):
                print(f"⚠️ Попытка {attempt + 1}: ошибка {r.status_code}, ждем 5 сек...")
                time.sleep(5)
                continue
            else:
                print(f"❌ Ошибка FreeLLMAPI: {r.status_code} - {r.text[:200]}")
                return "Не удалось сжать текст."
        except Exception as e:
            print(f"⚠️ Попытка {attempt + 1}: исключение {e}, ждем 5 сек...")
            time.sleep(5)
            continue
    return "Не удалось сжать текст (после 3 попыток)."


# 4. Создаем событие в МойСклад
def create_event(cp_id, text):
    url = f"{BASE}/entity/counterparty/{cp_id}/notes"
    payload = {"description": text}
    r = requests.post(url, headers=H, json=payload)
    return r.status_code in (200, 201)


# 5. Основной процесс
def main():
    print("Загружаем клиентов...")
    clients = get_clients()
    print(f"Найдено клиентов: {len(clients)}")

    print("Загружаем почту...")
    emails = get_emails()
    print(f"Найдено писем: {len(emails)}")

    # Сопоставляем
    created = 0
    for msg in emails:
        from_email = msg["from"]
        for client in clients:
            if client["email"] == from_email:
                print(f"Совпадение: {client['name']} ({from_email})")
                import time

                time.sleep(7)  # Пауза между запросами (7 секунд, чтобы не превысить лимит)
                summary = summarize(msg["body"])
                if create_event(client["id"], f"Ответ: {summary}"):
                    created += 1
                    print(f"  ✅ Событие создано: {summary[:50]}...")
                else:
                    print("  ❌ Ошибка при создании события")
                break

    print(f"\n✅ Создано событий: {created}")


if __name__ == "__main__":
    main()
