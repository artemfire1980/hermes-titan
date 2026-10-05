---
name: moysklad-workflow
query: "МойСклад"
description: Полный справочник полей МойСклад, их назначение и взаимосвязи — для построения корректных запросов через MCP-инструменты.
version: 1.0.0
author: hermes
license: MIT
---

# Moysklad Workflow — Справочник полей и взаимосвязей

## Путь работы с данными

1. `get_catalog()` — список всех resource (dictionary / document / report)
2. `get_schema(key=<resource>)` — поля, типы, фильтры, child_key
3. `get_resources(key=<key>, fields=[...], filters=[...])` — данные
4. `get_child_resources(key=<parent>, entityId=<id>, child_key=<ck>, fields=[...])` — позиции документа

## Каталог resources

### Справочники (dictionary)
| key | label | назначение |
|-----|-------|------------|
| counterparty | Контрагент | Клиенты и поставщики |
| organization | Юрлицо | Собственные юрлица компании |
| product | Товар | Номенклатура товаров |
| service | Услуга | Услуги (без закупочной цены) |
| variant | Модификация | Варианты товара |
| bundle | Комплект | Наборы товаров |
| productfolder | Группа товаров | Каталог товаров |
| store | Склад | Склады и группы |
| retailstore | Точка продаж | Точки розницы |
| employee | Сотрудник | Сотрудники |
| group | Отдел | Группы сотрудников |
| contract | Договор | Договоры с контрагентами |
| pricetype | Тип цен | Типы цен номенклатуры |
| currency | Валюта | Валюты |
| uom | Единица измерения | Ед. изм. |
| taxrate | Ставка НДС | Ставки НДС |
| expenseitem | Статья расходов | Статьи расходов |
| project | Проект | Проекты |
| saleschannel | Канал продаж | Каналы продаж |
| saleplatform | Площадка продаж | Маркетплейсы |
| country | Страна | Справочник стран |
| region | Регион | Справочник регионов |
| consignment | Серия | Партии товаров |
| thing | Серийный номер | Серийные номера |
| bonusprogram | Бонусная программа | |
| bonustransaction | Бонусная операция | Начисления/списания |
| customentity | Пользовательский справочник | |
| processingplan | Техкарта | Рецептуры |
| processingplanfolder | Группа техкарт | |
| processingprocess | Техпроцесс | |
| processingstage | Этап производства | |
| discount | Скидка | |
| cashier | Кассир | Привязка сотрудника к точке продаж |

### Документы (document) — ключевые
| key | label | child_key | назначение |
|-----|-------|-----------|------------|
| customerorder | Заказ покупателя | customerorder_position | Заказ клиента |
| demand | Отгрузка | demandposition | Отгрузка товаров |
| supply | Приёмка | supply_position | Приёмка от поставщика |
| enter | Оприходование | enter_position | Оприходование на склад |
| move | Перемещение | move_position | Перемещение между складами |
| inventory | Инвентаризация | inventory_position | Инвентаризация |
| salesreturn | Возврат покупателя | salesreturn_position | Возврат от клиента |
| purchasereturn | Возврат поставщику | purchasereturn_position | Возврат поставщику |
| cashin | Приходный ордер | — | Приходный ордер |
| cashout | Расходный ордер | — | Расходный ордер |
| paymentin | Входящий платёж | — | Оплата от контрагента |
| paymentout | Исходящий платёж | — | Оплата контрагенту |
| invoicein | Счёт поставщика | invoicein_position | Счёт от поставщика |
| invoiceout | Счёт покупателю | invoiceout_position | Счёт клиенту |
| facturein | Счёт-фактура полученный | — | |
| factureout | Счёт-фактура выданный | — | |
| purchaseorder | Заказ поставщику | purchaseorder_position | |
| processingorder | Заказ на производство | processingorder_position | |
| processing | Техоперация | processing_position | |
| internalorder | Внутренний заказ | internalorder_position | |
| prepayment | Предоплата | prepayment_position | |
| prepaymentreturn | Возврат предоплаты | prepaymentreturn_position | |
| pricelist | Прайс-лист | pricelist_position | |
| retaildemand | Розничная продажа | retaildemand_position | |
| retailsalesreturn | Розничный возврат | retailsalesreturn_position | |
| retailshift | Розничная смена | — | |
| retireorder | Вывод из оборота | retireorder_position | |
| emissionorder | Заказ кодов маркировки | emissionorder_position | |
| commissionreportin | Полученный отчёт комиссионера | commissionreportin_position | |
| commissionreportout | Выданный отчёт комиссионера | commissionreportout_position | |
| counterpartyadjustment | Корректировка взаиморасчётов | — | |
| loss | Списание | loss_position | |
| productiontask | Производственное задание | productiontask_position | |
| productionstagecompletion | Выполнение этапа | productionstagecompletion_position | |
| payroll | Начисление зарплаты | — | |
| retaildrawercashin | Внесение в кассу | — | |
| retaildrawercashout | Выплата из кассы | — | |

