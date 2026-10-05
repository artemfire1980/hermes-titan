---
name: kiln-printer
query: "Kiln, 3D-принтер, ZAV, статус принтера, мониторинг, камера, температура, printer status, snapshot"
description: Read-only мониторинг 3D-принтера ZAV через Kiln MCP. Статус, температуры, прогресс, снимки камеры, список принтеров. Без управления, без write.
version: 1.0.0
author: hermes
license: MIT
---

# Kiln Printer — read-only мониторинг принтера ZAV

> ⚠️ **Только READ.** Для WRITE/EXECUTE — см. `kiln-safety` + подтверждение Артёма.

## Что такое Kiln MCP

**Kiln** — MCP-сервер для управления 3D-принтерами. **468 инструментов** (46 плагинов):
- **Мониторинг** — статус, температуры, прогресс.
- **Камера** — снимки, stream.
- **Валидация** — проверка моделей.
- **Слайсинг** — STL/3MF → G-code.
- **Печать** — start, cancel, pause.

**У нас активны 71 read-инструмент.**

## Контекст принтера ZAV

| Параметр | Значение |
|----------|----------|
| **Имя** | `zav` |
| **MCU** | BTT Manta M5P + CB1 |
| **Toolhead** | EBB36 CAN |
| **Probe** | BTT Eddy |
| **Build volume** | 295 × 200 × 200 мм |
| **Hotend max** | 300 °C |
| **Bed max** | 130 °C |
| **Камера** | ustreamer, 640×480, `100.92.59.53:8080` |

## Инструменты (read-only)

| Инструмент | Что делает |
|-----------|------------|
| `printer_status` | State, temps, progress |
| `kiln_health` | Версия, uptime |
| `monitor_print` | Полный отчёт + снимок |
| `snapshot` | Снимок камеры |
| `preflight_check` | Проверка перед печатью |
| `validate_model` | Проверка модели |
| `analyze_print_failure_smart` | Анализ сбоя |
| `recommend_design_material` | Материал |
| `estimate_cost` | Стоимость |

## Что нельзя

- `start_print`, `cancel_print`, `pause_print` — WRITE.
- `set_temp`, `set_fan`, `set_speed` — WRITE.
- `home`, `calibrate` — EXECUTE.
- `emergency_stop` — EXECUTE.

Для WRITE/EXECUTE — см. `kiln-safety`.

## Правила

1. Только MCP — не `curl`, не `kiln3d status`.
2. Read-only — 71 инструмент.
3. Показывать полные данные.
4. Снимок — inline, не путь.

## Ссылки

- `kiln-safety` — human-in-the-loop.
- `docs/KILN.md`, `docs/PRINTER-CONFIG.md`.
