import uuid
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.models.booking import Booking, BookingStatus
from app.models.payment import Payment, PaymentStatus
from app.schemas.payment import PaymentSimulateRequest


def simulate_payment(
    db: Session, user_id: int, payment_data: PaymentSimulateRequest
) -> Payment:
    booking = (
        db.query(Booking)
        .filter(Booking.id == payment_data.booking_id)
        .with_for_update()
        .first()
    )
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )
    if booking.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to pay for this booking",
        )
    if booking.status != BookingStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot process payment for booking with status '{booking.status}'",
        )

    if payment_data.status == PaymentStatus.SUCCESS:
        booking.status = BookingStatus.CONFIRMED.value
        actual_payment_status = PaymentStatus.SUCCESS.value
        logger.info(f"Payment simulation successful: booking_id={booking.id}")
    else:
        booking.status = BookingStatus.FAILED.value
        actual_payment_status = PaymentStatus.FAILED.value
        logger.warning(f"Payment simulation failed: booking_id={booking.id}")

    provider_id = f"sim_pay_{uuid.uuid4().hex[:12]}"
    payment = Payment(
        booking_id=booking.id,
        amount=booking.amount,
        status=actual_payment_status,
        provider_payment_id=provider_id,
        idempotency_key=f"pay_sim_{booking.id}_{uuid.uuid4().hex[:8]}",
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment
