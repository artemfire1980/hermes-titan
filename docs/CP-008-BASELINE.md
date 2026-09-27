# CP-008 Baseline — Holographic Memory

**Дата фиксации:** 2026-09-27
**Узел:** Khadas VIM4 (ARM64, 8 GB RAM, Ubuntu 24.04.5, kernel 5.15.137)
**Статус:** CP-008 закрыт условно — работает, но с известными ограничениями.
**Цель документа:** точка возврата для будущих сессий / техокна.

---

## 1. TL;DR

### Что было
Memory provider = Holographic (плагин Hermes). Для семантического поиска
(HRR-векторы) ему нужен NumPy. NumPy отсутствовал в runtime venv
gateway → новые факты писались с hrr_vector = NULL → семантический поиск
не работал, оставался только FTS5 keyword.

### Первопричина (подтверждена фактами)
В Hermes — три Python:

| Python | Путь | Используется | NumPy |
|---|---|---|---|
| venv Hermes | /mnt/ai-ssd/hermes/hermes-agent/venv | нашими скриптами | 2.5.3 |
| PM Python | /mnt/ai-ssd/hermes/tools/python-3.14.7+20260901-linux-arm64 | PM-managed | 2.5.3 |
| Runtime venv | /mnt/ai-ssd/hermes/installs/21af0c3aa8d717d2/environments/661225cb695e4e36a685ccf3aa8792d9/venv | gateway | отсутствовал → 2.5.3 после фикса |

gateway использует runtime venv, и NumPy ставили не туда (дважды).

### Что сделали
1. Поставили NumPy 2.5.3 в runtime venv через uv pip install --python.
2. Создали /mnt/ai-ssd/hermes/bin/ensure-hrr-numpy — скрипт-страховка.
3. Подключили его как ExecStartPre systemd-дроп-ином.
4. Сделали бэкапы: facts.json.bak.*, memory_store.db.bak, config.yaml.bak, numpy-2.5.3-backup/.

### Что работает (проверено фактами 2026-09-27)
- numpy 2.5.3 в runtime venv (прямой импорт).
- ExecStartPre отработал при рестарте gateway в 12:50:52 (status=0).
- Факты 23–28 в memory_store.db — hrr_len = 4100.
- Факт 28 (SYSTEMD-ENSURE-TEST-53) создан после рестарта — сквозной цикл замкнут.

### Что не работает / не проверено
- ensure-hrr-numpy хардкодит хэши путей → сломается при hermes pm repair.
- В installs/21af0c3aa8d717d2/environments/ пять каталогов. Неизвестно,
  какой именно использует gateway.
- hermes pm out of sync: ffmpeg, ripgrep, venv vs uv.lock.
- source-completion-pending в каталоге install (12:51) — не выяснено.
- memory_banks пуст (опционально, требует _rebuild_bank).

---

## 2. Текущее состояние

### 2.1. Config (/mnt/ai-ssd/hermes/config.yaml)

memory:
  provider: holographic
plugins:
  disabled: []
  enabled: []
database:
  journal_mode: delete

Секреты — в /mnt/ai-ssd/hermes/.env (chmod 600). Не читать целиком, не коммитить.

### 2.2. Runtime venv

Путь:
/mnt/ai-ssd/hermes/installs/21af0c3aa8d717d2/environments/661225cb695e4e36a685ccf3aa8792d9/venv

Python: readlink -f venv/bin/python →
/mnt/ai-ssd/hermes/tools/python-3.14.7+20260901-linux-arm64/bin/python3.14

NumPy: 2.5.3 (установлен вручную через uv pip install).

Проверка:
RT_VENV="/mnt/ai-ssd/hermes/installs/21af0c3aa8d717d2/environments/661225cb695e4e36a685ccf3aa8792d9/venv"
"$RT_VENV/bin/python" -c "import numpy; print('numpy', numpy.__version__)"
# ожидаем: numpy 2.5.3

### 2.3. Скрипт ensure-hrr-numpy

Путь: /mnt/ai-ssd/hermes/bin/ensure-hrr-numpy (chmod +x)

