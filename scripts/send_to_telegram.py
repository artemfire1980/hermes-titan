#!/usr/bin/env python3
"""Отправляет файл в Telegram (с caption и preview)"""

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from env_utils import load_env

load_env([Path.home() / "ai-system" / ".env", Path.home() / ".hermes" / ".env"])

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

if not BOT_TOKEN or not CHAT_ID:
    print("❌ TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID не установлены в .env", file=sys.stderr)
    sys.exit(1)


def send_document(file_path: Path, caption: str = ""):
    """Отправляет документ в Telegram"""
    import json
    import mimetypes
    import urllib.parse
    import urllib.request

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"

    # Multipart form data
    boundary = "----PythonTelegramBoundary"
    body = []

    # chat_id field
    body.append(f"--{boundary}".encode())
    body.append(b'Content-Disposition: form-data; name="chat_id"')
    body.append(b"")
    body.append(CHAT_ID.encode())

    # caption field (если есть)
    if caption:
        body.append(f"--{boundary}".encode())
        body.append(b'Content-Disposition: form-data; name="caption"')
        body.append(b"")
        body.append(caption.encode("utf-8"))

    # document file
    body.append(f"--{boundary}".encode())
    filename = file_path.name
    mime = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
    body.append(f'Content-Disposition: form-data; name="document"; filename="{filename}"'.encode())
    body.append(f"Content-Type: {mime}".encode())
    body.append(b"")
    body.append(file_path.read_bytes())
    body.append(f"--{boundary}--".encode())

    data = b"\r\n".join(body)

    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode())
            if result.get("ok"):
                print(f"✅ Файл отправлен в Telegram: {filename}")
                return True
            else:
                print(f"❌ Telegram error: {result}", file=sys.stderr)
                return False
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}", file=sys.stderr)
        return False


def send_message(text: str):
    """Отправляет текстовое сообщение"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = urllib.parse.urlencode(
        {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    ).encode()

    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            return result.get("ok", False)
    except Exception as e:
        print(f"❌ Ошибка отправки сообщения: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("file", help="Путь к файлу для отправки")
    ap.add_argument("--caption", "-c", default="", help="Подпись к файлу")
    ap.add_argument("--message", "-m", help="Дополнительное текстовое сообщение")
    args = ap.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"❌ Файл не найден: {file_path}")
        sys.exit(1)

    if args.message:
        send_message(args.message)

    if send_document(file_path, args.caption):
        sys.exit(0)
    else:
        sys.exit(1)
