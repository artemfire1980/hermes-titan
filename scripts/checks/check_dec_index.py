#!/usr/bin/env python3
"""Генерирует docs/INDEX.md из DECISIONS.md.

Без аргументов — генерирует / обновляет docs/INDEX.md.
С --check — проверяет, что docs/INDEX.md актуален (exit 1 при drift).
"""

import re
import sys
from pathlib import Path


def parse_decs(dec_src: str) -> list[tuple[str, str]]:
    """Возвращает [(id, title)] для каждого ## DEC-NNN: title."""
    result = []
    for m in re.finditer(r"^## (DEC-\d+):\s*(.+)$", dec_src, re.MULTILINE):
        result.append((m.group(1), m.group(2).strip()))
    return result


def generate(dec_file: Path) -> str:
    src = dec_file.read_text(encoding="utf-8")
    decs = parse_decs(src)

    lines = [
        "# DEC Index",
        "",
        "> Автогенерируется `scripts/checks/check_dec_index.py`.",
        f"> Источник: `DECISIONS.md` ({len(decs)} записей).",
        "> **Не редактировать вручную.**",
        "",
        "| ID | Заголовок |",
        "|----|-----------|",
    ]
    for dec_id, title in sorted(decs, key=lambda x: int(x[0].split("-")[1])):
        anchor = dec_id.lower()  # GitHub anchor
        lines.append(f"| [{dec_id}](DECISIONS.md#{anchor}) | {title} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    check_mode = "--check" in sys.argv

    repo = Path(__file__).resolve().parent.parent.parent
    dec_file = repo / "DECISIONS.md"
    idx_file = repo / "docs" / "INDEX.md"

    if not dec_file.exists():
        print(f"❌ {dec_file} не найден")
        return 1

    new_content = generate(dec_file)

    if check_mode:
        if not idx_file.exists():
            print(f"❌ {idx_file} отсутствует (запусти без --check для генерации)")
            return 1
        if idx_file.read_text(encoding="utf-8") != new_content:
            print("❌ docs/INDEX.md устарел (запусти без --check для обновления)")
            return 1
        print("✅ docs/INDEX.md актуален")
        return 0

    idx_file.parent.mkdir(parents=True, exist_ok=True)
    idx_file.write_text(new_content, encoding="utf-8")
    count = new_content.count("| [DEC-")
    print(f"✅ docs/INDEX.md обновлён: {count} DEC")
    return 0


if __name__ == "__main__":
    sys.exit(main())