Содержание (как есть, с хардкодом):
#!/usr/bin/env bash
set -euo pipefail
RT_VENV="/mnt/ai-ssd/hermes/installs/21af0c3aa8d717d2/environments/661225cb695e4e36a685ccf3aa8792d9/venv"
PY="$RT_VENV/bin/python"
UV="/mnt/ai-ssd/hermes/tools/uv-0.12.3-linux-arm64/uv"
# ... проверка numpy, установка через uv, exit 0/1 ...

Известное ограничение: если после hermes pm repair хэши изменятся —
[ ! -x "$PY" ] → exit 1 → по ignore_errors=no gateway не стартует.

Быстрый смягчитель (если падает): заменить exit 1 на exit 0 с warning.

### 2.4. Systemd drop-in

Файл: ~/.config/systemd/user/hermes-gateway-469b1f3f.service.d/ensure-hrr-numpy.conf

[Service]
ExecStartPre=/mnt/ai-ssd/hermes/bin/ensure-hrr-numpy

Рядом: runtime.conf (не наш):
[Service]
Environment="HERMES_RUNTIME_DIR=/mnt/ai-ssd/hermes/tools"

Проверка:
systemctl --user show hermes-gateway-469b1f3f.service -p ExecStartPre -p DropInPaths --no-pager

### 2.5. База memory_store.db

Путь: /mnt/ai-ssd/hermes/memory_store.db

journal_mode = delete

Факты 23–28 (свежие) — hrr_len = 4100. Проверка:
sqlite3 /mnt/ai-ssd/hermes/memory_store.db \
  "SELECT fact_id, length(hrr_vector), substr(content,1,50) FROM facts ORDER BY fact_id DESC LIMIT 10;"

### 2.6. Бэкапы

- /mnt/ai-ssd/hermes/installs/21af0c3aa8d717d2/facts.json.bak*
- /mnt/ai-ssd/hermes/memory_store.db.bak
- /mnt/ai-ssd/hermes/config.yaml.bak
- /mnt/ai-ssd/hermes/backups/numpy-2.5.3-backup/

---

## 3. Как воспроизвести проверку

export HERMES_HOME=/mnt/ai-ssd/hermes
source "$HERMES_HOME/hermes-agent/venv/bin/activate"

# 1. gateway жив
hermes gateway status

# 2. провайдер памяти
hermes memory status

# 3. runtime NumPy
RT_VENV="/mnt/ai-ssd/hermes/installs/21af0c3aa8d717d2/environments/661225cb695e4e36a685ccf3aa8792d9/venv"
"$RT_VENV/bin/python" -c "import numpy; print('numpy', numpy.__version__)"

# 4. hrr_len свежих фактов
sqlite3 /mnt/ai-ssd/hermes/memory_store.db \
  "SELECT fact_id, length(hrr_vector) AS hrr_len, substr(content,1,50) FROM facts ORDER BY fact_id DESC LIMIT 10;"

# 5. ExecStartPre
systemctl --user show hermes-gateway-469b1f3f.service -p ExecStartPre -p DropInPaths --no-pager

---

## 4. Известные проблемы и что с ними делать

### 4.1. ensure-hrr-numpy хардкодит хэши — риск высокий

Когда проявится: после hermes pm repair / hermes pm install / hermes update.

Симптом: gateway не стартует, ExecStartPre возвращает status=1.

Быстрая мера (1 мин):
Заменить в /mnt/ai-ssd/hermes/bin/ensure-hrr-numpy:
  if [ ! -x "$PY" ]; then ... exit 1; fi
на:
  if [ ! -x "$PY" ]; then echo "Runtime Python не найден"; exit 0; fi
Затем: systemctl --user daemon-reload && hermes gateway restart

Правильное решение (техокно): динамический поиск runtime venv. См. TODO 6.1.

### 4.2. Пять environments в installs — риск средний

/mnt/ai-ssd/hermes/installs/21af0c3aa8d717d2/environments/
├── ed3139373ef640ef8b949dab5c0b18a3/
├── 5915f6ea179440c0a0c43155b99b9a42/
├── 112f294d43d2476994ad349def95ea8b/
├── 6773136bae1c4b82b7f1d5323b5d0e54/
└── 661225cb695e4e36a685ccf3aa8792d9/   ← сюда ставили NumPy

