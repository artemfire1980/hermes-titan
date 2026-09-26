# Решения

## DEC-001: Переустановка начисто

Обоснование: накопленный долг старой системы.
Откат: расшифровать `pre-wipe-staging/vim4_golden_snapshot.7z` (архив зашифрован, пароль отдельно).

## DEC-002: Проект на SSD, симлинк в home

Обоснование: защита eMMC от переполнения.
Откат: перенести обратно.

## DEC-003: Ядро в минимальной комплектации (Blank Slate)

Обоснование: осознанное включение возможностей.
Откат: перенастроить.

## DEC-004: FreeLLMAPI — обязательный компонент

Обоснование: агрегатор бесплатных тиров с адаптивным роутингом, чего нет в штатном подборе моделей.
Откат: переключиться на штатный подбор.

## DEC-005: SearXNG — обязательный компонент

Обоснование: приватный метапоиск, штатная интеграция в Hermes.
Откат: переключиться на другой веб-бэкенд.

## DEC-006: ctx7 в режиме CLI+Skills (не MCP)

Обоснование: переиспользуем terminal tool Hermes, избегаем лишнего слоя MCP.
Откат: `ctx7 setup --mcp`.

## DEC-007: FreeLLMAPI образ — проверка нескольких источников

Обоснование: ghcr.io может не иметь ARM64 manifest.
Откат: сборка из исходников.

## DEC-008: fstab по UUID, не LABEL

Обоснование: UUID стабильнее при переименовании.
Запись: `UUID=dbf51535-... /mnt/ai-ssd ext4 defaults,noatime,nofail,x-systemd.device-timeout=10 0 2`.
Проверено: переживает ребут.

## DEC-009: Бэкап старой системы зашифрован

Обнаружено при аудите: `vim4_golden_snapshot.7z` требует пароль.
Следствие для CP-005: пароль вводится интерактивно, не хранится в проекте.

## DEC-010: `hermes pm repair` — обязательный шаг после установки из исходников

Обоснование: `pip install -e .` не ставит все зависимости в PM-окружение Hermes.
Симптом: `venv_is_current=False` → бесконечный цикл `source-update completion failed`.
Решение: `hermes pm repair` — восстанавливает committed-окружение.
Источник: issue #122425 (upstream).

## DEC-011: systemd-юнит обновляется через `hermes setup` / `hermes gateway setup`

Обоснование: после ручного создания юнита он может быть устаревшим.
Симптом: `⚠ Installed gateway service definition is outdated`.
Решение: `hermes setup` или `hermes gateway restart` — автоматически обновляют unit.

## DEC-012: PM сам управляет зависимостями платформ

Обоснование: python-telegram-bot был поставлен в venv вручную, но PM использует свой Python.
Симптом: `Platform 'Telegram' dependencies missing — attempting install...`.
Решение: PM auto-install зависимостей; не ставить пакеты в hermes-agent/venv вручную.

## DEC-013: CDN Nous 403 — ffmpeg/ripgrep/PM artifacts недоступны

Обоснование: `hermes-assets.nousresearch.com` отдаёт 403 Forbidden.
Симптом: `⚠ install out of sync (ffmpeg, ripgrep)`.
Влияние: на работу не влияет — gateway, Telegram, модель работают.
Решение: игнорировать до фикса upstream. При необходимости — ручная установка.

## DEC-014: SearXNG через Docker, подключён к Hermes

Обоснование: приватный метапоиск, штатная интеграция Hermes.
Развёртывание: `/mnt/ai-ssd/searxng/` (Docker Compose), порт `127.0.0.1:8888`.
Конфиг: `web.search_backend=searxng`, `web.searxng_url=http://127.0.0.1:8888`.
Секрет: `SEARXNG_SECRET` в `.env` (права 600).
Тест: поиск "bitcoin price today" — успешно через SearXNG.

## DEC-015: FreeLLMAPI база восстановлена из старого `freeapi.db`

Обоснование: 77 ключей провайдеров, 314 моделей — восстановлены без пересоздания.
Путь: `/mnt/ai-ssd/freellmapi/` (Docker Compose), порт `127.0.0.1:3001`.
Доступ: `https://khadas.taila31870.ts.net` (Tailscale Serve).
Ключ шифрования: `ENCRYPTION_KEY` в `.env` (права 400).
