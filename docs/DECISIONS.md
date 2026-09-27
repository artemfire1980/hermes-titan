
---

## DEC-027: Holographic HRR требует NumPy в runtime venv

**Дата:** 2026-09-27
**Статус:** принято (с известными ограничениями)
**Контекст:** CP-008, закрытие memory provider

### Проблема
Memory provider Holographic для семантического поиска (HRR-векторы) требует NumPy.
NumPy отсутствовал в runtime venv gateway → новые факты писались с hrr_vector = NULL.
В Hermes три Python: hermes-agent/venv (наши скрипты), tools/python-3.14.7 (PM),
и runtime venv в installs/<hash>/environments/<hash>/venv — последний используется
gateway. NumPy ставили в первые два, а нужен был в третьем.

### Решение
1. NumPy 2.5.3 установлен в runtime venv через:
   uv pip install --python <runtime-venv>/bin/python numpy==2.5.3
2. Создан скрипт /mnt/ai-ssd/hermes/bin/ensure-hrr-numpy — проверяет и ставит NumPy.
3. Скрипт подключён как ExecStartPre systemd-юнита gateway через drop-in
   ~/.config/systemd/user/hermes-gateway-469b1f3f.service.d/ensure-hrr-numpy.conf.

### Результат
- numpy 2.5.3 в runtime venv (прямой импорт).
- ExecStartPre отработал при рестарте gateway (status=0).
- Факты 23–28 в memory_store.db имеют hrr_len = 4100.
- Сквозной цикл замкнут.

### Известные ограничения
- ensure-hrr-numpy хардкодит хэши installs/21af0c3aa8d717d2 и environments/661225cb...
  После hermes pm repair хэши изменятся → exit 1 → gateway не стартует.
- В installs/21af0c3aa8d717d2/environments/ пять каталогов. Неизвестно, какой активен.
- Правильный долгосрочный путь: свой holographic extra в pyproject.toml
  или upstream issue в NousResearch/hermes-agent (holographic.py не использует
  pm.ensure_import).

### Отложено в техокно
- Динамический поиск runtime venv (без хардкода).
- Починка PM (ffmpeg, ripgrep, digest mismatch).
- Offline WAL-конвертация state.db, kanban.db, projects.db.
- Разбор source-completion-pending.

### Ссылки
- Полный baseline: docs/CP-008-BASELINE.md
- Связанные: DEC-023 (built-in only, отменено), DEC-024 (Hindsight отклонён),
  DEC-025 (Holographic выбран), DEC-026 (Holographic принят с ограничениями).