### Отчёты (report)
| key | label | назначение |
|-----|-------|------------|
| stock_all | Остатки по товарам (подробный) | |
| stock_bystore | Остатки по складам | |
| stock_all_current | Остатки (краткий) | |
| stock_bystore_current | Остатки по складам (краткий) | |
| turnover | Обороты товаров | |
| assortment | Ассортимент | |
| sales | Показатели продаж | |
| orders | Показатели заказов | |
| profit_byproduct | Прибыльность по товарам | |
| profit_byvariant | Прибыльность по модификациям | |
| profit_byemployee | Прибыльность по сотрудникам | |
| profit_bycounterparty | Прибыльность по покупателям | |
| profit_bysaleschannel | Прибыльность по каналам | |
| money | Движение денежных средств | |
| dashboard | Показатели | |
| counterpartymetrics | Показатели контрагентов | |
| byoperations | По документам номенклатуры | |

---

## Схемы полей (fields) по resource

### counterparty (Контрагент)
| field | label | type | filterable | назначение |
|-------|-------|------|-----------|------------|
| name | Наименование | String | text | Юрлицо/ИП/ФИО |
| code | Код | String | text | Внутренний код |
| externalCode | Внешний код | String | text | Внешняя интеграция |
| legalTitle | Полное наименование | String | text | Полное название |
| companyType | Тип контрагента | Enum | eq_neq | legal/entrepreneur/individual |
| inn | ИНН | String | text | ИНН |
| kpp | КПП | String | text | КПП |
| email | Email | String | text | |
| phone | Телефон | String | text | |
| fax | Факс | String | text | |
| actualAddress | Фактический адрес | String | text | |
| legalAddress | Юридический адрес | String | text | |
| discountCardNumber | Номер дисконтной карты | String | text | |
| description | Комментарий | String | text | |
| tags | Группы контрагента | Array(String) | text | |
| archived | В архиве | Boolean | eq_neq | |
| salesAmount | Сумма продаж | Int | нет | Только чтение |
| bonusPoints | Бонусные баллы | Int | нет | Только чтение |
| created | Момент создания | DateTime | date | |
| updated | Момент обновления | DateTime | date | |
| id | ID | UUID | eq_neq | |

### organization (Юрлицо)
| field | label | type | filterable | назначение |
|-------|-------|------|-----------|------------|
| name | Наименование | String | text | |
| code | Код | String | text | |
| externalCode | Внешний код | String | text | |
| companyType | Тип юрлица | Enum | eq_neq | legal/entrepreneur/individual |
| inn | ИНН | String | text | |
| kpp | КПП | String | text | |
| email | Email | String | text | |
| fax | Факс | String | text | |
| actualAddress | Фактический адрес | String | text | |
| description | Комментарий | String | text | |
| archived | В архиве | Boolean | eq_neq | |
| created | Дата создания | DateTime | date | |
| updated | Момент обновления | DateTime | date | |
| id | ID | UUID | eq_neq | |

