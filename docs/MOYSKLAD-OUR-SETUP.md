# МойСклад — структура и специфика (HERMES-TITAN)

> **Источник истины** для работы с МойСклад в проекте HERMES-TITAN.
> Аудит: 2026-10-09. Данные: 2694 контрагента, 1851 заказ, 764 товара.
> API: `https://api.moysklad.ru/api/remap/1.2`
> Токен: `MOYSKLAD_TOKEN` в `/mnt/ai-ssd/hermes/.env`
> Файлы аудита: `/mnt/ai-ssd/hermes/cache/moysklad-audit/`

## 0. Как работать с API

### Обязательные заголовки

Authorization: Bearer $MOYSKLAD_TOKEN
Accept: application/json;charset=utf-8
Accept-Encoding: gzip

Без `Accept-Encoding: gzip` API возвращает **HTTP 415 Unsupported Media Type**.
Без `Accept: application/json;charset=utf-8` — тоже возможен 415 (nginx).

### Пагинация и expand

- `?limit=N&offset=M` — N максимум 1000.
- **`expand` работает только до `limit=100`.** На `limit>=200` expand молча отключается: вложенные объекты (`contactpersons`, `positions.assortment`) пропадают **без ошибки**.
- **Вывод:** для сбора с expand — `limit=100`. Для справочников без expand — `limit=1000`.

### MCP-ограничения

- `mcp__moysklad__get_resources` — **не более 1000 объектов, без пагинации**.
- Возвращает **только поля, указанные в `fields`**. Без `fields` — пустой массив.
- MCP-схема **неполная**: нет `owner`, `group`, `contactpersons`, `ogrnip`, `accounts`, `files`, `state`, `actualAddressFull`, `legalFirstName/LastName/MiddleName`.
- **`id` возвращается**, если явно указать его в `fields`. Утверждение «id не возвращается» — ошибочно.

### Ресурсы с 403 (нет прав у токена)

`saleschannel`, `retailstore`, `purchaseorder`, `enter`, `loss`, `move`, `inventory`, `internalorder`, `invoicein`, `prepayment`, `purchasereturn`, `retaildemand`.

## 1. Рабочие страницы (где что делаем)

| Раздел UI | Ресурс API | Что делаем |
|---|---|---|
| `#customerorder` | `customerorder` | Формируем заказы покупателя |
| `#invoiceout` | `invoiceout` | Выставляем счета |
| `#demand` | `demand` | Отгрузки (накладные) |
| `#good` | `product` | Список товаров |
| `#pricelist` | `pricelist` | Действующий прайс |
| `#finance` | `paymentin` / `paymentout` | Поступление денег |
| `#customersbalancelist?selectedAspect=WithCompanies` | `report_*` | Взаиморасчёты, долги, акты сверок |
| `#company` | `counterparty` | База клиентов |
| `#Company/edit?id=<uuid>` | `counterparty/<id>` | Карточка клиента |

## 2. Ключевые сущности

### 2.1. counterparty (Контрагент) — 2694

**Поля API (30):**
`meta`, `id`, `accountId`, `owner`, `shared`, `group`, `updated`, `name`, `description`, `externalCode`, `archived`, `created`, `email`, `phone`, `companyType`, `legalTitle`, `actualAddress`, `actualAddressFull`, `legalLastName`, `legalFirstName`, `legalMiddleName`, `inn`, `ogrnip`, `accounts`, `tags`, `contactpersons`, `notes`, `state`, `salesAmount`, `files`.

**Поля MCP-схемы (21):**
`name`, `code`, `externalCode`, `legalTitle`, `companyType`, `inn`, `kpp`, `email`, `phone`, `fax`, `actualAddress`, `legalAddress`, `discountCardNumber`, `description`, `tags`, `archived`, `salesAmount`, `bonusPoints`, `created`, `updated`, `id`.

**Типы контрагентов:**

| companyType | Кол-во | % | Что это |
|---|---|---|---|
| legal | 2419 | 89.8% | Юрлицо |
| entrepreneur | 273 | 10.1% | ИП |
| individual | 2 | 0.1% | Физлицо |

**Заполненность полей (2694):**

