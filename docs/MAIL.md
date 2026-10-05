# Почта — rubit-mcp-mail

> MCP-сервер для чтения почты Mail.ru (IMAP). Read-only by construction.
> Обновлено: 2026-10-05.

## Что это

**`rubit-mcp-mail==1.0.0`** — read-only MCP-сервер для почты.

**Ключевое:**
- **Read-only by construction:** `EXAMINE` + `BODY.PEEK` (не помечает прочитанным).
- **Нет** send / move / delete / flag в code paths.
- **IMAP** — любой провайдер (Mail.ru, Gmail, Fastmail).
- **Python 3.11+**, работает на ARM64 VIM4.
- **6 инструментов** (5 в whitelist).

**PyPI:** `rubit-mcp-mail`

## Конфигурация Hermes

```yaml
mcp_servers:
  rubit-mail:
    command: uvx
    args:
      - rubit-mcp-mail==1.0.0
      - serve
    enabled: true
    tools:
      include:
        - list_accounts
        - list_folders
        - list_messages
        - search_messages
        - read_message
      resources: false
      prompts: false
Настройка Mail.ru
1. Пароль для внешнего приложения
Веб-интерфейс Mail.ru:

Настройки → Все настройки → Безопасность.

Пароли для внешних приложений → Создать.

Название: Hermes MCP.

Тип: «Только чтение и удаление писем в Почте (IMAP, POP3)».

Скопировать пароль.

⚠️ Не «Полный доступ» — там SMTP, который нам не нужен.

2. Конфиг rubit-mcp-mail
~/.config/rubit-mcp-mail/config.toml:
download_dir = "~/Downloads/rubit-mcp-mail"

[accounts.mailru]
provider = "generic"
email    = "<mailbox>"
host     = "imap.mail.ru"
~/.config/rubit-mcp-mail/secrets.json — пароль (создан через auth mailru, права 600).

3. Активация
uvx rubit-mcp-mail==1.0.0 auth mailru
# ввести пароль для внешнего приложения
Проверка:
uvx rubit-mcp-mail==1.0.0 doctor mailru
Ожидаю: auth ok, список папок.

Whitelist — 5 инструментов
Инструмент	Что делает
list_accounts	Список настроенных аккаунтов
list_folders	Папки с количеством писем
list_messages	Сообщения в папке (пагинация)
search_messages	Поиск (критерии AND)
read_message	Полное чтение письма (headers + body + метаданные вложений)
Исключён:

Инструмент	Почему
get_attachment	Скачивание вложений на диск. Нарушает «только метаданные».
Использование
Список папок
Покажи список папок в почте
→ list_folders — INBOX (8201), Отправленные (8559), ...

Поиск писем
Найди письма от example@mail.ru за последнюю неделю
→ search_messages — фильтры.

Чтение письма
Прочитай последнее письмо в INBOX
→ read_message — headers, body, attachments (метаданные).

Что НЕ работает и почему
1. Отправка — исключена
rubit-mcp-mail — не имеет send-инструментов. By construction. Даже если пароль позволяет SMTP — инструмента нет.

2. Вложения — только метаданные
read_message возвращает имя, размер, mime. Содержимое — только через get_attachment — не в whitelist.

3. HTML — уточнить
README заявляет HTML → text. На практике — может возвращать HTML. Sanitizer — не реализован (TODO).

4. Ссылки — не открываются
Hermes в этом профиле не имеет browser/fetch/web. Ссылка в тексте — не активна.

Безопасность
Барьер	Что
Права Mail.ru	Пароль для внешнего приложения, только IMAP (без SMTP)
rubit-mcp-mail	EXAMINE + BODY.PEEK, нет write
Hermes tools.include	5 инструментов, без get_attachment
Профиль	Нет browser/fetch/web/telegram-команд
Известные проблемы
1. Пароль — только в secrets.json
Не в git, не в config.toml. Права 600. Никогда не показывать в чат.

2. KILN_LOG_LEVEL — аналог: config в secrets.json
Hermes не сохраняет два --env — но для rubit env не нужен (config.toml + secrets.json).

3. Firewall SMTP
Дополнительный барьер: iptables / ufw — блок исходящего smtp.mail.ru:465 для процесса. TODO (не реализовано).

Реальные данные (2026-10-05)
Аккаунт: <mailbox>

IMAP: imap.mail.ru:993

Папки: INBOX (8201), Archive (0), Отправленные (8559), Черновики (1), Корзина (0), Спам (5)

Всего: 16766 писем, 1 непрочитанное

Проверено: hermes chat -q "list_folders" → реальные данные.
