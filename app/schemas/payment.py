from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models import PaymentMethod, PaymentStatus


class PaymentCreate(BaseModel):
    amount: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )
    currency: str = Field(
        default="INR",
        min_length=3,
        max_length=3,
    )
    payment_method: PaymentMethod


class PaymentResponse(BaseModel):
    id: int
    transaction_id: str
    user_id: int
    amount: Decimal
    currency: str
    payment_method: PaymentMethod
    gateway_transaction_id: str | None
    status: PaymentStatus
    fraud_score: int
    risk_level: str

    model_config = ConfigDict(from_attributes=True)


class PaymentVerifyRequest(BaseModel):
    payment_id: int = Field(gt=0)
    gateway_status: str | None = Field(
        default=None,
        pattern="^(SUCCESS|FAILED|TIMEOUT)$",
    )