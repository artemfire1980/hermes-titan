---
name: moysklad-query
query: "МойСклад"
description: Query Moysklad via MCP tools with 1000-object limit.
version: 1.0.0
author: hermes
license: MIT
---

# Moysklad Query

Query Moysklad (МойСклад) account data through the `mcp__moysklad__*` MCP tools.

## When to Use

Use when the user asks about Moysklad data: client counts, supplier lists, product catalogs, order statuses, warehouse stock, or any other resource in their Moysklad account. Also use when you need to discover what data is available in a Moysklad account via the MCP interface.

## Workflow

1. **Discover resources** — call `mcp__moysklad__get_catalog()` to see available `dictionary`, `document`, and `report` resources with their keys and labels.

2. **Inspect schema** — call `mcp__moysklad__get_schema(key=<resource_key>)` to see fields, filter operators, and parameters for that resource. This tells you which fields you can request and which support filtering.

3. **Query data** — call `mcp__moysklad__get_resources(key=<key>, fields=[...], filters=[...])`. Use `fields` to limit response size; use `filters` with `field` + `operator` + `value` to narrow results.

## Critical Pitfall: 1000-Object Limit

**The MCP `get_resources` endpoint returns at most 1000 objects per call, with no built-in pagination.** If a query returns exactly 1000 results, the actual count is higher — you cannot get an exact total through this interface alone.

**Workarounds for exact counts:**
- Query with different `companyType` filters (legal / entrepreneur / individual) separately and sum — if each subset is under 1000 you get exact numbers.
- Query archived=true vs archived=false separately.
- Use the `counterpartymetrics` report resource (key: `counterpartymetrics`) for aggregated stats per counterparty — but note it may not support all query parameters.
- For truly large datasets, use the Moysklad API directly with `limit`/`offset` pagination (not available through MCP).

## Filter Operators

From the schema's `filter_operator_group`:

| Operator | Meaning |
|----------|---------|
| `=` | equals |
| `!=` | not equals |
| `~` | contains |
| `~=` | starts with |
| `=~` | ends with |
| `<`, `>`, `<=`, `>=` | comparison (for dates/numbers) |

Only fields with a `filter_operator_group` in their schema entry support filtering. Check the schema before filtering.

## Key Resources

| Resource | Key | What it holds |
|----------|-----|---------------|
| Counterparty | `counterparty` | Clients and suppliers |
| Product | `product` | Products / nomenclature |
| Customer Order | `customerorder` | Customer orders |
| Demand | `demand` | Shipment documents |
| Store | `store` | Warehouses |
| Retail Store | `retailstore` | Points of sale |
| Organization | `organization` | Own legal entities |

## Complete field reference
For the full catalog of all resources, field schemas, and relationship diagrams see skill `moysklad-workflow`.

## Counterparty Fields (commonly used)

| Field | Type | Filterable |
|-------|------|------------|
| `name` | String | yes (text) |
| `companyType` | Enum (legal/entrepreneur/individual) | yes (eq_neq) |
| `archived` | Boolean | yes (eq_neq) |
| `inn` | String | yes (text) |
| `email` | String | yes (text) |
| `phone` | String | yes (text) |
| `id` | UUID | yes (eq_neq) |

## Response Handling

- Large responses are saved to disk as spillover files under `/mnt/ai-ssd/hermes/cache/spillover/`.
- Parse them with Python (not sqlite3 CLI) to count, aggregate, or extract specific fields.
- Always check `len(payload)` against 1000 to detect truncation.