| Поле | Заполнено | % |
|---|---|---|
| name | 2694 | 100.0% |
| companyType | 2694 | 100.0% |
| group | 2694 | 100.0% |
| accounts | 2694 | 100.0% |
| owner | 2690 | 99.9% |
| tags | 2490 | 92.4% |
| legalAddress | 2138 | 79.4% |
| legalTitle | 2094 | 77.7% |
| inn | 1997 | 74.1% |
| kpp | 1615 | 59.9% |
| ogrn | 1541 | 57.2% |
| actualAddress | 1400 | 52.0% |
| phone | 1108 | 41.1% |
| email | 940 | 34.9% |
| description | 683 | 25.4% |
| salesAmount | 442 | 16.4% |
| fax | 285 | 10.6% |
| legalLastName | 264 | 9.8% |
| ogrnip | 240 | 8.9% |
| legalFirstName | 180 | 6.7% |
| legalMiddleName | 179 | 6.6% |
| archived | 0 | 0.0% |
| state | 0 | 0.0% |
| status | 0 | 0.0% |

**Кастомные поля (attributes):**

| Поле | Тип | Заполнено | % |
|---|---|---|---|
| Сайт | string | 831 | 30.8% |
| ХОЛДИНГ | string | 461 | 17.1% |
| Маркировка | string | 284 | 10.5% |
| GLN | string | 51 | 1.9% |
| Схема проезда | file | 29 | 1.1% |

**Owner (менеджеры) — 22:**

| ФИО | Клиентов |
|---|---|
| Самсонов А. О. | 418 |
| Демух А. Г. | 383 |
| Ерашов М. В. | 365 |
| Богданович Н. | 334 |
| Сушко О. М. | 230 |
| Агабабян А. Г. | 209 |
| Банкузов О. В. | 183 |
| Фернандо Г. | 146 |
| Хапанков В. | 101 |
| П Т. | 90 |
| Саутыч Б. Л. | 71 |
| Денисов С. В. | 65 |
| Демидова А. С. | 34 |
| Павлович Д. М. | 21 |
| Карманова Т. О. | 10 |
| Чернышова Е. В. | 8 |
| Мазурчик И. В. | 6 |
| Шило К. | 4 |
| Героник И. И. | 4 |
| Шкундалев М. Е. | 4 |
| Кашников Д. | 3 |
| Смирнов С. С. | 1 |

**Group (отделы) — 2:**
- `Основной` — 2693
- `ОтделГлазури` — 1 (тестовый)

**Статусы (metadata) — 7, но НЕ используются:**
`покупатель`, `в разработке`, `поставщик`, `С ВЫСТАВКИ`, `АРХИВНЫЙ`, `перевозчик`, `ОП`.

**Контактные лица (contactpersons):**
- Всего: **2859**, из них **1910 с email (66.8%)**.
- Доступны только через `expand=contactpersons` у контрагента.
- Отдельного ресурса `/entity/counterparty/contactpersons` **нет** (404).
- Поля: `name` (только имя), `email`, `phone`, `position` (не заполнена).

**Email — два источника:**

| Источник | Контрагентов | % |
|---|---|---|
| только `counterparty.email` | 420 | 15.6% |
| только `contactpersons[].email` | 759 | 28.2% |
| и там, и там | 520 | 19.3% |
| **ХОТЬ ГДЕ-ТО** | **1699** | **63.1%** |
| нигде | 995 | 36.9% |

**Уникальных email: 2369.**

**Холдинги (кастомное поле ХОЛДИНГ) — 221, 461 контрагент:**
X5 (65), Магнит (45), Светофор (14+7), Олимп (13+3), Объединённые кондитеры (10+3), ОЗОН (6), ДЕСЕРТ (6), ШИРИН-АСТАНА (5), ПЯТЬ ФУТОВ (4), ВЕЛЯН (4), ВАШИ ПРОДУКТЫ (4), ТС Верный (4), Вкусландия (4), Виноградов (4).

**Связи:**
- `counterparty.id` ← `customerorder.agent`, `demand.agent`, `invoiceout.agent`, `paymentin.agent`, `paymentout.agent`, `contract.agent`.
- `counterparty.owner` → `employee`.
- `counterparty.group` → `group`.
- `counterparty.contactpersons` → вложенный список (только expand).

### 2.2. product (Товар) — 764

**Состав:** 420 активных + 340 архивных + 4 услуги.

**Топ-15 по сумме заказов:**

