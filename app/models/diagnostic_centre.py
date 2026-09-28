from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class CentreTest(Base):
    __tablename__ = "centre_tests"
    __table_args__ = (
        UniqueConstraint("centre_id", "test_id", name="uq_centre_test"),
        CheckConstraint("custom_price >= 0", name="chk_centre_test_price_positive"),
    )

    id = Column(Integer, primary_key=True, index=True)
    centre_id = Column(
        Integer,
        ForeignKey("diagnostic_centres.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    test_id = Column(
        Integer,
        ForeignKey("diagnostic_tests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    custom_price = Column(Numeric(10, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    centre = relationship("DiagnosticCentre", back_populates="test_associations")
    test = relationship("DiagnosticTest", back_populates="centre_associations")


class DiagnosticCentre(Base):
    __tablename__ = "diagnostic_centres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    location = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    test_associations = relationship(
        "CentreTest",
        back_populates="centre",
        cascade="all, delete-orphan",
    )
    bookings = relationship("Booking", back_populates="centre")
