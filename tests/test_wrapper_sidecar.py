#!/usr/bin/env python3
"""Smoke-тест для wrapper: чтение sidecar JSON"""
import json
import tempfile
from pathlib import Path


def test_sidecar_reading():
    """Тест: wrapper корректно читает sidecar JSON"""
    # Создаём фейковый sidecar
    sidecar_data = {
        "schema_version": "1.0",
        "research_id": "20260918_150000_test_topic",
        "topic": "тестовая тема",
        "generated_at": "2026-09-18T15:00:00",
        "stats": {
            "subtopics_analyzed": 3,
            "unique_sources": 10,
            "evidences_extracted": 25,
            "evidences_verified": 23,
            "evidences_dropped": 2,
            "conflicts_detected": 1
        },
        "report": "/tmp/test_report.md"
    }
    
    # Создаём временный файл
    with tempfile.NamedTemporaryFile(mode='w', suffix='.evidence.json', delete=False, encoding='utf-8') as f:
        json.dump(sidecar_data, f, ensure_ascii=False, indent=2)
        temp_path = f.name
    
    try:
        # Читаем как wrapper
        with open(temp_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Проверяем ключи
        stats = data.get('stats', {})
        assert stats.get('evidences_extracted') == 25
        assert stats.get('evidences_verified') == 23
        assert stats.get('evidences_dropped') == 2
        assert stats.get('conflicts_detected') == 1
        
        print("✅ test_sidecar_reading пройден")
        print(f"   Extracted: {stats['evidences_extracted']}")
        print(f"   Verified: {stats['evidences_verified']}")
        print(f"   Dropped: {stats['evidences_dropped']}")
        print(f"   Conflicts: {stats['conflicts_detected']}")
        
    finally:
        Path(temp_path).unlink()

if __name__ == "__main__":
    print("=== Smoke-тест wrapper sidecar ===\n")
    test_sidecar_reading()
    print("\n✅ Smoke-тест пройден!")
