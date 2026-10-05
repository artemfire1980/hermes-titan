# Local skills

> Наши skills (local, созданы вручную или Hermes curator).
> Обновлено: 2026-10-05.

## Наши (ручные)

| Skill | Строк | Путь | Назначение |
|-------|-------|------|------------|
| **`mail`** | 52 | `skills/email/mail/SKILL.md` | Read-only почта Mail.ru через MCP `rubit-mcp-mail` |
| **`kiln-safety`** | 106 | `skills/printing/kiln-safety/SKILL.md` | Human-in-the-loop для Kiln MCP (read vs write) |
| **`kiln-printer`** | 130 | `skills/printing/kiln-printer/SKILL.md` | Read-only мониторинг 3D-принтера ZAV |
| **`kiln-analyze`** | 102 | `skills/printing/kiln-analyze/SKILL.md` | Анализ конфигов, логов, тестов (без изменений) |
| **`moysklad-workflow`** | 633 | `skills/research/moysklad-workflow/SKILL.md` | Полный справочник полей МойСклад |
| **`moysklad-query`** | 82 | `skills/research/moysklad-query/SKILL.md` | Компактный workflow для МойСклад |

## Созданы curator (Hermes auto)

| Skill | Автор | Создан | Назначение |
|-------|-------|--------|------------|
| **`voice-transcription`** | user | 2026-10-03 | Транскрипция голосовых (faster-whisper) |
| **`industry-event-research`** | hermes-agent | 2026-09-29 | Поиск выставок, trade fairs |

## Что делает curator

**Hermes curator** — автоматическая система:
- **Создаёт** skills по evidence (session_id).
- **Патчит** их на основе новых данных.
- **Логирует** в `.curator_ledger.jsonl`.

**Правило:** curator-created skills **ценные** — не удалять бездумно.

## Использование

### МойСклад
- **`moysklad-query`** — быстрый справочник (1000-объектный pitfall).
- **`moysklad-workflow`** — полный справочник (33 dictionary + 47 document + 17 report).

### Kiln (3D-принтер)
- **`kiln-safety`** — правила (обязательно).
- **`kiln-printer`** — read-only мониторинг.
- **`kiln-analyze`** — анализ конфигов и логов.

### Почта
- **`mail`** — read-only (5 tools).
- **`voice-transcription`** — транскрипция голосовых.

### Research
- **`industry-event-research`** — выставки, trade fairs.

## Правила

- **`kiln-safety`** — **обязателен** перед любым WRITE/EXECUTE для принтера.
- **Read-only по умолчанию** — write только с подтверждением (см. `docs/SECURITY.md`).
- **Не править curator skills** — curator сам обновит.
- **Не дублировать** — использовать `moysklad-query` для быстрых запросов, `moysklad-workflow` — для поиска полей.

## Ссылки

- `docs/MOYSKLAD.md` — инструкция MCP.
- `docs/KILN.md` — инструкция Kiln.
- `docs/MAIL.md` — инструкция почты.
- `docs/SECURITY.md` — правила безопасности.
