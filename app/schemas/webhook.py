from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


ALLOWED_WEBHOOK_EVENTS = {
    "payment.success",
    "payment.failed",
}

WebhookDeliveryStatus = Literal[
    "PENDING",
    "PROCESSING",
    "DELIVERED",
    "FAILED",
]


class WebhookEndpointCreate(BaseModel):
    url: str = Field(min_length=1, max_length=2048)

    events: list[str] = Field(
        min_length=1,
        max_length=2,
    )

    @field_validator("url")
    @classmethod
    def validate_url_not_empty(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Webhook URL cannot be empty")

        return value

    @field_validator("events")
    @classmethod
    def validate_events(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("Duplicate webhook events are not allowed")

        invalid_events = set(value) - ALLOWED_WEBHOOK_EVENTS

        if invalid_events:
            raise ValueError(
                f"Unsupported webhook events: {sorted(invalid_events)}"
            )

        return value


class WebhookEndpointResponse(BaseModel):
    id: int
    url: str
    events: list[str]
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WebhookEndpointCreateResponse(WebhookEndpointResponse):
    secret: str


class WebhookDeliveryResponse(BaseModel):
    id: int
    event_id: str
    endpoint_id: int
    payment_id: int
    event_type: str
    payload: dict
    status: WebhookDeliveryStatus
    attempts: int
    max_attempts: int
    http_status_code: int | None
    response_body: str | None
    last_error: str | None
    next_retry_at: datetime | None
    delivered_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WebhookDeliveryListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[WebhookDeliveryResponse]