# CRM МойСклад — ОТЛОЖЕНО

> Статус: ⏸️ **отложено** (Unicode-баг в alpha-версии MCP-сервера).
> Обновлено: 2026-10-05.

## Что планировалось

**`ilyautov/moysklad-mcp-ru`** — MCP-сервер для JSON API 1.2 МойСклад.

- **36 инструментов** (20 read в whitelist).
- **Python 3.10+**, ARM64 OK.
- **Write-guard** в коде (`MOYSKLAD_ALLOW_WRITE` + `confirm_write`).
- **Токен** в `~/.moysklad-mcp/cabinets.json`.

## Почему отложено

**Bash:** `UnicodeEncodeError: 'ascii' codec can't encode characters in position 7-10`

**Что происходит:**
- `ms_ping` **подключается** к `api.moysklad.ru` ✅.
- **Сервер падает** при **обработке ответа** — где-то `.encode('ascii')` на кириллице.
- **Все read-tools** — **та же ошибка**.

**Причина:** **баг в коде** `moysklad-mcp-ru` (alpha). **Не наш**.

## Что сделано

- ✅ **Токен** создан, сохранён в `~/.moysklad-mcp/cabinets.json` (chmod 600).
- ✅ **Whitelist** из 20 read-tools составлен.
- ✅ **Config** Hermes подготовлен.
- ❌ **Тест** — падает на Unicode.

**Токен:** **отозвать** (он **попал в чат** — утечка). **Создать новый** — при **разблокировке** задачи.

## Что дальше

### Вариант A — ждать фикс от автора

**`ilyautov/moysklad-mcp-ru`** — **alpha**. **Issue** на GitHub — **создать** с описанием.

**Репозиторий:** https://github.com/ilyautov/moysklad-mcp-ru

### Вариант B — использовать официальный MCP от МойСклад

**`https://mcp.moysklad.ru/tools/main`** — **облачный** MCP от **самого МойСклад**.

- **Плюсы:** официальный, работает.
- **Минусы:** **облако** — данные **идут через** `mcp.moysklad.ru`.

**Подключение:**
hermes mcp add moysklad --url https://mcp.moysklad.ru/tools/main --auth header

**Токен** — из МойСклад → Настройки → Пользователи → Токены доступа.

### Вариант C — свой минимальный MCP

**~200 строк Python** (FastMCP) — **только read**. **Максимум гарантий**.

**TODO**, если понадобится.

## Whitelist (готовый, для будущего)

**20 read-tools** `ilyautov`:

ms_check_auth, ms_list_sections, ms_get_section, ms_search_methods,
ms_map, ms_describe_method, ms_fetch_all, ms_list_cabinets,
ms_list_workflows, ms_get_workflow,
ms_get_stock, ms_get_products, ms_get_orders, ms_get_profit,
ms_get_money, ms_get_turnover, ms_get_counterparties,
ms_get_stores, ms_get_documents, ms_ping

**Исключены:** `ms_write_*`, `ms_create_*`, `ms_post_*`, `ms_delete_*`, `ms_call_raw`, `ms_get_raw`, `ms_add_cabinet`, `ms_set_key`, `ms_use_cabinet`, `ms_remove_cabinet`.

## Безопасность

| Барьер | Что |
|---|---|
| **Права МойСклад** | Read-only user (если возможно) или токен от основного |
| **`moysklad-mcp-ru`** | Write-guard: `MOYSKLAD_ALLOW_WRITE` не задан |
| **Hermes `tools.include`** | 20 read-tools, без write |
| **Профиль** | Нет browser/fetch/web |

## Решение

**Отложено до:**
1. **Фикса** Unicode-бага в `ilyautov` (issue на GitHub).
2. **Или** — перехода на **официальный MCP** МойСклад.
3. **Или** — написания **своего** MCP.

**Не критично** — CRM **не входит** в срочные задачи.
