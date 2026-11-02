from decimal import Decimal

from sqlalchemy.orm import Session

from app.fraud_engine.engine import evaluate_payment
from app.models import Payment, PaymentStatus
from app.services.mock_gateway_service import process_mock_payment


def verify_payment(
    db: Session,
    payment: Payment,
) -> Payment:
    """
    Run fraud detection and then process the payment
    through the educational mock gateway.
    """

    fraud_result = evaluate_payment(
        amount=Decimal(payment.amount),
        transaction_count=1,
        is_new_device=False,
        is_unusual_location=False,
    )

    if fraud_result.risk_level == "HIGH":
        payment.status = PaymentStatus.FAILED.value

        db.commit()
        db.refresh(payment)

        return payment

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