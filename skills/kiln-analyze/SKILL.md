--- name: kiln-analyze query: "Kiln, анализ принтера, конфиг принтера, printer.cfg, klippy.log,
input shaper, PID, bed mesh, оптимизация, диагностика" description: Анализ конфигов, логов и
тестов 3D-принтера ZAV. Определение оптимальных настроек, выявление проблем, рекомендации по
оптимизации. БЕЗ внесения изменений — только анализ и предложения. version: 1.0.0 author: hermes
license: MIT ---
# Kiln Analyze — анализ и оптимизация принтера ZAV
> ⚠️ **Только анализ.** Никаких изменений в конфигах, настройках, прошивке без явного подтверждения
> Артёма (см. `kiln-safety`).
## Что этот skill делает
1. **Читает** конфиги принтера, логи, результаты тестов. 2. **Анализирует** — выявляет проблемы,
отклонения, возможности оптимизации. 3. **Предлагает** конкретные изменения с обоснованием. 4.
**Ждёт** подтверждения перед применением. **НЕ делает:** - Не изменяет файлы (`printer.cfg`,
`moonraker.conf`). - Не перезапускает сервисы. - Не применяет настройки. - Не выполняет G-code, не
калибрует.
## Где что лежит
### Локальные конфиги (скачаны)
**Путь:** `/tmp/printer-config/config/` (26 файлов, ~80 КБ).
| Файл | Что внутри | ------|-----------| `printer.cfg` | Главный, #include остальных |
| `klipper-config/manta.cfg` | MCU Manta M5P, пины | `klipper-config/ebbcan.cfg` | Toolhead EBB36
| CAN, extruder, input shaper | `klipper-config/steppers.cfg` | Кинематика, build volume |
| `klipper-config/bed.cfg` | Стол, PID, max temp | `klipper-config/eddy.cfg` | Probe BTT Eddy, bed
| mesh | `klipper-config/sfs2.cfg` | Filament sensor | `klipper-config/gcode-macros.cfg` | 21
| макрос | `klipper-config/fans.cfg` | Вентиляторы | `klipper-config/display.cfg` | Дисплей |
| `crowsnest.conf` | Камера | `moonraker.conf` | Moonraker API |
**Если конфиги устарели** — обновить: mkdir -p /tmp/printer-config scp -r
    biqu@100.92.59.53:/home/biqu/printer_data/config/ /tmp/printer-config/
### Живые конфиги (на принтере)
**Через SSH** (только чтение): ssh biqu@100.92.59.53 "cat ~/printer_data/config/printer.cfg" ssh
    biqu@100.92.59.53 "cat ~/printer_data/config/klipper-config/steppers.cfg"
### Логи (на принтере)
| Файл | Путь | Что внутри | ------|------|-----------| **klippy.log** |
| `~/printer_data/logs/klippy.log` | Klipper — ошибки, тайминги, warnings | **moonraker.log** |
| `~/printer_data/logs/moonraker.log` | Moonraker | **crowsnest.log** |
| `~/printer_data/logs/crowsnest.log` | Камера |
**Чтение (последние 200 строк):** ssh biqu@100.92.59.53 "tail -200 ~/printer_data/logs/klippy.log"
**Поиск ошибок:**
    ssh biqu@100.92.59.53 "grep -iE 'error|warning|failed' ~/printer_data/logs/klippy.log | tail
    -50"