### product (Товар)
| field | label | type | filterable | назначение |
|-------|-------|------|-----------|------------|
| name | Наименование | String | text | |
| code | Код | String | text | |
| article | Артикул | String | text | |
| externalCode | Внешний код | String | text | |
| barcode | Штрихкод | String | text | В ответе — массив barcodes |
| description | Описание | String | text | |
| pathName | Группа товара (путь) | String | text | Только чтение |
| productFolder | Группа товара | Ref(productfolder) | нет | |
| supplier | Поставщик | Ref(counterparty) | eq_neq | |
| uom | Единица измерения | Ref(uom) | нет | |
| country | Страна | Ref(country) | нет | |
| minimumBalance | Неснижаемый остаток | Float | date | |
| weight | Вес | Float | date | |
| volume | Объём | Float | date | |
| vat | НДС, % | Int | нет | |
| archived | В архиве | Boolean | eq_neq | |
| isSerialTrackable | Учёт по серийным номерам | Boolean | eq_neq | |
| variantsCount | Кол-во модификаций | Int | нет | Только чтение |
| updated | Момент обновления | DateTime | date | |
| id | ID | UUID | eq_neq | |

### store (Склад)
| field | label | type | filterable | назначение |
|-------|-------|------|-----------|------------|
| name | Наименование | String | text | |
| code | Код | String | text | |
| externalCode | Внешний код | String | text | |
| address | Адрес | String | text | |
| pathName | Группа склада | String | text | |
| parent | Родительский склад | Ref(store) | eq_neq | |
| description | Комментарий | String | text | |
| archived | В архиве | Boolean | eq_neq | |
| updated | Момент обновления | DateTime | date | |
| id | ID | UUID | eq_neq | |

### variant (Модификация)
| field | label | type | filterable | назначение |
|-------|-------|------|-----------|------------|
| name | Наименование товара с модификацией | String | text | |
| code | Код | String | text | |
| externalCode | Внешний код | String | text | |
| barcode | Штрихкод | String | text | |
| productid | ID товара-родителя | UUID | eq_neq | Фильтр модификаций по товару |
| description | Описание | String | text | |
| archived | В архиве | Boolean | eq_neq | |
| id | ID | UUID | eq_neq | |

### customerorder (Заказ покупателя)
| field | label | type | filterable | назначение |
|-------|-------|------|-----------|------------|
| name | Номер/наименование | String | text | |
| code | Код | String | text | |
| externalCode | Внешний код | String | text | |
| moment | Дата документа | DateTime | date | |
| description | Комментарий | String | text | |
| deliveryPlannedMoment | План. дата отгрузки | DateTime | date | |
| sum | Сумма | Float | date | Только чтение, копейки |
| applicable | Проведён | Boolean | eq_neq | |
| agent | Контрагент | Ref(counterparty, organization) | eq_neq | |
| organization | Юрлицо | Ref(organization) | eq_neq | |
| store | Склад | Ref(store) | eq_neq | |
| contract | Договор | Ref(contract) | eq_neq | |
| project | Проект | Ref(project) | eq_neq | |
| salesChannel | Канал продаж | Ref(saleschannel) | eq_neq | |
| shipmentAddress | Адрес доставки | String | text | |
| printed | Напечатан | Boolean | eq_neq | |
| published | Опубликован | Boolean | eq_neq | |
| created | Дата создания | DateTime | date | |
| updated | Момент обновления | DateTime | date | |
| id | ID | UUID | eq_neq | |
child_key: customerorder_position

### demand (Отгрузка)
| field | label | type | filterable | назначение |
|-------|-------|------|-----------|------------|
| name | Номер/наименование | String | text | |
| code | Код | String | text | |
| externalCode | Внешний код | String | text | |
| moment | Дата документа | DateTime | date | |
| description | Комментарий | String | text | |
| sum | Сумма | Float | date | Копейки, только чтение |
| applicable | Проведён | Boolean | eq_neq | |
| agent | Контрагент | Ref(counterparty, organization) | eq_neq | |
| organization | Юрлицо | Ref(organization) | eq_neq | |
| store | Склад | Ref(store) | eq_neq | |
| contract | Договор | Ref(contract) | eq_neq | |
| project | Проект | Ref(project) | eq_neq | |
| salesChannel | Канал продаж | Ref(saleschannel) | eq_neq | |
| shipmentAddress | Адрес доставки | String | text | |
| printed | Напечатан | Boolean | eq_neq | |
| published | Опубликован | Boolean | eq_neq | |
| created | Дата создания | DateTime | date | |
| updated | Момент обновления | DateTime | date | |
| id | ID | UUID | eq_neq | |
child_key: demandposition

