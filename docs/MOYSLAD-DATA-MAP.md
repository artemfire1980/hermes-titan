# Карта данных МойСклад

**Дата:** 2026-10-06
**Источник:** официальный MCP `https://mcp.moysklad.ru/tools/main`
**Инструменты:** `get_catalog`, `get_schema`, `get_resources`, `get_child_resources`

## Общая структура (81 ресурс)

- **31 dictionary** — справочники
- **37 document** — документы
- **13 report** — отчёты

## Ключевые справочники (dictionary)

| key | Что | Связка |
|---|---|---|
| `counterparty` | Клиенты и поставщики | **email** → почта |
| `organization` | Свои юрлица | |
| `product` | Номенклатура | |
| `service` | Услуги | |
| `variant` | Модификации | |
| `store` | Склады | |
| `retailstore` | Точки продаж | |
| `employee` | Сотрудники | |
| `contract` | Договоры | |
| `saleschannel` | Каналы продаж | |
| `project` | Проекты | |
| `pricetype` | Типы цен | |
| `currency` | Валюты | |
| `uom` | Единицы измерения | |
| `taxrate` | Ставки НДС | |
| `expenseitem` | Статьи расходов | |
| `country`, `region` | Страны, регионы | |
| `discount` | Скидки | |

## Ключевые документы (document)

| key | Что | child_key |
|---|---|---|
| `customerorder` | Заказ покупателя | customerorder_position |
| `demand` | Отгрузка | demandposition |
| `supply` | Приёмка | supply_position |
| `enter` | Оприходование | enter_position |
| `move` | Перемещение | move_position |
| `inventory` | Инвентаризация | inventory_position |
| `salesreturn` | Возврат покупателя | salesreturn_position |
| `purchasereturn` | Возврат поставщику | purchasereturn_position |
| `cashin`, `cashout` | Кассовые ордера | — |
| `paymentin`, `paymentout` | Платежи | — |
| `invoicein`, `invoiceout` | Счета | invoicein_position |
| `purchaseorder` | Заказ поставщику | purchaseorder_position |

## Ключевые отчёты (report)

- `profit_bycounterparty` — **прибыль по клиентам**.
- `report_counterparty_metrics` — метрики клиентов.
- `report_orders` — показатели заказов.
- `report_sales` — показатели продаж.
- `profit_byproduct` — прибыльность по товарам.
- `stock_all`, `stock_bystore` — остатки.
- `turnover` — обороты.
- `money` — движение денег.
- `dashboard` — общие показатели.

## Поля counterparty (для связки с почтой)

| field | type | filterable | Связка |
|---|---|---|---|
| `name` | String | ~ | по названию |
| `legalTitle` | String(4096) | ~ | по юрлицу |
| **`email`** | **String(255)** | **~, ~=** | **с почтой** |
| `phone` | String | ~ | по телефону |
| `inn` | String | ~ | уникальный |
| `kpp` | String | ~ | |
| `companyType` | Enum | =, != | legal/entrepreneur/individual |
| `archived` | Boolean | =, != | |
| `salesAmount` | Int | — | **сумма продаж** |
| `id` | UUID | =, != | |

## Поля customerorder

| field | type | filterable |
|---|---|---|
| `name` | String | ~ |
| `moment` | DateTime | date |
| `sum` | Float (копейки) | date |
| `agent` | Ref(counterparty, organization) | =, != |
| `organization` | Ref(organization) | =, != |
| `store` | Ref(store) | =, != |
| `contract` | Ref(contract) | =, != |
| `project` | Ref(project) | =, != |
| `salesChannel` | Ref(saleschannel) | =, != |
| `applicable` | Boolean | =, != |
| `created` | DateTime | date |
| `id` | UUID | =, != |

**child_key:** `customerorder_position` — позиции.

**НЕТ в схеме:** `state`, `createdAt`.

## Ограничения MCP

- **1000 объектов** — лимит `get_resources` за вызов.
- **Нет пагинации** в MCP — только через **прямой API** (`limit`/`offset`).
- **Токен** — в `.env` Hermes.

## Связка с почтой — план

1. **Из почты:** `company_summary.json` (204 компании, домены, контакты, даты).
2. **Из МойСклад:** `get_resources key=counterparty fields=[name,email,inn,salesAmount]`.
3. **Сопоставить** по `email` (или `name`).
4. **Для совпадений** — `get_resources key=customerorder filters=[agent.id=...]`.
5. **Собрать** `customer_360.json` — карточка клиента.
6. **Отчёт** — по всем + приоритезированные действия.

## Skills

- `moysklad-workflow` (34 КБ) — полный справочник полей.
- `moysklad-query` — процедура запросов (1000-лимит, операторы).
