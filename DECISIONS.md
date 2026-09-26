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
