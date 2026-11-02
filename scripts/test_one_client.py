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

CLIENT_ID = "e385d294-10b5-11f1-0a80-04d1002eb724"
CLIENT_EMAIL = "svetlana.muschak@gmail.com"


def get_emails():
    secrets_path = Path.home() / ".config" / "rubit-mcp-mail" / "secrets.json"
    data = json.loads(secrets_path.read_text(encoding="utf-8"))
    password = data.get("password:mailru") or data.get("mailru")

    imap = imaplib.IMAP4_SSL("imap.mail.ru", timeout=120)
    imap.login("artem_s@chocoladovo.by", password)
    imap.select("INBOX")

    # Ищем письма за 7 дней
    date = time.strftime("%d-%b-%Y", time.localtime(time.time() - 7 * 86400))
    _, data = imap.search(None, f"(SINCE {date})")
    email_ids = data[0].split()
    print(f"Всего писем за 7 дней: {len(email_ids)}")

    # Фильтруем по отправителю
    matched = []
    for eid in email_ids[-100:]:  # Проверяем последние 100
        _, msg_data = imap.fetch(eid, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])

        from_header = msg.get("From", "")
        from_email = ""
        if "<" in from_header:
            from_email = from_header.split("<")[1].split(">")[0].lower()
        else:
            from_email = from_header.lower()

        if CLIENT_EMAIL in from_email:
            # Извлекаем текст
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            charset = part.get_content_charset() or "utf-8"
                            body = payload.decode(charset, errors="ignore")
                            break
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    charset = msg.get_content_charset() or "utf-8"
                    body = payload.decode(charset, errors="ignore")

            matched.append(
                {
                    "subject": str(decode_header(msg.get("Subject", ""))[0][0]),
                    "body": body[:1000],  # Берем первые 1000 символов
                    "date": msg.get("Date", ""),
                }
            )

    imap.logout()
    return matched


def compress_text(text):
    payload = {
        "model": "qwen3-coder-plus",
        "messages": [
            {"role": "user", "content": f"Сожми суть этого письма в 2-3 предложениях:\n\n{text}"}
        ],
        "max_tokens": 200,
    }
    headers = {"Authorization": f"Bearer {FREELLM_KEY}", "Content-Type": "application/json"}
    try:
        r = requests.post(FREELLM_API, headers=headers, json=payload, timeout=60)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        else:
            return f"Ошибка: {r.status_code}"
    except Exception as e:
        return f"Ошибка: {e}"


def create_event(client_id, description):
    payload = {"description": description}
    url = f"{BASE}/entity/counterparty/{client_id}/notes"
    r = requests.post(url, headers=H, json=payload)
    return r.status_code == 200


if __name__ == "__main__":
    print(f"Ищем письма от {CLIENT_EMAIL}...")
    emails = get_emails()
    print(f"Найдено писем от {CLIENT_EMAIL}: {len(emails)}")

    for i, em in enumerate(emails):
        print(f"\n--- Письмо {i + 1} ---")
        print(f"Тема: {em['subject']}")
        print(f"Дата: {em['date']}")

        print("Сжимаем текст...")
        summary = compress_text(em["body"])
        print(f"Суть: {summary[:200]}...")

        if create_event(CLIENT_ID, f"Письмо от {em['date']}: {summary}"):
            print("✅ Событие создано")
        else:
            print("❌ Ошибка создания события")
