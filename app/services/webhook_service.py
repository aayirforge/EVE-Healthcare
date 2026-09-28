from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.models.booking import Booking, BookingStatus
from app.models.payment import Payment, PaymentStatus, WebhookEvent
from app.schemas.payment import WebhookEventRequest, WebhookResponse


def process_webhook(db: Session, payload: WebhookEventRequest) -> WebhookResponse:
    existing_event = (
        db.query(WebhookEvent)
        .filter(WebhookEvent.event_id == payload.event_id)
        .first()
    )
    if existing_event:
        booking = (
            db.query(Booking)
            .filter(Booking.id == existing_event.booking_id)
            .first()
        )
        logger.info(f"Duplicate webhook event received: event_id={payload.event_id}")
        return WebhookResponse(
            status="ignored",
            message="Duplicate event already processed",
            event_id=payload.event_id,
            booking_id=existing_event.booking_id,
            booking_status=booking.status if booking else None,
        )

    booking = (
        db.query(Booking)
        .filter(Booking.id == payload.booking_id)
        .with_for_update()
        .first()
    )
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    webhook_event = WebhookEvent(
        event_id=payload.event_id,
        booking_id=booking.id,
        payment_status=payload.payment_status.value,
        provider_payment_id=payload.provider_payment_id,
    )

    try:
        db.add(webhook_event)
        if booking.status == BookingStatus.PENDING.value:
            if payload.payment_status == PaymentStatus.SUCCESS:
                booking.status = BookingStatus.CONFIRMED.value
                payment_status_str = PaymentStatus.SUCCESS.value
            else:
                booking.status = BookingStatus.FAILED.value
                payment_status_str = PaymentStatus.FAILED.value

            payment = Payment(
                booking_id=booking.id,
                amount=booking.amount,
                status=payment_status_str,
                provider_payment_id=payload.provider_payment_id,
                idempotency_key=payload.event_id,
            )
            db.add(payment)

        db.commit()
        db.refresh(booking)
    except IntegrityError:
        db.rollback()
        logger.info(f"Concurrent duplicate webhook detected: event_id={payload.event_id}")
        return WebhookResponse(
            status="ignored",
            message="Duplicate event already processed",
            event_id=payload.event_id,
            booking_id=booking.id,
            booking_status=booking.status,
        )

    logger.info(
        f"Webhook event processed: event_id={payload.event_id}, "
        f"booking_id={booking.id}, booking_status={booking.status}"
    )
    return WebhookResponse(
        status="processed",
        message="Webhook event processed successfully",
        event_id=payload.event_id,
        booking_id=booking.id,
        booking_status=booking.status,
    )
