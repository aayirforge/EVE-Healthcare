from enum import Enum
from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class BookingStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        CheckConstraint("amount >= 0", name="chk_booking_amount_positive"),
        CheckConstraint(
            "status IN ('PENDING', 'CONFIRMED', 'FAILED', 'CANCELLED')",
            name="chk_booking_status_valid",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    centre_id = Column(
        Integer,
        ForeignKey("diagnostic_centres.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    test_id = Column(
        Integer,
        ForeignKey("diagnostic_tests.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    appointment_time = Column(DateTime(timezone=True), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(30), nullable=False, default=BookingStatus.PENDING.value, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship("User", back_populates="bookings")
    centre = relationship("DiagnosticCentre", back_populates="bookings")
    test = relationship("DiagnosticTest", back_populates="bookings")
    payments = relationship("Payment", back_populates="booking", cascade="all, delete-orphan")
