from dataclasses import dataclass
from decimal import Decimal

from app.fraud_engine.rules import (
    FraudCheckResult,
    check_high_amount,
    check_new_device,
    check_unusual_location,
    check_velocity,
)


@dataclass
class FraudEvaluation:
    total_score: int
    risk_level: str
    triggered_rules: list[FraudCheckResult]


def evaluate_payment(
    amount: Decimal,
    transaction_count: int,
    is_new_device: bool,
    is_unusual_location: bool,
) -> FraudEvaluation:
    """
    Run all fraud rules and calculate the overall risk level.
    """

    results = [
        check_high_amount(amount),
        check_velocity(transaction_count),
        check_new_device(is_new_device),
        check_unusual_location(is_unusual_location),
    ]

    total_score = sum(result.score for result in results)

    if total_score >= 60:
        risk_level = "HIGH"
    elif total_score >= 30:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    triggered_rules = [
        result for result in results
        if result.triggered
    ]

    return FraudEvaluation(
        total_score=total_score,
        risk_level=risk_level,
        triggered_rules=triggered_rules,
    )