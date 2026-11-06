import logging

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models import User, WebhookEndpoint, WebhookDelivery
from app.schemas.webhook import (
    WebhookEndpointCreate,
    WebhookEndpointCreateResponse,
    WebhookEndpointResponse,
    WebhookDeliveryResponse,
    WebhookDeliveryListResponse,
)
from app.services.webhook_security_service import (
    encrypt_webhook_secret,
    generate_webhook_secret,
)
from app.services.webhook_url_service import validate_webhook_url
from app.workers.tasks import deliver_webhook


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"],
)


@router.post(
    "",
    response_model=WebhookEndpointCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_webhook(
    webhook_data: WebhookEndpointCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Validate the destination URL.
    try:
        validate_webhook_url(webhook_data.url)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    # Generate a unique secret for this endpoint.
    secret = generate_webhook_secret()

    encrypted_secret = encrypt_webhook_secret(secret)

    endpoint = WebhookEndpoint(
        user_id=current_user.id,
        url=webhook_data.url,
        secret_encrypted=encrypted_secret,
        events=webhook_data.events,
        is_active=True,
    )

    try:
        db.add(endpoint)
        db.commit()
        db.refresh(endpoint)

    except IntegrityError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This webhook URL is already registered",
        ) from exc

    return {
        "id": endpoint.id,
        "url": endpoint.url,
        "events": endpoint.events,
        "is_active": endpoint.is_active,
        "created_at": endpoint.created_at,
        "secret": secret,
    }


@router.get(
    "",
    response_model=list[WebhookEndpointResponse],
)
def list_webhooks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    endpoints = db.scalars(
        select(WebhookEndpoint)
        .where(WebhookEndpoint.user_id == current_user.id)
        .order_by(WebhookEndpoint.created_at.desc())
    ).all()

    return endpoints


@router.post("/{endpoint_id}/deactivate")
def deactivate_webhook(
    endpoint_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    endpoint = db.scalar(
        select(WebhookEndpoint).where(
            WebhookEndpoint.id == endpoint_id,
            WebhookEndpoint.user_id == current_user.id,
        )
    )

    if endpoint is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook endpoint not found",
        )

    endpoint.is_active = False

    db.commit()

    return {
        "success": True,
        "message": "Webhook endpoint deactivated successfully",
        "endpoint_id": endpoint.id,
    }
@router.get(
    "/deliveries",
    response_model=WebhookDeliveryListResponse,
)
def list_webhook_deliveries(
    delivery_status: str | None = Query(
        default=None,
        alias="status",
        pattern="^(PENDING|PROCESSING|DELIVERED|FAILED)$",
    ),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    base_query = (
        select(WebhookDelivery)
        .join(
            WebhookEndpoint,
            WebhookDelivery.endpoint_id == WebhookEndpoint.id,
        )
        .where(WebhookEndpoint.user_id == current_user.id)
    )

    if delivery_status:
        base_query = base_query.where(
            WebhookDelivery.status == delivery_status
        )

    total = db.scalar(
        select(func.count()).select_from(base_query.subquery())
    )

    deliveries = db.scalars(
        base_query
        .order_by(WebhookDelivery.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).all()

    return {
        "total": total or 0,
        "limit": limit,
        "offset": offset,
        "items": deliveries,
    }


@router.get(
    "/deliveries/{delivery_id}",
    response_model=WebhookDeliveryResponse,
)
def get_webhook_delivery(
    delivery_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    delivery = db.scalar(
        select(WebhookDelivery)
        .join(
            WebhookEndpoint,
            WebhookDelivery.endpoint_id == WebhookEndpoint.id,
        )
        .where(
            WebhookDelivery.id == delivery_id,
            WebhookEndpoint.user_id == current_user.id,
        )
    )

    if delivery is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook delivery not found",
        )

    return delivery


@router.post("/deliveries/{delivery_id}/retry")
def retry_webhook_delivery(
    delivery_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Confirm that this delivery belongs to the logged-in user
    # and that its endpoint is active.
    delivery = db.scalar(
        select(WebhookDelivery)
        .join(
            WebhookEndpoint,
            WebhookDelivery.endpoint_id == WebhookEndpoint.id,
        )
        .where(
            WebhookDelivery.id == delivery_id,
            WebhookEndpoint.user_id == current_user.id,
        )
    )

    if delivery is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook delivery not found",
        )

    if delivery.status != "FAILED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only FAILED deliveries can be manually retried",
        )

    if not delivery.endpoint.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Activate the webhook endpoint before retrying",
        )

    # Atomically grant exactly one additional attempt.
    # The attempt history is preserved; it is not reset to zero.
    active_owned_endpoint_ids = select(WebhookEndpoint.id).where(
        WebhookEndpoint.id == WebhookDelivery.endpoint_id,
        WebhookEndpoint.user_id == current_user.id,
        WebhookEndpoint.is_active.is_(True),
    )

    retry_update = db.execute(
        update(WebhookDelivery)
        .where(
            WebhookDelivery.id == delivery_id,
            WebhookDelivery.status == "FAILED",
            WebhookDelivery.endpoint_id.in_(
                active_owned_endpoint_ids
            ),
        )
        .values(
            status="PENDING",
            max_attempts=WebhookDelivery.max_attempts + 1,
            next_retry_at=datetime.now(timezone.utc).replace(
                tzinfo=None
            ),
        )
        .execution_options(synchronize_session=False)
    )

    if retry_update.rowcount != 1:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Delivery could not be retried. Check its current status.",
        )

    db.commit()

    # Submit only after the database transaction succeeds.
    try:
        deliver_webhook.delay(delivery_id)

        message = "Manual retry submitted successfully"

    except Exception:
        logger.exception(
            "Could not immediately queue manual webhook retry %s",
            delivery_id,
        )

        # The delivery remains PENDING. The existing recovery task
        # can pick it up when its retry time arrives.
        message = (
            "Retry saved as PENDING. Background recovery "
            "will attempt to queue it."
        )

    return {
        "success": True,
        "delivery_id": delivery_id,
        "status": "PENDING",
        "message": message,
    }