### supply (Приёмка)
| field | label | type | filterable | назначение |
|-------|-------|------|-----------|------------|
| name | Номер/наименование | String | text | |
| code | Код | String | text | |
| externalCode | Внешний код | String | text | |
| moment | Дата документа | DateTime | date | |
| description | Комментарий | String | text | |
| incomingNumber | Входящий номер | String | text | |
| incomingDate | Входящая дата | DateTime | date | |
| sum | Сумма | Float | date | Копейки, только чтение |
| applicable | Проведён | Boolean | eq_neq | |
| agent | Контрагент (поставщик) | Ref(counterparty, organization) | eq_neq | |
| organization | Юрлицо | Ref(organization) | eq_neq | |
| store | Склад | Ref(store) | eq_neq | |
| contract | Договор | Ref(contract) | eq_neq | |
| project | Проект | Ref(project) | eq_neq | |
| printed | Напечатан | Boolean | eq_neq | |
| published | Опубликован | Boolean | eq_neq | |
| created | Дата создания | DateTime | date | |
| updated | Момент обновления | DateTime | date | |
| id | ID | UUID | eq_neq | |
child_key: supply_position

### enter (Оприходование)
| field | label | type | filterable | назначение |
|-------|-------|------|-----------|------------|
| name | Номер/наименование | String | text | |
| code | Код | String | text | |
| externalCode | Внешний код | String | text | |
| moment | Дата документа | DateTime | date | |
| description | Комментарий | String | text | |
| sum | Сумма | Float | date | Копейки |
| applicable | Проведён | Boolean | eq_neq | |
| agent | Контрагент | Ref(counterparty, organization) | eq_neq | |
| organization | Юрлицо | Ref(organization) | eq_neq | |
| store | Склад | Ref(store) | eq_neq | |
| contract | Договор | Ref(contract) | eq_neq | |
| project | Проект | Ref(project) | eq_neq | |
| salesChannel | Канал продаж | Ref(saleschannel) | eq_neq | |
| printed | Напечатан | Boolean | eq_neq | |
| published | Опубликован | Boolean | eq_neq | |
| created | Дата создания | DateTime | date | |
| updated | Момент обновления | DateTime | date | |
| id | ID | UUID | eq_neq | |
child_key: enter_position

### retaildemand (Розничная продажа)
| field | label | type | filterable | назначение |
|-------|-------|------|-----------|------------|
| name | Номер/наименование | String | text | |
| code | Код | String | text | |
| externalCode | Внешний код | String | text | |
| moment | Дата документа | DateTime | date | |
| description | Комментарий | String | text | |
| sum | Сумма | Float | number | Копейки |
| applicable | Проведён | Boolean | eq_neq | |
| agent | Контрагент | Ref(counterparty, organization) | eq_neq | |
| organization | Юрлицо | Ref(organization) | eq_neq | |
| store | Склад | Ref(store) | eq_neq | |
| retailStore | Точка продаж | Ref(retailstore) | eq_neq | |
| retailShift | Розничная смена | Ref(retailshift) | eq_neq | |
| project | Проект | Ref(project) | eq_neq | |
| printed | Напечатан | Boolean | eq_neq | |
| published | Опубликован | Boolean | eq_neq | |
| created | Дата создания | DateTime | date | |
| updated | Момент обновления | DateTime | date | |
| id | ID | UUID | eq_neq | |
child_key: retaildemand_position

