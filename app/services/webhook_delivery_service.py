from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Payment, WebhookDelivery, WebhookEndpoint


ALLOWED_EVENTS = {
    "payment.success",
    "payment.failed",
}


def create_webhook_deliveries(
    db: Session,
    payment: Payment,
    event_type: str,
) -> list[WebhookDelivery]:
    """
    Create pending webhook deliveries for all active endpoints
    subscribed to the specified payment event.

    This function does not commit the transaction.
    The caller controls the database commit.
    """

    if event_type not in ALLOWED_EVENTS:
        raise ValueError(f"Unsupported webhook event: {event_type}")

    endpoints = db.scalars(
        select(WebhookEndpoint).where(
            WebhookEndpoint.user_id == payment.user_id,
            WebhookEndpoint.is_active.is_(True),
        )
    ).all()

    matching_endpoints = [
        endpoint
        for endpoint in endpoints
        if event_type in endpoint.events
    ]

    payment_status = (
        payment.status.value
        if hasattr(payment.status, "value")
        else str(payment.status)
    )

    payment_method = (
        payment.payment_method.value
        if hasattr(payment.payment_method, "value")
        else str(payment.payment_method)
    )

    event_created_at = (
        datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )

    deliveries = []

    for endpoint in matching_endpoints:
        event_id = f"evt_{uuid4().hex}"

        payload = {
            "id": event_id,
            "type": event_type,
            "created_at": event_created_at,
            "data": {
                "payment": {
                    "id": payment.id,
                    "transaction_id": payment.transaction_id,
                    "amount": str(payment.amount),
                    "currency": payment.currency,
                    "payment_method": payment_method,
                    "status": payment_status,
                    "gateway_transaction_id": payment.gateway_transaction_id,
                    "fraud_score": payment.fraud_score,
                    "risk_level": payment.risk_level,
                }
            },
        }

        delivery = WebhookDelivery(
            event_id=event_id,
            endpoint_id=endpoint.id,
            payment_id=payment.id,
            event_type=event_type,
            payload=payload,
            status="PENDING",
            attempts=0,
            max_attempts=5,
        )

        db.add(delivery)
        deliveries.append(delivery)

    db.flush()

    return deliveries