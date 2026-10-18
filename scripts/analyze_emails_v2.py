#!/usr/bin/env python3
"""Анализ: кому из МойСклад давно не писал. Матчинг по домену + email + имени."""

import json
import re
from datetime import datetime
from pathlib import Path

AUDIT = Path("/mnt/ai-ssd/hermes/cache/moysklad-audit")
EMAILS = AUDIT / "emails_all.json"
EMAIL_BASE = AUDIT / "email_base.json"
COUNTERPARTY = AUDIT / "counterparty_full.json"
OUT = AUDIT / "analysis_overdue_v2.json"

now = datetime.now()

# 1. Загрузить контрагентов (email_base + counterparty_full для owner)
email_base = json.loads(EMAIL_BASE.read_text(encoding="utf-8"))
cp_owner = {}
if COUNTERPARTY.exists():
    cps = json.loads(COUNTERPARTY.read_text(encoding="utf-8"))
    for cp in cps:
        owner = (cp.get("owner") or {}).get("name")
        cp_owner[cp.get("id")] = owner
        cp_owner[cp.get("name")] = owner

# 2. Построить индекс:
#    - email -> cp
#    - domain -> set(cp)
email_to_cp = {}
domain_to_cps = {}
for cp in email_base:
    for e in cp.get("emails", []):
        el = e.lower().strip()
        if not el or "@" not in el:
            continue
        email_to_cp[el] = cp
        domain = el.split("@", 1)[1]
        domain_to_cps.setdefault(domain, set()).add(cp.get("id"))
        # owner
        if cp.get("owner") is None:
            cp["owner"] = cp_owner.get(cp.get("id")) or cp_owner.get(cp.get("name"))

# 3. Пройти по письмам: обновить last_seen для email, для домена
emails = json.loads(EMAILS.read_text(encoding="utf-8"))
last_seen_email = {}
last_seen_domain = {}

for e in emails:
    dt_str = e.get("date")
    if not dt_str:
        continue
    try:
        dt = datetime.fromisoformat(dt_str)
    except Exception:
        continue
    if dt.tzinfo is not None:
        dt = dt.astimezone().replace(tzinfo=None)

    for field in ("from", "to"):
        val = e.get(field, "")
        m = re.search(r"<([^>]+)>", val)
        addr = (m.group(1) if m else val).strip().lower()
        if not addr or "@" not in addr:
            continue
        # по email
        if addr not in last_seen_email or dt > last_seen_email[addr]:
            last_seen_email[addr] = dt
        # по домену
        domain = addr.split("@", 1)[1]
        if domain not in last_seen_domain or dt > last_seen_domain[domain]:
            last_seen_domain[domain] = dt

# 4. Анализ: по каждому cp — последнее письмо
#    - сначала по email
#    - потом по домену (если email не найден)
result = []
for cp in email_base:
    cp_emails = [e.lower() for e in cp.get("emails", [])]
    last = None
    match_type = None
    # по email
    for el in cp_emails:
        dt = last_seen_email.get(el)
        if dt and (last is None or dt > last):
            last = dt
            match_type = "email"
    # по домену
    if last is None:
        for el in cp_emails:
            if "@" not in el:
                continue
            domain = el.split("@", 1)[1]
            dt = last_seen_domain.get(domain)
            if dt and (last is None or dt > last):
                last = dt
                match_type = "domain"

    if last is None:
        result.append(
            {
                "name": cp.get("name"),
                "owner": cp.get("owner"),
                "tags": cp.get("tags"),
                "emails": cp.get("emails"),
                "last_email": None,
                "days_ago": None,
                "match_type": None,
                "status": "никогда не писал",
            }
        )
    else:
        days = (now - last).days
        if days > 90:
            result.append(
                {
                    "name": cp.get("name"),
                    "owner": cp.get("owner"),
                    "tags": cp.get("tags"),
                    "emails": cp.get("emails"),
                    "last_email": last.isoformat(),
                    "days_ago": days,
                    "match_type": match_type,
                    "status": "давно не писал" if days < 180 else "очень давно",
                }
            )

result.sort(key=lambda x: (x["days_ago"] is None, -(x["days_ago"] or 0)))
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

never = sum(1 for r in result if r["last_email"] is None)
d90_180 = sum(1 for r in result if r["days_ago"] and 90 < r["days_ago"] <= 180)
d180 = sum(1 for r in result if r["days_ago"] and r["days_ago"] > 180)
by_email = sum(1 for r in result if r["match_type"] == "email")
by_domain = sum(1 for r in result if r["match_type"] == "domain")

print(f"Всего контрагентов: {len(email_base)}")
print(f"В отчёте: {len(result)}")
print(f"  Никогда не писал: {never}")
print(f"  90-180 дней:      {d90_180}")
print(f"  >180 дней:        {d180}")
print(f"  (match по email: {by_email}, по домену: {by_domain})")
print()
print("=== Топ-30 ===")
for r in result[:30]:
    owner = (r["owner"] or "?")[:20]
    name = (r["name"] or "?")[:40]
    last = r["last_email"][:10] if r["last_email"] else "никогда"
    days = r["days_ago"] if r["days_ago"] is not None else "—"
    mt = r["match_type"] or "—"
    emails = ", ".join(r["emails"][:2])
    print(f"  {name:40s} | {owner:20s} | {last} | {days} дн | {mt:6s} | {emails}")