| Товар | Сумма | Кол-во |
|---|---|---|
| Соломка "Chocolike caramel" глазированная с арахисом | 120.24 млн | 442 206 |
| 📦 Соломка с ирисо-сливочным ароматом, карамельная глазурь с арахисом | 90.55 млн | 615 283 |
| Зефир глазированный с арахисом (кор. 2,5 кг) | 59.16 млн | 253 820 |
| Зефир в глазури со вкусом карамели и арахисом (кор. 2,5 кг) | 58.23 млн | 266 180 |
| Зефир глазированный с кокосовой стружкой "VIVALDI ZIMA" | 38.89 млн | 130 535 |
| Глазурь кондитерская со вкусом карамели | 34.52 млн | 124 170 |
| Зефир глазированный "VIVALDI CLASSIC" (кор. 3 кг) | 34.04 млн | 106 290 |
| Печенье глазированное с арахисом "Chocoline" | 30.92 млн | 158 811 |
| Соломка "Chocolike classic" глазированная с арахисом | 22.97 млн | 82 641 |
| 📦 Вафельные трубочки "Сливочные" глазированные карамельной глазурью с арахисом | 21.41 млн | 174 797 |
| Печенье "Chocoline" глазированное с арахисом | 21.26 млн | 134 446 |
| Вафельные трубочки "CHOCOROLLS" со сливочным вкусом | 15.56 млн | 52 510 |
| Вафли "Waffer-r-rs" с молочно-шоколадным вкусом | 14.50 млн | 46 029 |
| 📦 Вафельные трубочки "CHOCOROLLS Caramel" | 13.47 млн | 50 208 |
| 📦 Вафли "Waffer-r-rs Caramel" | 13.06 млн | 48 225 |

📦 = архивный товар (снят с производства, но продаётся).

**Основные линейки:**
- **Соломка** "Chocolike" (caramel, classic) — главный продукт.
- **Зефир** "VIVALDI" (CLASSIC, ZIMA, с арахисом, кокосом).
- **Печенье** "Chocoline" / "Шоколайн".
- **Вафли** "Waffer-r-rs", "CHOCOROLLS", "Шокотти".
- **Глазурь кондитерская** (карамель, белая).
- **Сладости мучные** "Крендельки".
- **Конфеты** "Кокосик", "Toffeo" (шоу-боксы 40г).

**Каталог:** 71 группа товаров (`productfolder`).

### 2.3. customerorder (Заказ покупателя) — 1851

**Поля API:** `meta`, `id`, `accountId`, `owner`, `shared`, `group`, `updated`, `name`, `externalCode`, `moment`, `applicable`, `rate`, `sum`, `agent`, `organization`, `organizationAccount`, `state`, `attributes`, `created`, `printed`, `published`, `files`, `positions`, `vatEnabled`, `vatIncluded`, `vatSum`, `payedSum`, `shippedSum`, `invoicedSum`, `reservedSum`.

**Денежные поля (в копейках, read-only):**
- `sum` — сумма заказа.
- `payedSum` — оплачено.
- `shippedSum` — отгружено.
- `invoicedSum` — выставлено счетов.
- `reservedSum` — зарезервировано.
- `vatSum` — НДС.

**Статусы (9 используются из 17):**

| Статус | Заказов | % |
|---|---|---|
| ОТГРУЖЕН | 1788 | 96.6% |
| ПЛАНЫ | 35 | 1.9% |
| ПЛАНИРУЕМЫЙ | 11 | 0.6% |
| СНЯТО | 6 | 0.3% |
| НА ОТГРУЗКУ | 3 | 0.2% |
| (без статуса) | 3 | 0.2% |
| В РАБОТЕ | 2 | 0.1% |
| НА СКЛАДЕ | 2 | 0.1% |
| СОГЛАСОВАНО на ОТГРУЗКУ | 1 | 0.1% |

**Суммы:**
- Реальные заказы: **0.60 млрд руб**.
- Планы (статус ПЛАНЫ): **0.42 млрд руб**.
- Итого: **1.02 млрд руб**.
- Средний чек: **592 тыс руб**.
- Максимум: **25.1 млн руб**.

**Динамика по годам (реальные заказы):**

| Год | Заказов | Сумма |
|---|---|---|
| 2014 | 50 | 18.17 млн |
| 2015 | 123 | 27.93 млн |
| 2016 | 159 | 49.78 млн |
| 2017 | 170 | 38.91 млн |
| 2018 | 111 | 36.27 млн |
| 2019 | 130 | 38.36 млн |
| 2020 | 217 | 45.12 млн |
| 2021 | 216 | 52.15 млн |
| 2022 | 168 | 44.50 млн |
| 2023 | 191 | 49.82 млн |
| 2024 | 140 | 81.62 млн |
| 2025 | 68 | 46.22 млн |
| 2026 (10 мес) | 62 | 68.93 млн |

