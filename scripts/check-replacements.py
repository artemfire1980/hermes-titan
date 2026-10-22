#!/usr/bin/env python3
"""Анализ: что нового в Hermes (OLD..NEW) vs наши плагины.
Read-only: git log, без Hermes/uv. Использование: check-replacements.py [OLD] [NEW]"""

import subprocess
import sys
from pathlib import Path

REPO = Path("/mnt/ai-ssd/hermes/hermes-agent")
OUR_PLUGINS = ["holographic", "progressive-skill"]
KEYWORDS = [
    "leaving core",
    "moved to core",
    "holographic",
    "memory provider",
    "built-in",
    "plugin-catalog: add",
    "leaving the core",
]


def git_log(old, new):
    r = subprocess.run(
        ["git", "-C", str(REPO), "log", "--oneline", f"{old}..{new}"],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    return r.stdout.splitlines() if r.returncode == 0 else []


def main():
    old = sys.argv[1] if len(sys.argv) > 1 else "v0.22.2"
    new = sys.argv[2] if len(sys.argv) > 2 else "v0.22.4"
    lines = git_log(old, new)
    print(f"=== {old}..{new}: {len(lines)} коммитов ===")

    hits = [ln for ln in lines if any(k.lower() in ln.lower() for k in KEYWORDS)]
    print(f"\n=== ключевые ({len(hits)}) ===")
    for h in hits:
        print(" ", h)

    # leaving core → plugins
    leaving = [h for h in hits if "leaving core" in h.lower() or "leaving the core" in h.lower()]
    if leaving:
        print("\n⚠️ Функциональность выходит из ядра → ставь плагин:")
        for l in leaving:
            print("  -", l)

    # наши плагины
    print("\n=== наши плагины ===")
    for p in OUR_PLUGINS:
        touched = [h for h in lines if p.lower() in h.lower()]
        if touched:
            print(f"⚠️ {p}: затронут ({len(touched)}):")
            for t in touched[:5]:
                print("   ", t)
        else:
            print(f"✅ {p}: не тронут")

    # moved to core → можно удалить плагин
    moved = [h for h in hits if "moved to core" in h.lower()]
    if moved:
        print("\n⚠️ Переехало в ядро → плагин можно удалить:")
        for m in moved:
            print("  -", m)


if __name__ == "__main__":
    main()
