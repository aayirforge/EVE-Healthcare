from sqlalchemy import CheckConstraint, Column, DateTime, Integer, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class DiagnosticTest(Base):
    __tablename__ = "diagnostic_tests"
    __table_args__ = (
        CheckConstraint("price >= 0", name="chk_test_price_positive"),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(String(500), nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    centre_associations = relationship(
        "CentreTest",
        back_populates="test",
        cascade="all, delete-orphan",
    )
    bookings = relationship("Booking", back_populates="test")
