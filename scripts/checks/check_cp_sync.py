#!/usr/bin/env python3
"""Проверяет синхронность CP в README, IMPLEMENTATION_STATUS, PROJECT-STATE.

Берёт последний CP-NNN (по номеру) из каждого файла и сравнивает.

Exit 0 — совпадают.
Exit 1 — расхождение.
"""

import re
import sys
from pathlib import Path


def last_cp(path: Path) -> str | None:
    if not path.exists():
        return None
    src = path.read_text(encoding="utf-8")
    cps = re.findall(r"CP-(\d+)", src)
    if not cps:
        return None
    return f"CP-{max(int(c) for c in cps):03d}"


def main() -> int:
    repo = Path(__file__).resolve().parent.parent.parent

    files = {
        "README.md": repo / "README.md",
        "IMPLEMENTATION_STATUS.md": repo / "IMPLEMENTATION_STATUS.md",
        "docs/PROJECT-STATE.md": repo / "docs" / "PROJECT-STATE.md",
    }

    cps = {name: last_cp(p) for name, p in files.items()}

    # Игнорируем отсутствующие файлы
    present = {n: c for n, c in cps.items() if c is not None}

    if not present:
        print("❌ Не найдено CP ни в одном файле")
        return 1

    unique = set(present.values())
    if len(unique) == 1:
        cp = unique.pop()
        print(f"✅ CP sync ок: {cp} во всех ({len(present)} файлах)")
        return 0

    print("❌ CP расхождение:")
    for name, cp in sorted(present.items()):
        print(f"   {name}: {cp}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