Неизвестно, какой из них активный у gateway. Проверить:
GW_PID=$(systemctl --user show hermes-gateway-469b1f3f.service -p MainPID --value)
readlink -f /proc/$GW_PID/exe
tr '\0' ' ' < /proc/$GW_PID/cmdline

Если путь указывает не на 661225cb... — NumPy ставить в тот, что у gateway.

### 4.3. PM out of sync

hermes memory --help предупреждает:
install out of sync (ffmpeg: not installed or outdated;
ripgrep: not installed or outdated; venv: out of sync with uv.lock)
— run `hermes pm install`

Не блокер для CP-008. Разбирать в техокне (CDN 403 — DEC-013).

### 4.4. WAL warnings

hermes doctor предупреждает про state.db, kanban.db, projects.db в WAL.
Не критично. Требует остановки всех процессов Hermes для offline-конвертации.

### 4.5. source-completion-pending

Файл: /mnt/ai-ssd/hermes/installs/21af0c3aa8d717d2/source-completion-pending (32 байта, 12:51).

Не выяснено. Возможно — маркер незавершённой синхронизации PM. Смотреть в техокне.

---

## 5. Точка возврата (rollback)

### 5.1. Отключить внешний провайдер (остаться на built-in)

export HERMES_HOME=/mnt/ai-ssd/hermes
source "$HERMES_HOME/hermes-agent/venv/bin/activate"
hermes memory off
hermes gateway restart

После этого: работает built-in memory (MEMORY.md / USER.md).
Holographic отключён. Семантический поиск по фактам — недоступен,
но агент жив и базовые функции памяти работают.

Внимание: built-in всегда активен — его «включить» нельзя. memory off
отключает только внешний провайдер.

### 5.2. Восстановить БД из бэкапа

cp /mnt/ai-ssd/hermes/memory_store.db.bak /mnt/ai-ssd/hermes/memory_store.db

### 5.3. Вернуть provider = holographic

hermes memory setup   # интерактивно выбрать holographic
# или вручную: config.yaml → memory.provider: holographic
hermes gateway restart

### 5.4. Убрать ensure-hrr-numpy из systemd

rm ~/.config/systemd/user/hermes-gateway-469b1f3f.service.d/ensure-hrr-numpy.conf
systemctl --user daemon-reload
hermes gateway restart

---

## 6. TODO для техокна

### 6.1. Динамический поиск runtime venv (правильное решение)

Заменить хардкод в ensure-hrr-numpy на эвристику:
1. Явно заданный HERMES_RUNTIME_VENV (если PM начнёт давать).
2. Поиск в installs/*/environments/*/venv/bin/python, фильтр — живой python.
3. Если один — взять.
4. Если несколько — проверить через MainPID gateway (readlink /proc/PID/exe).
5. Если не нашли — exit 0 с warning (gateway важнее HRR).

Правило: агент > HRR.

### 6.2. Починить PM

hermes pm install --tools-only         # поставить ffmpeg / ripgrep
# если 403 — apt install ffmpeg ripgrep, потом hermes pm doctor
hermes pm repair                        # с бэкапами!
hermes pm install --extra all --extra telegram --extra audio-io

Или свой holographic extra в pyproject.toml (правильный долгосрочный путь).

### 6.3. Upstream issue

plugins/memory/holographic.py не использует pm.ensure_import — архитектурный gap.
Завести issue в NousResearch/hermes-agent.

### 6.4. Offline WAL-конвертация

Остановить все процессы Hermes, конвертировать state.db, kanban.db,
projects.db в journal_mode=delete, запустить обратно.

### 6.5. Разобрать source-completion-pending

Посмотреть, что это за маркер, кто его создаёт, зачем.

---

## 7. Ссылки

- Hermes docs: https://hermes-agent.nousresearch.com/docs
- Hermes repo: https://github.com/NousResearch/hermes-agent
- Наш проект: https://github.com/artemfire1980/hermes-titan
- DECISIONS: docs/DECISIONS.md (DEC-023…DEC-027)
- Связанные DEC: DEC-023 (built-in only — отменено), DEC-024 (Hindsight отклонён),
  DEC-025 (Holographic выбран), DEC-026 (Holographic принят с ограничениями),
  DEC-027 (NumPy в runtime venv).

---

Конец документа.