**Тренд:** количество падает, сумма растёт (укрупнение клиентов). 2025–2026 — резкое падение активности (~6 заказов/мес против ~18 в 2020).

**Связи:**
- `customerorder.agent` → `counterparty`.
- `customerorder.organization` → `organization`.
- `customerorder.store` → `store`.
- `customerorder.contract` → `contract`.
- `customerorder.project` → `project`.
- `customerorder.salesChannel` → `saleschannel`.
- `customerorder.state` → статус (metadata).
- `customerorder.owner` → `employee`.
- `customerorder.positions[].assortment` → `product` / `service` / `variant` / `bundle`.
- `child_key = customerorder_position`.

**Позиции:** 13 856 позиций в 1851 заказе (обогащены названиями товаров).

**Топ-10 клиентов по сумме заказов (без планов):**

| Клиент | Сумма | Заказов |
|---|---|---|
| Велян | 61.69 млн | 73 |
| Biologic | 60.41 млн | 6 |
| АХМАД ТИЧОРАТ (РУХМИН) | 47.56 млн | 38 |
| Мекенаева А.К. КАЗАХСТАН | 39.92 млн | 111 |
| Молдабекова Г.О. | 37.87 млн | 38 |
| BAOLIS (SUIFENHE) | 35.31 млн | 12 |
| ЛЮБИМАЯ КУБАНЬ КФ | 33.83 млн | 15 |
| ЛИДЕР | 26.84 млн | 63 |
| ШИРИН-АСТАНА (Алем-Тетті) | 23.63 млн | 80 |
| ШИРИН-АСТАНА (ПЕЧЕНЮШ) | 22.83 млн | 40 |

**Важно:** «Самсонов А. (план)» — 361 млн — это **НЕ клиент**, а **план продаж**. Исключать из аналитики.

### 2.4. demand (Отгрузка) — 1283

**Поля:** аналогично customerorder + `positions`, `payedSum`, `shippedSum`, `invoicedSum`, `reservedSum`, `vatSum`, `sum`.

**Связи:**
- `demand.agent` → `counterparty`.
- `demand.organization` → `organization`.
- `demand.store` → `store`.
- `demand.contract` → `contract`.
- `demand.project` → `project`.
- `demand.salesChannel` → `saleschannel`.
- `demand.state` → статус (metadata, 8 штук).
- `demand.owner` → `employee`.
- `demand.positions[].assortment` → `product`.
- `child_key = demandposition`.

### 2.5. invoiceout (Счёт покупателю) — 1338

**Поля:** аналогично.
**Связи:** `agent`, `organization`, `store`, `contract`, `project`, `salesChannel`, `state`, `owner`, `positions`.
**child_key = invoiceout_position**.

### 2.6. paymentin (Входящий платёж) — 1490

**Поля:** `sum`, `agent`, `organization`, `contract`, `project`, `salesChannel`, `state`, `owner`, `paymentPurpose`, `incomingNumber`, `incomingDate`, `moment`.
**Связи:** `agent` → `counterparty`, `contract` → `contract`.

### 2.7. paymentout (Исходящий платёж) — 21

### 2.8. contract (Договор) — 246

**Поля:** `name`, `code`, `externalCode`, `moment`, `sum`, `agent`, `organization`, `owner`, `state`, `contractType`, `rewardPercent`, `rewardType`.

**Связи:**
- `contract.agent` → `counterparty`.
- `contract.organization` → `organization`.
- `contract.owner` → `employee`.
- `contract.state` → статус (3 штуки в metadata).

### 2.9. organization (Юрлицо) — 2

**Поля:** `name`, `legalTitle`, `inn`, `kpp`, `ogrn`, `legalAddress`, `actualAddress`, `accounts`, `email`, `phone`.

### 2.10. store (Склад) — 10

**Поля:** `name`, `code`, `externalCode`, `description`, `address`, `parent`, `group`, `owner`, `shared`, `archived`.

### 2.11. project (Проект) — 13

**Поля:** `name`, `code`, `description`, `owner`, `shared`, `group`, `archived`.

### 2.12. group (Отдел) — 9

**Поля:** `name`, `description`, `parent`, `index`, `shared`.

### 2.13. employee (Сотрудник) — 1

**Поля:** `name`, `externalCode`, `email`, `phone`, `position`, `inn`, `uid`, `archived`, `group`, `owner`.

### 2.14. region (Регион) — 86

### 2.15. country (Страна) — 254

### 2.16. uom (Единица измерения) — 72

