
import json
import logging

from datetime import datetime, timedelta, timezone

import httpx

from sqlalchemy import select, update

from app.workers.celery_app import celery_app
from app.core.database import SessionLocal
from app.models import WebhookDelivery

from app.services.webhook_security_service import (
    decrypt_webhook_secret,
    generate_webhook_signature,
)

from app.services.webhook_url_service import validate_webhook_url


logger = logging.getLogger(__name__)


def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


@celery_app.task(name="smartpay.test_task")
def test_task(name: str):
    message = f"Hello {name}! Celery is working with SMARTPAY."

    print(message)

    return {
        "status": "SUCCESS",
        "message": message,
    }


@celery_app.task(
    bind=True,
    name="smartpay.deliver_webhook",
    max_retries=4,
)
def deliver_webhook(self, delivery_id: int):

    db = SessionLocal()

    try:
        delivery = db.get(WebhookDelivery, delivery_id)

        if delivery is None:
            return {
                "status": "NOT_FOUND",
                "delivery_id": delivery_id,
            }

        if delivery.status == "DELIVERED":
            return {
                "status": "ALREADY_DELIVERED",
                "delivery_id": delivery_id,
            }

        if delivery.status == "PROCESSING":
            return {
                "status": "ALREADY_PROCESSING",
                "delivery_id": delivery_id,
            }

        if delivery.status == "FAILED":
            return {
                "status": "FAILED",
                "delivery_id": delivery_id,
            }

        # Atomically mark exhausted deliveries as FAILED.
        exhausted = db.execute(
            update(WebhookDelivery)
            .where(
                WebhookDelivery.id == delivery_id,
                WebhookDelivery.status == "PENDING",
                WebhookDelivery.attempts >= WebhookDelivery.max_attempts,
            )
            .values(
                status="FAILED",
                next_retry_at=None,
                last_error="Maximum delivery attempts reached",
            )
            .execution_options(synchronize_session=False)
        )

        if exhausted.rowcount == 1:
            db.commit()

            return {
                "status": "FAILED",
                "message": "Maximum delivery attempts reached",
                "delivery_id": delivery_id,
            }

        # Atomically claim the pending delivery.
        # Only one worker can successfully perform this update.
        claim = db.execute(
            update(WebhookDelivery)
            .where(
                WebhookDelivery.id == delivery_id,
                WebhookDelivery.status == "PENDING",
                WebhookDelivery.attempts < WebhookDelivery.max_attempts,
            )
            .values(
                status="PROCESSING",
                attempts=WebhookDelivery.attempts + 1,
                last_error=None,
                next_retry_at=None,
            )
            .execution_options(synchronize_session=False)
        )

        if claim.rowcount != 1:
            db.rollback()
            db.expire_all()

            current = db.get(WebhookDelivery, delivery_id)

            if current is None:
                result_status = "NOT_FOUND"
            elif current.status == "DELIVERED":
                result_status = "ALREADY_DELIVERED"
            elif current.status == "PROCESSING":
                result_status = "ALREADY_PROCESSING"
            elif current.status == "FAILED":
                result_status = "FAILED"
            else:
                result_status = "NOT_CLAIMED"

            return {
                "status": result_status,
                "delivery_id": delivery_id,
            }

        db.commit()
        db.expire_all()

        # Reload the claimed delivery and its endpoint.
        delivery = db.get(WebhookDelivery, delivery_id)
        endpoint = delivery.endpoint

        if not endpoint.is_active:
            delivery.status = "FAILED"
            delivery.last_error = "Webhook endpoint is inactive"
            delivery.next_retry_at = None
            db.commit()

            return {
                "status": "FAILED",
                "message": "Webhook endpoint is inactive",
                "delivery_id": delivery_id,
            }

        try:
            # Revalidate URL immediately before sending.
            validate_webhook_url(endpoint.url)

            secret = decrypt_webhook_secret(
                endpoint.secret_encrypted
            )

            payload_bytes = json.dumps(
                delivery.payload,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")

            signature = generate_webhook_signature(
                payload=payload_bytes,
                secret=secret,
            )

            headers = {
                "Content-Type": "application/json",
                "X-SmartPay-Event": delivery.event_type,
                "X-SmartPay-Event-ID": delivery.event_id,
                "X-SmartPay-Signature": signature,
            }

            timeout = httpx.Timeout(
                connect=5.0,
                read=10.0,
                write=10.0,
                pool=5.0,
            )

            with httpx.Client(
                timeout=timeout,
                follow_redirects=False,
            ) as client:

                response = client.post(
                    endpoint.url,
                    content=payload_bytes,
                    headers=headers,
                )

            delivery.http_status_code = response.status_code
            delivery.response_body = response.text[:4000]

            if 200 <= response.status_code < 300:
                delivery.status = "DELIVERED"
                delivery.delivered_at = utc_now()
                delivery.next_retry_at = None
                delivery.last_error = None

                db.commit()

                return {
                    "status": "DELIVERED",
                    "delivery_id": delivery_id,
                    "http_status_code": response.status_code,
                    "attempts": delivery.attempts,
                }

            raise RuntimeError(
                f"Webhook receiver returned HTTP {response.status_code}"
            )

        except Exception as exc:

            delivery.last_error = str(exc)[:4000]

            if delivery.attempts >= delivery.max_attempts:
                delivery.status = "FAILED"
                delivery.next_retry_at = None

                db.commit()

                return {
                    "status": "FAILED",
                    "delivery_id": delivery_id,
                    "attempts": delivery.attempts,
                    "error": delivery.last_error,
                }

            retry_delay = min(
                30 * (2 ** (delivery.attempts - 1)),
                300,
            )

            delivery.status = "PENDING"

            delivery.next_retry_at = (
                utc_now() + timedelta(seconds=retry_delay)
            )

            db.commit()

            return {
                "status": "RETRY_SCHEDULED",
                "delivery_id": delivery_id,
                "attempts": delivery.attempts,
                "next_retry_at": delivery.next_retry_at.isoformat(),
            }

    finally:
        db.close()


@celery_app.task(name="smartpay.recover_pending_webhooks")
def recover_pending_webhooks():

    """
    Find pending webhook deliveries whose retry time has arrived
    and submit them to Celery.
    """

    db = SessionLocal()

    try:
        now = utc_now()

        deliveries = db.scalars(
            select(WebhookDelivery).where(
                WebhookDelivery.status == "PENDING",
                (
                    WebhookDelivery.next_retry_at.is_(None)
                    | (WebhookDelivery.next_retry_at <= now)
                ),
            ).limit(100)
        ).all()

        delivery_ids = [
            delivery.id for delivery in deliveries
        ]

        submitted = 0

        for delivery_id in delivery_ids:
            try:
                deliver_webhook.delay(delivery_id)
                submitted += 1

            except Exception:
                logger.exception(
                    "Could not recover webhook delivery %s",
                    delivery_id,
                )

        return {
            "status": "SUCCESS",
            "found": len(delivery_ids),
            "submitted": submitted,
        }

    finally:
        db.close()
