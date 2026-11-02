from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models import Payment, User
from app.schemas.payment import (
    PaymentCreate,
    PaymentResponse,
    PaymentVerifyRequest,
)
from app.services.payment_service import create_payment
from app.services.payment_verification_service import verify_payment


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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    payment = create_payment(
        db=db,
        user_id=current_user.id,
        payment_data=payment_data,
    )

    return payment

@router.post("/verify", response_model=PaymentResponse)
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