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
- **Marketplace** — поиск моделей (Makerworld).
- **Дизайн** — text-to-3D, шаблоны.

**У нас активны 71 read-инструмент** (WRITE/EXECUTE — за скобками whitelist).

## Контекст принтера ZAV

| Параметр | Значение |
|----------|----------|
| **Имя** | `zav` (или `ZAV`) |
| **Прошивка** | Klipper |
| **MCU** | BTT Manta M5P + CB1 |
| **Toolhead** | EBB36 CAN |
| **Probe** | BTT Eddy |
| **Filament sensor** | SFS2 |
| **Build volume** | 295 × 200 × 200 мм |
| **Hotend max** | 300 °C |
| **Bed max** | 130 °C |
| **Камера** | ustreamer, 640×480, `100.92.59.53:8080` |
| **Moonraker** | `100.92.59.53:7125` (Tailscale) |

## Инструменты (read-only)

### Статус и здоровье

| Инструмент | Что делает |
|-----------|------------|
| `printer_status` | State, temps, progress, filename, time remaining |
| `kiln_health` | Версия, uptime, safety-gate |
| `printer_list` | Список зарегистрированных принтеров |

### Мониторинг печати

| Инструмент | Что делает |
|-----------|------------|
| `monitor_print` | Полный отчёт + снимок + стоимость |
| `snapshot` | Снимок камеры (path к файлу) |

### Анализ

| Инструмент | Что делает |
|-----------|------------|
| `preflight_check` | Проверка перед печатью |
| `validate_model` | Проверка модели на печатаемость |
| `analyze_print_failure_smart` | Анализ причины сбоя |
| `troubleshoot_print_issue` | Диагностика проблемы |
| `get_recovery_plan` | План восстановления (без выполнения) |

### Design intelligence

| Инструмент | Что делает |
|-----------|------------|
| `recommend_design_material` | Рекомендация материала |
| `find_design_templates` | 18 templates |
| `get_material_design_profile` | Свойства материала |
| `estimate_structural_load` | Оценка нагрузки |
| `estimate_cost` | Оценка стоимости |

## Типичные сценарии

### 1. «Покажи статус принтера»

    printer_status()

Показать пользователю полные данные, не сокращать.

### 2. «Сделай снимок камеры»

    snapshot()

Прочитать файл как изображение и показать inline (не просто путь).

### 3. «Мониторь печать»

    monitor_print()

1. Показать полный отчёт.
2. Прочитать снимок и показать inline.
3. Включить оценку стоимости.

### 4. «Проверь модель на печатаемость»

    validate_model(file_path="/path/to/model.stl")

Показать проблемы + рекомендации.

## Что нельзя через этот skill

- `start_print`, `cancel_print`, `pause_print`, `resume_print` — **WRITE**.
- `set_temp`, `set_fan`, `set_speed` — **WRITE**.
- `home`, `calibrate` — **EXECUTE**.
- `emergency_stop` — **EXECUTE** (только при аварии).
- `restart_server` — **EXECUTE**.

**Для WRITE/EXECUTE — см. `kiln-safety` + подтверждение.**

## Правила

1. **Только MCP** — не `curl`, не `kiln3d status` из CLI.
2. **Read-only** — 71 инструмент.
3. **Показывать полные данные** — не сокращать.
4. **Снимок** — inline, не путь.
5. **При ошибке MCP** — сообщить, не обходить через curl.

## Ссылки

- `kiln-safety` — human-in-the-loop.
- `docs/KILN.md` — инструкция MCP.
- `docs/PRINTER-CONFIG.md` — конфиг принтера.
