#!/usr/bin/env python3
"""Проверяет уникальность и непрерывность DEC в DECISIONS.md.

Порядок DEC — хронологический (не нумерованный), поэтому НЕ проверяется.

Exit 0 — нет дублей и пропусков.
Exit 1 — есть дубли или пропуски.
"""

import re
import sys
from collections import Counter
from pathlib import Path


def main() -> int:
    repo = Path(__file__).resolve().parent.parent.parent
    dec_file = repo / "DECISIONS.md"
    if not dec_file.exists():
        print(f"❌ {dec_file} не найден")
        return 1

    src = dec_file.read_text(encoding="utf-8")
    nums = [int(m.group(1)) for m in re.finditer(r"^## DEC-(\d+)", src, re.MULTILINE)]

    if not nums:
        print("❌ DEC не найдены")
        return 1

    errors = 0

    # Дубли
    dups = [n for n, c in Counter(nums).items() if c > 1]
    if dups:
        print(f"❌ Дубли DEC: {sorted(dups)}")
        errors += 1

    # Пропуски (между min и max)
    full = set(range(min(nums), max(nums) + 1))
    missing = sorted(full - set(nums))
    if missing:
        print(f"❌ Пропуски DEC: {missing}")
        errors += 1

    if errors == 0:
        print(
            f"✅ DEC ок: {len(nums)} шт, диапазон DEC-{min(nums):03d}…DEC-{max(nums):03d}, без дублей и пропусков"
        )
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
