from decimal import Decimal

from sqlalchemy.orm import Session

from app.fraud_engine.engine import evaluate_payment
from app.models import Payment, PaymentStatus
from app.services.mock_gateway_service import process_mock_payment
from app.services.fraud_velocity_service import record_transaction_and_count


def verify_payment(
    db: Session,
    payment: Payment,
) -> Payment:
    """
    Run fraud detection using Redis transaction velocity,
    then process the payment through the mock gateway.
    """

    # Get the user's unique transaction count from Redis.
    transaction_count = record_transaction_and_count(
        user_id=payment.user_id,
        transaction_id=payment.transaction_id,
    )

    # Evaluate payment risk.
    fraud_result = evaluate_payment(
        amount=Decimal(payment.amount),
        transaction_count=transaction_count,
        is_new_device=False,
        is_unusual_location=False,
    )

    # Save fraud detection results.
    payment.fraud_score = fraud_result.total_score
    payment.risk_level = fraud_result.risk_level

    # Block high-risk payments.
    if fraud_result.risk_level == "HIGH":
        payment.status = PaymentStatus.FAILED.value

        db.commit()
        db.refresh(payment)

        return payment

    # Process payment through the mock gateway.
    gateway_response = process_mock_payment()

    gateway_status = gateway_response["status"]
    gateway_transaction_id = gateway_response["gateway_transaction_id"]

    payment.gateway_transaction_id = gateway_transaction_id

    if gateway_status == "SUCCESS":
        payment.status = PaymentStatus.SUCCESS.value

    elif gateway_status == "FAILED":
        payment.status = PaymentStatus.FAILED.value

    elif gateway_status == "TIMEOUT":
        payment.status = PaymentStatus.PENDING.value

    db.commit()
    db.refresh(payment)

    return payment