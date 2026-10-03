# HERMES-TITAN — Workflow: внедрение плагина/фичи

> Как агент обрабатывает задачу «внедри X» из Telegram.
> Обновлено: 2026-10-03.

## 1. Приём задачи

Ты пишешь в Telegram: **«внедри X»** или **«сделай Y»**.

Gateway (PID 10911) принимает → агент собирает контекст:
- `SOUL.md` (тон) + `MEMORY.md` (gotchas) + `USER.md` (профиль).
- Toolsets Telegram: `web`, `terminal`, `file`, `image_gen`, `skills`, `todo`, `memory`, `session_search`, `connections`, `clarify`, `delegation`, `cronjob`, `kanban`.
- Может вызывать: `terminal`, `web_search`, `web_extract`, `file`, `kanban`, `skills`, `delegation`.

## 2. Поиск готового решения (обязательно первым)

**Порядок поиска:**

1. **Skills Hub** — 1826 скиллов (152 official Nous):

       hermes skills browse
       hermes skills search <ключ>

2. **Official plugins** Hermes:

       hermes plugins list
       hermes mcp catalog

3. **Web + GitHub** — через `web_search` (SearXNG) + `web_extract` (Exa):

       найдите на GitHub плагин/библиотеку для <задача>

**Что искать:**
- Готовый плагин Hermes.
- MCP-сервер.
- Python-библиотеку (pip).
- Готовый скрипт.

**Если ничего нет** → секция 5 (план создания).

## 3. Анализ найденного

**Критерии оценки:**

| Критерий | Что смотреть |
|----------|--------------|
| **Популярность** | GitHub stars, forks, downloads (PyPI/npm), дата последнего коммита |
| **Функционал** | Что делает, какие зависимости, размер |
| **Совместимость** | ARM64, Python 3.12, Ubuntu 24.04, без systemd-конфликтов |
| **Лицензия** | MIT/Apache/BSD — ок; GPL — проверить; проприетарные — отказ |
| **Активность** | Последний коммит < 1 года, issues отвечают |
| **Документация** | README, примеры, API |

**Что делать:**
- Сравнить 2–3 варианта.
- Аргументировать выбор (почему этот, а не другой).

## 4. Проверка безопасности (обязательно)

**Перед внедрением — проверить код:**

| Риск | Что искать |
|------|-----------|
| **Сетевые запросы** | `requests`, `urllib`, `curl`, `wget` к неизвестным доменам |
| **Запись в системные пути** | `/etc`, `/usr`, `/bin`, `~/.ssh`, `~/.config/systemd` |
| **Доступ к секретам** | `.env`, `~/.ssh`, токены, `id_rsa` |
| **Опасные команды** | `sudo`, `rm -rf /`, `curl \| bash`, `eval`, `exec` |
| **Обфускация** | base64-строки, hex-код, `marshal.loads`, `pickle.loads` |
| **Телеметрия** | Отправка данных на внешние серверы (не-официальные) |
| **Backdoors** | Скрытые порты, reverse shell, `nc -l`, `socat` |
| **Зависимости** | `pip install` цепочки с подозрительными пакетами |

**Если подозрительно:**
- **Остановиться.**
- Объяснить, что именно насторожило.
- **Не внедрять.**
- Предложить безопасную альтернативу.

**Если код чист:**
- Продолжить внедрение.

**Инструменты проверки:**
- `gitleaks` — в pre-commit и CI.
- `grep -rE "curl\|wget\|requests\|urllib"` — быстрый поиск сетевых вызовов.
- `bash scripts/selfcheck.sh` — включает gitleaks.

## 5. Если готового нет — план создания

**Принцип: модульность.**

- Разбить задачу на **маленькие модули** (1 модуль = 1 функция).
- Каждый модуль **тестируемый отдельно**.
- Не создавать «монолит».
- Использовать `docs/CODE_EDITING_RULES.md` для методов.

**План должен содержать:**
1. Что делаем (цель).
2. Какие модули (список).
3. Какие зависимости (если нужны).
4. Как проверить (тесты, smoke).
5. Как откатить (git reset, бэкап).

## 6. Внедрение

**Через Aider:**

    python3 scripts/aider_runner.py <project> '<task>'