## Что анализировать
### 1. Input shaper
**Файл:** `klipper-config/ebbcan.cfg` → `[input_shaper]`. **Что смотреть:** - `shaper_freq_x`,
`shaper_freq_y` — частоты резонанса. - `shaper_type_x`, `shaper_type_y` — тип (ei, mzv, zv, ...).
**Оптимально:** измерены через `ADXL345` (test resonance). **Проблемы:** - Частота ниже 30 Гц —
сильный ringing. - Нетипичный shaper — не оптимален. **Рекомендации:** - Перезапустить
`TEST_RESONANCES AXIS=X` (требует подтверждения). - Обновить shaper type — если данные устарели.
### 2. PID хотэнда / стола
**Файл:** `klipper-config/bed.cfg`, `ebbcan.cfg` → `[extruder]`, `[heater_bed]`. **Что смотреть:**
- `pid_Kp`, `pid_Ki`, `pid_Kd`. - Отклонение температуры при печати (в логах). **Проблемы:** -
Колебания >±3°C — PID не оптимален. - Расхождение с последней калибровкой. **Рекомендации:** -
Перезапустить `PID_CALIBRATE HEATER=extruder TARGET=200` (требует подтверждения).
### 3. Bed mesh
**Файл:** `printer.cfg` → `#*# [bed_mesh default]` (автогенерируемое). **Что смотреть:** -
Значения в точках mesh. - Разброс (min/max). **Проблемы:** - Разброс >0.5 мм — стол неровный. -
`bicubic` vs `lagrange` — если плоскость сложная. **Рекомендации:** - Убедиться, что стол
выровнен. - При необходимости — `BED_MESH_CALIBRATE` (требует подтверждения).
### 4. Pressure advance
**Файл:** `ebbcan.cfg` → `[extruder]` → `pressure_advance`. **Что смотреть:** текущее значение (у
нас 0.04). **Проблемы:** - Углы с «каплями» — PA слишком низкий. - Пропуски в углах — PA слишком
высокий. **Рекомендации:** - Проверить через `TUNING_TOWER` (требует подтверждения).
### 5. Тайминги в klippy.log
**Что искать:** - `Timer too close` — Klipper не успевает. - `Move queue overflow`. -
`Communication timeout with MCU`. **Причины:** USB-шум, медленный CB1, ошибки в конфиге.
**Рекомендации:** анализ + предложения (без изменений).
### 6. Логи печати
**Из `printer_status` / `monitor_print`:** - Прогресс. - Температуры (стабильность). - Ошибки.
**Что искать:** - Отклонения температуры. - Паузы, остановки. - Warnings.
## Как формулировать предложения
**Формат:**
    ## Предложение: <название>
    ### Проблема
    <что не так>
    ### Данные
    <какие логи/конфиги указывают на проблему>
    ### Предлагаемое изменение
    <конкретное: файл, строка, было → станет>
    ### Обоснование
    <почему это лучше>
    ### Риск
    <что может пойти не так>
    ### Откат
    <как вернуть назад>
    ### Подтверждение
    Подтверждаешь? (да/нет)
## Что нельзя
- Изменять `printer.cfg` без подтверждения. - Перезапускать Klipper (`RESTART`,
`FIRMWARE_RESTART`) без подтверждения. - Выполнять `PID_CALIBRATE`, `BED_MESH_CALIBRATE`,
`TEST_RESONANCES` без подтверждения. - Изменять `moonraker.conf` без подтверждения. -
Автоматически применять рекомендации — **только** после **явного** «да».
## Примеры задач
**1. «Проанализируй input shaper»** Действия: 1. Прочитать `ebbcan.cfg` → `[input_shaper]`. 2.
Сравнить с типичными значениями. 3. Прочитать `klippy.log` — искать ringing warnings. 4.
Предложить: оставить / изменить (с подтверждением). **2. «Проверь PID стола»** Действия: 1.
Прочитать `bed.cfg` → PID. 2. Прочитать `klippy.log` — найти отклонения температур. 3. Сравнить.
4. Предложить: оставить / перекалибровать (с подтверждением). **3. «Анализ логов за последний
час»** Действия: 1. `ssh ... "tail -500 ~/printer_data/logs/klippy.log"` 2. Найти: errors,
warnings, timer issues. 3. Сгруппировать. 4. Предложить действия. **4. «Оптимизируй настройки под
печать PLA»** Действия: 1. Прочитать текущие настройки. 2. Сравнить с рекомендованными для PLA. 3.
Предложить изменения (температуры, скорости, охлаждение). 4. **Ждать** подтверждения.
## Ссылки
- `kiln-safety` — правила human-in-the-loop. - `kiln-printer` — read-only мониторинг. -
`docs/PRINTER-CONFIG.md` — полный конфиг принтера.
- `docs/KILN.md` — инструкция Kiln MCP.
