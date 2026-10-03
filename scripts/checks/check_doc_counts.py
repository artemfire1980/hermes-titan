#!/usr/bin/env python3
"""Проверяет, что README «N архитектурных решений» совпадает с реальным числом DEC.

Exit 0 — совпадает.
Exit 1 — расхождение.
"""

import re
import sys
from pathlib import Path


def main() -> int:
    repo = Path(__file__).resolve().parent.parent.parent
    readme = repo / "README.md"
    dec_file = repo / "DECISIONS.md"

    if not readme.exists() or not dec_file.exists():
        print("❌ README.md или DECISIONS.md не найдены")
        return 1

    # Реальное число DEC
    dec_src = dec_file.read_text(encoding="utf-8")
    real = len(re.findall(r"^## DEC-\d+", dec_src, re.MULTILINE))

    # README заявление
    readme_src = readme.read_text(encoding="utf-8")
    m = re.search(r"(\d+)\s+архитектурных\s+решений", readme_src)
    if not m:
        print("❌ README: не найдена фраза '<N> архитектурных решений'")
        return 1

    claimed = int(m.group(1))

    if claimed == real:
        print(f"✅ README DEC count ок: {claimed} = {real}")
        return 0

    print(f"❌ README: заявлено {claimed} DEC, реально {real}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