### 2.17. productfolder (Группа товаров) — 71

### 2.18. saleplatform (Площадка продаж) — 21

### 2.19. expenseitem (Статья расходов) — 11

### 2.20. taxrate (Ставка НДС) — 6

### 2.21. currency (Валюта) — 4

### 2.22. discount (Скидка) — 1

### 2.23. task (Задача) — 1

### 2.24. pricelist (Прайс-лист) — 29

**Поля:** `name`, `moment`, `organization`, `priceType`, `positions[]` (товар + цена).

## 3. Карта связей

counterparty (id)
├── ← customerorder.agent
├── ← demand.agent
├── ← invoiceout.agent
├── ← paymentin.agent
├── ← paymentout.agent
├── ← contract.agent
├── → owner (employee)
├── → group (group)
└── → contactpersons[] (вложенный)

customerorder
├── → agent (counterparty)
├── → organization (organization)
├── → store (store)
├── → contract (contract)
├── → project (project)
├── → salesChannel (saleschannel)
├── → state (metadata)
├── → owner (employee)
└── → positions[].assortment → product/service/variant/bundle

demand → аналогично customerorder
invoiceout → аналогично customerorder
paymentin → agent, organization, contract, project, salesChannel, owner
paymentout → аналогично paymentin

contract
├── → agent (counterparty)
├── → organization (organization)
└── → owner (employee)

product
├── → productFolder (productfolder)
└── → owner (employee)

pricelist
├── → organization
└── → positions[].assortment → product

## 4. Теги (ключ к сегментации)

**Теги — основная система сегментации.** `status` и `state` не используются.

**29 уникальных тегов.**

### Менеджеры (16):

| Тег | Контрагентов |
|---|---|
| самсонов | 348 |
| богданович | 330 |
| демух | 325 |
| ерашов | 318 |
| сушко | 228 |
| агабабян | 206 |
| банкузов | 134 |
| фернандо | 128 |
| хапанков | 99 |
| денисов | 67 |
| демидова | 33 |
| саутыч | 29 |
| мазурчик | 5 |
| павлович | 4 |
| шило | 4 |
| кашников | 1 |

**Важно:** теги-менеджеры **не всегда совпадают с `owner`**. Например, есть `П Т.` (90 клиентов, owner), но тега `п т.` нет в списке менеджеров — вместо него тег `п т.` (82). Есть owner `Карманова`, `Чернышова`, `Героник`, `Шкундалев`, `Смирнов` — без тегов.

### Категории (3):

| Тег | Контрагентов |
|---|---|
| глазури | 1335 |
| кондитерка | 962 |
| напитки | 7 |

### Роли:

| Тег | Контрагентов |
|---|---|
| покупатель | 215 |
| перевозчик | 56 |
| поставщик | 43 |

### События:

| Тег | Контрагентов |
|---|---|
| продэкспо | 165 |

### Прочее:

| Тег | Контрагентов |
|---|---|
| п т. | 82 |
| арма | 19 |
| x5 | 5 |
| маркетинг | 3 |
| займ | 3 |
| диадок | 1 |

### Кросс-таблица: менеджер × категория

| Менеджер | глазури | кондитерка | покупатель | поставщик | перевозчик | продэкспо |
|---|---|---|---|---|---|---|
| Ерашов М. В. | 59 | 265 | 88 | 1 | 11 | 38 |
| Самсонов А. О. | 129 | 250 | 4 | 0 | 9 | 0 |
| Богданович Н. | 280 | 57 | 3 | 1 | 0 | 1 |
| Демух А. Г. | 176 | 147 | 0 | 0 | 9 | 0 |
| Сушко О. М. | 209 | 0 | 2 | 0 | 0 | 74 |
| Агабабян А. Г. | 158 | 0 | 3 | 12 | 15 | 7 |
| Банкузов О. В. | 23 | 144 | 3 | 1 | 3 | 0 |
| П Т. | 6 | 77 | 74 | 0 | 1 | 0 |
| Фернандо Г. | 123 | 1 | 2 | 0 | 3 | 0 |
| Хапанков В. | 74 | 2 | 0 | 0 | 0 | 36 |
| Саутыч Б. Л. | 1 | 13 | 6 | 27 | 1 | 0 |

**Выводы:**
- **Ерашов** — универсал (кондитерка + покупатели + продэкспо).
- **Самсонов** — универсал (глазури + кондитерка).
- **Богданович** — специалист по глазурям.
- **Сушко** — глазури + продэкспо.
- **Саутыч** — закупки (поставщик).
- **Агабабян** — закупки + логистика.

