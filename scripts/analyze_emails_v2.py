#!/usr/bin/env python3
"""Анализ: кому из МойСклад давно не писал. Матчинг по домену + email + имени."""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

PUBLIC_DOMAINS = frozenset(
    {
        # RU
        "mail.ru",
        "bk.ru",
        "list.ru",
        "inbox.ru",
        "internet.ru",
        "mail.by",
        "yandex.ru",
        "yandex.com",
        "ya.ru",
        "narod.ru",
        "rambler.ru",
        "tut.by",
        "onliner.by",
        # Global
        "gmail.com",
        "googlemail.com",
        "outlook.com",
        "hotmail.com",
        "live.com",
        "msn.com",
        "icloud.com",
        "me.com",
        "mac.com",
        "yahoo.com",
        "aol.com",
        "protonmail.com",
        "proton.me",
        # Corporate-but-shared
        "yandex-team.ru",
        "sberbank.ru",
    }
)

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
    # по домену — только корпоративные (PUBLIC_DOMAINS → только точный email)
    if last is None:
        for el in cp_emails:
            if "@" not in el:
                continue
            domain = el.split("@", 1)[1]
            if domain in PUBLIC_DOMAINS:
                continue  # публичный — только точный email, не domain
            dt = last_seen_domain.get(domain)
            if dt and (last is None or dt > last):
                last = dt
                match_type = "domain_corporate"

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
by_domain = sum(1 for r in result if r["match_type"] == "domain_corporate")
by_domain_public = sum(1 for r in result if r["match_type"] == "domain")  # старые

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

# === argparse + фильтр по owner (универсальный отчёт) ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Анализ email — кому давно не писал")
    parser.add_argument("--owner", help="Фильтр по owner (например, 'Самсонов А. О.')")
    args = parser.parse_args()

    if args.owner:
        filtered = [r for r in result if r.get("owner") == args.owner]
        print(f"\n=== Фильтр по owner: {args.owner} → {len(filtered)} ===")
        # TITAN: пишем в отдельный файл, не затираем общий OUT
        slug = "".join(c if c.isalnum() else "_" for c in args.owner).strip("_")[:40]
        owner_out = OUT.parent / f"analysis_overdue_v2_{slug}.json"
        owner_out.write_text(json.dumps(filtered, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  → сохранено: {owner_out}")
        never = sum(1 for r in filtered if r["last_email"] is None)
        d90_180 = sum(1 for r in filtered if r["days_ago"] and 90 < r["days_ago"] <= 180)
        d180 = sum(1 for r in filtered if r["days_ago"] and r["days_ago"] > 180)
        print(f"  никогда: {never}")
        print(f"  90-180:  {d90_180}")
        print(f"  >180:    {d180}")
        print(f"  всего:   {len(filtered)}")
