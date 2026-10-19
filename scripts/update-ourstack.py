#!/usr/bin/env python3
"""Обновляет версии в docs/OUR-STACK.md (точечно, с бэкапом).

Использование:
    python3 update-ourstack.py --freellmapi v0.16.5
    python3 update-ourstack.py --holographic 0.17.5 --progressive 3.2.2
    python3 update-ourstack.py --freellmapi v0.16.5 --dry-run
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

DOC = Path.home() / "ai-system" / "docs" / "OUR-STACK.md"


def patch_freellmapi(src: str, version: str) -> tuple[str, int]:
    """Меняет версию FreeLLMAPI в 3 местах. Возвращает (текст, число замен)."""
    n = 0
    # 1) Версия в таблице
    src, k = re.subn(
        r"(\| Версия \| )v[\d.]+( \(фиксированный тег[^|]*\) \|)",
        rf"\g<1>{version}\g<2>",
        src,
    )
    n += k
    # 2) Образ
    src, k = re.subn(
        r"(freellmapi:)v[\d.]+",
        rf"\g<1>{version}",
        src,
    )
    n += k
    # 3) Заголовок changelog
    src, k = re.subn(
        r"(\*\*Что нового в )v[\d.]+(:\*\*)",
        rf"\g<1>{version}\g<2>",
        src,
    )
    n += k
    return src, n


def patch_plugin(src: str, name: str, version: str) -> tuple[str, int]:
    """Меняет версию плагина в таблице."""
    if name == "holographic":
        pat = r"(\| Holographic memory \| community )[\d.]+( \|)"
    elif name == "progressive":
        pat = r"(\| progressive-skill \| )[\d.]+( \| git \|)"
    else:
        raise SystemExit(f"unknown plugin: {name}")
    src, k = re.subn(pat, rf"\g<1>{version}\g<2>", src)
    return src, k


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--freellmapi", help="например v0.16.5")
    ap.add_argument("--holographic", help="например 0.17.5")
    ap.add_argument("--progressive", help="например 3.2.2")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not any([args.freellmapi, args.holographic, args.progressive]):
        ap.error("нужен хотя бы один --freellmapi/--holographic/--progressive")

    if not DOC.exists():
        print(f"ERR: {DOC} not found", file=sys.stderr)
        return 2

    src = DOC.read_text(encoding="utf-8")
    orig = src
    total = 0

    if args.freellmapi:
        if not re.fullmatch(r"v[\d.]+", args.freellmapi):
            print(
                f"ERR: --freellmapi должен быть vX.Y.Z, получил {args.freellmapi!r}",
                file=sys.stderr,
            )
            return 2
        src, n = patch_freellmapi(src, args.freellmapi)
        print(f"FreeLLMAPI -> {args.freellmapi}: {n} замен")
        total += n

    if args.holographic:
        src, n = patch_plugin(src, "holographic", args.holographic)
        print(f"holographic -> {args.holographic}: {n} замен")
        total += n

    if args.progressive:
        src, n = patch_plugin(src, "progressive", args.progressive)
        print(f"progressive-skill -> {args.progressive}: {n} замен")
        total += n

    if total == 0:
        print("no changes (версии уже актуальны?)", file=sys.stderr)
        return 1
    if src == orig:
        print("no changes", file=sys.stderr)
        return 1

    if args.dry_run:
        print("DRY-RUN: не записываю")
        return 0

    # бэкап
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    bak = DOC.with_name(f"OUR-STACK.md.bak.{ts}")
    shutil.copy2(DOC, bak)
    DOC.write_text(src, encoding="utf-8")
    print(f"OK: записано в {DOC} (бэкап: {bak.name})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
