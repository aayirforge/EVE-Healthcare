from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class BookingCreate(BaseModel):
    centre_id: int
    test_id: int
    appointment_time: datetime


class BookingResponse(BaseModel):
    id: int
    user_id: int
    centre_id: int
    test_id: int
    appointment_time: datetime
    amount: Decimal
    status: str
    created_at: datetime
    centre_name: Optional[str] = None
    test_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
