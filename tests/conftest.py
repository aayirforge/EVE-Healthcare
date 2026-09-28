from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.security import create_access_token, get_password_hash
from app.db.database import Base, SessionLocal, engine, get_db
from app.main import app
from app.models.diagnostic_centre import CentreTest, DiagnosticCentre
from app.models.diagnostic_test import DiagnosticTest
from app.models.user import User


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture(autouse=True)
def clean_db():
    with engine.begin() as conn:
        conn.execute(
            text(
                "TRUNCATE TABLE webhook_events, payments, bookings, centre_tests, "
                "diagnostic_tests, diagnostic_centres, users RESTART IDENTITY CASCADE;"
            )
        )
    yield


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    def override_get_db():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    user = User(
        email="testuser@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test User",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    token = create_access_token(subject=test_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_user(db):
    user = User(
        email="otheruser@example.com",
        hashed_password=get_password_hash("password456"),
        full_name="Other User",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def second_auth_headers(second_user):
    token = create_access_token(subject=second_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_centre(db):
    centre = DiagnosticCentre(
        name="Apollo Diagnostics",
        location="Indiranagar, Bangalore",
    )
    db.add(centre)
    db.commit()
    db.refresh(centre)
    return centre


@pytest.fixture
def test_diagnostic(db):
    diagnostic = DiagnosticTest(
        name="Complete Blood Count",
        description="Routine blood screen",
        price=Decimal("450.00"),
    )
    db.add(diagnostic)
    db.commit()
    db.refresh(diagnostic)
    return diagnostic


@pytest.fixture
def test_setup(db, test_centre, test_diagnostic):
    assoc = CentreTest(
        centre_id=test_centre.id,
        test_id=test_diagnostic.id,
        custom_price=Decimal("400.00"),
    )
    db.add(assoc)
    db.commit()
    db.refresh(assoc)
    return {
        "centre": test_centre,
        "test": test_diagnostic,
        "assoc": assoc,
    }
