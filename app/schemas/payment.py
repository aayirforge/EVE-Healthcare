from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.payment import PaymentStatus


class PaymentSimulateRequest(BaseModel):
    booking_id: int
    status: PaymentStatus = PaymentStatus.SUCCESS


class PaymentResponse(BaseModel):
    id: int
    booking_id: int
    amount: Decimal
    status: str
    provider_payment_id: Optional[str] = None
    created_at: datetime
    booking_status: str

    model_config = ConfigDict(from_attributes=True)


class WebhookEventRequest(BaseModel):
    event_id: str = Field(..., min_length=1, max_length=100)
    booking_id: int
    payment_status: PaymentStatus
    provider_payment_id: Optional[str] = None


class WebhookResponse(BaseModel):
    status: str
    message: str
    event_id: str
    booking_id: Optional[int] = None
    booking_status: Optional[str] = None
