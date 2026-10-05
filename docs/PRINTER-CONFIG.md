# 3D-принтер ZAV — конфигурация

> Полная спецификация принтера. Источник: конфиги Klipper (скачаны 2026-10-04).
> Обновлено: 2026-10-05.

## Железо

| Компонент | Модель |
|---|---|
| **Main MCU** | BIGTREETECH Manta M5P |
| **Хост** | BIGTREETECH CB1 (ARM64, Armbian 26.8.3) |
| **Toolhead** | BIGTREETECH EBB36 CAN (uuid: 8ab3849465d5) |
| **Probe** | BIGTREETECH Eddy (uuid: 3edf0ec5b36b, ldc1612) |
| **Accelerometer** | ADXL345 (в EBB36) |
| **Filament sensor** | SFS2 (Smart Filament Sensor 2) |
| **Extruder driver** | TMC2209 (0.8 А, stealthchop off) |
| **Корпус** | ZAV v3 Pro (самосбор) |
| **Кинематика** | **H-Bot** |
| **Nozzle** | 0.400 мм |
| **Filament** | 1.75 мм |

## Геометрия

| Параметр | Значение |
|---|---|
| **Build volume** | **295 × 200 × 200 мм** |
| **Рабочая зона (mesh)** | X: 5–290, Y: 27–196 → ~285 × 169 мм |
| **Bed mesh** | 6 × 4, bicubic, tension 0.2 |
| **Probe offset** | X: 0, Y: +22 мм |
| **Safe Z home** | X 150, Y 100, Z-hop 10 мм |

## Температуры

| Зона | Min | Max |
|---|---|---|
| **Extruder** | 0 | **300 °C** |
| **Bed** | 0 | **130 °C** |
| **MCU** | 10 | 100 °C |

## Extruder

| Параметр | Значение |
|---|---|
| **Sensor** | ATC Semitec 104NT-4-R025H42G |
| **rotation_distance** | 5.6146 |
| **PID** | Kp=32.914, Ki=9.540, Kd=28.388 |
| **Pressure advance** | 0.04 |
| **microsteps** | 16 |

## Input shaper

| Ось | Тип | Частота |
|---|---|---|
| **X** | `ei` | 74.6 Hz |
| **Y** | `mzv` | 64.6 Hz |

## Вентиляторы

| Вентилятор | Pin | Назначение |
|---|---|---|
| Part cooling | EBBCan:PA1 | Обдув модели |
| Hotend fan | EBBCan:PA0 | Обдув хотэнда (50°C) |

## Камера

| Параметр | Значение |
|---|---|
| **Software** | crowsnest + ustreamer v6.36 |
| **Device** | /dev/video0 |
| **Resolution** | 640 × 480 |
| **FPS** | 15 |
| **Port** | 8080 |
| **MJPEG** | http://100.92.59.53:8080/?action=stream |
| **Snapshot** | http://100.92.59.53:8080/?action=snapshot |

**Статус:** ❌ **камера не подключена** (`/dev/video0` отсутствует, crowsnest падает).

## Klipper-макросы (21)

**Печать:** PAUSE, RESUME, CANCEL_PRINT
**Filament:** M600, M701, M702, FILAMENT_CHANGE, LOAD_FILAMENT, UNLOAD_FILAMENT
**SFS2:** SFS_ENABLE, SFS_DISABLE
**Служебные:** M300, M80, M81, SHUTDOWN, REBOOT, M486, M125

## Модульная структура `printer.cfg`

[include fluidd.cfg]
[include klipper-config/manta.cfg]
[include klipper-config/ebbcan.cfg]
[include klipper-config/steppers.cfg]
[include klipper-config/bed.cfg]
[include klipper-config/fans.cfg]
[include klipper-config/display.cfg]
[include klipper-config/sfs2.cfg]
[include klipper-config/eddy.cfg]
[include klipper-config/gcode-macros.cfg]
[include klipper-config/gcode_shell_command.cfg]

## Интеграция с Kiln MCP

**См.** `docs/KILN.md`.

- **71 read-инструмент** в whitelist.
- **8 EXECUTE** — исключены (start_print, set_temperature).
- **60 WRITE** — исключены (delete, generate).
- **`connect_timeout: 180`** — хватает на 70-сек старт.
- **`KILN_NO_UPDATE_CHECK=1`** + **`KILN_LOG_LEVEL=ERROR`**.

## Управление

- **Moonraker:** http://100.92.59.53:7125
- **Fluidd:** http://100.92.59.53/
- **SSH:** ssh biqu@100.92.59.53
- **Tailscale IP:** 100.92.59.53
- **LAN IP:** 192.168.10.21

## Файлы

Локальная копия конфигов: `/tmp/printer-config/config/` (26 файлов, ~80 КБ).
Оригиналы: `biqu@100.92.59.53:/home/biqu/printer_data/config/`.

## Известные ограничения

- **Build volume 295×200×200** — нестандартный (Ender-3: 235×235×250). Kiln `klipper_generic` — без точных лимитов.
- **Hotend 300°C** — высокотемпературный (стандарт 260–280).
- **Камера 640×480** — для детекции дефектов достаточно, точность ограничена.
- **`gcode_shell_command.cfg`** — закомментирован (нет `extras/gcode_shell_command.py`).
- **Камера не подключена** — snapshot не работает.

## Kiln install-mcp — НЕ использовать

`kiln3d install-mcp` записывает config в Claude/Cursor/Codex. **НЕ для Hermes** — конфликт.
