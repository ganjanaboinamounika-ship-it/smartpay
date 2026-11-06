from decimal import Decimal

from app.fraud_engine.rules import (
    check_high_amount,
    check_velocity,
    check_new_device,
    check_unusual_location,
)
from app.fraud_engine.engine import evaluate_payment


def test_high_amount_rule_triggered():
    result = check_high_amount(Decimal("100000"))

    assert result.triggered is True
    assert result.score == 30
    assert result.rule == "HIGH_AMOUNT"


def test_high_amount_rule_not_triggered():
    result = check_high_amount(Decimal("99999"))

    assert result.triggered is False
    assert result.score == 0


def test_velocity_rule_triggered():
    result = check_velocity(6)

    assert result.triggered is True
    assert result.score == 25


def test_velocity_rule_not_triggered():
    result = check_velocity(5)

    assert result.triggered is False
    assert result.score == 0


def test_new_device_rule_triggered():
    result = check_new_device(True)

    assert result.triggered is True
    assert result.score == 15


def test_known_device_rule_not_triggered():
    result = check_new_device(False)

    assert result.triggered is False
    assert result.score == 0


def test_unusual_location_rule_triggered():
    result = check_unusual_location(True)

    assert result.triggered is True
    assert result.score == 20


def test_normal_location_rule_not_triggered():
    result = check_unusual_location(False)

    assert result.triggered is False
    assert result.score == 0


def test_low_risk_payment():
    result = evaluate_payment(
        amount=Decimal("500"),
        transaction_count=1,
        is_new_device=False,
        is_unusual_location=False,
    )

    assert result.total_score == 0
    assert result.risk_level == "LOW"
    assert len(result.triggered_rules) == 0


def test_medium_risk_payment():
    result = evaluate_payment(
        amount=Decimal("100000"),
        transaction_count=1,
        is_new_device=False,
        is_unusual_location=False,
    )

    assert result.total_score == 30
    assert result.risk_level == "MEDIUM"
    assert len(result.triggered_rules) == 1


def test_high_risk_payment():
    result = evaluate_payment(
        amount=Decimal("100000"),
        transaction_count=6,
        is_new_device=True,
        is_unusual_location=True,
    )

    assert result.total_score == 90
    assert result.risk_level == "HIGH"
    assert len(result.triggered_rules) == 4


def test_combined_medium_risk_payment():
    result = evaluate_payment(
        amount=Decimal("100000"),
        transaction_count=1,
        is_new_device=False,
        is_unusual_location=True,
    )

    assert result.total_score == 50
    assert result.risk_level == "MEDIUM"
    assert len(result.triggered_rules) == 2


def test_triggered_rule_names():
    result = evaluate_payment(
        amount=Decimal("100000"),
        transaction_count=6,
        is_new_device=False,
        is_unusual_location=False,
    )

    rule_names = [rule.rule for rule in result.triggered_rules]

    assert "HIGH_AMOUNT" in rule_names
    assert "HIGH_VELOCITY" in rule_names
    assert "NEW_DEVICE" not in rule_names