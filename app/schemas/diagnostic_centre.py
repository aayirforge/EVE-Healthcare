from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class DiagnosticCentreCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    location: str = Field(..., min_length=1, max_length=255)


class CentreTestAssociationCreate(BaseModel):
    test_id: int
    custom_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)


class CentreTestDetail(BaseModel):
    test_id: int
    name: str
    description: Optional[str] = None
    price: Decimal


class DiagnosticCentreResponse(BaseModel):
    id: int
    name: str
    location: str
    created_at: datetime
    available_tests: List[CentreTestDetail] = []

    model_config = ConfigDict(from_attributes=True)
