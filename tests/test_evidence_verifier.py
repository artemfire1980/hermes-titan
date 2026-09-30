#!/usr/bin/env python3
"""Unit-тесты для EvidenceVerifier"""

from research_runner import EvidenceVerifier


def test_evidence_verifier_exact_match():
    """Тест: точное совпадение текста"""
    evidence_text = "Рынок вырос на 22.3% в 2024 году"
    doc_text = "Согласно отчету, рынок вырос на 22.3% в 2024 году благодаря новым технологиям."

    ok, method, score = EvidenceVerifier.verify(evidence_text, doc_text)
    assert ok == True, "Должно быть верифицировано"
    assert method in ["exact", "fuzzy"], f"Неверный метод: {method}"
    assert score >= 0.7, f"Слишком низкий score: {score}"
    print("✅ test_evidence_verifier_exact_match пройден")


def test_evidence_verifier_fuzzy_match():
    """Тест: нечёткое совпадение (опечатки, перефразирование)"""
    evidence_text = "Объем рынка составил 19.7 миллиардов долларов"
    doc_text = "Общий объем рынка достиг 19,7 млрд долларов в отчетном периоде."

    ok, method, score = EvidenceVerifier.verify(evidence_text, doc_text)
    assert ok == True, "Должно быть верифицировано нечётким совпадением"
    assert method == "fuzzy", f"Ожидался fuzzy метод, получен: {method}"
    print("✅ test_evidence_verifier_fuzzy_match пройден")


def test_evidence_verifier_no_match():
    """Тест: отсутствие совпадения"""
    evidence_text = "Компания Apple выпустила новый iPhone"
    doc_text = "Рынок 3D-принтеров демонстрирует устойчивый рост в течение последних лет."

    ok, method, score = EvidenceVerifier.verify(evidence_text, doc_text)
    assert ok == False, "Не должно быть верифицировано"
    assert score < 0.5, f"Слишком высокий score для несовпадения: {score}"
    print("✅ test_evidence_verifier_no_match пройден")


def test_evidence_verifier_numbers():
    """Тест: числа должны корректно сравниваться"""
    evidence_text = "CAGR составил 22.3%"
    doc_text = "Совокупный годовой темп роста (CAGR) равен 22,3 процента за период 2020-2024."

    ok, method, score = EvidenceVerifier.verify(evidence_text, doc_text)
    assert ok == True, "Числа должны быть верифицированы"
    print("✅ test_evidence_verifier_numbers пройден")


if __name__ == "__main__":
    print("=== Запуск unit-тестов EvidenceVerifier ===\n")
    test_evidence_verifier_exact_match()
    test_evidence_verifier_fuzzy_match()
    test_evidence_verifier_no_match()
    test_evidence_verifier_numbers()
    print("\n✅ Все тесты EvidenceVerifier пройдены!")
