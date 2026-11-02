from sqlalchemy.orm import Session

from app.models import Payment, PaymentStatus
from app.services.mock_gateway_service import process_mock_payment


def verify_payment(
    db: Session,
    payment: Payment,
) -> Payment:
    gateway_response = process_mock_payment()

    gateway_status = gateway_response["status"]
    gateway_transaction_id = gateway_response["gateway_transaction_id"]

    payment.gateway_transaction_id = gateway_transaction_id

    if gateway_status == "SUCCESS":
        payment.status = PaymentStatus.SUCCESS.value

    elif gateway_status == "FAILED":
        payment.status = PaymentStatus.FAILED.value

    elif gateway_status == "TIMEOUT":
        # A timeout means the gateway did not confirm the payment.
        # Keep the payment pending instead of marking it successful.
        payment.status = PaymentStatus.PENDING.value

    db.commit()
    db.refresh(payment)

    return payment