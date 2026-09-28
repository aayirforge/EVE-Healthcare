from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.booking import Booking
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingResponse
from app.schemas.common import PaginatedResponse
from app.services.booking_service import (
    cancel_booking,
    create_booking,
    get_user_booking,
    list_user_bookings,
)

router = APIRouter(prefix="/bookings", tags=["Bookings"])


def to_booking_response(booking: Booking) -> BookingResponse:
    return BookingResponse(
        id=booking.id,
        user_id=booking.user_id,
        centre_id=booking.centre_id,
        test_id=booking.test_id,
        appointment_time=booking.appointment_time,
        amount=booking.amount,
        status=booking.status,
        created_at=booking.created_at,
        centre_name=booking.centre.name if booking.centre else None,
        test_name=booking.test.name if booking.test else None,
    )


@router.post(
    "/",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
)
def book_test(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = create_booking(db, current_user.id, booking_data)
    return to_booking_response(booking)


@router.get(
    "/",
    response_model=PaginatedResponse[BookingResponse],
)
def get_my_bookings(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bookings, total, pages = list_user_bookings(db, current_user.id, page, size)
    items = [to_booking_response(b) for b in bookings]
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = get_user_booking(db, booking_id, current_user.id)
    return to_booking_response(booking)


@router.post(
    "/{booking_id}/cancel",
    response_model=BookingResponse,
)
def cancel_my_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = cancel_booking(db, booking_id, current_user.id)
    return to_booking_response(booking)
