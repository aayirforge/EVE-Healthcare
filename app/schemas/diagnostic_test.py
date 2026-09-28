from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class DiagnosticTestCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    price: Decimal = Field(..., ge=0, decimal_places=2)


class DiagnosticTestResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