## 5. ХОЛДИНГи (кастомное поле)

**221 уникальный холдинг, 461 контрагент (17.1%).**

**Топ-20:**

| Холдинг | Контрагентов |
|---|---|
| т/с "Х5" | 65 |
| т/с "Магнит" | 45 |
| ТС Светофор | 14 |
| Олимп | 13 |
| Объединённые кондитеры | 10 |
| Воронежский МК | 9 |
| ТС Маяк | 7 |
| ТС Светофор ТС Маяк | 7 |
| Щебуняева | 6 |
| ДЕСЕРТ | 6 |
| ОЗОН | 6 |
| ШИРИН-АСТАНА | 5 |
| Смолякова | 5 |
| ПЯТЬ ФУТОВ | 4 |
| ВЕЛЯН | 4 |
| ВАШИ ПРОДУКТЫ | 4 |
| ТС Верный | 4 |
| Вкусландия | 4 |
| Виноградов | 4 |
| ОРЛОВ | 3 |

**Важно:** холдинг — **текстовое поле**, не API-связь. Для агрегации продаж по холдингу — группировать по значению `ХОЛДИНГ`.

## 6. Наши соглашения (специфика)

1. **Email — в двух местах:** `counterparty.email` (34.9%) И `contactpersons[].email`. Собирать **оба**. Общий охват — **63.1% (1699 контрагентов)**.
2. **Менеджер — `owner`** (99.9% заполнен). Теги-фамилии **дублируют**, но не всегда. Использовать `owner` как первичный.
3. **Категория — теги** (`глазури`, `кондитерка`, `напитки`).
4. **Роль — теги** (`покупатель`, `поставщик`, `перевозчик`).
5. **Источник лида — теги** (`продэкспо`, `С ВЫСТАВКИ` в статусах).
6. **ХОЛДИНГ — кастомное поле**, текстовое, для группировки.
7. **Воронка контрагентов — через теги.** `status` и `state` не используются (0%).
8. **Товары — архивные продаются.** Проверять `archived`.
9. **Контактные лица** — только `expand=contactpersons`, работает до `limit=100`.
10. **Планы заказов** — статус `ПЛАНЫ` (35 заказов, 0.42 млрд). **Исключать из реальных продаж.**
11. **Заказы почти все ОТГРУЖЕН** (96.6%). Система — документооборот, не CRM.
12. **`counterparty.id` возвращается**, если явно указать в `fields`. Связка заказов с контрагентом — **по `agent.id`**.

## 7. Рабочие сценарии

### 7.1. Аналитика продаж

1. Заказы: GET /entity/customerorder?expand=agent,positions.assortment&limit=100

2. Исключить status=ПЛАНЫ

3. Сумма = sum / 100 (копейки → рубли)

4. Группировать по agent, agent.tags, ХОЛДИНГ, периоду


### 7.2. Создание нового клиента

Обязательные поля:
- `name` (краткое)
- `companyType` (legal / entrepreneur / individual)

Для юрлица:
- `legalTitle`, `inn`, `kpp`, `ogrn`, `legalAddress`, `actualAddress`

Для ИП:
- `legalFirstName`, `legalLastName`, `legalMiddleName`, `ogrnip`

Для рассылки:
- `email` (у контрагента)
- или добавить контактное лицо с email

Сегментация:
- `tags`: категория (глазури / кондитерка) + менеджер
- `owner`: ответственный сотрудник
- `ХОЛДИНГ`: если часть группы

### 7.3. База email для рассылки

**Файлы:**
- `/mnt/ai-ssd/hermes/cache/moysklad-audit/email_base.txt` — 2369 email (по одному на строку).
- `/mnt/ai-ssd/hermes/cache/moysklad-audit/email_base.json` — 1699 контрагентов с email, тегами, owner.

**Логика:**
- Собрать `counterparty.email` + все `contactpersons[].email`.
- Дедуплицировать.
- Опционально: фильтровать по тегам (только `покупатель`, только определённые категории).

### 7.4. Матчинг email-корреспондента с контрагентом

Приоритеты:
1. **Точный `email`** (наибольшая уверенность).
2. **Домен email** (`@company.ru` → контрагент с `email` на том же домене).
3. **ИНН** (если найден в письмах — 74.1% контрагентов имеют ИНН).
4. **Название** (нормализация: убрать ООО/ИП, регистр).
5. **Контактное лицо** (имя из письма ↔ `contactpersons[].name`).

