# Внешние интеграции — MCP-серверы

> MCP-серверы, подключённые к Hermes-Titan: почта, CRM, 3D-принтер.
> Обновлено: 2026-10-05.

## Обзор

| Сервис | MCP-сервер | Инструментов | Статус |
|---|---|---|---|
| **Почта Mail.ru** | `rubit-mcp-mail==1.0.0` | 5 read | ✅ работает |
| **CRM МойСклад** | `ilyautov/moysklad-mcp-ru` | — | ⏸️ отложен (Unicode-баг alpha) |
| **3D-принтер ZAV** | `Kiln (kiln3d) 1.4.1.1` | 71 read | ✅ работает |

## Принципы безопасности

### 1. Defense in depth — 4 барьера

1. **Права в сервисе** — read-only аккаунт / токен.
2. **MCP-сервер** — write-guard в коде (где возможно).
3. **`tools.include` в Hermes** — whitelist (только нужные инструменты).
4. **Изоляция профиля** — нет browser/fetch/web, куда утекать.

### 2. Whitelist, не blacklist

- **Только `include`** — явный список разрешённых.
- **Никогда `exclude`** — новые инструменты сервера могут пройти мимо.

### 3. Секреты — вне git

- **`~/.config/rubit-mcp-mail/secrets.json`** — пароль Mail.ru (600).
- **`~/.kiln/config.yaml`** — auth Kiln (600).
- **`/mnt/ai-ssd/hermes/.env`** — остальные секреты.

### 4. Sanitizer (TODO)

- **HTML → plain text** — не реализован.
- **URL → `[REDACTED]`** — не реализован.
- **Приоритет:** низкий (сейчас нет write-инструментов в whitelist).

## Правила безопасности MCP

**Полные правила:** `docs/SECURITY.md`.

**Кратко:**
- **Только read-only** — write/create/delete/set/run/print запрещены.
- **Не обходить** `tools.include` через прямой HTTP/curl/G-code.
- **Не читать секреты** (`.env`, `secrets.json`, `config.toml`).
- **Не открывать ссылки**, не скачивать вложения.
- **Нет инструмента** → «недоступно по политике безопасности».

## Управление MCP-серверами

**Добавить:**
```bash
hermes mcp add <name> --command <bin> --env KEY=VALUE --args <args>
⚠️ Правило: все Hermes-флаги — до --args. --args — последним.

Проверить:
hermes mcp list
hermes mcp test <name>
Удалить:
hermes mcp remove <name>
Применить после изменений:
hermes gateway restart
Известные проблемы
1. Hermes input() падает на кириллице
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xd0
Обход: отвечать латиницей (y, n), не да/нет.

2. --args — nargs=REMAINDER
Поглощает все опции после себя. Правило: --args — последним.

3. connect_timeout — из config, не из CLI
--connect-timeout в hermes mcp add не сохраняется в config. Fix: python-патч mcp_servers.<name>.connect_timeout.

4. Два --env — сохраняется один
Из --env A=1 --env B=2 — Hermes может сохранить только один. Fix: python-патч.

5. Python SDK initialize timeout
MCP Python SDK игнорирует connect_timeout — свой таймаут 60 сек. Fix: для тяжёлых серверов — --connect-timeout 180 через CLI (правильный порядок), или python-патч.

Ссылки
docs/KILN.md — 3D-принтер Kiln.

docs/MAIL.md — почта Mail.ru.

docs/MOYSKLAD.md — CRM (отложен).

docs/PRINTER-CONFIG.md — конфиг принтера ZAV.
