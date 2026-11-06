from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class WebhookEndpoint(Base):
    __tablename__ = "webhook_endpoints"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "url",
            name="uq_webhook_endpoint_user_url",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    url: Mapped[str] = mapped_column(
        String(2048),
        nullable=False,
    )

    # Encrypted using Fernet. Never store the plaintext secret here.
    secret_encrypted: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Example: ["payment.success", "payment.failed"]
    events: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship("User", backref="webhook_endpoints")

    deliveries = relationship(
        "WebhookDelivery",
        back_populates="endpoint",
        cascade="all, delete-orphan",
    )


class WebhookDelivery(Base):
    __tablename__ = "webhook_deliveries"

    __table_args__ = (
        Index(
            "ix_webhook_delivery_status_retry",
            "status",
            "next_retry_at",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    event_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    endpoint_id: Mapped[int] = mapped_column(
        ForeignKey("webhook_endpoints.id"),
        nullable=False,
        index=True,
    )

    payment_id: Mapped[int] = mapped_column(
        ForeignKey("payments.id"),
        nullable=False,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    payload: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="PENDING",
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    max_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5,
    )

    http_status_code: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    response_body: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    last_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    next_retry_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    delivered_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    endpoint = relationship(
        "WebhookEndpoint",
        back_populates="deliveries",
    )

    payment = relationship("Payment")