### paymentin (Входящий платёж)
| field | label | type | filterable | назначение |
|-------|-------|------|-----------|------------|
| name | Номер/наименование | String | text | |
| code | Код | String | text | |
| externalCode | Внешний код | String | text | |
| moment | Дата документа | DateTime | date | |
| description | Комментарий | String | text | |
| paymentPurpose | Назначение платежа | String | text | |
| incomingNumber | Входящий номер | String | text | |
| incomingDate | Входящая дата | DateTime | date | |
| sum | Сумма | Float | date | |
| applicable | Проведён | Boolean | eq_neq | |
| agent | Контрагент | Ref(counterparty, organization) | eq_neq | |
| organization | Юрлицо | Ref(organization) | eq_neq | |
| contract | Договор | Ref(contract) | eq_neq | |
| project | Проект | Ref(project) | eq_neq | |
| salesChannel | Канал продаж | Ref(saleschannel) | eq_neq | |
| printed | Напечатан | Boolean | eq_neq | |
| published | Опубликован | Boolean | eq_neq | |
| created | Дата создания | DateTime | date | |
| updated | Момент обновления | DateTime | date | |
| id | ID | UUID | eq_neq | |

### paymentout (Исходящий платёж)
| field | label | type | filterable | назначение |
|-------|-------|------|-----------|------------|
| name | Номер/наименование | String | text | |
| code | Код | String | text | |
| externalCode | Внешний код | String | text | |
| moment | Дата документа | DateTime | date | |
| description | Комментарий | String | text | |
| paymentPurpose | Назначение платежа | String | text | |
| sum | Сумма | Float | date | |
| applicable | Проведён | Boolean | eq_neq | |
| agent | Контрагент/сотрудник | Ref(counterparty, employee, org) | eq_neq | |
| organization | Юрлицо | Ref(organization) | eq_neq | |
| expenseItem | Статья расходов | Ref(expenseitem) | нет | |
| contract | Договор | Ref(contract) | eq_neq | |
| project | Проект | Ref(project) | eq_neq | |
| salesChannel | Канал продаж | Ref(saleschannel) | eq_neq | |
| printed | Напечатан | Boolean | eq_neq | |
| published | Опубликован | Boolean | eq_neq | |
| created | Дата создания | DateTime | date | |
| updated | Момент обновления | DateTime | date | |
| id | ID | UUID | eq_neq | |

### cashin / cashout (Приходный/Расходный ордер)
| field | label | type | filterable | назначение |
|-------|-------|------|-----------|------------|
| name | Номер/наименование | String | text | |
| code | Код | String | text | |
| externalCode | Внешний код | String | text | |
| moment | Дата документа | DateTime | date | |
| description | Комментарий | String | text | |
| paymentPurpose | Основание | String | text | |
| sum | Сумма | Float | number | Копейки |
| applicable | Проведён | Boolean | eq_neq | |
| agent | Контрагент | Ref(counterparty, organization) | eq_neq | |
| organization | Юрлицо | Ref(organization) | eq_neq | |
| store | Склад | Ref(store) | eq_neq | |
| contract | Договор | Ref(contract) | eq_neq | |
| project | Проект | Ref(project) | eq_neq | |
| salesChannel | Канал продаж | Ref(saleschannel) | eq_neq | |
| printed | Напечатан | Boolean | eq_neq | |
| published | Опубликован | Boolean | eq_neq | |
| created | Дата создания | DateTime | date | |
| updated | Момент обновления | DateTime | date | |
| id | ID | UUID | eq_neq | |

### employee (Сотрудник)
| field | label | type | filterable | назначение |
|-------|-------|------|-----------|------------|
| name | Наименование (ФИО) | String | text | Только чтение |
| firstName | Имя | String | text | |
| middleName | Отчество | String | text | |
| lastName | Фамилия | String | text | |
| fullName | Имя Отчество Фамилия | String | text | Только чтение |
| shortFio | Краткое ФИО | String | text | Только чтение |
| code | Код | String | text | |
| externalCode | Внешний код | String | text | |
| email | Email | String | text | |
| phone | Телефон | String | text | |
| position | Должность | String | text | |
| inn | ИНН | String | text | |
| uid | Логин | String | text | Только чтение |
| description | Комментарий | String | text | |
| archived | В архиве | Boolean | eq_neq | |
| created | Момент создания | DateTime | text | |
| updated | Момент обновления | DateTime | date | |
| id | ID | UUID | eq_neq | |

