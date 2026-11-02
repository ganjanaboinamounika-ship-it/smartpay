from dataclasses import dataclass
from decimal import Decimal


@dataclass
class FraudCheckResult:
    rule: str
    triggered: bool
    score: int
    reason: str


def check_high_amount(amount: Decimal) -> FraudCheckResult:
    """
    Flag unusually large payments.
    """
    threshold = Decimal("100000")

    if amount >= threshold:
        return FraudCheckResult(
            rule="HIGH_AMOUNT",
            triggered=True,
            score=30,
            reason="Payment amount exceeds the high-value threshold",
        )

    return FraudCheckResult(
        rule="HIGH_AMOUNT",
        triggered=False,
        score=0,
        reason="Payment amount is within the normal range",
    )


def check_velocity(transaction_count: int) -> FraudCheckResult:
    """
    Flag too many transactions in a short period.
    """
    threshold = 5

    if transaction_count > threshold:
        return FraudCheckResult(
            rule="HIGH_VELOCITY",
            triggered=True,
            score=25,
            reason="Too many transactions detected in a short period",
        )

    return FraudCheckResult(
        rule="HIGH_VELOCITY",
        triggered=False,
        score=0,
        reason="Transaction frequency is within the normal range",
    )


def check_new_device(is_new_device: bool) -> FraudCheckResult:
    """
    Flag payments originating from a new device.
    """
    if is_new_device:
        return FraudCheckResult(
            rule="NEW_DEVICE",
            triggered=True,
            score=15,
            reason="Payment originated from a new device",
        )

    return FraudCheckResult(
        rule="NEW_DEVICE",
        triggered=False,
        score=0,
        reason="Payment originated from a known device",
    )


def check_unusual_location(is_unusual_location: bool) -> FraudCheckResult:
    """
    Flag payments from an unusual location.
    """
    if is_unusual_location:
        return FraudCheckResult(
            rule="UNUSUAL_LOCATION",
            triggered=True,
            score=20,
            reason="Payment originated from an unusual location",
        )

    return FraudCheckResult(
        rule="UNUSUAL_LOCATION",
        triggered=False,
        score=0,
        reason="Payment originated from a normal location",
    )