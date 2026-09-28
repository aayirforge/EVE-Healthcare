from math import ceil
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.diagnostic_test import DiagnosticTest
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.diagnostic_test import (
    DiagnosticTestCreate,
    DiagnosticTestResponse,
)

router = APIRouter(prefix="/tests", tags=["Diagnostic Tests"])


@router.post(
    "/",
    response_model=DiagnosticTestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_test(
    test_data: DiagnosticTestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    test = DiagnosticTest(
        name=test_data.name,
        description=test_data.description,
        price=test_data.price,
    )
    db.add(test)
    db.commit()
    db.refresh(test)
    return test


@router.get(
    "/",
    response_model=PaginatedResponse[DiagnosticTestResponse],
)
def list_tests(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(DiagnosticTest)
    total = query.count()
    pages = ceil(total / size) if total > 0 else 0
    items = (
        query.order_by(DiagnosticTest.id.asc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get(
    "/{test_id}",
    response_model=DiagnosticTestResponse,
)
def get_test(
    test_id: int,
    db: Session = Depends(get_db),
):
    test = db.query(DiagnosticTest).filter(DiagnosticTest.id == test_id).first()
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnostic test not found",
        )
    return test
