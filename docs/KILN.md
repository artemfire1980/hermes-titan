# Kiln — MCP-сервер для 3D-принтера

> Интеграция Kiln (kiln3d 1.4.1.1) с Hermes-Titan.
> Обновлено: 2026-10-05.

## Что это

**Kiln** — open-source MCP-сервер для управления 3D-принтерами (Bambu, Creality, Prusa, Elegoo, Klipper/Moonraker, OctoPrint, Duet, Marlin).

- **468 инструментов** (46 плагинов).
- **MCP stdio** transport.
- **Free-tier** для личных проектов.
- **AGPL-3.0** лицензия.

**Репозиторий:** https://github.com/codeofaxel/kiln

## Конфигурация Hermes

```yaml
mcp_servers:
  kiln:
    command: /home/khadas/.cache/uv/archive-v0/vZuWT9b7EakyQtIV/bin/kiln3d
    args:
      - serve
    env:
      KILN_NO_UPDATE_CHECK: '1'
      KILN_LOG_LEVEL: ERROR
    connect_timeout: 180.0
    enabled: true
    tools:
      include: [<71 инструмент>]
      resources: false
      prompts: false
Установка:
uvx kiln3d setup
# выбрать: moonraker, host=100.92.59.53:7125, name=ZAV, model=klipper_generic
Настройка Hermes (важные моменты)
1. --args — последним
hermes mcp add kiln --command <bin> --env K1=V1 --env K2=V2 --connect-timeout 180 --args serve
Правило: --args — последний. Всё после — аргументы Kiln, не Hermes.

2. connect_timeout: 180
Kiln стартует 70 секунд (46 плагинов, check deps). Default Hermes — 30 сек → Connection closed.

Fix: python-патч config — mcp_servers.kiln.connect_timeout: 180.

3. KILN_NO_UPDATE_CHECK=1
Отключает проверку обновлений при старте. Ускоряет запуск.

4. KILN_LOG_LEVEL=ERROR
Меньше INFO-логов. Не ускоряет, но чище.

Whitelist — 71 инструмент
Разрешены:

Мониторинг (12)
printer_status, monitor_print, monitor_print_vision, kiln_health, health_check, check_print_health, check_print_readiness, check_printer_health, get_bed_mesh, ams_status, cfs_status, bed_level_status

Камера (2)
printer_snapshot, list_snapshots

Инфо (8)
get_started, get_skill_manifest, check_my_tier, get_agent_context, plugin_info, database_status, encryption_status, emergency_status

Валидация / диагностика (12)
validate_and_prepare, analyze_printability, analyze_print_file, analyze_mesh_geometry, analyze_non_manifold_edges, analyze_warping_risk, analyze_print_failure, analyze_print_failure_smart, troubleshoot_print_issue, detect_print_failure, diagnose_print_failure_live, diagnose_mesh

Материалы (8)
get_active_material, get_compatible_materials, recommend_design_material, find_material_match, find_material_substitute, check_material_match, check_material_sufficiency, check_material_environment

Оценка (8)
estimate_cost, estimate_print_time, estimate_material_cost, estimate_mesh_weight, estimate_supports, estimate_structural_load, estimate_before_design, estimate_print_progress

Design intelligence (8)
find_design_templates, analyze_design_requirements, list_design_versions, get_design_version, search_design_versions, design_advisor, design_improvement_plan, audit_original_design

Мониторинг в реальном времени (3)
watch_print, watch_print_status, webcam_stream

Принтеры / модели (4)
find_printers_with_material, list_slicer_profiles, get_slicer_profile, find_slicer

Модели (read) (6)
browse_models, community_stats, model_revenue, search_all_models, cross_section_view, extract_file_metadata

Что ИСКЛЮЧЕНО и почему
🔴 EXECUTE (High) — 8 инструментов
Физический вред, пожар, поломка:

Инструмент	Риск
start_print	Запуск печати — пожар, таран стола
cancel_print	Прерывание — поломка детали
pause_print	Пауза — сопло остаётся 250°C → капание
resume_print	Возобновление — отслоение
set_temperature	M104 S500 → пожар
set_fan	Перегрев / деформация
slice_and_print	Комбо: слайсинг + печать без проверки
multi_material_print	Запутанность филамента
❌ WRITE (Medium) — 60 инструментов
Не физически опасны, но изменяют состояние:

delete_* (5) — удаление файлов, webhooks, кеша.

update_firmware, rollback_firmware — прошивка.

register_printer, register_webhook — регистрация.

generate_* (9) — LLM-генерация (токены).

save_*, create_*, add_*, remove_* — изменения.

set_autonomy_level — уровень автономии агента.

trim_serve_processes, upgrade_kiln, restart_server — управление.

signin, pair, link — аккаунт.

clear_emergency_stop, emergency_stop, emergency_trip_input — аварийные.

❌ Остальные (~330)
Не классифицированы — не включаем. Принцип: только проверенный whitelist.

Использование
Мониторинг
Покажи статус принтера ZAV
→ printer_status — состояние, температуры, прогресс.

Камера
Сделай снимок принтера
→ printer_snapshot — путь к JPEG. Требует работающей камеры (сейчас не подключена).

Валидация модели
Проверь, можно ли напечатать model.stl
→ analyze_printability, analyze_mesh_geometry.

Оценка стоимости
Сколько будет стоить печать model.stl?
→ estimate_cost, estimate_print_time.

Диагностика
Почему последняя печать упала?
→ analyze_print_failure_smart, troubleshoot_print_issue.

Ограничения
1. Камера не подключена
/dev/video0 — отсутствует. crowsnest — падает (No usable Devices Found). printer_snapshot — не работает.

Fix: подключить USB-камеру к CB1. После: /dev/video0 → crowsnest подхватит → printer_snapshot заработает.

2. KILN_LOG_LEVEL — через python-патч
Hermes не сохраняет два --env из CLI. Fix: python-патч config.

3. Kiln — AGPL-3.0
Для коммерческого использования (продажа печати) — Business-tier. Личное — Free.

Параметры принтера ZAV
См. docs/PRINTER-CONFIG.md.

BTT Manta M5P + CB1

EBB36 CAN toolhead

BTT Eddy probe

SFS2 (Smart Filament Sensor)

Build volume: 295 × 200 × 200 мм

Hotend max: 300°C

Bed max: 130°C

Moonraker: http://100.92.59.53:7125
