---
name: mail
query: "почта, письма, mail, rubit"
description: Read-only доступ к почте Mail.ru (<mailbox>) через MCP rubit-mcp-mail. 5 инструментов чтения. Без отправки, удаления, скачивания вложений.
version: 1.0.0
author: hermes
license: MIT
---

# Mail — Rubit MCP Mail Reader

## Инструменты

| # | Инструмент | Аргументы | Назначение |
|---|-----------|-----------|------------|
| 1 | `list_accounts` | — | Список аккаунтов и статус аутентификации. Вызывать первым при ошибках auth. |
| 2 | `list_folders` | `account` (opt) | Папки ящика с кол-вом сообщений и непрочитанных. Нормализованный `role` (inbox/sent/junk/trash/drafts/archive). |
| 3 | `list_messages` | `account`, `folder` (inbox), `limit` (25), `offset` (0), `unread_only` (false) | Список сообщений в папке, новизна сверху. Сводки без тела. `handle` → `read_message`. |
| 4 | `read_message` | `handle` (обяз.), `account`, `max_chars` (20000) | Полное сообщение: заголовки, тело (HTML→text), метаданные вложений. Не помечает прочитанным. |
| 5 | `search_messages` | `account`, `folder` (inbox), `text`, `from_`, `subject`, `since`, `before`, `unread_only`, `limit` (25), `offset` (0) | IMAP-поиск по папке. Все критерии — AND. Результат → `handle` → `read_message`. |

## Папки и роли

| Role | Серверное имя (Mail.ru) | Примечание |
|------|------------------------|------------|
| inbox | INBOX | Входящие |
| sent | Sent | Отправленные |
| drafts | Drafts | Черновики |
| trash | Trash | Корзина |
| junk | Junk / Spam | Спам — роль нормализована, но Mail.ru может называть по-разному; `list_folders` покажет реальное имя |

Архива у Mail.ru нет как отдельной папки — `list_folders` покажет, что доступно.

## Ограничения

- **Read-only**: нет отправки, удаления, перемещения, маркировки прочитанным.
- **Вложения**: `read_message` возвращает метаданные (имя, размер, тип), но не скачивает и не отдаёт тело файла.
- **Ссылки**: не извлекает и не открывает URL из тела письма.
- **Тело**: HTML конвертируется в plain text; обрезается по `max_chars` (дефолт 20 000).
- **Пагинация**: `limit` ≤ 200, `offset` для постраничного обхода.

## Типичные сценарии

1. **Что нового** — `list_folders` → `list_messages(folder="inbox", unread_only=true, limit=20)` → `read_message` по интересным `handle`.
2. **Поиск по отправителю** — `search_messages(from_="example@domain.ru", folder="inbox", since="2026-10-01")`.
3. **Поиск по теме** — `search_messages(subject="заказ", folder="sent")`.
4. **Полный текст письма** — `handle` из списка → `read_message(handle, max_chars=50000)`.
5. **Опрос ящика** — `list_accounts` (проверка auth) → `list_folders` → цикл по папкам.

## Сводка

5 инструментов, всё read-only. Рабочий путь: `list_accounts` → `list_folders` → `list_messages`/`search_messages` → `read_message`. Вложения и ссылки только метаданные — скачивания нет.