### contract (Договор)
| field | label | type | filterable | назначение |
|-------|-------|------|-----------|------------|
| name | Номер договора | String | text | |
| code | Код | String | text | |
| externalCode | Внешний код | String | text | |
| contractType | Тип договора | Enum | нет | Договор комиссии / купли-продажи |
| description | Описание | String | text | |
| moment | Дата договора | DateTime | date | |
| agent | Контрагент | Ref(counterparty) | eq_neq | |
| ownAgent | Своё юрлицо | Ref(organization) | eq_neq | |
| archived | В архиве | Boolean | eq_neq | |
| updated | Момент обновления | DateTime | date | |
| id | ID | UUID | eq_neq | |

### saleschannel (Канал продаж)
| field | label | type | filterable | назначение |
|-------|-------|------|-----------|------------|
| name | Наименование | String | text | |
| code | Код | String | text | |
| externalCode | Внешний код | String | text | |
| description | Описание | String | text | |
| type | Тип канала | Enum | eq_neq | MESSENGER/SOCIAL_NETWORK/MARKETPLACE/ECOMMERCE/CLASSIFIED_ADS/DIRECT_SALES/RETAIL_SALES/OTHER |
| archived | В архиве | Boolean | eq_neq | |
| updated | Момент обновления | DateTime | date | |
| id | ID | UUID | eq_neq | |

### pricetype (Тип цен)
| field | label | type | filterable | назначение |
|-------|-------|------|-----------|------------|
| name | Наименование | String | text | |
| externalCode | Внешний код | String | text | |
| id | ID | UUID | eq_neq | |

### currency (Валюта)
| field | label | type | filterable | назначение |
|-------|-------|------|-----------|------------|
| name | Краткое наименование | String | text | |
| fullName | Полное наименование | String | text | |
| code | Цифровой код | String | text | |
| isoCode | Буквенный код ISO | String | text | |
| default | Валюта учёта | Boolean | eq_neq | Только чтение |
| archived | В архиве | Boolean | eq_neq | |
| multiplicity | Кратность курса | Int | date | |
| id | ID | UUID | eq_neq | |

### uom (Единица измерения)
| field | label | type | filterable | назначение |
|-------|-------|------|-----------|------------|
| name | Краткое наименование | String | text | |
| description | Полное наименование | String | text | |
| code | Код | String | text | |
| externalCode | Внешний код | String | text | |
| updated | Момент обновления | DateTime | date | |
| id | ID | UUID | eq_neq | |

### taxrate (Ставка НДС)
| field | label | type | filterable | назначение |
|-------|-------|------|-----------|------------|
| rate | Ставка, % | Float | нет | |
| comment | Комментарий | String | text | |
| archived | В архиве | Boolean | eq_neq | |
| id | ID | UUID | eq_neq | |

### expenseitem (Статья расходов)
| field | label | type | filterable | назначение |
|-------|-------|------|-----------|------------|
| name | Наименование | String | text | |
| code | Код | String | text | |
| externalCode | Внешний код | String | text | |
| description | Описание | String | text | |
| archived | В архиве | Boolean | eq_neq | |
| id | ID | UUID | eq_neq | |

### group (Отдел)
| field | label | type | filterable | назначение |
|-------|-------|------|-----------|------------|
| name | Наименование | String | text | |
| code | Код | String | text | |
| externalCode | Внешний код | String | text | |
| description | Описание | String | text | |
| archived | В архиве | Boolean | eq_neq | |
| id | ID | UUID | eq_neq | |

### project (Проект)
| field | label | type | filterable | назначение |
|-------|-------|------|-----------|------------|
| name | Наименование | String | text | |
| code | Код | String | text | |
| externalCode | Внешний код | String | text | |
| description | Описание | String | text | |
| archived | В архиве | Boolean | eq_neq | |
| id | ID | UUID | eq_neq | |

---

## Взаимосвязи между ресурсами