**Что происходит:**
- Aider запускается в `~/ai-system/projects/<project>/`.
- Читает `docs/CONVENTIONS.md` (стиль, workflow, запреты).
- Работает изолированно — не трогает `~/ai-system/scripts`, `docs`, конфиги Hermes.
- Модель: NVIDIA NIM Ultra (DEC-020).

**Через Kanban** (для сложных задач):

    hermes kanban create "<title>" --body "<описание>" --workspace dir:/mnt/ai-ssd/ai-system/projects/<project>

Dispatcher (тик 60 сек) подхватит → запустит Aider → результат в лог.
Мониторинг: `hermes kanban list`, `hermes kanban show <task-id>`.

**Лимит параллелизма:** `kanban.max_in_progress: 2` (DEC-050).

## 7. Проверка

**Обязательно перед коммитом:**

    bash scripts/selfcheck.sh

**Что делает:**
1. Python syntax (все `.py`).
2. Bash syntax (все `.sh`).
3. `ruff` — статический анализ.
4. `pytest` — тесты.
5. `gitleaks` — проверка секретов.
6. Smoke-тесты (FORBIDDEN_ROOTS, NVIDIA key, drop_total).
7. Consistency check (drift).

**Exit 0** — всё ок. **Exit 1** — фиксить.

## 8. Коммит, пуш, документация

**Коммит:**

    git add <files>
    git commit -m "<type>(<scope>): <описание>"
    git push origin main

**Типы:** `feat`, `fix`, `docs`, `chore`, `refactor`, `test`.

**Автоматически** — `scripts/git-auto-push.sh` (cron, раз в 6 часов).

**Обновление документации (обязательно):**

| Что | Куда |
|-----|------|
| Новый DEC (архитектурное решение) | `DECISIONS.md` + README + `docs/INDEX.md` |
| История изменений | `CHANGELOG.md` секция `[Unreleased]` |
| Текущее состояние | `docs/PROJECT-STATE.md` раздел `Last completed` |
| Consistency | `bash scripts/check_consistency.sh` |

**Порядок для нового DEC:**
1. Добавить `## DEC-NNN: Title`.
2. Обновить README (`<N> решений`, диапазон).
3. `python3 scripts/checks/check_dec_index.py` — регенерировать INDEX.
4. `bash scripts/check_consistency.sh` — проверить.

## 9. Пример: «внедри плагин X»

1. **Ты пишешь в Telegram:** «внедри плагин X».
2. **Агент ищет:** `hermes skills search X`, `web_search "X hermes plugin github"`.
3. **Анализ:** 3 варианта, выбирает лучший (звёзды, активность, лицензия).
4. **Проверка безопасности:** `grep -rE "curl|wget|requests"` + глазами.
5. **Решение:**
   - Есть готовый плагин → `hermes plugins install X`.
   - Нет → план + Aider.
6. **Внедрение:** Aider правит код в `projects/<x>/`.
7. **Проверка:** `bash scripts/selfcheck.sh`.
8. **Коммит/пуш:** автоматически или вручную.
9. **Документация:** DEC (если решение архитектурное) + CHANGELOG + PROJECT-STATE.
10. **Ответ в Telegram:** «Готово. Что сделано, что проверено, что осталось».

## 10. Быстрая шпаргалка

| Шаг | Команда |
|-----|---------|
| Поиск скилла | `hermes skills search <ключ>` |
| Поиск плагина | `hermes plugins list` |
| Анализ веб | `web_search` + `web_extract` |
| Внедрение через Aider | `python3 scripts/aider_runner.py <project> '<task>'` |
| Через Kanban | `hermes kanban create "<title>" --workspace dir:...` |
| Проверка | `bash scripts/selfcheck.sh` |
| Consistency | `bash scripts/check_consistency.sh` |
| Коммит | `git add ... && git commit -m "..." && git push` |
| INDEX DEC | `python3 scripts/checks/check_dec_index.py` |

## 11. Ссылки

- `docs/MAINTENANCE.md` — поддержка системы.
- `docs/PROJECT-MAP.md` — навигация.
- `docs/PROJECT-STATE.md` — состояние.
- `docs/CONVENTIONS.md` — правила Aider.
- `docs/OPERATIONS.md` — справочник команд.
- `DECISIONS.md` — архитектурные решения.
