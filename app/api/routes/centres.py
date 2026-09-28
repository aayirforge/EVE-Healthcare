from math import ceil
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.diagnostic_centre import CentreTest, DiagnosticCentre
from app.models.diagnostic_test import DiagnosticTest
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.diagnostic_centre import (
    CentreTestAssociationCreate,
    CentreTestDetail,
    DiagnosticCentreCreate,
    DiagnosticCentreResponse,
)

router = APIRouter(prefix="/centres", tags=["Diagnostic Centres"])


def build_centre_response(centre: DiagnosticCentre) -> DiagnosticCentreResponse:
    tests = []
    for assoc in centre.test_associations:
        if assoc.test:
            effective_price = (
                assoc.custom_price
                if assoc.custom_price is not None
                else assoc.test.price
            )
            tests.append(
                CentreTestDetail(
                    test_id=assoc.test.id,
                    name=assoc.test.name,
                    description=assoc.test.description,
                    price=effective_price,
                )
            )
    return DiagnosticCentreResponse(
        id=centre.id,
        name=centre.name,
        location=centre.location,
        created_at=centre.created_at,
        available_tests=tests,
    )


@router.post(
    "/",
    response_model=DiagnosticCentreResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_centre(
    centre_data: DiagnosticCentreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    centre = DiagnosticCentre(
        name=centre_data.name,
        location=centre_data.location,
    )
    db.add(centre)
    db.commit()
    db.refresh(centre)
    return build_centre_response(centre)


@router.get(
    "/",
    response_model=PaginatedResponse[DiagnosticCentreResponse],
)
def list_centres(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(DiagnosticCentre)
    total = query.count()
    pages = ceil(total / size) if total > 0 else 0
    centres = (
        query.options(joinedload(DiagnosticCentre.test_associations).joinedload(CentreTest.test))
        .order_by(DiagnosticCentre.id.asc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    items = [build_centre_response(c) for c in centres]
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get(
    "/{centre_id}",
    response_model=DiagnosticCentreResponse,
)
def get_centre(
    centre_id: int,
    db: Session = Depends(get_db),
):
    centre = (
        db.query(DiagnosticCentre)
        .options(joinedload(DiagnosticCentre.test_associations).joinedload(CentreTest.test))
        .filter(DiagnosticCentre.id == centre_id)
        .first()
    )
    if not centre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnostic centre not found",
        )
    return build_centre_response(centre)


@router.post(
    "/{centre_id}/tests",
    response_model=DiagnosticCentreResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_test_to_centre(
    centre_id: int,
    assoc_data: CentreTestAssociationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    centre = db.query(DiagnosticCentre).filter(DiagnosticCentre.id == centre_id).first()
    if not centre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnostic centre not found",
        )

    test = db.query(DiagnosticTest).filter(DiagnosticTest.id == assoc_data.test_id).first()
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnostic test not found",
        )

    existing = (
        db.query(CentreTest)
        .filter(
            CentreTest.centre_id == centre_id,
            CentreTest.test_id == assoc_data.test_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test is already associated with this centre",
        )

    assoc = CentreTest(
        centre_id=centre_id,
        test_id=assoc_data.test_id,
        custom_price=assoc_data.custom_price,
    )
    db.add(assoc)
    db.commit()

    centre = (
        db.query(DiagnosticCentre)
        .options(joinedload(DiagnosticCentre.test_associations).joinedload(CentreTest.test))
        .filter(DiagnosticCentre.id == centre_id)
        .first()
    )
    return build_centre_response(centre)


@router.delete(
    "/{centre_id}/tests/{test_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_test_from_centre(
    centre_id: int,
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    centre = db.query(DiagnosticCentre).filter(DiagnosticCentre.id == centre_id).first()
    if not centre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnostic centre not found",
        )

    assoc = (
        db.query(CentreTest)
        .filter(
            CentreTest.centre_id == centre_id,
            CentreTest.test_id == test_id,
        )
        .first()
    )
    if not assoc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test association not found for this centre",
        )

    db.delete(assoc)
    db.commit()