```
organization (юрлицо компании)
  ├── ownAgent в contract (своё юрлицо в договоре)
  └── organization в customerorder, demand, supply, enter, paymentin/out, cashin/out

counterparty (контрагент)
  ├── supplier → product (поставщик товара)
  ├── agent в customerorder (клиент)
  ├── agent в demand (покупатель)
  ├── agent в supply (поставщик)
  ├── agent в paymentin/out, cashin/out
  ├── agent в contract (контрагент договора)
  └── contract → ownAgent: organization (контрагент + своё юрлицо = договор)

store (склад)
  ├── store в customerorder, demand, supply, enter, cashin/out, paymentin/out
  ├── parent → store (группа складов)
  └── retailStore в retaildemand

product (товар)
  ├── productFolder → productfolder (группа товара)
  ├── supplier → counterparty
  ├── uom → uom
  ├── country → country
  ├── vat → taxrate (ставка)
  ├── variant → product (productid)
  └── входит в позиции: customerorder_position, demandposition, supply_position, enter_position

variant (модификация)
  └── productid → product (привязка к товару)

customerorder → demand → supply/enter (цепочка документов)
  customerorder_position → assortment → product/variant/service/bundle/consignment
  demand → demandposition → assortment
  supply → supply_position → assortment

customerorder → paymentout (оплата по заказу)
demand → paymentout (оплата отгрузки)

saleschannel → customerorder, demand, paymentin/out, cashin/out, retaildemand
contract → customerorder, demand, supply, enter, paymentin/out, cashin/out
project → customerorder, demand, supply, enter, paymentin/out, cashin/out, retaildemand
pricetype → product/variant (тип цены номенклатуры)
retailstore → retaildemand
retailshift → retaildemand
employee → paymentout (agent), retailshift, cashier
expenseitem → paymentout (статья расходов)
```

## Цепочки документов

```
customerorder (заказ)
  └─> demand (отгрузка) — по positions из customerorder
       └─> supply (приёмка у поставщика) или enter (оприходование)

purchaseorder (заказ поставщику)
  └─> supply (приёмка) — по positions из purchaseorder

supply (приёмка)
  └─> enter_position (схождение) — оприходование на склад

retaildemand (розничная продажа)
  └─> retailshift (розничная смена) — привязка к смене ККМ
```

## Фильтры: операторы

| Оператор | Значение |
|----------|----------|
| = | равно |
| != | не равно |
| ~ | содержит |
| ~= | начинается с |
| =~ | заканчивается на |
| <, >, <=, >= | сравнение (числа, даты) |

Только поля с `filter_operator_group` поддерживают фильтрацию.

## Позиции документов (child resources)

| parent | child_key | fields |
|--------|-----------|--------|
| customerorder | customerorder_position | assortment, quantity, price, discount, vat, vatEnabled, reserve, shipped |
| demand | demandposition | assortment, quantity, price, discount, vat, vatEnabled |
| supply | supply_position | assortment, quantity, price, discount, vat, vatEnabled |
| enter | enter_position | assortment, quantity, price, discount, vat, vatEnabled |
| purchaseorder | purchaseorder_position | assortment, quantity, price, discount, vat |
| retaildemand | retaildemand_position | assortment, quantity, price, discount, vat |
| retailsalesreturn | retailsalesreturn_position | assortment, quantity, price, discount, vat |
| salesreturn | salesreturn_position | assortment, quantity, price, discount, vat |
| purchasereturn | purchasereturn_position | assortment, quantity, price, discount, vat |
| inventory | inventory_position | assortment, quantity, reason, type |
| move | move_position | assortment, quantity, sourceStore, destinationStore |
| pricelist | pricelist_position | assortment, price, vat |
| prepayment | prepayment_position | assortment, quantity, price |
| prepaymentreturn | prepaymentreturn_position | assortment, quantity, price |

## Важные нюансы

- `sum` в копейках (Float) — во всех документах с позициями
- `price` в копейках — в позициях
- `agent` принимает Ref(counterparty, organization, employee) — в зависимости от документа
- `assortment` в позициях: Ref(product, variant, service, bundle, consignment)
- Дата: формат `YYYY-MM-DD HH:mm:ss` без `T` и без таймзоны
- 1000-объектный лимит на get_resources — нет пагинации; при =1000 результатов общее число больше
- archived=true/false — фильтр для скрытых объектов
- applicable=true — только проведённые документы
