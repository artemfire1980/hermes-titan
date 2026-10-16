# MEMORY.md — snapshot (2026-10-16)

> **Источник:** `/mnt/ai-ssd/hermes/memories/MEMORY.md`
> **Обновлять при значимых изменениях.**

# HERMES-TITAN — Memory (hot facts)

## Platform
- Khadas VIM4, ARM64, 8 GB RAM, Ubuntu 24.04.5.
- HERMES_HOME=/mnt/ai-ssd/hermes, project=~/ai-system.

## Hard constraints
- ARM64, 8 GB RAM — не предлагать тяжёлое. Kubernetes/distributed/облака — нет.
- Секреты — в .env, не в git. Токены не читать.
- Если инструмента нет — "недоступно по политике".

## Gotchas
- sqlite3 CLI — не использовать. Пакеты в venv — через pm.sync_venv.
- Аудит — по git ls-files, .pyc игнорировать.
- Код пишет Aider в ~/ai-system/projects/.

## Kiln (3D-принтер, Klipper CB1, Moonraker btt-cb1:7125)
- Разрешено: printer_status, temp (read), calibrate.
- ЗАПРЕЩЕНО: start_print, cancel_print, emergency_stop, firmware, fan.
- Печать — ТОЛЬКО человек. При дефекте — уведомить, НЕ останавливать.

## Память и маршрутизация
Проекты (МойСклад, Kiln, почта, Hermes update, voice, research, Артём) — в Holographic.
При запросе про проект: skill (по query) → recall("проект") → API (если свежее).
MEMORY.md — universal. Skills — алгоритмы. Holographic — факты.
