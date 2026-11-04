from uuid import uuid4

from sqlalchemy.orm import Session

from app.models import Payment, PaymentStatus
from app.schemas.payment import PaymentCreate


def create_payment(
    db: Session,
    user_id: int,
    payment_data: PaymentCreate,
) -> Payment:
    transaction_id = f"TXN-{uuid4().hex[:16].upper()}"

    payment = Payment(
        transaction_id=transaction_id,
        user_id=user_id,
        amount=payment_data.amount,
        currency=payment_data.currency.upper(),
        payment_method=payment_data.payment_method.value,
        status=PaymentStatus.PENDING.value,
    )

    db.add(payment)

    # Send the INSERT to PostgreSQL without committing.
    # This allows the idempotency record to be saved
    # in the same transaction.
    db.flush()

    return payment