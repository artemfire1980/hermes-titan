"""Конфигурация pytest для Hermes-Titan.

Добавляет scripts/ в sys.path, чтобы research_runner.py мог
импортировать summary_generator и другие локальные модули.
"""
import sys
from pathlib import Path

# Корень проекта = родитель tests/
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# Добавляем scripts/ в начало sys.path
for p in (PROJECT_ROOT, SCRIPTS_DIR):
    p_str = str(p)
    if p_str not in sys.path:
        sys.path.insert(0, p_str)
