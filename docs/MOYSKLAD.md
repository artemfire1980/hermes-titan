# CRM МойСклад — работает

> Интеграция через **официальный MCP** МойСклад (`mcp.moysklad.ru`).
> Обновлено: 2026-10-05.

## Что подключено

**Официальный MCP от МойСклад** — `https://mcp.moysklad.ru/tools/main`.

- **Версия:** moysklad-mcp 1.29.0.
- **Transport:** HTTP (JSON-RPC over POST).
- **ProtocolVersion:** 2024-11-05.
- **Зависимости:** нулевые (облако).
- **Токен:** `MOYSKLAD_TOKEN` в `/mnt/ai-ssd/hermes/.env`.
- **Headers:** `Authorization: Bearer ${MOYSKLAD_TOKEN}`.

## 4 инструмента (read-only by construction)

| Tool | Что делает |
|---|---|
| **`get_catalog`** | Каталог ресурсов: справочники (dictionary), документы (document), отчёты (report) |
| **`get_schema`** | Схема resource: fields, parameters, child_key, filter_operator_groups |
| **`get_resources`** | Список объектов с реальными данными (требует токен) |
| **`get_child_resources`** | Дочерние объекты для конкретного родителя |

**Write-инструментов нет.** **Только `get_*`.** Безопасность by construction.

## Порядок работы (из инструкции сервера)

1. `get_catalog` — выбрать ресурс.
2. `get_schema` — узнать поля.
3. `get_resources` — запросить данные (с `fields`!).
4. `get_child_resources` — дочерние (например, позиции заказа).

**Правила от МойСклад:**
- Только MCP-инструменты. Прямые HTTP-вызовы запрещены.
- `fields` обязателен — только нужные поля.
- Минимизировать вызовы.
- Только точные ключи из схемы. Никаких синонимов.

## Конфигурация Hermes

```yaml
mcp_servers:
  moysklad:
    url: https://mcp.moysklad.ru/tools/main
    headers:
      Authorization: "Bearer ${MOYSKLAD_TOKEN}"
    connect_timeout: 60
    enabled: true
    tools:
      include:
        - get_catalog
        - get_schema
        - get_resources
        - get_child_resources
      resources: false
      prompts: false
Токен — создание
Веб-интерфейс МойСклад:

Настройки → Пользователи → Токены доступа.

Создать → скопировать (показывается один раз).

Вставить в /mnt/ai-ssd/hermes/.env:
MOYSKLAD_TOKEN=<токен>
Права токена: просмотр (без редактирования/удаления).

Проверено
2026-10-05: hermes chat -q "Покажи список товаров" → 14 tool calls, 50 сек, реальные данные:

112+ товаров, включая:

Жировая глазурь «Экзотический аромат» (арт. 100557)

Плитка Chocotti-caramel (арт. 106135)

...

Отличие от ilyautov/moysklad-mcp-ru
Критерий	Официальный	ilyautov
Unicode-баг	❌ нет	✅ есть
Версия	1.29.0	0.2.0 alpha
Transport	HTTP (облако)	stdio (локально)
Зависимости	0	uvx + Python
Write	нет	есть (за гейтами)
Токен	.env	cabinets.json
Что осталось
Sanitizer — TODO (HTML → text, URL → redact).

Whitelist — 4 инструмента (все get_*).

Rate limits МойСклад — проверить при больших запросах.

fields — обязателен в get_resources, не забывать.
