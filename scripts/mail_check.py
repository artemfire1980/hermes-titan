#!/usr/bin/env python3
"""Ежедневная проверка новых писем в Mail.ru через IMAP.

Запуск: cron (9:00). Уведомление в Telegram через `hermes send`.
Логи: /mnt/ai-ssd/hermes/logs/mail_check.log
"""

import imaplib
import json
import sys
import time
from pathlib import Path

LOG_FILE = Path("/mnt/ai-ssd/hermes/logs/mail_check.log")
CONFIG = Path.home() / ".config" / "rubit-mcp-mail" / "config.toml"
SECRETS = Path.home() / ".config" / "rubit-mcp-mail" / "secrets.json"


def log(msg):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")


def load_password():
    if not SECRETS.exists():
        raise RuntimeError(f"{SECRETS} не найден")
    data = json.loads(SECRETS.read_text(encoding="utf-8"))
    # Формат: {"password:mailru": "..."}
    return data.get("password:mailru") or data.get("mailru")


def main():
    log("=== start mail check ===")
    try:
        user = "artem_s@chocoladovo.by"
        host = "imap.mail.ru"
        password = load_password()
        if not password:
            log("ERROR: password not found in secrets.json")
            return 1

        imap = imaplib.IMAP4_SSL(host)
        imap.login(user, password)
        imap.select("INBOX")
        _, data = imap.search(None, "UNSEEN")
        unread = len(data[0].split()) if data[0] else 0
        imap.logout()

        log(f"Unread: {unread}")
        if unread > 0:
            print(f"📬 Почта: {unread} непрочитанных в INBOX")
        return 0
    except Exception as e:
        log(f"ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
