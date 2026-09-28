from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.payment import (
    PaymentResponse,
    PaymentSimulateRequest,
    WebhookEventRequest,
    WebhookResponse,
)
from app.services.payment_service import simulate_payment
from app.services.webhook_service import process_webhook

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post(
    "/",
    response_model=PaymentResponse,
    status_code=status.HTTP_200_OK,
)
def make_payment(
    payment_data: PaymentSimulateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = simulate_payment(db, current_user.id, payment_data)
    return PaymentResponse(
        id=payment.id,
        booking_id=payment.booking_id,
        amount=payment.amount,
        status=payment.status,
        provider_payment_id=payment.provider_payment_id,
        created_at=payment.created_at,
        booking_status=payment.booking.status,
    )


@router.post(
    "/webhook/",
    response_model=WebhookResponse,
    status_code=status.HTTP_200_OK,
)
def payment_webhook(
    payload: WebhookEventRequest,
    db: Session = Depends(get_db),
):
    return process_webhook(db, payload)