### 7.5. Топ клиентов по холдингу

```python
# Группировка продаж по ХОЛДИНГ
holdings = {}
for order in orders:
    if "ПЛАН" in order["state"]:
        continue
    cp_id = order["agent"]["id"]
    holding = cp_by_id[cp_id].get("ХОЛДИНГ", cp_by_id[cp_id]["name"])
    holdings[holding] = holdings.get(holding, 0) + order["sum"]
```

## 8. Ограничения и подводные камни

1. **MCP `get_resources`** — не более 1000 объектов, без пагинации.
2. **MCP `fields` обязателен** — без него пустой массив.
3. **`expand` только до `limit=100`** — на 200+ молча отключается.
4. **API требует `Accept-Encoding: gzip`** — иначе HTTP 415.
5. **API требует `Accept: application/json;charset=utf-8`.**
6. **`state` и `status` у контрагентов не используются.**
7. **MCP-схема неполная:** нет `owner`, `group`, `contactpersons`, `ogrnip`, `accounts`, `files`, `state`, `actualAddressFull`, `legalFirstName/LastName/MiddleName`.
8. **403 Forbidden** на: `saleschannel`, `retailstore`, `purchaseorder`, `enter`, `loss`, `move`, `inventory`, `internalorder`, `invoicein`, `prepayment`, `purchasereturn`, `retaildemand`.
9. **`contract` статусы** — 3 штуки, используются.
10. **`customerorder` статусы** — 17 определены, 9 используются, 96.6% — ОТГРУЖЕН.

## 9. Файлы аудита (2026-10-09)

Путь: `/mnt/ai-ssd/hermes/cache/moysklad-audit/`

| Файл | Что | Размер |
|---|---|---|
| `counterparty_full.json` | 2694 контрагента со всеми полями | 17 MB |
| `customerorder_v2.json` | 1851 заказ с позициями | 60 MB |
| `order_positions_final.json` | 13856 позиций (обогащённые) | 7.3 MB |
| `full_demand.json` | 1283 отгрузки | 148 MB |
| `full_invoiceout.json` | 1338 счетов | 169 MB |
| `full_paymentin.json` | 1490 платежей | 29 MB |
| `full_product.json` | 420 активных товаров | 5.4 MB |
| `all_items_map.json` | 764 товара (включая архивные) | 213 KB |
| `email_base.json` | 1699 контрагентов с email | 523 KB |
| `email_base.txt` | 2369 уникальных email | — |
| `full_*.json` | 28 ресурсов (contract, organization, store, ...) | — |

## 10. Ссылки

- **API МойСклад:** https://dev.moysklad.ru/doc/api/remap/1.2/
- **UI:** https://online.moysklad.ru/app/
- **MCP-сервер:** https://mcp.moysklad.ru/tools/main
- **MCP tools (4):** `get_catalog`, `get_schema`, `get_resources`, `get_child_resources`
- **Аудит-файлы:** `/mnt/ai-ssd/hermes/cache/moysklad-audit/`

## 11. MCP-сервер МойСклад

### Характеристики

- **URL:** `https://mcp.moysklad.ru/tools/main`
- **Версия:** `moysklad-mcp 1.29.0`
- **Transport:** HTTP (JSON-RPC over POST)
- **ProtocolVersion:** `2024-11-05`
- **Зависимости:** нулевые (облако)
- **Токен:** `MOYSKLAD_TOKEN` в `/mnt/ai-ssd/hermes/.env`
- **Headers:** `Authorization: Bearer ${MOYSKLAD_TOKEN}`

### 4 инструмента (read-only by construction)

| Tool | Что делает |
|---|---|
| `get_catalog` | Каталог ресурсов: справочники (dictionary), документы (document), отчёты (report) |
| `get_schema` | Схема resource: fields, parameters, child_key, filter_operator_groups |
| `get_resources` | Список объектов с реальными данными (**требует `fields`!**) |
| `get_child_resources` | Дочерние объекты для конкретного родителя (требует `entityId` + `child_key`) |

**Write-инструментов в MCP нет.** Только `get_*`. Безопасность by construction.

**Важно:** MCP — read-only, **но прямой HTTP API МойСклад — работает** (используется для аудита). Заголовки: `Authorization: Bearer $MOYSKLAD_TOKEN`, `Accept: application/json;charset=utf-8`, `Accept-Encoding: gzip`.

### Порядок работы (MCP)

