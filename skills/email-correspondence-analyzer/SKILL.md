---
name: email-correspondence-analyzer
query: "почта корреспонденция анализ"
description: Анализ почтовой корреспонденции: группировка по компаниям, восстановление истории, присвоение статусов.
version: 1.0.0
author: hermes-titan
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


## Notes

- `answered` flag unreliable — mostly false even for replied threads
- Filter out service emails: security@, mailer-daemon@, no-reply@
- Personal contacts on public domains should be excluded (<personal-contact>, etc.)
- Processing is incremental — continue from last offset when more batches needed
