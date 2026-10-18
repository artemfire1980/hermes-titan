---
name: email-correspondence-analyzer
query: "почта корреспонденция анализ"
description: Анализ почтовой корреспонденции: группировка по компаниям, восстановление истории, присвоение статусов.
version: 1.0.0
author: hermes
license: MIT
---

# Email Correspondence Analyzer

## Workflow

1. Connect to mail MCP (rubit-mail): `list_accounts` → `list_folders`
2. Fetch emails in batches of 50 from INBOX + Отправленные
3. Filter out self-sent (artem_s@chocoladovo.by → @chocoladovo.by)
4. Group by company domain, excluding public mail services
5. Assign statuses per rules
6. Generate report

## Память (Holographic) — перед ответом

При вопросах про **почту / письма** — **сначала** recall:

1. `recall("Почта")` — общее (аккаунт, IMAP, MCP rubit-mail).
2. `recall("Почта [тема]")` — конкретика:
   - `recall("Почта инструменты")` — 5 MCP tools.
   - `recall("Почта лимиты")` — list_messages без limit зависает.
   - `recall("Почта папки")` — INBOX, Sent, Drafts, Trash, Junk.
   - `recall("Почта аудит")` — 2309 писем, 204 компании.

**Важно:** `list_messages` **всегда** с `folder` + `limit ≤ 200`. Без limit — **зависает**.

**Read-only:** нет отправки, удаления, вложений.

**Документация:** `docs/EMAIL-ANALYSIS-2026-10-06.md`.

**Skills:** `mail`, `email-correspondence-analyzer`.

## Company Detection Rules

- Domain = part after "@"
- Ignore public domains: mail.ru, gmail.com, yandex.ru, outlook.com, hotmail.com, icloud.com, yahoo.com, rambler.ru, bk.ru, list.ru, inbox.ru
- If public domain but company name in subject/signature → attribute to company
- If public domain without identifiers → "Частное лицо / не определено"

## Status Rules

1. Действующий — коммерческая переписка, последнее письмо ≤ 90 дней, активный диалог
2. Требует внимания — коммерческая переписка, последнее письмо > 90 дней
3. Срочно требует внимания — есть неотвеченный запрос с коммерческим контекстом
4. Завершено — был интерес, переписка закрылась естественно
5. Не определено — частное лицо, рассылка, спам

## Current Analysis (2026-10-06)

Mailbox: artem_s@chocoladovo.by
Period: 2026-01-29 – 2026-10-06
Total emails processed: ~972 (filtered)
Companies identified: 82

Status distribution:
- Действующий: 15
- Требует внимания: 2
- Не определено: 60
- Срочно требует внимания: 0
- Завершено: 0

Top companies:
1. cvk-trade.ru — 250 писем, Королькова Елена, ВК (заказы, документы, отгрузка)
2. pub_mail.ru — 127 писем, AZNUR MMC, Artem Fireglow (таджик, договоры, документы)
3. chocoladovo.by — 114 писем, внутренние (Volha, Production, Елена Чернышова)
4. vkonditery.ru — 57 писем, Галина Смирнова (документы, отгрузка, сверки)
5. pub_gmail.com — 44 писем, Kaplinski, Sattorov (спецификации, каталоги)

## Notes

- `answered` flag unreliable — mostly false even for replied threads
- Filter out service emails: security@, mailer-daemon@, no-reply@
- Personal contacts on public domains should be excluded (aleksandr150572@gmail.com, etc.)
- Processing is incremental — continue from last offset when more batches needed

## Анализ: кому давно не писал

**Готовый файл:** `/mnt/ai-ssd/hermes/cache/moysklad-audit/emails_all.json` — 18932 письма (INBOX + Sent, from/to/date).

**Готовый отчёт:** `docs/EMAIL-OVERDUE-2026-10-18.md`.

**Порядок:**
1. `email_base.json` — 1702 контрагента (email, owner, tags).
2. `emails_all.json` — 18932 письма (from/to/date).
3. `analyze_emails_v2.py` — матчинг: email → domain (только корпоративные) → last_seen.
4. Фильтр: >90 дней → «давно», >180 → «очень давно», нет писем → «никогда».

**НЕ ХОДИ в MCP** для email — там только `counterparty.email` (12 из 348).

**Скрипты:**
- `collect_emails.py` — сбор (IMAP, батчи 200, ~25 мин для 19K писем).
- `analyze_emails_v2.py` — анализ (1–2 сек).
