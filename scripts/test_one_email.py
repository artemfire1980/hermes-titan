import email
import imaplib
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv("/mnt/ai-ssd/hermes/.env")
FREELLM_API = "http://127.0.0.1:3001/v1/chat/completions"
FREELLM_KEY = os.getenv("HERMES_CUSTOM_127_0_0_1_3001_API_KEY")

# 1. Подключаемся к почте
secrets_path = Path.home() / ".config" / "rubit-mcp-mail" / "secrets.json"
data = json.loads(secrets_path.read_text(encoding="utf-8"))
password = data.get("password:mailru") or data.get("mailru")

imap = imaplib.IMAP4_SSL("imap.mail.ru")
imap.login("artem_s@chocoladovo.by", password)
imap.select("INBOX")

# 2. Ищем письмо от Элигита Азия
_, data = imap.search(None, 'FROM "svetlana.muschak@gmail.com"')
email_ids = data[0].split()
if not email_ids:
    print("Письма не найдены.")
    sys.exit()

latest_id = email_ids[-1]
_, msg_data = imap.fetch(latest_id, "(RFC822)")
msg = email.message_from_bytes(msg_data[0][1])

# 3. Извлекаем текст (с правильной кодировкой)
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

# 4. Очищаем текст от цитат и подписей
for marker in ["-----Original Message-----", "From:", "От:", "________________________________"]:
    if marker in body:
        body = body.split(marker)[0]
for marker in ["Best regards", "С уважением", "С уважением,"]:
    if marker in body:
        body = body.split(marker)[0]
body = body.strip()

print("=== Очищенный текст письма (первые 500 символов) ===")
print(body[:500])
print("\n" + "=" * 50 + "\n")

# 5. Отправляем в FreeLLMAPI
payload = {
    "model": "auto",
    "messages": [
        {
            "role": "system",
            "content": "Ты — CRM-ассистент. Твоя задача — сжать суть письма до 1-2 предложений. ОТВЕЧАЙ ТОЛЬКО НА РУССКОМ ЯЗЫКЕ. ЗАПРЕЩЕНО: писать по-английски, писать Let me analyze, The user wants, We need to summarize, I should, писать списки, цифры, маркеры. ТОЛЬКО СУТЬ: что запросил клиент или что ответил менеджер. Пример правильного ответа: Клиент запросил спецификации на какао-порошок и сиропы, менеджер уточнил объемы. Пример неправильного: We need analyze the request. Сейчас напиши ТОЛЬКО ответ, начиная с сути, без рассуждений.",
        },
        {"role": "user", "content": body[:3000]},
    ],
    "temperature": 0.2,
    "max_tokens": 150,
}

r = requests.post(FREELLM_API, headers={"Authorization": f"Bearer {FREELLM_KEY}"}, json=payload)
if r.status_code == 200:
    result = r.json()["choices"][0]["message"]["content"].strip()
    print("=== Сжатый результат ===")
    print(result)
else:
    print(f"❌ Ошибка FreeLLMAPI: {r.status_code} - {r.text[:200]}")

imap.logout()
