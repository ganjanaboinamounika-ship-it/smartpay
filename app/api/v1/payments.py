
import re

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models import IdempotencyRecord, Payment, User
from app.schemas.payment import (
    PaymentCreate,
    PaymentResponse,
    PaymentVerifyRequest,
)
from app.services.payment_service import create_payment
from app.services.payment_verification_service import verify_payment
from app.services.idempotency_service import generate_request_fingerprint


router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


@router.post(
    "/create",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_payment_endpoint(
    payment_data: PaymentCreate,
    response: Response,
    idempotency_key: str = Header(
        ...,
        alias="Idempotency-Key",
        min_length=8,
        max_length=255,
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Step 1: Validate the idempotency key.
    if not re.fullmatch(r"[A-Za-z0-9._:-]{8,255}", idempotency_key):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Idempotency-Key format",
        )

    # Step 2: Generate a fingerprint for the request.
    fingerprint = generate_request_fingerprint(
        current_user.id,
        payment_data,
    )

    # Step 3: Check whether this user has already used this key.
    existing_record = db.scalar(
        select(IdempotencyRecord).where(
            IdempotencyRecord.user_id == current_user.id,
            IdempotencyRecord.idempotency_key == idempotency_key,
        )
    )

    if existing_record is not None:
        if existing_record.request_fingerprint != fingerprint:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Idempotency-Key was already used with different payment details",
            )

        original_payment = db.scalar(
            select(Payment).where(
                Payment.id == existing_record.payment_id,
                Payment.user_id == current_user.id,
            )
        )

        if original_payment is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Original payment record could not be found",
            )

        response.status_code = status.HTTP_200_OK
        return original_payment

    # Step 4: Create payment and idempotency record
    # inside the same database transaction.
    try:
        payment = create_payment(
            db=db,
            user_id=current_user.id,
            payment_data=payment_data,
        )

        # Insert the payment into the current transaction.
        db.flush()

        idempotency_record = IdempotencyRecord(
            user_id=current_user.id,
            idempotency_key=idempotency_key,
            request_fingerprint=fingerprint,
            payment_id=payment.id,
            status="COMPLETED",
        )

        db.add(idempotency_record)

        # Save both records together.
        db.commit()
        db.refresh(payment)

        return payment

    except IntegrityError:
        # Another simultaneous request may have inserted
        # this same user's idempotency key first.
        db.rollback()

        existing_record = db.scalar(
            select(IdempotencyRecord).where(
                IdempotencyRecord.user_id == current_user.id,
                IdempotencyRecord.idempotency_key == idempotency_key,
            )
        )

        if existing_record is not None:
            if existing_record.request_fingerprint != fingerprint:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Idempotency-Key was already used with different payment details",
                )

            original_payment = db.scalar(
                select(Payment).where(
                    Payment.id == existing_record.payment_id,
                    Payment.user_id == current_user.id,
                )
            )

            if original_payment is not None:
                response.status_code = status.HTTP_200_OK
                return original_payment

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment could not be created. Please retry using the same Idempotency-Key.",
        )

    except Exception:
        db.rollback()
        raise


@router.post(
    "/verify",
    response_model=PaymentResponse,
)
def verify_payment_endpoint(
    verify_data: PaymentVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    payment = db.scalar(
        select(Payment).where(
            Payment.id == verify_data.payment_id,
            Payment.user_id == current_user.id,
        )
    )

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    if payment.status == "SUCCESS":
        return payment

    if payment.status == "FAILED":
        return payment

    return verify_payment(
        db=db,
        payment=payment,
    )


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
)
def get_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    payment = db.scalar(
        select(Payment).where(
            Payment.id == payment_id,
            Payment.user_id == current_user.id,
        )
    )

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    return payment