1. `get_catalog` — выбрать ресурс.
2. `get_schema` — узнать поля.
3. `get_resources` — запросить данные (с `fields`!).
4. `get_child_resources` — дочерние (например, позиции заказа).

### Конфигурация Hermes

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
### Создание токена
1. Веб-интерфейс МойСклад: Настройки → Пользователи → Токены доступа.
2. Создать → скопировать (показывается один раз).
3. Вставить в /mnt/ai-ssd/hermes/.env: MOYSKLAD_TOKEN=<токен>.
4. Права токена: просмотр (без редактирования/удаления).

### Сравнение с ilyautov/moysklad-mcp-ru
| Критерий | Официальный | ilyautov |
|---|---|---|
| Unicode-баг | нет | есть |
| Версия | 1.29.0 | 0.2.0 alpha |
| Transport | HTTP (облако) | stdio (локально) |
| Зависимости | 0 | uvx + Python |
| Write | нет | есть (за гейтами) |
| Токен | `.env` | `cabinets.json` |
Вывод: используем официальный MCP — нет Unicode-бага, без локальных зависимостей.

### Проверено
- 2026-10-05: hermes chat -q "Покажи список товаров" → 14 tool calls, 50 сек, реальные данные (112+ товаров).
- 2026-10-09: полный аудит через HTTP API — 2694 контрагента, 1851 заказ, 764 товара.

## 12. Полный каталог ресурсов (81)

Из официального MCP (`get_catalog`, 2026-10-09).

### Общая структура

- **31 dictionary** — справочники
- **37 document** — документы
- **13 report** — отчёты

### Ключевые справочники (dictionary)

| key | Что | Связка |
|---|---|---|
| `counterparty` | Клиенты и поставщики | email → почта, id → заказы |
| `organization` | Свои юрлица | |
| `product` | Номенклатура | |
| `service` | Услуги | |
| `variant` | Модификации | |
| `bundle` | Комплекты | |
| `productfolder` | Группы товаров | |
| `store` | Склады | |
| `retailstore` | Точки продаж | |
| `employee` | Сотрудники | owner контрагента |
| `group` | Отделы | group контрагента |
| `contract` | Договоры | agent → counterparty |
| `project` | Проекты | |
| `saleschannel` | Каналы продаж | |
| `saleplatform` | Площадки продаж | маркетплейсы |
| `currency` | Валюты | |
| `uom` | Единицы измерения | |
| `taxrate` | Ставки НДС | |
| `expenseitem` | Статьи расходов | |
| `country` | Страны | |
| `region` | Регионы | |
| `discount` | Скидки | |
| `bonusprogram` | Бонусные программы | |
| `consignment` | Серии | партии товаров |
| `task` | Задачи CRM | |

### Ключевые документы (document)

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
| `invoiceout` | Счёт покупателю | invoiceout_position |
| `invoicein` | Счёт поставщика | invoicein_position |
| `purchaseorder` | Заказ поставщику | purchaseorder_position |
| `paymentin` | Входящий платёж | — |
| `paymentout` | Исходящий платёж | — |
| `cashin` | Приходный ордер | — |
| `cashout` | Расходный ордер | — |
| `pricelist` | Прайс-лист | pricelist_position |
| `prepayment` | Предоплата | prepayment_position |
| `retaildemand` | Розничная продажа | retaildemand_position |

### Ключевые отчёты (report)

| key | Что |
|---|---|
| `report_counterparty_metrics` | Метрики клиентов (CRM) |
| `report_orders` | Показатели заказов |
| `report_sales` | Показатели продаж |
| `profit_bycounterparty` | Прибыль по клиентам |
| `profit_byproduct` | Прибыльность по товарам |
| `profit_byvariant` | Прибыльность по модификациям |
| `profit_byemployee` | Прибыльность по сотрудникам |
| `profit_bysaleschannel` | Прибыльность по каналам |
| `stock_all` | Остатки по товарам (подробный) |
| `stock_bystore` | Остатки по складам |
| `stock_all_current` | Остатки (краткий) |
| `stock_bystore_current` | Остатки по складам (краткий) |
| `assortment` | Ассортимент |

### Устаревшее / неверное в старых документах

- ❌ `pricetype` — **нет** в реальном каталоге МойСклад (2026-10-09).
- ❌ «НЕТ в схеме customerorder: state» — **неверно**, `state` **есть** (17 статусов).
- ❌ «customerorder.agent — Ref(counterparty, organization)» — только **counterparty**.
- ❌ `company_summary.json` (204 компании) — устарело (сейчас 356 доменов, 2309 писем).
