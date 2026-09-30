#!/usr/bin/env python3
"""Unit-тесты для ConflictDetector"""

from research_runner import ConflictDetector, Evidence


def test_conflict_detector_same_metric():
    """Тест: одинаковые метрики с разными значениями должны создавать конфликт"""
    ev1 = Evidence(
        claim="Рынок вырос на 20%",
        metric="growth_rate",
        value=20.0,
        value_raw="20%",
        year=2024,
        market_scope="глобальный рынок",
        geography="глобальный",
        source_url="https://source1.com",
        source_title="Source 1",
        source_authority=0.8,
    )

    ev2 = Evidence(
        claim="Рынок вырос на 25%",
        metric="growth_rate",
        value=25.0,
        value_raw="25%",
        year=2024,
        market_scope="глобальный рынок",
        geography="глобальный",
        source_url="https://source2.com",
        source_title="Source 2",
        source_authority=0.7,
    )

    conflicts = ConflictDetector.detect([ev1, ev2])
    assert len(conflicts) > 0, "Должен быть обнаружен конфликт"
    assert conflicts[0].type in ["DIRECT_CONFLICT", "SCOPE_DIFF"], (
        f"Неверный тип конфликта: {conflicts[0].type}"
    )
    print("✅ test_conflict_detector_same_metric пройден")


def test_conflict_detector_no_conflict():
    """Тест: одинаковые значения не должны создавать конфликт"""
    ev1 = Evidence(
        claim="Рынок $19.7 млрд",
        metric="market_size",
        value=19.7,
        value_raw="$19.7 млрд",
        year=2024,
        market_scope="глобальный",
        geography="глобальный",
        source_url="https://source1.com",
        source_title="Source 1",
        source_authority=0.8,
    )

    ev2 = Evidence(
        claim="Рынок $19.7 млрд",
        metric="market_size",
        value=19.7,
        value_raw="$19.7 млрд",
        year=2024,
        market_scope="глобальный",
        geography="глобальный",
        source_url="https://source2.com",
        source_title="Source 2",
        source_authority=0.7,
    )

    conflicts = ConflictDetector.detect([ev1, ev2])
    assert len(conflicts) == 0, f"Не должно быть конфликтов, найдено: {len(conflicts)}"
    print("✅ test_conflict_detector_no_conflict пройден")


def test_conflict_detector_time_diff():
    """Тест: разные годы должны создавать TIME_DIFF конфликт"""
    ev1 = Evidence(
        claim="Рынок $16 млрд в 2025",
        metric="market_size",
        value=16.0,
        value_raw="$16 млрд",
        year=2025,
        market_scope="глобальный",
        geography="глобальный",
        source_url="https://source1.com",
        source_title="Source 1",
        source_authority=0.8,
    )

    ev2 = Evidence(
        claim="Рынок $35 млрд в 2030",
        metric="market_size",
        value=35.0,
        value_raw="$35 млрд",
        year=2030,
        market_scope="глобальный",
        geography="глобальный",
        source_url="https://source2.com",
        source_title="Source 2",
        source_authority=0.7,
    )

    conflicts = ConflictDetector.detect([ev1, ev2])
    assert len(conflicts) > 0, "Должен быть обнаружен TIME_DIFF конфликт"
    assert conflicts[0].type == "TIME_DIFF", f"Ожидался TIME_DIFF, получен: {conflicts[0].type}"
    print("✅ test_conflict_detector_time_diff пройден")


if __name__ == "__main__":
    print("=== Запуск unit-тестов ConflictDetector ===\n")
    test_conflict_detector_same_metric()
    test_conflict_detector_no_conflict()
    test_conflict_detector_time_diff()
    print("\n✅ Все тесты ConflictDetector пройдены!")
