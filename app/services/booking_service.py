from datetime import datetime, timezone
from math import ceil
from typing import Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.models.booking import Booking, BookingStatus
from app.models.diagnostic_centre import CentreTest, DiagnosticCentre
from app.models.diagnostic_test import DiagnosticTest
from app.schemas.booking import BookingCreate


def create_booking(db: Session, user_id: int, booking_data: BookingCreate) -> Booking:
    appointment_time = booking_data.appointment_time
    if appointment_time.tzinfo is None:
        appointment_time = appointment_time.replace(tzinfo=timezone.utc)

    if appointment_time <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment date/time must be in the future",
        )

    centre = db.query(DiagnosticCentre).filter(DiagnosticCentre.id == booking_data.centre_id).first()
    if not centre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnostic centre not found",
        )

    test = db.query(DiagnosticTest).filter(DiagnosticTest.id == booking_data.test_id).first()
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnostic test not found",
        )

    centre_test = (
        db.query(CentreTest)
        .filter(
            CentreTest.centre_id == booking_data.centre_id,
            CentreTest.test_id == booking_data.test_id,
        )
        .first()
    )
    if not centre_test:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test is not offered by the selected diagnostic centre",
        )

    effective_price = (
        centre_test.custom_price
        if centre_test.custom_price is not None
        else test.price
    )

    booking = Booking(
        user_id=user_id,
        centre_id=booking_data.centre_id,
        test_id=booking_data.test_id,
        appointment_time=appointment_time,
        amount=effective_price,
        status=BookingStatus.PENDING.value,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    logger.info(
        f"Booking created: id={booking.id}, user_id={user_id}, "
        f"centre_id={booking.centre_id}, test_id={booking.test_id}, amount={booking.amount}"
    )
    return booking


def get_user_booking(db: Session, booking_id: int, user_id: int) -> Booking:
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )
    if booking.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this booking",
        )
    return booking


def list_user_bookings(
    db: Session, user_id: int, page: int = 1, size: int = 10
) -> Tuple[list, int, int]:
    query = db.query(Booking).filter(Booking.user_id == user_id)
    total = query.count()
    pages = ceil(total / size) if total > 0 else 0
    items = query.order_by(Booking.created_at.desc()).offset((page - 1) * size).limit(size).all()
    return items, total, pages


def cancel_booking(db: Session, booking_id: int, user_id: int) -> Booking:
    booking = get_user_booking(db, booking_id, user_id)
    if booking.status != BookingStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel booking with status '{booking.status}'",
        )
    booking.status = BookingStatus.CANCELLED.value
    db.commit()
    db.refresh(booking)
    logger.info(f"Booking cancelled: id={booking.id}, user_id={user_id}")
    return booking
