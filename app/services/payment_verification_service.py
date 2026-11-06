
import logging
from decimal import Decimal

from sqlalchemy.orm import Session

from app.fraud_engine.engine import evaluate_payment
from app.models import Payment, PaymentStatus, WebhookDelivery
from app.services.mock_gateway_service import process_mock_payment
from app.services.fraud_velocity_service import record_transaction_and_count
from app.services.webhook_delivery_service import create_webhook_deliveries
from app.workers.tasks import deliver_webhook


logger = logging.getLogger(__name__)


def create_terminal_payment_event(
    db: Session,
    payment: Payment,
    previous_status: str,
) -> list[WebhookDelivery]:
    """
    Create webhook delivery records only when a payment
    transitions from a non-terminal state to SUCCESS or FAILED.
    """

    current_status = (
        payment.status.value
        if hasattr(payment.status, "value")
        else str(payment.status)
    )

    if previous_status in ("SUCCESS", "FAILED"):
        return []

    event_mapping = {
        "SUCCESS": "payment.success",
        "FAILED": "payment.failed",
    }

    event_type = event_mapping.get(current_status)

    if not event_type:
        return []

    return create_webhook_deliveries(
        db=db,
        payment=payment,
        event_type=event_type,
    )


def dispatch_webhook_deliveries(
    deliveries: list[WebhookDelivery],
) -> None:
    """
    Submit committed webhook delivery records to Celery.

    A publishing failure does not undo the payment transaction.
    Pending records can be recovered by a later retry mechanism.
    """

    for delivery in deliveries:
        try:
            deliver_webhook.delay(delivery.id)

        except Exception:
            logger.exception(
                "Could not submit webhook delivery %s to Celery",
                delivery.id,
            )


def verify_payment(
    db: Session,
    payment: Payment,
    forced_gateway_status: str | None = None,
) -> Payment:
    """
    Run fraud detection using Redis transaction velocity,
    then process the payment through the mock gateway.

    Payment changes and webhook delivery records are committed
    together before webhook delivery is submitted to Celery.
    """

    previous_status = (
        payment.status.value
        if hasattr(payment.status, "value")
        else str(payment.status)
    )

    transaction_count = record_transaction_and_count(
        user_id=payment.user_id,
        transaction_id=payment.transaction_id,
    )

    fraud_result = evaluate_payment(
        amount=Decimal(payment.amount),
        transaction_count=transaction_count,
        is_new_device=False,
        is_unusual_location=False,
    )

    payment.fraud_score = fraud_result.total_score
    payment.risk_level = fraud_result.risk_level

    if fraud_result.risk_level == "HIGH":
        payment.status = PaymentStatus.FAILED.value

        deliveries = create_terminal_payment_event(
            db=db,
            payment=payment,
            previous_status=previous_status,
        )

        db.commit()
        db.refresh(payment)

        dispatch_webhook_deliveries(deliveries)

        return payment

    gateway_response = process_mock_payment(
    forced_status=forced_gateway_status,
)

    gateway_status = gateway_response["status"]
    gateway_transaction_id = gateway_response["gateway_transaction_id"]

    payment.gateway_transaction_id = gateway_transaction_id

    if gateway_status == "SUCCESS":
        payment.status = PaymentStatus.SUCCESS.value

    elif gateway_status == "FAILED":
        payment.status = PaymentStatus.FAILED.value

    elif gateway_status == "TIMEOUT":
        payment.status = PaymentStatus.PENDING.value

    deliveries = create_terminal_payment_event(
        db=db,
        payment=payment,
        previous_status=previous_status,
    )

    db.commit()
    db.refresh(payment)

    dispatch_webhook_deliveries(deliveries)

    return payment
