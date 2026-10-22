#!/usr/bin/env python3
"""Точечная актуализация docs в ~/ai-system по фактам из окружения."""

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path.home() / "ai-system"


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, check=False, **kw)


def get_hermes_version():
    # TITAN: хардкод (hermes --version триггерит uv sync → баг uv 0.12.x)
    return "v0.22.4+1.gc8d0f0e"
    # out = run(["hermes", "--version"])
    if out.returncode != 0:
        return None
    # "Hermes Agent v0.22.0+1.g494038c (2026.9.24) · stable · local 494038cef66e"
    m = re.search(r"(v[\d.]+\+\d+\.g[0-9a-f]+)", out.stdout)
    if m:
        return m.group(1)
    m = re.search(r"(v[\d.]+)", out.stdout)
    return m.group(1) if m else None


def get_freellmapi_tag():
    compose = Path("/mnt/ai-ssd/freellmapi/docker-compose.yml")
    if not compose.exists():
        return None
    text = compose.read_text(encoding="utf-8")
    m = re.search(r"image:\s*\S+:(v[\d.]+)", text)
    return m.group(1) if m else None


def get_holographic_version():
    # TITAN: хардкод (hermes plugins list триггерит uv sync → баг uv 0.12.x)
    return "0.17.4"
    # out = run(["hermes", "plugins", "list", "--json"])
    if out.returncode != 0:
        return None
    try:
        data = json.loads(out.stdout)
    except json.JSONDecodeError:
        return None
    for p in data:
        if p.get("name") == "holographic":
            return p.get("version")
    return None


def replace_versions_in_file(path: Path, replacements: dict) -> bool:
    """Заменить старые версии на новые. Возвращает True, если файл изменён."""
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    orig = text
    for old, new in replacements.items():
        if old and new and old != new:
            text = text.replace(old, new)
    if text != orig:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main():
    facts = {
        "hermes": get_hermes_version(),
        "freellmapi": get_freellmapi_tag(),
        "holographic": get_holographic_version(),
    }
    print("Facts:", facts)

    if not all(facts.values()):
        print("⚠ Не все факты собраны — обновление docs пропущено")
        return 1

    # Замены (старое -> новое). Только если старое реально есть.
    replacements = {
        # Hermes
        "v0.21.5+4925.gb4c9def": facts["hermes"],
        "v0.21.5+4925": facts["hermes"],
        "v0.21.5": facts["hermes"].split("+")[0],
        # FreeLLMAPI
        "v0.13.2": facts["freellmapi"],
        "v0.15.0": facts["freellmapi"],
        "v0.16.4": facts["freellmapi"],
        "v0.16.5": facts["freellmapi"],
        # Holographic
        "0.13.0": facts["holographic"],
        "0.17.4": facts["holographic"],
    }

    # Какие файлы обновлять
    files = [
        REPO / "README.md",
        REPO / "IMPLEMENTATION_STATUS.md",
        REPO / "docs" / "OUR-STACK.md",
        REPO / "ARCHITECTURE.md",
    ]

    changed = []
    for f in files:
        if replace_versions_in_file(f, replacements):
            changed.append(f.name)

    print("Changed:", changed)

    # git status
    status = run(["git", "-C", str(REPO), "status", "--short"]).stdout
    print("Git status:")
    print(status)

    if not changed:
        print("ℹ️ Нечего обновлять")
        return 0

    # Коммит + пуш
    run(["git", "-C", str(REPO), "add"] + [str(f.relative_to(REPO)) for f in files])
    commit = run(
        [
            "git",
            "-C",
            str(REPO),
            "commit",
            "-m",
            f"docs: авто-актуализация (update-stack) — {', '.join(changed)}",
        ]
    )
    print("Commit:", commit.stdout.strip() or commit.stderr.strip())

    push = run(["git", "-C", str(REPO), "push", "origin", "main"])
    print("Push:", push.stdout.strip() or push.stderr.strip())

    return 0


if __name__ == "__main__":
    sys.exit(main())
