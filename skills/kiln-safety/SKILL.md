---
name: kiln-safety
query: "Kiln, 3D-принтер, ZAV, safety, безопасность, human-in-the-loop"
description: Правила безопасности для работы с Kiln MCP (3D-принтер ZAV). Read-only по умолчанию. Любое WRITE/EXECUTE — только с явным подтверждением Артёма.
version: 1.0.0
author: hermes
license: MIT
---

# Kiln Safety — правила работы с принтером ZAV

> ⚠️ **КРИТИЧНО.** Правила обязательны к соблюдению. Нарушение = физический риск (пожар, поломка принтера, потеря данных).

## Категории инструментов Kiln

| Категория | Примеры | Разрешение |
|-----------|---------|------------|
| **READ** | `printer_status`, `monitor_print`, `snapshot`, `kiln_health`, `printer_list` | ✅ **Всегда можно** |
| **ANALYZE** | `analyze_print_failure_smart`, `validate_model`, `preflight_check`, `troubleshoot_print_issue` | ✅ **Всегда можно** (анализ не меняет состояние) |
| **DESIGN** | `design_session`, `recommend_design_material`, `find_design_templates`, `estimate_structural_load` | ✅ **Можно** (советы, не действия) |
| **WRITE** | `start_print`, `cancel_print`, `pause_print`, `set_temp`, `set_fan`, `upload_file`, `slice_model` | 🛑 **ТОЛЬКО** с явным подтверждением |
| **EXECUTE** | `home`, `calibrate`, `emergency_stop`, `restart_server`, `set_speed` | 🛑 **ТОЛЬКО** с явным подтверждением |

## Правило human-in-the-loop (ОБЯЗАТЕЛЬНО)

**Перед ЛЮБЫМ WRITE или EXECUTE:**

1. **Опиши**, что **собираешься** сделать.
2. **Укажи**, какие **параметры** (например, «start_print ZAV, файл benchy.gcode»).
3. **Укажи**, какие **последствия** (например, «начнётся печать, ~45 мин»).
4. **Спроси явно:** «Подтверждаешь? (да/нет)».
5. **Жди** ответа.

**ЗАПРЕЩЕНО:**
- Вызывать WRITE/EXECUTE **без** подтверждения.
- «Просто попробовать» — **без** явного «да».
- «Для проверки» — **без** явного «да».
- Автоматически повторять **упавшие** WRITE-команды.
- **Изменять** настройки принтера (даже временно) **без** подтверждения.

## Что делать при ошибке

**Если** WRITE/EXECUTE **упал:**
1. **Не повторяй** автоматически.
2. **Покажи** ошибку.
3. **Спроси:** «Повторить? Возможно, нужно сначала исправить X».
4. **Жди** решения.

## Что можно **без** подтверждения

**READ / ANALYZE / DESIGN** — **свободно:**
- `printer_status` — статус.
- `monitor_print` — мониторинг + снимок.
- `snapshot` — снимок камеры.
- `kiln_health` — версия, uptime.
- `printer_list` — список принтеров.
- `validate_model` — проверка модели.
- `preflight_check` — предполётная проверка.
- `analyze_print_failure_smart` — анализ ошибки.
- `troubleshoot_print_issue` — диагностика.
- `recommend_design_material` — рекомендация материала.
- `estimate_cost` — оценка стоимости.

## Что нельзя **без** подтверждения

**WRITE / EXECUTE:**
- `start_print` — **начать** печать.
- `cancel_print` — **отменить**.
- `pause_print` / `resume_print` — **пауза/продолжить**.
- `set_temp` — **изменить** температуру.
- `set_fan` — **изменить** вентилятор.
- `set_speed` — **изменить** скорость.
- `home` — **парковка**.
- `calibrate` — **калибровка**.
- `emergency_stop` — **аварийный стоп**.
- `upload_file` — **загрузка** файла.
- `slice_model` — **слайсинг** (создаёт G-code).
- `restart_server` — **перезапуск** Kiln.

## Особые случаи

**1. `emergency_stop`** — **разрешено** вызывать **сразу** (без подтверждения) **только если**:
- Принтер **реально** в **аварийной** ситуации (дым, искры, разрушение).
- **Обычные** «останови печать» — **через** `cancel_print` **с** подтверждением.

**2. `preflight_check`** — **можно** свободно — это **read-only** проверка **перед** печатью.

**3. `analyze_print_failure_smart`** — **можно** свободно — **не** меняет состояние.

**4. `get_recovery_plan`** — **можно** свободно — **только** план, **не** выполнение.

**5. `retry_print_with_fix`** — **требует** подтверждения — **создаёт** новую печать.

## Контекст принтера

- **ZAV** — Klipper, BTT Manta M5P + CB1, EBB36 CAN.
- **Build volume:** 295×200×200.
- **Hotend:** max 300°C, **bed:** max 130°C.
- **Камера:** ustreamer 640×480.
- **Tailscale:** `100.92.59.53:7125`.

## Ссылки

- `docs/KILN.md` — инструкция MCP.
- `docs/PRINTER-CONFIG.md` — конфиг принтера.
- `docs/SECURITY.md` — общие правила безопасности MCP.
